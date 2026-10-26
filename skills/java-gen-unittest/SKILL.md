---
name: java-gen-unittest
description: "依据设计文档与代码生成 Java 单元测试，覆盖正常、边界与异常路径。适用于补充单元测试、提升覆盖率、验证修改行为。"
---

# 生成 Java 单元测试

## 适用场景

- 需要为既有代码补充单元测试
- 覆盖率不达标，需要定向补齐
- 修改代码前建立回归保护

## 前置条件

1. 确认项目测试框架与版本（JUnit 4/5、Mockito、AssertJ 等），以 `pom.xml` 为准。
2. 代码结构复杂时，先通过 skill `code-deconstruct` 理解模块与依赖关系。
3. 确认数据库、外部服务等依赖，决定使用 H2、Mock 还是测试替身。

## 执行步骤

1. 遍历目标包下的 Java 文件，梳理类的职责、公开方法与依赖。
2. 以 public 方法为主要目标，识别正常路径、边界条件与异常路径。
3. 对需要外部数据或远程调用的依赖使用 Mockito/PowerMock 隔离，保证测试可独立执行。
4. 涉及数据库时，优先在 test scope 引入 H2；无法使用 H2 时通过 Mock 模拟数据访问层。
5. 生成测试类，命名遵循 `{被测类}Test`，写入 `src/test/java` 对应 package。
6. 生成或更新测试套件，确保所有测试可一次执行。
7. 执行 `mvnd test` 或 `mvnd test -Dtest=XxxTest` 验证。

## 输出

- 测试代码：`src/test/java/{package}/{Class}Test.java`
- 测试套件：`src/test/java/{package}/AllTests.java`（或项目既有 suite）
- 覆盖率报告：`target/site/jacoco/index.html`（如已配置 JaCoCo）

## 核心原则

- 覆盖正常、边界、异常三类路径，不以行数覆盖代替分支覆盖。
- 测试必须可重复执行，不依赖执行顺序与外部环境。
- 断言聚焦行为与结果，不断言内部实现细节。
- 不修改生产代码以迁就测试；确需改动时遵循最小改动原则。

## 完成标准

- [ ] 目标类的 public 方法均有测试
- [ ] 正常、边界、异常路径均有覆盖
- [ ] 测试可独立、可重复执行
- [ ] `mvnd test` 全部通过
- [ ] 覆盖率数据已生成并记录
