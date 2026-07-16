---
name: rust-flamegraph
description: Rust 性能分析技能：通过 cargo flamegraph 生成火焰图(SVG)，定位 CPU 热点函数并量化占比。适用于 Rust 项目性能瓶颈定位、热点分析、优化验证。触发场景：(1)分析 Rust 代码性能瓶颈，(2)定位 CPU 热点函数，(3)量化函数调用占比，(4)优化前后对比验证，(5)bench/unittest 性能不达预期时根因分析。
---

# Rust Flamegraph 性能分析

## 前置条件

```bash
cargo install cargo-flamegraph
sudo sysctl kernel.perf_event_paranoid=0  # 允许非 root 采样
```

## 工作流

### Step 1: 确定分析目标

明确要分析的操作和测试入口：
- 哪个函数/模块需要分析？
- 对应的测试在哪里？（lib unit test / 集成测试 / bench）
- 预期的性能瓶颈在哪？（IO / CPU / 内存分配 / 锁争用）

### Step 2: 准备测试入口

**优先使用集成测试**（`tests/` 目录），`cargo flamegraph --unit-test` 对 lib 内测试支持不稳定。

```
# 集成测试（推荐）
cargo flamegraph --dev [OPTIONS] --test <test_file> -- <test_name> [test_args]

# bench
cargo flamegraph --dev [OPTIONS] --bench <bench_name> -- <bench_args>
```

**关键原则**：
- 测试函数内用 `std::time::Instant` 计时并 `eprintln!` 输出，配合 `--nocapture`
- 测试数据量要足够大（建议 10w+ 操作），否则采样点不足
- 随机数据范围要足够大，避免重复（如 0..5000 而非 0..500）
- 将耗时操作集中在单个测试函数中，避免 build 阶段混入火焰图

**典型测试结构**：
```rust
#[test]
fn perf_xxx() {
    // 1. 准备数据（不计入测量）
    let data = prepare_data();
    
    // 2. 计时执行（这是火焰图分析的目标）
    let start = Instant::now();
    for item in &data {
        target_function(item);
    }
    let elapsed = start.elapsed();
    
    // 3. 输出结果
    eprintln!("ops: {:.0}/s, per_op: {:.2?}", 
        count as f64 / elapsed.as_secs_f64(), elapsed / count as u32);
}
```

### Step 3: 临时移除 #[inline] 并生成火焰图

**关键**：`--no-inline` 仅控制编译器内联策略，源码中 `#[inline]` 标注的函数仍会被内联导致火焰图无法捕获。需先注释掉所有 `#[inline]`。

```bash
# 1. 注释掉所有 #[inline]（分析前）
fd -t f -e rs -X sed -i 's/#\[inline/\/\/ #\[inline/g' {}

# 2. 生成火焰图
cargo flamegraph \
  --dev \                          # debug 编译（保留函数名）
  --no-inline \                    # 不内联，保留函数调用栈
  --image-width 1500 \             # 宽图，看清函数名
  --freq 8000 \                    # 采样频率 8000Hz
  --palette rust \                 # Rust 友好配色
  --test <test_file> -- <test_name> --nocapture
```

**参数说明**：

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `--dev` | debug 编译，保留符号 | 必选 |
| `--no-inline` | 禁止编译器内联，展开调用栈 | 推荐（需配合源码注释 #[inline]） |
| `--image-width` | SVG 宽度(px) | 1500-2000 |
| `--freq` | perf 采样频率(Hz) | 8000-99999 |
| `--palette` | 配色方案 | rust / io / hot |
| `--test` | 集成测试文件名 | 对应 tests/ 下的文件 |
| `--bench` | bench 文件名 | benches/ 下的文件 |

**输出**: 项目根目录生成 `flamegraph.svg`

```bash
# 3. 恢复 #[inline]（分析后）
fd -t f -e rs -X sed -i 's/\/\/ #\[inline/#\[inline/g' {}
```

> **注意**：务必在分析后恢复 `#[inline]`，否则生产构建性能会严重退化。

### Step 4: 提取热点数据

从 SVG 中提取函数占比（自动化脚本）：

```bash
# 提取热点函数及占比，按占比降序
rg '<title>' flamegraph.svg | \
  sed 's/.*<title>\(.*\)<\/title>.*/\1/' | \
  rg -v 'kernel|syscall|page_fault|_dl_|glibc|__GI_|_start|clone|thread_start|_int_free|_int_malloc|cfree|libc_start' | \
  sort -t'(' -k2 -rn | head -30
```

**输出格式**: `function_name (N samples, X.XX%)`

**重点关注**：
- 项目自身函数（含 crate 名或模块路径）
- 标准库中的热点（`alloc::`, `core::`, `DashMap` 等）
- 内存分配相关（`malloc`, `_int_malloc`, `sysmalloc`）

### Step 5: 分析热点

**常见热点模式及优化方向**：

| 热点模式 | 典型占比 | 优化方向 |
|----------|----------|----------|
| `str::split` + `fold` | 10-15% | 预计算/缓存编码结果 |
| `DashMap::insert` | 10-20% | 减少写入/批量写入/Arc<str> 替代 String key |
| `DashMap::get` | 5-15% | 缓存查找结果/减少查表次数 |
| `alloc::fmt::format` | 2-5% | 预分配 String/避免热路径 format! |
| `String::hash` | 3-10% | Arc<str> 替代 String/换用更快的 hasher |
| `malloc/_int_malloc` | 5-15% | 对象池/预分配/减少 clone |
| `malloc_consolidate` | 1-3% | 减少内存碎片/用 jemalloc |
| `Drop` (析构) | 5-10% | 延迟析构/对象池复用 |
| `Arc::clone` | 1-5% | 减少引用计数操作/传引用 |

### Step 6: 量化对比

优化前后用相同参数生成火焰图，对比：
1. 同一函数占比变化
2. 总采样时间变化
3. `eprintln!` 输出的 ops/s 变化

**火焰图管理**：
```bash
# 重命名保留（SVG 被 .gitignore 排除，不提交）
mv flamegraph.svg flamegraph_<scenario>_<timestamp>.svg
```

## 常见问题

### perf_event_paranoid 报错
```
Error: Access to performance monitoring and observability operations is limited
```
解决: `sudo sysctl kernel.perf_event_paranoid=0`

### no automatically selectable target
```
Error: crate has no automatically selectable target
```
解决: 用 `--test <file>` 或 `--bench <file>` 指定目标，而非 `--unit-test`

### samples too few
火焰图信息稀疏 → 提高测试数据量或提高 `--freq`

### 火焰图中 inline 函数缺失
源码 `#[inline]` 标注的函数在火焰图中不可见 → 临时注释掉 `#[inline]` 后重新生成：
```bash
fd -t f -e rs -X sed -i 's/#\[inline/\/\/ #\[inline/g' {}
# 生成火焰图后恢复：
fd -t f -e rs -X sed -i 's/\/\/ #\[inline/#\[inline/g' {}
```

### build_trie 阶段占比过高
测试中 build 阶段被采样 → 在测试函数中仅对目标操作计时，build 放在计时外
