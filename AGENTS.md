# AI Skills 仓库

AI 编码代理技能和语言规范的文档仓库，为多个 AI 编码工具提供统一的技能定义。

## 交互规则

1. 所有交互均使用简体中文
2. 每次产出文件后执行 git 提交
3. 提交遵循约定式提交规范（Conventional Commits）
4. 除非明确要求，不推送到远端

## 验证命令

```bash
markdownlint '**/*.md'          # 验证所有 Markdown
markdownlint --fix '**/*.md'    # 自动修复格式
grep -r "^---$" skills/ | head  # 验证 YAML 前置数据
```

## 技能文件格式

每个 SKILL.md 必须包含 YAML 前置数据：

```markdown
---
name: skill-name
description: "技能简介"
---
```

## 可用技能

| 技能 | 用途 |
|------|------|
| `code-review` | 多语言代码审查（Java/Python/C++/Rust/JS/ANSI C）+ 数据库审查 |
| `code-deconstruct` | 源代码解构为设计文档、ER图（设计层面） |
| `requirement-collect` | 源代码解构为需求文档（需求层面） |
| `code-detect-problem` | 项目问题侦测、评分、重构/重建方案 |
| `code-detect-dup` | 代码重复度检测 |
| `code-refactor` | 重构方法论 |
| `merge-agents-md` | 合并语言模板到项目 AGENTS.md |
| `lets-loop` | 循环代码坏味道检测：性能问题、复杂度热点、N+1查询 |
| `long-task` | 长任务执行：理解、澄清、计划、连续执行 |
| `java-compile` | Java 编译指引 |
| `java-env` | Java 环境信息 |
| `java-gen-unittest` | Java 单元测试生成 |
| `java-g2m` | Gradle 转 Maven |
| `java-asprof` | Java 性能分析（async-profiler） |
| `jmh-bench` | JMH 基准测试 |

## 文件命名约定

| 类型 | 模式 | 示例 |
|------|------|------|
| 技能目录 | `kebab-case` | `code-review` |
| 技能文件 | `SKILL.md`（大写） | `SKILL.md` |
| 语言规范 | `spec.{lang}.md` | `spec.java.md` |
| 代理模板 | `AGENTS.{lang}.md` | `AGENTS.java.md` |

## 跨文件引用规范

```markdown
授权读取：/disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
```

## 新增技能流程

1. 在 `skills/` 下创建 `kebab-case` 目录
2. 创建 `SKILL.md`，包含 YAML 前置数据
3. 更新本文件技能表
4. 运行 `markdownlint` 验证
5. 提交变更