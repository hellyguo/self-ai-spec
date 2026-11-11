/*
 * mmap_scan.c —— 枚举 core 的匿名映射，识别 IS_MMAPPED chunk
 *
 * 背景：glibc 对 >= mmap_threshold（默认 128KB）的请求直接 mmap，chunk 独立于
 *       arena，不在 arena 的 chunk 链里，也不计入 malloc_state.system_mem。
 *       heap_scan.c 只能扫 arena 链，因此大块分配必须用本工具单独统计。
 *
 * 用法：
 *   gcc -O2 -o mmap_scan mmap_scan.c
 *   ./mmap_scan <core> [min_size]
 *   min_size 默认 131072（128KB），用于过滤小映射。
 *
 * 输出：
 *   - PT_LOAD 与文件映射（NT_FILE）统计
 *   - 匿名映射按 log2 大小的分桶
 *   - 疑似 IS_MMAPPED chunk：映射起始处的 chunk 头满足
 *       size & IS_MMAPPED、16 字节对齐、且 128KB <= size <= 映射长度
 *   - 其余大块匿名映射（如直接 mmap 的池化缓冲）列为 ANON，并给出头部样本
 *
 * 注意：
 *   - 页大小优先取 core 的 NT_AUXV(AT_PAGESZ)；跨架构分析时宿主 sysconf 不可用。
 *   - 仅支持 64 位 ELF core。
 *   - 非 chunk 的 ANON 映射无法仅凭 core 判断类型（可能是 [heap]、线程栈、vdso、
 *     池化缓冲或自定义分配器），需结合进程/JVM 的 NMT、pmap 或应用自身统计。
 *   - 映射长度可能大于 chunk size（相邻匿名 VMA 被内核合并），判定用上界容忍。
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

typedef struct { uint64_t start, end; } RANGE;

static RANGE *g_files;
static size_t g_nfiles;
static uint64_t g_page_size;   /* 目标进程页大小，来自 NT_AUXV/NT_FILE，而非宿主 */

static int range_is_file(uint64_t va) {
    for (size_t i = 0; i < g_nfiles; i++) {
        if (va >= g_files[i].start && va < g_files[i].end) return 1;
    }
    return 0;
}

/* 解析 core 的 NT_FILE note，记录所有文件映射区间。 */
static void parse_nt_file(unsigned char *base, size_t fsize, const Elf64_Phdr *ph) {
    if (ph->p_offset + ph->p_filesz > fsize) return;
    unsigned char *p = base + ph->p_offset;
    unsigned char *end = p + ph->p_filesz;

    while (p + 12 <= end) {
        uint32_t namesz = *(uint32_t *)p;
        uint32_t descsz = *(uint32_t *)(p + 4);
        uint32_t type   = *(uint32_t *)(p + 8);
        p += 12;
        size_t namesz_al = (namesz + 3u) & ~3u;
        size_t descsz_al = (descsz + 3u) & ~3u;
        if (p + namesz_al + descsz_al > end) break;

        if (type == NT_AUXV) {
            /* AT_PAGESZ 描述目标进程的页大小；跨架构分析时不能用宿主 sysconf。 */
            unsigned char *desc = p + namesz_al;
            for (uint32_t i = 0; i + 16 <= descsz; i += 16) {
                uint64_t a_type, a_val;
                memcpy(&a_type, desc + i, 8);
                memcpy(&a_val, desc + i + 8, 8);
                if (a_type == AT_PAGESZ && a_val >= 4096 &&
                    (a_val & (a_val - 1)) == 0) {
                    g_page_size = a_val;
                }
            }
        }
        if (type == NT_FILE && descsz >= 16) {
            unsigned char *desc = p + namesz_al;
            uint64_t count, page_size;
            memcpy(&count, desc, 8);
            memcpy(&page_size, desc + 8, 8);
            /* 部分内核在 NT_FILE 里写的 page_size 不可直接使用，仅作兜底 */
            if (!g_page_size && page_size >= 4096 &&
                (page_size & (page_size - 1)) == 0) {
                g_page_size = page_size;
            }
            /* 描述符：count, page_size, count*(start,end,file_ofs) */
            if (count > 0 && count < 1000000 && descsz >= 16 + count * 24) {
                RANGE *r = (RANGE *)calloc((size_t)count, sizeof(RANGE));
                if (r) {
                    for (uint64_t i = 0; i < count; i++) {
                        uint64_t start, end;
                        memcpy(&start, desc + 16 + i * 24, 8);
                        memcpy(&end, desc + 24 + i * 24, 8);
                        r[i].start = start;
                        r[i].end = end;
                    }
                    free(g_files);
                    g_files = r;
                    g_nfiles = (size_t)count;
                }
            }
        }
        p += namesz_al + descsz_al;
    }
}

static int printable(unsigned char c) { return c >= 32 && c < 127; }

/* 取头部可打印片段，非可打印字符以 '.' 代替。 */
static void sample_ascii(const unsigned char *q, size_t len, char *out, size_t outsz) {
    size_t j = 0;
    for (size_t i = 0; i < len && j + 1 < outsz; i++) {
        out[j++] = printable(q[i]) ? (char)q[i] : '.';
    }
    out[j] = 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <core> [min_size]\n", argv[0]);
        return 2;
    }
    const char *fn = argv[1];
    uint64_t min_size = (argc > 2) ? strtoull(argv[2], 0, 0) : 131072ULL;

    int fd = open(fn, O_RDONLY);
    if (fd < 0) { perror("open"); return 2; }
    struct stat st;
    if (fstat(fd, &st) != 0) { perror("fstat"); return 2; }
    size_t fsize = (size_t)st.st_size;
    unsigned char *base = mmap(NULL, fsize, PROT_READ, MAP_PRIVATE, fd, 0);
    if (base == MAP_FAILED) { perror("mmap"); return 2; }

    if (fsize < sizeof(Elf64_Ehdr) ||
        memcmp(base, ELFMAG, SELFMAG) != 0 ||
        base[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "not a 64-bit ELF core\n");
        return 2;
    }
    Elf64_Ehdr *eh = (Elf64_Ehdr *)base;
    if (eh->e_phoff + (uint64_t)eh->e_phnum * eh->e_phentsize > fsize) {
        fprintf(stderr, "bad program header table\n");
        return 2;
    }

    /* 先收集文件映射，用于区分匿名段。 */
    for (int i = 0; i < eh->e_phnum; i++) {
        Elf64_Phdr *ph = (Elf64_Phdr *)(base + eh->e_phoff + (uint64_t)i * eh->e_phentsize);
        if (ph->p_type == PT_NOTE) parse_nt_file(base, fsize, ph);
    }

    long host_pg = sysconf(_SC_PAGESIZE);
    if (host_pg <= 0) host_pg = 4096;
    uint64_t pg = g_page_size ? g_page_size : (uint64_t)host_pg;
    if (!g_page_size) {
        fprintf(stderr, "WARNING: target page size not found in core; "
                        "using host page size %ld\n", host_pg);
    }
    unsigned char *zero = (unsigned char *)calloc(1, (size_t)pg);
    if (!zero) { perror("calloc"); return 2; }

    uint64_t total_loads = 0, file_loads = 0, anon_loads = 0;
    uint64_t anon_bytes = 0, zero_bytes = 0;
    uint64_t anon_bucket_cnt[64] = {0}, anon_bucket_bytes[64] = {0};
    uint64_t mm_count = 0, mm_bytes = 0;
    /* chunk size -> 聚合（本工具只保留有限个不同尺寸） */
    typedef struct { uint64_t size, cnt, bytes, sample; } MMSIZE;
    MMSIZE mm[256];
    size_t nmm = 0;

    for (int i = 0; i < eh->e_phnum; i++) {
        Elf64_Phdr *ph = (Elf64_Phdr *)(base + eh->e_phoff + (uint64_t)i * eh->e_phentsize);
        if (ph->p_type != PT_LOAD || ph->p_filesz == 0) continue;
        if (ph->p_offset + ph->p_filesz > fsize) continue;

        total_loads++;
        uint64_t va = ph->p_vaddr;
        uint64_t len = ph->p_memsz ? ph->p_memsz : ph->p_filesz;
        uint64_t span = ph->p_filesz < len ? ph->p_filesz : len;
        int is_file = range_is_file(va) || range_is_file(va + span - 1);
        if (is_file) { file_loads++; continue; }

        anon_loads++;
        anon_bytes += len;

        /* 页扫描：只统计有内容的页，区分保留/未触碰。 */
        uint64_t npg = span / (uint64_t)pg;
        uint64_t nz = 0;
        for (uint64_t k = 0; k < npg; k++) {
            if (memcmp(base + ph->p_offset + k * (uint64_t)pg, zero, (size_t)pg) != 0) nz++;
        }
        zero_bytes += (npg - nz) * (uint64_t)pg;

        int lg = 0;
        for (uint64_t t = len; t > 1; t >>= 1) lg++;
        if (lg > 63) lg = 63;
        anon_bucket_cnt[lg]++;
        anon_bucket_bytes[lg] += len;

        if (len < min_size) continue;

        int is_mmapped = 0;
        uint64_t csize = 0;
        if (ph->p_filesz >= 16) {
            uint64_t raw = *(uint64_t *)(base + ph->p_offset + 8);
            csize = raw & ~7ULL;
            if ((raw & 2ULL) && csize >= min_size && csize <= len &&
                (csize & 0xfULL) == 0) {
                is_mmapped = 1;
                mm_count++;
                mm_bytes += csize;
                size_t k = 0;
                for (; k < nmm; k++) if (mm[k].size == csize) break;
                if (k == nmm && nmm < sizeof(mm) / sizeof(mm[0])) {
                    mm[k].size = csize; mm[k].sample = va; nmm++;
                }
                if (k < nmm) { mm[k].cnt++; mm[k].bytes += csize; }
            }
        }

        char smp[97];
        size_t lim = ph->p_filesz > 96 ? 96 : ph->p_filesz;
        sample_ascii(base + ph->p_offset, lim, smp, sizeof(smp));

        if (nz == 0) continue;  /* 全零保留区单独统计，不逐段列出 */

        printf("%s va=[0x%llx,0x%llx) len=0x%llx (%llu MiB) "
               "nonzero_pages=%llu/%llu %s sample=\"%s\"\n",
               is_mmapped ? "MMAPPED" : "ANON   ",
               (unsigned long long)va, (unsigned long long)(va + len),
               (unsigned long long)len, (unsigned long long)(len >> 20),
               (unsigned long long)nz, (unsigned long long)npg,
               is_mmapped ? "" : "(not a malloc chunk header)",
               smp);
    }

    printf("\ncore=%s size=%.2f GiB pagesize=%llu (%s) min_size=%llu\n",
           fn, (double)fsize / 1073741824.0, (unsigned long long)pg,
           g_page_size ? "from core" : "host fallback",
           (unsigned long long)min_size);
    printf("PT_LOAD=%llu file_backed=%llu anonymous=%llu anon_bytes=%.2f GiB "
           "zero_bytes=%.2f GiB (NT_FILE ranges=%zu)\n",
           (unsigned long long)total_loads, (unsigned long long)file_loads,
           (unsigned long long)anon_loads, (double)anon_bytes / 1073741824.0,
           (double)zero_bytes / 1073741824.0, g_nfiles);

    printf("\nanonymous mapping size buckets:\n");
    printf("%-8s %-10s %-14s\n", "log2", "count", "MiB");
    for (int i = 0; i < 64; i++) {
        if (!anon_bucket_cnt[i]) continue;
        printf("%-8d %-10llu %-14.1f\n", i,
               (unsigned long long)anon_bucket_cnt[i],
               (double)anon_bucket_bytes[i] / 1048576.0);
    }

    printf("\nIS_MMAPPED chunks (arena chain blind spot): count=%llu total=%.2f GiB\n",
           (unsigned long long)mm_count, (double)mm_bytes / 1073741824.0);
    for (size_t i = 0; i < nmm; i++) {
        printf("  chunk_size=%-12llu count=%-8llu total=%-10.1f MiB sample=0x%llx\n",
               (unsigned long long)mm[i].size, (unsigned long long)mm[i].cnt,
               (double)mm[i].bytes / 1048576.0, (unsigned long long)mm[i].sample);
    }
    if (!mm_count) {
        printf("  (none at mapping starts; large anon mappings may be direct "
               "mmap/pooled buffers, see ANON rows above)\n");
    }
    printf("NOTE: ANON rows include [heap], thread stacks, vdso and non-chunk "
           "native mappings; attribute them with process-side data (NMT/allocator "
           "stats), not core content alone.\n");

    free(zero);
    free(g_files);
    return 0;
}
