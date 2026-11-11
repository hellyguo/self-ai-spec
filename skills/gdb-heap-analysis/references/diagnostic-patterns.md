# Diagnostic Patterns

## Pattern 1: Large system_mem with No or Short Subheap Chain

**Symptoms**:
- Arena has `system_mem` > 1GB
- No `heap_info` chain, or the chain sum is far below `system_mem`
- Top chunk is far from the arena structure address

**Diagnosis**:
- For `main_arena`: `system_mem` is the brk heap; there is **no `heap_info`** and the
  arena structure lives in libc, so a far top chunk is normal. This is not mmap mode.
- For non-main arenas: subheap sum should be close to `system_mem` (modulo page
  rounding). A large gap means the subheap walk is incomplete (wrong `prev`
  direction / multiple subheaps / wrong offsets), not direct mmap.
- Single `IS_MMAPPED` allocations are **not** part of `system_mem` at all; see Pattern 9.

**Explanation**:
- `system_mem` covers brk heap (main arena) and mmap'd subheaps (non-main arenas)
- Individual mmapped chunks are tracked separately by the allocator
- `malloc_info` reports them under `<total type="mmap">`

**Next step**:
1. Use `readelf -lW core` to list the actual heap/subheap ranges.
2. For non-main arenas, re-walk `heap_info.prev` from the subheap containing top.
3. Run `scripts/mmap_scan.c` to account for mmapped chunks separately (Pattern 9).

---

## Pattern 2: Many Small Arenas

**Symptoms**:
- 20+ arenas
- Each arena < 10MB
- Total memory moderate

**Diagnosis**: Multi-threaded application with per-thread arenas

**Explanation**:
- glibc creates arena per thread (up to limit)
- Each thread's allocations go to its arena
- Normal behavior for thread-heavy apps

**Next step**: Focus on individual thread's allocation pattern if needed.

---

## Pattern 3: Arena with Huge top Chunk

**Symptoms**:
- top chunk size > 100MB
- Most bins empty
- system_mem ≈ top chunk size

**Diagnosis**: Large contiguous allocation fragmented

**Explanation**:
- Application allocated huge contiguous block
- Freed most of it, but fragmentation prevents return to system
- top chunk is the remaining wilderness

**Next step**: Check if application needs custom allocator for large blocks.

---

## Pattern 4: Corrupted Arena

**Symptoms**:
- Walking arena chain loops infinitely
- Invalid addresses in bins
- chunk size = 0 or negative

**Diagnosis**: Memory corruption (double-free, buffer overflow)

**Warning**: Automated scanning may crash. Use manual inspection.

**Next step**:
1. Stop automated traversal
2. Manually inspect suspicious addresses
3. Check for double-free patterns in bin links

---

## Pattern 5: No Symbols Available

**Symptoms**:
- `ptype struct malloc_state` fails
- glibc version unknown

**Diagnosis**: Need manual offset determination

**Approach**:
1. Check `ldd --version` on target system
2. Use offset table from references/glibc-offsets.md
3. Verify by reading known values:
   - system_mem should be reasonable size
   - next should point to another arena or null

**Manual verification example**:
```gdb
# Try offset 0x888 for system_mem
x/gx $arena+0x888
# If result is a plausible size, offset is correct
# If result is tiny or huge (like 0xFFFFFFFF), wrong offset
```

---

## Pattern 6: 同尺寸对象海量泄漏（克隆/记录缓冲）

**Symptoms**:
- 某一尺寸档独占 in-use 的 90%+，count 到百万级；
- 这些 chunk 在堆里**连续分布**（从堆底到堆顶），不是一次性大分配；
- 用对象内指针做可达性扫描：每个对象只命中 1 次（自身自指）→ 不可达 garbage；
- 对象内容高度重复（同一来源/标题/业务键占绝大多数）。

**Diagnosis**: 某条“失败/异常路径”上创建的对象没有被释放；常见于
“克隆/复制消息或记录 → 分发、解析或入库失败 → 只释放了外层容器，未释放克隆体”。

**典型统计形态（数值均为示意）**:

```
main_arena.system_mem = <large> GiB
chunk walk:
  inuse_bytes ≈ <large> GiB
  free_bytes  ≈ <small> GiB
  bad = 0
size bucket <chunk_size>B: <millions> 个，占 in-use 的 95%+
  → 其中绝大多数属于同一类型 T
        sizeof(T) = <request>；request2size(<request>) = <chunk_size>   ← 尺寸指纹吻合
  → 对象自指字段指向自身；全 core 指针扫描仅 1 hit → 不可达
  → 某业务字段分布：单一取值占 90%+
```

**根因链（代码级，示意）**:

```
入站消息/记录 → 关键字段被掩码或改写
→ 查表/路由匹配失败（表中无该字面量）
→ 外层容器被释放，克隆体未释放
→ 每条泄漏 <chunk_size>B；按速率与时长可反推总量
```

**Next step**:
1. 按 [large-core-chunk-scan.md](large-core-chunk-scan.md) 做尺寸指纹 + 内容聚类；
2. 用 `sizeof/request2size` 锁定类型，再回到源码找“谁 new、谁该 delete”；
3. 对“分发失败/异常”路径逐条核对所有权（注意 handler 提前 return、double-free）。

**可达性边界**：`hits==1` 只对“裸指针 + 标准 malloc”成立。自定义分配器（slab/对象池/
tcmalloc/jemalloc）用 freelist/位图管理空闲对象时，`hits==1` 也可能是在池中待复用；
TLS/线程缓存持有对象指针时，`hits>1` 仍可能是逻辑已释放、延迟归还。需结合分配器元数据
与引用者生命周期判断。

---

## Pattern 7: core 是 gcore 活体快照（不是崩溃）

**Symptoms**:
- `p $_siginfo` → `si_signo = 19`（SIGSTOP）、`si_code = 0`；
- 所有线程都在 `pthread_cond_wait`/`accept`，没有业务栈；
- 工作队列为空，但 RSS/堆极大。

**Diagnosis**: 现场是“内存吃满后停滞/濒死”，不是段错误/abort。不要花时间找崩溃栈。

**Additional checks**:
- 用 build-id 确认 core 对应的二进制；再看 `info line file:line` 是否与目标 commit 一致。
  - 若现场行号与目标 tag 不一致，说明现场二进制不是该版本；
  - 也可反汇编目标函数，确认是否包含修复对应的调用。
- 缺 libc 符号时 `bt` 可能出现 `profil`/`this=0x0`/`corrupt stack?` 的假帧，不要据此判断栈损坏。

**Next step**: 转泄漏/容量分析（Pattern 1/3/6）；把“是否已修”与“现场是否已部署修复”分开结论。

---

## Pattern 8: 大段全零映射 ≠ 泄漏

**Symptoms**:
- core 很大（十几 GB），但大量 `PT_LOAD` 内容全零；
- 映射权限为 R 或 RW，大小整齐（如若干段 64MB）。

**Diagnosis**: 这是保留/未触碰的匿名映射（arena 预留、共享内存段等），core 会按 VMA 整段写出零页。

**Verification**:

```bash
# 按页大小统计非零页（../scripts/scan_zero_pages.c）
gcc -O2 -o /tmp/scan_zero_pages ../scripts/scan_zero_pages.c
/tmp/scan_zero_pages <core> <va_start> <size> <file_off_at_va_start>
# → pages=<n> nonzero_pages=<m> runs=<k> ...
```

**Rule**: 判断真实占用用“非零页 × 页大小”，不要用 core 文件大小；泄漏定位看 in-use chunk 统计。
`bad>0` 时统计在首个坏块处截断，只能当下界。

---

## Pattern 9: IS_MMAPPED 大块分配不在 arena 链

**Symptoms**:
- arena 链统计的 in-use 总量与 RSS/实际占用有稳定差距；
- 差距不随 arena 数量变化，`system_mem` 也不包含这部分；
- `mmap_scan` 在匿名映射起始处发现 `IS_MMAPPED` chunk，或发现大块非零 ANON 映射。

**Diagnosis**: 请求 >= `mmap_threshold`（默认 128KB，动态可升到约 32MB）时，glibc 直接
`mmap`，chunk 独立于 arena：

- 不在 arena chunk 链里；
- 不计入 `malloc_state.system_mem`；
- chunk 头在映射起始处，`size` 带 `IS_MMAPPED`（bit 1）。

**Verification**:

```bash
gcc -O2 -o /tmp/mmap_scan ../scripts/mmap_scan.c
/tmp/mmap_scan <core> 131072
# MMAPPED: chunk_size 与映射长度接近、16 字节对齐
# ANON   : 非 chunk 的大块匿名映射，需结合应用/NMT 判断
```

**注意**:
- 不要用 “system_mem - subheap 总和” 去估算 mmap 量，两者没有该等式关系。
- 非 chunk 的 ANON 映射可能是池化缓冲、JIT 代码或自定义分配器；本工具只给尺寸与头部样本，
  不下类型结论。
- 页大小从 core 的 `AT_PAGESZ` 读；跨架构时宿主 `sysconf` 会给出错误页大小。

**Next step**: 把 `mmap_scan` 的分桶与 arena 链分桶合并，得到全量 native 分配画像；对
ANON 大块结合进程侧统计（NMT、分配器统计、池配置）定位来源。
