---
name: gdb-heap-analysis
description: GDB heap/arena memory analysis for core dump debugging. Use when analyzing glibc ptmalloc memory leaks, high memory usage, or arena corruption in core dumps. Triggers: (1) user asks about memory leak analysis, (2) core dump memory investigation, (3) arena/subheap/malloc_state analysis, (4) glibc heap debugging, (5) questions about malloc internals, (6) "heap分析", "内存泄漏", "arena分析", "core dump分析".
---

# GDB Heap Memory Analysis

Interactive skill for analyzing glibc ptmalloc heap structures in core dumps. Follow diagnostic workflow with human judgment at critical decision points.

## Workflow

```
Load core dump → Confirm symbols → Walk arenas → Analyze structure → Check distribution → Locate allocations
```

Each step requires observation and judgment - no automatic decisions.

## Step 1: Confirm Debug Symbols

Check if glibc debug symbols are available:

```gdb
ptype struct malloc_state
ptype struct malloc_chunk
```

**Judgment**:
- Outputs structure definition → Has symbols, use struct access
- "No symbol table" → No symbols, need manual offset lookup

### No Symbols Case

Check glibc version:

```bash
ldd --version  # on target machine
```

Or infer from core dump:

```gdb
info sharedlibrary libc
```

If no symbols, read [references/glibc-offsets.md](references/glibc-offsets.md) for known offsets by version.

## Step 2: Walk All Arenas

Find all arenas and identify the one with largest `system_mem`.

### With Symbols

```gdb
p &main_arena
p main_arena.system_mem
```

Walk the linked list:

```gdb
set $a = main_arena.next
while $a != &main_arena && $a != 0
  printf "Arena @ %p, sys_mem=%lu MB\n", $a, $a->system_mem / 1024 / 1024
  set $a = $a->next
end
```

### Without Symbols

Use offsets from references/glibc-offsets.md:

```gdb
set $arena = 0xfffd8c000020
x/gx $arena+0x888    # system_mem offset for glibc 2.28
x/gx $arena+0x870    # next offset
```

### Judgment Point

**Is any arena abnormally large?**

Compare arena sizes:
- Typical: < 100 MB per arena
- Suspicious: > 500 MB
- Definitely abnormal: > 1 GB

Record the address of largest arena for next step.

## Step 3: Analyze malloc_state Structure

Examine the arena's internal structure:

```gdb
p *(struct malloc_state *)$arena_addr
```

**Key fields to observe**:
- `top` - Address of top chunk (wilderness)
- `system_mem` - Total memory allocated from system
- `bins[]` - Free chunk bins
- `fastbinsY` - Fastbins array

### Judgment Point: Top Chunk Location

Check where `top` points:

```gdb
set $top = ((struct malloc_state *)$arena)->top
```

Compare `$top` address with `$arena_addr`:
- `$top` near `$arena_addr` (within 64MB range) → Traditional subheap mode
- `$top` in completely different address range → **Direct mmap mode**

Example abnormal pattern:
```
Arena @ 0xfffd8c000020
top   @ 0xfffcab6d86b0  ← Not in 0xfffd8c... range
→ Uses independent mmap regions, not subheap chain
```

## Step 4: Check Memory Distribution

Determine if memory comes from subheap chain or direct mmaps.

### Subheap Mode (traditional)

Check heap_info at `arena_addr - sizeof(heap_info)`:

```gdb
set $heap = $arena_addr - sizeof(heap_info)
x/3gx $heap
# +0: ar_ptr (should equal arena_addr)
# +8: prev (previous subheap)
# +16: size
```

Walk the prev chain:

```gdb
set $heap = $arena_addr - 32
while $heap != 0
  set $ar = *(void**)$heap
  if $ar != $arena_addr
    break
  end
  set $size = *(size_t*)($heap+16)
  printf "Subheap @ %p, size=%lu MB\n", $heap, $size/1024/1024
  set $heap = *(void**)($heap+8)  # prev pointer
end
```

### Judgment Point: Subheap vs system_mem Gap

Calculate:
- Sum of subheap sizes
- Compare with `system_mem`

**If gap > 1GB**: Arena has large direct mmap allocations outside subheap chain.

### Mmap Mode (modern glibc)

When subheap chain is short but `system_mem` is huge:

```gdb
info proc mappings
maint info sections
```

Look for anonymous mappings (no objfile) in address ranges not covered by subheaps.

Check top chunk's region:

```gdb
set $top = ((struct malloc_state *)$arena)->top
# Manually inspect which section contains $top
```

## Step 5: Locate Specific Allocations

### Examine Chunks

For any chunk address:

```gdb
set $chunk = 0xfffcab6d86b0
x/gx $chunk-8   # chunk header (prev_size + size with flags)
```

**Size field flags** (lowest 3 bits):
- Bit 0: PREV_INUSE
- Bit 1: IS_MMAPPED - **If 1, this is mmap allocation**
- Bit 2: NON_MAIN_ARENA

### Examine Bins

```gdb
p ((struct malloc_state *)$arena)->bins[0]@10
p ((struct malloc_state *)$arena)->fastbinsY
```

Large free chunks in bins may indicate freed but not returned to system.

## Key Judgment Points Summary

| Step | Check | Decision |
|------|-------|----------|
| 1 | Symbols? | Struct access vs manual offset |
| 2 | Arena size | >1GB = abnormal |
| 3 | Top location | Far from arena = mmap mode |
| 4 | Subheap vs sys_mem | >1GB gap = direct mmap |
| 5 | Chunk flags | IS_MMAPPED bit = mmap alloc |

## Common Issues

### main_arena not accessible

glibc static variable may not have exported symbol:

```gdb
info variables main_arena
```

If no result, trace backwards from any arena's `next` chain.

### heap_info undefined

Some glibc versions don't export `heap_info` type. Use fixed offset:
- sizeof(heap_info): usually 32-40 bytes
- Field offsets: ar_ptr=0, prev=8, size=16

### Memory access errors

Some addresses may be unmapped in core dump. Use Python for exception handling:

```python
import gdb
def read_ptr(addr):
    try:
        data = gdb.selected_inferior().read_memory(addr, 8)
        return int.from_bytes(bytes(data), 'little')
    except gdb.MemoryError:
        return None
```

## Resources

- [references/glibc-offsets.md](references/glibc-offsets.md) - Known offsets by glibc version
- [references/heap-structures.md](references/heap-structures.md) - Detailed struct layouts
- [references/diagnostic-examples.md](references/diagnostic-examples.md) - Real case studies