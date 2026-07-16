---
name: memrec
description: AI记忆持久化系统。使用memrec存储、检索、管理跨会话记忆。支持项目隔离、混合检索（KNN+BM25）、MMR重排、中文搜索。触发场景：(1)重要决策需记录，(2)关键知识需保存，(3)项目上下文需跨会话保持，(4)用户偏好需记忆，(5)检索历史知识辅助当前任务。
---

# MemRec - AI记忆持久化系统

为AI CLI工具提供跨会话记忆能力，支持项目隔离和混合检索（KNN + BM25）。

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
memrec add "内容" --mtype <type> [--tag <tag>] [--global] [--source <source>] [--scope <scope>]
```

**记忆类型：**
- `decision` - 关键决策（推荐--tag critical）
- `knowledge` - 知识点（通过tag细分）
- `context` - 项目配置/环境信息
- `preference` - 用户偏好（推荐--global）
- `conversation` - 对话记录（默认）

**来源权重（--source）：**
| 值 | 说明 | 搜索权重 |
|-----|------|----------|
| `user`（默认） | 用户输入 | 最高 |
| `system` | 系统生成 | 中等 |
| `inferred` | AI推断 | 较低 |
| `external` | 外部导入 | 较低 |

**示例：**
```bash
# 事实类知识
memrec add "光速c=3×10⁸m/s，真空环境中恒定" --mtype knowledge --tag fact --tag physics
memrec add "欧拉公式：e^(iπ)+1=0" --mtype knowledge --tag fact --tag math

# 最佳实践
memrec add "RAII模式：资源获取即初始化，析构自动释放" --mtype knowledge --tag best-practice --tag rust

# 决策
memrec add "选择JWT认证方案" --mtype decision --tag auth --tag critical

# 用户偏好（来源明确标记）
memrec add "用户偏好详细输出" --mtype preference --tag output --global --source user

# 项目上下文
memrec add "技术栈：Rust+Tokio+RocksDB" --mtype context --tag tech

# AI推断的知识
memrec add "根据代码模式推断偏好函数式风格" --mtype knowledge --source inferred
```

### 混合检索

```bash
memrec search "关键词" [--project-only] [--global-only] [--all] [-k <num>]
```

**搜索流程：**
1. KNN + BM25 并行搜索，合并归一化分数
2. 时间衰减：近期记忆权重更高（knowledge/decision 豁免）
3. 来源权重：user > system > inferred/external
4. MMR 重排：结果多样性，减少冗余

**中文搜索：** 自动支持，使用 N-gram 分词器（2-4 字）

**搜索范围：**
| 选项 | 范围 | 用途 |
|------|------|------|
| 默认 | 当前项目 + 公共记忆 | 日常使用 |
| `--project-only` | 仅当前项目 | 精确项目内搜索 |
| `--global-only` | 仅公共记忆 | 查找用户偏好 |
| `--all` | 所有项目（跨项目） | 查找跨项目关联记忆 |

**高级选项：**
| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--hybrid-alpha` | KNN vs BM25权重（0=纯BM25，1=纯KNN） | 0.5 |
| `--mmr-enabled` | 启用MMR重排 | true |
| `--mmr-lambda` | MMR多样性（0=最大多样性，1=最大相关性） | 0.7 |
| `--min-score` | 最低相似度阈值 | 0.5（BGE-M3）/ 0.75（MiniLM） |

**示例：**
```bash
memrec search "认证方案"
memrec search "Rust最佳实践" --project-only
memrec search "用户偏好" --global-only -k 20
memrec search "xlsb" --all                    # 跨项目搜索
memrec search "架构" --human                  # 中文搜索
memrec search "算法" --hybrid-alpha 0.8       # 更偏重向量检索
memrec search "决策" --mmr-enabled false      # 禁用MMR
memrec search "知识" --mmr-lambda 0.5         # 更多样的结果
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
├── fts/                # Tantivy全文检索索引
├── models/             # ONNX embedding模型
└── memrecd.log         # 服务日志
```

---
