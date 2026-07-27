# 陷阱与故障排除

按踩坑频率排序，附实测复现与解决方案。

## 陷阱 1：结果为 0 行（.gitignore 排除子目录）

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

## 陷阱 2：jq parse error: Invalid numeric literal

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

## 陷阱 3：jq syntax error (Unix shell quoting issues)

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

## 陷阱 4：Broken pipe (os error 32)

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

## 陷阱 5：build/target/gtest 目录大量噪声

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

## 陷阱 6：pom.xml 等配置 XML 误命中

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

## 陷阱 7：语言 kind 名称错误

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

## 陷阱 8：ast-grep -p 与 -k 互斥

**现象**：
```
error: the argument '--kind <KIND>' cannot be used with '--pattern <PATTERN>'
```

**解决**：`--pattern` 和 `--kind` 二选一。提取所有字符串字面量用 `--kind`，
精确匹配 AST 模式用 `--pattern`。

## 陷阱 9：拼接 SQL 片段化

**现象**：Java `"SELECT * FROM " + table + " WHERE id=?"` 被 ast-grep 解析为
两个独立 `string_literal`，输出两条记录（同行不同列）。

**原因**：AST 视角下，拼接表达式的每个字面量是独立节点。

**解决**：
- 接受现状：每段独立输出，便于定位
- 或用 AST 模式匹配整个拼接表达式（见 `recipes.md` 第 1 节）
- 或后处理：相邻行合并（见 `recipes.md` 第 5 节）

## 陷阱 10：fd/rg 工作目录默认尊重 .gitignore

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
