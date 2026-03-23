---
name: code-deconstruct
description: "读取所有源代码，解构为设计图，设计文档; 没有执行文件，请按流程执行"
---

# 源代码解构

1. 读取所有源代码，感知项目目的/意图/结构，以及代码之间关系
2. 定位若干核心类，生成主干类图，格式: `plantuml`，写入 `doc/deconstruct/classes_graph.puml`
3. 定位核心数据流，生成数据流图，格式: `plantuml` 和 `markdown+mermaid` 双格式，写入 `doc/deconstruct/core_data_flow.puml(md)`
4. 将代码结构分模块编写设计细节文档，格式: `markdown`，可辅以 `mermaid`，写入 `doc/deconstruct/design_{package}/design.md`
5. 汇总所有模块的设计细节后，写出全项目设计细节文档，格式: `markdown`，可辅以 `mermaid`，写入 `doc/deconstruct/global_design.md`
6. 将代码结构分模块编写需求文档，格式: `markdown`，可辅以 `mermaid`，写入 `doc/deconstruct/requirements_{package}/requirements.md`
7. 将源码实现的意图，提炼为需求`requirements`，格式: `markdown`，可辅以 `mermaid`，写入 `doc/deconstruct/global_requirements.md`

## 源代码类型

1. java: `*.java`
2. ansi c: `*.c/*.h`
3. cpp: `*.cpp/*.hpp/*.c/*.h`
4. javascript: `*.js/*.ts`
5. python: `*.py`
6. rust: `*.rs`

