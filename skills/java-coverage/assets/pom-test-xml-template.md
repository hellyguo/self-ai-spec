# pom-test.xml 模板

> 创建新模块的 pom-test.xml 时，复制模板后只替换 {占位符} 部分。
> 此文件由 assets/pom-test-xml-template.md 生成到 docs/pom-test-xml-template.md。
> 首次执行时，将项目特定的父 POM 信息、自定义属性等填充到占位符中。

## 差异化字段清单

创建 pom-test.xml 时，从原 pom.xml 中提取以下字段填入：

| 占位符 | 说明 | 获取方式 |
|--------|------|---------|
| `{ARTIFACT_ID}` | 模块 artifactId | 原 pom.xml 的 `<artifactId>` |
| `{PARENT_GROUP_ID}` | 父 POM groupId | 原 pom.xml 的 `<parent><groupId>` |
| `{PARENT_ARTIFACT_ID}` | 父 POM artifactId | 原 pom.xml 的 `<parent><artifactId>` |
| `{PARENT_VERSION}` | 父 POM version | 原 pom.xml 的 `<parent><version>` |
| `{PARENT_RELATIVE_PATH}` | 父POM相对路径 | 原 pom.xml 的 `<relativePath>` |
| `{MAIN_CLASS}` | Spring Boot 主类 | 原 pom.xml 的 mainClass，lib模块无此项 |
| `{ORIGINAL_DEPENDENCIES}` | 原有非测试依赖 | 原 pom.xml 的 `<dependencies>` 内容 |
| `{ORIGINAL_RESOURCES}` | 原有 resources 配置 | 原 pom.xml 的 `<build><resources>` 内容 |
| `{ORIGINAL_NON_TEST_PLUGINS}` | 原有非测试 plugins | 原 pom.xml 的 `<build><plugins>` 内容 |
| `{CUSTOM_PROPERTIES}` | 项目自定义 properties | 原 pom.xml 的 `<properties>` 中非标准字段 |

## 快速创建命令

```bash
# 1. 读取原 pom.xml 的关键字段
# 2. 填充模板
# 3. 输出到 pom-test.xml
```

## 完整模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">

    <parent>
        <groupId>{PARENT_GROUP_ID}</groupId>
        <artifactId>{PARENT_ARTIFACT_ID}</artifactId>
        <version>{PARENT_VERSION}</version>
        <relativePath>{PARENT_RELATIVE_PATH}</relativePath>
    </parent>

    <modelVersion>4.0.0</modelVersion>
    <artifactId>{ARTIFACT_ID}</artifactId>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <maven.compiler.encoding>UTF-8</maven.compiler.encoding>
        {CUSTOM_PROPERTIES}
        <!-- JaCoCo配置 -->
        <jacoco.line.coverage>0.80</jacoco.line.coverage>
        <jacoco.branch.coverage>0.60</jacoco.branch.coverage>
    </properties>

    <dependencies>
        <!-- 原有非测试依赖 - 直接从原 pom.xml 复制 -->
        {ORIGINAL_DEPENDENCIES}

        <!-- 测试依赖（固定，不需要修改） -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <version>{JUNIT_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>{JUNIT_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-params</artifactId>
            <version>{JUNIT_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>{MOCKITO_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <version>{MOCKITO_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <version>{H2_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <version>{SPRING_BOOT_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>{SPRING_BOOT_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <version>{ASSERTJ_VERSION}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>{JACOCO_VERSION}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <!-- ============================================ -->
    <!-- 可选依赖：集成测试（按需添加）              -->
    <!-- ============================================ -->
    <!-- 当模块中存在分类 C/D/E 的方法时，取消以下注释 -->
    <!--
    <dependencies>
        <dependency>
            <groupId>org.powermock</groupId>
            <artifactId>powermock-module-junit5</artifactId>
            <version>2.0.9</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.powermock</groupId>
            <artifactId>powermock-api-mockito2</artifactId>
            <version>2.0.9</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    -->

    <build>
        <testResources>
            <testResource>
                <directory>src/test/resources</directory>
                <excludes>
                    <exclude>target/**</exclude>
                    <exclude>pom-test.xml</exclude>
                </excludes>
            </testResource>
        </testResources>
        <resources>
            <!-- 从原 pom.xml 复制 resources 配置 -->
            {ORIGINAL_RESOURCES}
            <resource>
                <filtering>false</filtering>
                <directory>src/test/resources</directory>
                <excludes>
                    <exclude>target/**</exclude>
                    <exclude>**/surefire-reports/**</exclude>
                    <exclude>**/jacoco/**</exclude>
                </excludes>
            </resource>
        </resources>

        <plugins>
            <!-- 从原 pom.xml 复制非测试 plugins -->
            {ORIGINAL_NON_TEST_PLUGINS}

            <!-- Maven Surefire - JUnit 5（固定） -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>{SUREFIRE_VERSION}</version>
                <configuration>
                    <useSystemClassLoader>false</useSystemClassLoader>
                </configuration>
            </plugin>

            <!-- JaCoCo（固定） -->
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>{JACOCO_VERSION}</version>
                <executions>
                    <execution>
                        <id>prepare-agent</id>
                        <goals><goal>prepare-agent</goal></goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals><goal>report</goal></goals>
                    </execution>
                    <execution>
                        <id>check</id>
                        <phase>verify</phase>
                        <goals><goal>check</goal></goals>
                        <configuration>
                            <rules>
                                <rule>
                                    <element>BUNDLE</element>
                                    <limits>
                                        <limit>
                                            <counter>LINE</counter>
                                            <value>COVEREDRATIO</value>
                                            <minimum>${jacoco.line.coverage}</minimum>
                                        </limit>
                                        <limit>
                                            <counter>BRANCH</counter>
                                            <value>COVEREDRATIO</value>
                                            <minimum>${jacoco.branch.coverage}</minimum>
                                        </limit>
                                    </limits>
                                </rule>
                            </rules>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```
