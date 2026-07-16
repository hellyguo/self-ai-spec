# AI Skills 仓库

AI 编码代理技能和语言规范的文档仓库，为多个 AI 编码工具提供统一的技能定义。

## 交互规则

读取并遵循 agent-template/interaction.rules.md

额外补充：

1. **脚本测试提醒**：避免在测试中直接运行 `oc`、`cdbd`、`clc`、`qcc` 脚本，这些脚本会启动交互式AI工具并接管终端。优先使用 `bash -n` 进行语法检查，或通过环境变量和重定向测试特定功能。

## 验证命令

```bash
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
| `code-detect-dup` | 代码重复度检测（Simian + JSCPD） |
| `code-refactor` | 重构方法论 |
| `code-part-modification` | 局部代码修改：最小化修改完成功能，确保无蝴蝶效应，支持独立测试验证 |
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

| 类型         | 模式               | 示例             |
| :----------- | :----------------- | :--------------- |
| 技能目录     | `kebab-case`       | `code-review`    |
| 技能文件     | `SKILL.md`（大写） | `SKILL.md`       |
| 语言规范     | `spec.{lang}.md`   | `spec.java.md`   |
| 审查规则     | `review.{lang}.md` | `review.java.md` |
| 代理模板     | `AGENTS.{lang}.md` | `AGENTS.java.md` |

## 跨文件引用规范

```markdown
授权读取：${AI_SPEC_ROOT}/lang-spec/spec.java.md
授权读取：${AI_SPEC_ROOT}/lang-spec/review.java.md

Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md
Read ${AI_SPEC_ROOT}/lang-spec/review.java.md
```

### 语言规范文件结构

每个编程语言有两个关联文件：

| 文件类型           | 用途                                           | 示例             |
|--------------------|------------------------------------------------|------------------|
| `spec.{lang}.md`   | 编码规范、最佳实践、语言特性指南               | `spec.java.md`   |
| `review.{lang}.md` | 代码审查规则、静态分析规则、问题模式检测       | `review.java.md` |

**组合使用**：

- **编码时**：参考 `spec.{lang}.md` 确保代码符合规范
- **审查时**：同时参考 `spec.{lang}.md` 和 `review.{lang}.md` 进行全面检查
- **技能集成**：`/code-review` 技能自动加载对应语言的规范文件和审查规则

## 新增技能流程

1. 在 `skills/` 下创建 `kebab-case` 目录
2. 创建 `SKILL.md`，包含 YAML 前置数据
3. 更新本文件技能表
4. 提交变更
