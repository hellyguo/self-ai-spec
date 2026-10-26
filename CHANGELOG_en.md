# Change History

> Back to index: [README_en.md](README_en.md) | 中文：[CHANGELOG.md](CHANGELOG.md)

## 2026-10-26

### Documentation Bilingualization

- **New English documents**: `README_en.md` and `CHANGELOG_en.md`, semantically consistent with the Chinese versions
- **Cross-links completed**: `README.md` / `README_en.md` link to each other, `CHANGELOG.md` / `CHANGELOG_en.md` link to
  each other, and each bilingual README references the CHANGELOG in its own language
- **MANUAL decision**: this repository does not provide `MANUAL.md`; usage guidance is carried by `README.md` and the
  skill documents under `skills/`

### Skill and Specification Consolidation

- **Skill merges**: removed `java-compile` and `java-gen-unittest`
  - The compile commands of `java-compile` moved into `lang-spec/ci.java.md`; environment verification remains the
    responsibility of `java-env`
  - The test-writing workflow of `java-gen-unittest` moved into the "Test Writing Workflow" of `java-coverage`, so the
    coverage skill now covers both generation and measurement
  - `README.md`, `AGENTS.md`, `skills/code-part-modification`, and `skills/lets-loop/templates` updated accordingly
- **java-coverage fixes**: removed delegation to the non-existent `131-java-testing-unit-testing` and
  `spring-boot-test`, inlining the test guidance instead; added a "Scope" section clarifying its role in the fixed-file
  workflow; unified `mvn test` as `mvnd test`
- **AST rule deduplication**: `code-review` no longer maintains concrete rules and now points to `ast-grep-block` and
  `sql-extract`; five commonly used rules moved to section 11 of `ast-grep-block/templates/recipes.md`
- **Skill origin labels**: the skill table in `AGENTS.md` gained a "Source" column distinguishing this repository,
  locally untracked, and external symlinked skills
- **Template deduplication**: the local Java tool table moved from `AGENTS.java.md` into `java-env`, leaving only a
  pointer in the template; the rarely used `jitwatch-ui` was removed from `java-env`
- **Python review rules**: merged the overlapping "Code Quality Review Rules" and "Code Quality and Bad Smells" in
  `review.python.md`, with the bad smells table kept as section 3 (1.3.0 -> 1.3.1)
- **README correction**: `sync-repo-doc` corrected to `sync-repo-docs`
- **spec.java.md split assessment**: not splitting for now. Although the concurrency chapter is long, splitting would
  require synchronizing `review.java.md`, `AGENTS.java.md`, and all referenced anchors; the benefit is lower than the
  risk of broken links. Reassess when on-demand loading becomes a requirement

## 2026-10-23

### Prohibit Multiple Variable Declarations on a Single Line Across All Languages

- **Eight language coding standards**: added a high-priority "Variable Declarations" rule prohibiting multiple
  declarations on one line
  - Declaring several variables with commas in one statement is forbidden; each variable must occupy its own line
  - Mixed pointer and plain variable declarations (`int* p, q;`) must be split to avoid misreading
  - Multiple loop variables in a `for` loop must be split or initialized in advance
  - Pattern destructuring (Rust tuple destructuring, Kotlin destructuring declarations, Python tuple unpacking) is a
    single-assignment pattern match and is not treated as a multi-variable declaration
  - Affected files: `lang-spec/spec.js.md`, `spec.cpp.md`, `spec.ansi_c.md`, `spec.rust.md`, `spec.java.md`,
    `spec.shell.md`, `spec.kotlin.md`, `spec.python.md`
- **Code review framework**: the code quality rules in `skills/code-review/SKILL.md` gained a variable declaration check
  marked as high priority and applicable to all languages
- **Review rules**: the "Must Fix (High Priority)" lists in `review.java.md`, `review.cpp.md`, `review.ansi_c.md`, and
  `review.kotlin.md` gained the same single-line declaration check

## 2026-10-21

### Fan-in and Fan-out Design Rules Added to the Java Coding Standard

- **Java coding standard**: added a "Fan-in and Fan-out" subsection under "Design Patterns" (version 1.3.0 -> 1.4.0)
  - Core principle: abstraction follows fan-in, constraints follow fan-out; abstraction benefit is approximately `fan-in
    × change frequency`
  - Modules are split by reason for change, not by functional relatedness or technical layering
  - Business data must not directly control flow; split into a decision-rule interface, a rule-parameter data interface,
    and a route strategy
  - Behavioral interfaces return immutable decision objects and distinguish success/business rejection/system
    failure/unknown result; data interfaces are typed and distinguish missing/empty/zero states
  - Unit test boundaries equal interface boundaries; "at which stage does a change explode" is the inverse indicator for
    design trade-offs; hot paths eliminate hard branching on business data
- **Interface design correction**: "interface fan-out should not be limited" corrected to "interface fan-in should not
  be limited, while an interface's own fan-out must be controlled", removing the contradiction with the fan-in/fan-out
  principle
- **File size limit alignment**: the Java single-file line limit changed from "recommended not to exceed 2000 lines" to
  "split above 500 lines, must split above 1000 lines", consistent with `skills/code-review/SKILL.md`
- Source: memrec design preference record (2026-10-21, module design principles / fan-in and fan-out)

## 2026-10-16

### Computation and Branching Rules Added to Language Specifications

- **Java / C++ / ANSI C / Rust coding standards**: added a "Computation and Branching" chapter
  - Precompute where possible: perform computations that can be determined in advance at program, class, or module
    initialization to reduce runtime work
  - Loop-invariant expressions: expressions whose result is unchanged across iterations should be hoisted out of the
    loop and computed once
  - Whole-loop invariants: values that stay constant throughout the loop should be moved outside the loop rather than
    computed inside
  - Branches should read positively (affirmatively) rather than negatively; negated conditions increase reading
    difficulty
  - Affected files: `lang-spec/spec.java.md`, `spec.cpp.md`, `spec.ansi_c.md`, `spec.rust.md` (version 1.2.0 -> 1.3.0)

## 2026-10-12

### New Design Specification Skill

- **sync-dev-spec skill**: distills the descriptive output of code-deconstruct into normative development specifications
  - Checks the completeness of deconstruction artifacts first; runs code-deconstruct when artifacts are missing or
    shallow
  - Each rule has five fields: identifier (DS-{seq}), constraint, rationale, evidence, and scope
  - Inconsistencies, open questions, and gaps are escalated to the user for a decision rather than applying generic best
    practices absent from the code
  - The complete specification is written to `docs/dev-spec/design-charter.md`; constraint entries go into the `## 设计规约`
    section of the project's `AGENTS.md`; can be rerun for incremental synchronization
  - Location: `skills/sync-dev-spec/SKILL.md`, templates `templates/design-charter.md`, `templates/agents-section.md`
- Commits:
  - Commit: `41f7da3` feat: add sync-dev-spec skill turning deconstruct outputs into design charter
- Background: dev-balance (a seven-dimension questionnaire baseline, tag `20261012_dropped_dev-balance`) was retired
  because a fixed option menu cannot cover project diversity; replaced by deriving specifications from code facts

## 2026-10-08

### New Document Synchronization Skill

- **sync-repo-doc skill**: synchronizes repository documents based on git commits (`skills/sync-repo-docs/SKILL.md`)
  - File naming: all caps; Chinese versions without a suffix and English versions ending with `_en`
  - Three document pairs: README.md/README_en.md, CHANGELOG.md/CHANGELOG_en.md, MANUAL.md/MANUAL_en.md
  - Each pair cross-links, and each README references the CHANGELOG/MANUAL in its own language
  - Missing README/CHANGELOG are added automatically; adding MANUAL and expanding to bilingual requires user
    confirmation
- Commits:
  - Commit: `b2c16be` doc: new skill sync-repo-docs
  - Commit: `62bc591` doc: update skill sync-repo-docs
  - Commit: `0511a60` doc: update skill sync-repo-docs

### Document Synchronization

- **`sync-repo-doc` added to the skill tables in README.md and AGENTS.md** (Engineering and Memory category)
- **CHANGELOG.md and README.md cross-links completed**: added a back-to-README link at the top of CHANGELOG

## 2026-10-03

### Documentation Refresh

- **README.md / AGENTS.md skill tables refreshed**: filled in skill entries missing from the documents and clarified
  skill directory forms
  - Added `multype2txt` to the Document and Diagram Generation category
  - Added `semble-search` and `vbox-test-env` to the Engineering and Memory category
  - Added the `ci.{lang}.md` row to the language specification file structure in AGENTS.md
  - Extended the Extensions and Plugins chapter of README.md to describe the three origins of skills under `skills/`
    (maintained here, symlinked to external repositories, maintained locally without version control)
- **CHANGELOG.md completed**: added changes from 2026-08-12 through 2026-10-03

### New Test Environment Skill

- **vbox-test-env skill**: a VirtualBox three-machine test environment for cluster/distributed system testing
  - Provides three virtual machines, debian001/002/003, all configured with mutual trust and sudo privileges
  - Location: `skills/vbox-test-env/SKILL.md`
- Commits:
  - Commit: `3bd8047` doc: new skill vbox-test-env
  - Commit: `6f35975` doc: update skill vbox-test-env
  - Commit: `b647229` doc: update skill vbox-test-env

## 2026-09-27

### New Document Conversion Skill

- **multype2txt skill**: converts Office/PDF documents to plain text with local binaries at zero token cost
  - Supports doc/docx/ppt/pptx/xls/xlsx/pdf
  - Location: `skills/multype2txt/SKILL.md`

### Skill Placement Adjustments

- **memrec skill localized**: removed from git tracking and maintained by local/external sources instead
  - The corresponding directory is ignored in `skills/.gitignore`
- Commit: `d8340c9` chore: new skill

## 2026-09-24

### Interaction Rules Enhanced: Specialized Code Retrieval Guidance

- Added three retrieval guidance sections to `agent-template/interaction.rules.md`
  - **CodeGraph**: project knowledge graph, preferred for understanding and locating code
  - **Semble**: semantic code retrieval
  - **zvec-grep**: workspace hybrid retrieval (vector + lexical)
- Commit: `deffe89` doc: add codegraph/semble/zvec-grep guide

## 2026-09-18 ~ 2026-09-26

### Interaction Rule Revisions

- `agent-template/interaction.rules.md` revised multiple times (interaction conventions and tool guidance)
- Commits: `4f277b7`, `2d3e939`, `82efe64`

## 2026-09-16

### Documentation Cleanup

- **AGENTS.md and README.md skill documentation cleanup**: unified skill list categories and descriptions
  - Commit: `ad9d5fe` docs: reorganize AGENTS.md and README skill documentation

### Ignore Rules and External Extensions

- **Ignore rules split**: `skills/.gitignore`, `pi-extensions/.gitignore`, and `dsh-plugins/.gitignore` maintained
  separately
  - Commit: `00fd1c0` chore: ignore
- **memrec externalized**: removed the inline `pi-extensions/memrec.ts` and pulled in the external implementation via
  symbolic link
  - Commit: `e5edf30` chore: remove

## 2026-09-01

### jmh-bench Generalized

- Removed the jbpe project-specific example and switched to a generic execution approach
- Commits: `cd57240`, `777fcd7`, `8f14e59`

## 2026-08-31

### Java Environment Skill and Template

- Streamlined the `java-env` skill documentation and supplemented the content of the `AGENTS.java.md` template
- Commits: `c1abad3`, `5d0ae90`, `12e926e`, `12ef55b`

## 2026-08-28 ~ 2026-08-29

### memrec Skill Documentation Update

- Updated `skills/memrec/SKILL.md`
- Commits: `50c0bf7`, `95556d7`

## 2026-08-27

### Paths and Interaction Rules

- **Hard-coded paths removed**: `cpp-tscancode`, `java-asprof`, `java-check-pmd`, `java-check-spotbugs`, `java-env`, and
  other skills now use environment variables consistently
  - Commit: `fa828a2` doc: remove hard-code path
- Updated `agent-template/interaction.rules.md`
  - Commit: `2818386` doc: update interaction

## 2026-08-26

### Skill Templates

- Removed the plan document and added a Shell skill template
- Commit: `6e3f625` doc: remove plan; add skill template: shell

## 2026-08-20

### pi Extension

- **New pi extension**: `pi-extensions/memrec.ts`
- Commit: `2c6eec9` feat: pi extension, memrec

## 2026-08-12 ~ 2026-08-13

### Kotlin Support Added

- **Language specifications**: `lang-spec/spec.kotlin.md`, `review.kotlin.md`, `ci.kotlin.md`
- **Agent template**: `agent-template/AGENTS.kotlin.md`
- **Skill adaptation**: Kotlin added to `code-review` and `merge-agents-md`
- **Startup scripts**: `bin/common.sh` supports the kotlin language argument
- Commit: `16fea28` feat: add kotlin language spec, review rules and AGENTS template

### pi Quick-Start Scripts

- **New scripts**: `bin/pc` (start pi), `bin/updpiid` (update the pi session ID)
- Commit: `b58b22b` feat: add pi quick-start scripts (pc, updpiid)

### Specification Revisions

- Added entries to `lang-spec/spec.kotlin.md`
- Commit: `746f1a7` doc: update lang spec

## 2026-07-30

### Documentation Refresh

- **README.md refreshed**: reorganized the skill list and added several skill categories
  - Added the `code-part-modification` skill to the core skills
  - Added the `sql-extract` skill: SQL extraction
  - Added the `memrec` skill: AI memory persistence
  - Added the `gdb-heap-analysis` skill to the performance analysis category
  - Added the `rust-flamegraph` skill to the performance analysis category
  - Added the `java-coverage` skill to the Java development tools category
  - Added the `cpp-clang-tidy` skill to the static analysis category
  - Added the `ast-grep-block` skill to the static analysis category
  - Adjusted the skill category structure: static analysis tools and performance analysis tools became independent
    categories

- **AGENTS.md refreshed**: synchronized the skill list

### Skill Completeness Fill-In

This refresh added the following skills that existed but were missing from the documentation:

- `code-part-modification` (added 2026-07-12, missing from documentation)
- `gdb-heap-analysis` (long-standing, missing from documentation)
- `java-coverage` (long-standing, missing from documentation)
- `rust-flamegraph` (long-standing, missing from documentation)
- `sql-extract` (long-standing, missing from documentation)
- `cpp-clang-tidy` (long-standing, missing from documentation)
- `memrec` (long-standing, missing from documentation)
- `ast-grep-block` (long-standing, missing from documentation)

## 2026-07-12

### New Local Code Modification Skill

- **code-part-modification skill**: local code modification with minimal changes
  - Core principles: avoid butterfly effects, support standalone test verification and full related checks
  - Location: `skills/code-part-modification/SKILL.md`

### Commits

- Commit: `cab4697` feat: add code-part-modification skill for minimal code modification

## 2026-07-10

### New Static Analysis Skills

- **cpp-check skill**: Cppcheck static analysis for C/C++ defects, undefined behavior, and security vulnerabilities
  - Location: `skills/cpp-check/SKILL.md`
- **cpp-tscancode skill**: TscanCode (Tencent open source) C/C++ code checker
  - Location: `skills/cpp-tscancode/SKILL.md`
- **shell-check skill**: ShellCheck static analysis for shell script syntax errors and potential defects
  - Location: `skills/shell-check/SKILL.md`

### New Qualitative Assessment Skill

- **qualitative-assessment skill**: summarizes system properties across design, development, operations, and
  non-functional dimensions based on full analysis output
  - Location: `skills/qualitative-assessment/SKILL.md`
- **full-analysis skill enhanced**: added a qualitative assessment stage at the end of the full analysis pipeline
  - Pipeline: design deconstruction -> code review -> duplication detection -> problem detection -> qualitative
    assessment

### code-deconstruct Skill Enhanced

- Added a network estimation workflow to support analysis at the network level

### Script System Improvements

- **No-argument startup logic improved**: refined how the oc/cdbd/clc scripts start without arguments
  - Shows detailed help when there is neither a session ID nor an AGENTS.md
- **Financial quote system classification corrected**: clarified the financial quote system classification in
  qualitative assessment

### Commits

- Commit: `a530ae6` feat: add cpp-check and cpp-tscancode skills
- Commit: `20a4791` feat: add shell-check skill for shell script static analysis
- Commit: `39ccfda` feat(analysis): add qualitative-assessment skill and enhance full-analysis
- Commit: `f3bc9fd` feat: add network estimation workflow to code-deconstruct skill
- Commit: `1001687` fix: improve no-argument startup logic of AI tool scripts
- Commit: `c4adc53` fix(assessment): clarify financial quote system classification

## 2026-07-09

### code-review Skill Modularization

- **Modular framework**: refactored code-review into a layered architecture of a generic review framework plus
  language-specific rules
  - Generic framework: `skills/code-review/SKILL.md` + `docs/code-review-framework.md`
  - Language rules: `lang-spec/spec.{lang}.md` loaded on demand
- **Content deconstruction completed**: finished decomposing code-review skill content into the modular architecture
- **Code example simplification**: trimmed code examples in the code-review skill

### Enterprise-Level Java Code Review Rules

- **Enterprise rules restored**: restored enterprise-level Java code review rules from backup
- **Java thread creation and management standard**: added enterprise-level rules for creating and managing threads
  - Covers thread creation methods, management strategies, and risk prevention

### Security Review Rules Enhanced

- **Clock rollback attack detection**: added clock rollback attack detection rules for C++ and ANSI C
- **Infinite loop review standard**: enhanced infinite loop review, emphasizing the problems of ungraceful exit

### Path Reference Unification

- **Environment variable replaces hard-coded paths**: unified all path references by replacing hard-coded paths with the
  `${AI_SPEC_ROOT}` environment variable

### New Java Static Analysis Skills

- **java-check-spotbugs skill**: SpotBugs static analysis skill with Find Security Bugs and fb-contrib plugin
  integration
  - Detection scope: code defects, security vulnerabilities, performance issues
  - Tool version: SpotBugs 4.7.3 (supports up to Java 17)
  - Location: `skills/java-check-spotbugs/SKILL.md`

- **java-check-pmd skill**: PMD code quality analysis skill
  - Detection scope: coding standards, code smells, complexity analysis, security vulnerabilities
  - Tool version: PMD 6.19.0 (supports Java 25)
  - Location: `skills/java-check-pmd/SKILL.md`

### Tool Verification Results

- **PMD verified**: the tool works and correctly detected issues such as empty catch blocks and unused variables
- **SpotBugs version compatibility**: SpotBugs 4.7.3 does not support Java 25 due to ASM version limits and requires
  Java 17 or earlier
- **Skill documentation updated**: added version compatibility notes and solutions to the SpotBugs skill

### Skill List Updates

- Added the two new skills to the Java development tools section of README.md
- Updated skill descriptions and applicable scenarios

### Commits

- Commit: `a3cfa32` refactor: unify path references using environment variables instead of hard-coded paths
- Commit: `1bcce76` feat: enhance infinite loop review rules, emphasizing ungraceful exit
- Commit: `d733948` refactor: simplify code examples in the code-review skill
- Commit: `0ec5e64` feat: refactor code-review skill to modular framework
- Commit: `069c4ee` feat: add enterprise-level Java code review rules from backup
- Commit: `6cc8b1e` feat: add clock rollback attack detection for C++ and ANSI C
- Commit: `2503f25` feat: complete code-review skill content decomposition to modular architecture
- Commit: `9281533` feat: add Java thread creation and management standard (enterprise requirements)
- Commit: `a193e16` feat: add java-check-spotbugs and java-check-pmd skills

## 2025-07-07

### New Features

- **Shell support added**: language specifications and agent templates for Shell/Bash projects
- **Script system refactored**: symbolic link deployment and environment-variable-driven architecture
- **Architecture optimization**: shared functions centralized in `common.sh`, each script validates the environment
  variable independently

### Technical Improvements

- **Path reference unification**: replaced all hard-coded `/disk2/helly_data/code/markdown/self-ai-spec` paths with the
  `${AI_SPEC_ROOT}` environment variable
- **Script error handling**: fixed friendly messages in the `oc`/`cdbd`/`clc` scripts when there are no arguments and no
  session ID
- **Documentation standards**: separated change history from README.md into CHANGELOG.md
- **Security awareness**: added an AI tool script testing safety reminder to AGENTS.md

### Skill Updates

- **Java coding standard**: refined ForkJoinPool usage rules and added a chapter on task queuing and delay risks
- **AI tool testing reminder**: recorded in memrec to avoid running interactive tool scripts directly during tests

## 2025-07-06

### Major code-review Skill Update

- **Sensitive data review generalized**: sensitive data review is explicitly a mandatory item for all languages (not
  specific to C/C++)
- **Security review expanded**: added the following review points:
  - Sensitive information leakage
  - Sensitive data residue in memory
  - Sensitive field output
  - Secure logging
- **Special check renamed**: special check 6 renamed to "Sensitive Field Output Review (all languages)"
- **Multi-language examples**: provided code examples of sensitive information leakage in Java/Python/JavaScript

### New Language Specifications

- **Shell/Bash specifications**: `spec.shell.md` and `ci.shell.md` language specifications
- **Shell agent template**: `AGENTS.shell.md` agent configuration file

## 2025-07-05

### Script System Refactor

- **Environment-variable driven**: all scripts use the `AI_SPEC_ROOT` environment variable to locate resources
- **Symbolic link support**: scripts can be symlinked to any directory (for example `~/bin/`)
- **Session management**: optimized session ID saving and resume logic
- **Error handling**: improved error messages when the environment variable is missing

### New Skill

- **merge-agents-md**: a general AGENTS.md merge skill supporting multiple programming language templates

## Architecture Evolution

### Path Reference Pattern Evolution

- **Original pattern**: hard-coded absolute paths → inflexible, the repository cannot be moved
- **Current pattern**: the `${AI_SPEC_ROOT}` environment variable → flexible deployment with symbolic link support
- **Example**:

  ```
  old: Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
  new: Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md
  ```

### Script Architecture Optimization

- **Shared functions extracted**: `common.sh` holds the core session management logic
- **Independent validation**: each script validates the `AI_SPEC_ROOT` environment variable independently
- **Friendly error messages**: detailed help is shown when there are no arguments and no session ID

## Technical Notes

### Important Technical Decisions

1. **Path reference standardization**: all resource file references use the `${AI_SPEC_ROOT}` prefix
2. **Mandatory environment variable**: `AI_SPEC_ROOT` is required for scripts to run
3. **Symbolic link first**: deploying to the user bin directory via symbolic links is recommended
4. **Session isolation**: opencode, codebuddy, and claudecode each manage their own session state

### Security Reminders

- **Script testing caution**: avoid running the `oc`, `cdbd`, `clc`, and `qcc` scripts directly during tests
- **Interactive tool risk**: these scripts start interactive AI tools that take over the terminal and are hard to exit
- **Safe testing approach**: prefer `bash -n` syntax checks, or test through environment variables and redirection
