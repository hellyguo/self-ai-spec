---
name: merge-agents-md
description: "通用 AGENTS.md 合并技能，支持多种编程语言模板"
---

# 合并 AGENTS.md

## 概述

将语言特定的 AGENTS.md 模板与项目当前目录下的 AGENTS.md 进行合并，生成更新后的 AGENTS.md 文件。

## 语言支持

| 语言 | 模板文件 |
|------|----------|
| Java | `AGENTS.java.md` |
| Python | `AGENTS.python.md` |
| C++ | `AGENTS.cpp.md` |
| Rust | `AGENTS.rust.md` |
| JavaScript | `AGENTS.js.md` |
| ANSI C | `AGENTS.ansi_c.md` |

## 合并流程

### 1. 确定语言类型

根据以下方式确定语言类型：

- 用户明确指定语言
- 根据项目源代码文件类型自动推断
- 优先级：用户指定 > 自动推断

### 2. 授权读取模板

```
授权读取：/disk2/helly_data/code/markdown/self-ai-spec/agent-template/AGENTS.{lang}.md

Read /disk2/helly_data/code/markdown/self-ai-spec/agent-template/AGENTS.{lang}.md
```

### 3. 合并规则

| 模板内容 | 项目内容 | 合后结果 |
|----------|----------|----------|
| 通用规则（交互规则、角色定位等） | 无 | 直接添加 |
| 通用规则 | 已存在 | 检查一致性，补充缺失项 |
| 语言特定规则（构建命令、代码风格等） | 无 | 直接添加 |
| 语言特定规则 | 已存在 | 以项目内容为主，模板内容为补充 |
| 项目特定内容 | - | 保留不变 |

### 4. 合并优先级

1. **保留项目特有内容**：项目特有的配置、命令、规则不覆盖
2. **补充模板内容**：模板中有但项目中没有的内容，添加到项目
3. **校验一致性**：相同规则在不同版本中检查一致性

### 5. 输出

合并后更新当前目录下的 `AGENTS.md` 文件。

## 合并示例

### Java 项目合并

```
# 读取 Java 模板
Read /disk2/helly_data/code/markdown/self-ai-spec/agent-template/AGENTS.java.md

# 读取项目现有 AGENTS.md（如存在）
Read ./AGENTS.md

# 合并内容，输出到 ./AGENTS.md
Write ./AGENTS.md
```

### Python 项目合并

```
# 读取 Python 模板
Read /disk2/helly_data/code/markdown/self-ai-spec/agent-template/AGENTS.python.md

# 读取项目现有 AGENTS.md（如存在）
Read ./AGENTS.md

# 合并内容，输出到 ./AGENTS.md
Write ./AGENTS.md
```

## 合并检查清单

合并完成后检查：

- [ ] 交互规则完整
- [ ] 构建命令正确
- [ ] 代码风格指南存在
- [ ] 语言特定规则已添加
- [ ] 项目特有内容保留
- [ ] 无冲突内容
- [ ] 格式规范（Markdown）

## 提交变更

合并完成后执行 git 提交：

```bash
git add AGENTS.md
git commit -m "docs: 更新 AGENTS.md 合并 {lang} 模板"
```