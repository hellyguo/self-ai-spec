---
name: gdb-heap-analysis
description: "使用 GDB 分析 core dump 中的 glibc ptmalloc 堆与 arena，定位内存泄漏、内存占用异常与堆损坏。触发场景：内存泄漏分析、core dump 排查、arena 与 malloc_state 分析、glibc 堆调试、malloc 内部结构问题。"
---

# GDB 堆内存分析（glibc ptmalloc）

Analyze glibc ptmalloc heap structures in core dumps. Human judgment required at each decision point.

## Workflow

```
Step 0 判定 core 来源与符号一致 → Step 1 符号 → Step 2 走 arena → Step 3 分析 malloc_state
→ Step 4 看内存分布 → Step 5 定位具体分配 → Step 6 大 core 直接扫文件（>4GB 必用）
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
gdb -q -batch -ex 'source scripts/arena_walk.py' -ex 'arena_walk <arena_base>' ./app core
```

**Judgment**: Arena size thresholds — typical <100MB, suspicious >500MB, abnormal >1GB. Record largest arena address.

## Step 3: Analyze malloc_state

```gdb
p *(struct malloc_state *)$arena_addr
```

Key fields: `top`, `system_mem`, `bins[]`, `fastbinsY`

### Top Chunk Location

```gdb
set $top = ((struct malloc_state *)$arena)->top
```

- `$top` near `$arena_addr` (within 64MB) → Subheap mode
- `$top` in different address range → **Direct mmap mode**

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

**Judgment**: Sum subheap sizes, compare with `system_mem`. Gap >1GB → large direct mmap allocations.

### Mmap Mode

```gdb
info proc mappings        # 注意：core 上只列文件映射
readelf -lW core | grep LOAD   # 匿名段看这里
```

- 全零的大段 R/RW 映射多为保留/未触碰：用页扫描统计非零页，避免误判为泄漏。
- core 文件大小 ≠ RSS；`非零页 × 4KB` 更接近真实占用。

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
3. **可达性**：全 core 扫描该对象地址；命中 1 次且是“自指” → 不可达 garbage（真泄漏）；多次命中需定位引用者。
4. **内容聚类**：批量读取对象字段（如来源、标题、状态等）做分布统计，往往能直接指向泄漏来源。

## Step 6: 大 core（>4GB）/ 海量 chunk：直接扫 core 文件

当 core 很大或 chunk 数上百万时，gdb 逐地址 `x`/`find` 会慢到不可用。改为 **mmap core 文件按 chunk 链线性扫描**（GB 级 core 通常在秒级到十几秒内完成）。

```bash
gcc -O2 -o /tmp/heap_scan scripts/heap_scan.c
/tmp/heap_scan <core> <heap_start> <heap_end> <file_off_at_heap_start> [target_size]
```

关键点：

- **VA→文件偏移**：`off = p_offset + (va - p_vaddr)`；core 的 `p_offset` 与 `p_vaddr` **不必同余于页大小**，不要按页取整。
- 相邻 `PT_LOAD` 若 `off−vaddr` 差值一致，可视为连续，用同一线性映射（一个堆跨多个 `PT_LOAD` 很常见）。
- 遍历：`size = *(u64*)(p+8) & ~7`；校验 `16 <= size <= remain && size%16==0`；`next=p+size`；`in_use = (*(u64*)(next+8)) & PREV_INUSE`。
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
| 3 | Top location | Far from arena = mmap mode |
| 4 | Subheap vs sys_mem | >1GB gap = direct mmap |
| 5 | Chunk flags | IS_MMAPPED = mmap alloc |
| 5 | 尺寸指纹/自指 | 锁定泄漏对象类型 |
| 5 | 可达性扫描 | 仅自指 = 不可达泄漏 |
| 6 | 大 core | 直接扫文件，勿逐地址 gdb |

## Common Issues

- **exec/core 的 mtime 告警**：只是文件时间差，先比 build-id，别急着找 sysroot。
- **`info proc mappings` 看不到匿名段**：core 上只列文件映射；用 `readelf -lW core` 的 `PT_LOAD`。
- **`info line` 行号对不上 HEAD**：说明现场二进制不是当前源码；先确认版本，再谈“是否已修”。
- **libc 无符号时 `bt` 出现 `profil`/`this=0x0`/`corrupt stack?`**：多为假帧，改用堆/数据面证据。
- **`find` 很慢**：只在 libc 数据段（64KB 级）用 `find`，不要对整堆 `find`。
- **main_arena not accessible**：用 Step 2 的 “top 指针反查”；或从任一 arena 的 `next` 环回推。
- **heap_info undefined**：2.26–2.29 固定 32B（`ar_ptr/prev/size/mprotect_size`）；2.30+ 多 `pagesize` 字段。
- **大段全零映射**：多为保留/未触碰，先统计非零页再判断。
- **对象指针全变 “?”**：忘了把对象内部 VA 再做一次 `va2p()`。
- **没有应用日志时**：core 里常驻日志环形缓冲区，`grep -aob "<关键字>" core` 拿偏移，再 `dd | strings` 取上下文，常能还原失败点与释放缺失。
- **Memory access errors**：用 [scripts/arena_walk.py](scripts/arena_walk.py) 的 `gdb.MemoryError` 处理。

## Output Templates

- [templates/arena-walk-output.md](templates/arena-walk-output.md) - Arena walk and chunk analysis output format
- [templates/diagnostic-decision.md](templates/diagnostic-decision.md) - Pattern match and diagnosis result format
- [templates/leak-profile-output.md](templates/leak-profile-output.md) - 百万级同尺寸对象泄漏的交付模板

## Resources

- [references/glibc-offsets.md](references/glibc-offsets.md) - Known offsets by glibc version（含 2.26–2.31 与 2.30+ heap_info 差异）
- [references/heap-structures.md](references/heap-structures.md) - Detailed struct layouts
- [references/diagnostic-patterns.md](references/diagnostic-patterns.md) - Diagnostic patterns（含同尺寸海量泄漏、gcore 活体快照）
- [references/large-core-chunk-scan.md](references/large-core-chunk-scan.md) - 大 core 直接扫描方法论与坑
- [scripts/heap_scan.c](scripts/heap_scan.c) - 参数化 chunk 链扫描器
- [scripts/arena_walk.py](scripts/arena_walk.py) - 无符号 arena 链遍历（gdb python）
- [scripts/scan_zero_pages.c](scripts/scan_zero_pages.c) - 保留区/未触碰零页统计
