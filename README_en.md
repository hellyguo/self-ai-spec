# AI Skills Repository

> Language: [中文](README.md) | [English](README_en.md)

A documentation repository of skills and language specifications for AI coding agents, providing unified skill
definitions for multiple AI coding tools.

## Important Prerequisite

**The environment variable is mandatory**: before using any script, you must set the `AI_SPEC_ROOT` environment variable
to the root directory of this repository.

**Why the environment variable is required**:

- Supports deployment through symbolic links to any directory
- Allows the repository to be moved to a different location
- Simplifies script invocation without specifying full paths
- Provides a unified way to locate resource files

All scripts and templates reference resource files through `${AI_SPEC_ROOT}` instead of hard-coded paths.

```bash
# Point AI_SPEC_ROOT at this repository
export AI_SPEC_ROOT="/path/to/your/self-ai-spec-directory"

# Persist the setting (append to ~/.bashrc or ~/.zshrc)
echo 'export AI_SPEC_ROOT="/path/to/your/self-ai-spec-directory"' >> ~/.bashrc
source ~/.bashrc
```

**Verify the configuration**:

```bash
echo $AI_SPEC_ROOT                     # should print the correct path
ls $AI_SPEC_ROOT/bin/                  # should list the script files
ls $AI_SPEC_ROOT/agent-templates/      # should list the template files
```

## Directory Structure

```text
self-ai-spec/
├── skills/             # skill definitions, one kebab-case directory + SKILL.md per skill
├── lang-spec/          # language specifications: spec.{lang}.md coding rules + review.{lang}.md review rules
├── agent-templates/    # agent templates: AGENTS.{lang}.md + interaction.rules.md
├── bin/                # quick-start scripts for AI tools and shared function library
├── docs/               # framework design documents (code review framework, deconstruct reports, etc.)
├── pi-extensions/      # pi extensions (memrec, etc., symbolic links)
├── dsh-plugins/        # dsh plugins (memrec, etc., symbolic links)
├── CHANGELOG.md        # change history
├── CHANGELOG_en.md     # change history (English)
├── README.md
└── README_en.md        # project overview (English)
```

## Available Skills

### Core Analysis Skills

| Skill | Purpose |
| :--- | :--- |
| `code-review` | Multi-language code review (Java/Kotlin/Python/C++/Rust/JS/ANSI C) plus database review |
| `code-deconstruct` | Deconstruct source code into design documents and ER diagrams (design perspective) |
| `sync-dev-spec` | Synchronize design specifications: derive development rules from code-deconstruct output and write them into AGENTS.md as daily development constraints |
| `requirement-collect` | Deconstruct source code into requirement documents (requirements perspective) |
| `code-detect-problem` | Project problem detection, scoring, and refactor/rebuild proposals |
| `code-detect-dup` | Code duplication detection (Simian + JSCPD) |
| `code-refactor` | Refactoring methodology |
| `code-part-modification` | Local code modification: complete features with minimal changes, avoid butterfly effects, support standalone test verification |
| `full-analysis` | Full analysis pipeline: design deconstruction → code review → duplication detection → problem detection → qualitative assessment |
| `qualitative-assessment` | System qualitative assessment: summarize system properties across design, development, operations, and non-functional dimensions based on full analysis output |
| `long-term-task` | Long-running tasks: understand, clarify, plan, and execute continuously |
| `lets-loop` | Continuous loop scheduling framework: a general framework for composing skills in loops |

### Static Analysis Tools

| Skill | Purpose |
| :--- | :--- |
| `cpp-check` | Cppcheck static analysis: C/C++ code quality checks (defects, undefined behavior, security vulnerabilities) |
| `cpp-clang-tidy` | Clang-Tidy static analysis: C/C++ code quality checks (based on the Clang AST, supports auto-fix) |
| `cpp-tscancode` | TscanCode static analysis: Tencent's open-source C/C++ code checker |
| `shell-check` | ShellCheck static analysis: Shell script quality checks (syntax errors, potential defects, code style) |
| `rust-clippy` | Clippy static analysis: Rust code quality checks (errors, style, performance, security), supports `cargo fix` auto-fix |
| `java-check-spotbugs` | SpotBugs static analysis: Java defect and security vulnerability detection |
| `java-check-pmd` | PMD static analysis: Java code quality, coding standard, and security issue detection |
| `ast-grep-block` | ast-grep based review gate: graded scanning of Java/C++/ANSI C with the code-checklist rule set |

### Java Development Tools

| Skill | Purpose |
| :--- | :--- |
| `java-env` | Java environment information |
| `java-g2m` | Gradle to Maven migration |
| `java-asprof` | Java performance analysis (async-profiler) |
| `jmh-bench` | JMH benchmarks |
| `java-coverage` | Java test coverage improvement strategy: 80%+ line coverage / 60%+ branch coverage, supports incremental and full test runs |

### Performance and Runtime Analysis

| Skill | Purpose |
| :--- | :--- |
| `gdb-heap-analysis` | GDB heap analysis: glibc ptmalloc memory leak/arena analysis in core dumps |
| `rust-flamegraph` | Rust flame graphs: CPU hotspot analysis and bottleneck localization (cargo flamegraph) |

### Document and Diagram Generation

| Skill | Purpose |
| :--- | :--- |
| `multype2txt` | Office/PDF to plain text: local binary conversion with zero token cost (doc/docx/ppt/pptx/xls/xlsx/pdf) |
| `md2pdf` | Markdown to PDF with automatic Mermaid and PlantUML rendering |
| `creating-mermaid-diagrams` | Mermaid diagram generation and export (PNG/SVG/PDF) supporting 11+ diagram types |
| `plantuml-skill` | PlantUML diagram generation and export (Kroki API, no local installation required) |
| `drawio-skill` | draw.io diagram generation and export (local desktop CLI) |
| `excalidraw-diagram` | Excalidraw hand-drawn style diagram JSON generation |
| `html-ppt` | Static HTML presentation generation (multiple styles, layouts, keyboard navigation) |
| `ppt-master` | Professional PPT design and production (PptxGenJS + SVG chart templates) |

### Engineering and Memory

| Skill | Purpose |
| :--- | :--- |
| `merge-agents-md` | Merge language templates into a project's AGENTS.md |
| `sql-extract` | SQL extraction: extract embedded SQL from C++/Java/XML sources and identify SQL concatenation points |
| `memrec` | AI memory persistence: cross-session memory storage and retrieval, project isolation, hybrid retrieval (KNN+BM25) |
| `semble-search` | Code search sub-agent: find implementations by intent, understand code, discover related code (semantic search) |
| `vbox-test-env` | VirtualBox three-machine test environment with mutual trust and sudo configured, suitable for cluster/distributed system testing |
| `sync-repo-docs` | Repository document synchronization: sync README/CHANGELOG/MANUAL based on git commits and standardize bilingual naming and cross-links |

## Language Specifications (lang-spec)

Each programming language provides the following related files (`ci` is available for some languages only):

| File type          | Purpose                                           | Example          |
| :----------------- | :------------------------------------------------ | :--------------- |
| `spec.{lang}.md`   | Coding standards, best practices, language guides | `spec.java.md`   |
| `review.{lang}.md` | Code review rules, static analysis rules, pattern detection | `review.java.md` |
| `ci.{lang}.md`     | Build/CI guidance (provided for some languages)   | `ci.java.md`     |

- **When coding**: consult `spec.{lang}.md` to keep the code compliant
- **When reviewing**: consult both `spec.{lang}.md` and `review.{lang}.md` for a complete check
- **Skill integration**: the `/code-review` skill automatically loads the corresponding language specification and
  review rules

## Agent Template Configuration

Language-specific agent templates live in `agent-templates/` and are used to configure project templates for AI tools:

- `AGENTS.java.md` - Java project configuration
- `AGENTS.kotlin.md` - Kotlin project configuration
- `AGENTS.ansi_c.md` - ANSI C project configuration
- `AGENTS.cpp.md` - C++ project configuration
- `AGENTS.rust.md` - Rust project configuration
- `AGENTS.python.md` - Python project configuration
- `AGENTS.js.md` - JavaScript project configuration
- `AGENTS.shell.md` - Shell/Bash project configuration
- `AGENTS.blank.md` - blank template

## Interaction Rules

- `rules/interaction.rules.md` - general interaction rules

### Usage

1. **Manual copy**: copy a template into the project root and rename it to `AGENTS.md`
2. **Script copy**: use the startup scripts in `bin/` to configure automatically
3. **Skill merge**: use `/merge-agents-md` to merge templates into an existing `AGENTS.md`

## Quick-Start Scripts

The `bin/` directory contains quick-start scripts for AI coding tools, supporting session resume and automatic language
template configuration.
Session IDs are stored in hidden files at the project root, managed independently per tool.

| Script | Tool | Session ID file | Session resume |
| :----- | :--- | :-------------- | :------------- |
| `bin/oc` | opencode | `.opencode_id` | Supported |
| `bin/cdbd` | codebuddy | `.codebuddy_id` | Supported |
| `bin/clc` | claudecode | `.claudecode_id` | Supported |
| `bin/pc` | pi | `.pi_id` | Supported |
| `bin/qcc` | qodercli | - | Not supported |
| `bin/common.sh` | shared function library (sourced by the scripts above) | - | - |

```bash
# New session: a language argument is required
./bin/oc java          # start opencode for a Java project
./bin/cdbd java        # start codebuddy for a Java project
./bin/clc java         # start claudecode for a Java project
./bin/pc java          # start pi for a Java project

# Resume session: no arguments, resumes automatically
./bin/oc              # resume the opencode session
./bin/cdbd            # resume the codebuddy session
./bin/clc             # resume the claudecode session
./bin/pc              # resume the pi session

# qodercli does not support session resume
./bin/qcc <language>  # start qodercli
```

**Supported language arguments**: `java`, `kotlin`, `ansi_c`, `cpp`, `rust`, `python`, `js`, `shell`, `blank`

### Session ID Update Scripts

```bash
./bin/updocid          # update the opencode session ID (from clipboard)
./bin/updcbid          # update the codebuddy session ID (from clipboard)
./bin/updccid          # update the claudecode session ID (from clipboard)
./bin/updpiid          # update the pi session ID (from clipboard)
```

### Smart Resume Logic

- A session ID file exists → resume the session directly, skipping template copying
- No session ID → a language argument is required to set up the project template
- Tools are independent: opencode, codebuddy, claudecode, and pi each manage their own session state

## Symbolic Link Deployment (Recommended)

For convenience, the scripts can be symbolically linked into your personal bin directory:

```bash
# Ensure ~/bin is on PATH
export PATH="$HOME/bin:$PATH"
mkdir -p ~/bin

# Create symbolic links
for s in oc cdbd clc qcc pc updocid updcbid updccid updpiid; do
  ln -sf $AI_SPEC_ROOT/bin/$s ~/bin/$s
done

# Verify the links
ls -la ~/bin/ | grep -E 'oc|cdbd|clc|qcc|pc|upd'

# Now usable from any directory:
oc java
cdbd python
updocid
```

## Extensions and Plugins

- `pi-extensions/` - pi tool extension directory (external implementations pulled in as symbolic links)
- `dsh-plugins/` - dsh tool plugin directory (external implementations pulled in as symbolic links)

Both currently link to the corresponding `memrec` implementations (`pi-extension` / `dsh-plugin`).

### Origins of Skills

Not all skills under `skills/` are version-controlled in this repository; there are three forms:

- **Maintained in this repository**: the directory and `SKILL.md` are tracked directly (for example `code-review`,
  `java-env`, `vbox-test-env`).
- **Symbolic links to external repositories**: diagram and presentation skills point to independent repositories
  (`creating-mermaid-diagrams`, `drawio-skill`, `excalidraw-diagram`, `html-ppt`, `plantuml-skill`, `ppt-master`)
  and are ignored in `skills/.gitignore`.
- **Maintained locally, not version-controlled**: `memrec`, `multype2txt`, `semble-search`, and similar skills; this
  repository only keeps placeholders and documentation, while implementations come from local or external sources.

> Note: `.system` is a runtime directory generated by tools and is likewise ignored.

## Security Review Principles

**Important**: sensitive data review is mandatory for all code reviews regardless of programming language:

- Are passwords, keys, tokens, API Keys, etc. hard-coded
- Is sensitive information written to logs or debug output
- Is sensitive data in memory securely cleared
- Are secure logging macros used to filter sensitive fields

## Detailed Documents

- Interaction rules and repository conventions: [AGENTS.md](AGENTS.md),
  [rules/interaction.rules.md](rules/interaction.rules.md)
- Code review framework design: [docs/code-review-framework.md](docs/code-review-framework.md)
- Full change history: [CHANGELOG_en.md](CHANGELOG_en.md)
- Chinese version: [README.md](README.md) | [CHANGELOG.md](CHANGELOG.md)
