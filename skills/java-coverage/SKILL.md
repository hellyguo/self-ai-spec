---
name: java-coverage
description: Strategies and patterns to boost test coverage to 80%+ line or 60%+ branch coverage. Includes integration testing, MockMvc, and coverage optimization techniques.
origin: Custom
---

# Coverage Booster Skill

**目标**: 将测试覆盖率提升至行覆盖率>80%或分支覆盖率>60%；增量测试的的话只需要将测试的内容覆盖率提升至行覆盖率>80%或分支覆盖率>60%；
## When to Use This Skill
Use this skill when the user:
-对当前增量代码进行单元测试
-对当前项目代码进行单元测试
-生成增量/全量单元测试报告、增量/全量覆盖率报告

**约束条件**:
在应用任何单元测试更改之前，确保项目能够编译。如果编译失败，请立即停止 —— 在问题解决之前不要继续。应用改进后，运行完整验证

## 强制要求
1. **不允许修改源项目的文件**（重复三遍）
2. **增量源文件 100% 覆盖**（见下方"增量覆盖完整性校验"章节）
3. **生成可重复执行的脚本文件**（见下方"执行脚本生成"章节）

### 增量覆盖完整性校验

**定义**：diff 中出现的每个源代码文件，都必须有对应的测试文件。不允许以"逻辑简单"、"依赖复杂"等理由跳过任何源文件。

**校验规则**：
1. 从 diff 输出中提取所有变更的源代码文件（按语言后缀过滤，如 Java 的 `.java`，排除测试文件本身如 `*Test.java`、`*Tests.java`）
2. 对每个源文件，必须生成至少一个测试文件
3. 测试文件必须覆盖该源文件中**变更/新增的方法和分支**
4. DAO/Repository 接口：对新增方法签名，通过 Mockito 模拟测试其调用约定（参数传递、返回值处理）
5. Service 类：用 `@ExtendWith(MockitoExtension.class)` + `@Mock` + `@InjectMocks` 模拟所有依赖，测试变更方法的每个分支

**校验时机**：在进入"测试文件编写"阶段前，先输出覆盖清单表格：

```
| 源文件 | 是否需测试 | 测试文件名 | 备注 |
|--------|-----------|-----------|------|
| XxxEnum.java | 是 | XxxEnumTest.java | 枚举类 |
| XxxService.java | 是 | XxxServiceTest.java | Mockito模拟依赖 |
| XxxDao.java | 是 | XxxDaoTest.java | 接口新增方法用Mockito验证 |
| Xxx.xml | 否 | - | 非源代码文件，跳过 |
```

**停止条件**：如果清单中有任何源文件被标记为"否"且非"非源代码文件"原因，**立即停止并报错**，不允许跳过。

### 执行脚本生成

**强制要求**：在所有测试文件编写完成后，**必须**在 `report/` 目录下生成一个可重复执行的脚本文件 `{YYYY-MM-DD}_run_tests.sh`（Linux/Mac）和 `{YYYY-MM-DD}_run_tests.bat`（Windows）。

**脚本内容必须包含**：

```bash
#!/bin/bash
# 增量测试一键执行脚本
# 生成日期: YYYY-MM-DD
# 基线: git diff HEAD~N
# Java版本要求: {项目要求的JDK版本}
# ============================================

# [1] 环境检查
# - 检查 JAVA_HOME 是否指向正确版本
# - 检查 Maven 是否可用

# [2] 备份原 pom.xml（按模块逐个执行）
# cp pom.xml pom-backup.xml
# cp src/test/resources/pom-test.xml pom.xml

# [3] 执行测试 + 生成覆盖率
# mvn clean test
# mvn jacoco:report

# [4] 恢复原 pom.xml
# cp pom-backup.xml pom.xml && rm pom-backup.xml

# [5] 测试结果汇总
# 输出每个模块的: Tests run / Failures / Errors / Skipped

# [6] 报告路径提示
# 单元测试报告: report/YYYY-MM-DD_增量单元测试报告.html
# 覆盖率报告: report/YYYY-MM-DD_增量覆盖率报告.html
# JaCoCo原始报告: {模块}/target/site/jacoco/index.html
```

**脚本特性**：
- 支持传入参数指定模块名（只测试指定模块）或 `all`（测试全部）
- 支持失败继续（一个模块失败不影响其他模块）
- 最终返回非零退出码（如果有任何测试失败）
- 自动备份和恢复 pom.xml
- **采用并行构建优化**：分析模块依赖图后，无依赖关系的模块并行执行
- **支持增量构建模式**：`--incremental` 参数跳过 `clean`，仅重编译变更的测试文件

## 技能委托：单元测试质量标准

当编写分类 A/B 的单元测试时，委托 `131-java-testing-unit-testing` 技能：
- JUnit 5 注解、AssertJ 断言、Given-When-Then 结构
- 参数化测试（@ValueSource/@CsvSource/@MethodSource）
- Mockito 模拟（@Mock/@InjectMocks/when/verify）
- 边界条件（RIGHT-BICEP/CORRECT）、分支覆盖矩阵、循环边界测试
- 测试反模式检测、命名规范

## 技能委托：Spring Boot 集成测试

当遇到需要 Spring 容器的测试场景时，委托 `spring-boot-test` 技能：
- Controller 测试：@WebMvcTest + MockMvc + 认证/权限
- Service 集成测试：@SpringBootTest + @MockBean + 事务回滚
- Repository 测试：@DataJpaTest + TestEntityManager
- 测试配置：@TestPropertySource / @ActiveProfiles / application-test.yml
- TestDataBuilder 构建器模式

## 固化数据优先读取（关键优化）

**在执行任何步骤之前，先读取以下固化文件，避免重复探索：**

**读取路径**：固化文件存放在项目级 `.` 目录下（即 `{项目根}`）。

```
MEMORY.md              → 项目基本信息、测试框架版本、模块结构、用户偏好
docs/test-framework-cache.md → 测试依赖版本、模块路径、pom-test.xml差异化字段
docs/test-code-templates.md  → 各层测试代码模板（枚举/Domain/Service/工具类）
docs/pom-test-xml-template.md → pom-test.xml 生成模板
docs/html-report-template.md  → HTML 报告样式和组件清单
references/error-guide.md              → 已知错误知识库（编译/运行时问题及修复方案）
```

**初始化规则**：

- 如果 `MEMORY.md` 已存在且包含测试框架信息 → **跳过初始化**，直接读取全部固化文件后进入增量分析
- 如果 `MEMORY.md` 不存在 → 执行以下初始化流程：

#### 初始化流程（首次执行）

**Step 1: 模板分类处理**

模板文件按是否含项目专属占位符分为两类，区别处理：

| 分类 | 文件 | 占位符情况 | 处理方式 |
|------|------|-----------|---------|
| 直接复制 | `test-code-templates.md` | 无占位符，纯通用模板 | 从 `assets/` 直接复制到 `docs/`，无需分析 |
| 直接复制 | `html-report-template.md` | 无占位符，动态数据在报告生成时填充 | 从 `assets/` 直接复制到 `docs/`，无需分析 |
| 需分析填充 | `MEMORY.md` | 含项目名、技术栈、模块列表、依赖版本等占位符 | 需从项目提取信息 |
| 需分析填充 | `test-framework-cache.md` | 含依赖版本、模块路径、差异化字段等占位符 | 需从项目提取信息 |
| 需分析填充 | `pom-test-xml-template.md` | 含依赖版本占位符 | 需从项目提取信息 |

**Step 2: 项目信息提取（单次扫描，3个 Agent 并行）**

3个需填充模板的占位符高度重叠（均依赖 pom.xml 的依赖版本和模块信息），**一次扫描同时填充所有模板**：

```
Agent A ─── 读根 pom.xml ──→ 提取: modules列表、Java版本、全局依赖版本、properties
  │
  ├→ 填充 MEMORY.md 占位符（项目名、技术栈、依赖版本）
  ├→ 填充 test-framework-cache.md 占位符（依赖版本部分）
  └→ 填充 pom-test-xml-template.md 占位符（依赖版本部分）

Agent B ─── 读各模块 pom.xml ──→ 提取: artifactId、parent信息、自定义properties、mainClass
  │
  ├→ 填充 test-framework-cache.md 占位符（模块路径部分）
  └→ 填充 MEMORY.md 占位符（模块结构部分）

Agent C ─── 扫描各模块 src/test/ 目录 ──→ 提取: 测试文件数、pom-test.xml 状态
  │
  └→ 填充 MEMORY.md 占位符（测试目录现状部分）
```

**Step 3: 统一写入**

将所有文件写入当前目录：
- Agent A 完成后 → 写入 `MEMORY.md`（依赖版本部分）、`docs/pom-test-xml-template.md`
- Agent B 完成后 → 补充写入 `MEMORY.md`（模块部分）、`docs/test-framework-cache.md`
- Agent C 完成后 → 补充写入 `MEMORY.md`（目录现状部分）
- Step 1 的直接复制文件 → 与 Agent 并行写入（无依赖关系）

**通用约束**：
- **写入路径**：所有新增或更新的固化文件统一写入当前目录（项目级，跟随项目走）
- **assets/ 目录**：通用模板，随 skill 分发，不写入项目特定数据

步骤一:确认增量代码分析还是全量代码分析
当用户提出问题时，需要明确：
1.该项目是java语言还是C或者python语言（已固化到MEMORY.md，优先读取）
2.是增量分析还是全量分析
3.如果是增量分析，获取差异数据的流程如下：

#### 差异数据获取流程

```
用户是否提供了 diff 数据文件？
├─ 是 → 直接使用提供的文件，进入步骤二
└─ 否 → 检测项目版本控制工具
         ├─ 检测到 .svn 目录 → SVN 项目
         │   ├─ 执行 svn diff 获取差异数据
         │   ├─ 成功 → 保存差异到临时文件，进入步骤二
         │   └─ 失败 → 提示用户并停止
         ├─ 检测到 .git 目录 → Git 项目
         │   ├─ 执行 git diff 获取差异数据
         │   ├─ 成功 → 保存差异到临时文件，进入步骤二
         │   └─ 失败 → 提示用户并停止
         └─ 均未检测到 → 提示用户并停止
```

**具体检测规则**：

| 检测项 | 方法 | 命令 |
|--------|------|------|
| SVN | 项目根目录下存在 `.svn/` 目录 | `svn diff` 或 `svn diff -r 版本1:版本2` |
| Git | 项目根目录下存在 `.git/` 目录 | `git diff` 或 `git diff 基线分支...HEAD` |

**停止条件**：当无法获取差异数据时，向用户输出以下提示并停止执行，等待用户后续指令：

> 未检测到差异数据。请通过以下方式之一提供：
> 1. 提供 diff 数据文件路径
> 2. 提供 git/svn 的版本范围（如 `svn diff -r 102826:118529`）
> 3. 提供 git 的基线分支名（如 `git diff 2601/DEV...HEAD`）

步骤二:挑选测试框架（已固化，优先从 MEMORY.md 读取）
1.如果是C项目，可选用Unity (嵌入式) / Check (通用)框架
2.如果是java项目，可选用JUnit5 + Mockito+AssertJ框架（EMIS项目已固定此方案）
3.如果是python项目，可选用pytest框架
**注意：如果固化文件中已有测试框架信息，直接使用，不重新分析 pom.xml**

步骤三:增量执行流程（优化后）

**禁止进入 brainstorming 流程**。用户提出增量测试需求时，直接按以下标准流程执行，不做方案对比。

### 3.1 diff 分析与源文件读取（并行化）

```
Step A [并行] ─┬─ Agent A: 解析 diff 输出变更清单（按模块分组、按优先级排序）
                └─ Agent B: 检查各模块是否已有 pom-test.xml，无则标记需创建

Step B [并行] ─┬─ Agent C: 读取模块1的变更源文件（仅签名+依赖+新增方法逻辑）
                ├─ Agent D: 读取模块2的变更源文件（仅签名+依赖+新增方法逻辑）
                └─ ...每个模块一个 Agent，不超过5个并行
```

**Agent 输出约束（解决上下文过大问题）**：
- 每个源文件只返回：类签名、依赖注入列表、新增/变更方法的签名和核心逻辑（10~30行）
- 不返回 import 列表、不返回未变更的方法、不返回完整文件内容
- 单个 Agent 返回总量控制在 200 行以内

### 3.2 知识库预防性学习（测试编写前，强制）

**在编写任何测试文件之前，必须先读取以下两个文件**，提取与当前变更相关的已知陷阱，避免重复踩坑：

**必读文件 1**: `MEMORY.md`
- 重点关注"踩坑速查索引"和"关键类包路径"
- 提取当前模块的已有经验（如已验证的包路径、pom-test.xml 状态）

**必读文件 2**: `skills/java-coverage/references/error-guide.md`
- 扫描所有问题标题，提取与当前测试类型相关的预防规则
- 重点关注以下高频问题：
  - P16: import 包路径必须从源文件获取
  - P19: IBM MQ 常量值陷阱
  - P20: Mockito strict 模式 UnnecessaryStubbingException
  - P21: 反射调用私有方法的异常包装
  - P5: JUnit 5 需要 surefire >= 2.22.0 + engine 依赖
  - P9: Java 版本约束（var、List.of() 等）

**输出格式**：读完后在上下文中输出一个简表，表明已掌握的规则：

```
知识库预防性学习完成，已提取以下适用规则：
- P16: 所有 import 路径从源文件获取 → 当前变更涉及 Bonds/FreezingType 等，路径已记录在 MEMORY.md
- P20: 只 mock 实际会被调用的方法 → checkPledgeRule 非 PLEDGEFROZEN 时不调用 repository
- P21: 反射调用私有方法用 hasCauseInstanceOf() → checkPledgeRule/checkPledgeFlag 为 private
- P9: Java 1.8 约束 → 不用 var、List.of()
```

**强制规则**：如果跳过此步骤直接编写测试，导致踩了知识库中已记录的坑，视为流程违规。

### 3.3 测试文件编写（同步统计）

编写测试文件时，**同步维护统计数据**，避免最后再扫描一遍：

```
在创建每个测试文件时，立即记录到内存变量：
{
  file: "XxxTest.java",
  module: "commons",
  testCount: 6,
  paramTestCount: 11,
  nestedCount: 6,
  coversSource: "SystemPlatformAndSourceEnvEnums",
  coversMethods: ["isNormalEnv", "isSafeEnv"]
}
```

这样在所有测试文件写完后，统计数据已就绪，直接用于报告生成，无需再启动 Agent 扫描。

### 3.3 pom-test.xml 创建（模板化）

检查目标模块是否已有 pom-test.xml：
- **已有** → 跳过，直接使用
- **未有** → 从 `docs/pom-test-xml-template.md` 读取模板，填入 5 个差异化字段

### 3.5 编译执行与错误知识沉淀

在测试文件编写完成后，进入编译执行阶段（`mvn test`）。此阶段遇到的所有编译错误、运行时异常及其修复方案，**必须**记录到错误知识库中，为后续增量分析提供学习参考。如果错误知识库中已经存在相似的内容，不用加入进去。

#### 3.5.1 修复前知识库匹配（强制）

**每次遇到编译错误或测试失败后，在动手修复之前，必须先执行以下步骤**：

**Step 1**: 读取 `references/error-guide.md`，用错误信息匹配已有问题：
- 编译错误（找不到符号、类型不匹配）→ 搜索 P16（包路径）、P9（Java版本）、P11（参数签名）
- 运行时错误（NPE、Mock 失败）→ 搜索 P8（依赖未全部 mock）、P20（UnnecessaryStubbing）
- 异常断言失败 → 搜索 P21（InvocationTargetException 包装）、P19（MQ常量值）
- 构建问题（Tests run: 0、JaCoCo 跳过）→ 搜索 P5（Surefire版本）、P6（JaCoCo配置）、P7（类路径污染）

**Step 2**: 如果匹配到已有问题，直接按知识库中的解决方案修复，**不需要重新探索**。

**Step 3**: 如果未匹配到已有问题，按正常流程探索修复，修复成功后立即记录到知识库。

**输出格式**：修复前输出匹配结果：

```
错误信息: "找不到符号: 类 CommonParamRepository"
知识库匹配: P16 (import 包路径错误) → 解决方案：从源文件获取正确路径
执行: 按P16方案直接修复，跳过探索
```

**知识库路径**: `references/error-guide.md`（相对于 skill 根目录）

**记录时机**: 每次成功修复一个编译或运行时错误后，**立即记录**（不要等到最后统一记录）。

**记录模板**（与 error-guide.md 现有格式保持一致）:

```markdown
### 问题N: [简短描述问题]

**根因**: [问题的根本原因描述]

**解决方案/规则**: [修复方法描述]

[代码示例（如适用）]
```

**记录范围**:
- 编译错误：缺少依赖、类型不匹配、方法签名错误、Java版本不兼容等
- 运行时错误：NPE、Mock注入失败、测试框架配置问题等
- 构建问题：Surefire配置、JaCoCo配置、类路径污染等

**查重规则**: 记录前先读取 `references/error-guide.md`，确认是否已存在同类问题：
- **已存在** → 跳过，不重复记录
- **不存在** → 按模板追加到文件末尾，编号递增

**初始化规则**: 如果 `references/error-guide.md` 不存在，创建文件并写入 `## 常见问题解决` 标题后再追加。

### 3.5 HTML 报告生成（直接 HTML）

从 `docs/html-report-template.md` 获取报告组件和样式，填充动态数据直接生成 HTML。
**不生成 MD 格式报告，不经过 MD→HTML 转换步骤。**

### 3.7 完整执行时间线（优化后）

```
[Phase 1] 读取固化文件 (MEMORY.md 等)              ← 省去框架探索
    ↓
[Phase 2] 并行: diff分析 + 模块检查                ← 2个Agent并行
    ↓
[Phase 3] 覆盖完整性校验                           ← 输出源文件清单，确认无遗漏
    ↓                                              （有遗漏则停止并报错）
[Phase 4] 并行: 各模块源文件读取                    ← N个Agent并行, 每个只返回精华
    ↓
[Phase 4.5] 方法分类判定                           ← 提取 depCount/cascadeDepth/staticCalls
    ↓                                              输出分类结果表（A/B/C/D/E）
                                                   标记需要 PowerMock 的模块
[Phase 4.8] 知识库预防性学习（新增）                 ← 读取 error-guide.md + MEMORY.md
    ↓                                              提取适用规则，输出简表
                                                   避免重复踩坑
[Phase 5] 并行: pom-test.xml创建 + 测试编写         ← 模板填充 + 按分类套用模板
    ↓                                              A/B → 模板三（单元测试）
                                                   C → 模板六（PowerMock集成测试）
                                                   D/E → 模板七（深度Mock链路集成测试）
                                                   （同步记录统计）
[Phase 6] 编译执行                                  ← swap pom → mvn clean test
    ↓
    ┌─ 遇到错误？
    │   ├─ 是 → [6.1] 读取 error-guide.md 匹配已知问题（新增）
    │   │        ├─ 匹配到 → 直接按方案修复，跳过探索
    │   │        └─ 未匹配 → 探索修复 → 修复后立即记录到 error-guide.md
    │   └─ 否 → 继续
    └─ 重试（增量构建 mvn test，不 clean）
    ↓
[Phase 7] 生成 HTML 报告 + 执行脚本                 ← 直接HTML + 可重复执行脚本
```

### 3.8 编译执行效率优化策略（通用）

#### 问题分析

在多模块 Maven 项目中，`mvn clean test` 的单次执行耗时可分解为：

| 阶段 | 耗时占比 | 说明 |
|------|---------|------|
| 主代码编译 | **~50%** | 200-1400 个源文件全量编译，每次 `clean` 后必须重来 |
| Maven 基础开销 | ~35% | JVM 启动、依赖解析、插件初始化、JaCoCo agent |
| 测试执行 | ~5% | 实际测试代码运行（通常 <5s） |
| 测试代码编译 | ~3% | 仅几个测试文件 |
| JaCoCo 报告 | ~7% | 生成覆盖率数据 |

**核心瓶颈**：主代码编译占了 50% 时间，但测试过程中源代码不会变，只有测试代码在反复修改。

#### 优化一：增量构建策略（省 40%/次）

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

#### 优化二：无依赖模块并行构建（省 30-40% 总时间）

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

#### 优化三：JaCoCo 延迟到最终报告（省 ~10s/模块）

**适用场景**：编译-修复循环中不需要覆盖率数据。

**规则**：
1. 开发阶段：`mvn test -Djacoco.skip=true`（跳过 JaCoCo agent + 报告）
2. 最终验证：`mvn clean test`（包含 JaCoCo，生成覆盖率数据）
3. 仅报告：`mvn jacoco:report`（不重新运行测试，只从已有 jacoco.exec 生成报告）

#### 优化四：预编译分离策略（大型项目适用）

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

#### 整合后的 Phase 6 执行流程

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

### 3.7 变更源文件读取精简规则

Agent 读取源文件时，**只提取以下信息**：

```
1. 类定义行: public class Xxx extends Yyy
2. @Autowired 依赖: 仅字段名和类型
3. 新增方法: 方法签名 + 方法体（仅新增/变更的方法）
4. 枚举值: 枚举常量 + 新增静态方法
5. Domain 新增字段: 字段名、类型、getter/setter
6. 方法体依赖分析（用于分类判定）:
   - 该方法调用了哪些 @Autowired 字段（depCount）
   - 是否存在级联调用：A返回值→B参数→C参数（cascadeDepth）
   - 是否调用了静态工具方法（staticCalls）
   - 是否调用了外部系统 API（externalApiCalls）
```

**提取方法体依赖分析的规则**：
- 只分析**新增/变更**的方法，不分析未变更的方法
- 对于每个方法，输出一行分类数据：
  `{方法名} | depCount=N | cascadeDepth=N | staticCalls=N | externalApis=N`

**明确不提取**：
- import 列表
- 未变更的方法
- SQL XML 文件内容
- 完整的类体
- 注释和 Javadoc
## 核心策略

### 策略零：测试类型自动分类（单元测试 vs 集成测试）

在编写测试前，必须先对每个源方法进行分类判定。分类结果决定使用哪种测试模板。

#### 分类判定规则

**步骤 1：扫描方法体，提取依赖调用信息**

对源文件中每个需要测试的方法，提取以下数据：

| 指标 | 定义 | 计算方法 |
|------|------|---------|
| `depCount` | 方法内部调用的**不同**依赖服务/DAO 数量 | 统计 `@Autowired` 字段在方法体内的调用次数（去重） |
| `cascadeDepth` | 级联调用深度 | A 返回值直接作为 B 的参数 → depth=2；B 返回值传给 C → depth=3；无级联 → depth=1 |
| `staticCalls` | 调用静态工具方法的数量 | 统计非本类的静态方法调用（如 `SolarExcelImportUtil.importExcel`、`StringUtils.isEmpty`） |
| `externalApiCalls` | 调用外部系统 API 的数量 | 统计 Eflow、Jenkins、企业微信等外部系统接口调用 |

**步骤 2：套用分类矩阵**

| 分类 | 条件 | 测试类型 | 模板 |
|------|------|---------|------|
| **A. 简单方法** | `depCount ≤ 3` **且** `cascadeDepth = 1` **且** `staticCalls = 0` | 单元测试 | 模板三（Mockito） |
| **B. 复杂方法** | `depCount ≤ 3` **且** `cascadeDepth ≤ 2` **且** `staticCalls = 0` | 单元测试 | 模板三（Mockito），逐层 mock |
| **C. 静态依赖方法** | `staticCalls > 0` **且** `depCount ≤ 3` | 集成测试 | 模板六（PowerMock） |
| **D. 深度链路方法** | `depCount ≥ 4` **或** `cascadeDepth ≥ 3` | 集成测试 | 模板七（深度 Mock 链路） |
| **E. 外部系统方法** | `externalApiCalls ≥ 2` **且** 存在多步骤交互 | 集成测试 | 模板七（深度 Mock 链路） |

**判断优先级**：E > D > C > B > A（从严格到宽松）

**步骤 3：输出分类结果表**

```
| 源方法 | depCount | cascadeDepth | staticCalls | externalApis | 分类 | 测试类型 |
|--------|----------|-------------|-------------|-------------|------|---------|
| isHasRight | 2 | 1 | 0 | 0 | A | 单元测试 |
| getTerminationTypeName | 2 | 1 | 0 | 0 | A | 单元测试 |
| resignRequestListen | 7 | 3 | 0 | 2 | D+E | 集成测试 |
| batchImpInventories | 3 | 1 | 1 | 0 | C | 集成测试 |
```

#### 分类后的执行规则

**单元测试（分类 A/B）**：
- 使用模板三（Service 层 Mockito 测试）
- `@ExtendWith(MockitoExtension.class)` + `@Mock` + `@InjectMocks`
- 每个 `@Mock` 必须覆盖被测方法的所有依赖路径
- 编写到与源文件同包的测试目录

**集成测试（分类 C/D/E）**：
- 分类 C（静态依赖）→ 使用模板六（PowerMock）
- 分类 D/E（深度链路）→ 使用模板七（深度 Mock 链路）
- 集成测试文件命名：`{ClassName}IntegrationTest.java`
- 集成测试放置位置：与单元测试同目录
- **必须按方法体内调用顺序逐层 mock**，不能跳过任何中间调用
- 如果某个中间依赖无法 mock（如私有构造器、final 类），在报告中标注为"无法覆盖"并说明原因

#### 集成测试依赖配置（pom-test.xml）

当源方法被分类为 C/D/E 时，需要在 pom-test.xml 中添加以下可选依赖：

```xml
<!-- PowerMock（分类 C：静态方法 mock） -->
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
```

**注意**：仅在模块中存在分类 C/D/E 的方法时才添加，不影响纯单元测试模块。

#### 增量执行流程调整

在原有流程的 Phase 4（源文件读取）和 Phase 5（测试编写）之间，插入 **Phase 4.5：方法分类判定**：

```
[Phase 4]   并行: 各模块源文件读取
    ↓
[Phase 4.5] 方法分类判定                           ← 新增
    ↓         对每个源方法提取 depCount/cascadeDepth/staticCalls
              输出分类结果表
              标记需要 PowerMock 依赖的模块
[Phase 5]   并行: pom-test.xml 创建 + 测试编写
    ↓         单元测试 → 模板三
              集成测试(C) → 模板六
              集成测试(D/E) → 模板七
```

#### 报告中集成测试的展示

HTML 报告的测试用例明细表中，增加"测试类型"列：
- 单元测试标记为 `badge-unit`
- 集成测试标记为 `badge-integration`（新增样式，蓝色）

HTML 报告的"未覆盖项"改名为"补充说明"，分为：
- "集成测试已覆盖"：分类为 C/D/E 且已编写集成测试的方法
- "建议集成测试"：因技术限制（final 类、私有构造器等）无法 mock 的方法
- "无需测试"：getter/setter、简单委托方法

### 策略一：分层测试覆盖

| 层级 | 测试类型 | 覆盖重点 | 工具 |
|------|---------|---------|------|
| Service（简单）| 单元测试 | 业务逻辑 | Mockito + @ExtendWith |
| Service（复杂）| 集成测试 | 业务逻辑+依赖链 | PowerMock / 深度Mock链路 |
| Domain | 单元测试 | POJO属性 | JUnit 5 |

> Controller（@WebMvcTest）和 Repository（@DataJpaTest）的测试模式委托给 `spring-boot-test` 技能。

### 策略二：优先级排序

1. **高价值代码优先** - 核心业务逻辑、复杂算法
2. **分支密集代码** - 多条件判断、循环
3. **公共API** - Controller端点
4. **工具类** - 静态方法、工具函数

## 报告生成要求

### 强制要求：生成 HTML 格式报告

完成单元测试后，**必须**生成 HTML 格式的单元测试报告和覆盖率报告。不允许使用 Markdown 格式替代 HTML 报告。

### 报告类型

1. **增量单元测试报告（HTML）** - 包含测试用例详情、执行结果、覆盖范围
2. **增量覆盖率报告（HTML）** - 包含行覆盖率、分支覆盖率、未覆盖项

> 报告结构规范（头部/表格/仪表盘等）、样式规范、输出路径和生成步骤详见 `assets/html-report-template.md`。

## 覆盖率检查清单

- [ ] Service层: 公共方法+异常分支
- [ ] 工具类: 静态方法
- [ ] 枚举类: 所有值
- [ ] 异常: 自定义异常类
- [ ] **方法分类判定已完成**（A/B 单元测试，C/D/E 集成测试）
- [ ] **知识库预防性学习已完成**（Phase 4.8: 读取 error-guide.md + MEMORY.md）
- [ ] **无依赖模块已并行构建**
- [ ] **错误修复前已匹配知识库**（Phase 6.1: 先查 error-guide.md 再修复）
- [ ] **错误修复循环使用增量构建**（`mvn test` 而非 `mvn clean test`）
- [ ] **HTML格式单元测试报告已生成**
- [ ] **HTML格式覆盖率报告已生成**
