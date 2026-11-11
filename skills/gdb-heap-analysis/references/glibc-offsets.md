# glibc malloc_state / heap_info Offsets

Offsets for `struct malloc_state` fields by glibc version (64-bit, LP64).

> **两种运行验证方式，优先用第 1 种**
>
> 1. **用已知 top 指针反查**（无需符号，最可靠）：在 libc 可写段里搜 top 值，命中地址减 `0x60` 即 arena 基址，再用 `system_mem`/`next` 校验。
> 2. 有 debuginfo 时：`p &((struct malloc_state *)0)->next` 等直接取偏移。

## How to Verify Offsets

```gdb
p &((struct malloc_state *)0)->next
p &((struct malloc_state *)0)->system_mem
p &((struct malloc_state *)0)->top
```

## Offset Table

### glibc 2.26 – 2.31（64 位）

| Field | Offset (hex) | Offset (decimal) |
|-------|-------------|------------------|
| mutex | 0x0 | 0 |
| flags | 0x4 | 4 |
| have_fastchunks | 0x8 | 8 |
| fastbinsY[0] | 0x10 | 16 |
| top | **0x60** | **96** |
| last_remainder | 0x68 | 104 |
| bins[0] | 0x70 | 112 |
| binmap[0] | 0x860 | 2144 |
| next | **0x870** | **2160** |
| next_free | 0x878 | 2168 |
| attached_threads | 0x880 | 2176 |
| system_mem | **0x888** | **2184** |
| max_system_mem | 0x890 | 2192 |
| sizeof(malloc_state) | 0x898 | 2200 |

> 2.28 的 `malloc_state` 与 `heap_info` 偏移在 aarch64 与 x86_64 上一致；
> 不同发行版/补丁可能有增删字段，务必用符号或“top 反查 + system_mem 校验”现场确认。

### glibc ≤ 2.25（无 have_fastchunks）

| Field | Offset (hex) |
|-------|-------------|
| mutex | 0x0 |
| flags | 0x4 |
| fastbinsY[0] | 0x8 |
| top | 0x58 |
| last_remainder | 0x60 |
| bins[0] | 0x68 |
| binmap[0] | 0x858 |
| next | 0x868 |
| next_free | 0x870 |
| attached_threads | 0x878 |
| system_mem | 0x880 |
| max_system_mem | 0x888 |

> 该表按字段顺序推算；不同发行版/补丁可能有增删字段，务必用符号或实测校验。

### glibc 2.32+

字段布局在 2.32+ 有调整（`have_fastchunks` 等），**不要直接套用上表**；
优先用调试符号，或用 “top 反查 + system_mem 校验” 的方式现场确认。

## heap_info Offsets

### glibc 2.26 – 2.29

| Field | Offset |
|-------|--------|
| ar_ptr | 0 |
| prev | 8 |
| size | 16 |
| mprotect_size | 24 |

`sizeof(heap_info) = 32`；`ar_ptr` 通常 = 堆起始 + 0x20（即 `malloc_state` 紧跟在 heap_info 之后）。

### glibc 2.30+

新增 `pagesize` 字段（`ar_ptr/prev/size/mprotect_size/pagesize`），`sizeof` 变为 40→对齐 48。
用 `ar_ptr` 读出的地址反推更稳，不要写死 `+0x20`。

## Notes

1. 以上均为 **64-bit LP64**；aarch64 与 x86_64 相同（指针 8B、int 4B）。32 位系统偏移不同。
2. `bins` 是 254 个 `mchunkptr`（`bins[0]` 为 unsorted bin 的 fd/bk 头），不是 128 个。
3. `next` 把各 arena 串成**环形**链表，回到 `main_arena` 即结束。
4. `system_mem` 统计该 arena 从 subheap 与 direct mmap 获得的全部内存。
5. 2.28 的 `heap_info` 没有 `pagesize` 字段——网上不少“2.28 偏移表”把它算进去，导致 +8 错位。

## Verification Without Symbols（可直接执行）

```gdb
# 已知堆里最后一块（top 指针）为 <top_value>，在 libc 数据段搜它
find /g <libc_rw_start>, <libc_rw_end>, <top_value>
# 假设命中 <hit_addr>
set $ma = <hit_addr> - 0x60
x/1gx $ma+0x888        # system_mem，应为合理大小
x/1gx $ma+0x870        # next，应为另一个 arena 或回到自身
x/1gx $ma+0x60         # top，应等于 <top_value>（回环校验）
```

> 用 `find` 时只搜 libc 的 **RW 数据段**（通常 64KB），不要对整堆 `find`。
