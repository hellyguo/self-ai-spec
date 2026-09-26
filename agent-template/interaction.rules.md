# 交互规则

- 所有交互均使用简体中文，所有输出都不得带 Emoji，以显正式
- 每次交互的第一步，都是先检索 memrec-mcp，并在输出后随时、持续使用 memrec-mcp 记录核心观点、关键节点、重要内容(plan、design等)
- 每次产出最后一步，确认是否需要更新 MEMORY.md + 记录 memrec-mcp；如产出文件后，均执行 git 提交
- git 仅以当前 `user.name` 提交，绝不推送到远端
- git 提交均遵循约定式提交规范（Conventional Commits）执行
- 版本管理忽略 MEMORY.md，写入 .gitignore，不提交到 git
- 编排计划或设计时，如过长(>2000行)，拆分为多份文档
- 计划或设计中，不要穿插代码，代码不能成为设计或计划的主要内容，仅需要部分伪代码将逻辑讲清楚
- 编码时，合理生成注释。文件头/类头/函数头/方法头，应有描述和注意事项；重要算法，重要参数，重要设计，应有解释和说明
- 修改时，不删除原有注释，但如已经语义变化等必要情况，需要变更或删除，重新补充注释，参见上一条
- 禁止在编码使用stdout/stderr，测试代码也尽可能使用日志输出
- 本机为 linux，且配备了更高效的工具，倾向使用这些工具

    - fd[find]
    - rg[grep]
    - sd[sed]
    - eza[ls]
    - plocate[类似Windows下的everything]
    - f2[批量重命名]
    - rrn[同f2,弱化]
    - ntimes[重复执行，ntimes n -- cmd(串行执行) / ntimes n -p -- cmd(并行执行)]
    - zg/codegraph/semble[特化的代码检索]

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->


<!-- SEMBLE_START -->
## Semble Code Search

A `semble` MCP server is available with two tools:
- `mcp__semble__search` — search the codebase with a natural-language or code query.
- `mcp__semble__find_related` — find code similar to a specific file and line.

Use `mcp__semble__search` to find where something is implemented — instead of using Grep or Glob to discover files. After semble returns the file and line, navigate there directly and read that file. Do not grep for the same content again.

Pass `content="docs"` to the MCP search tool for documentation and prose, `content="config"` for config files, or `content="all"` for everything. On the CLI, use `--content docs`, `--content config`, or `--content all` instead.

For CLI fallback or sub-agents without MCP access, use:

```bash
semble search "authentication flow" ./my-project --max-snippet-lines 10
semble search "deployment guide" ./my-project --content docs
semble search "database host port" ./my-project --content config
semble find-related src/auth.py 42 ./my-project
semble search "save model to disk" ./my-project --top-k 10
```

The index is built on first run and cached automatically. If `semble` is not on `$PATH`, use `uvx --from "semble[mcp]==0.6.0" semble`.

### Workflow

1. Call `mcp__semble__search` with a query describing what the code does or its name. The tool returns results with 10 lines of context each (function/class signature + first body lines, enough to confirm the location).
2. Navigate directly to the top result's file and line. Read only the function or class at that location.
3. Make the edit. Do not re-search or grep for the same content.
4. Set the MCP search tool's `content` field to `docs`, `config`, or `all` when searching beyond code.
5. Optionally use `mcp__semble__find_related` with `file_path`, `line`, and the same `content` selection to discover similar code elsewhere.
6. Use Grep only when you need every occurrence of a literal string across the whole repo (e.g., all callers of a renamed function).
<!-- SEMBLE_END -->

<!-- ZVEC_GREP_START -->
## zvec-grep

Choose the evidence source before the retrieval mode.

### Workspace evidence
- Use the current workspace as the evidence source when the user asks about local material, prior context establishes it as relevant, or the question concerns how the current project works—even if the workspace is not mentioned explicitly.
- A workspace may contain any mix of code, documents, configuration, and data.
- Do not use workspace retrieval for unrelated open-world questions, current external facts, or web content that does not depend on local evidence.

### Retrieval routing
- When an exact word, phrase, name, date, identifier, filename, path, configuration key, error message, source fragment, literal, or regex is known and locating its occurrences is sufficient, use `zvec_grep_zvec_grep_rg` when it is listed by the current host; otherwise native Grep or `rg`.
- Use `zvec_grep_zvec_grep_search` when wording or location is unknown, or when the answer requires semantic, conceptual, fuzzy, or paraphrase discovery; relationships, chronology, causality, architecture, or data or control flow; or comparison or synthesis across files, sections, or documents.
- For a mixed task with exact anchors that still requires relationships or cross-file synthesis, call `zvec_grep_zvec_grep_search` with the concept and anchors, then use `zvec_grep_zvec_grep_rg` when it is listed by the current host; otherwise native Grep or `rg` for focused follow-up.
- When no sufficient exact anchor is available and the user asks whether conceptually related material exists locally, make at most one focused `zvec_grep_zvec_grep_search` probe using the question plus distinctive names, dates, or terms. This probe does not apply to exact quotations, configuration keys, filenames, regexes, or exhaustive occurrence requests. Continue only when results are relevant; otherwise stop and report that the indexed workspace did not establish the answer.
- Before broad file reads or delegating workspace discovery, use the appropriate search route. Do not delegate solely to locate material, and stop when the evidence is sufficient.

### Search evidence
- Search results include bounded source snippets. Treat a sufficient snippet as already-read evidence, and read a cited file only when a required detail falls outside the snippet.

### Freshness and index lifecycle
- Pass a daemon-visible absolute `root` on every zvec-grep workspace call.
- Read `freshness` and `background_refresh` from search results without a status preflight.
- When results are `served_from_current_index`, use them when sufficient instead of waiting for the background refresh.
- If the index is missing but exact or regex lookup can answer the task, use `zvec_grep_zvec_grep_rg` when it is listed by the current host; otherwise native Grep or `rg`.
- Creating, rebuilding, or dropping a persistent index requires an explicit user request or authorization; never do so silently.

<!-- ZVEC_GREP_END -->
