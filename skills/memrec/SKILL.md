---
name: memrec
description: AI记忆持久化系统。使用memrec存储、检索、管理跨会话记忆。支持项目隔离和语义检索。触发场景：(1)重要决策需记录，(2)关键知识需保存，(3)项目上下文需跨会话保持，(4)用户偏好需记忆，(5)检索历史知识辅助当前任务。
---

# MemRec - AI记忆持久化系统

为AI CLI工具提供跨会话记忆能力，支持项目隔离和语义检索。

## 触发场景

1. 重要决策需记录 → `memrec add --mtype decision --tag critical`
2. 关键知识需保存 → `memrec add --mtype knowledge`
3. 项目上下文需跨会话保持 → 自动关联项目ID
4. 用户偏好需记忆 → `memrec add --mtype preference --global`
5. 检索历史知识辅助当前任务 → `memrec search "关键词"`

## MCP Server

MemRec 可作为 MCP Server 直接被 AI 客户端（Claude Code、Codex、OpenCode）调用，无需 CLI 命令。

**启动方式：** `memrec --mcp`（stdio 模式）

**客户端配置：**
```json
{
  "mcpServers": {
    "memrec": {
      "command": "memrec",
      "args": ["--mcp"]
    }
  }
}
```

**MCP Tools：**

| Tool | 功能 | 必需参数 |
|------|------|----------|
| `mr_add` | 添加记忆 | `content`, `memory_type` |
| `mr_search` | 语义检索 | `query` |
| `mr_get` | 获取单条记忆 | `id` |
| `mr_list` | 列出记忆 | - |
| `mr_delete` | 删除记忆 | `id` |
| `mr_stats` | 统计信息 | - |

**MCP Resources：**

| URI | 描述 |
|-----|------|
| `memrec://stats` | 记忆统计 |
| `memrec://project` | 当前项目信息 |

**示例：**
```json
// mr_add
{"name": "mr_add", "arguments": {"content": "选择JWT认证", "memory_type": "decision", "tags": ["auth", "critical"]}}

// mr_search
{"name": "mr_search", "arguments": {"query": "认证方案", "min_score": 0.75, "project_only": true}}

// mr_search 跨项目
{"name": "mr_search", "arguments": {"query": "xlsb", "cross_project": true}}
```

## 核心命令

### 存储记忆

```bash
memrec add "内容" --mtype <type> [--tag <tag>] [--global]
```

**记忆类型：**
- `decision` - 关键决策（推荐--tag critical）
- `knowledge` - 知识点（通过tag细分）
- `context` - 项目配置/环境信息
- `preference` - 用户偏好（推荐--global）
- `conversation` - 对话记录（默认）

**knowledge通过tag细分：**
| tag | 用途 | 示例 |
|-----|------|------|
| `fact` | 物理定律、数学公式、客观事实 | `--tag fact --tag physics` |
| `best-practice` | 最佳实践、设计模式 | `--tag best-practice` |
| `algorithm` | 算法、公式推导 | `--tag algorithm` |
| `tool` | 工具使用技巧 | `--tag tool --tag rust` |

**示例：**
```bash
# 事实类知识
memrec add "光速c=3×10⁸m/s，真空环境中恒定" --mtype knowledge --tag fact --tag physics
memrec add "欧拉公式：e^(iπ)+1=0" --mtype knowledge --tag fact --tag math

# 最佳实践
memrec add "RAII模式：资源获取即初始化，析构自动释放" --mtype knowledge --tag best-practice --tag rust

# 决策
memrec add "选择JWT认证方案" --mtype decision --tag auth --tag critical

# 用户偏好
memrec add "用户偏好详细输出" --mtype preference --tag output --global

# 项目上下文
memrec add "技术栈：Rust+Tokio+RocksDB" --mtype context --tag tech
```

### 语义检索

```bash
memrec search "关键词" [--project-only] [--global-only] [--all] [-k <num>]
```

**搜索范围：**
| 选项 | 范围 | 用途 |
|------|------|------|
| 默认 | 当前项目 + 公共记忆 | 日常使用 |
| `--project-only` | 仅当前项目 | 精确项目内搜索 |
| `--global-only` | 仅公共记忆 | 查找用户偏好 |
| `--all` | 所有项目（跨项目） | 查找跨项目关联记忆 |

**示例：**
```bash
memrec search "认证方案"
memrec search "Rust最佳实践" --project-only
memrec search "用户偏好" --global-only -k 20
memrec search "xlsb" --all                    # 跨项目搜索
memrec search "架构" --human
```

### 其他命令

```bash
memrec get <memory-id> [--merge]
memrec list [--limit <num>] [--project-only] [--global-only]
memrec stats
memrec version
memrec delete <memory-id>
```

## 项目隔离

**自动检测机制：**
- 优先检测git root（`git rev-parse --show-toplevel`）
- 若非git仓库，使用当前工作目录
- 在项目根目录创建 `.mr_pid` 文件存储project_id

| 类型 | 用途 | project_id |
|------|------|------------|
| 公共记忆（--global） | 跨项目共享知识和用户偏好 | `Uuid::nil()`（全0） |
| 项目记忆 | 项目特定决策和上下文 | `.mr_pid`中的UUID |

**检索范围：**
- 默认：项目记忆 + 公共记忆
- `--project-only`：仅当前项目记忆
- `--global-only`：仅公共记忆

**示例：**
```bash
# 在 /disk2/code/rust/memrec 目录
memrec add "memrec项目决策" --mtype decision
# → 写入 memrec/.mr_pid 的 project_id

# 在 /disk2/code/java/hydrakiller 目录
memrec add "hydrakiller项目决策" --mtype decision
# → 写入 hydrakiller/.mr_pid 的 project_id（不同）

# 搜索时自动隔离
cd /disk2/code/rust/memrec
memrec search "决策" --project-only  # 仅返回memrec项目

cd /disk2/code/java/hydrakiller
memrec search "决策" --project-only  # 仅返回hydrakiller项目
```

**注意：**
- `.mr_pid` 文件不应提交到git（添加到.gitignore）
- 移动项目目录后，project_id保持不变（`.mr_pid`随项目移动）

## 工作流集成

```bash
# 开始任务：检索相关历史
memrec search "相关历史" --project-only

# 做出决策后
memrec add "选择XXX方案" --mtype decision --tag critical

# 用户表达偏好后
memrec add "用户偏好YYY" --mtype preference --global

# 结束任务
memrec stats
```

## 最佳实践

1. **决策即记录** - 做出决策后立即记录
2. **关键用critical** - 重要信息用critical标签
3. **偏好用global** - 用户偏好标记为公共记忆
4. **事实用fact** - 物理定律、数学公式用fact标签
5. **检索优先search** - 用语义检索而非枚举
6. **min_score默认0.75** - 过滤低相关度干扰项（可通过MEMREC_MIN_SCORE调整）
7. **项目隔离自动** - 无需手动指定，自动检测git root
8. **.mr_pid勿提交** - 添加到.gitignore，避免project_id冲突

## 数据位置

```
~/.memrec/
├── memrecd.sock        # Unix Socket
├── data/               # RocksDB记忆元数据
├── vectors/            # RocksDB向量存储
├── models/             # ONNX embedding模型
└── memrecd.log         # 服务日志
```

---
