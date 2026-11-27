# 更新历史

> 返回目录：[README.md](README.md) | English：[CHANGELOG_en.md](CHANGELOG_en.md)

## 2026-11-27

### code-review 新增 Java/Maven 依赖版本规则

- `skills/code-review/SKILL.md` 新增「依赖版本规则（Java/Maven）」：同一 `groupId:artifactId` 出现两个及以上不同版本判 P0（classpath 不确定，常见 `NoSuchMethodError`、`ClassCastException`、旧版本漏洞被解析）；仅由传递依赖引入、被就近原则静默覆盖的版本差异判 P1
- 检测命令：`mvnd dependency:tree -Dverbose` 过滤 `omitted for conflict`/`omitted for duplicate`、`dependency:list -Dverbose` 查重复声明来源、`help:effective-pom` 查实际生效版本；修复统一走 `dependencyManagement` 收敛并开启 enforcer `DependencyConvergence`
- 明确与 MR-JAR 的区分：MR-JAR 的 profile 切换的是编译源目录、compiler execution 与 `Multi-Release: true`，依赖版本唯一，不计入 P0；判别看 profile 内差异落在 `<dependency><version>` 还是 `<sourceDirectory>`/`maven-compiler-plugin`/`maven-jar-plugin`
- 依赖确实必须按 JDK 分版本时（如 MVEL2）按受控取舍处理：判 P1，要求在 pom 与决策记录中写明触发条件并由 CI 跨 JDK 矩阵验证，不得默认按 P0
- 分级口径：pom 中可见的同名不同版本为 P0，只能在 verbose 依赖树中看出被覆盖为 P1，MR-JAR 类构建 profile 不计入

## 2026-11-26

### code-review 新增入口与查询有界性 P0 规则

- `skills/code-review/SKILL.md` 新增「入口有界性规则（P0）」：controller/action、RPC/TCP、MQ listener、CLI 与定时任务必须显式约束条数、集合长度、体积与时间窗、并发与深度
- 数据库审查规则同时加硬门槛：查询必须约束输出条数（`LIMIT`/分页上限/流式分批）或约束查询条件（等值或范围且命中索引），二者都不满足判 P0，不允许以“表小”“调用少”放行
- 新增 `templates/endpoint-bounds.md`：五个必须显式有界的维度、四类入口的检查项、审查动作、豁免，以及「入口 × 查询」四象限判定表（入口是闸门，查询是兜底）
- `templates/database-review.md` 新增「查询有界性审查（P0）」：两条判据、7 种违规形态与检测法（无条件全表、ORM 全量列表、分页参数无上限、导出一次性加载、用户输入 `in` 列表无界、懒加载 N+1、分页漏数据）、内存侧三条判据、4 条豁免；并声明上游入口缺失时按入口记 P0

### rust-crossing-compile 分层重构

- `SKILL.md` 由 243 行压到 155 行：合并「适用场景 / 先决策 / 方案选型」三张重叠决策表为「适用场景与选型」，主线只保留 macOS 校验链，补齐「输出物」「完成标准」「参考索引」，对齐 `AGENTS.md` 的正文结构约定
- 下沉出 `references/troubleshooting.md`（13 条常见问题、6 条 Rust 重依赖交叉要点、排查顺序）、`references/verification.md`（三平台校验命令与 11 项验收清单）、`references/ci-release.md`（CI 建议、通用二进制与其他 Apple 平台、安全与合规）；内容只重组不删减
- 技能表同步：`AGENTS.md`、`README.md`、`README_en.md` 新增「构建与交叉编译」分类与 `rust-crossing-compile` 条目（该技能此前已入库但未进索引）

### ast-grep-block 扩展到六语言并支持 SFC 抽取

- 语言范围由 Java/C++/ANSI C 扩至 Java/C++/ANSI C/Rust/JavaScript/TypeScript，分级口径统一为 high/medium/low
- 新增 `--extract-sfc`：抽取 `.vue`/`.html`/`.htm` 的内联 `<script>` 后按 `js`/`ts` 扫描，仅这两个 `--lang` 可用
- `templates/recipes.md`、`templates/report-summary.md`、`templates/run-cli.sh` 同步补齐命令样例与报告格式

### vbox-test-env 纳入 Windows 构建虚拟机

- 技能结构拆为「Linux 三机集群」与「Windows 构建虚拟机」两部分，前者行为不变
- 新增 Windows Server 2019 构建机（VS2022 + Rust），覆盖 headless 启停、`guestcontrol` 以密码文件认证、工具链路径、`scp`/7z 传输与 Windows 构建注意事项
- 明确 UAC 约束：guest 侧无法以管理员身份执行；密码与宿主账号机密不写入技能

## 2026-11-25

### java-env 补充反编译工具

- `skills/java-env/SKILL.md` 的「诊断与分析工具路径」表新增 `cfr`（`${HOME}/bin/cfr`，包装 `~/app/cfr/cfr-0.152.jar`，参数透传）与 `fernflower`（`${HOME}/bin/fernflower`，包装 `~/bin/fernflower.jar`）
- 表后补调用约束：`cfr` 无输出目录参数时结果打到标准输出；`fernflower` 仅接受两个参数（输入、输出目录），缺参只打印 Usage，且脚本固定带 `-hes=0 -hdc=0 -rbr=0 -rsy=0 -rer=0`；两者均使用当前 PATH 中的 `java`，字节码版本过高时需切 JDK

## 2026-11-23

### markdown 波浪号转义约束

- `rules/interaction.rules.md` 的“约束”新增一条：markdown 正文中的 `~` 允许使用，但须转义为 `\~` 或放入行内代码，否则成对出现会按删除符渲染成删除线
- 现有受控文档扫描无成对 `~~` 误用，故无存量修正；该条不纳入 `bin/check-md-wrap.sh`（该脚本只判逻辑成行与表格空行）

### code-detect-dup 的 Simian 路径修正

- `skills/code-detect-dup/SKILL.md` 的 Simian 命令引用 `~/app/simian/simian-4.2.1.jar`，该文件在本机不存在，命令必然失败；实际可用的是 `~/app/simian/simian.jar`（Simian 4.2.1，`-version` 与 `-language=java` 实测通过），已改为该路径

## 2026-11-18

### markdown 排版规则收紧：逻辑成行 + 唯一检查脚本

- **规则改写**：`rules/interaction.rules.md` 把原“不按行宽硬换行”一条扩写为“一个段落、一个列表项、一个引用块写成一个逻辑行”，明确“一句一换行”同样违规，并补齐中英文同口径、代码块与表格不重排不折断、表格前保留空行、强制换行仅限签名/元数据区
- **判据调整**：改为“同一逻辑块内出现第二行连续文本”，不再以“上一行是否以句末标点收尾”判定。标点判据可判定但可被绕过——按句号逐句拆行同样能通过，因此判定必须落在逻辑块上；作者仍负责逻辑归类，脚本只保证“一个逻辑块占一行”
- **新增检查**：`bin/check-md-wrap.sh` 输出 WRAP（段内换行）与 TABLE（表格前缺空行）两类问题，默认检查变更集、`--all` 检查全仓、自动跳过符号链接以免改写外部技能仓库，退出码 0/1/2
- **关闭 markdownlint**：删除 `.markdownlint.json`，仓库不再以 MD013 等按行宽计算的检查验收；`docs/code-review-framework.md` 的规则验证命令改为调用新脚本
- **存量归一**：`CHANGELOG.md`、`CHANGELOG_en.md`、`README.md`、`README_en.md` 的 160 处续行在此次先合并；随后把其余 179 处（51 个文件）一次性归一——正文续行并入上一行，标签对补空行，引用块内的并列项用裸 `>` 行分隔——`--all` 全仓归零。除新增的 13 行裸引用分隔外，非空白字符数与改动前完全一致，未出现中英文粘连

## 2026-11-17

### AGENTS.java.md 新增 MR-JAR 章节

- 记录 multi-release jar 的源码分层：`src/main/java` 只放与 JDK 版本无关的代码、`java8` 编进 jar 根目录、`java{N}` 编进 `META-INF/versions/{N}`；明确 MR-JAR 没有 `versions/8`
- 固化 Maven 接线方式：`build-helper-maven-plugin:add-source` 并入 `src/main/java8`、版本目录用独立 compiler execution + `compileSourceRoots` 覆盖、按 JDK 区间激活 profile、`Multi-Release: true`
- 提炼七条硬约束：基础类不能用 `--release 8` 编 Unsafe、版本化类只在从 jar 加载时生效、版本化类同名同签名且不触碰旧 JDK API、后端开关单一且访问层与桥接层一致、restricted method 需 native-access、桥接层热路径常量折叠且不用 `layout.varHandle()`、codegen 不发射版本相关指令
- 给出验收清单：JDK8 clean test、成品 jar 结构校验、双端探针、基准对照、source jar 完整性

### 静态分析技能按能力合并（5 → 2）

- **合并判据**：技能的拆分轴是“能力”而非语言前缀。同语言同能力、仅引擎不同的静态分析器属于真重复，改为 router 型技能（`SKILL.md` 选型 + `references/` 按需读取），单技能超过 300 行必须分层
- **`java-static-analysis`**：由 `java-check-pmd`、`java-check-spotbugs` 合并，新增 `references/combined-workflow.md` 双引擎串联与去重规则，统一三级严重度（PMD priority 1-2 / SpotBugs high → P0），模板加 `pmd-`、`spotbugs-` 前缀
- **`cpp-static-analysis`**：由 `cpp-check`、`cpp-clang-tidy`、`cpp-tscancode` 合并，新增三引擎差异表与 “快筛 → 精修”组合策略，明确 `compile_commands.json` 缺失时的误报风险与报告标注要求
- **未合并**：`rust-clippy`（静态分析）与 `rust-flamegraph`（CPU 采样）能力不相干；`java-asprof` 与 `jmh-bench` 分属运行时采样与微基准。按语言前缀合并会让 description 失焦、触发不准
- **索引同步**：`AGENTS.md`、`README.md`、`README_en.md` 技能表由 5 行收敛为 2 行，技能入口 42 → 39

## 2026-11-13

### sync-repo-docs 联动 merge-agents-md

- **执行流程新增联动步骤**：`skills/sync-repo-docs/SKILL.md` 在补齐互链后增加第 5 步，调用 `merge-agents-md` 同步 `AGENTS.md`，原「输出变更清单」顺延为第 6 步，清单需包含 AGENTS.md 的合并结果
- **新增「联动 AGENTS.md」章节**：明确模板引用锚点、语言判定顺序（用户指定 > 扩展名推断 > 询问用户）、沿用被调用技能的合并硬门禁（项目事实优先、增量合并不整篇覆盖），并规定跳过条件与记录要求
- **冲突处理与检查清单**：补充 `AGENTS.md` 缺失且语言无法判定时的询问与跳过规则；检查清单新增 AGENTS.md 合并或跳过原因的确认项
- **索引同步**：`README.md`、`README_en.md` 技能表更新 `sync-repo-docs` 的描述

## 2026-11-11

### gdb-heap-analysis 扩展：大 core 取证与 mmap 统计

- **新增 mmap 统计（Step 4.5）**：`IS_MMAPPED` 分配独立于 arena、不计入 `system_mem`，此前属于统计盲区；新增 `scripts/mmap_scan.c`，解析 `PT_LOAD` 与 `NT_FILE`，输出文件/匿名映射计数、匿名映射大小分桶、疑似 `IS_MMAPPED` chunk 与非 chunk 大块 ANON，`min_size` 默认 128KB
- **新增大 core 直接扫描（Step 6）**：`references/large-core-chunk-scan.md` 给出 >4GB / 百万级 chunk 的文件级扫描方法论，含 `p_offset` 与 `p_vaddr` 不同余、chunk 链遍历、尺寸指纹分桶、内容聚类、可达性判定、零页与 RSS 对照
- **新增脚本**：`heap_scan.c`（arena 链统计，含最后一块越界保护、`bad>0` 告警、`memcpy` 未对齐读）、 `scan_zero_pages.c`（零页统计）、`arena_walk.py`（按 glibc 版本遍历 arena）
- **跨架构页大小修正**：页大小优先读 core 的 `NT_AUXV`（`AT_PAGESZ`），不再使用宿主 `sysconf`；修复 x86 宿主分析 aarch64 64KB 页 core 时页数与 MiB 全错的问题
- **可移植性与边界**：修正 glibc 2.28 aarch64 偏移（`top=0x60`、`next=0x870`、`system_mem=0x888`）；新增 `references/scope-and-limits.md`，界定 glibc ptmalloc、非 glibc 分配器、JVM 堆/Metaspace 与 Netty 各分配路径的可见性；新增 `templates/leak-profile-output.md`
- **清洗**：移除技能内的项目特征（产品名、core 文件名、具体地址、业务字段与实测数字），改为占位符；删除无用的 `agents/openai.yaml`

### 技能来源更正与文档同步

- **自维护技能标注**：`memrec`、`multype2txt` 的 `SKILL.md` 实为软链接，指向本人独立维护的仓库，此前在 `AGENTS.md` 中误标为「本地」
  - `AGENTS.md` 技能来源新增 `外部（自维护）` 分类，并列出两个技能的 GitHub / Gitee 仓库地址
  - `README.md`、`README_en.md` 的「技能目录的来源形态」拆分为四类：本仓库维护、软链到自维护仓库、软链到第三方仓库、本地未发布；新增「自维护技能仓库」地址表
  - `semble-search` 仍归类为本地维护、不发布
- **索引补齐**：`AGENTS.md`、`README.md`、`README_en.md` 补入 `java-quality-loop`，并把 `gdb-heap-analysis` 描述扩展为「含 IS_MMAPPED/mmap 统计与大 core 扫描」
- **文档同步**：按 `sync-repo-docs` 规划复核三份文档的命名与互链，MANUAL 维持既有「不设」决策；补记 2026-11-05 至 2026-11-11 期间遗漏的技能与规则变更

## 2026-11-10

### 交互规则补充

- **禁止访问 `~/.ssh`**：`rules/interaction.rules.md` 明确代理不得访问 `~/.ssh` 目录

## 2026-11-09

### java-quality-loop 技能新增

- **新增 `java-quality-loop`**：面向 Maven/Gradle 多模块 Java 项目的执行型循环 SOP，基本轮次为 `Scan → Rank → Select → Baseline → Refactor → Verify → Review → Commit → Record`，强调可回滚、可验证
- **治理边界**：显式声明本技能是持续减压环节，不能替代测试体系、CI 门禁、架构治理、可观测性与安全治理；成功标准是持续降低腐化增量，而非重复率或复杂度归零
- **重构参考与脚本**：新增重复、复杂度、结构分派三类重构指南，以及 `dup_clusters.py`、`pattern_scan.py`、 `complexity_scan.py` 三个扫描脚本；配套 backlog、round-report、metrics、decision-record、 cycle-summary、state.json、loop-config.yaml 等模板
- **`code-review` 结构透镜**：新增 `templates/structure-lens.md`，把结构分派、相似范式与复杂度信号纳入审查视角

## 2026-11-06

### 交互规则语言口径收敛

- **按输出类型分口径**：LLM 交互与输出统一简体中文且不带 Emoji；正式文档用中文，除非明确要求英文； git 提交用英文，必要时附中文
- **删除 thinking 语言条款**：隐藏推理语言不可强制执行也无法验证，条款只增加噪音，予以移除
- **同步位置**：`AGENTS.md` 内联副本与 `code-detect-problem`、`long-term-task`、`merge-agents-md` 三个技能的提交示例同步为新口径

## 2026-11-05

### requirement-collect 强化根本需求提炼

- **根本需求优先（强制）**：技术实现只是参考实现，不是需求本身；每条需求先写根本需求，再写参考技术实现，最后给代码证据，禁止用「系统做了 X」代替「系统必须保证 Y」
- **模板与检查清单**：模块、业务规则、全局需求三个模板同步增加根本需求与参考实现说明，完整性检查清单新增「根本需求」产出项
- **中性表达**：清洗模板中的行业业务词汇（如价源、报价、定价），改为通用中性表述

### 交互规则新增嵌套深度上限

- **最大嵌套深度**：从行首算起等效 Tab 长度达到 6 个 Tab 时，该处代码必须优化或重构，不允许继续加深嵌套

## 2026-11-04

### 技能边界融通

- **`lets-loop` 与 `long-term-task` 分工明确**：前者负责循环系统设计（L1-L4 模型、循环模式、配置模板），后者负责单次长任务执行协议（澄清、计划确认、连续执行、完成总结）
  - `lets-loop` 新增「适用边界：框架设计 vs 任务执行」一节，给出场景路由表，并指定执行期可选用模式 4（Reflexion）与模式 7（计划→执行→重新规划）
  - `long-term-task` 新增「与 lets-loop 的关系」一节，声明两者边界与模式借用方式，明确不改变 HARD-GATE、计划确认门与 TODO 记录要求
  - 两个技能的 `description` 互指，便于技能路由时区分触发场景
- **索引同步**：`AGENTS.md`、`README.md`、`README_en.md` 的技能表描述改为边界化表述
- **错误引用修正**：`skills/code-review/SKILL.md` 的「与其他技能集成」表删除错误的 `lets-loop` 行；`lang-spec/review.java.md` 的 AI 生成代码性能陷阱不再指向 `lets-loop`，改为内联审查要求

## 2026-10-26

### 文档双语化

- **新增英文版文档**：`README_en.md`、`CHANGELOG_en.md`，与中文版语义一致
- **互链补齐**：`README.md` / `README_en.md` 互链，`CHANGELOG.md` / `CHANGELOG_en.md` 互链，双语 README 各自引用同语言 CHANGELOG
- **MANUAL 决策**：本仓库不设 `MANUAL.md`，使用手册内容由 `README.md` 与 `skills/` 下的技能文档承担

### 技能与规范收敛

- **技能合并**：删除 `java-compile` 与 `java-gen-unittest`
  - `java-compile` 的编译命令并入 `lang-spec/ci.java.md`，环境确认仍由 `java-env` 负责
  - `java-gen-unittest` 的测试编写流程并入 `java-coverage` 的「测试编写流程」，覆盖率技能统一承接生成与度量
  - 同步更新 `README.md`、`AGENTS.md`、`skills/code-part-modification`、`skills/lets-loop/templates`
- **java-coverage 修复**：移除对不存在的 `131-java-testing-unit-testing`、`spring-boot-test` 的委托，改为内联测试要点；补充「适用范围」，明确固化文件工作流定位；`mvn test` 统一为 `mvnd test`
- **AST 规则去重**：`code-review` 不再维护具体规则，改为指向 `ast-grep-block` 与 `sql-extract`；5 条常用规则移入 `ast-grep-block/templates/recipes.md` 第 11 节
- **技能来源标注**：`AGENTS.md` 技能表新增「来源」列，区分本仓库、本地未跟踪与外部软链
- **模板去重**：本机 Java 工具表由 `AGENTS.java.md` 移入 `java-env`，模板只保留指针；`java-env` 移除不常用的 `jitwatch-ui`
- **Python 审查规则**：合并 `review.python.md` 中重叠的「代码质量审查规则」与「代码质量与坏味道」，坏味道表作为第 3 小节（1.3.0 -> 1.3.1）
- **README 更正**：`sync-repo-doc` 更正为 `sync-repo-docs`
- **spec.java.md 拆分评估**：暂不拆分。并发章节虽长，但拆分需同步 `review.java.md`、`AGENTS.java.md` 与全部引用锚点，收益低于链接失效风险；待出现按需加载诉求时再评估

## 2026-10-23

### 全语言新增变量单行多声明禁止规则

- **八种语言编码规范**：新增「变量声明（高优先级）」规则，禁止单行多声明
  - 禁止在同一语句中用逗号并列声明多个变量，每个变量独占一行
  - 指针与普通变量混写（`int* p, q;`）必须拆开，避免误读
  - `for` 循环的多个循环变量拆开或提前初始化
  - 模式解构（Rust 元组解构、Kotlin 解构声明、Python 元组解包）属于一次赋值的模式匹配，不视为单行多声明
  - 涉及文件：`lang-spec/spec.js.md`、`spec.cpp.md`、`spec.ansi_c.md`、`spec.rust.md`、`spec.java.md`、`spec.shell.md`、`spec.kotlin.md`、`spec.python.md`
- **代码审查框架**：`skills/code-review/SKILL.md` 的代码质量规则新增变量声明检查项，标注高优先级，适用于所有语言
- **审查规则**：`review.java.md`、`review.cpp.md`、`review.ansi_c.md`、`review.kotlin.md` 的「必须修正（高优先级）」清单同步新增单行多声明检查项

## 2026-10-21

### Java 编码规范补充扇入与扇出设计规则

- **Java 编码规范**：在「设计模式」中新增「扇入与扇出」小节（版本 1.3.0 -> 1.4.0）
  - 核心原则：抽象看扇入，约束看扇出；抽象收益约等于 `扇入 × 变化频率`
  - 模块按变更原因切分，不按功能相关或技术分层切分
  - 禁止业务数据直接控制流程，拆为判定规则接口 + 规则参数数据接口 + 路线策略
  - 行为接口返回不可变决策对象，并区分成功/业务拒绝/系统失败/结果未知；数据接口类型化，区分缺失/空/零三态
  - 单测边界等于接口边界；以「改动在哪个阶段爆炸」作为设计取舍的反向指标；热路径消除基于业务数据的硬分叉
- **接口设计条目修正**：将「接口扇出不应受限」修正为「接口扇入不应受限，接口自身扇出必须受控」，消除与扇入扇出原则的矛盾
- **文件大小限制对齐**：Java 规范单文件行数由「建议不超过 2000 行」改为「超过 500 行应当拆分、超过 1000 行必须拆分」，与 `skills/code-review/SKILL.md` 一致
- 来源：memrec 设计偏好记录（2026-10-21，模块设计主旨/扇入扇出）

## 2026-10-16

### 语言规范补充计算与分支规则

- **Java / C++ / ANSI C / Rust 编码规范**：新增「计算与分支规范」章节
  - 尽量预计算：在程序初始化、类初始化、模块初始化等阶段完成可提前确定的计算，减少运行时计算
  - 循环内不变量：循环体内每次迭代结果不变的表达式，提取到循环外，仅计算一次
  - 整体循环不变量：贯穿整个循环保持不变的量，尽量提取到循环外部，不在循环内计算
  - 分支以正向（肯定）阅读为主，尽量不反向（否定），反向条件增加阅读难度
  - 涉及文件：`lang-spec/spec.java.md`、`spec.cpp.md`、`spec.ansi_c.md`、`spec.rust.md`（版本 1.2.0 -> 1.3.0）

## 2026-10-12

### 新增设计规约技能

- **sync-dev-spec 技能**：将 code-deconstruct 的描述性产物提炼为规范性开发规约
  - 先检查解构产物完整性，缺失或空洞则先执行 code-deconstruct
  - 规约条目五字段：编号（DS-{seq}）、约束、理由、依据、适用范围
  - 不一致、未决、缺失三类问题向用户裁决，不套用代码中不存在的通用最佳实践
  - 完整规约落 `docs/dev-spec/design-charter.md`，约束条目写入项目 `AGENTS.md` 的 `## 设计规约` 章节，可重复执行增量同步
  - 位置：`skills/sync-dev-spec/SKILL.md`，模板 `templates/design-charter.md`、`templates/agents-section.md`
- 提交记录：
  - Commit: `41f7da3` feat: add sync-dev-spec skill turning deconstruct outputs into design charter
- 背景：dev-balance（七维度问询式基线，标签 `20261012_dropped_dev-balance`）已废弃，固定选项菜单无法覆盖项目多样性；改为从代码事实提炼规约

## 2026-10-08

### 新增文档同步技能

- **sync-repo-doc 技能**：基于 git 提交记录同步仓库文档（`skills/sync-repo-docs/SKILL.md`）
  - 文件命名规范：全大写，中文不带后缀、英文以 `_en` 结尾
  - 三对文档：README.md/README_en.md、CHANGELOG.md/CHANGELOG_en.md、MANUAL.md/MANUAL_en.md
  - 两两互链，且 README 需引用各自语言的 CHANGELOG/MANUAL
  - 缺失 README/CHANGELOG 时自动补充，MANUAL 与双语扩充需询问确认
- 提交记录：
  - Commit: `b2c16be` doc: new skill sync-repo-docs
  - Commit: `62bc591` doc: update skill sync-repo-docs
  - Commit: `0511a60` doc: update skill sync-repo-docs

### 文档同步

- **README.md / AGENTS.md 技能表收录 `sync-repo-doc`**（工程与记忆分类）
- **CHANGELOG.md 与 README.md 互链补齐**：CHANGELOG 顶部增加返回 README 的链接

## 2026-10-03

### 文档刷新

- **README.md / AGENTS.md 技能表刷新**：补齐文档中遗漏的技能条目并澄清技能目录形态
  - 新增 `multype2txt` 到文档与图表生成分类
  - 新增 `semble-search`、`vbox-test-env` 到工程与记忆分类
  - AGENTS.md 语言规范文件结构补充 `ci.{lang}.md` 行
  - README.md 扩展与插件章节说明 `skills/` 的三种来源形态（本仓库维护、符号链接外部仓库、本地不纳入版本控制）
- **CHANGELOG.md 补齐**：补入 2026-08-12 至 2026-10-03 期间的变更记录

### 新增测试环境技能

- **vbox-test-env 技能**：VirtualBox 三机测试环境，适用于集群/分布式系统测试
  - 提供 debian001/002/003 三台虚拟机，均已配置互信与 sudo 高权
  - 位置：`skills/vbox-test-env/SKILL.md`
- 提交记录：
  - Commit: `3bd8047` doc: new skill vbox-test-env
  - Commit: `6f35975` doc: update skill vbox-test-env
  - Commit: `b647229` doc: update skill vbox-test-env

## 2026-09-27

### 新增文档转换技能

- **multype2txt 技能**：用本地二进制将 Office/PDF 文档转换为纯文本，零 token 消耗
  - 支持 doc/docx/ppt/pptx/xls/xlsx/pdf
  - 位置：`skills/multype2txt/SKILL.md`

### 技能归置调整

- **memrec 技能本地化**：从 git 跟踪中移出，改由本地/外部来源维护，不再纳入本仓库版本管理
  - 在 `skills/.gitignore` 中忽略对应目录
- Commit: `d8340c9` chore: new skill

## 2026-09-24

### 交互规则增强：特化代码检索工具指引

- 在 `agent-template/interaction.rules.md` 中新增三节检索指引
  - **CodeGraph**：项目知识图谱，优先用于理解与定位代码
  - **Semble**：语义代码检索
  - **zvec-grep**：工作区混合检索（向量 + 词法）
- Commit: `deffe89` doc: add codegraph/semble/zvec-grep guide

## 2026-09-18 ~ 2026-09-26

### 交互规则修订

- 多次修订 `agent-template/interaction.rules.md`（交互约定与工具指引）
- 提交记录：`4f277b7`、`2d3e939`、`82efe64`

## 2026-09-16

### 文档整理

- **AGENTS.md 与 README.md 技能文档整理**：统一技能列表分类与描述
  - Commit: `ad9d5fe` docs: 整理 AGENTS.md 与 README 技能文档

### 忽略规则与外部扩展

- **忽略规则拆分**：`skills/.gitignore`、`pi-extensions/.gitignore`、`dsh-plugins/.gitignore` 各自维护
  - Commit: `00fd1c0` chore: ignore
- **memrec 外部化**：移除内联的 `pi-extensions/memrec.ts`，改以符号链接引入外部实现
  - Commit: `e5edf30` chore: remove

## 2026-09-01

### jmh-bench 通用化

- 移除 jbpe 项目专用示例，改为通用执行方式
- 提交记录：`cd57240`、`777fcd7`、`8f14e59`

## 2026-08-31

### Java 环境技能与模板

- 精简 `java-env` 技能文档，补充 `AGENTS.java.md` 模板内容
- 提交记录：`c1abad3`、`5d0ae90`、`12e926e`、`12ef55b`

## 2026-08-28 ~ 2026-08-29

### memrec 技能文档更新

- 更新 `skills/memrec/SKILL.md`
- 提交记录：`50c0bf7`、`95556d7`

## 2026-08-27

### 路径与交互规则

- **移除硬编码路径**：`cpp-tscancode`、`java-asprof`、`java-check-pmd`、`java-check-spotbugs`、`java-env` 等技能统一使用环境变量
  - Commit: `fa828a2` doc: remove hard-code path
- 更新 `agent-template/interaction.rules.md`
  - Commit: `2818386` doc: update interaction

## 2026-08-26

### 技能模板

- 移除计划文档，新增 Shell 技能模板
- Commit: `6e3f625` doc: remove plan; add skill template: shell

## 2026-08-20

### pi 扩展

- **新增 pi extension**：`pi-extensions/memrec.ts`
- Commit: `2c6eec9` feat: pi extension, memrec

## 2026-08-12 ~ 2026-08-13

### 新增 Kotlin 支持

- **语言规范**：`lang-spec/spec.kotlin.md`、`review.kotlin.md`、`ci.kotlin.md`
- **代理模板**：`agent-template/AGENTS.kotlin.md`
- **技能适配**：`code-review`、`merge-agents-md` 纳入 Kotlin
- **启动脚本**：`bin/common.sh` 支持 kotlin 语言参数
- Commit: `16fea28` feat: add kotlin language spec, review rules and AGENTS template

### pi 快速启动脚本

- **新增脚本**：`bin/pc`（启动 pi）、`bin/updpiid`（更新 pi 会话 ID）
- Commit: `b58b22b` feat: add pi quick-start scripts (pc, updpiid)

### 规范修订

- `lang-spec/spec.kotlin.md` 补充条目
- Commit: `746f1a7` doc: update lang spec

## 2026-07-30

### 文档刷新

- **README.md刷新**：重新整理技能列表，新增多个技能分类
  - 新增`code-part-modification`技能到核心技能库
  - 新增`sql-extract`技能：SQL抽取功能
  - 新增`memrec`技能：AI记忆持久化系统
  - 新增`gdb-heap-analysis`技能到性能分析工具分类
  - 新增`rust-flamegraph`技能到性能分析工具分类
  - 新增`java-coverage`技能到Java开发工具分类
  - 新增`cpp-clang-tidy`技能到静态分析工具分类
  - 新增`ast-grep-block`技能到静态分析工具分类
  - 调整技能分类结构：静态分析工具、性能分析工具独立分类

- **AGENTS.md刷新**：同步更新技能列表

### 技能完整性补齐

本次刷新补齐了以下已存在但文档未记录的技能：

- `code-part-modification` (2026-07-12新增，文档遗漏)
- `gdb-heap-analysis` (长期存在，文档遗漏)
- `java-coverage` (长期存在，文档遗漏)
- `rust-flamegraph` (长期存在，文档遗漏)
- `sql-extract` (长期存在，文档遗漏)
- `cpp-clang-tidy` (长期存在，文档遗漏)
- `memrec` (长期存在，文档遗漏)
- `ast-grep-block` (长期存在，文档遗漏)

## 2026-07-12

### 新增局部代码修改技能

- **code-part-modification技能**：局部代码修改技能，支持最小化修改完成功能
  - 核心原则：确保无蝴蝶效应，支持独立测试验证和全量关联检查
  - 位置：`skills/code-part-modification/SKILL.md`

### 提交记录

- Commit: `cab4697` feat: add code-part-modification skill for minimal code modification

## 2026-07-10

### 新增静态分析技能

- **cpp-check技能**：Cppcheck静态分析，检测C/C++代码缺陷、未定义行为和安全漏洞
  - 位置：`skills/cpp-check/SKILL.md`
- **cpp-tscancode技能**：TscanCode（腾讯开源）C/C++代码检测工具
  - 位置：`skills/cpp-tscancode/SKILL.md`
- **shell-check技能**：ShellCheck静态分析，检测Shell脚本语法错误和潜在缺陷
  - 位置：`skills/shell-check/SKILL.md`

### 新增系统定性评估技能

- **qualitative-assessment技能**：基于全面分析输出，从设计、开发、运维、非功能等维度总结系统性质
  - 位置：`skills/qualitative-assessment/SKILL.md`
- **full-analysis技能增强**：完整分析流程末尾增加定性评估环节
  - 流程：设计解构->代码审查->重复检测->问题侦测->定性评估

### code-deconstruct技能增强

- 新增网络估算工作流，支持网络层面的分析

### 脚本系统改进

- **无参启动逻辑优化**：改进 oc/cdbd/clc 脚本在无参数时的启动逻辑
  - 既无会话ID也无AGENTS.md时显示详细帮助信息
- **金融行情系统分类修正**：澄清定性评估中的金融行情系统分类

### 提交记录

- Commit: `a530ae6` feat: add cpp-check and cpp-tscancode skills
- Commit: `20a4791` feat: add shell-check skill for shell script static analysis
- Commit: `39ccfda` feat(analysis): add qualitative-assessment skill and enhance full-analysis
- Commit: `f3bc9fd` feat: add network estimation workflow to code-deconstruct skill
- Commit: `1001687` fix: 改进AI工具脚本的无参启动逻辑
- Commit: `c4adc53` fix(assessment): clarify financial quote system classification

## 2026-07-09

### code-review技能模块化重构

- **模块化框架**：将code-review重构为通用审查框架 + 语言特定规则的分层架构
  - 通用框架：`skills/code-review/SKILL.md` + `docs/code-review-framework.md`
  - 语言规则：`lang-spec/spec.{lang}.md` 按需加载
- **内容解构完成**：完成code-review技能内容向模块化架构的解构
- **代码示例简化**：精简code-review技能中的代码示例

### 企业级Java代码审查规则

- **新增企业级规则**：从备份恢复企业级Java代码审查规则
- **Java线程创建与管理规范**：新增企业级Java线程创建与管理规范
  - 覆盖线程创建方式、管理策略、风险防范

### 安全审查规则增强

- **时钟回拨攻击检测**：为C++和ANSI C新增时钟回拨攻击检测规则
- **无限循环审查规范**：增强无限循环审查，强调不优雅退出问题

### 路径引用统一

- **环境变量替换硬编码路径**：统一所有路径引用，使用 `${AI_SPEC_ROOT}` 环境变量替换硬编码路径

### 新增Java静态分析技能

- **java-check-spotbugs技能**：SpotBugs静态分析工具技能，支持Find Security Bugs和fb-contrib插件集成
  - 检测范围：代码缺陷、安全漏洞、性能问题
  - 工具版本：SpotBugs 4.7.3（最高支持Java 17）
  - 位置：`skills/java-check-spotbugs/SKILL.md`
  
- **java-check-pmd技能**：PMD代码质量分析工具技能
  - 检测范围：编码规范、代码坏味道、复杂度分析、安全漏洞
  - 工具版本：PMD 6.19.0（支持Java 25）
  - 位置：`skills/java-check-pmd/SKILL.md`

### 工具验证结果

- **PMD验证成功**：工具工作正常，正确检测出空catch块、未使用变量等问题
- **SpotBugs版本兼容性**：SpotBugs 4.7.3因ASM版本限制不支持Java 25，需要Java 17或更早版本
- **技能文档更新**：在SpotBugs技能中添加版本兼容性说明和解决方案

### 技能列表更新

- 在README.md中添加两个新技能到Java开发工具部分
- 更新技能描述和适用场景说明

### 提交记录

- Commit: `a3cfa32` refactor: 统一路径引用，使用环境变量替换硬编码路径
- Commit: `1bcce76` feat: 增强无限循环审查规范，强调不优雅退出问题
- Commit: `d733948` refactor: 简化code-review技能中的代码示例
- Commit: `0ec5e64` feat: refactor code-review skill to modular framework
- Commit: `069c4ee` feat: add enterprise-level Java code review rules from backup
- Commit: `6cc8b1e` feat: add clock rollback attack detection for C++ and ANSI C
- Commit: `2503f25` feat: complete code-review skill content decomposition to modular architecture
- Commit: `9281533` feat: 添加Java线程创建与管理规范（企业级要求）
- Commit: `a193e16` feat: add java-check-spotbugs and java-check-pmd skills

## 2025-07-07

### 新增功能

- **新增 Shell 支持**：添加 Shell/Bash 项目的语言规范和代理模板
- **脚本系统重构**：支持符号链接部署，环境变量驱动架构
- **架构优化**：公共函数集中在 `common.sh`，各脚本独立验证环境变量

### 技术改进

- **路径引用统一**：将所有硬编码的 `/disk2/helly_data/code/markdown/self-ai-spec` 路径替换为 `${AI_SPEC_ROOT}` 环境变量
- **脚本错误处理**：修复 `oc`/`cdbd`/`clc` 脚本在没有参数和会话ID时的友好提示
- **文档规范**：将更新历史从 README.md 分离到 CHANGELOG.md
- **安全意识**：在 AGENTS.md 中添加 AI工具脚本测试安全提醒

### 技能更新

- **Java编码规范**：完善 ForkJoinPool 使用规范，增加任务排队与延时风险章节
- **AI工具测试提醒**：记录 memrec 避免在测试中直接运行交互式工具脚本

## 2025-07-06

### code-review 技能重要更新

- **敏感数据审查通用化**：明确敏感数据审查为所有语言通用必须项（不是C/C++特有）
- **安全审查扩展**：增加以下审查要点：
  - 敏感信息泄露
  - 敏感数据内存残留  
  - 敏感字段输出
  - 安全日志处理
- **专项检查重命名**：专项检查6重命名为"敏感字段输出审查（所有语言通用）"
- **多语言示例**：提供Java/Python/JavaScript敏感信息泄露的代码示例

### 新增语言规范

- **Shell/Bash 规范**：`spec.shell.md` 和 `ci.shell.md` 语言规范
- **Shell 代理模板**：`AGENTS.shell.md` 代理配置文件

## 2025-07-05

### 脚本系统重构

- **环境变量驱动**：所有脚本使用 `AI_SPEC_ROOT` 环境变量定位资源
- **符号链接支持**：脚本支持符号链接到任意目录（如 `~/bin/`）
- **会话管理**：优化会话ID保存和恢复逻辑
- **错误处理**：增强环境变量缺失时的错误提示

### 新增技能

- **merge-agents-md**：通用 AGENTS.md 合并技能，支持多种编程语言模板

## 架构演进

### 路径引用模式演进

- **原始模式**：硬编码绝对路径 → 不灵活，无法移动仓库
- **当前模式**：环境变量 `${AI_SPEC_ROOT}` → 灵活部署，支持符号链接
- **示例**：

  ```
  旧：Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.java.md
  新：Read ${AI_SPEC_ROOT}/lang-spec/spec.java.md
  ```

### 脚本架构优化

- **分离公共函数**：`common.sh` 包含会话管理核心逻辑
- **独立验证**：每个脚本独立验证 `AI_SPEC_ROOT` 环境变量
- **错误提示友好**：无参数且无会话ID时显示详细帮助信息

## 技术备忘

### 重要技术决策

1. **路径引用标准化**：所有资源文件引用使用 `${AI_SPEC_ROOT}` 前缀
2. **环境变量必须性**：`AI_SPEC_ROOT` 是脚本运行的必须条件
3. **符号链接优先**：推荐使用符号链接部署到用户bin目录
4. **会话隔离**：opencode、codebuddy、claudecode 各自管理会话状态

### 安全提醒

- **脚本测试注意事项**：避免在测试中直接运行 `oc`、`cdbd`、`clc`、`qcc` 脚本
- **交互式工具风险**：这些脚本启动交互式AI工具会接管终端，难以退出
- **安全测试方法**：优先使用 `bash -n` 语法检查，或通过环境变量和重定向测试
