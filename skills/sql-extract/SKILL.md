---
name: sql-extract
description: "SQL抽取技能：从C++/Java/XML源代码中抽取内嵌SQL语句，使用ast-grep(AST精准匹配)+jq(流式过滤)+ripgrep(兜底)组合方案，识别SQL拼接点，输出文件清单"
---

# SQL 抽取技能

从源代码中**精准抽取**内嵌 SQL 语句，识别 SQL 拼接点，输出位置清单与统计。

适用场景：
- 代码审查前的 SQL 注入风险点盘点
- 慢 SQL 优化的候选 SQL 收集
- 数据库迁移时的全量 SQL 走查
- 重构时的 SQL 集中化（迁移到 DAO/Mapper 层）

## 核心思路

**两层方案，互补使用**：

1. **主层（AST 精准）**：`ast-grep` 提取字符串字面量节点 → `jq` 正则过滤含 SQL 关键字的字面量
   - 优势：基于 AST，不受注释/字符串拼接/转义干扰，零误报
   - 适用：C++/Java 内嵌 SQL
2. **兜底层（正则）**：`ripgrep`/`grep` 直接扫描文本
   - 优势：支持 XML（ast-grep 不支持 XML 语言）
   - 适用：MyBatis mapper.xml、配置文件、其他语言

## 工具依赖

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

### 步骤 2：编写过滤脚本

将 jq 过滤脚本保存到文件，**避免 shell 转义陷阱**：

```bash
# 复用模板
cp templates/jq-filter.jq /tmp/sql-filter.jq
```

模板详情见 `templates/jq-filter.jq`。**禁止在命令行内联复杂正则**。

### 步骤 3：抽取 C++ 内嵌 SQL

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

**关键参数**：
- `--kind string_literal`：tree-sitter cpp 的字符串字面量节点名
- `--json=stream`：NDJSON 流式输出（每行一个 JSON 对象）
- `--no-ignore vcs`：忽略 `.gitignore`（项目根 .gitignore 常排除子模块）
- `--globs '!pattern'`：排除目录

### 步骤 4：抽取 Java 内嵌 SQL

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

Java 字符串拼接（`"select" + var + "from t"`）会按片段匹配，每个片段独立输出。如需识别拼接点，参见 `templates/recipes.md` 的「拼接点识别」。

### 步骤 5：抽取 XML 内嵌 SQL

ast-grep **不支持** XML 语言，必须用 ripgrep：

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

抽样核对 10 处命中与 5 处未命中的字符串字面量：

```bash
head -10 /tmp/sql_cpp.lst                          # 命中样本
ast-grep run -l cpp --kind string_literal <file>   # 全量字面量对照
```

## 输出格式

每行：`<文件绝对路径>:<行号>:<列号>\t<源代码行（折叠空白，截 300 字符）>`

示例：
```
src/Dao.cpp:42:13   sqlStr << "insert into T (a,b) values(1,2)";
src/Svc.java:108:25  String sql = "SELECT * FROM user WHERE id=" + id;
```

详见 `templates/output-schema.md`。

## 命令速查

| 场景 | 命令 |
|------|------|
| C++ 内嵌 SQL | 见步骤 3 |
| Java 内嵌 SQL | 见步骤 4 |
| XML MyBatis SQL | 见步骤 5 |
| 仅统计拼接点 | `templates/recipes.md` |
| 增量分析（git diff） | `templates/recipes.md` |
| 按 SQL 类型分类 | `templates/recipes.md` |

## 参数详解

### ast-grep 关键参数

| 参数 | 作用 | 必备 |
|------|------|------|
| `-l, --lang <LANG>` | 指定语言（cpp/java/csharp/go...） | 是 |
| `-k, --kind <KIND>` | AST 节点 kind（`string_literal`） | 是 |
| `--json=stream` | NDJSON 流式输出 | 是 |
| `--no-ignore vcs` | 忽略 `.gitignore` | 视项目而定 |
| `--globs '!pat'` | 排除路径 | 推荐 |
| `-p, --pattern` | AST 模式（与 `--kind` 互斥） | 否 |

### 各语言 string_literal kind

| 语言 | lang | kind |
|------|------|------|
| C/C++ | `cpp` | `string_literal` |
| Java | `java` | `string_literal` |
| C# | `csharp` | `string_literal` 或 `verbatim_string_literal`（需 `--kind` 多次匹配） |
| Go | `go` | `interpreted_string_literal` / `raw_string_literal` |
| Python | `python` | `string` |

新语言先验证：`echo '<sample>' > /tmp/t.<ext> && ast-grep run -l <lang> --kind string_literal /tmp/t.<ext>`。

## 陷阱与故障排除

详见 `templates/gotchas.md`。高频问题：

| 现象 | 原因 | 解决 |
|------|------|------|
| 结果为 0 行 | `.gitignore` 排除子目录 | 加 `--no-ignore vcs` |
| jq parse error | 未指定 `--json=stream` | 显式 `--json=stream` |
| jq syntax error | 命令行内联正则转义错 | 用 `-f /tmp/sql-filter.jq` |
| Broken pipe | jq 提前退出 | 正常现象，stderr 可忽略 |
| 包含 `gtest/` 噪声 | 未排除测试目录 | 加 `--globs '!**/gtest/**'` |

## 最佳实践

1. **AST 优先**：能用 ast-grep 就不用 rg，AST 零误报
2. **脚本化过滤**：jq 过滤脚本独立成文件，便于版本管理与迭代
3. **范围分级**：先小范围试跑（如单模块），验证无误后再全量
4. **结果去重**：同一文件多行 SQL 拼接，需后处理合并（见 recipes）
5. **复核必做**：抽取后抽样核对，验证准确率
6. **统计画像**：输出文件分布 Top N，快速定位热点文件
7. **构建产物必排**：`build/` `target/` `out/` 含生成代码，会严重噪声

## 适用与限制

**适用**：
- C/C++/Java/C#/Go/Python/Rust 等支持 ast-grep 的语言
- 字符串字面量形式的内嵌 SQL
- MyBatis 等 XML 配置文件

**不适用**：
- 字节码反编译场景（用 JD-GUI 等）
- ORM 框架的 Query Builder（需另外的 AST 模式）
- 存储过程/数据库内 SQL（用数据库字典查询）

## 模板引用

| 模板文件 | 用途 |
|----------|------|
| `templates/jq-filter.jq` | SQL 过滤 jq 脚本（核心） |
| `templates/recipes.md` | 进阶命令配方（拼接点、增量、分类） |
| `templates/output-schema.md` | 输出格式说明与示例 |
| `templates/gotchas.md` | 陷阱与故障排除详解 |

---

**技能版本**: 1.0.0
**核心工具**: ast-grep 0.45+ / jq 1.6+ / ripgrep 13+
**输出位置**: `/tmp/sql_<lang>.lst`
**典型耗时**: C++ 5k 文件 ≈ 1-2 分钟；Java 12k 文件 ≈ 3-5 分钟
