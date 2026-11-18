# clang-tidy（Clang AST 分析，可自动修复）

clang-tidy 基于 Clang AST 分析 C/C++，规则规模大，支持 `--fix` 自动修复，适合精修、PR 级检查与现代化改造。精度依赖 `compile_commands.json`。

> 本页中的 `templates/...` 相对技能根目录。严重度归并见 `SKILL.md` 的“严重度归并”。

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

- 项目配置：`templates/clang-tidy-dot-clang-tidy.yaml` → 复制到项目根目录为 `.clang-tidy`
- CI 集成：`templates/clang-tidy-ci-github-actions.yaml`
- CMake 集成：`templates/clang-tidy-cmake-integration.cmake`
- Makefile 集成：`templates/clang-tidy-Makefile`

## 分析结果处理

```bash
# 统计问题类型
clang-tidy --format-style=json src/main.cpp -- -Iinclude | \
  jq -r '.[].DiagnosticName' | sort | uniq -c | sort -nr

# 提取高危问题
clang-tidy src/main.cpp -- -Iinclude 2>&1 | grep -E '(error|warning):'
```

输出报告模板：`templates/clang-tidy-report.md`

## 与其它引擎对比

参见 `SKILL.md` 的“三引擎差异”表。要点：精度最高、可自动修复、但最慢且强依赖编译数据库。

## 最佳实践

1. 使用 `compile_commands.json` 确保精度
2. 项目级 `.clang-tidy` 统一规范
3. 渐进式采用：从 `bugprone-*,performance-*,modernize-*` 开始
4. `--fix` 优先处理可自动修复项，修复后务必编译验证
5. CI 集成，定期更新

## 注意事项

- 无编译数据库时需手动指定 `-I` 参数，误报会显著增加，报告中必须标注该前提
- 大型项目用 `run-clang-tidy -j N` 并行
- 误报用 `// NOLINT` 或 `.clang-tidy` 抑制
- `--fix` 可能不完整，修复后需编译验证

---

**工具页面版本**: 1.1.0（自 `cpp-clang-tidy` 1.0.0 迁入）

**工具版本**: Clang-Tidy 19.1.7

**适用项目**: C/C++（需 compile_commands.json）

**输出位置**: 当前目录下的诊断输出 / `tidy-fixes.yaml`
