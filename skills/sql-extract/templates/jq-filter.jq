# jq SQL 过滤脚本
#
# 用途：过滤 ast-grep --json=stream 输出的字符串字面量，仅保留含 SQL 的字面量
# 输入：NDJSON（每行一个 JSON 对象，来自 ast-grep --json=stream）
# 输出：tab 分隔的 `<file>:<line>:<col>\t<source_line>`
#
# 使用：
#   ast-grep run -l cpp --kind string_literal --json=stream ... \
#     | jq -r -f /tmp/sql-filter.jq > /tmp/sql_cpp.lst
#
# 匹配规则说明（避免误报与漏报）：
#   - 忽略大小写：(?i)
#   - 词边界：\b
#   - 关键动词：select / insert / update / delete
#   - 关键介词/上下文：from / into / set
#   - 动词后必须紧跟介词，避免 "select" / "update" 等英文单词误命中
#   - 用 .* 连接（不跨多行，单字面量 SQL 一般单行）
#
# 调参建议：
#   - 收紧（高精度）：去掉 update/delete 的单独匹配，只匹配 select.*from / insert.*into
#   - 放宽（高召回）：去掉介词约束，仅匹配动词
#   - 含 PL/SQL：扩展动词列表，加 create/alter/drop/merge/truncate

select(
  .text | test("(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b")
)
# 输出格式：<file>:<line>:<col>\t<source_line>
# 行列号 +1：ast-grep 行列号从 0 开始，转 1-based 以匹配编辑器
| "\(.file):\(.range.start.line + 1):\(.range.start.column + 1)\t\(.lines | gsub("\\s+"; " ") | .[0:300])"
