---
name: java-check-spotbugs
description: "SpotBugs静态分析技能：使用SpotBugs、Find Security Bugs、fb-contrib进行Java代码缺陷和安全分析"
---

# SpotBugs Java静态分析技能

## 版本兼容性

- **SpotBugs 4.7.3**：最高支持Java 17（class文件major version 61）
- **Java 25不兼容**，需使用Java 17或更早版本运行分析

```bash
java -version
javap -verbose target/classes/com/example/Test.class | grep major
```

## 工具位置

```bash
SPOTBUGS_HOME=~/app/spotbugs-4.7.3
SPOTBUGS_JAR=$SPOTBUGS_HOME/lib/spotbugs.jar
FIND_SEC_BUGS_SRC=/home/helly/open_source/github/find-sec-bugs/
FB_CONTRIB_SRC=/home/helly/open_source/github/fb-contrib/
```

## 执行流程

### 步骤1：准备字节码

```bash
mvn compile          # Maven
gradle classes       # Gradle
javac -d target/classes src/*.java  # 手动
```

### 步骤2：执行分析

```bash
# 基础分析
java -jar $SPOTBUGS_JAR -textui -output spotbugs-basic.txt target/classes/

# 含安全检测
java -jar $SPOTBUGS_JAR -textui -output spotbugs-security.txt \
  -pluginList $FIND_SEC_BUGS_JAR target/classes/

# 完整分析（所有插件）
java -jar $SPOTBUGS_JAR -textui -output spotbugs-full.txt \
  -pluginList $FIND_SEC_BUGS_JAR:$FB_CONTRIB_JAR target/classes/
```

### 步骤3：特定检测器

```bash
# 仅安全漏洞
java -jar $SPOTBUGS_JAR -textui -output security-only.txt \
  -pluginList $FIND_SEC_BUGS_JAR -onlyAnalyze ".*Security.*" target/classes/

# 性能和资源问题
java -jar $SPOTBUGS_JAR -textui -output performance.txt \
  -effort:max -visitors "FindDeadLocalStores,FindUnconditionalWait,FindReturnRef" target/classes/
```

### 步骤4：生成报告

使用模板 `templates/report.md` 输出分析报告。

## 配置与过滤

使用模板 `templates/filter.xml` 自定义过滤器：

```bash
java -jar $SPOTBUGS_JAR -textui -output filtered.txt \
  -exclude filter.xml target/classes/
```

## 输出格式

| 格式 | 命令参数 | 用途 |
|------|----------|------|
| 文本 | `-textui` | 默认，终端查看 |
| XML | `-xml` | CI集成 |
| HTML | `-html` | 可视化报告 |

## 检测器分类

| 插件 | 主要检测 | 典型Pattern |
|------|----------|-------------|
| SpotBugs核心 | 空指针、资源泄漏、并发、性能 | IC_SUPERCLASS_USES_SUBCLASS |
| Find Security Bugs | SQL注入、XSS、命令注入 | SQL_INJECTION, COMMAND_INJECTION |
| fb-contrib | 代码坏味道、命名规范 | LOOP_CAN_BE_WHILE |

## 常用命令

| 场景 | 命令 |
|------|------|
| 查看所有检测器 | `java -jar $SPOTBUGS_JAR -textui -list` |
| 分析特定类 | `java -jar $SPOTBUGS_JAR -textui -onlyAnalyze "com.example.security.*" target/classes/` |
| 低阈值（更多问题） | `java -jar $SPOTBUGS_JAR -textui -low target/classes/` |
| 高阈值（仅严重） | `java -jar $SPOTBUGS_JAR -textui -high target/classes/` |

## CI/CD集成

### Maven

```xml
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <version>4.7.3.0</version>
  <configuration>
    <effort>Max</effort>
    <threshold>Low</threshold>
  </configuration>
</plugin>
```

### Gradle

```groovy
plugins {
  id "com.github.spotbugs" version "5.0.14"
}
spotbugs {
  toolVersion = '4.7.3'
  effort = 'max'
  reportLevel = 'low'
}
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| Unsupported class file major version | 使用Java 17或更早版本 |
| ClassNotFoundException | 检查类路径 |
| No classes specified | 确认编译后字节码存在 |
| 插件加载失败 | 检查插件JAR路径和版本 |

版本兼容性解决：

```bash
export JAVA_HOME=/path/to/java17
java -jar $SPOTBUGS_JAR -textui target/classes/
```

---

**技能版本**: 1.0.0
**工具版本**: SpotBugs 4.7.3 + Find Security Bugs + fb-contrib
**适用项目**: Java 17及以下版本项目
