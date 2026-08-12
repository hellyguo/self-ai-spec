# Kotlin 构建工具

首选 Gradle + Kotlin DSL（`build.gradle.kts`），次选 Maven

相关工具路径，见 skill /java-env（Kotlin 运行于 JVM，依赖 JDK 环境）

## 构建/测试命令

```bash
# 编译项目
./gradlew compileKotlin

# 编译并运行所有测试
./gradlew test

# 运行单个测试类
./gradlew test --tests "com.example.UserServiceTest"

# 运行单个测试方法
./gradlew test --tests "com.example.UserServiceTest.login 失败时返回错误码"

# 打包（跳过测试）
./gradlew build -x test

# 清理并编译
./gradlew clean compileKotlin

# 完整构建流程
./gradlew clean test build

# 静态分析
./gradlew detekt                 # detekt 质量检查
./gradlew ktlintCheck            # ktlint 风格检查

# 测试覆盖率
./gradlew koverReport            # Kover 覆盖率报告
```

## 常用配置

```kotlin
// build.gradle.kts 示例片段
plugins {
    kotlin("jvm") version "2.0.0"
}

kotlin {
    jvmToolchain(17)
    compilerOptions {
        allWarningsAsErrors = true
        freeCompilerArgs.add("-Xjsr305=strict")
    }
}

dependencies {
    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:1.13.10")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
}
```

## 版本管理

- 依赖版本统一集中在 `gradle/libs.versions.toml`（Version Catalog）管理
- 避免散落硬编码版本号
