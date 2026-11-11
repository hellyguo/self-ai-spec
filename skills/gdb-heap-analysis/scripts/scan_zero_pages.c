/*
 * scan_zero_pages.c —— 统计 core 某个 VA 区间内的“非零页”
 *
 * 用途：区分“真实占用”与“保留/未触碰的匿名映射”（core 会把零页也写出来）。
 *
 * 用法：
 *   gcc -O2 -o scan_zero_pages scan_zero_pages.c
 *   ./scan_zero_pages <core> <va_start> <size> <file_off_at_va_start> [page_size]
 * 例：
 *   ./scan_zero_pages ./core <va_start> <size> <file_off>
 *
 * 页大小：默认从 core 的 NT_AUXV(AT_PAGESZ) 读取；跨架构分析必须用它，
 *         不能用宿主 sysconf。可显式传 page_size 覆盖。
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
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/mman.h>
#include <sys/stat.h>

/* 从 core 的 NT_AUXV 读取 AT_PAGESZ；跨架构分析时不能依赖宿主页大小。 */
static unsigned long long core_page_size(unsigned char *base, size_t fsize) {
    if (fsize < sizeof(Elf64_Ehdr) || memcmp(base, ELFMAG, SELFMAG) != 0 ||
        base[EI_CLASS] != ELFCLASS64) {
        return 0;
    }
    Elf64_Ehdr *eh = (Elf64_Ehdr *)base;
    if (eh->e_phoff + (uint64_t)eh->e_phnum * eh->e_phentsize > fsize) return 0;

    for (int i = 0; i < eh->e_phnum; i++) {
        Elf64_Phdr *ph = (Elf64_Phdr *)(base + eh->e_phoff + (uint64_t)i * eh->e_phentsize);
        if (ph->p_type != PT_NOTE || ph->p_offset + ph->p_filesz > fsize) continue;
        unsigned char *p = base + ph->p_offset;
        unsigned char *end = p + ph->p_filesz;
        while (p + 12 <= end) {
            uint32_t namesz, descsz, type;
            memcpy(&namesz, p, 4);
            memcpy(&descsz, p + 4, 4);
            memcpy(&type, p + 8, 4);
            p += 12;
            size_t na = (namesz + 3u) & ~3u;
            size_t da = (descsz + 3u) & ~3u;
            if (p + na + da > end) break;
            if (type == NT_AUXV) {
                unsigned char *desc = p + na;
                for (uint32_t k = 0; k + 16 <= descsz; k += 16) {
                    uint64_t a_type, a_val;
                    memcpy(&a_type, desc + k, 8);
                    memcpy(&a_val, desc + k + 8, 8);
                    if (a_type == AT_PAGESZ && a_val >= 4096 &&
                        (a_val & (a_val - 1)) == 0) {
                        return a_val;
                    }
                }
            }
            p += na + da;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr, "usage: %s <core> <va_start> <size> <file_off_at_va_start> [page_size]\n"
                        "       page_size omitted = read AT_PAGESZ from core (fallback: host)\n", argv[0]);
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

    long pg = (argc > 5) ? (long)strtoull(argv[5], 0, 0) : 0;
    const char *pg_src = "arg";
    if (pg <= 0) {
        pg = (long)core_page_size(m, (size_t)st.st_size);
        pg_src = "core";
    }
    if (pg <= 0) {
        pg = sysconf(_SC_PAGESIZE);
        pg_src = "host fallback";
    }
    if (pg <= 0) { pg = 4096; pg_src = "default"; }
    unsigned char *zero = (unsigned char *)calloc(1, (size_t)pg);
    if (!zero) { perror("calloc"); return 2; }
    unsigned long long npg = sz / (unsigned long long)pg;
    unsigned long long nz = 0, runs = 0, prev = ~0ULL, first = 0, last = 0;

    for (unsigned long long i = 0; i < npg; i++) {
        unsigned char *q = m + off0 + i * (unsigned long long)pg;
        if (memcmp(q, zero, (size_t)pg) == 0) continue;
        nz++;
        unsigned long long va = va0 + i * (unsigned long long)pg;
        if (!first) first = va;
        last = va;
        if (i != prev + 1) runs++;
        prev = i;
    }

    printf("va=[0x%llx,0x%llx) pagesize=%ld (%s) pages=%llu nonzero_pages=%llu (%.1f MiB) runs=%llu first=0x%llx last=0x%llx\n",
           va0, va0 + sz, pg, pg_src, npg, nz,
           (double)nz * (double)pg / 1048576.0, runs, first, last);
    return 0;
}
