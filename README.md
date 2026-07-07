# AI Skills 仓库

## 环境变量配置

**重要**：所有脚本都需要 `AI_SPEC_ROOT` 环境变量来定位资源文件：

```bash
# 设置 AI_SPEC_ROOT 指向本仓库目录
export AI_SPEC_ROOT="/disk2/helly_data/code/markdown/self-ai-spec"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export AI_SPEC_ROOT="/disk2/helly_data/code/markdown/self-ai-spec"' >> ~/.bashrc
source ~/.bashrc
```

**验证配置**：

```bash
echo $AI_SPEC_ROOT                    # 应该显示正确的路径
ls $AI_SPEC_ROOT/bin/                 # 应该能看到脚本文件
ls $AI_SPEC_ROOT/agent-template/      # 应该能看到模板文件
```

**为什么需要环境变量？**

- 支持将脚本符号链接到任意目录（如 `~/bin/`）
- 避免硬编码路径，提高可移植性
- 简化多人协作时的配置

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

脚本从 `$AI_SPEC_ROOT/agent-template/` 复制对应的模板文件：

- `AGENTS.java.md` - Java 项目配置
- `AGENTS.ansi_c.md` - ANSI C 项目配置
- `AGENTS.cpp.md` - C++ 项目配置
- `AGENTS.rust.md` - Rust 项目配置  
- `AGENTS.python.md` - Python 项目配置
- `AGENTS.js.md` - JavaScript 项目配置
- `AGENTS.blank.md` - 空白模板

### 脚本架构设计

**设计原则**：

1. **环境变量驱动**：所有路径通过 `AI_SPEC_ROOT` 环境变量推导
2. **符号链接友好**：脚本可以从任意位置通过符号链接调用
3. **错误处理**：明确的环境变量验证和文件存在检查
4. **统一函数库**：公共逻辑集中在 `common.sh` 中
5. **会话管理**：支持智能会话恢复和跨工具工作流

**脚本依赖**：

- `opencode`, `codebuddy`, `claude`, `qodercli` - 对应的AI工具
- `xclip` - 剪贴板操作（会话ID更新脚本）
- `bash` - Shell环境

**文件结构**：

```
$AI_SPEC_ROOT/
├── bin/
│   ├── common.sh           # 公共函数库
│   ├── oc                  # opencode启动脚本
│   ├── cdbd                # codebuddy启动脚本
│   ├── clc                 # claudecode启动脚本
│   ├── qcc                 # qodercli启动脚本
│   ├── updocid             # 更新opencode会话ID
│   ├── updcbid             # 更新codebuddy会话ID
│   └── updccid             # 更新claudecode会话ID
└── agent-template/
    ├── AGENTS.java.md      # Java模板
    ├── AGENTS.ansi_c.md    # ANSI C模板
    ├── AGENTS.cpp.md       # C++模板
    ├── AGENTS.rust.md      # Rust模板
    ├── AGENTS.python.md    # Python模板
    ├── AGENTS.js.md        # JavaScript模板
    └── AGENTS.blank.md     # 空白模板
```

## 最新更新

**2025-07-07**: 脚本系统全面重构，支持符号链接部署：

- **环境变量驱动**：所有脚本通过 `AI_SPEC_ROOT` 环境变量定位资源
- **符号链接友好**：脚本可以符号链接到任意目录（如 `~/bin/`）
- **架构优化**：公共函数集中在 `common.sh`，各脚本独立验证环境变量
- **错误处理增强**：明确的配置验证和错误提示

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
