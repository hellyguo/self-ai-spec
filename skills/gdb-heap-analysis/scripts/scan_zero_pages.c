/*
 * scan_zero_pages.c —— 统计 core 某个 VA 区间内的“非零页”
 *
 * 用途：区分“真实占用”与“保留/未触碰的匿名映射”（core 会把零页也写出来）。
 *
 * 用法：
 *   gcc -O2 -o scan_zero_pages scan_zero_pages.c
 *   ./scan_zero_pages <core> <va_start> <size> <file_off_at_va_start>
 * 例：
 *   ./scan_zero_pages ./core <va_start> <size> <file_off>
 *
 * 输出：总页数、非零页数（MB）、连续非零段数、首个/最后一个非零页 VA。
 *
 * 注意：进程内存里的零页也可能是“真的全零数据”，需结合映射权限与业务判断；
 *      本工具只说“这页是否有非零字节”，不下结论。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr, "usage: %s <core> <va_start> <size> <file_off_at_va_start>\n", argv[0]);
        return 2;
    }
    const char *fn = argv[1];
    unsigned long long va0 = strtoull(argv[2], 0, 0);
    unsigned long long sz = strtoull(argv[3], 0, 0);
    unsigned long long off0 = strtoull(argv[4], 0, 0);

    int fd = open(fn, O_RDONLY);
    if (fd < 0) { perror("open"); return 2; }
    struct stat st;
    if (fstat(fd, &st) != 0) { perror("fstat"); return 2; }
    if (off0 + sz > (unsigned long long)st.st_size) {
        fprintf(stderr, "range exceeds file: need %llu, file %llu\n",
                off0 + sz, (unsigned long long)st.st_size);
        return 2;
    }
    unsigned char *m = mmap(NULL, (size_t)st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (m == MAP_FAILED) { perror("mmap"); return 2; }

    const unsigned long long pg = 4096;
    unsigned long long npg = sz / pg;
    unsigned long long nz = 0, runs = 0, prev = ~0ULL, first = 0, last = 0;

    for (unsigned long long i = 0; i < npg; i++) {
        uint64_t *q = (uint64_t *)(m + off0 + i * pg);
        int nzpage = 0;
        for (int j = 0; j < 512; j++) {
            if (q[j]) { nzpage = 1; break; }
        }
        if (!nzpage) continue;
        nz++;
        unsigned long long va = va0 + i * pg;
        if (!first) first = va;
        last = va;
        if (i != prev + 1) runs++;
        prev = i;
    }

    printf("va=[0x%llx,0x%llx) pages=%llu nonzero_pages=%llu (%.1f MiB) runs=%llu first=0x%llx last=0x%llx\n",
           va0, va0 + sz, npg, nz, (double)nz * 4.0 / 1024.0, runs, first, last);
    return 0;
}
