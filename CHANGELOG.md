# 更新历史

## 2026-07-12

### 新增局部代码修改技能

- **code-part-modification技能**：局部代码修改技能，支持最小化修改完成功能
  - 核心原则：确保无蝴蝶效应，支持独立测试验证和全量关联检查
  - 位置：`skills/code-part-modification/SKILL.md`

### 提交记录

- Commit: `cab4697` feat: add code-part-modification skill for minimal code modification

## 2026-07-10

### 新增静态分析技能

- **cpp-check技能**：Cppcheck静态分析，检测C/C++代码缺陷、未定义行为和安全漏洞
  - 位置：`skills/cpp-check/SKILL.md`
- **cpp-tscancode技能**：TscanCode（腾讯开源）C/C++代码检测工具
  - 位置：`skills/cpp-tscancode/SKILL.md`
- **shell-check技能**：ShellCheck静态分析，检测Shell脚本语法错误和潜在缺陷
  - 位置：`skills/shell-check/SKILL.md`

### 新增系统定性评估技能

- **qualitative-assessment技能**：基于全面分析输出，从设计、开发、运维、非功能等维度总结系统性质
  - 位置：`skills/qualitative-assessment/SKILL.md`
- **full-analysis技能增强**：完整分析流程末尾增加定性评估环节
  - 流程：设计解构->代码审查->重复检测->问题侦测->定性评估

### code-deconstruct技能增强

- 新增网络估算工作流，支持网络层面的分析

### 脚本系统改进

- **无参启动逻辑优化**：改进 oc/cdbd/clc 脚本在无参数时的启动逻辑
  - 既无会话ID也无AGENTS.md时显示详细帮助信息
- **金融行情系统分类修正**：澄清定性评估中的金融行情系统分类

### 提交记录

- Commit: `a530ae6` feat: add cpp-check and cpp-tscancode skills
- Commit: `20a4791` feat: add shell-check skill for shell script static analysis
- Commit: `39ccfda` feat(analysis): add qualitative-assessment skill and enhance full-analysis
- Commit: `f3bc9fd` feat: add network estimation workflow to code-deconstruct skill
- Commit: `1001687` fix: 改进AI工具脚本的无参启动逻辑
- Commit: `c4adc53` fix(assessment): clarify financial quote system classification

## 2026-07-09

### code-review技能模块化重构

- **模块化框架**：将code-review重构为通用审查框架 + 语言特定规则的分层架构
  - 通用框架：`skills/code-review/SKILL.md` + `docs/code-review-framework.md`
  - 语言规则：`lang-spec/spec.{lang}.md` 按需加载
- **内容解构完成**：完成code-review技能内容向模块化架构的解构
- **代码示例简化**：精简code-review技能中的代码示例

### 企业级Java代码审查规则

- **新增企业级规则**：从备份恢复企业级Java代码审查规则
- **Java线程创建与管理规范**：新增企业级Java线程创建与管理规范
  - 覆盖线程创建方式、管理策略、风险防范

### 安全审查规则增强

- **时钟回拨攻击检测**：为C++和ANSI C新增时钟回拨攻击检测规则
- **无限循环审查规范**：增强无限循环审查，强调不优雅退出问题

### 路径引用统一

- **环境变量替换硬编码路径**：统一所有路径引用，使用 `${AI_SPEC_ROOT}` 环境变量替换硬编码路径

### 新增Java静态分析技能

- **java-check-spotbugs技能**：SpotBugs静态分析工具技能，支持Find Security Bugs和fb-contrib插件集成
  - 检测范围：代码缺陷、安全漏洞、性能问题
  - 工具版本：SpotBugs 4.7.3（最高支持Java 17）
  - 位置：`skills/java-check-spotbugs/SKILL.md`
  
- **java-check-pmd技能**：PMD代码质量分析工具技能
  - 检测范围：编码规范、代码坏味道、复杂度分析、安全漏洞
  - 工具版本：PMD 6.19.0（支持Java 25）
  - 位置：`skills/java-check-pmd/SKILL.md`

### 工具验证结果

- **PMD验证成功**：工具工作正常，正确检测出空catch块、未使用变量等问题
- **SpotBugs版本兼容性**：SpotBugs 4.7.3因ASM版本限制不支持Java 25，需要Java 17或更早版本
- **技能文档更新**：在SpotBugs技能中添加版本兼容性说明和解决方案

### 技能列表更新

- 在README.md中添加两个新技能到Java开发工具部分
- 更新技能描述和适用场景说明

### 提交记录

- Commit: `a3cfa32` refactor: 统一路径引用，使用环境变量替换硬编码路径
- Commit: `1bcce76` feat: 增强无限循环审查规范，强调不优雅退出问题
- Commit: `d733948` refactor: 简化code-review技能中的代码示例
- Commit: `0ec5e64` feat: refactor code-review skill to modular framework
- Commit: `069c4ee` feat: add enterprise-level Java code review rules from backup
- Commit: `6cc8b1e` feat: add clock rollback attack detection for C++ and ANSI C
- Commit: `2503f25` feat: complete code-review skill content decomposition to modular architecture
- Commit: `9281533` feat: 添加Java线程创建与管理规范（企业级要求）
- Commit: `a193e16` feat: add java-check-spotbugs and java-check-pmd skills

## 2025-07-07

### 新增功能

- **新增 Shell 支持**：添加 Shell/Bash 项目的语言规范和代理模板
- **脚本系统重构**：支持符号链接部署，环境变量驱动架构
- **架构优化**：公共函数集中在 `common.sh`，各脚本独立验证环境变量

### 技术改进

- **路径引用统一**：将所有硬编码的 `/disk2/helly_data/code/markdown/self-ai-spec` 路径替换为 `${AI_SPEC_ROOT}` 环境变量
- **脚本错误处理**：修复 `oc`/`cdbd`/`clc` 脚本在没有参数和会话ID时的友好提示
- **文档规范**：将更新历史从 README.md 分离到 CHANGELOG.md
- **安全意识**：在 AGENTS.md 中添加 AI工具脚本测试安全提醒

### 技能更新

- **Java编码规范**：完善 ForkJoinPool 使用规范，增加任务排队与延时风险章节
- **AI工具测试提醒**：记录 memrec 避免在测试中直接运行交互式工具脚本

## 2025-07-06

### code-review 技能重要更新

- **敏感数据审查通用化**：明确敏感数据审查为所有语言通用必须项（不是C/C++特有）
- **安全审查扩展**：增加以下审查要点：
  - 敏感信息泄露
  - 敏感数据内存残留  
  - 敏感字段输出
  - 安全日志处理
- **专项检查重命名**：专项检查6重命名为"敏感字段输出审查（所有语言通用）"
- **多语言示例**：提供Java/Python/JavaScript敏感信息泄露的代码示例

### 新增语言规范

- **Shell/Bash 规范**：`spec.shell.md` 和 `ci.shell.md` 语言规范
- **Shell 代理模板**：`AGENTS.shell.md` 代理配置文件

## 2025-07-05

### 脚本系统重构

- **环境变量驱动**：所有脚本使用 `AI_SPEC_ROOT` 环境变量定位资源
- **符号链接支持**：脚本支持符号链接到任意目录（如 `~/bin/`）
- **会话管理**：优化会话ID保存和恢复逻辑
- **错误处理**：增强环境变量缺失时的错误提示

### 新增技能

- **merge-agents-md**：通用 AGENTS.md 合并技能，支持多种编程语言模板

## 架构演进

### 路径引用模式演进

- **原始模式**：硬编码绝对路径 → 不灵活，无法移动仓库
- **当前模式**：环境变量 `${AI_SPEC_ROOT}` → 灵活部署，支持符号链接
- **示例**：

  ```
  旧：Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
  新：Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md
  ```

### 脚本架构优化

- **分离公共函数**：`common.sh` 包含会话管理核心逻辑
- **独立验证**：每个脚本独立验证 `AI_SPEC_ROOT` 环境变量
- **错误提示友好**：无参数且无会话ID时显示详细帮助信息

## 技术备忘

### 重要技术决策

1. **路径引用标准化**：所有资源文件引用使用 `${AI_SPEC_ROOT}` 前缀
2. **环境变量必须性**：`AI_SPEC_ROOT` 是脚本运行的必须条件
3. **符号链接优先**：推荐使用符号链接部署到用户bin目录
4. **会话隔离**：opencode、codebuddy、claudecode 各自管理会话状态

### 安全提醒

- **脚本测试注意事项**：避免在测试中直接运行 `oc`、`cdbd`、`clc`、`qcc` 脚本
- **交互式工具风险**：这些脚本启动交互式AI工具会接管终端，难以退出
- **安全测试方法**：优先使用 `bash -n` 语法检查，或通过环境变量和重定向测试
