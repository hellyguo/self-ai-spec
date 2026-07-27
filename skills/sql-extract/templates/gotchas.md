# 陷阱与故障排除

按踩坑频率排序，附实测复现与解决方案。

## MCP 模式陷阱

### 陷阱 M1：constraints.regex 转义错误

**现象**：`find_code_by_rule` 返回 0 结果，但代码中明确有 SQL 字面量。

**原因**：YAML 中 `\b` 需写为 `\\b`，`\s` 需写为 `\\s`。单反斜杠在 YAML 中被解释为转义序列，传给 ast-grep 的正则已损坏。

**复现**：
```yaml
# 错误：\b 在 YAML 中被吞
constraints:
  SQL:
    regex: '(?i)\b(select|insert)\b.*\b(from|into)\b'
```

**解决**：
```yaml
# 正确：双反斜杠
constraints:
  SQL:
    regex: '(?i)\\b(select|insert)\\b.*\\b(from|into)\\b'
```

**验证**：用 `test_match_code_rule` 先验证规则能命中已知 SQL 代码。

### 陷阱 M2：regex 写在 rule 而非 constraints 下

**现象**：
```
Error: Cannot parse rule INLINE_RULES
Caused by: invalid type: map, expected a string
```

**原因**：ast-grep 的 `rule` 下不支持 `regex` 字段。正则约束必须放在 `constraints` 下，对 meta-variable 施加。

**复现**：
```yaml
# 错误：regex 不属于 rule
rule:
  pattern: '"$SQL"'
  regex:
    id: SQL
    regex: '(?i)...'
```

**解决**：
```yaml
# 正确：regex 属于 constraints
rule:
  pattern: '"$SQL"'
constraints:
  SQL:
    regex: '(?i)...'
```

### 陷阱 M3：MCP 超时（大型项目）

**现象**：`find_code_by_rule` 无返回或报超时错误。

**原因**：项目文件量过大（>10k 文件），ast-grep 扫描耗时超过 MCP 超时限制。

**解决**：
1. 将 `project_folder` 限定为子目录，分批搜索
2. 使用 `max_results` 限制返回数量
3. 回退到 CLI 模式（无超时限制）

### 陷阱 M4：find_code_by_rule 不支持 --globs 排除

**现象**：结果中包含 `build/`、`target/` 目录下的生成代码。

**原因**：MCP 的 `find_code_by_rule` 不支持 `--globs` 参数，无法排除目录。

**解决**：
1. 将 `project_folder` 限定为业务源码目录（如 `src/main/`），而非项目根
2. 搜索后人工过滤 `build/`、`target/`、`third_party/` 路径下的结果
3. 回退到 CLI 模式使用 `--globs '!**/build/**'`

### 陷阱 M5：any + constraints 的交叉约束

**现象**：使用 `any` 组合多个 pattern 时，constraints 对所有分支生效，导致部分分支误过滤。

**原因**：`constraints` 中的变量名在 `any` 的某个分支中不存在时，该分支自动不满足约束被过滤。

**解决**：为 `any` 的每个分支分别定义约束变量名，或在 `any` 外层不使用 constraints：

```yaml
# 方案 A：每个分支独立约束
rule:
  any:
    - pattern: '"$SQL"'
    - pattern: '"$L" + $R'
constraints:
  SQL:
    regex: '(?i)\\b(select|insert|update|delete)\\b'
  L:
    regex: '(?i)\\b(select|insert|update|delete)\\b'
# 注意：SQL 约束对第二个分支无效（无 $SQL 变量），L 约束对第一个分支无效（无 $L 变量）
# 但 ast-grep 对 any 的语义是：任一分支匹配即可，constraints 中不存在的变量视为满足
```

### 陷阱 M6：Java 正则语法限制

**现象**：constraints.regex 使用 lookbehind `(?<=...)` 或 named group `(?<name>...)` 后报错。

**原因**：ast-grep 的 constraints.regex 使用 Java 正则引擎（`java.util.regex.Pattern`），但部分高级特性可能不被支持。

**解决**：使用基础正则语法：`(?i)`、`\b`、`\s`、`.*`、`|`、`()` 等。避免 lookbehind、named group、atomic group 等高级特性。

## CLI 模式陷阱

### 陷阱 1：结果为 0 行（.gitignore 排除子目录）

**现象**：项目根的 `.gitignore` 排除了所有子模块目录（`QES3`、`qes3_client` 等），fd/rg 默认返回 0 文件，ast-grep 默认也尊重 `.gitignore`。

**复现**：
```bash
$ fd -e cpp -t f /disk2/.../QES_mixed_project | wc -l
0   # 期望数千
```

**解决**：必须加 `--no-ignore vcs`：
```bash
ast-grep run -l cpp --kind string_literal --no-ignore vcs ...
```

rg 等价参数：`--no-ignore-vcs`。

### 陷阱 2：jq parse error: Invalid numeric literal

**现象**：
```
jq: parse error: Invalid numeric literal at line 1, column 44
```

**原因**：未指定 `--json=stream`，ast-grep 默认 `--json=pretty` 输出为数组 `[...]`，
但流式管道中 jq 收到的是「被管道缓冲切断的 JSON 片段」。

**解决**：显式 `--json=stream` 输出 NDJSON（每行一对象）：
```bash
ast-grep run ... --json=stream | jq -r -f filter.jq
```

### 陷阱 3：jq syntax error (Unix shell quoting issues)

**现象**：
```
jq: error: syntax error, unexpected INVALID_CHARACTER (Unix shell quoting issues?)
```

**原因**：在 `-o`/命令行内联含 `\\b`、`\\s`、`(?i)` 等的正则时，shell 的双引号
与反斜杠转义相互干扰，传给 jq 的字符串已被破坏。

**解决**：**永远用 `-f 文件`**：
```bash
# 错误（shell 转义陷阱）
jq -r 'select(.text | test("(?i)\\b(select...)\\b"))'

# 正确（脚本文件，无 shell 干扰）
jq -r -f /tmp/sql-filter.jq
```

### 陷阱 4：Broken pipe (os error 32)

**现象**：ast-grep stderr 报：
```
Error: Broken pipe (os error 32)
```

**原因**：jq 提前结束（如 `select(...)` 过滤大量行后），上游管道关闭。

**解决**：**正常现象，不影响结果**。仅在 stderr 输出，stdout 已正确生成 lst。
若需消除噪声：
```bash
ast-grep ... 2>/dev/null | jq ...
```

### 陷阱 5：build/target/gtest 目录大量噪声

**现象**：结果中包含大量 `build/CMakeFiles/`、`target/generated-sources/`、
`gtest/` 下的文件，与业务无关。

**解决**：必排除：
```bash
--globs '!**/build/**' \
--globs '!**/target/**' \
--globs '!**/.git/**' \
--globs '!**/gtest/**' \
--globs '!**/out/**' \
--globs '!**/dist/**' \
```

### 陷阱 6：pom.xml 等配置 XML 误命中

**现象**：XML 兜底检索时，`pom.xml` 命中 `<update.class>`、`<select.org>` 等自定义标签。

**原因**：rg 用 `<select\b|<update\b` 匹配 XML 标签名，但 Maven 的 pom.xml
允许任意自定义标签（如 `update.class`）。

**解决**：
```bash
# 排除 pom.xml
rg --no-ignore-vcs -g '*.xml' -g '!pom.xml' ...

# 或限定更严格的 MyBatis namespace 模式
rg --no-ignore-vcs -g '*Mapper.xml' ...
```

### 陷阱 7：语言 kind 名称错误

**现象**：
```
Error: Cannot parse kind as a valid selector.
Kind `string` is invalid.
```

**原因**：tree-sitter 各语言的 kind 名不一致，并非都是 `string`。

**对照表**：

| 语言 | kind |
|------|------|
| cpp | `string_literal` |
| java | `string_literal` |
| csharp | `string_literal`、`verbatim_string_literal` |
| go | `interpreted_string_literal`、`raw_string_literal` |
| python | `string` |
| rust | `string_literal`、`raw_string_literal` |

**验证方法**：
```bash
echo 'const char* s = "SELECT * FROM t";' > /tmp/t.cpp
ast-grep run -l cpp --kind string_literal /tmp/t.cpp
# 应输出 1 行命中
```

**MCP 验证方法**：
```
dump_syntax_tree(code: 'const char* s = "SELECT * FROM t";', language: cpp, format: cst)
# 查看 string_literal 节点名
```

### 陷阱 8：ast-grep -p 与 -k 互斥

**现象**：
```
error: the argument '--kind <KIND>' cannot be used with '--pattern <PATTERN>'
```

**解决**：`--pattern` 和 `--kind` 二选一。提取所有字符串字面量用 `--kind`，
精确匹配 AST 模式用 `--pattern`。

**MCP 等价**：`find_code` 使用 pattern，`find_code_by_rule` 使用 rule.pattern，无 kind 选项。
MCP 模式下用 `pattern: '"$SQL"'` 等价于 CLI 的 `--kind string_literal` + jq 过滤。

### 陷阱 9：拼接 SQL 片段化

**现象**：Java `"SELECT * FROM " + table + " WHERE id=?"` 被 ast-grep 解析为
两个独立 `string_literal`，输出两条记录（同行不同列）。

**原因**：AST 视角下，拼接表达式的每个字面量是独立节点。

**解决**：
- MCP：用 `any` 组合规则匹配拼接表达式（见 `recipes.md` 第 1 节）
- CLI：用 AST 模式匹配整个拼接表达式（见 `recipes.md` 第 1 节）
- 通用：后处理相邻行合并（见 `recipes.md` 第 5 节）

### 陷阱 10：fd/rg 工作目录默认尊重 .gitignore

**现象**：
```
rg: No files were searched, which means ripgrep probably applied a filter you didn't expect.
```

**解决**：
```bash
# rg
rg --no-ignore-vcs ...

# fd
fd --no-ignore ...

# ast-grep
ast-grep ... --no-ignore vcs
```

## 故障排除速查

### MCP 模式

| 现象 | 原因 | 解决 |
|------|------|------|
| 0 结果 | constraints.regex 转义错误 | YAML 中 `\\b` 非 `\b` |
| rule parse error | regex 写在 rule 下 | 移到 `constraints.SQL.regex` |
| 超时无返回 | 项目文件量过大 | 分目录搜索或回退 CLI |
| 含 build/ 噪声 | 无 --globs 支持 | 限定 project_folder 或人工过滤 |
| any 分支误过滤 | constraints 交叉约束 | 每个分支独立约束变量名 |
| regex 报错 | Java 正则高级特性 | 用基础语法，避免 lookbehind 等 |

### CLI 模式

| 现象 | 原因 | 解决 |
|------|------|------|
| 0 结果 | .gitignore 排除 | `--no-ignore vcs`（ast-grep）/ `--no-ignore-vcs`（rg） |
| jq parse error | 缺 `--json=stream` | 显式 `--json=stream` |
| jq syntax error | 内联正则转义 | `-f /tmp/sql-filter.jq` |
| Broken pipe | jq 提前退出 | 正常现象，stderr 重定向 `/dev/null` |
| kind invalid | 语言 kind 名不对 | 参见陷阱 7 对照表 |
| -p/-k 互斥 | 二者只能选一 | 用 `-k` 提取所有字面量 |
| build 噪声 | 未排除产物 | `--globs '!**/build/**'` |
| pom.xml 噪声 | 自定义标签 | `--globs '!pom.xml'` |
| 拼接 SQL 片段化 | AST 自然行为 | 接受或用 AST 模式合并 |
| 速度慢 | 单线程 | 默认并发，必要时 `--threads N` |
| 内存峰值高 | 全量缓冲 | 用 stream 管道，避免 `--json=pretty` |

## 调试技巧

### MCP 模式

```
# 1. 验证规则是否匹配已知代码
test_match_code_rule(code: 'String sql = "SELECT * FROM t";', yaml: '<rule>')

# 2. 查看代码的 AST 结构（调试 pattern）
dump_syntax_tree(code: 'String sql = "SELECT * FROM t";', language: java, format: cst)

# 3. 查看 ast-grep 如何解释 pattern
dump_syntax_tree(code: '"$SQL"', language: java, format: pattern)

# 4. 简单 pattern 快速搜索
find_code(pattern: '"SELECT"', language: java, project_folder: "<dir>")
```

### CLI 模式

```bash
# 1. 查看 ast-grep 解析的 AST（调试 pattern）
ast-grep run -l cpp --debug-query=ast -p '"SELECT"' /tmp/t.cpp

# 2. 查看 tree-sitter 完整 CST
ast-grep run -l cpp --debug-query=cst -p '$X' /tmp/t.cpp

# 3. jq 调试：不过滤，看原始 JSON
ast-grep run -l cpp --kind string_literal --json=stream <dir> | head

# 4. 验证单文件
ast-grep run -l cpp --kind string_literal <one_file>

# 5. 测试 jq 脚本（不依赖 ast-grep）
echo '{"text":"\"SELECT * FROM t\"","range":{"start":{"line":1,"column":0}},"file":"/tmp/x","lines":"  \"SELECT * FROM t\""}' \
  | jq -r -f /tmp/sql-filter.jq
```
