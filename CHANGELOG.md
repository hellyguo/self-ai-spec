# 更新历史

## 2026-07-09

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