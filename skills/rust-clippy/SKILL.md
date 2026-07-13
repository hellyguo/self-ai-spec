---
name: rust-clippy
description: "Rust Clippy 静态分析技能：使用 cargo clippy 进行 Rust 代码质量检测，配合 cargo fix 自动修复"
---

# Rust Clippy 静态分析技能

## 概述

Clippy 是 Rust 官方 lint 工具，通过 `cargo clippy` 运行，可检测代码中的：

- **错误**：逻辑错误、死代码、未使用变量
- **代码风格**：不符合 Rust 惯用法的写法
- **性能**：低效模式、不必要的分配
- **安全**：不安全代码的潜在问题
- **正确性**：数值溢出、条件错误

## 执行流程

### 步骤1：确定项目路径

```bash
PROJECT_DIR=.  # Rust 项目根目录（包含 Cargo.toml）
```

### 步骤2：执行 Clippy 检查

```bash
# 基础检查
cargo clippy

# 检查所有目标（包括测试、示例）
cargo clippy --all-targets

# 检查特定包
cargo clippy -p <package_name>

# 严格模式（所有 lint 提升为 error）
cargo clippy -- --deny warnings

# 允许特定 lint
cargo clippy -- --allow <lint_name>

# 禁止特定 lint
cargo clippy -- --deny <lint_name>
```

### 步骤3：自动修复

```bash
# 应用安全建议的自动修复
cargo clippy --fix

# 允许可能破坏语义的修复
cargo clippy --fix --allow-dirty --allow-staged

# 检查修复结果
cargo clippy --all-targets
```

### 步骤4：指定输出格式

```bash
# JSON 格式（机器可读）
cargo clippy --message-format=json > clippy-report.json

# 简短格式
cargo clippy --message-format=short
```

## 常用 Lint 级别

| 级别 | 描述 | 示例 |
| --- | --- | --- |
| `allow` | 允许，不提示 | 默认禁用的 lint |
| `warn` | 警告（默认） | `clippy::pedantic` 中的部分 lint |
| `deny` | 错误，阻止编译 | 需严格禁止的模式 |
| `forbid` | 禁止，无法覆盖 | 安全关键 lint |

## Lint 组

| 组名 | 描述 | 严格程度 |
| --- | --- | --- |
| `clippy::all` | 所有稳定 lint（默认） | 适中 |
| `clippy::pedantic` | 非常严格的 lint | 严格 |
| `clippy::nursery` | 实验性 lint | 不稳定 |
| `clippy::style` | 代码风格相关 | 宽松 |
| `clippy::correctness` | 正确性相关 | 严格 |
| `clippy::complexity` | 代码复杂度 | 适中 |
| `clippy::perf` | 性能相关 | 适中 |
| `clippy::cargo` | Cargo 配置相关 | 宽松 |
| `clippy::restriction` | 限制性 lint（需手动启用） | 最严格 |

## 启用/禁用 Lint

### 命令行

```bash
# 启用 pedantic 组
cargo clippy -- --clippy::pedantic

# 禁用特定 lint
cargo clippy -- --allow clippy::too_many_arguments

# 组合使用
cargo clippy -- --clippy::pedantic --deny clippy::unwrap_used
```

### 代码内属性

```rust
//! #![warn(clippy::pedantic)]
//! #![allow(clippy::module_name_repetitions)]

// 文件级别
#![warn(clippy::pedantic)]
#![allow(clippy::too_many_lines)]

// 函数级别
#[allow(clippy::too_many_arguments)]
fn complex_function(a: i32, b: i32, c: i32, d: i32, e: i32) {}
```

### Cargo.toml 配置

```toml
[package.metadata.clippy]
# 工作区级别配置
[lints]
workspace = true

[workspace.lints.clippy]
pedantic = "warn"
unwrap_used = "deny"
too_many_arguments = "allow"
```

## 与 Cargo Fix 配合

```bash
# 检查并自动修复
cargo clippy --fix && cargo clippy --all-targets

# 修复特定 lint
cargo clippy --fix -- --allow clippy::all --warn clippy::unwrap_used

# 批量修复后验证
cargo clippy --fix --allow-dirty && cargo test
```

## CI 集成

### GitHub Actions

```yaml
name: Clippy
on: [push, pull_request]
jobs:
  clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - run: cargo clippy --all-targets -- --deny warnings
```

### pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/doublify/pre-commit-rust
    rev: v1.0
    hooks:
      - id: clippy
        args: ["--all-targets", "--", "--deny", "warnings"]
```

### Makefile

```makefile
clippy:
    cargo clippy --all-targets -- --deny warnings

clippy-fix:
    cargo clippy --fix --allow-dirty
    cargo clippy --all-targets -- --deny warnings
```

## 分析结果处理

### 统计 lint 类型

```bash
cargo clippy --message-format=json 2>/dev/null | \
  jq -r 'select(.message != null) | .message.code | .code // empty' | \
  sort | uniq -c | sort -nr
```

### 提取错误级别问题

```bash
cargo clippy --message-format=json 2>/dev/null | \
  jq -r 'select(.message != null and .message.level == "error") | .message.rendered'
```

### 生成摘要

```bash
echo "=== Clippy 分析报告 ==="
cargo clippy --message-format=json 2>/dev/null | \
  jq -r 'select(.message != null) | .message.level' | \
  sort | uniq -c | sort -rn | \
  awk '{print $2 ": " $1}'
```

## 典型使用场景

### 场景1：快速检查

```bash
cargo clippy --all-targets
```

### 场景2：严格模式（CI 推荐）

```bash
cargo clippy --all-targets -- --deny warnings
```

### 场景3：渐进式采用

```bash
# 第一步：修复默认 lint
cargo clippy --fix

# 第二步：启用 pedantic
cargo clippy --all-targets -- --warn clippy::pedantic

# 第三步：逐步收紧
cargo clippy --all-targets -- --warn clippy::pedantic --deny clippy::unwrap_used
```

### 场景4：修复后验证

```bash
cargo clippy --fix --allow-dirty && \
  cargo clippy --all-targets -- --deny warnings && \
  cargo test
```

## 最佳实践

1. **CI 中 deny warnings**：确保新代码不引入 clippy 警告
2. **渐进式采用**：从 `clippy::all` 开始，逐步启用 `pedantic`
3. **自动修复优先**：先用 `--fix` 处理自动可修复项
4. **代码属性抑制**：对合理的例外使用 `#[allow()]` 并附注释
5. **与 rustfmt 配合**：先格式化再 clippy
6. **定期更新**：`rustup update && cargo clippy` 保持 lint 规则最新

## 注意事项

1. **`--fix` 可能改变语义**：部分修复（如 `clippy::let_and_return`）可能改变行为，修复后务必运行测试
2. **`nursery` 不稳定**：实验性 lint 可能在未来版本变化
3. **`restriction` 需手动启用**：该组 lint 默认关闭，按需启用
4. **与 `#[deny(warnings)]` 冲突**：如果 Cargo.toml 中设置了 `deny(warnings)`，clippy 警告也会被拒绝

---
**技能版本**: 1.0.0
**工具**: cargo clippy (Rust 工具链组件)
**适用项目**: Rust 项目（包含 Cargo.toml）
**输出位置**: 标准输出或指定文件
