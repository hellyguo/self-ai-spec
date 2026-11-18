---
name: cpp-static-analysis
description: "C/C++ 静态分析统一入口：在 Cppcheck（免编译、快筛）、clang-tidy（Clang AST、可自动修复）与 TscanCode（腾讯规则集）之间选型并执行，输出分级问题清单。适用于 C/C++ 项目静态检查、CI 质量门禁、现代化改造、缺陷与安全审计。"
---

# C/C++ 静态分析（Cppcheck / clang-tidy / TscanCode）

本技能是 C/C++ 静态分析的统一入口，只负责选型、组合与结果归并；单个工具的完整参数、命令与故障排除放在 `references/` 下按需读取，不要一次性全部加载。

> 本文件与各 references 页中的 `references/...`、`templates/...` 均相对本技能目录。

## 适用场景

- 提交/合并前的 C/C++ 代码自检。
- CI 质量门禁（缺陷、未定义行为、规范、安全）。
- C++ 现代化改造（`modernize-*` 规则 + `--fix`）。
- 存量 ANSI C / 大型 C++ 项目体检与问题盘点。

不适用：

- 需要运行期性能数据时用 `rust-flamegraph`（Rust）或对应语言的采样工具，本技能不做运行时分析。
- 需要规则级 AST 门禁（code-checklist 规则集、CI 退出码）时用 `ast-grep-block`。

## 选型（先做这一步）

| 检查目标 / 约束 | 引擎 | 读取 |
| :--- | :--- | :--- |
| 无编译数据库、要求快；缺陷、未定义行为、可移植性 | Cppcheck | `references/cppcheck.md` |
| 需 AST 精度、需自动修复、现代 C++ 改造、项目级 `.clang-tidy` | clang-tidy | `references/clang-tidy.md` |
| 与既有 TscanCode 流水线对齐，或需要其规则集口径 | TscanCode | `references/tscancode.md` |
| 大型项目：快筛 + 精修 | Cppcheck 后接 clang-tidy | 两页 + 下方“组合策略” |

## 三引擎差异

| 特性 | Cppcheck | clang-tidy | TscanCode |
| :--- | :--- | :--- | :--- |
| 分析引擎 | 自研解析器 | Clang AST | 自研（腾讯） |
| 编译数据库 | 可选 | 必需（精度依赖它） | 不支持 |
| 自动修复 | 不支持 | 支持 `--fix` | 不支持 |
| 规则规模 | 200+ | 500+ | 与 Cppcheck 类别相近，命名自成体系 |
| 速度 | 快 | 慢（需编译前端） | 快 |
| 输出 | stderr 重定向 / XML | 文本 / JSON / YAML fixes | stderr 重定向 / XML |
| 典型用途 | 全量快筛、CI 第一道 | 改造与精修、PR 级检查 | 存量口径对齐 |

## 前置条件

- Cppcheck：`/usr/bin/cppcheck`（2.17.1）。可选 `compile_commands.json` 提升精度。
- clang-tidy：`/usr/bin/clang-tidy`（LLVM 19.1.7），必须能生成 `compile_commands.json`：

```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build  # CMake
bear -- make                                        # 非 CMake
compiledb make                                      # 非 CMake
```

- TscanCode：`${HOME}/app/TscanCode.linux/tscancode`。

## 执行步骤

1. 按“选型”确定引擎，只读取对应 references 页。
2. 按该页“执行流程”运行，输出文件按该页约定命名。
3. 结果归并为统一三级严重度（见下），写入报告。
4. P0 逐条给出文件:行号与修复方向；P1 汇总计数与样例；P2 仅保留计数与规则名。

## 严重度归并

| 来源 | 原始等级 | 归并后 |
| :--- | :--- | :--- |
| Cppcheck / TscanCode | `(error)` | P0（必须修正） |
| Cppcheck / TscanCode | `(warning)` | P1（应当修正） |
| Cppcheck / TscanCode | `(style)`、`(performance)`、`(portability)` | P2（建议改进） |
| clang-tidy | `error:` 诊断 | P0 |
| clang-tidy | `warning:` 诊断 | P1 |
| 任一引擎的 `information` / 缺失包含类 | 不进报告主表，只统计 |

## 组合策略

1. **快筛 → 精修**：Cppcheck `--enable=warning,style -j 4` 出全量清单，只用 clang-tidy 处理 P0/P1 且集中在被改动文件，避免对整仓跑 AST。
2. **不重复计数**：同一 `文件:行号` 且缺陷语义相同（如空指针、资源泄漏）时保留 clang-tidy 条目，Cppcheck 条目降为“同源告警”。
3. **TscanCode 定位**：仅当项目已有 TscanCode 基线或需要与历史报告可比时使用，不与 Cppcheck 并行出两份主表。
4. **修复后必编译**：clang-tidy `--fix` 可能只完成部分改写，修复后必须重新编译并复跑。

## 输出物

- 原始结果：当前目录下 `cppcheck-*.txt|xml`、clang-tidy 诊断输出 / `tidy-fixes.yaml`、`tscancode-*.txt|xml`。
- 报告：`templates/clang-tidy-report.md`（clang-tidy 单引擎），组合场景按“严重度归并”表自行汇总为一份 Markdown。
- 构建/CI 集成：`templates/clang-tidy-dot-clang-tidy.yaml`、`templates/clang-tidy-ci-github-actions.yaml`、`templates/clang-tidy-cmake-integration.cmake`、`templates/clang-tidy-Makefile`、`templates/tscancode-check.sh`、`templates/tscancode-summary.sh`、`templates/tscancode-CMakeLists.txt`、`templates/tscancode-Makefile`。

## 完成标准

- 报告写明所用引擎、版本，以及是否使用了 `compile_commands.json`。
- 每条 P0 均可定位到文件:行号，并给出修复方向。
- 抑制项（`// cppcheck-suppress`、`// NOLINT`、`.clang-tidy` 排除、TscanCode 抑制）在报告中列出并说明理由。
- CI 场景下退出码语义明确：P0 > 0 失败，仅 P1/P2 告警。

## 注意事项

1. 三个工具对“未使用函数”“缺失包含”的口径差异大，这类告警跨工具合并会失真，只做单引擎内统计。
2. clang-tidy 无编译数据库时会退化为 `-I` 手工配置，误报显著上升，报告须标注该前提。
3. Cppcheck 与 TscanCode 默认输出到 stderr，必须重定向捕获；日志不要直接写 stdout。

---

**技能版本**: 2.0.0

**合并来源**: `cpp-check` 1.0.0、`cpp-clang-tidy` 1.0.0、`cpp-tscancode` 1.0.0

**工具版本**: Cppcheck 2.17.1、Clang-Tidy 19.1.7、TscanCode

**适用项目**: C/C++（含 ANSI C）
