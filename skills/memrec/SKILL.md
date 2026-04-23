---
name: memrec
description: AI记忆持久化系统。使用memrec存储、检索、管理跨会话记忆。触发场景：(1)重要决策需记录，(2)关键知识需保存，(3)项目上下文需跨会话保持，(4)用户偏好需记忆，(5)检索历史知识辅助当前任务。
---

# MemRec - AI记忆持久化系统

为AI CLI工具提供跨会话记忆能力，通过Unix Socket与memrecd守护进程通信。

## 核心命令

### 存储记忆

```bash
# 添加决策记录
memrec add "选择JWT+OAuth2认证方案" --mtype decision --tag auth --tag security --tag critical

# 添加知识点
memrec add "Rust RocksDB使用rocksdb crate" --mtype knowledge --tag rust --tag storage

# 添加项目上下文
memrec add "项目使用clap构建CLI" --mtype context --tag config --tag cli

# 添加用户偏好
memrec add "用户偏好英文输出" --mtype preference --tag output --tag lang
```

**记忆类型：**
- `decision` - 关键决策（推荐用critical标签）
- `knowledge` - 知识点/最佳实践
- `context` - 项目配置/环境信息
- `preference` - 用户偏好
- `conversation` - 对话记录（默认）

### 检索记忆

```bash
# 查看所有记忆
memrec list --limit 20

# 获取特定记忆
memrec get <memory-id>

# 查看统计
memrec stats
```

### 删除记忆

```bash
# 软删除（可恢复）
memrec delete <memory-id>

# 再次删除会硬删除
memrec delete <memory-id>  # 第二次执行
```

## 使用模式

### 模式1：关键决策记录

**触发：做出技术决策、架构选择时**

```bash
# 决策后立即记录
memrec add "决定使用SQLite替代MySQL，因为单用户场景" --mtype decision --tag database --tag architecture --tag critical
```

**检索：遇到类似问题时**

```bash
memrec list
# 找到历史决策，避免重复讨论
```

### 模式2：知识积累

**触发：学到新知识、发现最佳实践时**

```bash
memrec add "Tokio runtime必须在main中使用#[tokio::main]" --mtype knowledge --tag rust --tag async
```

**检索：需要相关知识时**

```bash
memrec list --limit 10
# 找到历史知识库
```

### 模式3：项目上下文保持

**触发：项目初始化或关键配置时**

```bash
memrec add "项目目录: ~/work/myapp，技术栈: Rust+Tokio+RocksDB" --mtype context --tag project --tag setup
```

**检索：新会话恢复上下文**

```bash
memrec list
# 快速恢复项目上下文，无需重新探索
```

### 模式4：用户偏好记忆

**触发：用户表达偏好时**

```bash
memrec add "用户偏好使用详细模式输出，不喜欢简洁模式" --mtype preference --tag output --tag style
```

**检索：做出符合用户偏好的决策**

```bash
memrec list
# 根据历史偏好调整行为
```

## 工作流集成

### 工作开始时

```bash
# 启动守护进程（如未启动）
memrecd

# 检索相关记忆
memrec list --limit 10

# 恢复项目上下文
memrec list
```

### 工作过程中

**记录时机：**
- 做出重要决策后
- 学到关键知识后  
- 发现最佳实践后
- 用户表达偏好后

```bash
# 实时记录
memrec add "重要内容" --mtype decision --tag critical
```

### 工作结束时

```bash
# 查看本次会话添加的记忆
memrec stats

# 如有需要，记录总结
memrec add "本次会话完成XXX，关键决策YYY" --mtype context --tag session
```

## 标签策略

**推荐标签：**
- `critical` - 关键信息（最高权重）
- `decision` - 决策记录
- `project:<name>` - 项目特定
- `module:<name>` - 模块特定
- `tech:<name>` - 技术栈
- `temp` - 临时记忆（低权重）

**标签作用：**
1. 分类检索
2. 影响重要性评分（critical=1.0, temp=0.1）
3. 记忆生命周期管理

## 记忆管理

系统自动管理记忆生命周期：

- **重要性评分**：时间衰减 + 访问频率 + 标签权重 + 用户标记
- **压缩**：低重要性记忆自动压缩为摘要
- **遗忘**：重要性<0.1且90天未访问会删除

**手动干预：**
```bash
# 查看统计
memrec stats

# 删除不需要的记忆
memrec delete <id>
```

## 最佳实践

1. **决策即记录** - 做出决策后立即记录，避免遗忘
2. **关键用critical** - 重要信息用critical标签，权重最高
3. **定期检索** - 开始工作时检索历史记忆，恢复上下文
4. **标签规范** - 使用统一标签规范，便于检索和管理
5. **类型明确** - 使用正确的记忆类型，便于分类管理

## 长文本处理

超过7.5KB的文本会自动拆分：
```bash
# CLI自动拆分并添加part标签
memrec add "长文档内容..." --mtype knowledge --tag doc

# 输出：
# WARN: Content too long, auto-splitting into chunks...
# WARN: Split into 3 parts
# Part 1: Added [id1] (tags: part:1-3, part:first)
# Part 2: Added [id2] (tags: part:2-3)
# Part 3: Added [id3] (tags: part:3-3, part:last)
```

## 守护进程

```bash
# 启动（自动）
memrecd

# 检查运行状态
ps aux | grep memrecd

# Socket位置
~/.memrec/memrecd.sock
```

## 数据位置

```
~/.memrec/
├── memrecd.sock    # Unix Socket
├── data/           # RocksDB数据
└── config.toml     # 配置（可选）
```