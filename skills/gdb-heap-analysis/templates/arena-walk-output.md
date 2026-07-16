# Arena Walk Output Template

## Arena Summary

```
Arena[0] (main_arena) @ 0x{addr}, sys_mem={size} MB
Arena[1] @ 0x{addr}, sys_mem={size} MB
...
Total arenas: {count}
Largest: Arena[{n}] @ 0x{addr}, sys_mem={size} MB
```

## Arena Detail

```
Arena @ 0x{addr}
  top       @ 0x{top_addr}
  system_mem  = {sys_mem} MB
  max_system  = {max_sys} MB
  top size    = {top_size} MB
  Mode: {subheap|mmap|mixed}
```

## Subheap Chain

```
Subheap @ 0x{addr}, size={size} MB
Subheap @ 0x{addr}, size={size} MB
...
Total subheap: {total} MB
Gap (system_mem - subheap): {gap} MB → {direct mmap|none}
```

## Chunk Analysis

```
Chunk @ 0x{addr}
  prev_size = 0x{val}
  size      = 0x{val} ({actual_size} bytes)
  flags     = PREV_INUSE={0|1} IS_MMAPPED={0|1} NON_MAIN_ARENA={0|1}
```
