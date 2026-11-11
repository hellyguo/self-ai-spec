# 大 core 直接扫描方法论（>4GB / 百万级 chunk）

gdb 适合“看结构、看单点”，不适合“遍历 GB 级堆里的百万个 chunk”。
本文给出一套通用方法：**把 core 当文件 mmap，按 chunk 链线性走**，
在秒级到十几秒内得到 in-use/free 分桶、泄漏对象尺寸、内容聚类；再用 gdb 做定点核对。

> 适用形态：in-use 集中在一个尺寸档、count 达百万级、对象内容高度重复。
> 对应 [diagnostic-patterns.md](diagnostic-patterns.md) 的 Pattern 6。

---

## 1. 何时使用

- core > 2~4GB，或 gdb 的 `find`/`x` 明显变慢；
- 疑似“大量同尺寸对象”泄漏（分桶会一眼看出）；
- 需要统计“谁占了多少、多少条、什么内容”，而不是单点回溯。

## 2. 先决条件与假设

1. **确定堆的 VA 范围**：从 `info files` 的 `loadN` 或 `readelf -lW core` 的 `PT_LOAD` 取。
   - 主 arena 一般是 `[heap]`/brk 段；非主 arena 从 `heap_info` 开始。
   - 一个堆可能跨多个 `PT_LOAD`，但 chunk 链可以连续。
2. **建立 VA→文件偏移映射**：`off = p_offset + (va - p_vaddr)`。
3. **线性假设**：相邻 PT_LOAD 的 `off - vaddr` 差值一致时，可用同一公式覆盖多个段
   （即 `file_off = FILE_OFF + (va - HEAP_START)`）。
   若差值不一致，需按段建表（`va_start, va_end, off_start` 三元组）。

### 2.1 最容易踩的坑：p_offset 与 p_vaddr 不同余

```
LOAD 0x<off> 0x<vaddr> 0x<filesz> RW
      ^ offset mod page_size 可能非 0
                 ^ vaddr  mod page_size 可能为 0
```

core 的 `PT_LOAD` **不保证** `p_offset ≡ p_vaddr (mod page_size)`（这与普通 ELF 映射不同）。
**不要**按页对齐去推算偏移；直接用 `p_offset + (va - p_vaddr)`，并做一次双方法校验：

```bash
# gdb 读一段
gdb -batch -ex "dump binary memory /tmp/g.bin <va_start> <va_end>" <exe> <core>
# 文件读同一段（偏移用 p_offset + (va - p_vaddr) 计算）
dd if=<core> bs=1 skip=$((<computed_offset>)) count=64 2>/dev/null > /tmp/d.bin
md5sum /tmp/g.bin /tmp/d.bin    # 必须一致
```

> 大数算术要用计算器/脚本，别心算；差一页就会得出“gdb 与 dd 不一致”的假象。

## 3. chunk 链遍历算法

```c
p = heap_start;                       /* 第一块 chunk 指针（不是 user 指针） */
while (p + 16 <= heap_end) {
    size = *(uint64_t *)(va2p(p) + 8) & ~7ULL;   /* size 在 chunk+8 */
    if (size < 16 || size > (heap_end - p) || (size & 0xf)) { bad++; break; }
    next = p + size;
    if (next + 16 > heap_end) in_use = 0;   /* 最后一块：下一块头部在堆外 */
    else in_use = *(uint64_t *)(va2p(next) + 8) & PREV_INUSE;
    /* 统计 in_use / free、按 size 分桶、对目标 size 抽样 */
    p = next;
}
```

要点：

| 项 | 说明 |
|---|---|
| chunk 指针 | 指向 `prev_size` 字段（malloc 返回值 = chunk + 0x10） |
| size 位置 | `chunk + 8`，低 3 位是标志（PREV_INUSE/IS_MMAPPED/NON_MAIN_ARENA） |
| in-use 判定 | **下一块**的 `size & PREV_INUSE`，不是本块；最后一块的 next 头部在堆外，直接按 free/top |
| 未对齐读 | core 的 `p_offset` 与 VA 不保证 8 字节对齐，u64 读取用 `memcpy` 或逐字节 |
| top | 最后一块，free 且 `p + size == heap_end`（允许 brk 尾差几页） |
| 破坏判定 | 只有出现 `size<16 / 超界 / 非 16 对齐` 才怀疑破坏；`bad=0` 说明链完整 |
| 迭代上限 | 加一个 `n > 4e8` 的保护，防止异常 core 卡死 |

### 3.1 user 指针 vs chunk 指针

```
chunk:  +0 prev_size | +8 size | +0x10 user data ...
```

- 对象指针通常指向 **user data（chunk+0x10）**；
- chunk 统计用 chunk 指针；对象字段用 user 指针。

## 4. 分桶与“尺寸指纹”

按 `log2(size)` 或精确 size 计数，输出 in-use/free 的 count 与 bytes。
若某一档出现 **百万级 count 且 bytes 占 in-use 的 90%+**，基本就是泄漏主体。

**尺寸指纹**：把 chunk size 换算回请求大小，与候选类 `sizeof(T)` 对齐：

```
request2size(n) = (n + 8 + 15) & ~15      // 64-bit glibc
示例：sizeof(T)=<x> → request2size(<x>)=<chunk_size>，与实测块大小完全一致
```

估算时注意：`request2size` 会向上取整到 16 字节并加 chunk 头，因此相邻请求大小可能落到同一档。
再结合对象内容（vtable、自指字段、业务字段）确认类型。

### 4.1 IS_MMAPPED 不在 chunk 链里

`heap_scan` 只走 arena 的 chunk 链。请求 `>= mmap_threshold`（默认 128KB，动态可升到
约 32MB）时 glibc 直接 `mmap`，这类 chunk：

- 不在 arena 链里，`heap_scan` 完全看不到；
- 不计入 `malloc_state.system_mem`；
- chunk 头在映射起始处，`size` 带 `IS_MMAPPED`（bit 1）。

```bash
gcc -O2 -o /tmp/mmap_scan ../scripts/mmap_scan.c
/tmp/mmap_scan <core> [min_size]
```

`mmap_scan` 解析 core 的 `PT_LOAD` 与 `NT_FILE` note，区分文件映射与匿名映射，
输出匿名映射大小分桶、疑似 `IS_MMAPPED` chunk、以及非 chunk 大块 ANON 的头部样本。

判读要点：

- `MMAPPED`：映射起始处 chunk size 与映射长度接近、16 字节对齐；
- 映射长度可能大于 chunk size（相邻匿名 VMA 被内核合并），用上界容忍；
- `ANON` 且非零页很少 → 保留/未触碰，不是泄漏；
- `ANON` 且有内容 → 可能是池化缓冲/自定义分配器，也可能是 `[heap]`、线程栈、vdso；
  必须结合应用统计或 NMT，不能只凭 core 判类型。

> Linux core 的 note 按 4 字节对齐，`NT_FILE` descriptor 在 name 之后；解析错位会得到
> 0 个文件映射，把可执行文件/libc 段误当匿名段，导致分桶失真。

## 5. 内容聚类

对目标尺寸的每个对象，按已知偏移读取字符串字段（来源、标题、ID、状态等），
做 `(field1, field2) → count` 的哈希统计。通常几十种组合就能把泄漏来源定位到“哪类消息/哪个上游”。

注意：

- 对象内部指针是 **进程 VA**，解引用前必须 `va2p()`；
- 统计脚本要限制单字段长度、去重表大小，避免被异常数据拖垮；
- 采样时同时记录“最小/最大对象地址”，确认泄漏是**持续累积**（跨整个堆）而非一次性大分配。

### 5.1 应用内日志缓冲区（没有日志文件时的关键证据）

很多 C++ 服务把最近若干条日志放在堆上的环形缓冲区。即使拿不到磁盘日志，
也能从 core 里直接取证：

```bash
# 1) 定位：-o 输出字节偏移，-b 按二进制处理
grep -aob "<关键日志文本>" <core> | head
# <offset>:<key text>

# 2) 取上下文（前后各 1KB，再看字符串）
dd if=<core> bs=1 skip=$((<offset-1000>)) count=2400 2>/dev/null | strings -n 8
```

据此常能还原“发生了什么 → 哪一步失败 → 对象是否被释放”的完整因果链。

注意：`grep -c` 统计的是“行数”不是“次数”；要偏移用 `-b`，要多次命中用 `-o`。

## 6. 可达性判定（泄漏 vs 缓存/仍被引用）

对抽样对象地址做全 core 的 8 字节扫描：

```c
for (align = 0; align < 8; align++)
  for (i = align; i + 8 <= filesize; i += 8)
    if (*(uint64_t *)(base + i) == obj) hits++;
```

- `hits == 1`：只命中对象自身的自指字段 → **不可达 garbage，真泄漏**；
- `hits > 1`：还有引用，需定位引用者（可能是缓存/队列，不能直接判泄漏）；
- 用 3 个抽样（首/中/尾）即可，无需全量。

**边界（必须写进结论）**：

- 自定义分配器（slab、对象池、tcmalloc/jemalloc）用 freelist 或位图管理空闲对象，
  指针不在对象内，`hits==1` 也可能是“池中待复用”，不是泄漏；
- TLS/线程缓存只存一个指针时，`hits>1` 仍可能是逻辑已释放、延迟归还；
- 判断要结合分配器元数据与引用者生命周期，不能只看 hit 数。

> 对齐很重要：core 的某个 LOAD `p_offset` 可能不是 8 的倍数，
> 只扫一种对齐会漏掉一半指针。

## 7. 零页、保留区与 RSS

- core 会把“未触碰的匿名页”也写成全零；**文件大小 ≠ 实际占用**。
- 对可疑大段做页扫描（按目标进程页大小判断整页是否全零），统计 `nonzero_pages`。
- 页大小从 core 的 `NT_AUXV`（`AT_PAGESZ`）读取；**不要用宿主 `sysconf`**：x86 4KB 宿主分析 aarch64 64KB core 时，页数与 MiB 会差 16 倍。
- 工具已自动检测；手工计算时同样以 `AT_PAGESZ` 为准。
- 若某段整齐的 R/RW 映射全零，通常是保留/未触碰；真实占用应看非零页。

## 8. 与 gdb 的分工

| 任务 | 工具 |
|---|---|
| 结构体偏移、arena/top/bin 字段 | gdb |
| 单对象字段、调用栈、行号 | gdb |
| 百万级 chunk 统计、内容聚类、可达性 | 直接扫文件（本节） |
| 最终结论的关键证据 | 两者互相校验（堆统计 + 内存内容 + 运行时结构/配置/日志） |

## 9. 现成工具

```bash
gcc -O2 -o /tmp/heap_scan ../scripts/heap_scan.c
/tmp/heap_scan <core> <heap_start> <heap_end> <file_off_at_heap_start> [target_size]
```

输出：`chunks/inuse_chunks/inuse_bytes/free_bytes/bad/last`、按 log2 分桶、目标尺寸样本。
`bad>0` 时统计在首个坏块处截断，不能用于结论。

```bash
gcc -O2 -o /tmp/mmap_scan ../scripts/mmap_scan.c
/tmp/mmap_scan <core> [min_size]
```

输出：`PT_LOAD`/文件映射/匿名映射计数、匿名映射分桶、`IS_MMAPPED` chunk 列表与非 chunk
大块 ANON 样本。用于补齐 arena 链的盲区。

## 10. 检查清单

- [ ] 用 `p $_siginfo` 确认 core 来源（gcore vs 崩溃）
- [ ] 用 build-id 确认 exec/libc 是否匹配；`info line` 对照现场版本
- [ ] `readelf -lW core` 取堆的 PT_LOAD 与 `p_offset`
- [ ] gdb 读一段 + `dd/od` 读同一段，md5 校验 VA→offset
- [ ] 线性扫 chunk，`bad=0` 后再相信统计；`bad>0` 时只当下界
- [ ] 用 `mmap_scan` 统计 `IS_MMAPPED` 与大块 ANON，补齐 arena 链盲区
- [ ] 对最大尺寸档做 `sizeof/request2size` 指纹 + 内容聚类
- [ ] 抽样做可达性扫描（8 种对齐），并说明自定义分配器/TLS 的边界
- [ ] 用页扫描排除全零保留区（页大小取自 core 的 `AT_PAGESZ`，不是宿主）
- [ ] 结论用“堆统计 + 内存内容 + 运行时结构（配置/路由/日志）”三方互证
