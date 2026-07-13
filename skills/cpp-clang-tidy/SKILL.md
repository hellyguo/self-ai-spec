---
name: cpp-clang-tidy
description: "Clang-Tidy 静态分析技能：使用 clang-tidy 进行 C/C++ 代码质量检测，支持自定义检查规则和自动修复"
---

# Clang-Tidy C/C++ 静态分析技能

## 概述

Clang-Tidy 是基于 Clang 的 C/C++ 静态分析工具，利用 Clang 的 AST 进行精确分析，可检测代码中的：

- **缺陷**：空指针解引用、逻辑错误、未初始化变量
- **代码风格**：命名规范、代码格式、现代 C++ 用法
- **性能**：不必要的拷贝、低效算法
- **安全**：缓冲区溢出、格式化字符串、未定义行为
- **现代 C++ 迁移**：C++11/14/17/20 新特性使用建议

## 工具位置

```bash
CLANG_TIDY=/usr/bin/clang-tidy
# 版本: Debian LLVM 19.1.7
```

## 前置条件

Clang-Tidy 需要 `compile_commands.json` 编译数据库：

```bash
# CMake 项目
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build

# 非 CMake 项目（使用 bear）
bear -- make

# 非 CMake 项目（使用 compiledb）
pip install compiledb
compiledb make
```

## 执行流程

### 步骤1：确定源代码路径

```bash
SRC_DIR=src           # 源代码目录
COMPILE_DB=build      # compile_commands.json 所在目录
```

### 步骤2：执行分析

```bash
# 检查单个文件
clang-tidy src/main.cpp -- -Iinclude

# 检查目录下所有 C/C++ 文件
find $SRC_DIR -name '*.cpp' -o -name '*.c' -o -name '*.h' -o -name '*.hpp' | \
  xargs clang-tidy -- -Iinclude

# 使用 compile_commands.json（推荐）
clang-tidy -p $COMPILE_DB src/main.cpp

# 批量检查（使用 run-clang-tidy 脚本）
run-clang-tidy -p $COMPILE_DB
```

### 步骤3：自动修复

```bash
# 应用自动修复（生成 .yaml 格式修复）
clang-tidy --fix src/main.cpp -- -Iinclude

# 修复并格式化
clang-tidy --fix-errors src/main.cpp -- -Iinclude

# 批量修复
find $SRC_DIR -name '*.cpp' | \
  xargs -I{} clang-tidy --fix-errors {} -p $COMPILE_DB
```

### 步骤4：指定输出格式

```bash
# 文本格式（默认）
clang-tidy src/main.cpp -- -Iinclude

# JSON 格式
clang-tidy --format-style=json src/main.cpp -- -Iinclude > tidy-report.json

# 导出修复建议（YAML）
clang-tidy --export-fixes=tidy-fixes.yaml src/main.cpp -- -Iinclude
```

## 常用检查规则

### 内置检查类别

| 类别 | 前缀 | 描述 |
| --- | --- | --- |
| 正确性 | `clang-diagnostic-*` | 编译器警告级别检查 |
| 正确性 | `clang-analyzer-*` | Clang 静态分析器检查 |
| 现代 C++ | `modernize-*` | 现代 C++ 用法建议 |
| 性能 | `performance-*` | 性能优化建议 |
| 可读性 | `readability-*` | 代码可读性改进 |
| 安全 | `bugprone-*` | 常见编程错误 |
| 安全 | `security-*` | 安全漏洞检查 |
| 并发 | `concurrency-*` | 并发相关检查 |
| 移植性 | `portability-*` | 平台移植性问题 |
| LLVM 相关 | `llvm-*` | LLVM 编码规范 |
| Google 规范 | `google-*` | Google C++ 编码规范 |
| CERT | `cert-*` | CERT 安全编码标准 |
| MISRA | `misra-*` | MISRA C/C++ 规范 |
| Boost | `boost-*` | Boost 库使用相关 |
| MPIT | `mpit-*` | MPI 相关检查 |
| OpenMP | `openmp-*` | OpenMP 相关检查 |
| HICPP | `hicpp-*` | High-Integrity C++ 规范 |
| LinuxKernel | `linuxkernel-*` | Linux 内核编码规范 |
| Fuchsia | `fuchsia-*` | Fuchsia 编码规范 |
| Zircon | `zircon-*` | Zircon 编码规范 |
| Objective-C | `objc-*` | Objective-C 相关检查 |
| Altera | `altera-*` | Altera OpenCL 相关 |
| Abseil | `abseil-*` | Abseil 库使用相关 |
| Darwin | `darwin-*` | Darwin 平台相关 |
| Android | `android-*` | Android 相关检查 |
| ES | `es-*` | Embedded Systems 相关 |

### 常用检查规则

| 规则 | 描述 |
| --- | --- |
| `bugprone-*` | 常见编程错误：整数溢出、除零、未初始化 |
| `performance-*` | 性能：不必要的拷贝、移动语义 |
| `modernize-*` | 现代 C++：auto、override、nullptr |
| `readability-*` | 可读性：命名、简化表达式 |
| `clang-analyzer-*` | 静态分析：空指针、内存泄漏 |
| `security-*` | 安全：缓冲区溢出、注入 |
| `concurrency-*` | 并发：死锁、竞态条件 |

## 配置文件（.clang-tidy）

项目根目录创建 `.clang-tidy` 文件：

```yaml
---
Checks: >
  *,
  -readability-*,
  -llvm-*,
  -fuchsia-*,
  -altera-*,
  bugprone-*,
  performance-*,
  modernize-*,
  readability-braces-around-statements,
  readability-identifier-naming,
CheckOptions:
  readability-identifier-naming.ClassCase: CamelCase
  readability-identifier-naming.FunctionCase: camelBack
  readability-identifier-naming.VariableCase: camelBack
  readability-identifier-naming.MemberCase: CamelCase
  readability-identifier-naming.MemberPrefix: 'm_'
  readability-identifier-naming.ConstantCase: UPPER_CASE
  modernize-use-auto.MinTypeNameLength: 5
  modernize-pass-by-value.ValuesOnly: true
WarningsAsErrors: '*'
HeaderFilterRegex: '.*'
AnalyzeTemporaryDtors: false
FormatStyle: file
```

## 典型使用场景

### 场景1：快速检查单个文件

```bash
clang-tidy src/main.cpp -- -Iinclude
```

### 场景2：全项目检查

```bash
# 使用 compile_commands.json
run-clang-tidy -p build -j 4

# 或手动
find src -name '*.cpp' | xargs clang-tidy -p build -j 4
```

### 场景3：特定检查规则

```bash
# 只检查安全和 bugprone 规则
clang-tidy --checks='bugprone-*,security-*' src/main.cpp -- -Iinclude

# 排除特定规则
clang-tidy --checks='*,-readability-*,-llvm-*' src/main.cpp -- -Iinclude
```

### 场景4：自动修复

```bash
# 修复 modernize 相关规则
clang-tidy --checks='modernize-*' --fix src/main.cpp -- -Iinclude

# 批量修复后验证
find src -name '*.cpp' | \
  xargs -I{} clang-tidy --fix-errors {} -p build && \
  run-clang-tidy -p build
```

## CI 集成

### GitHub Actions

```yaml
name: Clang-Tidy
on: [push, pull_request]
jobs:
  clang-tidy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure
        run: cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build
      - name: Run clang-tidy
        run: run-clang-tidy -p build
```

### CMake 集成

```cmake
# 添加 clang-tidy 目标
set(CMAKE_CXX_CLANG_TIDY
    clang-tidy
    --checks='bugprone-*,performance-*,modernize-*'
    --warnings-as-errors='*'
)

# 或作为独立目标
add_custom_target(tidy
    COMMAND run-clang-tidy -p ${CMAKE_BINARY_DIR} -j 4
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running clang-tidy..."
)
```

### Makefile 集成

```makefile
CLANG_TIDY=/usr/bin/clang-tidy
COMPILE_DB=build

clang-tidy:
    run-clang-tidy -p $(COMPILE_DB) -j 4

clang-tidy-fix:
    find src -name '*.cpp' | \
      xargs -I{} $(CLANG_TIDY) --fix-errors {} -p $(COMPILE_DB)
```

## 分析结果处理

### 统计问题类型

```bash
clang-tidy --format-style=json src/main.cpp -- -Iinclude | \
  jq -r '.[].DiagnosticName' | sort | uniq -c | sort -nr
```

### 提取高危问题

```bash
clang-tidy src/main.cpp -- -Iinclude 2>&1 | grep -E '(error|warning):'
```

### 生成摘要

```bash
echo "=== Clang-Tidy 分析报告 ==="
clang-tidy --format-style=json src/main.cpp -- -Iinclude | \
  jq -r '.[].DiagnosticName' | sort | uniq -c | sort -rn | \
  awk '{print $2 ": " $1}'
```

## 与 Cppcheck 对比

| 特性 | Clang-Tidy | Cppcheck |
| --- | --- | --- |
| 分析引擎 | Clang AST | 自定义解析器 |
| 精度 | 高（基于真实 AST） | 中等 |
| 编译数据库 | 必需 | 可选 |
| 自动修复 | 支持 | 不支持 |
| 检查规则数量 | 500+ | 200+ |
| 配置灵活性 | 极高（.clang-tidy） | 中等 |
| 现代 C++ 支持 | 优秀 | 一般 |
| 分析速度 | 较慢（需编译） | 快 |

## 最佳实践

1. **使用 compile_commands.json**：确保分析精度
2. **项目级 .clang-tidy**：统一团队规范
3. **渐进式采用**：从 `bugprone-*,performance-*,modernize-*` 开始
4. **自动修复优先**：先用 `--fix` 处理可自动修复项
5. **CI 集成**：将 clang-tidy 纳入 CI 流程
6. **定期更新**：随 LLVM 版本更新检查规则

## 注意事项

1. **需要编译数据库**：没有 `compile_commands.json` 时需手动指定 `-I` 参数
2. **分析速度较慢**：大型项目建议使用 `run-clang-tidy` 并行分析
3. **误报处理**：使用 `// NOLINT` 或 `.clang-tidy` 配置抑制
4. **`--fix` 可能不完整**：部分修复需要手动调整，修复后务必编译验证

---
**技能版本**: 1.0.0
**工具版本**: Clang-Tidy 19.1.7 (Debian LLVM)
**适用项目**: C/C++ 项目（需要 compile_commands.json）
**输出位置**: 标准输出或指定文件
