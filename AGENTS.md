# AGENTS.md 模板仓库指南

## 项目概述

本仓库提供多语言 AGENTS.md 模板，用于指导 AI 编码代理在项目中的行为规范。每个模板针对特定编程语言优化，包含角色定位、编码规范、构建命令等。

## 模板文件说明

| 文件 | 用途 |
|------|------|
| `AGENTS.java.md` | Java 项目模板（最完整，180行） |
| `AGENTS.python.md` | Python 项目模板 |
| `AGENTS.rust.md` | Rust 项目模板 |
| `AGENTS.js.md` | JavaScript/TypeScript 项目模板 |
| `AGENTS.cpp.md` | C++ 项目模板 |
| `AGENTS.ansi_c.md` | ANSI C 项目模板 |
| `AGENTS.blank.md` | 空白模板 |

## 使用方法

1. 根据项目技术栈选择对应模板
2. 将模板内容复制到项目根目录的 `AGENTS.md` 文件
3. 根据项目实际情况补充以下内容：
   - 构建/测试/ lint 命令
   - 项目特定编码规范
   - 环境配置信息

## 通用编码规范

### 注释规范

- 文件顶部添加总体功能说明注释
- 重点代码添加详尽注释，说明意图和逻辑
- 不使用行尾注释，注释独占一行

### 命名约定

- 静态不可变变量：全大写蛇形命名（`MAX_CONNECTION_COUNT`）
- 静态可变变量：小写驼峰或蛇形命名
- 类/类型：帕斯卡命名法（`UserService`，`HttpClient`）
- 方法/函数：小写驼峰命名（`getUserById`，`processRequest`）
- 变量：小写驼峰命名（`userName`，`itemCount`）
- 常量：全大写蛇形命名（`DEFAULT_TIMEOUT_MS`）

### 布尔命名

- 布尔方法/变量使用 `is`、`has`、`can`、`should` 前缀
- 示例：`isActive`、`hasPermission`、`canRead`、`shouldRetry`

### 类/模块设计

- 遵循单一职责原则，大类拆分为职责明确的小类
- 优先组合而非继承
- 工具类使用 `final` 修饰 + 私有构造函数
- 常量类使用 `final` 修饰 + 私有构造函数 + `static final` 字段

### 错误处理

- 尽早验证输入参数，快速失败
- 使用描述性错误消息
- 区分可恢复错误和不可恢复错误
- 记录错误上下文便于调试

## Git 提交规范

### 约定式提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 提交类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响逻辑）
- `refactor`: 重构（非新功能、非 bug 修复）
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 提交规则

1. 每次产出文件后执行 git 提交
2. 仅以当前 `user.name` 提交，不推送到远端
3. 提交消息使用中文或英文，保持一致
4. 一个提交只做一件事

## 模板扩展指南

### 构建命令示例

```markdown
## 构建命令

### Java (Maven)
- 构建：`mvn clean package -DskipTests`
- 测试：`mvn test`
- 单个测试：`mvn test -Dtest=ClassName#methodName`
- Lint：`mvn checkstyle:check`

### Python
- 构建：`python -m build`
- 测试：`pytest tests/`
- 单个测试：`pytest tests/test_file.py::test_function`
- Lint：`ruff check .`

### Rust
- 构建：`cargo build --release`
- 测试：`cargo test`
- 单个测试：`cargo test test_function_name`
- Lint：`cargo clippy`

### JavaScript/TypeScript
- 构建：`npm run build`
- 测试：`npm test`
- 单个测试：`npm test -- -t "test name"`
- Lint：`npm run lint`
```

### 环境信息模板

```markdown
## 环境信息

- 运行时版本：[填写具体版本]
- 包管理器：[填写具体工具]
- 构建工具：[填写具体工具]
- 关键依赖：[列出核心依赖及版本]
```

## 架构师角色定位

作为 AI 编码代理，应具备以下能力：

1. **需求分析能力**
   - 提供多套方案，以上、中、下三策形式呈现
   - 分析各方案优劣及适用场景

2. **设计能力**
   - 考虑非功能性需求：安全性、可扩展性、可用性、可观测性、性能
   - 运用适当设计模式
   - 遵循 SOLID 原则

3. **编码能力**
   - 熟练掌握目标语言特性
   - 编写可读、可维护、高性能代码
   - 注重代码质量与测试覆盖

## 相关资源

- [约定式提交规范](https://www.conventionalcommits.org/)
- [Google 编码规范](https://google.github.io/styleguide/)
- [各语言官方编码规范](https://example.com)