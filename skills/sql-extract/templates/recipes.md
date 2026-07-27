# 进阶命令配方

## 1. SQL 拼接点识别

字符串拼接（`"select" + var + "from t"`）会被 ast-grep 按片段匹配。
识别「拼接 SQL」的两种方法：

### 方法 A：基于拼接 AST 模式

```bash
# Java: 字符串拼接（+ 操作符）含 SQL 片段
ast-grep run -l java -p '"$$$L" + $$$R' --json=stream <java_dirs> \
  | jq -r -f /tmp/sql-filter.jq > /tmp/sql_java_concat.lst

# C++: stringstream << "SQL"
ast-grep run -l cpp -p '$STREAM << "$$$ARGS"' --json=stream <cpp_dirs> \
  | jq -r 'select(.lines | test("(?i)\\b(select|insert|update|delete)")) | "\(.file):\(.range.start.line+1)"' \
  > /tmp/sql_cpp_stream.lst
```

### 方法 B：基于 rg 兜底

```bash
# 含变量插值的 SQL（Java String.format / Python f-string / C sprintf）
rg -n -i '(String\.format|sprintf|snprintf|f".*SELECT)' <dirs>
```

## 2. 增量分析（仅 git diff）

仅抽取改动行中的 SQL，用于 PR 审查：

```bash
# 获取改动的文件列表
CHANGED=$(git diff --name-only --diff-filter=AM HEAD~1 HEAD | grep -E '\.(cpp|java)$')

# 限定文件传入 ast-grep
ast-grep run -l cpp --kind string_literal --json=stream $CHANGED \
  | jq -r -f /tmp/sql-filter.jq > /tmp/sql_diff.lst
```

## 3. 按 SQL 类型分类

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

```bash
# 排除第三方/二方库
ast-grep run -l cpp --kind string_literal --json=stream \
  --globs '!**/third_party/**' \
  --globs '!**/extern/**' \
  --globs '!**/vendor/**' \
  ...
```

## 7. 输出 CSV（便于表格工具导入）

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

输出 vim/VSCode quickfix 格式：

```bash
# vim quickfix（grep -n 格式：file:line:content）
sed 's/^\([^:]*\):\([0-9]*\):\([0-9]*\)\t/\1:\2:/' /tmp/sql_cpp.lst > /tmp/sql_cpp.qf
vim -q /tmp/sql_cpp.qf
```

## 9. 性能优化

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

适合临时排查，但正则转义易出错，慎用：

```bash
# 不推荐：内联 jq 正则（容易出现 shell 转义错误）
ast-grep run -l cpp --kind string_literal --json=stream <dir> \
  | jq -r 'select(.text | test("(?i)\\bselect\\b")) | .file' \
  | sort -u

# 推荐：用 rg 兜底（更简单但精度略低）
rg -l -i --type cpp '(select|insert|update|delete).*(from|into|set)' <dir>
```
