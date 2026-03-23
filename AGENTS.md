# AI Skills Repository

Documentation repository for AI coding agent skills and language specifications.

## Project Overview

This repository contains:
- **Skills**: Instructions for code review, compilation, refactoring, etc.
- **Language Specifications**: Coding standards for Java, Python, C++, Rust, ANSI C, JavaScript
- **Agent Templates**: Template files for creating AGENTS.md in different project types

## Build/Validation Commands

This is a documentation-only repository with no code to build or test.

```bash
# Validate all Markdown files (requires markdownlint-cli)
markdownlint '**/*.md'

# Validate a single file
markdownlint skills/java-review/SKILL.md

# Check for broken links (requires markdown-link-check)
markdown-link-check README.md

# Validate YAML front matter in skill files
grep -r "^---$" skills/ | head -20
```

## Code Style Guidelines

### Markdown Formatting

- **Headings**: ATX style with space after `#` (`# Heading`)
- **Lists**: Use `-` for unordered, `1.` for ordered
- **Code blocks**: Always specify language for syntax highlighting
- **Line length**: Maximum 120 characters
- **Blank lines**: One before/after headings and lists

### Skill File Format (SKILL.md)

Every skill file requires YAML front matter:

```markdown
---
name: skill-name
description: "Brief skill description"
---

# Title

## Overview

[Content...]
```

### Language Specification Format

Follow this structure for `lang-spec/spec.{language}.md`:

1. **通用规则** (General Rules): Universal coding principles
2. **命名约定** (Naming Conventions): Variable, function, class naming
3. **类型系统** (Type System): Language-specific type guidelines
4. **错误处理** (Error Handling): Exception/error patterns
5. **代码风格** (Code Style): Formatting and indentation
6. **测试** (Testing): Test framework and conventions
7. **性能** (Performance): Optimization guidelines

### File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Skill directories | `kebab-case` | `java-review`, `code-deconstruct` |
| Skill files | `SKILL.md` (uppercase) | `SKILL.md` |
| Language specs | `spec.{lang}.md` | `spec.java.md` |
| Agent templates | `AGENTS.{lang}.md` | `AGENTS.java.md` |

### Document Titles

Use clear, descriptive titles in Chinese or English:
- Pattern: `# {Language} 编码规范` or `# {Language} Coding Standards`

## Cross-File References

Use absolute paths when referencing other files:

```markdown
授权读取：/disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md

Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
```

## Git Commit Guidelines

1. Follow Conventional Commits specification
2. Commit after each file modification
3. Use Chinese commit messages for consistency
4. Do not push to remote unless explicitly requested

## AI Agent Role Definition

When operating in this repository:

1. **Role**: Senior architect and developer
2. **Analysis**: Provide multiple solutions (upper, middle, lower strategies)
3. **Design**: Consider security, scalability, availability, observability, performance
4. **Communication**: Commit after each file modification

## Available Skills Summary

| Skill | Language | Purpose |
|-------|----------|---------|
| `java-review` | Java | Full codebase review |
| `java-inc-review` | Java | Incremental review (git/svn diff) |
| `java-compile` | Java | Compilation guidance |
| `java-env` | Java | Environment information |
| `java-gen-unittest` | Java | Unit test generation |
| `java-refactor` | Java | Refactoring methodology |
| `java-g2m` | Java | Gradle to Maven conversion |
| `python-review` | Python | Full codebase review |
| `cpp-review` | C++ | Full codebase review |
| `rust-review` | Rust | Full codebase review |
| `ansi-c-review` | ANSI C | Full codebase review |
| `code-deconstruct` | All | Generate design documents |
| `*-merge-agent-md` | All | Merge AGENTS.md templates |

## Symlink Setup

This repository is symlinked to multiple AI tool directories:

```
~/.opencode/skills   → /home/helly/code/markdown/ai-skills
~/.codebuddy/skills  → /home/helly/code/markdown/ai-skills
~/.qoder/skills      → /home/helly/code/markdown/ai-skills
```

## Code Review Checklist

When reviewing skill or specification files:

- [ ] YAML front matter is correct
- [ ] Headings are properly nested
- [ ] Code blocks have language specified
- [ ] Cross-references use correct absolute paths
- [ ] No broken internal links
- [ ] Consistent terminology throughout

## Error Handling

1. **Broken links**: Must be fixed before commit
2. **Missing references**: Document with `TODO` marker
3. **Outdated content**: Update version/section headers