# 项目记忆文件

> 此文件由 assets/MEMORY.md 模板生成。首次执行增量测试时，自动探索项目信息并填充下方占位符，生成到 MEMORY.md。

## 项目基本信息
- **项目名称**: {PROJECT_NAME}
- **技术栈**: {TECH_STACK}  <!-- 例: Java 8 + Spring Boot 2.1.7.RELEASE -->
- **构建工具**: {BUILD_TOOL}  <!-- 例: Maven, 父 POM: xxx-parent -->
- **版本号规则**: {VERSION_PATTERN}  <!-- 例: 1.0.0-SNAPSHOT -->
- **项目根路径**: {PROJECT_ROOT_PATH}

## 项目模块结构
<!-- 首次执行时，扫描 pom.xml 的 <modules> 自动填入 -->
<!-- 格式: - **{模块名}** ({artifactId}) - {描述}，主类: {MainClass}(如有) -->
- **{MODULE_1}** ({ARTIFACT_ID_1}) - {描述}
- **{MODULE_2}** ({ARTIFACT_ID_2}) - {描述}

## 测试框架（首次探索后固化）
<!-- 首次执行时，从父 pom.xml 和子模块 pom.xml 中扫描依赖版本 -->
- JUnit Jupiter: {JUNIT_VERSION}
- Mockito: {MOCKITO_VERSION} + MockitoExtension
- AssertJ: {ASSERTJ_VERSION}
- Spring Boot Test: {SPRING_BOOT_VERSION}
- JaCoCo: {JACOCO_VERSION} (行覆盖率>=80%, 分支覆盖率>=60%)
- H2: {H2_VERSION} (内存数据库)
- Maven Surefire: {SUREFIRE_VERSION}
- **测试 POM 模式**: {TEST_POM_MODE}  <!-- 例: 使用 pom-test.xml 替换 / 或直接在 pom.xml 中配置 -->

## 测试目录现状
<!-- 首次执行时，扫描各模块 src/test/ 目录 -->
<!-- 格式: - {模块名} 模块: {状态描述} -->
- {MODULE_1}: {有/无}测试 (X个文件, pom-test.xml {已/未}创建)
- {MODULE_2}: {有/无}测试

## 测试代码风格（首次探索后固化）
<!-- 根据项目 Java 版本自动确定 -->
- 使用 @ExtendWith(MockitoExtension.class)，不启动 Spring 容器
- @DisplayName 中文描述
- @Nested 按方法分组
- @ParameterizedTest + @CsvSource/@ValueSource 用于枚举和多值场景
- Given-When-Then 注释风格
- Domain 对象用纯 JUnit 5（无 Mock）
- Service 用 Mockito Mock 依赖
- **Java 版本约束**: {JAVA_VERSION}  <!-- 例: Java 8 不用 var、List.of() -->

## 增量测试固化文件索引
详细固化内容存放在以下文件中：
- [测试框架与项目结构](./test-framework-cache.md) - 测试依赖版本、模块结构
- [测试代码模板](./test-code-templates.md) - 各层测试代码模板
- [pom-test.xml 模板](./pom-test-xml-template.md) - 测试 POM 模板
- [HTML报告模板](./html-report-template.md) - 报告模板结构说明

## 用户偏好
- 只需一种最优方案，不需要多方案对比
- 报告必须是 HTML 格式，不要 MD 格式
- 不要执行 git add / git commit
- 不要删除原代码注释
- 不要对源代码进行任何的修改，只允许修改自己新增的文件
- 用中文回复
