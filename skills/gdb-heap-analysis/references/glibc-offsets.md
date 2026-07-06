# glibc malloc_state Offsets

Offsets for `struct malloc_state` fields by glibc version.

## How to Verify Offsets

If you have glibc debug symbols:

```gdb
p &((struct malloc_state *)0)->next
p &((struct malloc_state *)0)->system_mem
p &((struct malloc_state *)0)->top
```

## Offset Table

### glibc 2.28 - 2.31 (x86_64)

| Field | Offset (hex) | Offset (decimal) |
|-------|-------------|------------------|
| mutex | 0x0 | 0 |
| flags | 0x4 | 4 |
| have_fastchunks | 0x8 | 8 |
| fastbinsY[0] | 0x10 | 16 |
| top | 0x860 | 2144 |
| last_remainder | 0x868 | 2152 |
| bins[0] | 0x870 | 2160 |
| next | 0x870 | 2160 |
| next_free | 0x878 | 2168 |
| attached_threads | 0x880 | 2176 |
| system_mem | 0x888 | 2184 |
| max_system_mem | 0x890 | 2192 |

Note: `bins` array overlaps with `next` in the struct union.

### glibc 2.17 - 2.27 (x86_64)

| Field | Offset (hex) |
|-------|-------------|
| mutex | 0x0 |
| flags | 0x4 |
| fastbinsY[0] | 0x8 |
| top | 0x858 |
| last_remainder | 0x860 |
| bins[0] | 0x868 |
| next | 0x868 |
| system_mem | 0x880 |

### glibc 2.35+ (x86_64)

Offset may change. Always verify with debug symbols or reverse engineering.

## heap_info Offsets

| Field | Offset |
|-------|--------|
| ar_ptr | 0 |
| prev | 8 |
| size | 16 |
| mstate | 24 |

sizeof(heap_info) = 32 bytes (typically)

## Notes

1. Offsets are for x86_64. 32-bit systems have different offsets.
2. `bins` is a large array (254 elements) that follows `last_remainder`.
3. `next` pointer is used to link arenas in a circular list.
4. `system_mem` tracks all memory from both subheaps and direct mmaps.

## Verification Without Symbols

If you don't have debug symbols but know the glibc version:

1. Find an arena address with valid `system_mem` value
2. Search around expected offsets for reasonable values
3. Verify by walking the arena chain

Example verification:

```gdb
set $arena = 0xfffd8c000020
# Try offset 0x888 for system_mem
x/gx $arena+0x888
# Should see a reasonable size (e.g., 0x4f7e0000 = 1.2GB)

# Try offset 0x870 for next
x/gx $arena+0x870
# Should be NULL (end of chain) or another valid arena address
```
