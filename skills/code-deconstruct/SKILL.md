---
name: code-deconstruct
description: "读取所有源代码，解构为设计图、设计文档、数据库设计; 没有执行文件，请按流程执行"
---

# 源代码解构（设计）

<HARD-GATE>
完整全面，不遗漏细节。
</HARD-GATE>

## 代码解构流程

1. 读取所有源代码，感知项目目的/意图/结构，以及代码之间关系
2. 定位若干核心类，生成主干类图 `docs/deconstruct/classes_graph.puml`
3. 定位核心数据流，生成数据流图 `docs/deconstruct/core_data_flow.puml(md)`
4. 将代码结构分模块编写设计细节文档 `docs/deconstruct/design_{package}/design.md`
5. 分析内存使用代价、探测是否存在内存泄漏 `docs/deconstruct/memory_usage.md`
6. 对核心算法、数据结构，生成算法文档 `docs/deconstruct/algorithm_{package}/algorithm.md`
7. 对重要的架构设计，总结归纳 `docs/deconstruct/arch_design_summary.md`
8. 汇总所有模块的设计细节后，写出全项目设计细节文档 `docs/deconstruct/global_design.md`

### 模块定义

- Java: `package`，如有 maven module，需识别为 `{module}-{package}`
- Python: `package`/`module`
- Ansi C/C++: Makefile target/CMakeLists.txt target
- JS: `module`
- Rust: `mod`，如有 cargo workspace，需识别为 `{member}-{mod}`

## 数据库解构流程

1. 扫描 SQL 文件、MyBatis/iBATIS 映射文件、代码内嵌 SQL
2. 生成数据库清单 `docs/deconstruct/database/database_inventory.md`
3. 构建 ER 图 `docs/deconstruct/database/er_diagram.puml(md)`
4. 生成数据库设计思路摘要 `docs/deconstruct/database/database_design.md`

### SQL 提取规则

- MyBatis: 从 `<sql>` `<select>` `<insert>` `<update>` `<delete>` 标签提取
- Java注解: 从 `@Query` `@NamedQuery` 注解提取
- 字符串: 正则匹配 `(SELECT|INSERT|UPDATE|DELETE)\s+` 开头的字符串

## 内存使用分析

识别内存热点：大对象创建、集合操作、字符串处理、字节数组、流处理、缓存对象

探测内存泄漏：静态集合增长、ThreadLocal未清理、监听器未注销、连接未关闭、缓存无过期

模板: `templates/memory_usage.md`

## 中间件消息追踪

识别中间件：xnet、webnet、TDMQ、RabbitMQ、IBMMQ、RocketMQ、Kafka

扫描：配置文件、注解配置、编程式API、硬编码字符串

模板: `templates/middleware_tracing.md`

## 网络估算

识别通信类型：HTTP API、RPC调用、消息队列、数据库连接、文件传输、WebSocket、缓存同步

估算维度：请求大小、响应大小、并发请求、上行/下行流量、总带宽

模板: `templates/network_usage.md`

## 算法分析

识别算法类型：搜索、排序、加密、压缩、编码、校验、计算、匹配、路径、分配

识别数据结构：数组/列表、链表、树结构、图结构、哈希表、队列、栈、堆、位图、缓存

模板: `templates/algorithm.md`

## 架构设计总结

识别架构模式：分层架构、MVC架构、微服务架构、事件驱动、管道过滤、插件架构、代理架构、适配器架构、工厂架构、单例架构

识别设计模式：策略、工厂、观察者、装饰器、适配器、代理、模板方法、命令、责任链、状态

模板: `templates/arch_design_summary.md`

## 输出目录结构

```text
docs/deconstruct/
├── classes_graph.puml
├── core_data_flow.puml
├── core_data_flow.md
├── global_design.md
├── memory_usage.md
├── network_usage.md
├── arch_design_summary.md
├── database/
│   ├── database_inventory.md
│   ├── er_diagram.puml
│   ├── er_diagram.md
│   ├── database_design.md
│   ├── tables/
│   ├── indexes/
│   └── constraints/
├── design_{package}/
│   └── design.md
└── algorithm_{package}/
    └── algorithm.md
```

## 关联技能

需求收集请使用技能：`requirement-collect`
