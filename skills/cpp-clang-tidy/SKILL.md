---
name: cpp-clang-tidy
description: "Clang-Tidy 静态分析技能：使用 clang-tidy 进行 C/C++ 代码质量检测，支持自定义检查规则和自动修复"
---

# Clang-Tidy C/C++ 静态分析技能

## 工具位置

```bash
CLANG_TIDY=/usr/bin/clang-tidy
# 版本: Debian LLVM 19.1.7
```

## 前置条件

需要 `compile_commands.json` 编译数据库：

```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build  # CMake
bear -- make                                        # 非 CMake (bear)
compiledb make                                      # 非 CMake (compiledb)
```

## 执行流程

### 步骤1：确定路径

```bash
SRC_DIR=src
COMPILE_DB=build
```

### 步骤2：执行分析

```bash
clang-tidy src/main.cpp -- -Iinclude                          # 单文件
clang-tidy -p $COMPILE_DB src/main.cpp                        # 使用编译数据库
run-clang-tidy -p $COMPILE_DB                                 # 批量检查(推荐)
find $SRC_DIR -name '*.cpp' -o -name '*.c' | \
  xargs clang-tidy -p $COMPILE_DB                             # 手动批量
```

### 步骤3：自动修复

```bash
clang-tidy --fix src/main.cpp -- -Iinclude                    # 自动修复
clang-tidy --fix-errors src/main.cpp -- -Iinclude             # 修复含 error
find $SRC_DIR -name '*.cpp' | \
  xargs -I{} clang-tidy --fix-errors {} -p $COMPILE_DB        # 批量修复
```

### 步骤4：输出格式

```bash
clang-tidy src/main.cpp -- -Iinclude                          # 文本(默认)
clang-tidy --format-style=json src/main.cpp -- -Iinclude      # JSON
clang-tidy --export-fixes=tidy-fixes.yaml src/main.cpp        # YAML 修复建议
```

### 步骤5：指定检查规则

```bash
clang-tidy --checks='bugprone-*,security-*' src/main.cpp      # 仅安全和 bugprone
clang-tidy --checks='*,-readability-*,-llvm-*' src/main.cpp   # 排除特定规则
```

## 常用检查规则

| 类别 | 前缀 | 描述 |
| --- | --- | --- |
| 正确性 | `clang-diagnostic-*` / `clang-analyzer-*` | 编译器警告、静态分析 |
| 现代 C++ | `modernize-*` | 现代 C++ 用法建议 |
| 性能 | `performance-*` | 性能优化 |
| 可读性 | `readability-*` | 代码可读性 |
| 安全 | `bugprone-*` / `security-*` | 常见错误、安全漏洞 |
| 并发 | `concurrency-*` | 死锁、竞态条件 |
| 规范 | `cert-*` / `misra-*` / `google-*` | CERT/MISRA/Google 规范 |

## 配置与集成

- 项目配置：`templates/dot-clang-tidy.yaml` → 复制到项目根目录为 `.clang-tidy`
- CI 集成：`templates/ci-github-actions.yaml`
- CMake 集成：`templates/cmake-integration.cmake`
- Makefile 集成：`templates/Makefile-tidy`

## 分析结果处理

```bash
# 统计问题类型
clang-tidy --format-style=json src/main.cpp -- -Iinclude | \
  jq -r '.[].DiagnosticName' | sort | uniq -c | sort -nr

# 提取高危问题
clang-tidy src/main.cpp -- -Iinclude 2>&1 | grep -E '(error|warning):'
```

输出报告模板：`templates/report.md`

## 与 Cppcheck 对比

| 特性 | Clang-Tidy | Cppcheck |
| --- | --- | --- |
| 分析引擎 | Clang AST | 自定义解析器 |
| 编译数据库 | 必需 | 可选 |
| 自动修复 | 支持 | 不支持 |
| 检查规则数 | 500+ | 200+ |
| 分析速度 | 较慢 | 快 |

## 最佳实践

1. 使用 `compile_commands.json` 确保精度
2. 项目级 `.clang-tidy` 统一规范
3. 渐进式采用：从 `bugprone-*,performance-*,modernize-*` 开始
4. `--fix` 优先处理可自动修复项，修复后务必编译验证
5. CI 集成，定期更新

## 注意事项

- 无编译数据库时需手动指定 `-I` 参数
- 大型项目用 `run-clang-tidy -j N` 并行
- 误报用 `// NOLINT` 或 `.clang-tidy` 抑制
- `--fix` 可能不完整，修复后需编译验证

---
**技能版本**: 1.0.0 | **工具版本**: Clang-Tidy 19.1.7 | **适用**: C/C++ (需 compile_commands.json)
