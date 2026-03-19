# AI Skills Repository

AI agent skill definitions for guiding coding agents in code review, refactoring, compilation, and other tasks.

## Repository Structure

```
ai-skills/
├── AGENTS.md                          # This file
├── README.md                          # Repository overview
├── {language}-review/                 # Code review skills
│   ├── SKILL.md                       # Skill definition
│   └── review-rules.md                # Detailed review rules (optional)
├── {language}-merge-agent-md/         # AGENTS.md merge skills
│   └── SKILL.md
├── {language}-env/                    # Environment config skills
│   └── SKILL.md
├── java-compile/                      # Compilation skills
├── java-g2m/                          # Gradle to Maven conversion
├── java-refactor/                     # Refactoring methodology
├── java-gen-unittest/                 # Unit test generation
├── code-deconstruct/                  # Code structure analysis
└── ...
```

## Skill File Format (SKILL.md)

Every skill must have a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: {skill-name}
description: "Brief description of the skill purpose"
---

# Title

## Overview
Brief description of what this skill does.

## Process
1. Step one
2. Step two
   1. Sub-step
3. Step three

## Output
Where and how to output results.

## Core Principles
Guiding principles for execution.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier, matches directory name |
| `description` | Yes | Brief description, starts with "该skill没有执行文件，为..." |

### Content Sections

| Section | Required | Description |
|---------|----------|-------------|
| 概述/Overview | Yes | What the skill accomplishes |
| 过程/Process | Yes | Step-by-step instructions |
| 输出/Output | Recommended | Output location and format |
| 核心原则/Core Principles | Recommended | Guiding philosophy |

## Naming Conventions

### Directory Names

- Pattern: `{language}-{action}` or `{language}-{subtype}-{action}`
- Use lowercase with hyphens
- Examples:
  - `java-review` - Java code review
  - `java-gen-unittest` - Java unit test generation
  - `ansi-c-review` - ANSI C code review
  - `cpp-review` - C++ code review
  - `python-merge-agent-md` - Merge Python AGENTS.md

### Language Prefixes

| Prefix | Language |
|--------|----------|
| `java` | Java |
| `cpp` | C++ |
| `ansi-c` | ANSI C |
| `python` | Python |
| `rust` | Rust |
| `js` | JavaScript/TypeScript |

### Action Suffixes

| Suffix | Purpose |
|--------|---------|
| `-review` | Code review/audit |
| `-env` | Environment configuration |
| `-compile` | Compilation |
| `-refactor` | Code refactoring |
| `-gen-unittest` | Unit test generation |
| `-merge-agent-md` | AGENTS.md merge |
| `-inc-review` | Incremental/diff-based review |
| `-g2m` | Gradle to Maven conversion |
| `-deconstruct` | Code structure analysis |

## Code Style Guidelines

### Skill Content Style

1. **Language**: Chinese (中文) for descriptions, English for code examples
2. **Numbered lists**: Use `1.` for all items (not incrementing)
3. **Indentation**: 3 spaces for sub-items
4. **Code blocks**: Always specify language
5. **Tables**: Use for structured data like rules, comparisons

### Review Skill Structure

```markdown
# 代码走查

## 概述

通过代码走查，找出代码中做得好的部分，找出做得不到位的部分

## 过程

1. 遍历所有的{ext}，确保对代码之间联系有清晰认识
1. 对设计进行梳理，对使用的设计模式进行整理
1. 重点走查可被复用/可被抽象的重复代码
1. 重点走查线程问题
   1. 线程创建必须命名
   1. 线程组必须存在关闭入口，且被调用
1. 重点走查代码结构
   1. if分发应优先考虑使用多态，次选switch
   1. if过大应予以抽取，形成独立方法
1. 重点检查过长、扇入/扇出过多的方法
1. 重点检查反复调用可缓存变量问题

## 输出

每次结果都以中文输出到 `doc/review/{skill-name}-{yyyymmdd}-{seq%000}.md` 中

## 核心原则

谦逊，目的是治病救人，目的不是羞辱人
```

### Language-Specific File Extensions

| Skill Prefix | File Extensions |
|--------------|-----------------|
| `java` | `*.java` |
| `cpp` | `*.cpp/*.hpp/*.c/*.h` |
| `ansi-c` | `*.c/*.h` |
| `python` | `*.py` |
| `rust` | `*.rs` |
| `js` | `*.js/*.ts` |

## Output File Conventions

### Review Output

- Path: `doc/review/{skill-name}-{yyyymmdd}-{seq%000}.md`
- Format: Markdown in Chinese
- Example: `doc/review/java-review-20260319-001.md`

### Deconstruct Output

- Class diagram: `doc/deconstruct/classes_graph.puml`
- Data flow: `doc/deconstruct/core_data_flow.puml` and `.md`
- Design docs: `doc/deconstruct/design_{package}/design.md`
- Global design: `doc/deconstruct/global_design.md`

## Available Skills

### Code Review Skills

| Skill | Description |
|-------|-------------|
| `java-review` | Full Java codebase review |
| `java-inc-review` | Incremental Java review (git/svn diff) |
| `cpp-review` | C++ codebase review with detailed rules |
| `ansi-c-review` | ANSI C codebase review |
| `python-review` | Python codebase review |
| `rust-review` | Rust codebase review |

### Build & Environment Skills

| Skill | Description |
|-------|-------------|
| `java-env` | Java environment configuration (JDK, Maven, tools) |
| `java-compile` | Java compilation with mvnd/mvn |
| `java-g2m` | Gradle to Maven project conversion |

### Code Generation Skills

| Skill | Description |
|-------|-------------|
| `java-gen-unittest` | Generate Java unit tests with mockito/powermock |
| `java-refactor` | Refactoring methodology and patterns |
| `code-deconstruct` | Generate class diagrams and design docs from code |

### AGENTS.md Merge Skills

| Skill | Source File |
|-------|-------------|
| `java-merge-agent-md` | AGENTS.java.md |
| `cpp-merge-agent-md` | AGENTS.cpp.md |
| `ansi-c-merge-agent-md` | AGENTS.ansi_c.md |
| `python-merge-agent-md` | AGENTS.python.md |
| `rust-merge-agent-md` | AGENTS.rust.md |
| `js-merge-agent-md` | AGENTS.js.md |

## Adding New Skills

1. Create directory: `{language}-{action}`
2. Create `SKILL.md` with frontmatter and content
3. Follow naming conventions above
4. Add detailed rules in `review-rules.md` if needed for review skills
5. Update this AGENTS.md if adding a new skill category

## Review Rules Format (review-rules.md)

When creating detailed review rules, use this structure:

```markdown
## 一、{Category}规则

### R{Category}.{Subcategory} 规则

| 规则ID | 规则描述 | 严重程度 | 检查方法 |
|--------|----------|----------|----------|
| R1.1.1 | Rule description | P0/P1/P2/P3 | How to check |

**检查命令**:
```bash
grep -rn "pattern" src/
```

**典型问题**:
```language
// 错误示例
// 正确示例
```
```

### Severity Levels

| Level | Description |
|-------|-------------|
| P0 | Critical - Must fix immediately |
| P1 | High - Should fix before release |
| P2 | Medium - Should fix when possible |
| P3 | Low - Nice to have |