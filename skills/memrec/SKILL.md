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
memrec search "关键词" [--project-only] [--global-only] [-k <num>]
```

**示例：**
```bash
memrec search "认证方案"
memrec search "Rust最佳实践" --project-only
memrec search "用户偏好" --global-only -k 20
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

| 类型 | 用途 |
|------|------|
| 公共记忆（--global） | 跨项目共享知识和用户偏好 |
| 项目记忆 | 项目特定决策和上下文 |

**检索范围：**
- 默认：项目记忆 + 公共记忆
- `--project-only`：仅项目记忆
- `--global-only`：仅公共记忆

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

---