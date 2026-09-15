# AI Skills 仓库

AI 编码代理技能和语言规范的文档仓库，为多个 AI 编码工具提供统一的技能定义。

## 重要前提

**环境变量配置是必须的**：在使用任何脚本前，必须设置 `AI_SPEC_ROOT` 环境变量指向本仓库的根目录。

**为什么需要环境变量**：

- 支持符号链接部署到任意目录
- 允许仓库移动到不同位置
- 简化脚本调用，无需指定完整路径
- 统一资源文件定位方式

所有脚本和模板都使用 `${AI_SPEC_ROOT}` 引用资源文件，不再使用硬编码路径。

```bash
# 设置 AI_SPEC_ROOT 指向本仓库目录
export AI_SPEC_ROOT="/path/to/your/self-ai-spec-directory"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export AI_SPEC_ROOT="/path/to/your/self-ai-spec-directory"' >> ~/.bashrc
source ~/.bashrc
```

**验证配置**：

```bash
echo $AI_SPEC_ROOT                    # 应该显示正确的路径
ls $AI_SPEC_ROOT/bin/                 # 应该能看到脚本文件
ls $AI_SPEC_ROOT/agent-template/      # 应该能看到模板文件
```

## 目录结构

```text
self-ai-spec/
├── skills/            # 技能定义，每个技能一个 kebab-case 目录 + SKILL.md
├── lang-spec/         # 语言规范：spec.{lang}.md 编码规范 + review.{lang}.md 审查规则
├── agent-template/    # 代理模板：AGENTS.{lang}.md + interaction.rules.md
├── bin/               # AI 工具快速启动脚本与公共函数库
├── docs/              # 框架设计文档（代码审查框架、解构报告等）
├── pi-extensions/     # pi 扩展（memrec 等，符号链接）
├── dsh-plugins/       # dsh 插件（memrec 等，符号链接）
├── CHANGELOG.md       # 更新历史
└── README.md
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
| `ast-grep-block` | 基于 ast-grep 的代码审查门禁：code-checklist 规则集分级扫描 Java/C++/ANSI C |

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
| `md2pdf` | Markdown 转 PDF，支持 Mermaid 和 PlantUML 图表自动渲染 |
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

## 语言规范（lang-spec）

每个编程语言有两个关联文件：

| 文件类型           | 用途                                     | 示例             |
| :----------------- | :--------------------------------------- | :--------------- |
| `spec.{lang}.md`   | 编码规范、最佳实践、语言特性指南         | `spec.java.md`   |
| `review.{lang}.md` | 代码审查规则、静态分析规则、问题模式检测 | `review.java.md` |
| `ci.{lang}.md`     | 构建/CI 指引（部分语言提供）             | `ci.java.md`     |

- **编码时**：参考 `spec.{lang}.md` 确保代码符合规范
- **审查时**：同时参考 `spec.{lang}.md` 和 `review.{lang}.md` 进行全面检查
- **技能集成**：`/code-review` 技能自动加载对应语言的规范文件和审查规则

## 代理模板配置

语言特定的代理模板位于 `agent-template/` 目录，用于配置 AI 工具的项目模板：

- `AGENTS.java.md` - Java 项目配置
- `AGENTS.kotlin.md` - Kotlin 项目配置
- `AGENTS.ansi_c.md` - ANSI C 项目配置
- `AGENTS.cpp.md` - C++ 项目配置
- `AGENTS.rust.md` - Rust 项目配置
- `AGENTS.python.md` - Python 项目配置
- `AGENTS.js.md` - JavaScript 项目配置
- `AGENTS.shell.md` - Shell/Bash 项目配置
- `AGENTS.blank.md` - 空白模板
- `interaction.rules.md` - 通用交互规则

### 使用方式

1. **手动复制**：将模板复制到项目根目录并重命名为 `AGENTS.md`
2. **脚本复制**：使用 `bin/` 目录的启动脚本自动配置
3. **技能合并**：使用 `/merge-agents-md` 将模板合并到已存在的 `AGENTS.md`

## 快速启动脚本

`bin/` 目录包含 AI 编码工具的快速启动脚本，支持会话恢复和语言模板自动配置：
会话 ID 保存在项目根目录的隐藏文件中，各工具独立管理。

| 启动脚本 | 工具 | 会话 ID 文件 | 会话恢复 |
| :------- | :--- | :----------- | :------- |
| `bin/oc` | opencode | `.opencode_id` | 支持 |
| `bin/cdbd` | codebuddy | `.codebuddy_id` | 支持 |
| `bin/clc` | claudecode | `.claudecode_id` | 支持 |
| `bin/pc` | pi | `.pi_id` | 支持 |
| `bin/qcc` | qodercli | - | 不支持 |
| `bin/common.sh` | 公共函数库（被上述脚本 source） | - | - |

```bash
# 新会话：需要指定语言参数
./bin/oc java          # 启动 opencode 处理 Java 项目
./bin/cdbd java        # 启动 codebuddy 处理 Java 项目
./bin/clc java         # 启动 claudecode 处理 Java 项目
./bin/pc java          # 启动 pi 处理 Java 项目

# 恢复会话：无需参数，自动恢复
./bin/oc              # 自动恢复 opencode 会话
./bin/cdbd            # 自动恢复 codebuddy 会话
./bin/clc             # 自动恢复 claudecode 会话
./bin/pc              # 自动恢复 pi 会话

# qodercli 不支持会话恢复
./bin/qcc <language>  # 启动 qodercli
```

**支持的语言参数**：`java`、`kotlin`、`ansi_c`、`cpp`、`rust`、`python`、`js`、`shell`、`blank`

### 会话ID更新脚本

```bash
./bin/updocid          # 更新 opencode 会话ID（从剪贴板）
./bin/updcbid          # 更新 codebuddy 会话ID（从剪贴板）
./bin/updccid          # 更新 claudecode 会话ID（从剪贴板）
./bin/updpiid          # 更新 pi 会话ID（从剪贴板）
```

### 智能恢复逻辑

- 检测到会话ID文件存在 → 直接恢复会话，跳过模板复制
- 无会话ID → 需要语言参数来设置项目模板
- 各工具独立：opencode、codebuddy、claudecode、pi 各自管理会话状态

## 符号链接部署（推荐）

为了方便使用，可以将脚本符号链接到个人 bin 目录：

```bash
# 确保 ~/bin 在 PATH 中
export PATH="$HOME/bin:$PATH"
mkdir -p ~/bin

# 创建符号链接
for s in oc cdbd clc qcc pc updocid updcbid updccid updpiid; do
  ln -sf $AI_SPEC_ROOT/bin/$s ~/bin/$s
done

# 验证链接
ls -la ~/bin/ | grep -E 'oc|cdbd|clc|qcc|pc|upd'

# 现在可以在任何目录使用：
oc java
cdbd python
updocid
```

## 扩展与插件

- `pi-extensions/` - pi 工具扩展目录（以符号链接方式引入外部实现）
- `dsh-plugins/` - dsh 工具插件目录（以符号链接方式引入外部实现）

目前两者均链接到 `memrec` 的对应实现（`pi-extension` / `dsh-plugin`）。

## 安全审查原则

**重要**：敏感数据审查是所有代码审查的必须项，无论使用何种编程语言：

- 密码、密钥、令牌、API Key 等是否硬编码
- 敏感信息是否被记录到日志/调试输出
- 内存中的敏感数据是否被安全清除
- 是否使用安全日志宏过滤敏感字段

## 详细文档

- 交互规则与仓库约定：[AGENTS.md](AGENTS.md)、[agent-template/interaction.rules.md](agent-template/interaction.rules.md)
- 代码审查框架设计：[docs/code-review-framework.md](docs/code-review-framework.md)
- 完整更新历史：[CHANGELOG.md](CHANGELOG.md)
