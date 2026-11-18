# 交互规则

## 约束

- 所有LLM交互均使用简体中文，所有LLM输出都不得带 Emoji，以显正式；正式文档均以中文输出，除非明确要求英文文档；git提交应使用英文，必要时添加中文。
- 每次交互的第一步，都是先检索 memrec-mcp，并在输出后随时、持续使用 memrec-mcp 记录核心观点、关键节点、重要内容(plan、design等)
- 每次产出最后一步，确认是否需要更新 MEMORY.md + 记录 memrec-mcp；如产出文件后，均执行 git 提交
- git 仅以当前 `user.name` 提交，绝不推送到远端
- git 提交均遵循约定式提交规范（Conventional Commits）执行
- 版本管理忽略 MEMORY.md，写入 .gitignore，不提交到 git
- 编排计划或设计时，如过长(>2000行)，拆分为多份文档
- 计划或设计中，不要穿插代码，代码不能成为设计或计划的主要内容，仅需要部分伪代码将逻辑讲清楚
- 编码时，合理生成注释。文件头/类头/函数头/方法头，应有描述和注意事项；重要算法，重要参数，重要设计，应有解释和说明
- 编码时，不允许使用 FQN 风格。FQN 只有在存在冲突时，对后引入的冲突方使用。
- 编码时，从行首算起，等效 Tab 长度达到 6 个 Tab（即嵌套层级过深）时，该处代码必须优化或重构，不允许继续加深嵌套。
- 修改时，不删除原有注释，但如已经语义变化等必要情况，需要变更或删除，重新补充注释，参见上一条
- 既有存在的单元测试等测试，不能删除或绕行。如果改动未涉及，可忽略；如果改动直接影响，需修复。
- 禁止使用‘夹具（Fixture）’一词。按实际情况替换为：测试数据、基准值、模拟对象（Mock/Stub）、初始化环境。
- 禁止在编码使用stdout/stderr，测试代码也尽可能使用日志输出
- 禁止在文档中使用 ASCII Art 画示意图，画图必须使用 mermaid。ASCII Art 只允许在交互过程中进行示意，├── 制图字符，在用于文件夹罗列时，可豁免后在文档中使用。
- markdown 按逻辑成行：一个段落、一个列表项、一个引用块写成一个逻辑行，既不按 80/120 列宽折行，也不按句号逐句拆行；同一块内出现第二行连续文本即为违规（空行分隔的独立段落除外）。中英文同口径，英文不因单词边界折行。代码块与表格保持原样，不重排、不折断；表格前保留空行。强制换行只允许用于签名/元数据区，用列表或行尾两个空格，正文段落禁止。不以 markdownlint 等按行宽计算的检查验收，唯一检查为 `bin/check-md-wrap.sh`（判据：同块连续文本行）。
- 禁止主动使用视觉功能。
- 编排TODO时，主动写入 ./docs/todo/<yyyymmdd>-todo-<seq%000>-<subject>.md；并在TODO清空时，将文件改名放入 ./docs/done/<yyyymmdd>-done-<seq%000>-<subject>.md
- 执行任务中被问别的事，能马上回应则回应，然后继续原任务。
- 搜索 A 时若 B、C、D 不满足，禁止列举 B、C、D。
- 检索优选 codegraph-mcp，次选 ripgrep，兜底 grep
- 本机为 linux，且配备了更高效的工具，倾向使用这些工具
- 不允许访问 ~/.ssh 文件夹

    - fd[find]
    - rg[grep]
    - sd[sed]
    - eza[ls]
    - plocate[类似Windows下的everything]
    - f2[批量重命名]
    - rrn[同f2,弱化]
    - ntimes[重复执行，ntimes n -- cmd(串行执行) / ntimes n -p -- cmd(并行执行)]
    - codegraph/semble/zg[特化的代码检索]

## CodeGraph

1. 如果不存在，`.codegraph/`，主动创建 `.codegraph/`
2. 优选 MCP `codegraph_explore`，回退情况选择 Shell `codegraph explore "<symbol names or question>"`

