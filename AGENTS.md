# AI Skills 仓库

AI 编码代理技能和语言规范的文档仓库，为多个 AI 编码工具提供统一的技能定义。

## AI guide

### 角色定位

你是百科全书，熟知大量常识；格式偏好 `markdown`

### 环境变量

`${AI_SPEC_ROOT}` 定义在 bash/zsh 环境变量中，可被读取：`echo ${AI_SPEC_ROOT}`

### 交互规则

必须遵循 `agent-template/interaction.rules.md` 中描述的规则。

授权读取：${AI_SPEC_ROOT}/agent-template/interaction.rules.md

- 所有交互均使用简体中文，所有输出都不得带 Emoji，以显正式
- 每次交互的第一步，都是先检索 memrec-mcp，并在输出后随时、持续使用 memrec-mcp 记录核心观点、关键节点、重要内容（plan、design 等）
- 每次产出最后一步，确认是否需要更新 MEMORY.md + 记录 memrec-mcp；如产出文件后，均执行 git 提交
- git 仅以当前 `user.name` 提交，不推送到远端
- git 提交均遵循约定式提交规范（Conventional Commits）执行
- 版本管理忽略 MEMORY.md，写入 .gitignore，不提交到 git
- 如当前文件夹下无 `.codegraph`，先执行 `codegraph init -i`，确保后续可使用 codegraph
- 编排计划或设计时，如过长（>2000 行），拆分为多份文档
- 计划或设计中，不要穿插代码，代码不能成为设计或计划的主要内容，仅需要部分伪代码将逻辑讲清楚
- 编码时，合理生成注释。文件头/类头/函数头/方法头，应有描述和注意事项；重要算法、重要参数、重要设计，应有解释和说明
- 修改时，不删除原有注释，但如已经语义变化等必要情况，需要变更或删除，重新补充注释，参见上一条
- 禁止在编码使用 stdout/stderr，测试代码也尽可能使用日志输出
- 本机为 linux，且配备了更高效的工具，倾向使用这些工具
  - fd[find]、rg[grep]、sd[sed]、eza[ls]、plocate[类似 Windows 下的 everything]、f2[批量重命名]、rrn[同 f2，弱化]

本仓库额外补充：

1. **脚本测试提醒**：避免在测试中直接运行 `oc`、`cdbd`、`clc`、`qcc`、`pc` 脚本，这些脚本会启动交互式 AI 工具并接管终端。优先使用 `bash -n` 进行语法检查，或通过环境变量和重定向测试特定功能。

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

### 核心分析技能

| 技能 | 用途 |
| :--- | :--- |
| `code-review` | 多语言代码审查（Java/Kotlin/Python/C++/Rust/JS/ANSI C）+ 数据库审查 |
| `code-deconstruct` | 源代码解构为设计文档、ER图（设计层面） |
| `requirement-collect` | 源代码解构为需求文档（需求层面） |
| `code-detect-problem` | 项目问题侦测、评分、重构/重建方案 |
| `code-detect-dup` | 代码重复度检测（Simian + JSCPD） |
| `code-refactor` | 重构方法论 |
| `code-part-modification` | 局部代码修改：最小化修改完成功能，确保无蝴蝶效应，支持独立测试验证 |
| `full-analysis` | 完整分析流程：设计解构→代码审查→重复检测→问题侦测→定性评估 |
| `qualitative-assessment` | 系统定性评估：基于全面分析输出，从设计、开发、运维、非功能等维度总结系统性质 |
| `long-term-task` | 长任务执行：理解、澄清、计划、连续执行 |
| `lets-loop` | 持续循环调度框架：循环调度组合技能的通用框架 |

### 静态分析工具

| 技能 | 用途 |
| :--- | :--- |
| `cpp-check` | Cppcheck 静态分析：C/C++ 代码质量检测（缺陷、未定义行为、安全漏洞） |
| `cpp-clang-tidy` | Clang-Tidy 静态分析：C/C++ 代码质量检测（基于 Clang AST，支持自动修复） |
| `cpp-tscancode` | TscanCode 静态分析：腾讯开源 C/C++ 代码检测工具 |
| `shell-check` | ShellCheck 静态分析：Shell 脚本代码质量检测（语法错误、潜在缺陷、代码风格） |
| `rust-clippy` | Clippy 静态分析：Rust 代码质量检测（错误、风格、性能、安全），支持 cargo fix 自动修复 |
| `java-check-spotbugs` | SpotBugs 静态分析：Java 代码缺陷和安全漏洞检测 |
| `java-check-pmd` | PMD 静态分析：Java 代码质量、编码规范和安全问题检测 |
| `ast-grep-block` | 基于 ast-grep 的代码审查门禁：code-checklist 规则集分级扫描 Java/C++/ANSI C，输出 CI 退出码 |

### Java 开发工具

| 技能 | 用途 |
| :--- | :--- |
| `java-env` | Java 环境信息 |
| `java-compile` | Java 编译指引 |
| `java-g2m` | Gradle 转 Maven |
| `java-gen-unittest` | Java 单元测试生成 |
| `java-asprof` | Java 性能分析（async-profiler） |
| `jmh-bench` | JMH 基准测试 |
| `java-coverage` | Java 测试覆盖率提升策略：80%+ 行覆盖/60%+ 分支覆盖，支持增量/全量测试 |

### 性能与运行时分析

| 技能 | 用途 |
| :--- | :--- |
| `gdb-heap-analysis` | GDB 堆内存分析：core dump 中的 glibc ptmalloc 内存泄漏/arena 分析 |
| `rust-flamegraph` | Rust 火焰图：CPU 热点分析、性能瓶颈定位（cargo flamegraph） |

### 文档与图表生成

| 技能 | 用途 |
| :--- | :--- |
| `md2pdf` | Markdown 转 PDF 工具，支持 Mermaid 和 PlantUML 图表自动渲染 |
| `creating-mermaid-diagrams` | Mermaid 图表生成与导出（PNG/SVG/PDF），支持 11+ 图表类型 |
| `plantuml-skill` | PlantUML 图表生成与导出（Kroki API，无需本地安装） |
| `drawio-skill` | draw.io 图表生成与导出（本地桌面 CLI） |
| `excalidraw-diagram` | Excalidraw 手绘风格图表 JSON 生成 |
| `html-ppt` | HTML 静态演示文稿生成（多风格、多布局、键盘导航） |
| `ppt-master` | 专业 PPT 设计制作（PptxGenJS + SVG 图表模板） |

### 工程与记忆

| 技能 | 用途 |
| :--- | :--- |
| `merge-agents-md` | 合并语言模板到项目 AGENTS.md |
| `sql-extract` | SQL 抽取：从 C++/Java/XML 源代码中抽取内嵌 SQL 语句，识别 SQL 拼接点 |
| `memrec` | AI 记忆持久化：跨会话记忆存储、检索、项目隔离、混合检索（KNN+BM25） |

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
