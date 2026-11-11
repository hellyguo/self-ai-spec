/*
 * heap_scan.c —— 直接扫描 core 文件的 ptmalloc chunk 链
 *
 * 适用：core 很大（>2~4GB）或 chunk 数上百万，gdb 逐地址读太慢。
 * 前提：堆 VA 范围在文件中的偏移是线性的，即
 *         file_off = FILE_OFF + (va - HEAP_START)
 *       若堆跨多个 PT_LOAD，要求各段 (p_offset - p_vaddr) 相同（常见）。
 *
 * 用法：
 *   gcc -O2 -o heap_scan heap_scan.c
 *   ./heap_scan <core> <heap_start> <heap_end> <file_off_at_heap_start> [target_size]
 * 例：
 *   ./heap_scan ./core <heap_start> <heap_end> <file_off> 4096
 *
 * 输出：
 *   chunks/inuse_chunks/inuse_bytes/free_bytes/bad/last
 *   max_free_chunk
 *   按 log2(size) 分桶的 in-use/free 计数与字节数
 *   target_size 样本（前 6 个）的 ASCII 内容
 *
 * 注意：
 *   - size 在 chunk+8，低 3 位是标志；in-use 由“下一块”的 PREV_INUSE 判定。
 *   - 对象内部指针是进程 VA，不是本程序的 mmap 指针；要解引用需再 va2p()。
 *   - 校验失败即停（bad>0 才怀疑堆破坏）。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <string.h>

static unsigned char *M;
static unsigned long long HEAP_START, HEAP_END, FSTART;

static inline unsigned char *va2p(unsigned long long va) {
    return M + FSTART + (va - HEAP_START);
}

/* core 的文件偏移与 VA 不保证 8 字节对齐，用 memcpy 避免未对齐读。 */
static inline unsigned long long rd64(const void *p) {
    unsigned long long v;
    memcpy(&v, p, sizeof(v));
    return v;
}

typedef struct { unsigned long long cnt, bytes; unsigned long long sample[6]; } BUCKET;
static BUCKET b_in[64], b_free[64];
static int s_in[64];

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr, "usage: %s <core> <heap_start> <heap_end> <file_off_at_heap_start> [target_size]\n", argv[0]);
        return 2;
    }
    const char *fn = argv[1];
    HEAP_START = strtoull(argv[2], 0, 0);
    HEAP_END   = strtoull(argv[3], 0, 0);
    FSTART     = strtoull(argv[4], 0, 0);
    unsigned long long target = (argc > 5) ? strtoull(argv[5], 0, 0) : 0;

    int fd = open(fn, O_RDONLY);
    if (fd < 0) { perror("open"); return 2; }
    struct stat st;
    if (fstat(fd, &st) != 0) { perror("fstat"); return 2; }
    if (FSTART + (HEAP_END - HEAP_START) > (unsigned long long)st.st_size) {
        fprintf(stderr, "mapping out of file range: need %llu, file %llu\n",
                FSTART + (HEAP_END - HEAP_START), (unsigned long long)st.st_size);
        return 2;
    }
    size_t mlen = (size_t)st.st_size;
    M = mmap(NULL, mlen, PROT_READ, MAP_PRIVATE, fd, 0);
    if (M == MAP_FAILED) { perror("mmap"); return 2; }

    unsigned long long p = HEAP_START, n = 0;
    unsigned long long in_chunks = 0, in_bytes = 0, free_bytes = 0, bad = 0;
    unsigned long long max_free = 0, max_free_va = 0, last = 0;

    while (p + 16 <= HEAP_END) {
        unsigned char *q = va2p(p);
        unsigned long long sz = rd64(q + 8) & ~7ULL;
        if (sz < 16 || sz > (HEAP_END - p) || (sz & 0xf)) {
            bad++;
            printf("BAD at 0x%llx size=0x%llx prev_size=0x%llx\n", p, sz, rd64(q));
            break;
        }
        unsigned long long next = p + sz;
        int in_use;
        if (next + 16 > HEAP_END) {
            /* 最后一块：下一块头部已在堆外，不能读 PREV_INUSE，按 top/free 处理 */
            in_use = 0;
        } else {
            in_use = rd64(va2p(next) + 8) & 1ULL;
        }

        int lg = 0;
        unsigned long long t = sz;
        while (t > 1) { t >>= 1; lg++; }
        if (lg > 63) lg = 63;

        if (in_use) {
            b_in[lg].cnt++;
            b_in[lg].bytes += sz;
            in_bytes += sz;
            in_chunks++;
            if (target && sz == target && s_in[lg] < 6) {
                b_in[lg].sample[s_in[lg]++] = p;
            }
        } else {
            b_free[lg].cnt++;
            b_free[lg].bytes += sz;
            free_bytes += sz;
            if (sz > max_free) { max_free = sz; max_free_va = p; }
        }
        last = p;
        n++;
        p = next;
        if (n > 400000000ULL) { printf("ABORT: too many chunks\n"); break; }
    }

    printf("heap=[0x%llx,0x%llx) file_off=0x%llx target=%llu\n",
           HEAP_START, HEAP_END, FSTART, target);
    printf("chunks=%llu inuse_chunks=%llu inuse_bytes=%llu (%.2f GiB) "
           "free_bytes=%llu (%.2f GiB) bad=%llu last=0x%llx\n",
           n, in_chunks, in_bytes, (double)in_bytes / 1073741824.0,
           free_bytes, (double)free_bytes / 1073741824.0, bad, last);
    if (bad) {
        printf("WARNING: statistics truncated at first bad chunk; "
               "inuse_bytes/inuse_chunks are NOT reliable\n");
    }
    printf("NOTE: arena chunk chain only; IS_MMAPPED allocations are not included "
           "(use mmap_scan.c)\n");
    printf("max_free_chunk=0x%llx at 0x%llx\n", max_free, max_free_va);

    printf("\n%-4s %-14s %-16s %-14s %-16s\n", "lg", "inuse_cnt", "inuse_MiB", "free_cnt", "free_MiB");
    for (int i = 0; i < 64; i++) {
        if (!b_in[i].cnt && !b_free[i].cnt) continue;
        printf("%-4d %-14llu %-16.1f %-14llu %-16.1f\n",
               i, b_in[i].cnt, (double)b_in[i].bytes / 1048576.0,
               b_free[i].cnt, (double)b_free[i].bytes / 1048576.0);
    }

    if (target) {
        printf("\ntarget(%llu) samples:\n", target);
        for (int lg = 0; lg < 64; lg++) {
            for (int k = 0; k < s_in[lg]; k++) {
                unsigned long long va = b_in[lg].sample[k];
                if (!va) continue;
                unsigned char *q = va2p(va);
                unsigned long long sz = *(uint64_t *)(q + 8) & ~7ULL;
                if (sz != target) continue;
                printf("  va=0x%llx size=%llu |", va, sz);
                int lim = sz > 96 ? 96 : (int)sz;
                for (int j = 0; j < lim; j++) {
                    unsigned char c = q[j];
                    putchar(c >= 32 && c < 127 ? c : '.');
                }
                printf("|\n");
            }
        }
    }
    return 0;
}
