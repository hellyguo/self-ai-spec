# Diagnostic Patterns

## Pattern 1: Large Arena with Short Subheap Chain

**Symptoms**:
- Arena has `system_mem` > 1GB
- Subheap chain shows only 1-2 subheaps (< 128MB)
- Top chunk address far from arena address

**Diagnosis**: Modern glibc using direct mmap for large allocations

**Example** (glibc 2.28):
```
Arena[24] @ 0xfffd8c000020
system_mem = 1271 MB
Subheap chain: 1 subheap (64 MB)
top @ 0xfffcab6d86b0 ← not in arena address range
```

**Explanation**: 
- Subheap provides initial 64MB
- Remaining ~1207MB comes from direct mmap allocations
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
# If result is ~1GB, offset is correct
# If result is tiny or huge (like 0xFFFFFFFF), wrong offset
```