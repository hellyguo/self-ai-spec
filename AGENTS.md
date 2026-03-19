# AI Skills Repository

AI agent skill definitions for guiding coding agents in code review, refactoring, compilation, and other tasks.

## Overview

This repository contains skill definitions used by various AI coding assistants. Each skill is a self-contained set of instructions that guides AI agents through specific tasks.

## Symlink Setup

This repository is symlinked to multiple AI tool directories:

```
~/.opencode/skills   → /home/helly/code/markdown/ai-skills
~/.codebuddy/skills  → /home/helly/code/markdown/ai-skills
~/.qoder/skills      → /home/helly/code/markdown/ai-skills
```

## Skill File Format (SKILL.md)

Every skill must have a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: {skill-name}
description: "该skill没有执行文件，为..."
---

# Title

## 概述
What this skill accomplishes.

## 过程
1. Step one
2. Step two

## 输出
Output location and format.

## 核心原则
Guiding philosophy.
```

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Unique identifier, matches directory name |
| `description` | Starts with "该skill没有执行文件，为..." |

## Naming Conventions

### Pattern

`{language}-{action}` or `{language}-{subtype}-{action}`

### Language Prefixes

| Prefix | Language | Extensions |
|--------|----------|------------|
| `java` | Java | `*.java` |
| `cpp` | C++ | `*.cpp/*.hpp/*.c/*.h` |
| `ansi-c` | ANSI C | `*.c/*.h` |
| `python` | Python | `*.py` |
| `rust` | Rust | `*.rs` |
| `js` | JavaScript/TypeScript | `*.js/*.ts` |

### Action Suffixes

| Suffix | Purpose |
|--------|---------|
| `-review` | Code review/audit |
| `-inc-review` | Incremental review (git/svn diff) |
| `-env` | Environment configuration |
| `-compile` | Compilation |
| `-refactor` | Code refactoring |
| `-gen-unittest` | Unit test generation |
| `-merge-agent-md` | AGENTS.md merge |
| `-g2m` | Gradle to Maven conversion |
| `-deconstruct` | Code structure analysis |

## Code Style Guidelines

1. **Language**: Chinese for descriptions, English for code examples
2. **Numbered lists**: Use `1.` for all items
3. **Indentation**: 3 spaces for sub-items
4. **Code blocks**: Always specify language
5. **Tables**: Use for structured data

## Output Conventions

| Skill Type | Path Pattern |
|------------|--------------|
| Review | `doc/review/{skill-name}-{yyyymmdd}-{seq%000}.md` |
| Deconstruct | `doc/deconstruct/*.puml`, `doc/deconstruct/design_*/design.md` |

## Available Skills

### Code Review

| Skill | Description |
|-------|-------------|
| `java-review` | Full Java codebase review |
| `java-inc-review` | Incremental Java review |
| `cpp-review` | C++ review with detailed rules |
| `ansi-c-review` | ANSI C codebase review |
| `python-review` | Python codebase review |
| `rust-review` | Rust codebase review |

### Build & Environment

| Skill | Description |
|-------|-------------|
| `java-env` | Java environment (JDK, Maven) |
| `java-compile` | Java compilation |
| `java-g2m` | Gradle to Maven conversion |

### Code Generation

| Skill | Description |
|-------|-------------|
| `java-gen-unittest` | Generate unit tests |
| `java-refactor` | Refactoring methodology |
| `code-deconstruct` | Generate design docs |

### AGENTS.md Merge

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
3. Add `review-rules.md` if needed
4. Update this file if adding a new category