---
name: java-env
description: "提供本机 Java 开发环境信息：JDK、mvnd/mvn 路径与版本、环境变量与别名。适用于编译、运行、性能分析前确认 Java 环境。"
---

# Java 环境信息

本机 Java 工具链的查找路径与版本切换方式。工具路径为机器事实，迁移到其他机器时以实际探测结果为准。

## JDK 查找路径

| 范围 | 路径 | 说明 |
|------|------|------|
| 系统 | `/usr/lib/jvm` | 系统安装的多个 JDK |
| 用户 | `${HOME}/lang` | 用户自装的多个 JDK |

## 构建工具路径

| 工具 | 路径 | 优先级 |
|------|------|--------|
| mvnd | `${HOME}/app/maven-mvnd` | 首选 |
| mvn | `${HOME}/app/apache-maven` | 次选 |

## 环境确认

```bash
# 加载 shell 配置以获取 alias 与 JAVA_HOME
source ~/.bashrc

# 查看 Java 相关环境变量
env | grep JAVA

# 查看 Java 相关 alias
alias | grep java

# 查看可用 JDK
ls /usr/lib/jvm
ls "${HOME}/lang"
```

## 版本选择原则

1. 以项目 `pom.xml` 的 `maven.compiler.*`、`java.version` 或 toolchain 配置为准选择 JDK。
2. 构建优先使用 mvnd，mvnd 不可用时回退 mvn。
3. 同一任务内不得混用不同 JDK 版本；编译、测试、性能分析必须使用同一版本。

## 版本切换别名

以下别名依赖预先导出的 `JAVA_HOME*` 与 `NOJAVA_HOME_PATH`：

```bash
java7='JAVA_HOME=$JAVA_HOME7 PATH=$JAVA_HOME7/bin:$NOJAVA_HOME_PATH java'
java8='JAVA_HOME=$JAVA_HOME8 PATH=$JAVA_HOME8/bin:$NOJAVA_HOME_PATH java'
java11='JAVA_HOME=$JAVA_HOME11 PATH=$JAVA_HOME11/bin:$NOJAVA_HOME_PATH java'
java17='JAVA_HOME=$JAVA_HOME17 PATH=$JAVA_HOME17/bin:$NOJAVA_HOME_PATH java'
java21='JAVA_HOME=$JAVA_HOME21 PATH=$JAVA_HOME21/bin:$NOJAVA_HOME_PATH java'
java23='JAVA_HOME=$JAVA_HOME23 PATH=$JAVA_HOME23/bin:$NOJAVA_HOME_PATH java'
java25='JAVA_HOME=$JAVA_HOME25 PATH=$JAVA_HOME25/bin:$NOJAVA_HOME_PATH java'
```

## 诊断与分析工具路径

工具路径为机器事实，迁移到其他环境时以实际探测结果为准。

| 工具 | 路径 | 用途 |
|------|------|------|
| SpotBugs | `${HOME}/app/spotbugs` | 字节码缺陷扫描 |
| PMD | `${HOME}/app/pmd` | 源码规范扫描 |
| Arthas | `${HOME}/app/arthas` | 运行时诊断与挂载分析 |
| async-profiler | `${HOME}/app/async-profiler` | CPU/内存采样与火焰图 |
| aspfit / aspfitn / aspflist | `${HOME}/bin/` | 按 PID/进程名采样、列出支持的采集模式 |
| jitwatch | `${HOME}/app/jitwatch` | JIT 编译分析 |
| jarScanMax325 | `${HOME}/bin/jarScanMax325` | 扫描超过 325 字节、无法被 JIT 内联的方法 |
| hprof-slurp / jhh | `${HOME}/.cargo/bin/` | 堆转储解析，命令行方式，速度快于 GUI |

## 验证

- `java -version`、`mvnd -version`、`mvn -version` 均可正常输出。
- `JAVA_HOME` 指向的版本与项目要求一致。
- 别名切换后 `which java` 指向目标 JDK。
