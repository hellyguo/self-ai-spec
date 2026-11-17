---
name: java-static-analysis
description: "Java 静态分析统一入口：按检查目标在 PMD（源码规范与坏味道）与 SpotBugs（字节码缺陷与安全）之间选型并执行，可串联两引擎输出分级问题清单。适用于 Java 项目规范检查、缺陷排查、安全审计、CI 质量门禁、提交前自检。"
---

# Java 静态分析（PMD / SpotBugs）

本技能是 Java 静态分析的统一入口，只负责选型、串联与结果归并；单个工具的完整参数、命令与故障排除放在 `references/` 下按需读取，不要一次性全部加载。

> 本文件与各 references 页中的 `references/...`、`templates/...` 均相对本技能目录。

## 适用场景

- 提交/合并前的 Java 代码质量自检。
- CI 质量门禁（规范违规、缺陷、安全问题）。
- 专项排查：安全审计、并发与资源泄漏、复杂度与坏味道。
- 存量项目体检：需要一份可分级、可追踪的静态问题清单。

不适用：

- 需要运行期数据（CPU 热点、锁竞争）时用 `java-asprof`。
- 需要微基准结论时用 `jmh-bench`。
- 需要 AST 规则级门禁（code-checklist 规则集、CI 退出码）时用 `ast-grep-block`。

## 选型（先做这一步）

| 检查目标 | 引擎 | 读取 |
| :--- | :--- | :--- |
| 编码规范、命名、复杂度、代码坏味道、源码级重复（CPD） | PMD（源码） | `references/pmd.md` |
| 空指针、资源泄漏、并发缺陷、SQL 注入/XSS/命令注入 | SpotBugs（字节码 + 插件） | `references/spotbugs.md` |
| 提交前全量体检，需同时覆盖源码与字节码 | 两引擎串联 | `references/combined-workflow.md` |

选型判据：

1. 只有源码、没有编译产物，或需要快速给出规范类结论：PMD。
2. 已有 `target/classes`（或 `build/classes`）且关心缺陷/安全：SpotBugs。
3. 两者都要时不要并行各写一份报告，按 `references/combined-workflow.md` 归并，避免同一问题重复计数。

## 前置条件

- PMD：源码目录可读，无需编译；本机工具路径见 `references/pmd.md` 的“工具位置”。
- SpotBugs：必须先编译出字节码；SpotBugs 4.7.3 最高支持 class major 61（Java 17），分析 Java 18+ 项目需用 JDK 17 运行分析器，而不是用项目自身 JDK。
- 两者结果均落盘到当前工作目录，报告文件不要覆盖已有报告。

## 执行步骤

1. 按“选型”确定引擎，只读取对应 references 页。
2. 按该页的“工具位置 → 执行流程”运行，输出文件按该页约定命名。
3. 结果归并为统一三级严重度（见下），写入报告。
4. 对 P0 项逐条给出文件:行号与修复方向；P1 项汇总计数与代表样例；P2 项只保留计数与规则名。

## 严重度归并

| 来源 | 原始等级 | 归并后 |
| :--- | :--- | :--- |
| SpotBugs | High priority | P0（必须修正） |
| SpotBugs | Medium priority | P1（应当修正） |
| SpotBugs | Low priority / 实验性检测器 | P2（建议改进） |
| PMD | priority 1-2 | P0 |
| PMD | priority 3 | P1 |
| PMD | priority 4-5 | P2 |
| CPD 重复片段 | 任一 | P1，并在报告中标注重复 token 数与涉及文件 |

## 输出物

- 原始结果：当前目录下的 `pmd-*.txt` / `spotbugs-*.txt`（格式与命名见各 references 页）。
- 归并报告：单引擎时用 `templates/spotbugs-report.md` 或 `templates/pmd-result-processing.md` 的统计脚本；双引擎串联时按 `references/combined-workflow.md` 的表结构输出一份 Markdown 报告。
- 构建/CI 集成配置：`templates/pmd-build-integration.md`、`templates/spotbugs-filter.xml`。

## 完成标准

- 选型有明确依据，且报告中写明所用引擎与版本。
- 每条 P0 均有文件:行号、规则名、修复方向。
- 已执行的抑制项（PMD 抑制文件、SpotBugs filter）在报告中列出并说明理由。
- CI 场景下退出码语义明确：P0 > 0 时失败，仅 P1/P2 时告警。

## 注意事项

1. 不要用 SpotBugs 结论替代编译期检查，它只分析字节码可达的路径。
2. 两个引擎的规则名不可直接比对，归并表只按严重度与位置去重，不按规则名合并。
3. 大项目优先增量分析（PMD 文件列表、SpotBugs `-onlyAnalyze`），全量分析放到 CI。

---

**技能版本**: 2.0.0
**合并来源**: `java-check-pmd` 1.0.0、`java-check-spotbugs` 1.0.0
**工具版本**: PMD 6.19.0、SpotBugs 4.7.3（含 Find Security Bugs、fb-contrib）
**适用项目**: Java 8+（SpotBugs 分析侧需 JDK 17 及以下）
