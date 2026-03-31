---
name: jmh-bench
description: "运行JMH基准测试的标准流程"
---

# JMH 基准测试执行指南

## 核心要求

一般默认参数：

- 预热10次，每次100ms
- 执行5次，每次20ms
- 4线程执行
- fork 3次

## 前置准备

### 1. 获取环境信息

执行 skill `/java-env` 获取 Java 开发环境信息：

```
skill java-env
```

确认：
- Maven/Mvnd 目录位置
- JDK 版本匹配项目需求

### 2. 配置 pom.xml

在项目中添加 JMH 依赖：

```xml
<dependencies>
    <!-- JMH Core -->
    <dependency>
        <groupId>org.openjdk.jmh</groupId>
        <artifactId>jmh-core</artifactId>
        <version>1.37</version>
    </dependency>
    
    <!-- JMH Annotations -->
    <dependency>
        <groupId>org.openjdk.jmh</groupId>
        <artifactId>jmh-generator-annprocess</artifactId>
        <version>1.37</version>
        <scope>provided</scope>
    </dependency>
</dependencies>

<build>
    <plugins>
        <!-- 编译插件，确保 annotation processor 生效 -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.11.0</version>
            <configuration>
                <annotationProcessorPaths>
                    <path>
                        <groupId>org.openjdk.jmh</groupId>
                        <artifactId>jmh-generator-annprocess</artifactId>
                        <version>1.37</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

## 执行方式

### 方式一：Maven Exec 插件（推荐）

```bash
# 编译项目
mvn clean compile -q

# 运行全部基准测试
mvn exec:exec -Dexec.executable="java" \
    -Dexec.args="-cp %classpath org.openjdk.jmh.Main" -q

# 运行指定基准测试类
mvn exec:exec -Dexec.executable="java" \
    -Dexec.args="-cp %classpath org.openjdk.jmh.Main BenchmarkClassName" -q

# 运行指定基准测试（带参数）
mvn exec:exec -Dexec.executable="java" \
    -Dexec.args="-cp %classpath org.openjdk.jmh.Main BenchmarkClassName -wi 3 -i 3 -t 1 -f 1" -q
```

**参数说明：**
- `-wi N`: Warmup 迭代次数
- `-i N`: Measurement 迭代次数  
- `-t N`: 线程数
- `-f N`: Fork 次数

### 方式二：run_bench.sh 脚本

创建脚本 `run_bench.sh`：

```bash
#!/bin/bash

# Run JMH benchmark
# Usage: ./run_bench.sh [BenchmarkClass] [jmh_args...]

PROJECT_DIR=$(dirname "$0")
cd "$PROJECT_DIR"

BENCHMARK_CLASS="${1:-}"
JMH_ARGS="${2:-}"

# Build classpath
CLASSPATH="target/classes:target/test-classes:$(mvn dependency:build-classpath -Dmdep.outputFile=/dev/stdout -q)"

# Run JMH
if [ -n "$BENCHMARK_CLASS" ]; then
    java -cp "$CLASSPATH" org.openjdk.jmh.Main "$BENCHMARK_CLASS" $JMH_ARGS
else
    java -cp "$CLASSPATH" org.openjdk.jmh.Main
fi
```

使用方式：
```bash
chmod +x run_bench.sh

# 运行全部
./run_bench.sh

# 运行指定类
./run_bench.sh MyBenchmark

# 运行指定类带参数
./run_bench.sh MyBenchmark "-wi 5 -i 5"
```

## 常用命令模板

| 场景 | 命令 |
|------|------|
| 快速验证 | `-wi 3 -i 3 -t 1 -f 1` |
| 标准测试 | `-wi 5 -i 5 -t 4 -f 2` |
| 精确测试 | `-wi 10 -i 10 -t 1 -f 3` |
| 列出所有Benchmark | `-l` |

## 输出解读

典型输出示例：
```
Benchmark                         Mode  Cnt    Score    Error  Units
MyBenchmark.testMethod           thrpt    5  123456.789 ± 5000  ops/s
```

**指标说明：**
- `thrpt`: Throughput 吞吐量（ops/s）
- `avgt`: Average Time 平均耗时（us/op）
- `sample`: Sampling 时间采样
- `Score`: 平均值
- `Error`: 置信区间误差（99.9%）

## 最佳实践

1. **Warmup 充足** - 至少 5 次预热，让 JIT 编译稳定
2. **避免 GC 影响** - 测试前可手动触发 GC：`System.gc()`
3. **Blackhole 消费** - 防止死代码消除：`bh.consume(result)`
4. **State 隔离** - 使用 `@State(Scope.Thread)` 避免线程竞争
5. **单线程对比** - 多框架对比时先用 `-t 1` 消除并发因素
