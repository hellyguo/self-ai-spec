# 输出格式说明

## 文件格式

每行一条 SQL 命中，制表符分隔：

```
<file>:<line>:<column>\t<source_line>
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | string | 文件绝对路径（与传入 ast-grep 的根有关） |
| `line` | int | 1-based 行号（ast-grep 输出 0-based，jq 已 +1） |
| `column` | int | 1-based 列号（同上） |
| `source_line` | string | 源代码行原文，已折叠连续空白为单空格，截断至 300 字符 |

## 示例

### C++ 样例

输入：
```cpp
// src/Dao.cpp
std::stringstream ss;
ss << "insert into TQE_PS_DEALS (bankid, name) values ("
   << bankid << ", '" << name << "')";
```

输出：
```
/disk2/.../src/Dao.cpp:42:13	 ssStr << "insert into TQE_PS_DEALS (bankid, name) values ("
```

### Java 样例

输入：
```java
String sql = "SELECT * FROM user WHERE id = " + userId;
```

输出：
```
/.../src/UserService.java:25:25	 String sql = "SELECT * FROM user WHERE id = " + userId;
```

注意 Java 拼接的两段会**分别**命中：
```
/.../src/UserService.java:25:25	 String sql = "SELECT * FROM user WHERE id = " + userId;
/.../src/UserService.java:25:51	 String sql = "SELECT * FROM user WHERE id = " + userId;
```
（同一行，列号不同）。如需合并，参见 `recipes.md` 第 5 节。

## ast-grep JSON 原始结构

`--json=stream` 输出每行一个对象：

```json
{
  "text": "\"SELECT * FROM user\"",
  "range": {
    "byteOffset": { "start": 100, "end": 122 },
    "start": { "line": 24, "column": 24 },
    "end":   { "line": 24, "column": 46 }
  },
  "file": "/abs/path/Dao.java",
  "lines": "        String sql = \"SELECT * FROM user\";",
  "charCount": { "leading": 24, "trailing": 1 },
  "language": "Java"
}
```

字段用途：

| 字段 | 用途 |
|------|------|
| `text` | 字符串字面量原文（含引号），**正则过滤的目标** |
| `range.start.line/column` | 0-based 位置，输出时 +1 |
| `file` | 文件路径 |
| `lines` | 整行源码，便于人工复核 |
| `language` | 语言（Cpp/Java/...） |

## ast-grep 其他 JSON 样式

| 样式 | 用途 | 输出形式 |
|------|------|---------|
| `pretty`（默认） | 人工查看 | 缩进数组，jq 必须用 `[.[] | ...]` |
| `stream` | 流式管道 | NDJSON，每行一对象，**推荐** |

管道场景必须用 `stream`，否则 jq 会因首字符不是 `{`/`[` 而解析失败。

## 输出文件命名约定

| 文件 | 内容 |
|------|------|
| `/tmp/sql_cpp.lst` | C++ 内嵌 SQL |
| `/tmp/sql_java.lst` | Java 内嵌 SQL（含 XML 兜底） |
| `/tmp/sql_<lang>.lst` | 其他语言 |
| `/tmp/sql_*.err` | jq 错误输出 |
| `/tmp/sql_*.ast.err` | ast-grep 错误输出 |

## 统计画像示例

```
===== C++ (/tmp/sql_cpp.lst) =====
1384 /tmp/sql_cpp.lst
唯一文件数: 226

===== 文件分布 Top 10 =====
    107 QES3/src/pos/checkiosvr/MainAction.cpp
     96 QES3/src/pos/psmansvr/DealAction.cpp
     ...
```

命令见 `SKILL.md` 步骤 6。
