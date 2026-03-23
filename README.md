# AI Skills

AI 编码代理技能定义，用于指导编码代理进行代码审查、重构、编译等任务。

## 概述

本仓库包含各种 AI 编码助手使用的技能定义。每个技能都是一组自包含的指令，指导 AI 代理完成特定任务，如代码审查、重构、编译等。

## 符号链接设置

本仓库被符号链接到多个 AI 工具目录：

```
~/.opencode/skills   → /home/helly/code/markdown/ai-skills
~/.codebuddy/skills  → /home/helly/code/markdown/ai-skills
~/.qoder/skills      → /home/helly/code/markdown/ai-skills
```

这使得所有 AI 工具可以共享相同的技能定义，避免重复。

## 可用技能

### 代码审查
| 技能 | 语言 | 描述 |
|------|------|------|
| `java-review` | Java | 全量代码审查 |
| `java-inc-review` | Java | 增量审查（git/svn diff） |
| `cpp-review` | C++ | 包含详细规则的全面审查 |
| `ansi-c-review` | ANSI C | 全量代码审查 |
| `python-review` | Python | 全量代码审查 |
| `rust-review` | Rust | 全量代码审查 |

### 构建与环境
| 技能 | 描述 |
|------|------|
| `java-env` | Java 环境（JDK、Maven） |
| `java-compile` | Java 编译 |
| `java-g2m` | Gradle 转 Maven |

### 代码生成
| 技能 | 描述 |
|------|------|
| `java-gen-unittest` | 生成单元测试 |
| `java-refactor` | 重构方法论 |
| `code-deconstruct` | 生成设计文档 |

### AGENTS.md 合并
| 技能 | 源文件 |
|------|--------|
| `java-merge-agent-md` | AGENTS.java.md |
| `cpp-merge-agent-md` | AGENTS.cpp.md |
| `ansi-c-merge-agent-md` | AGENTS.ansi_c.md |
| `python-merge-agent-md` | AGENTS.python.md |
| `rust-merge-agent-md` | AGENTS.rust.md |
| `js-merge-agent-md` | AGENTS.js.md |

## 使用方法

技能会在任务匹配其目的时被 AI 工具自动加载。详细文档请参阅 AGENTS.md。