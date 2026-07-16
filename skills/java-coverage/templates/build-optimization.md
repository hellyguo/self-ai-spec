# 编译执行效率优化策略

## 问题分析

在多模块 Maven 项目中，`mvn clean test` 的单次执行耗时可分解为：

| 阶段 | 耗时占比 | 说明 |
| ------ | --------- | ------ |
| 主代码编译 | **~50%** | 200-1400 个源文件全量编译，每次 `clean` 后必须重来 |
| Maven 基础开销 | ~35% | JVM 启动、依赖解析、插件初始化、JaCoCo agent |
| 测试执行 | ~5% | 实际测试代码运行（通常 <5s） |
| 测试代码编译 | ~3% | 仅几个测试文件 |
| JaCoCo 报告 | ~7% | 生成覆盖率数据 |

**核心瓶颈**：主代码编译占了 50% 时间，但测试过程中源代码不会变，只有测试代码在反复修改。

## 优化一：增量构建策略（省 40%/次）

**适用场景**：编译-修复循环中，测试代码修改后重新验证。

**规则**：

1. **首次构建**：`mvn clean test`（全量编译，建立缓存）
2. **修复重试**：`mvn test`（增量编译，仅重编译变更的测试文件）
3. **pom-test.xml swap 后**：必须先 `mvn clean test` 一次，之后用 `mvn test`

```
首次: swap pom → mvn clean test  (~50s)
修复: 编辑测试文件 → mvn test    (~30s, 省掉主代码重编译)
再修: 编辑测试文件 → mvn test    (~30s)
...
完成: mvn clean test              (最终验证，~50s)
```

## 优化二：无依赖模块并行构建（省 30-40% 总时间）

**适用场景**：多个模块无相互依赖关系时（如都只依赖 commons）。

**依赖图分析规则**：

```
读取各模块 pom.xml 的 <dependencies>，构建模块依赖图。
依赖图中无直接依赖的模块可以并行构建。

示例依赖图:
  commons ←─ administration
          ←─ contract ←── development
          ←─ financial
          ←─ hr

可并行分组:
  Wave 1: commons install -DskipTests    (顺序，其他模块依赖它)
  Wave 2: contract install -DskipTests   (顺序，development 依赖它)
  Wave 3: administration + financial + hr  (并行，互不依赖)
  Wave 4: development                      (依赖 contract，Wave 2 后执行)
```

**并行构建命令模板**：

```bash
# 后台并行执行多个模块
JAVA_HOME="{JDK}" mvn clean test -f moduleA/pom.xml &
PID_A=$!
JAVA_HOME="{JDK}" mvn clean test -f moduleB/pom.xml &
PID_B=$!
JAVA_HOME="{JDK}" mvn clean test -f moduleC/pom.xml &
PID_C=$!

# 等待全部完成
wait $PID_A $PID_B $PID_C
```

**注意**：并行度建议不超过 CPU 核心数 - 1，避免磁盘 I/O 争用。

## 优化三：JaCoCo 延迟到最终报告（省 ~10s/模块）

**适用场景**：编译-修复循环中不需要覆盖率数据。

**规则**：

1. 开发阶段：`mvn test -Djacoco.skip=true`（跳过 JaCoCo agent + 报告）
2. 最终验证：`mvn clean test`（包含 JaCoCo，生成覆盖率数据）
3. 仅报告：`mvn jacoco:report`（不重新运行测试，只从已有 jacoco.exec 生成报告）

## 优化四：预编译分离策略（大型项目适用）

**适用场景**：模块数量 > 5，或单个模块主代码文件 > 500 个。

**策略**：将编译和测试执行分为两个独立阶段，中间可以并行。

```bash
# Stage 1: 预编译所有模块（顺序，按依赖顺序）
for module in commons contract administration financial hr development; do
  swap_pom $module
  JAVA_HOME="{JDK}" mvn compile test-compile -f $module/pom.xml   # 只编译不测试
done

# Stage 2: 并行执行测试（主代码已编译，只启动 Surefire）
for module in administration financial hr; do
  JAVA_HOME="{JDK}" mvn surefire:test -f $module/pom.xml &       # 并行
done
wait

# 依赖链上的模块顺序执行
JAVA_HOME="{JDK}" mvn surefire:test -f contract/pom.xml
JAVA_HOME="{JDK}" mvn surefire:test -f development/pom.xml
```

## 整合后的 Phase 6 执行流程

```
[Phase 6.1] 依赖安装（顺序）
    commons: mvn install -DskipTests
    其他被依赖模块: swap pom → mvn install -DskipTests → restore pom

[Phase 6.2] 首次编译+测试（并行分组）
    分析模块依赖图 → 确定可并行分组
    Wave 1: 无上游依赖的模块并行 swap → mvn clean test
    Wave 2: 依赖 Wave 1 的模块 swap → mvn clean test
    ...按依赖层级推进

[Phase 6.3] 错误修复循环（增量构建）
    for each 失败模块:
      编辑测试文件
      mvn test（增量，不 clean）     ← 优化一
      失败 → 继续修复循环
      成功 → 下一个模块

[Phase 6.4] 最终验证（全量，含 JaCoCo）
    所有模块: mvn clean test          ← 确保无缓存干扰
    收集 target/site/jacoco/ 数据
```
