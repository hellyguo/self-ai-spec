# Clippy 分析报告

## 概要

| 级别 | 数量 |
| --- | --- |
| error | {error_count} |
| warning | {warning_count} |
| note | {note_count} |

## Lint 分布

| Lint 代码 | 数量 | 级别 |
| --- | --- | --- |
| {lint_code} | {lint_count} | {lint_level} |

## 错误详情

{error_details}

## 修复建议

1. 自动修复：`cargo clippy --fix`
2. 严格模式验证：`cargo clippy --all-targets -- --deny warnings`
3. 运行测试：`cargo test`
