# SpotBugs分析报告：{项目名称}

## 项目概述

- **分析时间**：{时间戳}
- **Java版本**：{java_version}
- **分析范围**：{analyzed_paths}
- **检测器**：SpotBugs + {plugins}

## 问题统计

| 优先级 | 数量 |
|--------|------|
| 高危（High） | {high_count} |
| 中危（Medium） | {medium_count} |
| 低危（Low） | {low_count} |
| **合计** | **{total_count}** |

## 安全漏洞

| 检测器 | 漏洞类型 | 文件 | 行号 | 严重等级 |
|--------|----------|------|------|----------|
| {detector} | {vuln_type} | {file} | {line} | {severity} |

## 代码缺陷

| 类别 | Pattern | 文件 | 行号 | 描述 |
|------|---------|------|------|------|
| {category} | {pattern} | {file} | {line} | {message} |

## 高频问题Top5

| 排名 | Pattern | 出现次数 | 描述 |
|------|---------|----------|------|
| 1 | {pattern} | {count} | {description} |
| 2 | {pattern} | {count} | {description} |
| 3 | {pattern} | {count} | {description} |
| 4 | {pattern} | {count} | {description} |
| 5 | {pattern} | {count} | {description} |

## 改进建议

### 必须修正（高危）

[列出所有高危问题及修复方案]

### 建议修正（中危）

[列出所有中危问题及修复方案]

### 可选改进（低危）

[列出所有低危问题及优化建议]

## 总结

[整体评价、关键风险、修复优先级建议]

---

**分析工具**：SpotBugs {spotbugs_version} + Find Security Bugs + fb-contrib
**报告生成时间**：{时间戳}
