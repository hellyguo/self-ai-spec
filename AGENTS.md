# AI Skills 仓库

AI 编码代理技能和语言规范的文档仓库，为多个 AI 编码工具提供统一的技能定义。

## 交互规则

1. 所有交互均使用简体中文
2. 每次产出文件后执行 git 提交
3. 提交遵循约定式提交规范（Conventional Commits）
4. 除非明确要求，不推送到远端
5. **脚本测试提醒**：避免在测试中直接运行 `oc`、`cdbd`、`clc`、`qcc` 脚本，这些脚本会启动交互式AI工具并接管终端。优先使用 `bash -n` 进行语法检查，或通过环境变量和重定向测试特定功能。

## 验证命令

```bash
markdownlint '**/*.md'          # 验证所有 Markdown
markdownlint --fix '**/*.md'    # 自动修复格式
grep -r "^---$" skills/ | head  # 验证 YAML 前置数据
```

## 技能文件格式

每个 SKILL.md 必须包含 YAML 前置数据：

```markdown
---
name: skill-name
description: "技能简介"
---
```

## 可用技能

| 技能 | 用途 |
| :--- | :--- |
| `code-review` | 多语言代码审查（Java/Python/C++/Rust/JS/ANSI C）+ 数据库审查 |
| `code-deconstruct` | 源代码解构为设计文档、ER图（设计层面） |
| `requirement-collect` | 源代码解构为需求文档（需求层面） |
| `code-detect-problem` | 项目问题侦测、评分、重构/重建方案 |
| `code-detect-dup` | 代码重复度检测 |
| `code-refactor` | 重构方法论 |
| `code-part` | 局部代码修改：最小化修改完成功能，确保无蝴蝶效应，支持独立测试验证 |
| `cpp-check` | Cppcheck 静态分析：C/C++ 代码质量检测（缺陷、未定义行为、安全漏洞） |
| `cpp-tscancode` | TscanCode 静态分析：腾讯开源 C/C++ 代码检测工具 |
| `merge-agents-md` | 合并语言模板到项目 AGENTS.md |
| `lets-loop` | 持续循环调度框架：循环调度组合技能的通用框架 |
| `long-term-task` | 长任务执行：理解、澄清、计划、连续执行 |
| `full-analysis` | 完整分析流程：设计解构→代码审查→重复检测→问题侦测→定性评估 |
| `qualitative-assessment` | 系统定性评估：基于全面分析输出，从设计、开发、运维、非功能等维度总结系统性质 |
| `md2pdf` | Markdown 转 PDF 工具，支持 Mermaid 和 PlantUML 图表自动渲染 |
| `java-compile` | Java 编译指引 |
| `java-env` | Java 环境信息 |
| `java-gen-unittest` | Java 单元测试生成 |
| `java-g2m` | Gradle 转 Maven |
| `java-asprof` | Java 性能分析（async-profiler） |
| `jmh-bench` | JMH 基准测试 |
| `rust-clippy` | Clippy 静态分析：Rust 代码质量检测（错误、风格、性能、安全），支持 cargo fix 自动修复 |
| `cpp-clang-tidy` | Clang-Tidy 静态分析：C/C++ 代码质量检测（基于 Clang AST，支持自动修复） |
| `shell-check` | ShellCheck 静态分析：Shell 脚本代码质量检测（语法错误、潜在缺陷、代码风格） |

## 文件命名约定

| 类型 | 模式 | 示例 |
| :--- | :--- | :--- |
| 技能目录 | `kebab-case` | `code-review` |
| 技能文件 | `SKILL.md`（大写） | `SKILL.md` |
| 语言规范 | `spec.{lang}.md` | `spec.java.md` |
| 代理模板 | `AGENTS.{lang}.md` | `AGENTS.java.md` |

## 跨文件引用规范

```markdown
授权读取：${AI_SPEC_ROOT}/lang-spec/spec.java.md
Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md
```

## 新增技能流程

1. 在 `skills/` 下创建 `kebab-case` 目录
2. 创建 `SKILL.md`，包含 YAML 前置数据
3. 更新本文件技能表
4. 运行 `markdownlint` 验证
5. 提交变更
