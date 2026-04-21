# HTML 报告模板（通用）

> 增量测试完成后，填充数据到以下 HTML 模板即可生成报告。

## 报告输出路径

```
docs/{YYYY-MM-DD}_{seq}_增量单元测试报告.html
docs/{YYYY-MM-DD}_{seq}_增量覆盖率报告.html
```

## 需要填充的动态数据

### 单元测试报告
| 占位符 | 说明 | 数据来源 |
|--------|------|---------|
| `{DATE}` | 报告日期 | 当前日期 |
| `{VERSION}` | 基线版本 | git branch 名 |
| `{DIFF_SIZE}` | diff 大小 | diff.txt 文件大小 |
| `{TEST_FILE_COUNT}` | 测试文件数 | 统计 |
| `{TEST_METHOD_COUNT}` | 测试方法总数 | 统计 |
| `{MODULE_TABLE_ROWS}` | 模块分布表格行 | diff 分析 |
| `{TEST_DETAIL_ROWS}` | 测试用例明细行 | 每个测试文件 |
| `{SCENARIO_TABLES}` | 高优先级测试场景 | 测试代码分析 |

### 覆盖率报告
| 占位符 | 说明 | 数据来源 |
|--------|------|---------|
| `{LINE_COVERAGE}` | 行覆盖率 | JaCoCo 或预估值 |
| `{BRANCH_COVERAGE}` | 分支覆盖率 | JaCoCo 或预估值 |
| `{TOTAL_LINES}` | 新增代码总行数 | diff 分析 |
| `{COVERED_LINES}` | 已覆盖行数 | 计算 |
| `{TOTAL_BRANCHES}` | 总分支数 | 分析 |
| `{COVERED_BRANCHES}` | 已覆盖分支数 | 分析 |
| `{MODULE_COVERAGE_CARDS}` | 模块覆盖率卡片 | 按模块统计 |
| `{FILE_COVERAGE_TABLE}` | 文件覆盖率表格 | 按文件统计 |
| `{BRANCH_DETAIL_TABLES}` | 分支覆盖详情 | 测试代码分析 |

## HTML/CSS 样式要点（已固化）

### 配色方案
- 深色主题: bg=#1a1a2e, card=#0f3460, accent=#4ecca3
- 浅色主题: bg=#f5f7fa, card=#f0f2f5, accent=#16a085
- 覆盖率进度条: 绿(>=80%) / 黄(60-80%) / 红(<60%)

### 组件清单（从已有报告中直接复用）
1. `.header` - 报告头部（标题 + 元数据网格）
2. `.stat-card` - 统计卡片（数字 + 标签）
3. `.gauge-card` - 覆盖率仪表盘（SVG 环形图）
4. `.coverage-bar` - 覆盖率进度条
5. `.module-card` - 模块覆盖率卡片
6. `table` - 数据表格（斑马纹 + 悬停高亮）
7. `.badge` - 变更类型标签
8. `.theme-toggle` - 深浅主题切换按钮

### SVG 环形图计算公式
```
圆周长 = 2 * PI * r = 2 * 3.14159 * 65 = 408.4
stroke-dasharray = 408.4
stroke-dashoffset = 408.4 * (1 - 覆盖率百分比)
```
示例：92.9% → stroke-dashoffset = 408.4 * 0.071 = 29.0

### JavaScript（固定）
```javascript
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    var btn = document.querySelector('.theme-toggle');
    btn.textContent = document.body.classList.contains('light-theme')
        ? '切换深色主题' : '切换浅色主题';
}
```

## 报告结构规范（从 SKILL.md 迁入）

### 单元测试报告结构

报告应包含以下部分：

1. **报告头部**：项目名称、版本、生成时间、diff 基线信息
2. **变更范围分析**：按模块分组的变更文件列表、变更类型统计
3. **测试用例清单**：按模块/类/方法层级展示，每个测试用例包含：
   - 测试方法名和中文描述（@DisplayName）
   - 所属测试类和源文件
   - 测试类型（单元测试/参数化测试/嵌套测试）
   - 覆盖的源方法名
4. **测试统计摘要**：总用例数、通过/失败/跳过、各模块分布
5. **未覆盖项列表及建议**

### 覆盖率报告结构

报告应包含以下部分：

1. **覆盖率总览仪表盘**：行覆盖率/分支覆盖率的进度条 + 百分比
2. **覆盖率目标对比**：目标值 vs 实际值 vs 达标状态
3. **按模块覆盖率明细表**：模块名、行覆盖率、分支覆盖率、达标状态
4. **按变更文件覆盖率明细表**：文件名、新增/变更行数、覆盖行数、行覆盖率、分支覆盖率
5. **分支覆盖详情**：每个被测方法的分支条件与对应测试用例
6. **覆盖率趋势**（如有历史数据）
