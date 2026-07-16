---
name: cpp-tscancode
description: "TscanCode静态分析技能：使用TscanCode（腾讯开源）进行C/C++代码质量分析，检测缺陷、安全漏洞和代码风格问题"
---

# TscanCode C/C++静态分析技能

## 工具位置

```bash
TSCANCODE=/home/helly/app/TscanCode.linux/tscancode
```

## 执行流程

1. **确定源代码路径**：`SRC_DIR=src`（根据项目结构调整）
1. **执行分析**（按需选择级别）：

```bash
# 基础检查
$TSCANCODE $SRC_DIR

# 完整检查（含风格、性能、可移植性）
$TSCANCODE --enable=all $SRC_DIR 2> tscancode-full.txt

# 仅警告检查
$TSCANCODE --enable=warning $SRC_DIR 2> tscancode-warning.txt

# 风格和性能检查
$TSCANCODE --enable=style,performance $SRC_DIR 2> tscancode-style.txt
```

1. **指定输出格式**：

```bash
# 文本格式（默认，输出到stderr）
$TSCANCODE --enable=all $SRC_DIR 2> tscancode.txt

# XML格式
$TSCANCODE --enable=all --xml $SRC_DIR 2> tscancode.xml

# 静默模式
$TSCANCODE --quiet --enable=all $SRC_DIR 2> tscancode.txt
```

1. **处理结果**：

```bash
# 统计问题类型
grep -oP '\[.*?\]' tscancode.txt | sort | uniq -c | sort -nr

# 提取高危问题
grep -E '(error|warning):' tscancode.txt
```

## 常用参数

| 参数 | 描述 | 示例 |
| --- | --- | --- |
| `--enable=<id>` | 启用检查类别 | `warning`, `style`, `performance`, `portability`, `information`, `all` |
| `-I <dir>` | 包含目录 | `-I include -I /usr/include` |
| `-D<macro>` | 定义宏 | `-DDEBUG -DNDEBUG` |
| `-U<macro>` | 取消宏定义 | `-UDEBUG` |
| `-j <n>` | 并行检查线程数 | `-j 4` |
| `--quiet` | 静默模式 | `--quiet` |
| `--xml` | XML格式输出 | `--xml` |

## 检查类别

| 类别 | 关键检查项 |
| --- | --- |
| warning | 空指针解引用、数组越界、整数溢出、未初始化变量、内存泄漏、双重释放 |
| style | 冗余代码、复杂表达式、变量作用域、命名规范 |
| performance | 按值传递、冗余拷贝、低效算法 |
| portability | 平台依赖、类型大小假设 |
| information | 缺少包含、配置问题 |
| unusedFunction | 定义但未被调用的函数 |

## 典型场景

| 场景 | 命令 |
| --- | --- |
| 快速检查 | `$TSCANCODE --enable=warning $SRC_DIR 2> tscancode-warning.txt` |
| 完整检查 | `$TSCANCODE --enable=all -j 4 $SRC_DIR 2> tscancode-full.txt` |
| 特定目录 | `$TSCANCODE --enable=all -I include src/core/ 2> tscancode-core.txt` |
| CI集成 | `$TSCANCODE --quiet --enable=warning --xml $SRC_DIR 2> tscancode-report.xml` |
| 宏控制 | `$TSCANCODE --enable=all -DDEBUG $SRC_DIR 2> tscancode-debug.txt` |

## 构建系统集成

模板文件位于 `templates/` 目录：

- `tscancode-check.sh` - Shell脚本封装
- `tscancode-summary.sh` - 摘要报告生成
- `CMakeLists-tscancode.txt` - CMake集成目标
- `Makefile-tscancode` - Makefile集成

## 最佳实践

1. 增量检查：大型项目使用 `-j` 并行加速
2. 分级处理：先修复 error，再处理 warning，最后优化 style
3. 包含路径：确保 `-I` 参数包含所有必要的头文件路径
4. 宏定义：正确设置 `-D` 参数以覆盖所有代码路径
5. CI集成：将 TscanCode 纳入持续集成流程

## 注意事项

1. TscanCode 默认输出到 stderr，需重定向 `2>` 捕获
2. `--enable=all` 会启用 unusedFunction，建议全项目扫描
3. 确保 `-I` 路径正确，否则可能误报缺少包含

---

**技能版本**: 1.0.0 | **适用项目**: C/C++ | **输出位置**: 当前目录 tscancode-*.txt
