---
name: gdb-heap-analysis
description: GDB heap/arena memory analysis for core dump debugging. Use when analyzing glibc ptmalloc memory leaks, high memory usage, or arena corruption in core dumps. Triggers: (1) user asks about memory leak analysis, (2) core dump memory investigation, (3) arena/subheap/malloc_state analysis, (4) glibc heap debugging, (5) questions about malloc internals, (6) "heap分析", "内存泄漏", "arena分析", "core dump分析".
---

# GDB Heap Memory Analysis

Analyze glibc ptmalloc heap structures in core dumps. Human judgment required at each decision point.

## Workflow

```
Load core → Confirm symbols → Walk arenas → Analyze malloc_state → Check distribution → Locate allocations
```

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

```gdb
set $arena = 0xfffd8c000020
x/gx $arena+0x888    # system_mem (glibc 2.28)
x/gx $arena+0x870    # next
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
info proc mappings
```

Look for anonymous mappings not covered by subheaps.

## Step 5: Locate Specific Allocations

### Chunk Header

```gdb
set $chunk = 0xfffcab6d86b0
x/gx $chunk-8   # prev_size + size with flags
```

Size field flags (lowest 3 bits): PREV_INUSE(bit 0), IS_MMAPPED(bit 1), NON_MAIN_ARENA(bit 2)

### Bins

```gdb
p ((struct malloc_state *)$arena)->bins[0]@10
p ((struct malloc_state *)$arena)->fastbinsY
```

## Judgment Summary

| Step | Check | Decision |
|------|-------|----------|
| 1 | Symbols? | Struct access vs manual offset |
| 2 | Arena size | >1GB = abnormal |
| 3 | Top location | Far from arena = mmap mode |
| 4 | Subheap vs sys_mem | >1GB gap = direct mmap |
| 5 | Chunk flags | IS_MMAPPED = mmap alloc |

## Common Issues

- **main_arena not accessible**: `info variables main_arena`; trace backwards from any arena's `next` chain
- **heap_info undefined**: Use fixed offset (sizeof=32B, ar_ptr=0, prev=8, size=16)
- **Memory access errors**: Use Python helper with `gdb.MemoryError` exception handling

## Output Templates

- [templates/arena-walk-output.md](templates/arena-walk-output.md) - Arena walk and chunk analysis output format
- [templates/diagnostic-decision.md](templates/diagnostic-decision.md) - Pattern match and diagnosis result format

## Resources

- [references/glibc-offsets.md](references/glibc-offsets.md) - Known offsets by glibc version
- [references/heap-structures.md](references/heap-structures.md) - Detailed struct layouts
- [references/diagnostic-patterns.md](references/diagnostic-patterns.md) - Real case studies
