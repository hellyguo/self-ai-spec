---
name: lets-loop
description: "Loop Engineering 循环调度框架：企业Agent落地的第四层工程进化，支持20种循环设计模式、四层工程治理、自主持续改进"
---

# Let's Loop - Loop Engineering 循环调度框架

> 企业Agent落地的第四层工程进化：从提示词工程到循环工程，构建部署后每天都变得更好的系统

**核心洞察**：AI工程范式已从单次提示词演进到持续循环调度——生成→评估→学习→改进→直到输出真正足够好。

## 四层工程进化论

| 层级 | 名称 | 核心 | 关键技术 | 局限性 |
|------|------|------|----------|--------|
| L1 | Prompt Engineering | 说清楚任务 | CoT、Few-shot、结构化模板 | 信息孤岛、无记忆、人肉触发 |
| L2 | Context Engineering | 提供背景信息 | RAG、MCP协议、Message History | 模型手不受控、错误不自愈 |
| L3 | Harness Engineering | 验证正确性 | AGENTS.md、Sensors、Enforcement | 依赖人触发收尾、无跨session记忆 |
| L4 | Loop Engineering ⭐ | 持续迭代改进 | Automations、Worktrees、Skills、Sub-agents、State | — |

嵌套关系：L4 ⊃ L3 ⊃ L2 ⊃ L1

## Loop 六要素

| 要素 | 作用 | 示例 |
|------|------|------|
| Automations | 自动化心跳 | `--cron "0 9 * * *"` / `--trigger "git_push"` |
| Worktrees | 工作树隔离 | `concurrency: 3, isolation: git_worktree` |
| Skills | 技能编码 | 将历史错误提炼为可复用规则 |
| Plugins/Connectors | 插件连接器 | Jira、Slack等MCP集成 |
| Sub-agents | 子Agent制衡 | Maker-Checker分离 |
| State | 外部状态存储 | 迭代计数、错误/成功记忆、模式库 |

## 20种循环设计模式

### 类别1：质量改进

| # | 模式 | 要点 |
|---|------|------|
| 1 | 生成→批判→重写 | generator→critic→generator，until score≥85 |
| 2 | 打分并重试 | max_retries:5, quality_threshold:80, 按criteria评估 |
| 3 | 多批判者 | 多角色critic，consensus_required: 2/3 |

### 类别2：记忆

| # | 模式 | 要点 |
|---|------|------|
| 4 | Reflexion | 失败→分析假设→存储教训→重试，最重要的自我改进 |
| 5 | 错误库 | 错误驱动知识库，任务前precheck |
| 6 | 成功模式 | quality>90且time<threshold时捕获 |

### 类别3：规划

| # | 模式 | 要点 |
|---|------|------|
| 7 | 计划→执行→重新规划 | adaptive, observe→replan if unexpected |
| 8 | 动态工作流 | decision_points条件分支 |

### 类别4：探索

| # | 模式 | 要点 |
|---|------|------|
| 9 | 分支探索 | parallel_branches:3, select_best_by加权评分 |

### 类别5：系统优化

| # | 模式 | 要点 |
|---|------|------|
| 10 | 提示词优化 | evolutionary策略，mutation变体 |
| 11 | 工作流优化（元循环） | 监控latency/cost/quality/success_rate触发优化 |

## 企业级Loop模板

详见 `templates/` 子目录：

- `code-review-loop.yaml` — 代码审查自动化Loop
- `tech-debt-loop.yaml` — 技术债务管理Loop
- `risk-and-budget.yaml` — 风险管理和成本控制
- `industry-adaptation.yaml` — 行业适配（金融/软件/客服）
- `diagnostic-flow.yaml` — 诊断框架：问题在哪一层

## 采纳路径

| 阶段 | 目标 | 命令 |
|------|------|------|
| 1: 夯实L1+L2 | 验证AI能做这件事 | `--level L2 --scenarios "code-review,doc-generation" --goal "85%_accuracy"` |
| 2: 建设L3 | Agent可被信任独立完成 | `--level L3 --harness "agents.md,linter,test_gates" --goal "semi_autonomous"` |
| 3: 试点L4 | 验证无人值守可行性和ROI | `--level L4 --pilot "daily_ci_triage" --budget "50k_tokens" --supervision "high"` |
| 4: 规模化L4 | 扩展到多场景 | `--level L4 --scale "3_scenarios" --automation "full" --budget "500k_tokens"` |

## 核心原则：Build the Loop, Stay the Engineer

两个人可以搭建完全相同的Loop，得到完全相反的结果。一个人用它加速自己深刻理解的工作，另一个人用它逃避理解工作本身。

- ✅ 工程师：用Loop处理理解深刻的重复性工作，保持code walkthroughs，审查重大决策，把Loop当放大器
- ❌ 逃避者：用Loop处理不理解的新领域，停止审查输出，盲目信任决策，把Loop当外包团队

---

**愿景**：`lets-loop` 让Agent从"单次执行工具"进化为"持续改进系统"，从"需要人推动"进化为"自己发现工作"，从"概率性正确"进化为"可验证可靠"。
