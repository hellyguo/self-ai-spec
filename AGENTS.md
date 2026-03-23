# AI Skills Repository

This repository contains skill definitions and coding specifications for AI coding agents.

## Project Overview

This is a Markdown-based documentation repository containing:
- **Skills**: Instructions for code review, compilation, refactoring, etc.
- **Language Specifications**: Detailed coding standards for Java, Python, C++, Rust, ANSI C, JavaScript
- **Agent Templates**: Template files for creating AGENTS.md in different project types

## Repository Structure

```
├── skills/                    # Skill definitions
│   ├── java-review/          # Java code review skill
│   ├── java-compile/         # Java compilation skill
│   ├── java-env/             # Java environment info
│   ├── java-gen-unittest/    # Java unit test generation
│   ├── java-inc-review/      # Java incremental review
│   ├── java-refactor/        # Java refactoring guidance
│   ├── java-g2m/             # Gradle to Maven conversion
│   ├── java-merge-agent-md/  # Merge Java AGENTS.md
│   ├── python-review/        # Python code review skill
│   ├── python-merge-agent-md/
│   ├── cpp-review/           # C++ code review skill
│   ├── cpp-merge-agent-md/
│   ├── rust-review/          # Rust code review skill
│   ├── rust-merge-agent-md/
│   ├── ansi-c-review/        # ANSI C code review skill
│   ├── ansi-c-merge-agent-md/
│   ├── js-merge-agent-md/     # JavaScript merge skill
│   └── code-deconstruct/     # Code to design document
├── lang-spec/                # Language coding specifications
│   ├── spec.java.md
│   ├── spec.python.md
│   ├── spec.cpp.md
│   ├── spec.rust.md
│   ├── spec.ansi_c.md
│   └── spec.js.md
└── agent-template/           # AGENTS.md templates
    ├── AGENTS.java.md
    ├── AGENTS.python.md
    ├── AGENTS.cpp.md
    ├── AGENTS.rust.md
    ├── AGENTS.ansi_c.md
    ├── AGENTS.js.md
    └── AGENTS.blank.md
```

## Build/Test Commands

This is a documentation repository with no code to build or test.

### Validation Commands

```bash
# Check Markdown syntax (if markdownlint is installed)
markdownlint '**/*.md'

# Check for broken links (if markdown-link-check is installed)
markdown-link-check README.md

# Validate YAML front matter in skill files
grep -r "^---$" skills/ | head -20
```

### Single File Validation

```bash
# Validate a specific skill file
markdownlint skills/java-review/SKILL.md

# Check a specific language specification
markdownlint lang-spec/spec.java.md
```

## Code Style Guidelines

### Markdown Formatting

1. **Headings**: Use ATX style (`# Heading`) with space after `#`
2. **Lists**: Use `-` for unordered lists, `1.` for ordered lists
3. **Code blocks**: Specify language for syntax highlighting
4. **Line length**: Maximum 120 characters
5. **Blank lines**: One blank line before/after headings and lists

### Skill File Format (SKILL.md)

Every skill file must have YAML front matter:

```markdown
---
name: skill-name
description: "Brief description of the skill"
---

# Title

## Overview

[Content...]
```

### Language Specification Format

Language specifications follow this structure:

1. **General Rules**: Universal coding principles
2. **Naming Conventions**: Variable, function, class naming
3. **Type System**: Language-specific type guidelines
4. **Error Handling**: Exception/error patterns
5. **Code Style**: Formatting and indentation
6. **Testing**: Test framework and conventions
7. **Performance**: Optimization guidelines

## Import/Reference Conventions

### Cross-File References

When referencing other files, use absolute paths:

```markdown
授权读取：/disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md

Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
```

### Skill Invocation

Skills are loaded by name:

```
skill /java-env      # Load Java environment skill
skill /java-review   # Load Java review skill
```

## Naming Conventions

### Files and Directories

- **Skill directories**: `kebab-case` (e.g., `java-review`, `code-deconstruct`)
- **Skill files**: `SKILL.md` (uppercase)
- **Language specs**: `spec.{language}.md` (e.g., `spec.java.md`)
- **Agent templates**: `AGENTS.{language}.md` (e.g., `AGENTS.java.md`)

### Document Titles

- Use clear, descriptive titles in Chinese or English
- Follow the pattern: `# {Language} 编码规范` or `# {Language} Coding Standards`

## Error Handling in Documentation

1. **Broken links**: Must be fixed before commit
2. **Missing references**: Document with `TODO` marker
3. **Outdated content**: Update version/section headers

## Git Commit Guidelines

1. Follow Conventional Commits specification
2. Commit after each file modification
3. Use Chinese commit messages for consistency
4. Do not push to remote unless explicitly requested

## Code Review Checklist

When reviewing skill or specification files:

- [ ] YAML front matter is correct
- [ ] Headings are properly nested
- [ ] Code blocks have language specified
- [ ] Cross-references use correct paths
- [ ] No broken internal links
- [ ] Consistent terminology throughout

## Symlink Setup

This repository is symlinked to multiple AI tool directories:

```
~/.opencode/skills   → /home/helly/code/markdown/ai-skills
~/.codebuddy/skills  → /home/helly/code/markdown/ai-skills
~/.qoder/skills      → /home/helly/code/markdown/ai-skills
```

## AI Agent Role Definition

When acting as an AI agent in this repository:

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