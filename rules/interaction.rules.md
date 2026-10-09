# 交互规则

## 约束

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
- 禁止在文档中使用 ASCII Art 画示意图，画图必须使用 mermaid。ASCII Art 只允许在交互过程中进行示意，├── 制图字符，在用于文件夹罗列时，可豁免后在文档中使用。
- 禁止主动使用视觉功能。
- 执行任务中被问别的事，能马上回应则回应，然后继续原任务。
- 搜索 A 时若 B、C、D 不满足，禁止列举 B、C、D。
- 疑问句只回答，不执行，不反问，不提出替代方案。
- 检索优选 codegraph-mcp，次选 ripgrep，兜底 grep
- 本机为 linux，且配备了更高效的工具，倾向使用这些工具

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
