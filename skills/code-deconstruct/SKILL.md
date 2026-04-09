---
name: code-deconstruct
description: "读取所有源代码，解构为设计图，设计文档; 没有执行文件，请按流程执行"
---

# 源代码解构

## 代码解构流程

1. 读取所有源代码，感知项目目的/意图/结构，以及代码之间关系
2. 定位若干核心类，生成主干类图，格式: `plantuml`，写入 `docs/deconstruct/classes_graph.puml`
3. 定位核心数据流，生成数据流图，格式: `plantuml` 和 `markdown+mermaid` 双格式，写入 `docs/deconstruct/core_data_flow.puml(md)`
4. 将代码结构分模块编写设计细节文档，格式: `markdown`，可辅以 `mermaid`，写入 `docs/deconstruct/design_{package}/design.md`
5. 汇总所有模块的设计细节后，写出全项目设计细节文档，格式: `markdown`，可辅以 `mermaid`，写入 `docs/deconstruct/global_design.md`
6. 将代码结构分模块编写需求文档，格式: `markdown`，可辅以 `mermaid`，写入 `docs/deconstruct/requirements_{package}/requirements.md`
7. 将源码实现的意图，提炼为需求`requirements`，格式: `markdown`，可辅以 `mermaid`，写入 `docs/deconstruct/global_requirements.md`

## 数据库解构流程

### 1. 扫描数据库相关文件

扫描以下文件类型：
- SQL 文件：`*.sql`
- iBATIS 映射文件：`**/sqlmap*.xml`、`**/*SqlMap.xml`
- MyBatis 映射文件：`**/*Mapper.xml`、`**/*map.xml`

### 2. 构建数据库详细清单

生成数据库清单文档，写入 `docs/deconstruct/database/` 目录：

```
docs/deconstruct/database/
├── database_inventory.md    # 数据库清单总览
├── tables/                   # 表结构详情
│   ├── table_{table_name}.md
│   └── ...
├── indexes/                  # 索引清单
│   └── indexes.md
└── constraints/              # 约束清单
    └── constraints.md
```

清单内容包括：
- 数据库基本信息（名称、字符集、排序规则）
- 表清单（表名、注释、记录数估算）
- 字段清单（字段名、类型、长度、是否可空、默认值、注释）
- 索引清单（索引名、表名、字段、类型）
- 外键约束清单

### 3. 构建 ER 图

生成实体关系图，双格式输出：
- PlantUML 格式：`docs/deconstruct/database/er_diagram.puml`
- Markdown+Mermaid 格式：`docs/deconstruct/database/er_diagram.md`

ER 图要求：
- 展示所有表及其字段
- 标注主键、外键关系
- 显示一对一、一对多、多对多关系
- 使用中文注释表名和字段名

### 4. 数据库设计思路摘要

生成数据库设计文档，写入 `docs/deconstruct/database/database_design.md`，包括：

- **设计思路**：整体数据库设计理念、范式遵循情况
- **典型数据类型**：
  - 主键设计（自增/UUID/雪花算法等）
  - 时间字段类型（DATE/DATETIME/TIMESTAMP）
  - 大文本字段（TEXT/CLOB/JSON）
  - 金额字段（DECIMAL 精度设计）
  - 枚举字段（ENUM/字典表）
- **命名规范**：表名、字段名命名风格
- **分库分表策略**：如有
- **数据迁移历史**：从 Flyway/Liquibase 脚本推断

## 源代码类型

- java: `*.java`
- ansi c: `*.c/*.h`
- cpp: `*.cpp/*.hpp/*.c/*.h`
- javascript: `*.js/*.ts`
- python: `*.py`
- rust: `*.rs`
- sql: `*.sql`
- script: `*.sh/*.bat/*.cmd`

## 输出目录结构

```
docs/deconstruct/
├── classes_graph.puml           # 主干类图
├── core_data_flow.puml          # 数据流图
├── core_data_flow.md            # 数据流图
├── global_design.md             # 全局设计文档
├── global_requirements.md       # 全局需求文档
├── database/                    # 数据库解构输出
│   ├── database_inventory.md    # 数据库清单
│   ├── er_diagram.puml          # ER图
│   ├── er_diagram.md            # ER图
│   ├── database_design.md       # 数据库设计思路
│   ├── tables/                  # 表结构详情
│   ├── indexes/                 # 索引清单
│   └── constraints/             # 约束清单
├── design_{package}/            # 分模块设计文档
│   └── design.md
└── requirements_{package}/      # 分模块需求文档
    └── requirements.md
```

