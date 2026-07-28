# ast-grep-block 报告字段说明与统计命令

## 1. 文本输出格式

`run.sh` 默认（不带 `--json`）输出：

```
=== ast-grep 扫描报告 ===
扫描路径: /abs/path/to/project
高级(high): 12 条
中级(medium): 5 条
低级(low): 2 条

--- HIGH 命中明细 ---
src/dao/UserDao.java:42:13:empty-catch-block: catch (Exception e) {}
src/util/Crypto.java:108:25:hardcoded-secret: private String key = "sk-12345";
...

--- MEDIUM 命中明细 ---
src/service/Foo.java:50:9:system-out-print: System.out.println("debug");
...

--- LOW 命中明细（仅提示） ---
src/util/Util.java:15:5:unnecessary-import: import java.util.*;
...
```

**行格式**：`<相对路径>:<行号>:<列号>:<规则ID>: <命中代码行>`

字段说明：

| 字段 | 含义 | 备注 |
|------|------|------|
| 相对路径 | 相对于 `--path` 参数的路径 | 容易跳转 |
| 行号 | 命中起始行（1-based） | 直接 `vim +N file` |
| 列号 | 命中起始列（1-based） | 用于 IDE 定位 |
| 规则 ID | 对应 `rules/<lang>/<level>/<range>/<id>.yml` | 全局唯一 |
| 命中代码行 | 命中节点的第一行代码（折叠空白） | 多行命中仅显示首行 |

## 2. JSON 输出字段

`run.sh --json` 输出 JSON 数组，每个元素是一条命中：

```json
[
  {
    "file": "src/dao/UserDao.java",
    "lines": "catch (Exception e) {}",
    "text": "catch (Exception e) {}",
    "range": {
      "byteOffset": 1234,
      "start": { "line": 41, "column": 12 },
      "end":   { "line": 42, "column": 25 }
    },
    "language": "Java",
    "ruleId": "empty-catch-block",
    "level": "high"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | string | 命中文件**绝对路径** |
| `lines` | string | 命中代码原文（首行） |
| `text` | string | AST 节点完整文本（可能多行） |
| `range.byteOffset` | int | 文件内字节偏移 |
| `range.start.line` | int | 起始行（**0-based**，注意） |
| `range.start.column` | int | 起始列（0-based） |
| `range.end.line` | int | 结束行（0-based） |
| `range.end.column` | int | 结束列（0-based） |
| `language` | string | ast-grep 语言名（Java/CPP/C） |
| `ruleId` | string | 规则 ID |
| `level` | string | 级别（high/medium/low），由 run.sh 注入 |

> ⚠️ **行号偏移陷阱**：JSON 中 `range.start.line` 是 **0-based**，文本输出与 IDE 跳转是 **1-based**，转换：`line + 1`。

## 3. 常用 jq 统计命令

### 3a. 各级别命中数

```bash
jq -r '
    "high:   \([.[] | select(.level=="high")]   | length)",
    "medium: \([.[] | select(.level=="medium")] | length)",
    "low:    \([.[] | select(.level=="low")]    | length)"
' report.json
```

### 3b. 规则命中 Top N

```bash
jq -r '.ruleId' report.json | sort | uniq -c | sort -rn | head -20
```

### 3c. 文件命中 Top N（热点文件）

```bash
jq -r '.file' report.json | sort | uniq -c | sort -rn | head -20
```

### 3d. 目录命中分布 Top 10

```bash
jq -r '.file | sub("^(.*)/[^/]+$"; "\(.file)")' report.json 2>/dev/null \
    | xargs -n1 dirname 2>/dev/null \
    | sort | uniq -c | sort -rn | head -10
```

更稳的写法：

```bash
jq -r '.file' report.json \
    | sed 's|/[^/]*$||' \
    | sort | uniq -c | sort -rn | head -10
```

### 3e. 按级别过滤

```bash
# 仅 high
jq -c 'map(select(.level=="high"))' report.json > high-only.json

# 仅 medium + low（跟踪项）
jq -c 'map(select(.level!="high"))' report.json > tracking.json
```

### 3f. 按规则 ID 过滤

```bash
# 仅看 empty-catch-block 命中
jq -c 'map(select(.ruleId=="empty-catch-block"))' report.json
```

### 3g. 按目录过滤

```bash
# 仅看 src/dao 目录的命中
jq -c 'map(select(.file | contains("/src/dao/")))' report.json
```

### 3h. 输出为 CSV

```bash
jq -r '.[] | [.level, .ruleId, .file, (.range.start.line + 1), (.range.start.column + 1), (.lines | gsub("\\s+"; " ") | .[0:80])] | @csv' \
    report.json > report.csv
```

### 3i. 输出为 Markdown 表格

```bash
{
    echo "| 级别 | 规则 | 文件 | 行 | 列 | 代码 |"
    echo "|------|------|------|----|----|------|"
    jq -r '.[] | "| \(.level) | \(.ruleId) | \(.file) | \(.range.start.line + 1) | \(.range.start.column + 1) | \(.lines | gsub("\\s+"; " ") | .[0:60]) |"' report.json
} > report.md
```

## 4. 与规则元数据关联

规则 ID 对应规则文件的扩展元数据（level/category/title/message/references），可通过 `yaml-meta.py` 查询：

```bash
RULE_ID=empty-catch-block
RULE_FILE=$(find "$CODE_CHECKLIST_ROOT/rules" -name "$RULE_ID.yml" | head -1)
python3 "$CODE_CHECKLIST_ROOT/scripts/lib/yaml-meta.py" collect "$RULE_FILE" | jq
```

输出示例：

```json
{
  "id": "empty-catch-block",
  "language": "java",
  "level": "high",
  "category": "correctness",
  "title": "空 catch 块吞异常",
  "message": "空 catch 块会吞掉异常，导致问题难以诊断...",
  "references": { "spotbugs": "DE_MIGHT_IGNORE", "pmd": "EmptyCatchBlock", "cwe": "CWE-390" },
  "since": "v0.1.0",
  "file": "/abs/rules/java/high/0000-0999/empty-catch-block.yml"
}
```

批量关联：把命中报告与规则元数据 join 后输出带标题的清单：

```bash
jq -r '.[] | .ruleId' report.json | sort -u | while read rid; do
    rf=$(find "$CODE_CHECKLIST_ROOT/rules" -name "$rid.yml" | head -1)
    title=$(python3 "$CODE_CHECKLIST_ROOT/scripts/lib/yaml-meta.py" collect "$rf" | jq -r .title)
    count=$(jq --arg rid "$rid" '[.[] | select(.ruleId==$rid)] | length' report.json)
    echo "$count	$rid	$title"
done | sort -rn > /tmp/rule-titles.tsv
column -t -s $'\t' /tmp/rule-titles.tsv
```

## 5. 报告完整性自检

```bash
# 必须是数组
jq 'if type=="array" then "OK: array" else "FAIL: not array" end' report.json

# 每条必须含必需字段
jq -r '.[] | select(.file == null or .ruleId == null or .level == null) | "缺失字段: \(.)"' report.json

# level 必须合法
jq -r '.[] | select(.level != "high" and .level != "medium" and .level != "low") | "非法 level: \(.)"' report.json

# 文件存在性
jq -r '.[].file' report.json | sort -u | while read f; do
    [[ -f "$f" ]] || echo "MISSING: $f"
done
```

## 6. 误报归档模板

对人工确认的误报，登记到 `.astgrepignore` 时建议同时维护一份"误报审计"文档：

```markdown
# ast-grep-block 误报审计

> 维护原则：优先优化规则，`.astgrepignore` 仅兜底。每次新增 ignore 必须记录原因。

| 规则 ID | 文件/路径模式 | 原因 | 登记日期 | 责任人 | 复核计划 |
|---------|---------------|------|----------|--------|----------|
| hardcoded-secret | src/test/resources/** | 测试用例常含示例密码 | 2026-07-28 | @foo | 永久豁免 |
| system-out-print | **/Main.java | main 入口打印 banner | 2026-07-28 | @bar | 季度复核 |
```
