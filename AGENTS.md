# AI Skills 仓库

AI 编码代理技能和语言规范的文档仓库，为多个 AI 编码工具提供统一的技能定义。

## 交互规则

1. 所有交互均使用简体中文
2. 每次产出文件后执行 git 提交
3. 提交遵循约定式提交规范（Conventional Commits）
4. 除非明确要求，不推送到远端

## 项目结构

```
self-ai-spec/
├── skills/                  # 技能定义目录
│   ├── java-review/         # Java 代码审查
│   ├── python-review/       # Python 代码审查
│   ├── cpp-review/          # C++ 代码审查
│   ├── rust-review/         # Rust 代码审查
│   └── ...                  # 其他技能
├── lang-spec/               # 语言编码规范
│   ├── spec.java.md         # Java 规范
│   ├── spec.python.md       # Python 规范
│   └── ...                  # 其他语言规范
└── agent-template/          # AGENTS.md 模板
    ├── AGENTS.java.md       # Java 项目模板
    └── ...                  # 其他语言模板
```

## 构建/验证命令

纯文档仓库，无需构建。验证命令：

```bash
# 验证所有 Markdown 文件
markdownlint '**/*.md'

# 验证单个文件
markdownlint skills/java-review/SKILL.md

# 检查链接有效性
markdown-link-check README.md

# 验证技能文件 YAML 前置数据
grep -r "^---$" skills/ | head -20

# 自动修复格式问题
markdownlint --fix '**/*.md'
```

## 代码风格指南

### Markdown 格式规范

- **标题**：ATX 风格，`#` 后加空格（`# 标题`）
- **列表**：无序列表用 `-`，有序列表用 `1.`
- **代码块**：始终指定语言以启用语法高亮
- **行长度**：最大 120 字符
- **空行**：标题和列表前后各一个空行
- **表格**：对齐列分隔符，表头与内容间有空行

### 技能文件格式（SKILL.md）

每个技能文件必须包含 YAML 前置数据：

```markdown
---
name: skill-name
description: "技能简介"
---

# 标题

## 概述

[内容...]
```

### 语言规范格式

`lang-spec/spec.{language}.md` 文件结构：

1. 通用规则
2. 命名约定
3. 类型系统
4. 错误处理
5. 代码风格
6. 测试
7. 性能

### 文件命名约定

| 类型 | 模式 | 示例 |
|------|------|------|
| 技能目录 | `kebab-case` | `java-review` |
| 技能文件 | `SKILL.md`（大写） | `SKILL.md` |
| 语言规范 | `spec.{lang}.md` | `spec.java.md` |
| 代理模板 | `AGENTS.{lang}.md` | `AGENTS.java.md` |

### 文档标题规范

使用清晰、描述性的中文标题，模式：`# {语言} 编码规范`

## 跨文件引用规范

引用其他文件时使用绝对路径和标准格式：

```markdown
授权读取：/disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md

Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
```

## AI 代理角色定义

在本仓库中操作时：

1. **角色**：资深架构师和开发者
2. **分析**：提供多套方案（上、中、下三策）
3. **设计**：考虑安全性、可扩展性、可用性、可观测性、性能
4. **沟通**：每次修改文件后提交

## 可用技能汇总

| 技能 | 语言 | 用途 |
|------|------|------|
| `java-review` | Java | 全量代码审查 |
| `java-inc-review` | Java | 增量审查（git/svn diff） |
| `java-compile` | Java | 编译指引 |
| `java-env` | Java | 环境信息 |
| `java-gen-unittest` | Java | 单元测试生成 |
| `java-refactor` | Java | 重构方法论 |
| `java-g2m` | Java | Gradle 转 Maven |
| `python-review` | Python | 全量代码审查 |
| `cpp-review` | C++ | 全量代码审查 |
| `rust-review` | Rust | 全量代码审查 |
| `ansi-c-review` | ANSI C | 全量代码审查 |
| `code-deconstruct` | 所有 | 生成设计文档 |
| `*-merge-agent-md` | 所有 | 合并 AGENTS.md 模板 |

## 符号链接设置

本仓库被符号链接到多个 AI 工具目录：

```
~/.opencode/skills   → /home/helly/code/markdown/ai-skills
~/.codebuddy/skills  → /home/helly/code/markdown/ai-skills
~/.qoder/skills      → /home/helly/code/markdown/ai-skills
```

## 文档审查检查清单

审查技能或规范文件时：

- [ ] YAML 前置数据正确
- [ ] 标题层级正确嵌套
- [ ] 代码块已指定语言
- [ ] 跨文件引用使用正确的绝对路径
- [ ] 无损坏的内部链接
- [ ] 术语使用一致
- [ ] 行长度不超过 120 字符

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 损坏的链接 | 提交前必须修复 |
| 缺失的引用 | 使用 `TODO` 标记记录 |
| 过时的内容 | 更新版本/章节标题 |
| 格式问题 | 使用 markdownlint --fix 修复 |

## 新增技能流程

1. 在 `skills/` 下创建 `kebab-case` 目录
2. 创建 `SKILL.md` 文件，包含 YAML 前置数据
3. 按技能类型添加内容：
   - 审查类：参考 `java-review/SKILL.md` 结构
   - 编译类：参考 `java-compile/SKILL.md` 结构
4. 更新 README.md 和 AGENTS.md 的技能汇总表
5. 运行 markdownlint 验证
6. 提交变更