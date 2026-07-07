# AI Skills 仓库

## 环境变量配置

**重要**：使用脚本前需要设置环境变量：

```bash
# 设置 AI_SPEC_ROOT 指向本仓库目录
export AI_SPEC_ROOT="/disk2/helly_data/code/markdown/self-ai-spec"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export AI_SPEC_ROOT="/disk2/helly_data/code/markdown/self-ai-spec"' >> ~/.bashrc
source ~/.bashrc
```

**验证配置**：
```bash
echo $AI_SPEC_ROOT  # 应该显示正确的路径
ls $AI_SPEC_ROOT/agent-template/  # 应该能看到模板文件
```

## 快速启动脚本

`bin/` 目录包含 AI 编码工具的快速启动脚本，支持会话恢复和语言模板配置：

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

### 使用流程

1. **首次启动**（需要语言参数）：

```bash
./bin/oc java          # 启动 opencode 处理 Java 项目
# 项目完成后会显示: Session ID: ses_xxx...
```

1. **保存会话ID**：

```bash
# 复制 Session ID 到剪贴板
./bin/updocid          # 更新本地会话ID记录
```

1. **恢复会话**（无需参数）：

```bash
./bin/oc              # 自动使用保存的会话ID恢复
```

1. **跨工具工作**：

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

**脚本功能说明**：

- **`oc`** - 启动 opencode，支持会话恢复（依赖 `opencode`）
- **`cdbd`** - 启动 codebuddy，支持会话恢复（依赖 `codebuddy`）
- **`qcc`** - 启动 qodercli（依赖 `qodercli`）
- **`clc`** - 启动 claudecode，支持会话恢复（依赖 `claude`）
- **`updocid`** - 更新 opencode 会话ID（依赖 `xclip`）
- **`updcbid`** - 更新 codebuddy 会话ID（依赖 `xclip`）
- **`updccid`** - 更新 claudecode 会话ID（依赖 `xclip`）

### 会话文件格式

每个工具使用独立的ID文件：

- `.opencode_id` - opencode 会话ID
- `.codebuddy_id` - codebuddy 会话ID  
- `.claudecode_id` - claudecode 会话ID

会话ID自动从剪贴板获取，需符合相应工具的格式要求。

### 模板配置

脚本从 `~/code/markdown/self-ai-spec/agent-template/` 复制对应的 AGENTS.md 模板：

- `AGENTS.java.md` - Java 项目配置
- `AGENTS.ansi_c.md` - ANSI C 项目配置
- `AGENTS.cpp.md` - C++ 项目配置
- `AGENTS.rust.md` - Rust 项目配置  
- `AGENTS.python.md` - Python 项目配置
- `AGENTS.js.md` - JavaScript 项目配置
- `AGENTS.blank.md` - 空白模板

## 符号链接

```bash
~/.opencode/skills → 本仓库
~/.codebuddy/skills → 本仓库
~/.qoder/skills → 本仓库
```

## 最新更新

**2025-07-06**: code-review 技能重要更新：

- 敏感数据审查明确为所有语言通用必须项（不是C/C++特有）
- 安全审查部分增加：敏感信息泄露、敏感数据内存残留、敏感字段输出、安全日志处理
- 专项检查6重命名为"敏感字段输出审查（所有语言通用）"
- 提供Java/Python/JavaScript多语言示例

## 可用技能

### 代码审查与分析

| 技能                    | 描述                                                              |
| ----------------------- | ----------------------------------------------------------------- |
| `code-review`           | 多语言代码审查 + 数据库审查                                       |
| `code-deconstruct`      | 源代码解构为设计文档、ER图                                        |
| `requirement-collect`   | 源代码解构为需求文档                                              |
| `code-detect-problem`   | 项目问题侦测、评分、重构方案                                      |
| `code-detect-dup`       | 代码重复度检测                                                    |
| `code-refactor`         | 重构方法论                                                        |

### 调度与任务执行

| 技能             | 描述                                                              |
| ---------------- | ----------------------------------------------------------------- |
| `lets-loop`      | 循环调度组合技能的通用框架                                        |
| `long-term-task` | 长任务执行：理解、澄清、计划、连续执行                            |

### Java开发工具

| 技能                    | 描述                                                              |
| ----------------------- | ----------------------------------------------------------------- |
| `java-env`              | Java 环境信息                                                     |
| `java-compile`          | Java 编译指引                                                     |
| `java-g2m`              | Gradle 转 Maven                                                   |
| `java-gen-unittest`     | Java 单元测试生成                                                 |

### 性能分析与基准测试

| 技能           | 描述                                                              |
| -------------- | ----------------------------------------------------------------- |
| `java-asprof`  | Java 性能分析（async-profiler）                                   |
| `jmh-bench`    | JMH 基准测试                                                      |

### 项目配置

| 技能               | 描述                                                              |
| ------------------ | ----------------------------------------------------------------- |
| `merge-agents-md`  | 合并语言模板到项目 AGENTS.md                                      |

## 安全审查原则

**重要**：敏感数据审查是所有代码审查的必须项，无论使用何种编程语言：

- 密码、密钥、令牌、API Key等是否硬编码
- 敏感信息是否被记录到日志/调试输出
- 内存中的敏感数据是否被安全清除
- 是否使用安全日志宏过滤敏感字段

## 详细文档

详细技能文档和交互规则请参阅 [AGENTS.md](AGENTS.md)。
