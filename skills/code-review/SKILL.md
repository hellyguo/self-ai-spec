---
name: code-review
description: "代码审查框架：通用审查流程 + 语言特定规则引用，支持多语言代码审查"
---

# 代码审查框架

**审查原则**：理性、客观、实际、真实、不恭维、实事求是

## 概述

基于模块化设计的代码审查框架，包含：
1. **通用审查流程**：所有语言通用的审查步骤和原则
2. **语言规则引用**：按需加载语言特定审查规则
3. **组合审查支持**：支持多语言混合项目

**优势**：
- **减少LLM上下文负担**：每次只加载需要的语言规则
- **维护简单**：语言规则独立更新，互不影响
- **扩展灵活**：新增语言只需添加对应规则文件
- **复用性强**：其他技能可复用语言规则集

## 语言支持

### 直接源码文件

| 语言 | 文件类型 | 规则文件 | 加载指令 |
|------|----------|----------|----------|
| Java | `*.java` | `spec.java.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md` |
| Python | `*.py` | `spec.python.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.python.md` |
| C++ | `*.cpp *.hpp *.cxx *.hxx *.c *.h` | `spec.cpp.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.cpp.md` |
| Rust | `*.rs` | `spec.rust.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.rust.md` |
| ANSI C | `*.c *.h` | `spec.ansi_c.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.ansi_c.md` |
| JavaScript | `*.js *.mjs *.cjs` | `spec.js.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.js.md` |
| TypeScript | `*.ts *.tsx *.mts *.cts` | `spec.js.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.js.md` |
| Shell | `*.sh *.bash *.zsh` | `spec.shell.md` | `Read ${AI_SPEC_ROOT}/lang-spec/spec.shell.md` |

### SQL 来源（需拼接提取）

| 来源类型 | 文件/位置 | 审查要点 | 通用规则 |
|----------|-----------|----------|----------|
| SQL文件 | `*.sql` | SQL注入、性能、索引 | 通用安全规则 |
| MyBatis Mapper | `**/*Mapper.xml` | `$`符号拼接风险 | 通用安全规则 |
| 内嵌SQL | 各种源码 | 正则匹配审查 | 通用安全规则 |

## 审查模式

### 1. 全量审查（默认）

遍历项目所有源代码文件，自动识别语言并加载对应规则：

```bash
# 识别项目主要语言
detected_lang=$(detect_project_language)

# 加载对应语言规则
Read ${AI_SPEC_ROOT}/lang-spec/spec.${detected_lang}.md

# 执行审查
execute_code_review
```

### 2. 增量审查

根据 git/svn diff 进行增量审查：

```bash
# Git 增量审查
git diff main..feature-branch | review_diff

# SVN 增量审查  
svn diff -r 100:200 | review_diff
```

### 3. 混合语言审查

对于多语言项目，按文件类型加载不同规则：

```bash
# 多语言项目示例
for file in $(find . -name "*.java"); do
    Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md
    review_file $file
done

for file in $(find . -name "*.py"); do
    Read ${AI_SPEC_ROOT}/lang-spec/spec.python.md
    review_file $file
done
```

## 通用审查框架

### 1. 审查流程模板

**步骤1：项目分析**
- 识别项目技术栈
- 确定主要编程语言
- 分析项目结构

**步骤2：规则加载**
- 根据语言加载对应规则集
- 应用通用审查框架

**步骤3：代码遍历**
- 遍历所有源代码文件
- 理解代码结构和意图

**步骤4：执行审查**
- 应用通用审查规则
- 应用语言特定规则
- 记录问题和建议

**步骤5：生成报告**
- 汇总审查结果
- 提供改进建议
- 输出审查报告

### 2. 通用审查规则（所有语言适用）

#### 安全规则
- **敏感信息泄露**：检查硬编码的密码、密钥、API Key
- **SQL注入风险**：检查字符串拼接的SQL语句
- **XSS漏洞**：检查用户输入未转义
- **敏感数据内存残留**：检查内存中的敏感数据是否安全清除

#### 性能规则
- **资源泄漏**：检查文件句柄、数据库连接、网络连接是否关闭
- **内存泄漏**：检查动态分配的内存是否释放
- **循环性能**：检查嵌套循环、N+1查询
- **对象创建**：检查循环中不必要的对象实例化

#### 代码质量规则
- **重复代码**：检查可被复用的重复代码
- **方法长度**：检查方法是否过长（> 50行）
- **条件复杂度**：检查圈复杂度是否过高
- **命名规范**：检查模糊命名、命名不一致

#### 并发安全规则
- **线程安全**：检查共享状态是否同步
- **死锁风险**：检查锁顺序是否合理
- **优雅退出**：检查线程是否可控制退出

### 3. 语言规则引用机制

每个语言规则文件必须包含：

```markdown
# 语言审查规则：{语言名}

## 语言标识
- **文件类型**：{文件扩展名}
- **语法版本**：{语言版本}

## 语法特性审查
[该语言特有的语法检查点]

## 安全规则
[该语言特定的安全问题]

## 性能规则  
[该语言特有的性能陷阱]

## 最佳实践
[该语言的编码规范和最佳实践]

## 审查示例
[问题代码和改进代码示例]
```

## 审查执行器

### 单语言项目审查

```bash
# Java项目审查示例
lang="java"

# 1. 加载语言规则
Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md

# 2. 应用通用框架
- 执行安全审查
- 执行性能审查
- 执行代码质量审查

# 3. 应用语言特定规则
- 执行Java语法审查
- 检查Java最佳实践
- 验证Java并发模式

# 4. 生成报告
输出文件: docs/review/code-review-{yyyymmdd}-{seq%000}.md
```

### 多语言项目审查

```bash
# 混合项目审查示例
declare -A language_files=(
    ["java"]="*.java"
    ["python"]="*.py"
    ["javascript"]="*.js"
)

for lang in "${!language_files[@]}"; do
    pattern="${language_files[$lang]}"
    for file in $(find . -name "$pattern"); do
        # 加载对应语言规则
        Read ${AI_SPEC_ROOT}/lang-spec/spec.${lang}.md
        
        # 执行文件审查
        review_file_with_language $file $lang
    done
done
```

## 审查输出

### 文件命名规范

```text
docs/review/code-review-{yyyymmdd}-{seq%000}-{lang}.md
```

**示例**：
- `code-review-20250101-001-java.md`
- `code-review-20250101-002-python.md`
- `code-review-20250101-003-mixed.md`

### 报告结构模板

```markdown
# 代码审查报告

## 项目概述
- **项目语言**：{检测到的语言}
- **审查时间**：{时间戳}
- **使用规则**：${AI_SPEC_ROOT}/lang-spec/spec.{lang}.md

## 审查范围
[审查的文件范围、代码行数]

## 通用审查结果
### 安全问题
[通用安全规则检查结果]

### 性能问题  
[通用性能规则检查结果]

### 代码质量问题
[通用代码质量规则检查结果]

## 语言特定审查结果
[语言规则检查结果]

## 优秀设计
[值得表扬的设计和实现]

## 改进建议
### 必须修正
[严重问题，必须修复]

### 建议改进
[一般问题，建议优化]

### 参考建议
[优化建议，可选择性实施]

## 总结
[整体评价和建议]

---
Reviewed by {coding util}+{model name}
规则来源：${AI_SPEC_ROOT}/lang-spec/spec.{lang}.md
```

## 扩展和维护

### 新增语言支持

1. **创建语言规则文件**
   ```bash
   # 在 lang-spec 目录创建新语言规则
   touch ${AI_SPEC_ROOT}/lang-spec/spec.{new_lang}.md
   ```

2. **遵循规则模板**
   - 包含语言标识
   - 定义语法特性审查
   - 指定安全规则
   - 定义性能规则
   - 提供最佳实践
   - 包含审查示例

3. **更新语言支持表**
   - 在本文件的"语言支持"部分添加新语言
   - 指定文件类型和规则文件

### 规则更新

- **语言规则独立更新**：修改单个语言规则文件，不影响其他语言
- **通用框架独立更新**：修改通用规则，所有语言受益
- **向后兼容**：新规则不破坏已有审查流程

### 验证测试

```bash
# 验证规则文件格式
markdownlint ${AI_SPEC_ROOT}/lang-spec/spec.*.md

# 测试审查执行
模拟审查示例项目，验证规则加载和执行
```

## 最佳实践

### 1. 上下文优化
- 按需加载语言规则，避免加载不相关的规则
- 缓存常用语言规则，减少重复加载
- 增量审查时，只加载涉及的语言规则

### 2. 规则设计
- 保持语言规则文件紧凑，聚焦该语言特有内容
- 通用规则放在框架中，避免在各语言规则中重复
- 提供具体的代码示例，增强规则的可操作性

### 3. 审查效率
- 优先检查严重问题（安全漏洞、性能瓶颈）
- 批量处理相同模式的问题
- 提供具体的重构建议，不只是指出问题

### 4. 报告质量
- 问题定位准确（文件路径:行号）
- 提供具体的改进代码示例
- 区分问题严重等级（必须修正/建议改进/参考建议）

## 与其他技能集成

### 与 `lets-loop` 技能集成
```bash
# 针对循环代码的深度审查
/code-review   # 常规代码审查
/lets-loop     # 循环性能专项审查
```

### 与 `code-detect-dup` 技能集成  
```bash
# 代码重复度检测
/code-review       # 常规审查
/code-detect-dup   # 重复代码专项检测
```

### 与 `code-detect-problem` 技能集成
```bash
# 综合问题检测
/code-review           # 代码层面审查
/code-detect-problem   # 项目层面问题检测
```

---

**核心价值**：
1. **模块化设计**：通用框架 + 语言特定规则，解耦维护
2. **上下文友好**：按需加载，减少LLM token消耗
3. **扩展性强**：新增语言只需添加规则文件
4. **复用性高**：语言规则可被其他技能复用
5. **性能优化**：避免重复定义通用规则
