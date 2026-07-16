---
name: rust-clippy
description: "Rust Clippy 静态分析技能：使用 cargo clippy 进行 Rust 代码质量检测，配合 cargo fix 自动修复"
---

# Rust Clippy 静态分析技能

## 执行流程

### 步骤1：确定项目路径

```bash
PROJECT_DIR=.  # Rust 项目根目录（包含 Cargo.toml）
```

### 步骤2：执行 Clippy 检查

```bash
cargo clippy                              # 基础检查
cargo clippy --all-targets                # 含测试、示例
cargo clippy -p <package_name>            # 特定包
cargo clippy -- --deny warnings           # 严格模式
cargo clippy -- --allow <lint_name>       # 允许特定 lint
cargo clippy -- --deny <lint_name>        # 禁止特定 lint
```

### 步骤3：自动修复

```bash
cargo clippy --fix                        # 安全修复
cargo clippy --fix --allow-dirty --allow-staged  # 允许语义变更修复
cargo clippy --all-targets                # 验证修复结果
```

### 步骤4：输出与报告

```bash
cargo clippy --message-format=json > clippy-report.json   # JSON
cargo clippy --message-format=short                       # 简短
```

报告模板见 `templates/report.md`。

## Lint 级别与组

| 级别 | 描述 | 组名 | 严格程度 |
| --- | --- | --- | --- |
| allow | 允许，不提示 | clippy::all（默认） | 适中 |
| warn | 警告 | clippy::pedantic | 严格 |
| deny | 错误，阻止编译 | clippy::correctness | 严格 |
| forbid | 禁止，无法覆盖 | clippy::restriction | 最严格 |

其他组：`style`（宽松）、`complexity`（适中）、`perf`（适中）、`cargo`（宽松）、`nursery`（不稳定）。

## 启用/禁用 Lint

### 命令行

```bash
cargo clippy -- --clippy::pedantic
cargo clippy -- --allow clippy::too_many_arguments
cargo clippy -- --clippy::pedantic --deny clippy::unwrap_used
```

### 代码内属性

```rust
#![warn(clippy::pedantic)]
#![allow(clippy::too_many_lines)]
#[allow(clippy::too_many_arguments)]
fn complex_function(a: i32, b: i32, c: i32, d: i32, e: i32) {}
```

### Cargo.toml 配置

```toml
[lints]
workspace = true

[workspace.lints.clippy]
pedantic = "warn"
unwrap_used = "deny"
too_many_arguments = "allow"
```

## CI 集成

模板见 `templates/` 目录：

- `ci-github-actions.yaml` — GitHub Actions
- `ci-pre-commit.yaml` — pre-commit hook
- `Makefile` — Make 目标

## 分析结果处理

```bash
# 统计 lint 类型
cargo clippy --message-format=json 2>/dev/null | \
  jq -r 'select(.message != null) | .message.code | .code // empty' | \
  sort | uniq -c | sort -nr

# 提取错误级别
cargo clippy --message-format=json 2>/dev/null | \
  jq -r 'select(.message != null and .message.level == "error") | .message.rendered'
```

## 典型场景

| 场景 | 命令 |
| --- | --- |
| 快速检查 | `cargo clippy --all-targets` |
| CI 严格模式 | `cargo clippy --all-targets -- --deny warnings` |
| 渐进式采用 | `--fix` → `--warn clippy::pedantic` → `--deny clippy::unwrap_used` |
| 修复后验证 | `cargo clippy --fix --allow-dirty && cargo clippy --all-targets -- --deny warnings && cargo test` |

## 最佳实践

1. CI 中 deny warnings
2. 渐进式采用：从 `clippy::all` 到 `pedantic`
3. 自动修复优先：先用 `--fix`
4. 合理例外用 `#[allow()]` 并附注释
5. 先 rustfmt 再 clippy
6. 定期 `rustup update`

## 注意事项

1. `--fix` 可能改变语义，修复后务必测试
2. `nursery` 组不稳定，可能变化
3. `restriction` 需手动启用
4. 与 `#[deny(warnings)]` 冲突时 clippy 警告也会被拒绝

---
**技能版本**: 1.0.0 | **工具**: cargo clippy | **适用**: Rust 项目
