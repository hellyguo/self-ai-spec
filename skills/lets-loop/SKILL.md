---
name: lets-loop
description: "持续循环调度框架：循环调度组合技能的通用框架，支持动态任务编排、技能组合、状态保持和自动恢复"
---

# Let's Loop - 持续循环调度框架

> 循环调度组合技能的通用框架，支持动态任务编排、技能组合、状态保持和自动恢复

## 概述

`lets-loop` 是一个持续循环调度框架，灵感来源于文章中的循环检测概念，但扩展为一个通用的技能调度器。它能够：

1. **循环调度**：持续循环执行技能组合，直到完成目标
2. **动态编排**：根据任务状态动态调整技能组合和执行顺序
3. **状态保持**：在循环之间保持状态，支持中断恢复
4. **技能组合**：将多个技能组合成任务流水线
5. **进度监控**：实时监控任务进度和执行状态

## 核心概念

### 循环单元 (Loop Unit)

单个技能执行的最小单元，包含：

- 技能名称
- 输入参数
- 执行条件
- 输出处理规则
- 超时设置
- 重试策略

### 循环计划 (Loop Plan)

由多个循环单元组成的执行计划：

- 顺序执行：一个接一个执行
- 并行执行：同时执行多个单元
- 条件执行：基于条件选择执行路径
- 循环执行：重复执行直到条件满足

### 循环状态 (Loop State)

在整个循环过程中保持的状态：

- 执行进度
- 中间结果
- 错误信息
- 执行历史

## 工作流程

### 1. 计划制定阶段

```yaml
loop_plan:
  name: "代码质量改进循环"
  description: "持续改进代码质量的循环计划"
  steps:
    - step: "code-review"
      condition: "always"
      params:
        scope: "changed_files"
        language: "auto"
    
    - step: "lets-loop"  # 循环中的循环
      condition: "review_score < 80"
      params:
        sub_plan: "性能优化循环"
    
    - step: "code-refactor"
      condition: "issues_found > 0"
      params:
        priority: "high"
    
    - step: "git-commit"
      condition: "changes_made"
      params:
        message: "chore: 代码质量改进循环"
```

### 2. 循环执行阶段

```text
启动循环 → 执行技能 → 检查结果 → 更新状态 → 决策下一步 → [继续/终止]
```

### 3. 状态管理阶段

- 保存当前状态到 `.loop-state.json`
- 支持中断后从断点恢复
- 记录执行历史和性能指标

## 内置循环模式

### 1. 质量保障循环

```yaml
name: "质量保障循环"
trigger: "git_push"
steps:
  - code-review
  - code-detect-problem
  - java-gen-unittest  # 如果测试覆盖不足
  - merge-agents-md    # 如果配置变更
```

### 2. 性能优化循环

```yaml
name: "性能优化循环"
trigger: "review_found_performance_issue"
steps:
  - lets-loop --mode "复杂度检测"
  - java-asprof        # Java 性能分析
  - jmh-bench         # 基准测试
  - code-refactor     # 重构优化
  - jmh-bench         # 验证优化效果
```

### 3. 重构循环

```yaml
name: "重构循环"
trigger: "code_detected_dup > 50%"
steps:
  - code-detect-dup
  - code-deconstruct
  - requirement-collect
  - code-refactor
  - code-review       # 验证重构结果
```

## 使用方式

### 命令行调用

```bash
# 启动一个循环
/lets-loop --plan quality_assurance

# 执行特定技能组合
/lets-loop --steps "code-review,code-refactor,git-commit"

# 恢复中断的循环
/lets-loop --resume --state-file .loop-state.json

# 监控循环状态
/lets-loop --monitor --interval 30

# 生成循环报告
/lets-loop --report --format html
```

### 自然语言触发

```text
"启动一个持续改进循环"
"循环执行代码审查和重构"
"创建一个性能优化工作流"
"恢复上次中断的任务循环"
"监控当前的循环执行状态"
```

## 技能集成

### 现有技能适配

所有现有技能都可以作为循环单元：

| 技能 | 循环角色 | 触发条件 |
| ------ | ---------- | ---------- |
| `code-review` | 质量检查 | 代码变更、定期执行 |
| `code-refactor` | 改进执行 | 发现问题、计划执行 |
| `code-detect-problem` | 问题诊断 | 质量下降、性能问题 |
| `java-gen-unittest` | 测试增强 | 覆盖不足、新增功能 |
| `long-term-task` | 长任务包装 | 复杂多步骤任务 |

### 新技能组合示例

```yaml
# 完整的开发周期循环
name: "开发周期循环"
steps:
  - step: "requirement-collect"
    when: "new_feature"
  
  - step: "code-deconstruct"
    when: "design_needed"
  
  - step: "long-term-task"
    params:
      task: "实现新功能"
    
  - step: "java-gen-unittest"
    when: "java_project"
    
  - step: "code-review"
    always: true
    
  - step: "merge-agents-md"
    when: "agents_updated"
```

## 状态管理

### 状态文件格式

```json
{
  "loop_id": "quality_loop_20250703",
  "status": "running",
  "current_step": 3,
  "start_time": "2025-07-03T10:00:00Z",
  "elapsed_time": 120,
  "results": [
    {"step": 1, "skill": "code-review", "status": "completed", "score": 85},
    {"step": 2, "skill": "code-detect-problem", "status": "completed", 
  "issues": 3},
    {"step": 3, "skill": "code-refactor", "status": "in_progress"}
  ],
  "next_steps": [4, 5],
  "metrics": {
    "total_steps": 5,
    "completed": 2,
    "failed": 0,
    "success_rate": 100
  }
}
```

### 恢复机制

```bash
# 自动恢复上次状态
if [ -f ".loop-state.json" ]; then
  echo "检测到未完成循环，恢复执行..."
  /lets-loop --resume
else
  echo "启动新循环..."
  /lets-loop --plan default
fi
```

## 监控和报告

### 实时监控

```bash
# 监控循环执行
/lets-loop --monitor

# 输出示例
[10:00] 🔄 循环启动: 质量保障循环
[10:01] ✅ Step 1: code-review 完成 (评分: 85/100)
[10:03] ⚠️  Step 2: code-detect-problem 发现问题: 3个
[10:05] 🔄 Step 3: code-refactor 执行中...
[10:07] 📊 进度: 60% | 成功: 2/5 | 预计完成: 10:15
```

### 报告生成

```markdown
# 循环执行报告

## 循环概况
- 循环ID: quality_loop_20250703
- 状态: 已完成
- 持续时间: 15分钟
- 成功率: 100%

## 执行详情
| 步骤 | 技能 | 状态 | 耗时 | 结果 |
|------|------|------|------|------|

## 指标分析
- 代码质量提升: 85 → 92
- 问题解决: 3/3
- 测试覆盖提升: 65% → 78%

## 建议
1. 继续运行质量保障循环
2. 重点关注性能优化
3. 计划下轮重构循环
```

## 与 long-term-task 的关系

`lets-loop` 是对 `long-term-task` 的扩展和泛化：

| 特性 | long-term-task | lets-loop |
| ------ | ---------------- | ----------- |
| **核心目标** | 完成单个复杂任务 | 持续循环执行多个任务 |
| **执行模式** | 线性执行 | 循环调度 |
| **状态管理** | 简单进度跟踪 | 完整状态保持和恢复 |
| **技能组合** | 有限组合 | 灵活动态组合 |
| **适用场景** | 一次性长任务 | 持续改进、监控、自动化 |

## 扩展性

### 自定义循环模式

用户可以定义自己的循环模式：

```yaml
# 自定义循环定义
name: "团队代码规范循环"
description: "确保团队代码规范的持续检查"
schedule: "daily"  # 每日执行
steps:
  - step: "code-review"
    params:
      language: "java"
      strictness: "high"
  
  - step: "notify-team"
    condition: "issues_found > 0"
    params:
      channel: "team-slack"
      template: "代码规范问题提醒"
```

### 条件表达式系统

支持复杂的条件判断：

```yaml
condition: |
  (review_score < 80) 
  OR (performance_issues > 3) 
  OR (security_issues > 0)
  OR (changed_lines > 500)
```

### 事件驱动执行

```yaml
triggers:
  - event: "git_push"
    branch: "main"
    actions: ["quality_assurance_loop"]
  
  - event: "pr_created"
    actions: ["code-review", "test_coverage_check"]
  
  - event: "deployment"
    actions: ["smoke_test_loop"]
```

## 最佳实践

### 1. 循环设计原则

- **单一职责**：每个循环专注一个目标
- **适度长度**：循环不应过长，建议5-10个步骤
- **可中断性**：设计可安全中断的检查点
- **结果验证**：每个循环都应验证执行效果

### 2. 错误处理

```yaml
error_handling:
  retry_policy:
    max_retries: 3
    backoff: "exponential"
  
  fallback_actions:
    - action: "log_error"
    - action: "notify_admin"
    - action: "skip_to_next"
  
  recovery_points:
    - after_step: 2
    - after_step: 4
```

### 3. 性能考虑

- 定期清理旧状态文件
- 限制并行循环数量
- 监控循环执行时间
- 设置合理的超时值

## 示例用例

### 用例1：持续集成质量门禁

```bash
# GitHub Actions 集成
name: CI Quality Gate
on: [push]
jobs:
  quality-loop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Quality Loop
        run: |
          /lets-loop --plan ci_quality_gate
          if [ $? -ne 0 ]; then
            echo "质量门禁未通过"
            exit 1
          fi
```

### 用例2：团队代码审查自动化

```yaml
# 团队自动化审查循环
name: "团队代码审查自动化"
schedule: "weekly"
steps:
  - step: "collect_prs"
    params:
      team: "backend-team"
      timeframe: "7d"
  
  - step: "code-review"
    for_each: "pr"
    params:
      pr: "{{current_pr}}"
  
  - step: "generate_report"
    params:
      format: "team_dashboard"
  
  - step: "send_summary"
    params:
      recipients: "team-leads"
```

### 用例3：技术债务管理

```yaml
name: "技术债务管理循环"
trigger: "monthly"
steps:
  - step: "code-detect-problem"
    params:
      depth: "deep"
  
  - step: "prioritize_issues"
    params:
      criteria: ["impact", "effort", "risk"]
  
  - step: "create_tech_debt_tickets"
    params:
      system: "jira"
      priority: "based_on_analysis"
  
  - step: "track_progress"
    params:
      baseline: "previous_cycle"
```

---

**设计理念**：将文章中的"循环检测"概念抽象为通用的"循环调度"框架，使得各种技能能够被有序、持续、智能地组合和执行，形成一个自适应的改进系统。
