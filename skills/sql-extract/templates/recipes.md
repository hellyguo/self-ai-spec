# 进阶命令配方

## 1. SQL 拼接点识别

### MCP 模式（首选）

**Java 字符串拼接**（`"SELECT * FROM " + table`）：

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-concat-java
    language: java
    rule:
      any:
        - pattern: '"$SQL"'
        - pattern: '"$L" + $R'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b'
      L:
        regex: '(?i)\\b(select|insert|update|delete)\\b'
  '''
)
```

**C++ stringstream 拼接**：

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-stream-cpp
    language: cpp
    rule:
      pattern: '$STREAM << "$SQL"'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b'
  '''
)
```

**Java StringBuilder 拼接**：

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-builder-java
    language: java
    rule:
      any:
        - pattern: $SB.append("$SQL")
        - pattern: $SB.append(String.format("$SQL"))
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b'
  '''
)
```

**含变量插值的 SQL**（String.format / sprintf）：

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-format-java
    language: java
    rule:
      pattern: String.format("$SQL", $$$ARGS)
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b'
  '''
)
```

### CLI 模式（兜底）

```bash
# Java: 字符串拼接（+ 操作符）含 SQL 片段
ast-grep run -l java -p '"$$$L" + $$$R' --json=stream <java_dirs> \
  | jq -r -f /tmp/sql-filter.jq > /tmp/sql_java_concat.lst

# C++: stringstream << "SQL"
ast-grep run -l cpp -p '$STREAM << "$$$ARGS"' --json=stream <cpp_dirs> \
  | jq -r 'select(.lines | test("(?i)\\b(select|insert|update|delete)")) | "\(.file):\(.range.start.line+1)"' \
  > /tmp/sql_cpp_stream.lst

# 含变量插值的 SQL（Java String.format / Python f-string / C sprintf）
rg -n -i '(String\.format|sprintf|snprintf|f".*SELECT)' <dirs>
```

## 2. 增量分析（仅 git diff）

### MCP 模式

```bash
# 获取改动文件列表
CHANGED=$(git diff --name-only --diff-filter=AM HEAD~1 HEAD | grep -E '\.(cpp|java)$')
```

对每个改动文件调用 `find_code_by_rule`（限定 `project_folder` 为文件所在目录），
或对改动文件所在目录批量搜索。

> **注意**：`find_code_by_rule` 的 `project_folder` 是目录级搜索，无法精确到单文件。
> 如需单文件精确搜索，用 `find_code` + pattern。

### CLI 模式

```bash
# 获取改动的文件列表
CHANGED=$(git diff --name-only --diff-filter=AM HEAD~1 HEAD | grep -E '\.(cpp|java)$')

# 限定文件传入 ast-grep
ast-grep run -l cpp --kind string_literal --json=stream $CHANGED \
  | jq -r -f /tmp/sql-filter.jq > /tmp/sql_diff.lst
```

## 3. 按 SQL 类型分类

### MCP 模式

修改 `constraints.regex` 即可按类型过滤：

**仅 SELECT**（慢 SQL 优化候选）：
```
constraints:
  SQL:
    regex: '(?i)\\bselect\\b.*\\bfrom\\b'
```

**仅 INSERT**：
```
constraints:
  SQL:
    regex: '(?i)\\binsert\\b.*\\binto\\b'
```

**仅 UPDATE**：
```
constraints:
  SQL:
    regex: '(?i)\\bupdate\\b.*\\bset\\b'
```

**仅 DELETE**：
```
constraints:
  SQL:
    regex: '(?i)\\bdelete\\b.*\\bfrom\\b'
```

**仅 DDL**（建表/改表）：
```
constraints:
  SQL:
    regex: '(?i)\\b(create|alter|drop)\\b\\s+(table|index|view)\\b'
```

### CLI 模式

```bash
# 分类统计：select / insert / update / delete
for kw in select insert update delete; do
  count=$(rg -c -i "^.*\b$kw\b" /tmp/sql_cpp.lst | head -1)
  printf "%-8s %s\n" "$kw" "$count"
done

# 仅 SELECT（用于慢 SQL 优化候选）
rg '\bselect\b' -i /tmp/sql_cpp.lst > /tmp/sql_select.lst

# 仅 DDL（建表/改表）
rg '\b(create|alter|drop)\b\s+(table|index|view)' -i /tmp/sql_cpp.lst > /tmp/sql_ddl.lst
```

## 4. 多语言批量抽取

### MCP 模式

按语言依次调用 `find_code_by_rule`，仅改 `language` 字段：

```
# Java
find_code_by_rule(yaml: "id: sql-java\nlanguage: java\nrule: {pattern: '\"$SQL\"'}\nconstraints: {SQL: {regex: '(?i)\\\\b(select|insert|update|delete)\\\\b.*\\\\b(from|into|set)\\\\b'}}", project_folder: "<root>")

# C++
find_code_by_rule(yaml: "id: sql-cpp\nlanguage: cpp\nrule: {pattern: '\"$SQL\"'}\nconstraints: {SQL: {regex: '(?i)\\\\b(select|insert|update|delete)\\\\b.*\\\\b(from|into|set)\\\\b'}}", project_folder: "<root>")

# Go（含 raw string）
find_code_by_rule(yaml: "id: sql-go\nlanguage: go\nrule: {any: [{pattern: '\"$SQL\"'}, {pattern: '`$SQL`'}]}\nconstraints: {SQL: {regex: '(?i)\\\\b(select|insert|update|delete)\\\\b.*\\\\b(from|into|set)\\\\b'}}", project_folder: "<root>")

# Python
find_code_by_rule(yaml: "id: sql-py\nlanguage: python\nrule: {pattern: '\"$SQL\"'}\nconstraints: {SQL: {regex: '(?i)\\\\b(select|insert|update|delete)\\\\b.*\\\\b(from|into|set)\\\\b'}}", project_folder: "<root>")
```

### CLI 模式

```bash
#!/bin/bash
# extract-all.sh —— 全语言 SQL 抽取
set -e
PROJECT=$1
OUT=/tmp/sql_all

declare -A LANGS=(
  [cpp]="cpp cxx cc h hpp hxx"
  [java]="java"
  [cs]="cs"
  [go]="go"
  [py]="py"
)

for lang in "${!LANGS[@]}"; do
  exts=${LANGS[$lang]}
  echo ">>> 抽取 $lang ..."
  globs=""
  for e in $exts; do globs="$globs --globs '**/*.$e'"; done
  # shellcheck disable=SC2086
  ast-grep run -l $lang --kind string_literal --json=stream \
    --no-ignore vcs $globs "$PROJECT" \
    2>/dev/null \
    | jq -r -f /tmp/sql-filter.jq \
    > "$OUT.$lang.lst" 2>/dev/null || true
  wc -l "$OUT.$lang.lst"
done
```

## 5. 结果去重与合并

### MCP 模式

`find_code_by_rule` 返回 JSON 时，同一文件多行 SQL 拼接会分别输出。
Agent 可在内存中按文件聚合、相邻行合并。

### CLI 模式

同一文件连续行可能属于同一 SQL 拼接：

```bash
# 按文件聚合，相邻行合并为单条
awk -F: '
{
  file=$1; line=$2;
  if (file != prev_file || line != prev_line+1) {
    if (NR > 1) printf "\n";
    printf "%s:%s ", file, line;
  }
  prev_file=file; prev_line=line;
}' /tmp/sql_cpp.lst > /tmp/sql_cpp.merged.lst
```

## 6. 排除特定路径

### MCP 模式

`find_code_by_rule` 不支持 `--globs` 排除。替代方案：
- 将 `project_folder` 限定为业务源码目录（如 `src/main/`），而非项目根
- 搜索后人工过滤 `build/`、`target/`、`third_party/` 路径下的结果

### CLI 模式

```bash
# 排除第三方/二方库
ast-grep run -l cpp --kind string_literal --json=stream \
  --globs '!**/third_party/**' \
  --globs '!**/extern/**' \
  --globs '!**/vendor/**' \
  ...
```

## 7. 输出 CSV（便于表格工具导入）

### MCP 模式

`find_code_by_rule(output_format="json")` 返回结构化 JSON，可直接转换为 CSV。

### CLI 模式

修改 jq 输出格式：

```bash
# 修改 jq-filter.jq 末行，将 tab 改为逗号，并加 CSV 头
echo "file,line,column,source" > /tmp/sql_cpp.csv
ast-grep run -l cpp --kind string_literal --json=stream ... \
  | jq -r 'select(.text | test("(?i)...")) 
          | "\"\(.file)\",\(.range.start.line+1),\(.range.start.column+1),\"\(.lines | gsub("\""; "\"\"") | gsub("\\s+"; " "))\""'
  >> /tmp/sql_cpp.csv
```

## 8. 与 IDE 集成（quickfix 风格）

### MCP 模式

MCP 返回的 JSON 已包含 `file` + `range` 信息，可直接映射到 IDE 的 quickfix/diagnostic。

### CLI 模式

输出 vim/VSCode quickfix 格式：

```bash
# vim quickfix（grep -n 格式：file:line:content）
sed 's/^\([^:]*\):\([0-9]*\):\([0-9]*\)\t/\1:\2:/' /tmp/sql_cpp.lst > /tmp/sql_cpp.qf
vim -q /tmp/sql_cpp.qf
```

## 9. 性能优化

### MCP 模式

- 使用 `max_results` 限制返回数量，避免超时
- 分目录搜索：将大项目拆为多个子目录分别调用
- 先用 `find_code` 快速验证，再用 `find_code_by_rule` 全量搜索

### CLI 模式

```bash
# 限制并发（内存受限环境）
ast-grep run -l cpp --kind string_literal --json=stream \
  --threads 4 ...   # 默认是 CPU 核数

# 分批处理（巨型项目）
for dir in dir1 dir2 dir3; do
  ast-grep run -l cpp --kind string_literal --json=stream "$dir" \
    | jq -r -f /tmp/sql-filter.jq >> /tmp/sql_cpp.lst
done
```

## 10. 一行式管道（无临时脚本）

### MCP 模式

MCP 天然无需临时脚本，直接调用即可。

### CLI 模式

适合临时排查，但正则转义易出错，慎用：

```bash
# 不推荐：内联 jq 正则（容易出现 shell 转义错误）
ast-grep run -l cpp --kind string_literal --json=stream <dir> \
  | jq -r 'select(.text | test("(?i)\\bselect\\b")) | .file' \
  | sort -u

# 推荐：用 rg 兜底（更简单但精度略低）
rg -l -i --type cpp '(select|insert|update|delete).*(from|into|set)' <dir>
```

## 11. Go raw string literal

Go 的 raw string（反引号）不会被 `'"$SQL"'` 匹配，需额外规则：

### MCP 模式

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-go-raw
    language: go
    rule:
      pattern: '`$SQL`'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b'
  '''
)
```

组合普通字符串 + raw string：
```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-go-all
    language: go
    rule:
      any:
        - pattern: '"$SQL"'
        - pattern: '`$SQL`'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b'
  '''
)
```

## 12. C# verbatim string literal

C# 的 `@"..."` verbatim string 需单独匹配：

### MCP 模式

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-cs-verbatim
    language: csharp
    rule:
      any:
        - pattern: '"$SQL"'
        - pattern: '@"$SQL"'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b'
  '''
)
```
