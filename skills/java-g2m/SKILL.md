---
name: java-g2m
description: "将 Gradle 构建迁移为 Maven 构建，包括依赖、插件、目录结构与构建命令的等价转换。适用于 Gradle 转 Maven 的构建体系迁移。"
---

# Gradle 转 Maven

## 适用场景

- 项目构建体系需要从 Gradle 统一到 Maven
- 已有项目需要接入只支持 Maven 的 CI 或制品流程

## 前置条件

1. 通过 skill `java-env` 确认 JDK 与 mvnd/mvn 版本。
2. 阅读 `build.gradle` / `build.gradle.kts`、`settings.gradle`、`gradle.properties` 与 `gradle/libs.versions.toml`。
3. 确认多模块结构与模块间依赖关系。

## 迁移要求

1. 保持 JDK 要求不变；除非用户明确要求切换 JDK。
2. 所有依赖必须完整迁移到 `pom.xml`，不重不漏，作用域（compile/provided/runtime/test）与原构建一致。
3. Gradle 特有任务尽可能等价迁移为 Maven 插件或 profile；无法迁移的，在输出中列出任务清单、原因与替代方案。
4. 多模块项目使用 Maven 聚合与继承结构，模块坐标、依赖关系与原结构一致。
5. 版本号统一由 `dependencyManagement` 或 parent 管理，避免散落。

## 执行步骤

1. 盘点 Gradle 结构：模块、插件、依赖、仓库、属性、任务。
2. 生成或改写 `pom.xml`：parent、modules、properties、dependencyManagement、dependencies、build。
3. 迁移资源过滤、打包配置、测试配置与编码设置。
4. 逐模块执行 `mvnd -q -DskipTests compile`，修正依赖与插件差异。
5. 执行 `mvnd test`，确认测试全部通过。
6. 对比迁移前后构建产物与依赖树（`mvnd dependency:tree`）。

## 输出物

- 迁移后的 `pom.xml`（含多模块）。
- 迁移说明：依赖映射、插件映射、未能迁移的任务清单。
- 验证记录：编译、测试、依赖树对比结果。

## 完成标准

- [ ] 所有模块可编译
- [ ] 所有测试通过
- [ ] 依赖无缺失、无重复、作用域正确
- [ ] 未能迁移的 Gradle 任务已列出并有替代方案
