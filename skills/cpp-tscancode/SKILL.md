---
name: cpp-tscancode
description: "TscanCode静态分析技能：使用TscanCode（腾讯开源）进行C/C++代码质量分析，检测缺陷、安全漏洞和代码风格问题"
---

# TscanCode C/C++静态分析技能

## 概述

TscanCode是腾讯开源的C/C++静态分析工具，可检测代码中的：

- **缺陷**：空指针解引用、数组越界、内存泄漏
- **安全漏洞**：缓冲区溢出、格式化字符串漏洞
- **代码风格**：冗余代码、复杂表达式
- **性能问题**：低效算法、冗余操作

## 工具位置

```bash
TSCANCODE=/home/helly/app/TscanCode.linux/tscancode
```

## 执行流程

### 步骤1：确定源代码路径

```bash
SRC_DIR=src  # 根据项目结构调整
```

### 步骤2：执行分析

```bash
# 基础检查（默认级别）
$TSCANCODE $SRC_DIR

# 完整检查（含风格、性能、可移植性）
$TSCANCODE --enable=all $SRC_DIR 2> tscancode-full.txt

# 仅警告检查
$TSCANCODE --enable=warning $SRC_DIR 2> tscancode-warning.txt

# 风格和性能检查
$TSCANCODE --enable=style,performance $SRC_DIR 2> tscancode-style.txt
```

### 步骤3：指定输出格式

```bash
# 文本格式（默认，输出到stderr）
$TSCANCODE --enable=all $SRC_DIR 2> tscancode.txt

# XML格式
$TSCANCODE --enable=all --xml $SRC_DIR 2> tscancode.xml

# 静默模式（不显示进度）
$TSCANCODE --quiet --enable=all $SRC_DIR 2> tscancode.txt
```

## 常用参数

| 参数 | 描述 | 示例 |
| ------ | ------ | ------ |
| `--enable=<id>` | 启用检查类别 | `warning`, `style`, `performance`, `portability`, `information`, `all` |
| `-I <dir>` | 包含目录 | `-I include -I /usr/include` |
| `-D<macro>` | 定义宏 | `-DDEBUG -DNDEBUG` |
| `-U<macro>` | 取消宏定义 | `-UDEBUG` |
| `-j <n>` | 并行检查线程数 | `-j 4` |
| `--quiet` | 静默模式，不显示进度 | `--quiet` |
| `--xml` | XML格式输出 | `--xml` |
| `-h, --help` | 显示帮助 | `--help` |

## 检查类别详解

### 1. warning（警告）

| 检查项 | 描述 |
| -------- | ------ |
| 空指针解引用 | 解引用可能为NULL的指针 |
| 数组越界 | 数组索引超出范围 |
| 整数溢出 | 有符号整数运算溢出 |
| 未初始化变量 | 使用未初始化的变量 |
| 内存泄漏 | 动态分配的内存未释放 |
| 双重释放 | 同一内存释放两次 |

### 2. style（风格）

| 检查项 | 描述 |
| -------- | ------ |
| 冗余代码 | 永远不会执行的代码 |
| 复杂表达式 | 可简化的条件表达式 |
| 变量作用域 | 变量作用域可缩小 |
| 命名规范 | 变量命名不符合规范 |

### 3. performance（性能）

| 检查项 | 描述 |
| -------- | ------ |
| 按值传递 | 大对象按值传递应改为引用 |
| 冗余拷贝 | 不必要的对象拷贝 |
| 低效算法 | 可优化的算法模式 |

### 4. portability（可移植性）

| 检查项   | 描述               |
|----------|--------------------|
| 平台依赖 | 依赖特定平台行为   |
| 类型大小 | 假设特定类型大小   |

### 5. information（信息）

| 检查项   | 描述             |
|----------|------------------|
| 缺少包含 | 头文件包含缺失   |
| 配置问题 | 编译配置问题     |

### 6. unusedFunction（未使用函数）

| 检查项     | 描述                   |
|------------|------------------------|
| 未使用函数 | 定义但未被调用的函数   |

## 典型使用场景

### 场景1：快速检查

```bash
# 只检查警告级别问题
$TSCANCODE --enable=warning $SRC_DIR 2> tscancode-warning.txt
```

### 场景2：完整检查

```bash
# 启用所有检查，多线程加速
$TSCANCODE --enable=all -j 4 $SRC_DIR 2> tscancode-full.txt
```

### 场景3：特定目录检查

```bash
# 检查特定目录，指定包含路径
$TSCANCODE --enable=all -I include -I third_party/include src/core/ 2> tscancode-core.txt
```

### 场景4：CI集成

```bash
# XML输出用于CI解析
$TSCANCODE --quiet --enable=warning --xml $SRC_DIR 2> tscancode-report.xml
```

### 场景5：预处理宏控制

```bash
# 定义宏启用特定代码路径
$TSCANCODE --enable=all -DDEBUG -DENABLE_FEATURE_X $SRC_DIR 2> tscancode-debug.txt

# 取消宏忽略特定代码路径
$TSCANCODE --enable=all -UDEBUG $SRC_DIR 2> tscancode-release.txt
```

## 与构建系统集成

### CMake集成

```cmake
# 创建检查目标
add_custom_target(tscancode
  COMMAND /home/helly/app/TscanCode.linux/tscancode
    --enable=all
    --quiet
    --xml
    ${CMAKE_SOURCE_DIR}/src
    2> ${CMAKE_BINARY_DIR}/tscancode.xml
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Running TscanCode static analysis..."
)
```

### Makefile集成

```makefile
TSCANCODE=/home/helly/app/TscanCode.linux/tscancode

tscancode:
 $(TSCANCODE) --enable=all --quiet -I include src/ 2>tscancode.xml
```

### Shell脚本封装

```bash
#!/bin/bash
# tscancode-check.sh

TSCANCODE=/home/helly/app/TscanCode.linux/tscancode
SRC_DIR=${1:-src}
OUTPUT=${2:-tscancode-report.txt}

echo "=== TscanCode 分析开始 ==="
echo "源代码目录: $SRC_DIR"
echo "输出文件: $OUTPUT"

$TSCANCODE --enable=all --quiet -j 4 $SRC_DIR 2> "$OUTPUT"

echo "=== 分析完成 ==="
echo "问题数量: $(grep -c '\[' "$OUTPUT" 2>/dev/null || echo 0)"
```

## 分析结果处理

### 统计问题类型

```bash
grep -oP '\[.*?\]' tscancode.txt | sort | uniq -c | sort -nr
```

### 提取高危问题

```bash
grep -E '(error|warning):' tscancode.txt
```

### 生成摘要报告

```bash
#!/bin/bash
echo "=== TscanCode 分析报告 ==="
echo "分析时间: $(date)"
echo "源代码目录: $SRC_DIR"
echo "---"
echo "总问题数: $(grep -c '\[' tscancode.txt)"
echo "错误: $(grep -c '(error)' tscancode.txt)"
echo "警告: $(grep -c '(warning)' tscancode.txt)"
echo "风格: $(grep -c '(style)' tscancode.txt)"
echo "性能: $(grep -c '(performance)' tscancode.txt)"
```

## 与Cppcheck对比

| 特性 | TscanCode | Cppcheck |
| ------ | ----------- | ---------- |
| 来源 | 腾讯开源 | 开源社区 |
| 中文支持 | 原生支持 | 部分 |
| MISRA规则 | 支持 | 支持（插件） |
| 检查规则 | 类似 | 更丰富 |
| XML输出 | 支持 | 支持 |
| 并行分析 | 支持 | 支持 |

## 最佳实践

1. **增量检查**：大型项目使用`-j`并行加速
2. **分级处理**：先修复error，再处理warning，最后优化style
3. **包含路径**：确保`-I`参数包含所有必要的头文件路径
4. **宏定义**：正确设置`-D`参数以覆盖所有代码路径
5. **CI集成**：将TscanCode纳入持续集成流程

## 注意事项

1. **输出到stderr**：TscanCode默认输出到stderr，需要重定向`2>`捕获
2. **完整扫描**：`--enable=all`会启用unusedFunction，建议全项目扫描
3. **头文件路径**：确保`-I`路径正确，否则可能误报缺少包含

---
**技能版本**: 1.0.0
**工具位置**: /home/helly/app/TscanCode.linux/tscancode
**适用项目**: C/C++项目
**输出位置**: 当前目录下的tscancode-*.txt文件
