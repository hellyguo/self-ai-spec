---
name: java-coverage
description: Strategies and patterns to boost test coverage to 80%+ line or 60%+ branch coverage. Includes integration testing, MockMvc, and coverage optimization techniques.
origin: Custom
---

# Coverage Booster Skill

**目标**: 将测试覆盖率提升至行覆盖率>80%或分支覆盖率>60%；增量测试只需将测试内容覆盖率提升至目标值。

## When to Use This Skill

Use this skill when the user:

- 对当前增量代码进行单元测试
- 对当前项目代码进行单元测试
- 生成增量/全量单元测试报告、增量/全量覆盖率报告

## 强制要求

1. **不允许修改源项目的文件**
2. **增量源文件 100% 覆盖**（见 [templates/coverage-checklist-table.md](templates/coverage-checklist-table.md)）
3. **生成可重复执行的脚本文件**（见 [templates/run-tests-script.md](templates/run-tests-script.md)）

## 约束条件

在应用任何单元测试更改之前，确保项目能够编译。如果编译失败，请立即停止——在问题解决之前不要继续。应用改进后，运行完整验证。

## 技能委托

### 单元测试质量标准

当编写分类 A/B 的单元测试时，委托 `131-java-testing-unit-testing` 技能：

- JUnit 5 注解、AssertJ 断言、Given-When-Then 结构
- 参数化测试（@ValueSource/@CsvSource/@MethodSource）
- Mockito 模拟（@Mock/@InjectMocks/when/verify）
- 边界条件（RIGHT-BICEP/CORRECT）、分支覆盖矩阵、循环边界测试

### Spring Boot 集成测试

当遇到需要 Spring 容器的测试场景时，委托 `spring-boot-test` 技能：

- Controller 测试：@WebMvcTest + MockMvc + 认证/权限
- Service 集成测试：@SpringBootTest + @MockBean + 事务回滚
- Repository 测试：@DataJpaTest + TestEntityManager

## 固化数据优先读取

**在执行任何步骤之前，先读取以下固化文件，避免重复探索：**

| 文件 | 用途 |
| ------ | ------ |
| `MEMORY.md` | 项目基本信息、测试框架版本、模块结构、用户偏好 |
| `docs/test-framework-cache.md` | 测试依赖版本、模块路径、pom-test.xml差异化字段 |
| `docs/test-code-templates.md` | 各层测试代码模板（枚举/Domain/Service/工具类） |
| `docs/pom-test-xml-template.md` | pom-test.xml 生成模板 |
| `docs/html-report-template.md` | HTML 报告样式和组件清单 |
| `references/error-guide.md` | 已知错误知识库（编译/运行时问题及修复方案） |

**初始化规则**：如果 `MEMORY.md` 已存在且包含测试框架信息 → **跳过初始化**，直接读取全部固化文件后进入增量分析。如果不存在 → 执行初始化流程（见 [templates/init-flow.md](templates/init-flow.md)）。

## 执行流程

### 步骤一：确认分析类型

当用户提出问题时，需要明确：

1. 该项目是 Java/C/Python 语言（已固化到 MEMORY.md，优先读取）
2. 是增量分析还是全量分析
3. 如果是增量分析，获取差异数据

#### 差异数据获取

| 检测项 | 方法 | 命令 |
| -------- | ------ | ------ |
| SVN | 项目根目录下存在 `.svn/` 目录 | `svn diff` 或 `svn diff -r 版本1:版本2` |
| Git | 项目根目录下存在 `.git/` 目录 | `git diff` 或 `git diff 基线分支...HEAD` |

**停止条件**：当无法获取差异数据时，提示用户提供 diff 数据文件路径、版本范围或基线分支名。

### 步骤二：挑选测试框架

（已固化，优先从 MEMORY.md 读取）

- C 项目：Unity (嵌入式) / Check (通用)
- Java 项目：JUnit5 + Mockito + AssertJ
- Python 项目：pytest

**注意**：如果固化文件中已有测试框架信息，直接使用，不重新分析 pom.xml。

### 步骤三：增量执行流程

**禁止进入 brainstorming 流程**。用户提出增量测试需求时，直接按以下标准流程执行。

#### 3.1 diff 分析与源文件读取（并行化）

- Step A [并行]: Agent A 解析 diff 输出变更清单；Agent B 检查各模块是否已有 pom-test.xml
- Step B [并行]: 每个 Agent 读取一个模块的变更源文件，不超过5个并行

**Agent 输出约束**：每个源文件只返回类签名、依赖注入列表、新增/变更方法的签名和核心逻辑（10~30行）。单个 Agent 返回总量控制在 200 行以内。

#### 3.2 知识库预防性学习（测试编写前，强制）

**在编写任何测试文件之前，必须先读取以下两个文件**：

- `MEMORY.md`：重点关注"踩坑速查索引"和"关键类包路径"
- `references/error-guide.md`：扫描所有问题标题，提取与当前测试类型相关的预防规则

**输出格式**：读完后输出简表，表明已掌握的规则。

#### 3.3 测试文件编写（同步统计）

编写测试文件时，**同步维护统计数据**，避免最后再扫描一遍。创建每个测试文件时，立即记录：file、module、testCount、paramTestCount、nestedCount、coversSource、coversMethods。

#### 3.4 pom-test.xml 创建（模板化）

检查目标模块是否已有 pom-test.xml：

- **已有** → 跳过，直接使用
- **未有** → 从 `docs/pom-test-xml-template.md` 读取模板，填入差异化字段

#### 3.5 编译执行与错误知识沉淀

在测试文件编写完成后，进入编译执行阶段（`mvn test`）。此阶段遇到的所有编译错误、运行时异常及其修复方案，**必须**记录到错误知识库中。

**修复前知识库匹配（强制）**：每次遇到编译错误或测试失败后，在动手修复之前，必须先读取 `references/error-guide.md`，用错误信息匹配已有问题。如果匹配到，直接按知识库中的解决方案修复，不需要重新探索。详见 [templates/error-knowledge-record.md](templates/error-knowledge-record.md)。

#### 3.6 HTML 报告生成

从 `docs/html-report-template.md` 获取报告组件和样式，填充动态数据直接生成 HTML。**不生成 MD 格式报告，不经过 MD→HTML 转换步骤**。

## 核心策略

### 策略零：测试类型自动分类

在编写测试前，必须先对每个源方法进行分类判定。分类结果决定使用哪种测试模板。详见 [templates/method-classification-matrix.md](templates/method-classification-matrix.md)。

### 策略一：分层测试覆盖

| 层级 | 测试类型 | 覆盖重点 | 工具 |
| ------ | --------- | --------- | ------ |
| Service（简单） | 单元测试 | 业务逻辑 | Mockito + @ExtendWith |
| Service（复杂） | 集成测试 | 业务逻辑+依赖链 | PowerMock / 深度Mock链路 |
| Domain | 单元测试 | POJO属性 | JUnit 5 |

### 策略二：优先级排序

1. **高价值代码优先** - 核心业务逻辑、复杂算法
2. **分支密集代码** - 多条件判断、循环
3. **公共API** - Controller端点
4. **工具类** - 静态方法、工具函数

## 编译执行效率优化

详见 [templates/build-optimization.md](templates/build-optimization.md)，包括：

- 增量构建策略（省 40%/次）
- 无依赖模块并行构建（省 30-40% 总时间）
- JaCoCo 延迟到最终报告（省 ~10s/模块）
- 预编译分离策略（大型项目适用）

## 报告生成要求

**强制要求**：完成单元测试后，**必须**生成 HTML 格式的单元测试报告和覆盖率报告。不允许使用 Markdown 格式替代 HTML 报告。

报告结构规范、样式规范、输出路径和生成步骤详见 `assets/html-report-template.md`。

## 覆盖率检查清单

见 [templates/coverage-checklist.md](templates/coverage-checklist.md)。
