# Diagnostic Patterns

## Pattern 1: Large Arena with Short Subheap Chain

**Symptoms**:
- Arena has `system_mem` > 1GB
- Subheap chain shows only 1-2 subheaps (< 128MB)
- Top chunk address far from arena address

**Diagnosis**: Modern glibc using direct mmap for large allocations

**Example** (structure only, addresses are placeholders):
```
Arena[n] @ <arena_addr>
system_mem = <large_value> MB
Subheap chain: 1 subheap (<small_value> MB)
top @ <top_addr> ← not in arena address range
```

**Explanation**:
- Subheap provides initial 64MB
- Remaining memory comes from direct mmap allocations
- `system_mem` counts both sources

**Next step**: Check `info proc mappings` for anonymous regions containing top chunk.

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
# 按 4KB 页统计非零页（../scripts/scan_zero_pages.c）
gcc -O2 -o /tmp/scan_zero_pages ../scripts/scan_zero_pages.c
/tmp/scan_zero_pages <core> <va_start> <size> <file_off_at_va_start>
# → pages=<n> nonzero_pages=<m> runs=<k> ...
```

**Rule**: 判断真实占用用“非零页 × 4KB”，不要用 core 文件大小；泄漏定位看 in-use chunk 统计。
