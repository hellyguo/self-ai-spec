---
name: gdb-heap-analysis
description: "使用 GDB 分析 core dump 中的 glibc ptmalloc 堆与 arena，定位内存泄漏、内存占用异常与堆损坏；覆盖 arena chunk 链与 IS_MMAPPED/mmap 分配。触发场景：内存泄漏分析、core dump 排查、arena 与 malloc_state 分析、glibc 堆调试、malloc 内部结构问题、mmap 大块分配统计。"
---

# GDB 堆内存分析（glibc ptmalloc）

Analyze glibc ptmalloc heap structures in core dumps. Human judgment required at each decision point.

## Workflow

```
Step 0 判定 core 来源与符号一致 → Step 1 符号 → Step 2 走 arena → Step 3 分析 malloc_state
→ Step 4 看 subheap 分布 → Step 4.5 统计 mmap 分配 → Step 5 定位具体分配
→ Step 6 大 core 直接扫文件（>4GB 必用）
```

## Step 0: 判定 core 来源与符号一致性（先做，决定后续路线）

```gdb
p $_siginfo          # si_signo / si_code
info threads
thread apply all bt 10
```

| 观察 | 含义 | 路线 |
|---|---|---|
| `si_signo = 19`(SIGSTOP)、`si_code = 0` | **gcore/ptrace 活体快照**，不是崩溃 | 关注内存/队列；不要找崩溃栈 |
| 线程全在 `cond_wait`/`accept`，消息队列为空 | 泄漏 + 停滞/濒死，不是“积压” | 按泄漏分析 |
| 有非法 PC / `corrupt stack?` | 可能缺 libc 符号导致的假帧 | 先用数据面证据，勿据假帧下结论 |

**符号一致性**：

- `warning: exec file is newer than core file` **只说明 mtime 不同**，不代表符号不匹配。
- 用 core 里映射的 ELF build-id 与可执行文件对比（`readelf -n`），一致即可用该二进制符号。
- libc build-id 常与“本机安装版”不一致：到部署侧 sysroot 或运行环境里找同 build-id 的 libc；找不到 debuginfo 就走手工偏移。
- 需要确认“现场二进制是否含某次修复”时：`info line file:line` 与目标 commit 的源码行号对照，或直接反汇编目标函数看是否出现对应调用。

**core 的匿名映射**：`info proc mappings` 在 core 上通常只列文件映射；匿名段只出现在 `info files` 的 `loadN`，或 `readelf -lW core` 的 `PT_LOAD`。

## Step 1: Confirm Debug Symbols

```gdb
ptype struct malloc_state
ptype struct malloc_chunk
```

- Struct definition output → Has symbols, use struct access
- "No symbol table" → No symbols, need manual offsets

### No Symbols

```bash
ldd --version
```

```gdb
info sharedlibrary libc
```

Read [references/glibc-offsets.md](references/glibc-offsets.md) for known offsets by version.
（64 位下 aarch64 与 x86_64 的指针/对齐一致，2.26–2.31 的 `top=0x60`、`next=0x870`、`system_mem=0x888` 通用。）

## Step 2: Walk All Arenas

### With Symbols

```gdb
p &main_arena
p main_arena.system_mem
set $a = main_arena.next
while $a != &main_arena && $a != 0
  printf "Arena @ %p, sys_mem=%lu MB\n", $a, $a->system_mem / 1024 / 1024
  set $a = $a->next
end
```

### Without Symbols

**不要盲扫 libc 数据段**。用“已知 chunk 指针反查 top 字段”最可靠：

```gdb
# 1) 由堆里任意已知块/最后一块得到 top 指针值（见 Step 6 的 chunk 链）
# 2) 在 libc 的数据段（RW 映射，通常 64KB）里搜这个值
find /g <libc_rw_start>, <libc_rw_end>, <top_value>
# 命中地址 = &main_arena.top，减 0x60 即 main_arena
set $ma = <hit_addr> - 0x60
x/1gx $ma+0x888        # system_mem
x/1gx $ma+0x870        # next
```

非主 arena：从堆起始的 `heap_info` 反查（2.26–2.29 为 32B：`ar_ptr@0`、`prev@8`、`size@16`、`mprotect_size@24`），`ar_ptr` 即 `malloc_state`。再沿 `next` 环形链走完。

可直接用 [scripts/arena_walk.py](scripts/arena_walk.py)（带 `gdb.MemoryError` 处理）：

```bash
gdb -q -batch -ex 'source scripts/arena_walk.py' -ex 'arena_walk --glibc <ver> <arena_base>' ./app core
```

**Judgment**: Arena size thresholds — typical <100MB, suspicious >500MB, abnormal >1GB. Record largest arena address.

**多 arena 维度**：记录 arena 数量与各 arena 的 `system_mem`。

- Σ`system_mem` 占进程 RSS 的 50% 以上 → 多 arena 本身是内存大头，检查线程数、`MALLOC_ARENA_MAX` 与每线程缓存。
- 单个 arena 显著大于其余（相差一个数量级）→ 泄漏集中在该 arena，后续 Step 5 只查它。

## Step 3: Analyze malloc_state

```gdb
p *(struct malloc_state *)$arena_addr
```

Key fields: `top`, `system_mem`, `bins[]`, `fastbinsY`

### Top Chunk Location

```gdb
set $top = ((struct malloc_state *)$arena)->top
```

- top 始终位于某个 arena 堆内：main_arena 在 brk 区，非主 arena 在它的某个 64MB subheap 中。
- **不能用 top 与 arena 结构地址的远近判断是否 direct mmap**：main_arena 的结构在 libc，top 天然很远；非主 arena 也可能跨多个 subheap。
- top 不在任何已知堆区间 → 先怀疑符号/偏移错误，再怀疑堆损坏。
- IS_MMAPPED 分配没有 top，也不在 arena 链里，见 Step 4.5。

## Step 4: Check Memory Distribution

### Subheap Chain

```gdb
set $heap = $arena_addr - 32
while $heap != 0
  set $ar = *(void**)$heap
  if $ar != $arena_addr
    break
  end
  set $size = *(size_t*)($heap+16)
  printf "Subheap @ %p, size=%lu MB\n", $heap, $size/1024/1024
  set $heap = *(void**)($heap+8)
end
```

**Judgment**:

- `system_mem` 只统计 brk 堆与 subheap（`heap_info` 段），**不包含单个 `IS_MMAPPED` 分配**。
- main_arena 用 brk，**没有 `heap_info`**；不要对 main_arena 走 subheap 链。
- 非主 arena 的 Σsubheap 应接近 `system_mem`；明显 gap → subheap 链没走全（`prev` 方向/多个 subheap）或偏移错误，不是 direct mmap。
- mmapped chunk 用 `malloc_info` 的 `<total type="mmap">` 或 Step 4.5 单独统计。

## Step 4.5: 统计 mmap 分配（arena 链的盲区）

glibc 对 `>= mmap_threshold`（默认 128KB，释放后会动态上调，最高约 32MB）的请求直接 `mmap`：

- chunk 独立于 arena，**不在 chunk 链里**；
- **不计入** `malloc_state.system_mem`（`malloc_info` 中单独列在 `<total type="mmap">`）；
- 头部在映射起始处，`size` 字段带 `IS_MMAPPED`（bit 1）。

```bash
gcc -O2 -o /tmp/mmap_scan scripts/mmap_scan.c
/tmp/mmap_scan <core> [min_size]      # min_size 默认 128KB
```

输出包含：文件映射/匿名映射计数、匿名映射大小分桶、疑似 `IS_MMAPPED` chunk（尺寸与样本）、以及非 chunk 的大块 ANON 映射。

判读：

- `MMAPPED`：映射起始处的 chunk size 与映射长度接近、16 字节对齐；
- `ANON` 且非零页很少 → 保留/未触碰映射，不是泄漏；
- `ANON` 且有内容 → 可能是直接 mmap 的池化缓冲、自定义分配器，或 `[heap]`/线程栈/vdso；需结合应用统计/NMT 核对；
- 页大小优先从 core 的 `NT_AUXV`（`AT_PAGESZ`）读取；本机进程才用 `sysconf`。跨架构分析时宿主页大小会错（如 x86 4KB 宿主分析 aarch64 64KB core），`mmap_scan`/`scan_zero_pages` 已自动读取 core。

## Step 5: Locate Specific Allocations

### Chunk Header

```gdb
set $chunk = <chunk_addr>
x/gx $chunk-8   # prev_size + size with flags
```

Size field flags (lowest 3 bits): PREV_INUSE(bit 0), IS_MMAPPED(bit 1), NON_MAIN_ARENA(bit 2)

### Bins

```gdb
p ((struct malloc_state *)$arena)->bins[0]@10
p ((struct malloc_state *)$arena)->fastbinsY
```

### 对象类型反推（无分配栈时）

1. **尺寸指纹**：chunk size 与 `request2size(sizeof(T))` 精确匹配（先由分桶锁定 chunk size，再反推候选类型）。
2. **自指/指针字段**：对象内的自指字段等于自身地址、或 vtable/字符串指针落在堆内，可反推类型。
3. **可达性**：全 core 扫描该对象地址；标准 malloc 前提下，命中 1 次且是“自指” → 不可达 garbage（真泄漏）；多次命中需定位引用者。
4. **内容聚类**：批量读取对象字段（如来源、标题、状态等）做分布统计，往往能直接指向泄漏来源。

**可达性判断的边界**：

- 自定义分配器（slab、对象池、tcmalloc/jemalloc）用 freelist/位图管理空闲对象，指针不一定在对象内，`hits==1` 也可能是“池中待复用”，不是泄漏。
- TLS/线程缓存只持有对象指针时，`hits>1` 仍可能是“逻辑已释放、延迟归还”，需看引用者是否是长生命周期结构。
- 结论要结合分配器元数据与引用者生命周期，不能只凭 hit 数下判断。

## Step 6: 大 core（>4GB）/ 海量 chunk：直接扫 core 文件

当 core 很大或 chunk 数上百万时，gdb 逐地址 `x`/`find` 会慢到不可用。改为 **mmap core 文件按 chunk 链线性扫描**（GB 级 core 通常在秒级到十几秒内完成）。

**覆盖范围**：只扫 arena 的 chunk 链；`IS_MMAPPED` 分配不在链里，必须用 Step 4.5 的 `mmap_scan` 另行统计。`bad>0` 时统计在首个坏块处截断，`inuse_bytes` 不可用于结论。

```bash
gcc -O2 -o /tmp/heap_scan scripts/heap_scan.c
/tmp/heap_scan <core> <heap_start> <heap_end> <file_off_at_heap_start> [target_size]
```

关键点：

- **VA→文件偏移**：`off = p_offset + (va - p_vaddr)`；core 的 `p_offset` 与 `p_vaddr` **不必同余于页大小**，不要按页取整。
- 相邻 `PT_LOAD` 若 `off−vaddr` 差值一致，可视为连续，用同一线性映射（一个堆跨多个 `PT_LOAD` 很常见）。
- 遍历：`size = *(u64*)(p+8) & ~7`；校验 `16 <= size <= remain && size%16==0`；`next=p+size`；`in_use = (*(u64*)(next+8)) & PREV_INUSE`。
- 最后一块的 `next` 恰好等于堆尾，**不能再读 `next+8`**；按 free/top 处理，否则会越界读到相邻 PT_LOAD。
- core 的文件偏移与 VA 不保证 8 字节对齐，读 u64 用 `memcpy`/逐字节，避免未对齐访问。
- 最后一块为 top（free，覆盖到堆尾）；`bad>0` 才需要考虑破坏。
- **对象内部指针是进程 VA，不是文件 mmap 指针**：二次解引用必须再 `va2p()`（否则对象字段统计会全是 “?”）。
- 8 字节扫描要覆盖 0..7 全部对齐；`grep -c` 统计的是“行数”，不是匹配次数。

细节与完整方法论见 [references/large-core-chunk-scan.md](references/large-core-chunk-scan.md)。

## Judgment Summary

| Step | Check | Decision |
|------|-------|----------|
| 0 | `si_signo` | 19/SIGSTOP = gcore 活体快照，不是崩溃 |
| 0 | build-id | core 与 exec/libc 是否匹配；不匹配则换 sysroot |
| 1 | Symbols? | Struct access vs manual offset |
| 2 | Arena size | >1GB = abnormal |
| 2 | arena 数量 × 平均 | Σsystem_mem > RSS 50% = 多 arena 是大头 |
| 3 | Top location | 不在任何堆区间 = 符号/偏移错误或损坏 |
| 4 | Subheap vs sys_mem | gap = 链未走全/偏移错，不是 mmap |
| 4.5 | IS_MMAPPED | 不在 arena 链、不计入 system_mem，需单独统计 |
| 5 | Chunk flags | IS_MMAPPED = mmap alloc |
| 5 | 尺寸指纹/自指 | 锁定泄漏对象类型 |
| 5 | 可达性扫描 | 结合分配器与引用者，勿只看 hit 数 |
| 6 | 大 core | 直接扫文件，勿逐地址 gdb |

## Common Issues

- **exec/core 的 mtime 告警**：只是文件时间差，先比 build-id，别急着找 sysroot。
- **`info proc mappings` 看不到匿名段**：core 上只列文件映射；用 `readelf -lW core` 的 `PT_LOAD`。
- **`system_mem` 对不上实际占用**：它不含 `IS_MMAPPED` 分配；mmap 块用 `malloc_info` 的 `<total type="mmap">` 或 `mmap_scan` 单独看。
- **`heap_scan` 扫不到大块分配**：`IS_MMAPPED` 不在 arena 链里，用 Step 4.5 的 `mmap_scan`。
- **跨架构用宿主页大小**：core 里 `AT_PAGESZ` 才是目标页大小；用本机 `sysconf` 会把 aarch64 64KB 页算成 x86 4KB，页数与 MiB 全错。工具已优先读 core。
- **NT_FILE 解析错位**：Linux core 的 note 按 4 字节对齐，descriptor 在 name 之后；对齐/偏移错会得到 0 个文件映射，把可执行文件段误当匿名段。
- **`bad>0` 仍用 inuse_bytes**：统计在首个坏块处截断，只能当“下界”，不能做结论。
- **top 离 arena 很远不等于 mmap**：main_arena 结构在 libc，top 天然很远；以 top 是否落在已知堆区间为准。
- **`info line` 行号对不上 HEAD**：说明现场二进制不是当前源码；先确认版本，再谈“是否已修”。
- **libc 无符号时 `bt` 出现 `profil`/`this=0x0`/`corrupt stack?`**：多为假帧，改用堆/数据面证据。
- **`find` 很慢**：只在 libc 数据段（64KB 级）用 `find`，不要对整堆 `find`。
- **main_arena not accessible**：用 Step 2 的 “top 指针反查”；或从任一 arena 的 `next` 环回推。
- **heap_info undefined**：2.26–2.29 固定 32B（`ar_ptr/prev/size/mprotect_size`）；2.30+ 多 `pagesize` 字段。
- **大段全零映射**：多为保留/未触碰，先统计非零页再判断。
- **对象指针全变 “?”**：忘了把对象内部 VA 再做一次 `va2p()`。
- **没有应用日志时**：core 里常驻日志环形缓冲区，`grep -aob "<关键字>" core` 拿偏移，再 `dd | strings` 取上下文，常能还原失败点与释放缺失。
- **Memory access errors**：用 [scripts/arena_walk.py](scripts/arena_walk.py) 的 `gdb.MemoryError` 处理。

## 适用边界

详见 [references/scope-and-limits.md](references/scope-and-limits.md)。要点：

- 能看：走 glibc 的 native 分配（JNI、Netty 的 malloc 路径、JVM 自身的 native malloc/mmap）。
- 不能看：Java 堆、Metaspace、CodeCache、非 glibc 分配器（jemalloc/tcmalloc 等）和自定义池的内部状态。
- `DirectByteBuffer`：小 buffer 走 `malloc`，在 arena 链里；大块或池化 buffer 走 `mmap`，用 Step 4.5。
- 先确认“有没有走 glibc”，再决定用本技能还是 NMT/分配器自带工具。

## Output Templates

- [templates/arena-walk-output.md](templates/arena-walk-output.md) - Arena walk and chunk analysis output format
- [templates/diagnostic-decision.md](templates/diagnostic-decision.md) - Pattern match and diagnosis result format
- [templates/leak-profile-output.md](templates/leak-profile-output.md) - 百万级同尺寸对象泄漏的交付模板

## Resources

- [references/glibc-offsets.md](references/glibc-offsets.md) - Known offsets by glibc version（含 2.26–2.31 与 2.30+ heap_info 差异）
- [references/heap-structures.md](references/heap-structures.md) - Detailed struct layouts
- [references/diagnostic-patterns.md](references/diagnostic-patterns.md) - Diagnostic patterns（含同尺寸海量泄漏、gcore 活体快照）
- [references/large-core-chunk-scan.md](references/large-core-chunk-scan.md) - 大 core 直接扫描方法论与坑
- [references/scope-and-limits.md](references/scope-and-limits.md) - glibc/native/Java 场景的适用边界
- [scripts/heap_scan.c](scripts/heap_scan.c) - 参数化 arena chunk 链扫描器
- [scripts/mmap_scan.c](scripts/mmap_scan.c) - 匿名映射统计与 IS_MMAPPED chunk 识别
- [scripts/arena_walk.py](scripts/arena_walk.py) - 无符号 arena 链遍历（gdb python，支持 --glibc）
- [scripts/scan_zero_pages.c](scripts/scan_zero_pages.c) - 保留区/未触碰零页统计（页大小自动从 core 的 AT_PAGESZ 检测）
