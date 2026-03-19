# AI Skills

AI agent skill definitions for guiding coding agents in code review, refactoring, compilation, and other tasks.

## Overview

This repository contains skill definitions used by various AI coding assistants. Each skill is a self-contained set of instructions that guides AI agents through specific tasks like code review, refactoring, compilation, and more.

## Symlink Setup

This repository is symlinked to multiple AI tool directories:

```
~/.opencode/skills   → /home/helly/code/markdown/ai-skills
~/.codebuddy/skills  → /home/helly/code/markdown/ai-skills
~/.qoder/skills      → /home/helly/code/markdown/ai-skills
```

This allows all AI tools to share the same skill definitions without duplication.

## Available Skills

### Code Review
| Skill | Language | Description |
|-------|----------|-------------|
| `java-review` | Java | Full codebase review |
| `java-inc-review` | Java | Incremental review (git/svn diff) |
| `cpp-review` | C++ | Full review with detailed rules |
| `ansi-c-review` | ANSI C | Full codebase review |
| `python-review` | Python | Full codebase review |
| `rust-review` | Rust | Full codebase review |

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

## Usage

Skills are automatically loaded by AI tools when a task matches the skill's purpose. See AGENTS.md for detailed documentation.