---
name: sql-extract
description: "SQL抽取技能：从C++/Java/XML源代码中抽取内嵌SQL语句，优先使用ast-grep-mcp(AST精准匹配+constraints正则约束)，CLI管道为兜底方案，识别SQL拼接点，输出文件清单"
---

# SQL 抽取技能

从源代码中**精准抽取**内嵌 SQL 语句，识别 SQL 拼接点，输出位置清单与统计。

适用场景：
- 代码审查前的 SQL 注入风险点盘点
- 慢 SQL 优化的候选 SQL 收集
- 数据库迁移时的全量 SQL 走查
- 重构时的 SQL 集中化（迁移到 DAO/Mapper 层）

## 核心思路

**三层方案，优先使用 MCP**：

1. **首选层（ast-grep-mcp）**：通过 `find_code_by_rule` 使用 YAML rule 的 `pattern` + `constraints.regex` 一步完成 AST 匹配 + SQL 关键字过滤
   - 优势：无需 jq 管道、无需临时文件、无需 shell 转义、直接输出结构化结果
   - 适用：AI Agent 交互式分析场景（opencode/cursor 等）
2. **CLI 层（ast-grep + jq 管道）**：`ast-grep --kind string_literal --json=stream` → `jq` 正则过滤
   - 优势：流式处理、适合大规模项目（万级文件）、可脚本化批量运行
   - 适用：终端批量分析、CI/CD 集成、超大型项目
3. **兜底层（ripgrep）**：`rg` 直接扫描文本
   - 优势：支持 XML（ast-grep 不支持 XML 语言）
   - 适用：MyBatis mapper.xml、配置文件

## 工具依赖

### MCP 模式（首选）

| 工具 | 来源 | 用途 |
|------|------|------|
| ast-grep-mcp | MCP Server | `find_code_by_rule` / `find_code` / `test_match_code_rule` / `dump_syntax_tree` |

无需本地安装 jq，MCP 内置 AST 匹配 + regex constraints。

### CLI 模式（兜底）

| 工具 | 版本 | 安装 | 用途 |
|------|------|------|------|
| ast-grep | >= 0.45 | `cargo install ast-grep` | AST 提取字符串字面量 |
| jq | >= 1.6 | 系统包管理器 | JSON 流过滤 |
| ripgrep | >= 13 | `cargo install ripgrep` | 兜底正则检索 |
| fd | >= 8 | `cargo install fd-find` | 文件枚举（可选） |

验证：
```bash
ast-grep --version && jq --version && rg --version | head -1
```

## 执行流程

### 步骤 1：确定目标范围

先识别项目结构，明确：

- 源代码根目录（如 `QES3/src`、`qes3_client/qes-biz`）
- 构建产物目录（`build/`、`target/`、`out/`）→ **必须排除**
- 测试目录（`gtest/`、`src/test/`）→ 按需排除
- 第三方/二方库（`third_party/`、`lib/`）→ 按需排除

```bash
# 列出顶层目录
eza <project_root>

# 统计文件数
fd --no-ignore -e cpp -e h -e hpp -t f <project_root> | wc -l   # C++
fd --no-ignore -e java -t f <project_root> | wc -l               # Java
fd --no-ignore -e xml -t f <project_root> | wc -l                # XML
```

### 步骤 2：验证规则（MCP 模式必做）

用 `test_match_code_rule` 验证 YAML rule 在目标语言上能正确匹配 SQL 字面量、排除非 SQL 字面量：

**验证 SQL 字面量能命中**：
```
test_match_code_rule(
  code: 'String sql = "SELECT * FROM user WHERE id = 1";',
  yaml: '''
    id: sql-string-java
    language: java
    rule:
      pattern: '"$SQL"'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b'
  '''
)
```

**验证非 SQL 字面量不命中**：
```
test_match_code_rule(
  code: 'String normal = "hello world";',
  yaml: '''<同上 rule>'''
)
→ 应返回 "No matches found"
```

### 步骤 3：抽取内嵌 SQL（MCP 模式 - 首选）

#### 3a. Java 内嵌 SQL

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-string-java
    language: java
    rule:
      pattern: '"$SQL"'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b'
  '''
)
```

#### 3b. C++ 内嵌 SQL

```
find_code_by_rule(
  project_folder: "<project_root>",
  yaml: '''
    id: sql-string-cpp
    language: cpp
    rule:
      pattern: '"$SQL"'
    constraints:
      SQL:
        regex: '(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b'
  '''
)
```

#### 3c. 其他语言

各语言 pattern 相同（`'"$SQL"'`），只需改 `language` 字段：

| 语言 | language 值 |
|------|------------|
| C/C++ | `cpp` |
| Java | `java` |
| C# | `csharp` |
| Go | `go` |
| Python | `python` |
| Kotlin | `kotlin` |
| Rust | `rust` |
| Scala | `scala` |

> **注意**：Go 的 raw string literal（`` `SELECT * FROM t` ``）不会被 `'"$SQL"'` 匹配，
> 需额外用 pattern `` `$$$SQL` `` 匹配。参见 `templates/recipes.md`。

#### 3d. SQL 拼接点识别

Java 字符串拼接（`"SELECT * FROM " + table`）需用 `any` 组合规则：

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

C++ stringstream 拼接：
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

### 步骤 4：抽取内嵌 SQL（CLI 模式 - 兜底）

当 MCP 不可用、或项目文件量过大（>10k 文件）导致 MCP 超时时，回退到 CLI 管道。

#### 4a. 编写过滤脚本

```bash
cp templates/jq-filter.jq /tmp/sql-filter.jq
```

模板详情见 `templates/jq-filter.jq`。**禁止在命令行内联复杂正则**。

#### 4b. 抽取 C++ 内嵌 SQL

```bash
ast-grep run -l cpp --kind string_literal --json=stream \
  --no-ignore vcs \
  --globs '!**/build/**' --globs '!**/target/**' \
  --globs '!**/.git/**' --globs '!**/gtest/**' \
  <cpp_dirs...> \
  2>/tmp/sql_cpp.ast.err \
  | jq -r -f /tmp/sql-filter.jq \
  > /tmp/sql_cpp.lst 2>/tmp/sql_cpp.err
```

#### 4c. 抽取 Java 内嵌 SQL

```bash
ast-grep run -l java --kind string_literal --json=stream \
  --no-ignore vcs \
  --globs '!**/target/**' --globs '!**/build/**' \
  --globs '!**/.git/**' --globs '!**/test/**' \
  <java_dirs...> \
  2>/tmp/sql_java.ast.err \
  | jq -r -f /tmp/sql-filter.jq \
  > /tmp/sql_java.lst 2>/tmp/sql_java.err
```

### 步骤 5：抽取 XML 内嵌 SQL

ast-grep（无论 MCP 还是 CLI）**不支持** XML 语言，必须用 ripgrep：

```bash
# MyBatis mapper 风格
rg --no-ignore-vcs -n -g '*.xml' -- '(<select\b|<insert\b|<update\b|<delete\b|<sql\b)' <xml_dirs...> \
  >> /tmp/sql_java.lst

# 文本内嵌 SQL（非 MyBatis）
rg --no-ignore-vcs -n -i -g '*.xml' \
  -- '\b(select|insert\s+into|update\s+\w+\s+set|delete\s+from)\b\s+.*\b(from|where|values)\b' \
  <xml_dirs...> \
  >> /tmp/sql_java.lst
```

**注意**：`pom.xml` 等配置 XML 的 `<update.class>` 等自定义标签会误命中，需人工复核或加 `--glob '!pom.xml'`。

### 步骤 6：验证与统计

**MCP 模式**：`find_code_by_rule` 返回 JSON 时，直接统计命中数、文件分布。

**CLI 模式**：
```bash
# 行数
wc -l /tmp/sql_cpp.lst /tmp/sql_java.lst

# 唯一文件数
cut -d: -f1 /tmp/sql_cpp.lst | sort -u | wc -l

# 文件命中分布 Top 20（定位热点）
cut -d: -f1 /tmp/sql_cpp.lst | sort | uniq -c | sort -rn | head -20

# 目录命中分布
cut -d: -f1 /tmp/sql_cpp.lst | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -10
```

### 步骤 7：复核（必做）

**MCP 模式**：用 `find_code` 抽查单个文件的全量字符串字面量，与 SQL 命中结果对照：
```
find_code(pattern: '"$X"', language: java, project_folder: "<file_dir>")
```

**CLI 模式**：
```bash
head -10 /tmp/sql_cpp.lst                          # 命中样本
ast-grep run -l cpp --kind string_literal <file>   # 全量字面量对照
```

## MCP YAML Rule 详解

### 核心 Rule 结构

```yaml
id: <rule_id>           # 必填，规则唯一标识
language: <lang>        # 必填，目标语言
rule:                   # 必填，匹配规则
  pattern: '"$SQL"'     # 匹配字符串字面量，$SQL 捕获内容
constraints:            # 可选，对 meta-variable 施加正则约束
  SQL:
    regex: '<pattern>'  # Java 风格正则（非 PCRE）
```

### constraints.regex 说明

- 语法：Java 正则（`java.util.regex.Pattern`），**不是** PCRE/JavaScript 正则
- `(?i)` 内联忽略大小写：有效
- `\b` 词边界：有效
- `\s` 空白：有效
- **不支持** lookbehind `(?<=...)`、named groups `(?<name>...)` 等高级特性
- 转义：YAML 中 `\b` 需写为 `\\b`，`\s` 需写为 `\\s`

### SQL 过滤正则（推荐值）

**严格模式**（高精度，推荐默认使用）：
```
(?i)\\b(select|insert|update|delete)\\b.*\\b(from|into|set)\\b
```
要求动词后必须跟介词，避免 "select"/"update" 等英文单词误命中。

**宽松模式**（高召回，用于初步扫描）：
```
(?i)\\b(select|insert|update|delete)\\b
```
仅匹配动词，需人工复核排除误报。

**含 DDL**（建表/改表场景）：
```
(?i)\\b(select|insert|update|delete|create|alter|drop|merge|truncate)\\b.*\\b(from|into|set|table|index|view)\\b
```

### MCP 工具对照

| MCP 工具 | 用途 | 场景 |
|----------|------|------|
| `find_code_by_rule` | YAML rule 搜索项目代码 | **主力**：SQL 抽取、拼接点识别 |
| `find_code` | 简单 pattern 搜索 | 快速抽查单文件、验证语法 |
| `test_match_code_rule` | 测试 rule 是否匹配给定代码 | **步骤 2 必用**：验证规则正确性 |
| `dump_syntax_tree` | 查看代码的 AST/CST 结构 | 调试 pattern、确认节点 kind |

### MCP vs CLI 选择指南

| 维度 | MCP 模式 | CLI 模式 |
|------|----------|----------|
| 交互方式 | AI Agent 工具调用 | 终端命令 |
| 过滤方式 | `constraints.regex`（内置） | `jq` 管道（外部） |
| 临时文件 | 不需要 | 需要 jq 脚本 + lst 输出 |
| Shell 转义 | 无（YAML 原生） | 有（需 `-f` 避免） |
| 大规模项目 | 受 MCP 超时限制 | 无限制（流式管道） |
| 结果格式 | JSON（结构化） | 自定义文本格式 |
| 批量/CI | 不适合 | 适合 |
| 实时交互 | 适合 | 不适合 |

## 输出格式

**MCP 模式**：`find_code_by_rule` 返回 JSON，包含 `file`、`range`、`text`、`metaVariables` 等字段。

**CLI 模式**：每行 `<文件绝对路径>:<行号>:<列号>\t<源代码行（折叠空白，截 300 字符）>`

示例：
```
src/Dao.cpp:42:13   sqlStr << "insert into T (a,b) values(1,2)";
src/Svc.java:108:25  String sql = "SELECT * FROM user WHERE id=" + id;
```

详见 `templates/output-schema.md`。

## 命令速查

| 场景 | MCP | CLI |
|------|-----|-----|
| Java 内嵌 SQL | `find_code_by_rule` + sql-string-java rule | 步骤 4c |
| C++ 内嵌 SQL | `find_code_by_rule` + sql-string-cpp rule | 步骤 4b |
| SQL 拼接点 | `find_code_by_rule` + sql-concat-java rule | `templates/recipes.md` |
| XML MyBatis SQL | 不支持，用 rg | 步骤 5 |
| 验证规则 | `test_match_code_rule` | `ast-grep --debug-query` |
| 调试 pattern | `dump_syntax_tree` | `ast-grep --debug-query=cst` |
| 增量分析 | `find_code_by_rule`（限定目录） | `templates/recipes.md` |
| 按 SQL 类型分类 | 修改 constraints.regex | `templates/recipes.md` |

## 陷阱与故障排除

详见 `templates/gotchas.md`。高频问题：

| 现象 | 原因 | 解决 |
|------|------|------|
| MCP 返回 0 结果 | constraints.regex 转义错误 | YAML 中 `\\b` 非 `\b` |
| MCP rule parse error | regex 写在 rule 而非 constraints 下 | 必须用 `constraints.SQL.regex` |
| CLI 结果为 0 行 | `.gitignore` 排除子目录 | 加 `--no-ignore vcs` |
| CLI jq parse error | 未指定 `--json=stream` | 显式 `--json=stream` |
| CLI jq syntax error | 命令行内联正则转义错 | 用 `-f /tmp/sql-filter.jq` |
| Broken pipe | jq 提前退出 | 正常现象，stderr 可忽略 |
| 包含 `gtest/` 噪声 | 未排除测试目录 | 加 `--globs '!**/gtest/**'` |

## 最佳实践

1. **MCP 优先**：AI Agent 场景下优先用 `find_code_by_rule`，避免 shell 转义和临时文件
2. **验证先行**：用 `test_match_code_rule` 验证规则后再全量搜索
3. **AST 优先**：能用 ast-grep 就不用 rg，AST 零误报
4. **范围分级**：先小范围试跑（如单模块），验证无误后再全量
5. **结果去重**：同一文件多行 SQL 拼接，需后处理合并（见 recipes）
6. **复核必做**：抽取后抽样核对，验证准确率
7. **统计画像**：输出文件分布 Top N，快速定位热点文件
8. **构建产物必排**：`build/` `target/` `out/` 含生成代码，会严重噪声
9. **CLI 兜底**：MCP 超时或 CI 场景回退 CLI 管道

## 适用与限制

**适用**：
- C/C++/Java/C#/Go/Python/Rust/Kotlin/Scala 等支持 ast-grep 的语言
- 字符串字面量形式的内嵌 SQL
- MyBatis 等 XML 配置文件（rg 兜底）

**不适用**：
- XML 语言（ast-grep 不支持，无论 MCP 还是 CLI）
- 字节码反编译场景（用 JD-GUI 等）
- ORM 框架的 Query Builder（需另外的 AST 模式）
- 存储过程/数据库内 SQL（用数据库字典查询）

**MCP 额外限制**：
- 超大型项目（>10k 文件）可能触发 MCP 超时，需回退 CLI
- `find_code_by_rule` 不支持 `--globs` 排除目录，需在项目范围上控制
- `max_results` 限制返回数量，大项目需分批

## 模板引用

| 模板文件 | 用途 |
|----------|------|
| `templates/jq-filter.jq` | SQL 过滤 jq 脚本（CLI 模式核心） |
| `templates/recipes.md` | 进阶命令配方（拼接点、增量、分类、MCP 版本） |
| `templates/output-schema.md` | 输出格式说明与示例 |
| `templates/gotchas.md` | 陷阱与故障排除详解 |

---

**技能版本**: 2.0.0
**核心工具**: ast-grep-mcp（首选）/ ast-grep 0.45+ + jq 1.6+（兜底）/ ripgrep 13+（XML）
**输出位置**: MCP JSON / `/tmp/sql_<lang>.lst`（CLI）
**典型耗时**: MCP 即时返回 / CLI: C++ 5k 文件 ≈ 1-2 分钟；Java 12k 文件 ≈ 3-5 分钟
