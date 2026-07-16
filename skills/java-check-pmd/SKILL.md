---
name: java-check-pmd
description: "PMD静态分析技能：使用PMD进行Java代码质量分析，检测代码坏味道、编码规范和安全问题"
---

# PMD Java静态分析技能

PMD（Programming Mistake Detector）检测Java代码中的编码规范违规、代码坏味道、潜在缺陷和安全漏洞。

## 工具位置

```bash
PMD_HOME=~/app/pmd-bin-6.19.0
PMD_CLI=$PMD_HOME/bin/run.sh
PMD_RULESETS=/home/helly/open_source/github/pmd/pmd-java/src/main/resources/rulesets
```

## 执行流程

### 步骤1：准备源代码

```bash
SRC_DIR=src/main/java  # Maven项目
# 或 SRC_DIR=src       # 标准项目
```

### 步骤2：执行PMD分析

```bash
# 代码风格检查
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f text -r pmd-style.txt

# 完整质量检查
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/basic.xml,rulesets/java/design.xml -f text -r pmd-quality.txt

# 安全漏洞检查
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/security.xml -f text -r pmd-security.txt
```

### 步骤3：自定义规则集

```bash
$PMD_CLI pmd -d $SRC_DIR -R custom-ruleset.xml -f text -r pmd-custom.txt
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/basic.xml -R rulesets/java/codeestyle.xml -f text -r pmd-combined.txt
```

### 步骤4：重复代码检测（CPD）

```bash
$PMD_CLI cpd --minimum-tokens 100 --files $SRC_DIR --language java --format text --fail-on-violation true
$PMD_CLI cpd --minimum-tokens 50 --files $SRC_DIR --language java \
  --format xml --ignore-literals true --ignore-identifiers true
```

### 步骤5：分析结果处理

Read `templates/result-processing.md`

### 步骤6：增量分析

```bash
# 分析特定文件
$PMD_CLI pmd -d src/main/java/com/example/Test.java -R rulesets/java/quickstart.xml -f text

# 分析文件列表
$PMD_CLI pmd -filelist filelist.txt -R rulesets/java/quickstart.xml -f text
```

## 常用命令

```bash
$PMD_CLI pmd -list                           # 查看所有规则
$PMD_CLI pmd -list -language java            # 查看Java规则
$PMD_CLI pmd -help -language java -rule EmptyCatchBlock  # 查看规则详情
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f text -verbose  # 详细输出
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f text -debug    # 调试模式
```

## CPD参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--minimum-tokens` | 最小token数 | 100 |
| `--language` | 检测语言 | java |
| `--format` | 输出格式 | text |
| `--ignore-literals` | 忽略字面量 | false |
| `--ignore-identifiers` | 忽略标识符 | false |

## 最佳实践

1. **渐进式采用**：先启用基础规则，逐步增加设计/安全规则，根据团队接受度调整阈值
2. **规则定制**：根据项目特点定制规则集，排除不适用的规则，调整复杂度阈值
3. **集成策略**：开发环境用警告级别，构建环境用错误级别，发布环境严格检查
4. **团队培训**：解释规则含义，提供修复示例，建立代码审查标准

## 注意事项

1. 大型项目PMD分析可能较慢，建议增量分析
2. 部分规则可能有误报，需人工确认
3. 不同规则可能冲突，需权衡
4. 确保PMD版本与Java版本兼容

## 故障排除

| 问题 | 原因 |
|------|------|
| No files to process | 源代码路径不正确 |
| Unsupported language | 语言参数不正确 |
| RuleSetNotFoundException | 规则集文件不存在 |

## 模板引用

| 模板文件 | 用途 |
|----------|------|
| `templates/output-formats.md` | 输出格式（text/xml/csv/html） |
| `templates/custom-ruleset.md` | 自定义规则集XML模板 |
| `templates/build-integration.md` | Maven/Gradle集成配置 |
| `templates/rulesets-reference.md` | 规则集速查表（basic/codeestyle/design/security/performance） |
| `templates/result-processing.md` | 结果解析与趋势报告脚本 |

---

**技能版本**: 1.0.0  
**工具版本**: PMD 6.19.0  
**适用项目**: Java 8+ 企业级项目  
**输出位置**: 当前目录下的pmd-*.txt文件
