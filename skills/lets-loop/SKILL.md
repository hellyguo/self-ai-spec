---
name: lets-loop
description: "Loop Engineering 循环调度框架：企业Agent落地的第四层工程进化，支持20种循环设计模式、四层工程治理、自主持续改进"
---

# Let's Loop - Loop Engineering 循环调度框架

> **企业Agent落地的第四层工程进化：从提示词工程到循环工程，构建部署后每天都变得更好的系统**

**核心洞察**：AI工程的范式已从单次提示词，演进到持续循环调度。2026年，生产环境中最强大的AI系统不再是单次模型调用，而是循环：
生成 → 评估 → 学习 → 改进 → 一遍又一遍 → 直到输出真正足够好

## 四层工程进化论

`lets-loop` 代表了 **Loop Engineering（第四层工程）**，以下是完整的四层进化路径：

### L1: Prompt Engineering（提示词工程）

**核心**：怎么说清楚任务

- 优化提示词措辞、角色设定、输出格式
- 技术：Chain-of-Thought、Few-shot、结构化模板
- **局限性**：信息孤岛、无记忆、人肉触发

### L2: Context Engineering（上下文工程）

**核心**：提供什么背景信息

- 设计最优token集的信息策略
- 技术：RAG、MCP协议、Message History管理
- **局限性**：模型的手不受控、错误不会自愈

### L3: Harness Engineering（约束工程）

**核心**：如何验证正确性

- 构建让错误结构性不可重犯的执行环境
- 技术：AGENTS.md规则、Sensors感知、Enforcement约束、Observability
- **局限性**：仍然依赖人触发和收尾、无跨session记忆

### L4: Loop Engineering（循环工程） ⭐ **本技能**

**核心**：如何持续迭代改进

- 设计让Agent自己发现工作、自己推进、自己改进的循环
- 技术：Automations、Worktrees、Skills、Sub-agents、State、Plugins
- **价值**：无人值守运行、跨session连续性、知识复利

**嵌套关系**：Loop Engineering 包含 Harness Engineering，Harness Engineering 包含
Context Engineering，Context Engineering 包含 Prompt Engineering。

## Loop 的六个构成要素

基于Google Chrome团队Addy Osmani和Anthropic Claude Code负责人Boris Cherny的分析，每个生产级Loop需要六个原语：

### 1. Automations（自动化心跳）

```bash
# 定时触发
/lets-loop --cron "0 9 * * *" --plan daily_quality_check

# 事件触发  
/lets-loop --trigger "git_push" --branch main --plan ci_gate
```

### 2. Worktrees（工作树隔离）

```yaml
loop_config:
  concurrency: 3
  isolation: git_worktree
  branches:
    - feature/loop-1
    - feature/loop-2  
    - feature/loop-3
```

### 3. Skills（技能编码）

```markdown
---
name: java-performance-patterns
description: "Java性能优化模式，基于历史错误提炼"
---
# 不这样做
- 避免循环内查询（N+1问题）
- 禁止O(n²)嵌套循环
- 不要在线性查找中使用ArrayList

# 要这样做  
- 使用批量查询 + 预加载
- 改用Set/Map提高查找效率
- 使用stream并行处理
```

### 4. Plugins / Connectors（插件连接器）

```yaml
plugins:
  - name: jira-integration
    mcp_server: "jira-mcp"
    capabilities: ["read_issues", "update_status", "create_ticket"]
  
  - name: slack-notify
    mcp_server: "slack-mcp"  
    capabilities: ["send_message", "create_channel"]
```

### 5. Sub-agents（子Agent制衡）

```yaml
# Maker-Checker分离：写的人和查的人分开
sub_agents:
  - role: "builder"
    skill: "code-refactor"
    model: "gpt-4"
  
  - role: "reviewer"  
    skill: "code-review"
    model: "claude-3.5"
    authority: "approval_required"
```

### 6. State（外部状态存储）

```json
{
  "loop_type": "reflexion",
  "iteration": 15,
  "memory": {
    "errors": ["循环内查询导致性能下降", "缺少边界检查"],
    "successes": ["批量查询提升性能300%", "缓存策略减少DB调用80%"],
    "patterns": ["N+1问题 → 批量查询", "重复线性扫描 → Set查找"]
  }
}
```

## 20种循环设计模式

基于《每位AI工程师都应该了解的20种循环设计模式》的分类实现：

### 类别1：质量改进循环

#### 1. 生成 → 批判 → 重写

```yaml
pattern: "generate_critique_rewrite"
steps:
  - agent: "generator"
    skill: "code-refactor"
    output_as: "draft"
  
  - agent: "critic"  
    skill: "code-review"
    critique: "draft"
    output_as: "feedback"
  
  - agent: "generator"
    skill: "code-refactor"  
    input: "draft + feedback"
    until: "feedback.score >= 85"
```

#### 2. 打分并重试循环

```yaml
pattern: "score_retry"
max_retries: 5
quality_threshold: 80
steps:
  - generate_output
  - evaluate:
      criteria: ["correctness", "performance", "security"]
  - if score < threshold:
      - retry_with: "improved_prompt"
```

#### 3. 多批判者循环

```yaml
pattern: "multi_critic"
critics:
  - role: "security_expert"
    skill: "security-review"
  - role: "performance_expert"
    skill: "code-detect-problem"  
  - role: "architecture_expert"
    skill: "code-deconstruct"
consensus_required: 2/3
```

### 类别2：记忆循环

#### 4. Reflexion循环（最重要的自我改进）

```yaml
pattern: "reflexion"
memory_store: ".loop-memory.json"
steps:
  - attempt_task
  - if failed:
      - analyze_failure:
          questions: ["我假设了什么？", "假设为什么错？", "下次有什么不同？"]
      - store_lesson: "lesson.md"
      - retry_with: "lesson.md"
```

#### 5. 错误库循环

```bash
# 错误驱动的知识库
/lets-loop --pattern error_library --scope "java_n+1_queries"

# 处理新任务前先检查错误库
/lets-loop --task "optimize_query" --precheck "error_library"
```

#### 6. 成功模式循环

```yaml
pattern: "success_patterns"
capture_when: "quality_score > 90 AND execution_time < threshold"
store_as: "success_patterns/{{date}}/{{task_type}}.md"
```

### 类别3：规划循环

#### 7. 计划 → 执行 → 重新规划

```yaml
pattern: "plan_execute_replan"
adaptive: true
steps:
  - plan: "decompose_goal"
  - execute_step: 1
  - observe_results
  - if results_unexpected:
      - replan: "adjust_strategy"
  - continue_until: "goal_achieved"
```

#### 8. 动态工作流循环

```yaml
pattern: "dynamic_workflow"
decision_points:
  - after: "code-review"
    if: "security_issues > 0"
    then: "run security_audit"
    else: "continue_to_refactor"
```

### 类别4：探索循环  

#### 9. 分支探索循环

```yaml
pattern: "branch_exploration"
parallel_branches: 3
approaches: ["conservative", "aggressive", "creative"]
select_best_by: "quality_score * 0.6 + performance_score * 0.4"
```

### 类别5：系统优化循环

#### 10. 提示词优化循环

```yaml
pattern: "prompt_optimization"
test_set: "validation_cases.json"
target_score: 90
optimization_strategy: "evolutionary"
mutations:
  - add_few_shot_examples
  - rephrase_instructions
  - adjust_temperature
```

#### 11. 工作流优化循环（元循环）

```yaml
pattern: "workflow_optimization"
monitor_metrics: ["latency", "cost", "quality", "success_rate"]
optimization_triggers:
  - if: "latency > 5000ms"
    action: "parallelize_slow_steps"
  - if: "cost > budget"
    action: "replace_with_cheaper_model"
  - if: "quality < threshold"
    action: "add_additional_reviewer"
```

## 企业级Loop实现

### 代码审查自动化Loop

```yaml
name: "code_review_automation_loop"
level: "L4"
automation: "pr_created"
worktrees: 2

sub_agents:
  - builder:
      skill: "code-refactor"
      model: "claude-code"
    
  - reviewer:
      skill: "code-review"
      model: "gpt-4o"
      checkpoints: ["security", "performance", "maintainability"]
    
  - tester:
      skill: "java-gen-unittest"
      model: "claude-3.5"
      coverage_target: 80

state_management:
  memory: "errors.json"
  progress: "review_progress.md"
  patterns: "success_patterns/"

quality_gates:
  - test_coverage >= 80
  - security_issues == 0
  - performance_score >= 70
  - reviewer_consensus >= 2/3

cost_control:
  max_tokens_per_pr: 50000
  max_iterations: 10
  budget_alert_threshold: 0.8
```

### 技术债务管理Loop

```yaml
name: "tech_debt_management_loop"
schedule: "weekly"
trigger: "sunday_02:00"

phases:
  - detection:
      skills: ["code-detect-problem", "code-detect-dup"]
      depth: "deep"
    
  - prioritization:
      criteria: ["impact", "effort", "risk", "frequency"]
      matrix: "impact_vs_effort"
    
  - planning:
      skills: ["requirement-collect", "code-deconstruct"]
      output: "refactoring_plan.md"
    
  - execution:
      concurrency: 3
      isolation: "git_worktree"
      skills: ["code-refactor", "java-gen-unittest"]
    
  - validation:
      skills: ["code-review", "jmh-bench"]
      gates: ["tests_pass", "performance_improved", "no_regressions"]

reporting:
  format: "executive_dashboard"
  metrics: ["debt_reduction", "quality_improvement", "roi"]
  recipients: ["tech_leads", "engineering_manager"]
```

## 风险管理和成本控制

### Loop特有的风险

```yaml
risk_management:
  
  # 风险1：成本可预测性下降
  cost_controls:
    max_tokens_per_run: 100000
    max_sub_agents: 5
    budget_alerts:
      - at: "50%" 
        action: "notify"
      - at: "80%"
        action: "pause_non_critical"
      - at: "95%"
        action: "stop_all"
  
  # 风险2：可靠性的新风险面
  reliability_guards:
    - deadlock_detection:
        timeout: "30m"
        action: "kill_and_restart"
    
    - state_corruption:
        detection: "checksum_validation"
        recovery: "rollback_to_last_valid"
    
    - triage_errors:
        fallback: "human_review_queue"
        escalation: "senior_engineer"
  
  # 风险3：理解力负债
  comprehension_preservation:
    - mandatory_code_walkthroughs: "weekly"
    - architecture_documentation: "loop_generated_code.md"
    - knowledge_transfer: "pair_review_sessions"
```

### Token预算策略

```yaml
budget_strategies:
  
  # 策略1：渐进式预算（推荐新手）
  progressive:
    phase_1: "100k tokens/month"
    phase_2: "500k tokens/month"  
    phase_3: "unlimited_with_approval"
  
  # 策略2：按ROI分配
  roi_based:
    allocation_logic: "expected_savings * 0.3"
    roi_threshold: "2.0"  # ROI必须大于2
    tracking: "actual_vs_expected_roi"
  
  # 策略3：按优先级分配  
  priority_based:
    critical: "unlimited"
    high: "500k/month"
    medium: "100k/month"
    low: "10k/month"
```

## 采纳路径：企业四步走

### 阶段1：夯实L1+L2

```bash
# 验证"AI能不能做这件事"
/lets-loop --level L2 --scenarios "code-review,doc-generation" --goal "85%_accuracy"
```

### 阶段2：建设L3

```bash
# 让Agent能被信任独立完成任务
/lets-loop --level L3 --harness "agents.md,linter,test_gates" --goal "semi_autonomous"
```

### 阶段3：试点L4

```bash
# 验证无人值守运行的可行性和ROI
/lets-loop --level L4 --pilot "daily_ci_triage" --budget "50k_tokens" 
--supervision "high"
```

### 阶段4：规模化L4

```bash
# 扩展Loop到多个场景
/lets-loop --level L4 --scale "3_scenarios" --automation "full" --budget "500k_tokens"
```

## 行业适配模板

### 金融行业（合规优先）

```yaml
industry: "finance"
constraints: ["zero_error", "audit_trail", "regulatory_compliance"]
loop_config:
  focus_layers: ["L3", "L4_auxiliary"]
  critical_components:
    - "observability_pipeline"
    - "compliance_checker"
    - "maker_checker_separation"
  forbidden_patterns: ["fully_autonomous_decision", "unattended_trading"]
```

### 软件工程（原生场景）

```yaml
industry: "software_engineering"
constraints: ["code_quality", "test_coverage", "performance"]
loop_config:
  focus_layers: ["L3", "L4_full"]
  patterns: ["generate_critique_rewrite", "reflexion", "branch_exploration"]
  integration_points:
    - "ci_cd_pipeline"
    - "code_review_platform"
    - "project_management"
```

### 客户服务（体验优先）

```yaml
industry: "customer_service"
constraints: ["brand_voice", "escalation_logic", "customer_satisfaction"]
loop_config:
  focus_layers: ["L2", "L3_light"]
  patterns: ["multi_critic", "dynamic_workflow"]
  human_in_loop: "always_available"
```

## 诊断框架：问题在哪一层？

当Loop出问题时，先判断故障在哪一层：

```yaml
diagnostic_flow:
  
  # 症状：输出质量不稳定
  if quality_variance > 30%:
    check: "L1_prompt_clarity"
    fix: "improve_prompt_template"
  
  # 症状：重复犯同样的错  
  if same_error_recurring:
    check: "L2_context_rot"
    fix: "refresh_rag_pipeline"
  
  # 症状：业务规则被违反
  if business_rules_violated:
    check: "L3_harness_gaps"
    fix: "add_ci_check"
  
  # 症状：成本失控
  if cost_exceeds_budget:
    check: "L4_loop_configuration"
    fix: "add_token_limits"
```

## 核心原则：Build the Loop, Stay the Engineer

**最终警告**：两个人可以搭建完全相同的Loop，得到完全相反的结果。一个人用它加速自己深刻理解的工作，另一个人用它逃避理解工作本身。Loop不知道区别，你知道。

### 工程师vs逃避者检查表

```markdown
✅ 工程师的使用方式：
- 用Loop处理理解深刻的重复性工作
- 保持定期code walkthroughs
- 审查Loop的重大决策
- 把Loop当作放大器，不是替代品

❌ 逃避者的使用方式：
- 用Loop处理不理解的新领域
- 停止审查Loop输出
- 盲目信任Loop决策
- 把Loop当作外包团队
```

---

**愿景**：`lets-loop` 不只是技能调度框架，更是企业AI工程的第四层进化实现。它让Agent从"单次执行工具"进化为"持续改进系统"，从"需要人推动"进化为"自己发现工作"，从"概率性正确"进化为"可验证可靠"。

**设计理念**：集成Loop Engineering思想、20种循环模式、四层工程治理，构建部署后每天都变得更好的AI系统。
