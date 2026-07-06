# glibc Heap Structures

Detailed explanation of ptmalloc data structures.

## malloc_state (Arena Header)

Each arena has a `malloc_state` structure containing:

### Core Fields

- **mutex**: Lock for thread safety
- **flags**: Arena flags (bitmask)
- **fastbinsY[10]**: Array of fastbin lists for small chunks
- **top**: Pointer to top chunk (wilderness)
- **last_remainder**: Last remainder chunk from splitting
- **bins[254]**: Normal bins (small and large)
- **binmap[4]**: Bitmap for non-empty bins
- **next**: Next arena in circular list
- **next_free**: Next arena in free list
- **attached_threads**: Count of threads using this arena
- **system_mem**: Total memory from system
- **max_system_mem**: Historical max of system_mem

### Memory Tracking

`system_mem` includes:
1. Memory from subheaps (heap_info structures)
2. Memory from direct mmap allocations

This is why subheap total may be less than system_mem.

## malloc_chunk (Chunk Header)

Every allocated/free chunk has this header:

```c
struct malloc_chunk {
    size_t prev_size;  // Size of previous chunk (if free)
    size_t size;       // Size of this chunk + flags
    // User data follows...
};
```

### Size Field Flags (lowest 3 bits)

- **PREV_INUSE (bit 0)**: Previous chunk is in use
- **IS_MMAPPED (bit 1)**: This chunk was allocated via mmap
- **NON_MAIN_ARENA (bit 2)**: Chunk belongs to non-main arena

Actual size = `size & ~0x7` (mask off flags)

### Pointer Arithmetic

For a pointer returned by malloc:
- User pointer = chunk address + 16 (two size_t words)
- To find chunk header: `user_ptr - 16`

## heap_info (Subheap Header)

Non-main arenas use heap_info for each subheap:

```c
struct heap_info {
    struct malloc_state *ar_ptr;  // Arena this subheap belongs to
    struct heap_info *prev;       // Previous subheap in chain
    size_t size;                  // Size of this subheap
    size_t mstate;                // Reserved
    // Padding to 32 bytes...
};
```

### Subheap Chain

Subheaps are linked via `prev` pointer:
- Each subheap is at most 64MB (HEAP_MAX_SIZE)
- Arena address = subheap_base + sizeof(heap_info)
- Walk backwards through `prev` to find all subheaps

### Memory Layout

```
+-------------------+  <- subheap_base
| heap_info (32B)   |
+-------------------+
| malloc_state      |  <- arena_addr = subheap_base + 32
+-------------------+
| chunks...         |
|                   |
+-------------------+  <- subheap_base + size
```

## Allocation Paths

### Small Allocations (< 128KB)

1. Check fastbins (for very small sizes)
2. Check small bins
3. Split from top chunk
4. Get more memory from subheap or new subheap

### Large Allocations (>= 128KB)

Direct mmap allocation:
- Not tracked in subheap chain
- Chunk has IS_MMAPPED flag
- Freed via munmap directly

This explains why system_mem can be much larger than subheap total.

## Bin Types

### Fastbins (10 bins)

- Sizes: 16, 24, 32, 40, 48, 56, 64, 72, 80, 88 bytes
- LIFO (last in, first out)
- Single linked list
- Not consolidated

### Small Bins (62 bins)

- Sizes: 16 to 1008 bytes (16-byte increments)
- FIFO
- Double linked list

### Large Bins (63 bins)

- Sizes: >= 1024 bytes
- Range-based (multiple sizes per bin)
- Sorted by size

### Unsorted Bin (1 bin)

- Temporary holding area
- Chunks freed but not yet categorized

## Top Chunk

The "wilderness" chunk at the end of available memory:
- Serves as source for new allocations
- When exhausted, arena requests more memory
- Location indicates memory source (subheap vs mmap)

## Arena Types

### main_arena

- Global variable in glibc
- Uses program's brk area initially
- Can also have heap_info subheaps

### Non-main Arenas

- One per thread (typically)
- Each has heap_info header
- Memory from mmap'd regions

## Memory Limits

### HEAP_MAX_SIZE = 64MB

Maximum size of a single subheap. Larger allocations use direct mmap.

### MMAP_THRESHOLD = 128KB

Allocations >= this size use mmap directly, bypassing arena.
