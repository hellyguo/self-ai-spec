# ShellCheck分析报告：{项目名称}

## 项目概述

- **分析时间**：{时间戳}
- **Shell方言**：{bash/sh/dash/ksh}
- **分析范围**：{文件数}个脚本文件

## 问题统计

| 级别 | 数量 |
|------|------|
| error | {error_count} |
| warning | {warning_count} |
| info | {info_count} |
| style | {style_count} |
| **合计** | **{total_count}** |

## 问题详情

### 错误（error）

| 文件 | 行号 | SC编号 | 描述 | 修复建议 |
|------|------|--------|------|----------|
| {file} | {line} | {code} | {message} | {fix} |

### 警告（warning）

| 文件 | 行号 | SC编号 | 描述 | 修复建议 |
|------|------|--------|------|----------|
| {file} | {line} | {code} | {message} | {fix} |

### 信息（info）

| 文件 | 行号 | SC编号 | 描述 | 修复建议 |
|------|------|--------|------|----------|
| {file} | {line} | {code} | {message} | {fix} |

### 风格（style）

| 文件 | 行号 | SC编号 | 描述 | 修复建议 |
|------|------|--------|------|----------|
| {file} | {line} | {code} | {message} | {fix} |

## 高频问题Top5

| 排名 | SC编号 | 出现次数 | 描述 |
|------|--------|----------|------|
| 1 | {code} | {count} | {description} |
| 2 | {code} | {count} | {description} |
| 3 | {code} | {count} | {description} |
| 4 | {code} | {count} | {description} |
| 5 | {code} | {count} | {description} |

## 改进建议

### 必须修正（error级别）

[列出所有error级别问题及修复方案]

### 建议修正（warning级别）

[列出所有warning级别问题及修复方案]

### 可选改进（info/style级别）

[列出所有info/style级别问题及优化建议]

## 总结

[整体评价、关键风险、修复优先级建议]

---

**分析工具**：ShellCheck {version}
**报告生成时间**：{时间戳}
