# 测试框架与项目结构固化模板

> 此文件由 assets/test-framework-cache.md 模板生成。首次执行时，从项目 pom.xml 自动提取版本和模块信息，生成到 docs/test-framework-cache.md。

## 一、测试依赖版本（从父/子 pom.xml 中提取）

```
<!-- JUnit 5 -->
junit-jupiter-api: {JUNIT_VERSION}
junit-jupiter-engine: {JUNIT_VERSION}
junit-jupiter-params: {JUNIT_VERSION}

<!-- Mock -->
mockito-core: {MOCKITO_VERSION}
mockito-junit-jupiter: {MOCKITO_VERSION}

<!-- 断言 -->
assertj-core: {ASSERTJ_VERSION}

<!-- 覆盖率 -->
jacoco-maven-plugin: {JACOCO_VERSION}

<!-- Spring -->
spring-boot-starter-test: {SPRING_BOOT_VERSION}
spring-boot-starter-web: {SPRING_BOOT_VERSION}

<!-- 数据库 -->
h2: {H2_VERSION}

<!-- Maven -->
maven-surefire-plugin: {SUREFIRE_VERSION}
maven-compiler-plugin: {COMPILER_VERSION} (source/target {JAVA_VERSION})
```

## 二、各模块关键路径

<!-- 首次执行时，扫描项目根 pom.xml 的 <modules>，逐个模块提取信息 -->
<!-- 每个模块记录以下字段，格式如下： -->

### {模块名} 模块
- artifactId: {ARTIFACT_ID}
- parent relativePath: {PARENT_RELATIVE_PATH}
- 主类: {MAIN_CLASS 或 "无（lib模块）"}
- 主源码: {MAIN_SOURCE_PATH}
- 测试目录: {TEST_SOURCE_PATH}
- pom-test.xml: {已创建/未创建/已存在}
- {自定义依赖属性}: {值}  <!-- 例: dependency.erayt.beta 等，无则删除此行 -->

## 三、pom-test.xml 差异化字段

<!-- 首次执行时，根据项目 pom.xml 特点总结需要替换的字段 -->
创建新模块的 pom-test.xml 时，从原 pom.xml 中提取以下字段：

| 字段 | 说明 | 获取方式 |
|------|------|---------|
| `{ARTIFACT_ID}` | 模块 artifactId | 原 pom.xml 的 `<artifactId>` |
| `{PARENT_GROUP_ID}` | 父 POM groupId | 原 pom.xml 的 `<parent><groupId>` |
| `{PARENT_ARTIFACT_ID}` | 父 POM artifactId | 原 pom.xml 的 `<parent><artifactId>` |
| `{PARENT_VERSION}` | 父 POM version | 原 pom.xml 的 `<parent><version>` |
| `{PARENT_RELATIVE_PATH}` | 父POM相对路径 | 原 pom.xml 的 `<relativePath>` |
| `{MAIN_CLASS}` | Spring Boot 主类 | 原 pom.xml 的 mainClass，lib模块无此项 |
| `{ORIGINAL_DEPENDENCIES}` | 原有非测试依赖 | 原 pom.xml 的 `<dependencies>` 内容 |

## 四、JaCoCo 覆盖率配置（固定）

```xml
<jacoco.line.coverage>0.80</jacoco.line.coverage>
<jacoco.branch.coverage>0.60</jacoco.branch.coverage>
```

三个 execution: prepare-agent → report(test阶段) → check(verify阶段)

## 五、测试运行命令

```bash
cd {模块目录}
cp pom-test.xml pom.xml     # 替换正式 pom（注意备份）
mvn clean test               # 执行测试 + 生成覆盖率
mvn verify                   # 校验覆盖率是否达标
# 报告路径: target/site/jacoco/index.html
```
