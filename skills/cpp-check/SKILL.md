---
name: cpp-check
description: "Cppcheck静态分析技能：使用Cppcheck进行C/C++代码质量分析，检测缺陷、未定义行为、安全漏洞和代码风格问题"
---

# Cppcheck C/C++静态分析技能

## 概述

Cppcheck是C/C++静态分析工具，无需编译即可检测代码中的：

- **缺陷**：空指针解引用、数组越界、内存泄漏
- **未定义行为**：整数溢出、未初始化变量、空指针
- **安全漏洞**：缓冲区溢出、格式化字符串漏洞
- **代码风格**：冗余代码、复杂表达式

## 工具位置

```bash
CPPCHECK=/usr/bin/cppcheck
# 版本: Cppcheck 2.17.1
```

## 执行流程

### 步骤1：确定源代码路径

```bash
SRC_DIR=src  # 根据项目结构调整
```

### 步骤2：执行分析

```bash
# 基础检查（默认级别）
$CPPCHECK --enable=warning $SRC_DIR

# 完整检查（含风格、性能、可移植性）
$CPPCHECK --enable=all $SRC_DIR 2> cppcheck-full.txt

# 仅缺陷检查（不含风格）
$CPPCHECK --enable=warning,information $SRC_DIR 2> cppcheck-defects.txt

# 安全漏洞专项
$CPPCHECK --enable=warning --check-level=exhaustive $SRC_DIR 2> cppcheck-security.txt
```

### 步骤3：指定输出格式

```bash
# 文本格式（默认，输出到stderr）
$CPPCHECK --enable=all $SRC_DIR 2> cppcheck.txt

# XML格式
$CPPCHECK --enable=all --xml $SRC_DIR 2> cppcheck.xml

# XML版本2（推荐，用于CI集成）
$CPPCHECK --enable=all --xml-version=2 $SRC_DIR 2> cppcheck-v2.xml

# JSON格式
$CPPCHECK --enable=all --output-file=cppcheck.json --template=json $SRC_DIR
```

## 常用参数

| 参数 | 描述 | 示例 |
| ------ | ------ | ------ |
| `--enable=<id>` | 启用检查类别 | `warning`, `style`, `performance`, `portability`, `information`, `all` |
| `--check-level=<level>` | 分析深度 | `normal`, `exhaustive` |
| `--std=<standard>` | C/C++标准 | `c11`, `c17`, `c++11`, `c++17`, `c++20` |
| `--platform=<type>` | 目标平台 | `unix32`, `unix64`, `win32`, `win64`, `native` |
| `--language=<lang>` | 强制语言 | `c`, `c++` |
| `--suppress=<id>` | 抑制特定警告 | `unusedFunction`, `missingInclude` |
| `--suppress=<id>:<file>` | 抑制文件级警告 | `unusedFunction:src/main.cpp` |
| `--exit-on-suppression` | 遇抑制项时退出 | 用于验证抑制列表 |
| `-I <dir>` | 包含目录 | `-I include -I /usr/include` |
| `-D<macro>` | 定义宏 | `-DDEBUG -DNDEBUG` |
| `-U<macro>` | 取消宏定义 | `-UDEBUG` |
| `--output-file=<file>` | 输出文件 | `--output-file=report.txt` |
| `--project=<file>` | 项目文件 | `--project=compile_commands.json` |
| `--filter=<file>` | 过滤文件 | `--filter=cppcheck-filter.txt` |
| `--addon=<name>` | 加载插件 | `--addon=misra --addon=cert` |
| `--max-configs=<n>` | 最大配置数 | `--max-configs=20` |
| `--force` | 强制检查所有配置 | 跳过配置限制 |
| `-j <n>` | 并行检查线程数 | `-j 4` |

## 检查类别详解

### 1. warning（默认启用）

| 检查项 | 描述 |
| -------- | ------ |
| 空指针解引用 | 解引用可能为NULL的指针 |
| 数组越界 | 数组索引超出范围 |
| 整数溢出 | 有符号整数运算溢出 |
| 未初始化变量 | 使用未初始化的变量 |
| 内存泄漏 | 动态分配的内存未释放 |
| 双重释放 | 同一内存释放两次 |
| 资源泄漏 | 文件句柄等资源未关闭 |

### 2. style

| 检查项 | 描述 |
| -------- | ------ |
| 冗余代码 | 永远不会执行的代码 |
| 复杂表达式 | 可简化的条件表达式 |
| 变量作用域 | 变量作用域可缩小 |
| 重复条件 | if/else分支条件重复 |

### 3. performance

| 检查项 | 描述 |
| -------- | ------ |
| 按值传递 | 大对象按值传递应改为引用 |
| 冗余拷贝 | 不必要的对象拷贝 |
| 低效算法 | 可优化的算法模式 |

### 4. portability

| 检查项 | 描述 |
| -------- | ------ |
| 平台依赖 | 依赖特定平台行为 |
| 类型大小 | 假设特定类型大小 |
| 未指定行为 | 依赖未指定的求值顺序 |

## 与构建系统集成

### CMake集成

```cmake
# 生成compile_commands.json
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# CTest集成
add_test(NAME cppcheck
  COMMAND /usr/bin/cppcheck --enable=all --xml-version=2
          --project=${CMAKE_BINARY_DIR}/compile_commands.json
          2>${CMAKE_BINARY_DIR}/cppcheck.xml)
```

### Makefile集成

```makefile
cppcheck:
 /usr/bin/cppcheck --enable=all --xml-version=2 \
  -I include -I src \
  src/ 2>cppcheck.xml
```

### compile_commands.json

```bash
# CMake自动生成
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

# Bear工具生成（非CMake项目）
bear -- make

# 使用compile_commands.json分析
$CPPCHECK --enable=all --project=compile_commands.json 2> cppcheck.xml
```

## 抑制警告

### 行内抑制

```c
// cppcheck-suppress memoryLeak
char* p = malloc(100);
```

### 文件级抑制

```bash
$CPPCHECK --suppress=unusedFunction:src/main.cpp --enable=all $SRC_DIR
```

### 抑制文件（suppressions.txt）

```text
unusedFunction
memoryLeak:src/legacy.c
uninitvar:src/parser.c:100
```

```bash
$CPPCHECK --suppressions-list=suppressions.txt --enable=all $SRC_DIR
```

## MISRA C/C++检查

```bash
# MISRA C 2012检查
$CPPCHECK --addon=misra --enable=style $SRC_DIR 2> misra.txt

# MISRA C++ 2008检查
$CPPCHECK --addon=misra-cpp2008 --enable=style $SRC_DIR 2> misra-cpp.txt
```

## 分析结果处理

### 统计问题类型

```bash
grep -oP '\[(\w+)\]' cppcheck.txt | sort | uniq -c | sort -nr
```

### 提取高危问题

```bash
grep -E '(error|warning):' cppcheck.txt
```

### 生成摘要

```bash
echo "=== Cppcheck分析报告 ==="
echo "总问题数: $(grep -c '\[' cppcheck.txt)"
echo "错误: $(grep -c '(error)' cppcheck.txt)"
echo "警告: $(grep -c '(warning)' cppcheck.txt)"
echo "风格: $(grep -c '(style)' cppcheck.txt)"
```

## 最佳实践

1. **渐进式采用**：先启用warning，逐步增加style、performance
2. **使用compile_commands.json**：确保头文件路径正确
3. **并行分析**：大型项目使用`-j`参数加速
4. **抑制管理**：对误报使用抑制，定期审查抑制列表
5. **CI集成**：将cppcheck纳入持续集成流程

---
**技能版本**: 1.0.0
**工具版本**: Cppcheck 2.17.1
**适用项目**: C/C++项目
**输出位置**: 当前目录下的cppcheck-*.txt文件
