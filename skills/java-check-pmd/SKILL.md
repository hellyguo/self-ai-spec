---
name: java-check-pmd
description: "PMD静态分析技能：使用PMD进行Java代码质量分析，检测代码坏味道、编码规范和安全问题"
---

# PMD Java静态分析技能

## 概述

PMD（Programming Mistake Detector）是源代码分析工具，可检测Java代码中的：
- **编码规范违规**：命名约定、代码格式
- **代码坏味道**：重复代码、复杂方法
- **潜在缺陷**：空指针、资源泄漏
- **安全漏洞**：不安全API使用

## 工具位置

```bash
# PMD主工具
PMD_HOME=~/app/pmd-bin-6.19.0
PMD_CLI=$PMD_HOME/bin/run.sh  # 使用包装脚本
PMD_JAR=$PMD_HOME/lib/pmd-*.jar

# 规则集位置
PMD_RULESETS=/home/helly/open_source/github/pmd/pmd-java/src/main/resources/rulesets
```

## 使用场景

### 1. 代码规范检查
检查命名约定、代码格式、注释规范等。

### 2. 代码质量分析
检测重复代码、过长方法、高圈复杂度等。

### 3. 最佳实践检查
检查异常处理、资源管理、API使用等。

### 4. 安全漏洞扫描
检测不安全的编码实践。

## 执行流程

### 步骤1：准备源代码
```bash
# 确保源代码可访问
SRC_DIR=src/main/java  # Maven项目结构
# 或
SRC_DIR=src  # 标准项目结构
```

### 步骤2：执行PMD分析
```bash
# 基本代码风格检查
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f text -r pmd-style.txt

# 完整质量检查
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/basic.xml,rulesets/java/design.xml -f text -r pmd-quality.txt

# 安全漏洞检查
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/security.xml -f text -r pmd-security.txt
```

### 步骤3：自定义规则集
```bash
# 使用自定义规则集
$PMD_CLI pmd -d $SRC_DIR -R custom-ruleset.xml -f text -r pmd-custom.txt

# 多个规则集组合
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/basic.xml -R rulesets/java/codeestyle.xml -f text -r pmd-combined.txt
```

## 规则集详解

### 1. 基础规则集（basic.xml）
| 规则 | 描述 | 示例 |
|------|------|------|
| `EmptyCatchBlock` | 空的catch块 | `try { ... } catch (Exception e) {}` |
| `UnnecessaryConversionTemporary` | 不必要的类型转换 | `new String(str.toString())` |
| `OverrideBothEqualsAndHashcode` | 重写equals必须重写hashCode | 缺少hashCode方法 |
| `DoubleCheckedLocking` | 双重检查锁定问题 | 线程安全的单例模式错误实现 |

### 2. 代码风格规则集（codeestyle.xml）
| 规则 | 描述 | 建议 |
|------|------|------|
| `ShortVariable` | 变量名过短 | 使用有意义的变量名 |
| `LongVariable` | 变量名过长 | 简化变量名 |
| `ShortClassName` | 类名过短 | 使用描述性类名 |
| `AvoidFinalLocalVariable` | 避免final局部变量 | 除非必要，否则不用final |
| `OnlyOneReturn` | 方法中只有一个return | 保持方法简单 |
| `EmptyMethodInAbstractClassShouldBeAbstract` | 抽象类中的空方法应为抽象 | 明确方法意图 |

### 3. 设计规则集（design.xml）
| 规则 | 描述 | 影响 |
|------|------|------|
| `UseUtilityClass` | 应使用工具类 | 避免实例化只有静态方法的类 |
| `SimplifyBooleanReturns` | 简化布尔返回值 | 直接返回布尔表达式 |
| `SimplifyBooleanExpressions` | 简化布尔表达式 | 移除不必要的逻辑 |
| `SwitchDensity` | switch语句密度 | switch语句不宜过大 |
| `GodClass` | 上帝类 | 类职责过多，应拆分 |
| `CyclomaticComplexity` | 圈复杂度 | 方法过于复杂，应重构 |
| `ExcessiveClassLength` | 类过长 | 类代码行数过多 |
| `ExcessiveMethodLength` | 方法过长 | 方法代码行数过多 |
| `ExcessiveParameterList` | 参数列表过长 | 方法参数过多 |
| `ExcessivePublicCount` | 公共方法过多 | 类的公共接口过大 |
| `TooManyFields` | 字段过多 | 类包含太多字段 |
| `NcssConstructorCount` | 构造函数复杂度 | 构造函数过于复杂 |
| `NcssMethodCount` | 方法复杂度 | 方法过于复杂 |
| `NcssTypeCount` | 类型复杂度 | 类过于复杂 |

### 4. 安全规则集（security.xml）
| 规则 | 描述 | 风险等级 |
|------|------|----------|
| `HardCodedCryptoKey` | 硬编码加密密钥 | 高危 |
| `InsecureCryptoIv` | 不安全的加密IV | 高危 |
| `DataflowAnomalyAnalysis` | 数据流异常分析 | 中危 |
| `AvoidUsingHardCodedIP` | 避免硬编码IP地址 | 中危 |
| `AvoidUsingHardCodedURL` | 避免硬编码URL | 中危 |

### 5. 性能规则集（performance.xml）
| 规则 | 描述 | 性能影响 |
|------|------|----------|
| `AvoidArrayLoops` | 避免数组循环 | 高 |
| `AvoidInstantiatingObjectsInLoops` | 避免在循环中实例化对象 | 高 |
| `OptimizableToArrayCall` | 可优化的toArray调用 | 中 |
| `RedundantFieldInitializer` | 冗余字段初始化器 | 低 |

## 输出格式

### 1. 文本格式（默认）
```text
src/main/java/com/example/Test.java:10:  EmptyCatchBlock: Avoid empty catch blocks
src/main/java/com/example/Test.java:25:  ShortVariable: Avoid variables with short names like 'i'
src/main/java/com/example/Test.java:45:  CyclomaticComplexity: The method 'process' has a cyclomatic complexity of 12
```

### 2. XML格式（用于集成）
```bash
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f xml -r pmd.xml
```

### 3. CSV格式（表格数据）
```bash
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f csv -r pmd.csv
```

### 4. HTML报告（可视化）
```bash
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f html -r pmd.html
```

## 自定义规则集

### 创建自定义规则集（custom-ruleset.xml）
```xml
<?xml version="1.0"?>
<ruleset name="Custom Java Rules"
         xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://pmd.sourceforge.net/ruleset/2.0.0 
                             http://pmd.sourceforge.net/ruleset_2_0_0.xsd">
    
    <description>自定义Java代码检查规则集</description>
    
    <!-- 包含基础规则 -->
    <rule ref="rulesets/java/basic.xml"/>
    
    <!-- 包含代码风格规则，但排除特定规则 -->
    <rule ref="rulesets/java/codeestyle.xml">
        <exclude name="ShortVariable"/>
        <exclude name="OnlyOneReturn"/>
    </rule>
    
    <!-- 包含设计规则，自定义复杂度阈值 -->
    <rule ref="rulesets/java/design.xml/CyclomaticComplexity">
        <properties>
            <property name="reportLevel" value="15"/>  <!-- 默认10 -->
        </properties>
    </rule>
    
    <!-- 自定义规则组合 -->
    <rule ref="rulesets/java/basic.xml/EmptyCatchBlock"/>
    <rule ref="rulesets/java/codeestyle.xml/LongVariable"/>
    <rule ref="rulesets/java/design.xml/GodClass"/>
    <rule ref="rulesets/java/security.xml/HardCodedCryptoKey"/>
</ruleset>
```

## 集成到构建工具

### Maven集成
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-pmd-plugin</artifactId>
    <version>3.20.0</version>
    <configuration>
        <rulesets>
            <ruleset>rulesets/java/quickstart.xml</ruleset>
            <ruleset>custom-ruleset.xml</ruleset>
        </rulesets>
        <failurePriority>3</failurePriority>
        <minimumTokens>100</minimumTokens>
        <linkXRef>false</linkXRef>
    </configuration>
    <executions>
        <execution>
            <phase>verify</phase>
            <goals>
                <goal>check</goal>
                <goal>cpd-check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### Gradle集成
```groovy
plugins {
    id 'pmd'
}

pmd {
    toolVersion = '6.19.0'
    ruleSets = []
    ruleSetFiles = files("custom-ruleset.xml")
    ignoreFailures = false
    consoleOutput = true
}

pmdMain {
    ruleSets = ['rulesets/java/quickstart.xml']
}

pmdTest {
    ruleSets = ['rulesets/java/basic.xml']
}
```

## 重复代码检测（CPD）

### 基本使用
```bash
# 检测重复代码
$PMD_CLI cpd --minimum-tokens 100 --files $SRC_DIR --language java --format text --fail-on-violation true

# 详细报告
$PMD_CLI cpd --minimum-tokens 50 --files $SRC_DIR --language java --format xml --ignore-literals true --ignore-identifiers true
```

### CPD参数说明
| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--minimum-tokens` | 最小token数 | 100 |
| `--language` | 检测语言 | java |
| `--format` | 输出格式 | text |
| `--ignore-literals` | 忽略字面量 | false |
| `--ignore-identifiers` | 忽略标识符 | false |
| `--skip-lexical-errors` | 跳过词法错误 | false |

## 常用命令参考

### 查看所有规则
```bash
$PMD_CLI pmd -list
```

### 查看特定语言规则
```bash
$PMD_CLI pmd -list -language java
```

### 查看规则详情
```bash
$PMD_CLI pmd -help -language java -rule EmptyCatchBlock
```

### 增量分析
```bash
# 分析特定文件
$PMD_CLI pmd -d src/main/java/com/example/Test.java -R rulesets/java/quickstart.xml -f text

# 分析文件列表
$PMD_CLI pmd -filelist filelist.txt -R rulesets/java/quickstart.xml -f text
```

## 分析结果处理

### 1. 结果解析脚本示例
```bash
#!/bin/bash
# 解析PMD输出，统计问题类型
echo "=== PMD分析报告 ==="
echo "总问题数: $(grep -c ":" pmd.txt)"
echo "空catch块: $(grep -c "EmptyCatchBlock" pmd.txt)"
echo "圈复杂度问题: $(grep -c "CyclomaticComplexity" pmd.txt)"
echo "短变量名: $(grep -c "ShortVariable" pmd.txt)"
```

### 2. 问题严重性分类
```bash
# 高风险问题
grep -E "(HardCodedCryptoKey|InsecureCryptoIv|DataflowAnomalyAnalysis)" pmd.txt

# 代码质量问题  
grep -E "(CyclomaticComplexity|GodClass|ExcessiveMethodLength)" pmd.txt

# 代码风格问题
grep -E "(ShortVariable|LongVariable|OnlyOneReturn)" pmd.txt
```

### 3. 生成趋势报告
```bash
# 跟踪问题趋势
echo "日期: $(date)" >> pmd-trend.txt
echo "圈复杂度>10的方法: $(grep "CyclomaticComplexity" pmd.txt | grep -o "[0-9][0-9]" | awk '$1 > 10' | wc -l)" >> pmd-trend.txt
echo "代码行数>100的方法: $(grep "ExcessiveMethodLength" pmd.txt | wc -l)" >> pmd-trend.txt
```

## 最佳实践

### 1. 渐进式采用
- 开始阶段只启用基础规则
- 逐步增加设计规则和安全规则
- 根据团队接受度调整规则阈值

### 2. 规则定制
- 根据项目特点定制规则集
- 排除不适用于项目的规则
- 调整复杂度阈值

### 3. 集成策略
- 开发环境：警告级别
- 构建环境：错误级别
- 发布环境：严格检查

### 4. 团队培训
- 解释常见规则的含义
- 提供修复示例
- 建立代码审查标准

## 注意事项

1. **性能影响**：大型项目PMD分析可能较慢，建议增量分析
2. **误报问题**：部分规则可能有误报，需要人工确认
3. **规则冲突**：不同规则可能有冲突，需要权衡
4. **版本兼容**：确保PMD版本与Java版本兼容

## 故障排除

### 常见问题
1. **No files to process**：确认源代码路径正确
2. **Unsupported language**：确认语言参数正确
3. **RuleSetNotFoundException**：确认规则集文件存在

### 调试命令
```bash
# 启用详细输出
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f text -verbose

# 调试模式
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f text -debug
```

---
**技能版本**: 1.0.0  
**工具版本**: PMD 6.19.0  
**适用项目**: Java 8+ 企业级项目  
**输出位置**: 当前目录下的pmd-*.txt文件  
**规则来源**: PMD源码项目中的规则集文件