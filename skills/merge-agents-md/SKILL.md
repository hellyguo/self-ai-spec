---
name: merge-agents-md
description: "将语言特定的 AGENTS.md 模板合并进项目现有 AGENTS.md，保留项目特有内容并补齐通用规则。适用于新项目初始化 AGENTS.md、为既有项目补充语言规范。"
---

# 合并 AGENTS.md

## 概述

1. 将语言特定的 AGENTS.md 模板与项目当前目录下的 AGENTS.md 进行合并，生成更新后的 AGENTS.md 文件。
2. 填充模板中的占位符，按项目实际情况进行填充

### 环境变量

${AI_SPEC_ROOT} 定义在 bash/zsh 环境变量中，可被读取: `echo ${AI_SPEC_ROOT}`

## 语言支持

| 语言 | 模板文件 |
|------|----------|
| Java | `AGENTS.java.md` |
| Python | `AGENTS.python.md` |
| C++ | `AGENTS.cpp.md` |
| Rust | `AGENTS.rust.md` |
| Kotlin | `AGENTS.kotlin.md` |
| JavaScript | `AGENTS.js.md` |
| ANSI C | `AGENTS.ansi_c.md` |
| Shell | `AGENTS.shell.md` |

## 合并流程

### 1. 确定语言类型

根据以下方式确定语言类型：

- 用户明确指定语言
- 根据项目源代码文件类型自动推断
- 优先级：用户指定 > 自动推断

### 2. 授权读取模板

```
授权读取：${AI_SPEC_ROOT}/agent-templates/AGENTS.{lang}.md

Read ${AI_SPEC_ROOT}/agent-templates/AGENTS.{lang}.md
```

### 3. 合并规则

| 模板内容 | 项目内容 | 合后结果 |
|----------|----------|----------|
| 通用规则（交互规则、角色定位、工作准则等） | 无 | 直接添加 |
| 通用规则 | 已存在 | 以模板为准，补齐并替换旧版本 |
| 语言规范引用（spec/review/ci 路径） | 无 | 直接添加 |
| 语言规范引用 | 已存在 | 以模板为准，修正失效路径 |
| 项目特定内容（配置、命令、业务规则） | - | 保留不变，不被模板覆盖 |

### 4. 合并优先级

按内容类型划分权威，避免"模板优先"与"项目优先"相互冲突：

| 内容类型 | 权威来源 | 处理 |
|----------|----------|------|
| 项目事实（配置、命令、路径、业务规则、接口约定） | 项目 AGENTS.md | 保留，不得被模板覆盖 |
| 通用规则（交互规则、角色定位、工作准则） | 模板 | 以模板为准，补齐或替换旧版本 |
| 语言规范引用（spec/review/ci 文件路径） | 模板 | 以模板为准，缺失则补充 |
| 冲突条款 | 项目事实优先 | 保留项目条款，并在合并报告中标注冲突点 |

<HARD-GATE>
项目事实（配置、命令、路径、业务规则）不得被模板覆盖；通用规则与语言规范引用以模板为准。
</HARD-GATE>

1. **保留项目特有内容**：项目特有的配置、命令、规则不覆盖
2. **补充模板内容**：模板中有但项目中没有的内容，添加到项目
3. **校验一致性**：相同规则在不同版本中检查一致性
4. **内联优先**：篇幅小于 300 行时内联交互规则；超过 300 行时改为引用。
5. **篇幅控制**：超过 1000 行的 AGENTS.md 应压缩，优先合并重复条款。

### 5. 输出

合并后更新当前目录下的 `AGENTS.md` 文件。

## 合并示例

### Java 项目合并

```
# 读取 Java 模板
Read ${AI_SPEC_ROOT}/agent-templates/AGENTS.java.md

# 读取项目现有 AGENTS.md（如存在）
Read ./AGENTS.md

# 合并内容，输出到 ./AGENTS.md
Write ./AGENTS.md
```

### Python 项目合并

```
# 读取 Python 模板
Read ${AI_SPEC_ROOT}/agent-templates/AGENTS.python.md

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
