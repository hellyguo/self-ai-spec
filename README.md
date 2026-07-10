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

## 可用技能

### 核心技能库

| 技能 | 描述 |
| :--- | :--- |
| `code-review` | 多语言代码审查 + 数据库审查 |
| `code-deconstruct` | 源代码解构为设计文档、ER图、内存/网络分析 |
| `requirement-collect` | 源代码解构为需求文档 |
| `code-detect-problem` | 项目问题侦测、评分、重构方案 |
| `code-detect-dup` | 代码重复度检测 |
| `code-refactor` | 重构方法论 |
| `lets-loop` | 循环调度组合技能的通用框架 |
| `long-term-task` | 长任务执行：理解、澄清、计划、连续执行 |
| `full-analysis` | 完整分析流程：设计解构→代码审查→重复检测→问题侦测→定性评估 |
| `qualitative-assessment` | 系统定性评估：基于全面分析输出，从设计、开发、运维、非功能等维度总结系统性质 |
| `md2pdf` | Markdown 转 PDF 工具，支持 Mermaid 和 PlantUML 图表自动渲染 |
| `merge-agents-md` | 合并语言模板到项目 AGENTS.md |

### Java开发工具

| 技能 | 描述 |
| :--- | :--- |
| `java-env` | Java 环境信息 |
| `java-compile` | Java 编译指引 |
| `java-g2m` | Gradle 转 Maven |
| `java-gen-unittest` | Java 单元测试生成 |
| `java-asprof` | Java 性能分析（async-profiler） |
| `jmh-bench` | JMH 基准测试 |
| `java-check-spotbugs` | SpotBugs静态分析：Java代码缺陷和安全漏洞检测 |
| `java-check-pmd` | PMD静态分析：Java代码质量、编码规范和安全问题检测 |

## 代理模板配置

语言特定的代理配置文件位于 `agent-template/` 目录，用于配置 AI 工具的项目模板：

### 语言模板

- `AGENTS.java.md` - Java 项目配置
- `AGENTS.ansi_c.md` - ANSI C 项目配置  
- `AGENTS.cpp.md` - C++ 项目配置
- `AGENTS.rust.md` - Rust 项目配置
- `AGENTS.python.md` - Python 项目配置
- `AGENTS.js.md` - JavaScript 项目配置
- `AGENTS.shell.md` - Shell/Bash 项目配置
- `AGENTS.blank.md` - 空白模板

### 使用方式

1. **手动复制**：将模板复制到项目根目录并重命名为 `AGENTS.md`
2. **脚本复制**：使用 `bin/` 目录的启动脚本自动配置

## 快速启动脚本（辅助工具）

`bin/` 目录包含 AI 编码工具的快速启动脚本，支持会话恢复和语言模板自动配置：

### 主要工具启动脚本

```bash
# 新会话：需要指定语言参数
./bin/oc java          # 启动 opencode 处理 Java 项目
./bin/cdbd java        # 启动 codebuddy 处理 Java 项目
./bin/clc java         # 启动 claudecode 处理 Java 项目

# 恢复会话：无需参数，自动恢复
./bin/oc              # 自动恢复 opencode 会话
./bin/cdbd            # 自动恢复 codebuddy 会话  
./bin/clc             # 自动恢复 claudecode 会话

# qodercli 不支持会话恢复
./bin/qcc <language>  # 启动 qodercli
```

**支持的语言参数**：

- `java` - Java 项目
- `ansi_c` - ANSI C 项目  
- `cpp` - C++ 项目
- `rust` - Rust 项目
- `python` - Python 项目
- `js` - JavaScript 项目
- `shell` - Shell/Bash 项目
- `blank` - 空白模板

### 会话ID更新脚本

```bash
# 更新 opencode 会话ID（从剪贴板）
./bin/updocid

# 更新 codebuddy 会话ID（从剪贴板）
./bin/updcbid

# 更新 claudecode 会话ID（从剪贴板）
./bin/updccid
```

## 环境变量配置

**重要**：所有脚本都需要 `AI_SPEC_ROOT` 环境变量来定位资源文件，这是必须配置的环境变量：

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

## 脚本符号链接部署（推荐）

为了方便使用，可以将脚本符号链接到个人bin目录：

```bash
# 确保 ~/bin 在 PATH 中
export PATH="$HOME/bin:$PATH"
mkdir -p ~/bin

# 创建符号链接
ln -sf $AI_SPEC_ROOT/bin/oc ~/bin/oc
ln -sf $AI_SPEC_ROOT/bin/cdbd ~/bin/cdbd
ln -sf $AI_SPEC_ROOT/bin/clc ~/bin/clc
ln -sf $AI_SPEC_ROOT/bin/qcc ~/bin/qcc
ln -sf $AI_SPEC_ROOT/bin/updocid ~/bin/updocid
ln -sf $AI_SPEC_ROOT/bin/updcbid ~/bin/updcbid
ln -sf $AI_SPEC_ROOT/bin/updccid ~/bin/updccid

# 验证链接
ls -la ~/bin/ | grep -E 'oc|cdbd|clc|qcc|upd'

# 现在可以在任何目录使用：
oc java
cdbd python
updocid
```

## 使用流程

1. **首次启动**（需要语言参数）：

   ```bash
   ./bin/oc java          # 启动 opencode 处理 Java 项目
   # 项目完成后会显示: Session ID: ses_xxx...
   ```

2. **保存会话ID**：

   ```bash
   # 复制 Session ID 到剪贴板
   ./bin/updocid          # 更新本地会话ID记录
   ```

3. **恢复会话**（无需参数）：

   ```bash
   ./bin/oc              # 自动使用保存的会话ID恢复
   ```

4. **跨工具工作**：

   ```bash
   ./bin/oc java          # 开始 Java 项目
   ./bin/updocid          # 保存 opencode 会话ID
   ./bin/clc java         # 切换到 claudecode 继续
   ./bin/updccid          # 保存 claudecode 会话ID
   ```

**智能恢复逻辑**：

- 检测到会话ID文件存在 → 直接恢复会话，跳过模板复制
- 无会话ID → 需要语言参数来设置项目模板
- 各工具独立：opencode、codebuddy、claudecode 各自管理会话状态

## 安全审查原则

**重要**：敏感数据审查是所有代码审查的必须项，无论使用何种编程语言：

- 密码、密钥、令牌、API Key等是否硬编码
- 敏感信息是否被记录到日志/调试输出
- 内存中的敏感数据是否被安全清除
- 是否使用安全日志宏过滤敏感字段

## 详细文档

详细技能文档和交互规则请参阅 [AGENTS.md](AGENTS.md)。

完整更新历史请查看 [CHANGELOG.md](CHANGELOG.md)。
