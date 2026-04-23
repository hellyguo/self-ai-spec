---
name: memrec
description: AI记忆持久化系统。使用memrec存储、检索、管理跨会话记忆。支持项目隔离和语义检索。触发场景：(1)重要决策需记录，(2)关键知识需保存，(3)项目上下文需跨会话保持，(4)用户偏好需记忆，(5)检索历史知识辅助当前任务。
---

# MemRec - AI记忆持久化系统 (Phase 6)

为AI CLI工具提供跨会话记忆能力，支持项目隔离和语义检索。

## 核心原则

**MemRec是面向AI Agent的工具：**
- 默认JSON输出，便于AI解析
- 自动项目检测，无需手动管理
- 语义检索优先，标签过滤次要

## 触发场景

1. 重要决策需记录 → `memrec add --mtype decision --tag critical`
2. 关键知识需保存 → `memrec add --mtype knowledge`
3. 项目上下文需跨会话保持 → 自动关联项目ID
4. 用户偏好需记忆 → `memrec add --mtype preference --global`
5. 检索历史知识辅助当前任务 → `memrec search "关键词"`

## 核心命令

### 存储记忆

```bash
memrec add "内容" --mtype <type> [--tag <tag>] [--global]
```

**记忆类型：**
- `decision` - 关键决策（推荐--tag critical）
- `knowledge` - 知识点/最佳实践
- `context` - 项目配置/环境信息
- `preference` - 用户偏好（推荐--global）
- `conversation` - 对话记录（默认）

**参数：**
- `--global` - 标记为公共记忆（跨项目共享）
- `--tag` - 添加标签（可多次使用）

**示例：**
```bash
# 项目记忆（自动关联项目ID）
memrec add "选择JWT认证方案" --mtype decision --tag auth --tag critical

# 公共记忆（跨项目共享）
memrec add "用户偏好详细输出" --mtype preference --tag output --global

# 项目上下文
memrec add "技术栈：Rust+Tokio+RocksDB" --mtype context --tag tech
```

### 语义检索

```bash
memrec search --query "关键词" [--mtype <type>] [--project-only] [--global-only] [-k <num>]
```

**参数：**
- `--query` - 搜索文本（必填）
- `--project-only` - 仅当前项目记忆
- `--global-only` - 仅公共记忆
- `-k` - 返回数量（默认10）
- `--min-score` - 最低相似度（默认0.7）
- `--mtype` - 过滤类型
- `--human` - 人类可读格式（默认JSON）

**示例：**
```bash
# 默认检索项目+公共
memrec search --query "认证方案"

# 仅项目记忆
memrec search --query "Rust最佳实践" --project-only

# 仅公共记忆
memrec search --query "用户偏好" --global-only -k 20

# 人类可读格式
memrec search --query "架构" --human
```

### 获取记忆

```bash
memrec get <memory-id> [--merge]
```

**参数：**
- `--merge` - 合并分块记忆（获取完整内容）

### 列表检索

```bash
memrec list [--limit <num>] [--project-only] [--global-only]
```

**参数：**
- `--project-only` - 仅项目记忆
- `--global-only` - 仅公共记忆

### 其他命令

```bash
# 统计信息
memrec stats

# 版本检查
memrec version

# 删除记忆
memrec delete <memory-id>
```

## 项目隔离

### 公共记忆 vs 项目记忆

| 类型 | project_id | 用途 |
|------|-----------|------|
| 公共记忆 | `Uuid::nil()` | 跨项目共享知识和用户偏好 |
| 项目记忆 | 具体UUID | 项目特定决策和上下文 |

### 项目ID自动检测

系统自动检测项目ID：
1. 查找Git根目录
2. 检查 `.mr_pid` 文件
3. 无则自动生成

**`.mr_pid` 文件示例：**
```
memrec_project_id=550e8400-e29b-41d4-a716-446655440000
created_at=2026-04-23T10:30:00Z
```

### 检索范围

| 参数 | 检索范围 |
|------|---------|
| 默认 | 项目记忆 + 公共记忆 |
| `--project-only` | 仅项目记忆 |
| `--global-only` | 仅公共记忆 |

## 长文本处理

超过7.5KB自动拆分：
- 每块独立embedding
- 共享 `chunk_group_id`
- 使用 `--merge` 获取完整内容

## 工作流集成

### 开始任务

```bash
# 检索相关历史
memrec search --query "相关历史" --project-only

# 查看项目记忆统计
memrec stats
```

### 做出决策后

```bash
memrec add "选择XXX方案" --mtype decision --tag critical
```

### 用户表达偏好后

```bash
memrec add "用户偏好YYY" --mtype preference --global
```

### 结束任务

```bash
memrec stats
```

## 安装与管理

### 安装

```bash
cargo build --release
install -m 755 target/release/memrecd ~/.local/bin/
install -m 755 target/release/memrec ~/.local/bin/
./scripts/systemd/install.sh
systemctl --user enable memrecd
systemctl --user start memrecd
```

### 管理

```bash
# Systemd管理
systemctl --user status memrecd
systemctl --user restart memrecd
journalctl --user -u memrecd -f

# 或使用脚本
./scripts/status.sh
./scripts/restart.sh
```

### 验证

```bash
memrec version
memrec stats
memrec search --query "test"
```

## 数据位置

```
~/.memrec/
├── memrecd.sock      # Unix Socket
├── memrecd.pid       # PID文件
├── memrecd.log       # 日志文件
├── db/               # RocksDB数据
└── qdrant/           # 向量索引
```

## 性能指标

- 内存占用：约3.6MB
- 启动时间：<50ms
- 请求延迟：<1ms
- Embedding：本地生成，CPU友好

## 最佳实践

1. **决策即记录** - 做出决策后立即记录
2. **关键用critical** - 重要信息用critical标签
3. **偏好用global** - 用户偏好标记为公共记忆
4. **检索优先search** - 用语义检索而非枚举
5. **版本检查** - 定期检查CLI和服务版本一致性

---

*Updated: 2026-04-23 Phase 6*