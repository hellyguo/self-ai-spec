# 适用边界：glibc、native 与 Java 进程

本技能只分析 **glibc ptmalloc 管理的 native 内存**。core 里能看到所有虚拟内存，
但“能看到映射”不等于“能解释归属”。先确认分配路径，再决定是否用本技能。

## 1. 能覆盖的分配

- C/C++ 直接调用 `malloc`/`calloc`/`realloc`/`new`，且链接的是 glibc。
- JNI 库、第三方 native 库中的 glibc 分配。
- JVM 自身的 native 分配中，最终走 glibc `malloc` 的部分（例如 `os::malloc`
  路径；具体以 JDK 实现和启动参数为准）。
- JVM/框架通过 glibc 申请的大块内存：`>= mmap_threshold` 时成为 `IS_MMAPPED`
  chunk，可用 `mmap_scan` 统计。

## 2. 不能覆盖的内存

- Java 堆（G1/ZGC 等的 reserved/committed 区域）。
- Metaspace、CodeCache、压缩类空间等 JVM 用 `mmap` 自行管理的区域。
- 非 glibc 分配器：jemalloc、tcmalloc、mimalloc 等替换 `malloc` 后，ptmalloc
  的 arena/chunk 布局不再成立。
- 自定义池的内部状态：即使底层用 `malloc`，池的 freelist/位图/配额不体现在
  ptmalloc 结构里，可达性判断也会失真。
- GPU/驱动、共享内存、文件映射等非堆内存。

## 3. Java / Netty 场景对照

| 分配路径 | 底层 | 本技能可见性 |
|---|---|---|
| `ByteBuffer.allocateDirect`（小块） | JVM native `malloc` → glibc | 在 arena 链里，按尺寸指纹定位 |
| `ByteBuffer.allocateDirect`（大块） | glibc 直接 `mmap` | `IS_MMAPPED`，用 `mmap_scan` |
| Netty `allocateDirectNoCleaner`（小块） | `Unsafe.allocateMemory` → `malloc` | 在 arena 链里 |
| Netty pooled chunk（常见 16MB） | native `malloc` → glibc `mmap` | 映射起始处的 `IS_MMAPPED` chunk |
| Netty 使用 `mmap` 的自管理池 | 直接 `mmap` | 显示为 ANON，需结合池统计 |
| JVM 堆 / Metaspace / CodeCache | JVM 自行 `mmap` | 显示为 ANON，不能归属到 Java 对象 |
| jemalloc/tcmalloc 替换分配器 | 非 glibc | 不适用，改用对应分配器工具 |

注意：

- “DirectByteBuffer 有 Cleaner”不代表分配路径不同；关键是底层走 `malloc` 还是
  直接 `mmap`，以及请求大小是否超过 `mmap_threshold`。
- `mmap_threshold` 是动态的：释放 mmapped chunk 后可能上调（最高约 32MB），
  同一个请求大小在不同进程里可能落到不同的分配路径。
- core 中的 ANON 大段可能是 JVM 堆、JIT 代码、线程栈或池化缓冲，仅凭内容无法
  可靠区分，必须结合进程侧信息。

## 4. 选择工具的顺序

1. 先确认进程是否使用 glibc（`ldd`、`/proc/<pid>/maps`、启动参数）。
2. 用 `heap_scan` 统计 arena 链内分配（小块 `malloc` 泄漏主体）。
3. 用 `mmap_scan` 统计 `IS_MMAPPED` 与大块 ANON（大块 native 分配）。
4. 用 JDK NMT（`-XX:NativeMemoryTracking=summary` + `jcmd VM.native_memory`）
   或框架自带指标，给 ANON 段补上归属。
5. 若使用 jemalloc/tcmalloc，停止使用本技能，改用其 heap profile。

## 5. 结论表述要求

- 明确写“本结论覆盖 arena 链”还是“覆盖 arena + mmap”。
- 对无法归属的 ANON 映射，写“未归属”，不要猜成 Java 对象或具体类。
- 对自定义分配器，先声明“可达性规则不适用”，再给基于分配器元数据的结论。
