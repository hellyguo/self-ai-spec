---
name: ast-grep-block
description: "基于 ast-grep 与 code-checklist 规则库，对 Java/C++/ANSI C/Rust/JavaScript/TypeScript 项目执行分级（high/medium/low）AST 静态审查，并支持抽取 .vue/.html 内联脚本按 js/ts 扫描，输出命中清单与 CI 退出码。适用于提交/合并前质量门禁、CI 流水线静态检查、审查前自动化预检、存量问题盘点。"
---

# ast-grep-block 代码审查门禁技能

> 本文件中的 `templates/...` 均指本技能目录下的 `templates/` 子目录。

用 `code-checklist` 规则集对源代码项目进行**分级 AST 静态审查**，输出命中清单与 CI 退出码。

## 适用场景

- 提交/合并前的质量门禁（high 命中则阻断）
- 代码审查前的自动化预检（全级别扫描登记问题）
- 重构前的存量问题盘点（按级别/类别统计）
- CI 流水线集成的质量门禁节点

## 核心思路

**单一 CLI 模式**：直接调用 code-checklist 仓库的 `scripts/run.sh`，该脚本封装了规则遍历、`.astgrepignore` 过滤、分级统计、CI 退出码输出；对 `.vue` / `.html` 项目可加 `--extract-sfc` 抽取内联脚本后按 `js` / `ts` 一并扫描。

不使用 ast-grep-mcp，因为：
- 审查语义需要"全规则批量 + ignore 过滤 + 退出码"，这些是 CLI 模式的优势
- MCP 适合"交互式抽查看上下文"，不适合门禁场景

## 工具依赖

| 工具 | 版本 | 用途 |
|------|------|------|
| ast-grep | >= 0.51.0 | AST 匹配引擎（0.5x 起规则顶层严格校验，扩展字段须在 metadata 下） |
| bash | >= 4 | run.sh 运行环境 |
| python3 + pyyaml | - | 元数据读取 / ignore 解析 |
| jq | >= 1.6 | JSON 输出处理 |

验证：
```bash
ast-grep --version && python3 -c 'import yaml' && jq --version
```

## 规则库锚定

规则库通过环境变量定位：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CODE_CHECKLIST_ROOT` | `/disk2/helly_data/code/ast-grep-rules/code-checklist` | code-checklist 仓库根 |

```bash
# 检查锚定
[[ -n "$CODE_CHECKLIST_ROOT" ]] || CODE_CHECKLIST_ROOT=/disk2/helly_data/code/ast-grep-rules/code-checklist
[[ -x "$CODE_CHECKLIST_ROOT/scripts/run.sh" ]] || { echo "规则库未就绪: $CODE_CHECKLIST_ROOT" >&2; exit 2; }

# 查看当前覆盖（规则数，六种语言）
for lang in java cpp ansi_c rust js ts; do
    echo -n "$lang: "
    find "$CODE_CHECKLIST_ROOT/rules/$lang" -name '*.yml' | wc -l
done
```

> 如需切换规则库版本或位置，请在 shell 环境变量中配置 `CODE_CHECKLIST_ROOT`，本 skill 不在仓库内复制规则。

## 语言与规则体系

| `--lang` | ast-grep 语言标识 | 规则目录 | 说明 |
|----------|-------------------|----------|------|
| `java` | java | `rules/java/**` | 含 1 条配置类规则，由 `check-java-config.sh` 执行，`run.sh` 会跳过 |
| `cpp` | cpp | `rules/cpp/**` | AST 规则 |
| `ansi_c` | c | `rules/ansi_c/**` | AST 规则 |
| `rust` | rust | `rules/rust/**` | AST 规则 |
| `js` | javascript | `rules/js/**` | JavaScript（含 JSX 语法可解析，规则以 ES 为主） |
| `ts` | typescript | `rules/ts/**` | TypeScript；与 `js` 有 8 条同名规则，含义一致 |

注意：

1. `js` 与 `ts` 是两套独立规则集，**不要**用 `--lang js` 扫 TypeScript 文件，反之亦然； ast-grep 按扩展名选择解析器，语言参数与文件扩展名不匹配时不会命中。
2. 规则数为动态值，用上文"查看当前覆盖"的命令读取，不要在文档里写死。
3. 规则来源包括阿里巴巴 Java 开发手册与 Google 官方风格指南（Java/C++/Rust/JS/TS），条目取舍与冲突裁定记录在规则库 `docs/analysis/` 与 `docs/plans/` 下。

## 分级语义（用户口径）

| 级别 | 含义 | CI 行为 | run.sh 退出码 |
|------|------|---------|---------------|
| **high** | 必须修改，必须本次修改 | 阻断提交/合并 | 1 |
| **medium** | 必须修改，但并非本次修改 | 登记跟踪，下次迭代 | 0 |
| **low** | 可接受不改 | 提示性建议 | 0 |

`run.sh` 完整退出码：

| 退出码 | 含义 | 处理 |
|--------|------|------|
| 0 | 无 high 命中 | 通过 |
| 1 | 有 high 命中 | 按步骤 5 复核修复 |
| 2 | 参数错误 / 工具缺失 / ast-grep 版本过低 | 修正调用或升级 ast-grep |
| 3 | 规则解析失败或扫描出错 | **结果不可信，先修规则**（详见步骤 3 的说明） |

> 退出码 3 是"规则坏了"而非"代码干净"。历史上脚本用 `2>/dev/null || echo '[]'` 吞掉 > 解析错误，会输出假 0 命中；现在必须显式失败，不得把它当通过处理。

## 执行流程

### 步骤 1：确定目标范围

先识别项目结构，明确：

- 源代码根目录（如 `src/main/java`、`src/`、`<module>/src`）
- 构建产物目录（`build/`、`target/`、`out/`、`cmake-build-*/`）→ **必须排除**
- 第三方/二方库（`third_party/`、`vendor/`、`lib/`）→ 按需排除
- 测试目录（`src/test/`、`gtest/`）→ 按需排除

```bash
# 顶层结构盘点
eza <project_root>

# 文件数预估
fd --no-ignore -e java -t f <project_root> | wc -l   # Java
fd --no-ignore -e cpp -e h -e hpp -t f <project_root> | wc -l  # C++
fd --no-ignore -e c -e h -t f <project_root> | wc -l  # ANSI C
fd --no-ignore -e rs -t f <project_root> | wc -l  # Rust
fd --no-ignore -e js -e jsx -t f <project_root> | wc -l  # JavaScript
fd --no-ignore -e ts -e tsx -t f <project_root> | wc -l  # TypeScript
fd --no-ignore -e vue -e html -e htm -t f <project_root> | wc -l  # SFC/HTML 内联脚本（配合 --extract-sfc）
```

### 步骤 2：选语言与级别

| 参数 | 取值 | 默认 |
|------|------|------|
| `--lang` | `java` / `cpp` / `ansi_c` / `rust` / `js` / `ts` | 必填 |
| `--level` | `high` / `medium` / `low` | 任选其一 |
| `--all` | 扫描所有级别 | 替代 `--level` |
| `--path` | 被扫描项目根 | `.` |
| `--json` | 输出 JSON 数组 | 文本报告 |
| `--extract-sfc` | 抽取 `.vue` / `.html` / `.htm` 内联 `<script>`，仅 `--lang js|ts` 可用 | 关闭 |
| `--tmp-dir` | SFC 抽取临时目录 | `${CODE_CHECKLIST_TMP_DIR:-/tmp/opencode/code-checklist-sfc}` |
| `--keep-temp` | 保留 SFC 抽取目录便于排查 | 关闭（默认成功/失败都清理） |

**推荐顺序**：先跑 `high` 修阻断项，再跑 `--all` 盘点全量。

### 步骤 3：执行扫描（核心命令）

```bash
# 3a. 仅 high 级别（CI 门禁场景）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --level high \
    --path <project_root>
echo "退出码: $?  # 0 通过 / 1 high 命中 / 2 参数错误 / 3 规则解析失败（结果不可信）"

# 3b. 全级别扫描（盘点场景）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --all \
    --path <project_root>

# 3c. JSON 输出（CI/工具对接）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --level high \
    --path <project_root> --json > report.json
echo $?  # 退出码仍正确返回

# 3d. Vue / HTML 项目：抽取内联脚本后按 js/ts 扫描
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang js --all \
    --path <project_root> --extract-sfc --json > report.json

# 3e. 保留抽取现场排查（默认扫描结束即清理临时目录）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang ts --all --path <project_root> --extract-sfc --keep-temp
```

> `--extract-sfc` 仅支持 `--lang js|ts`，其他语言会以退出码 2 拒绝。

### 步骤 3 补充：SFC / HTML 内联脚本

ast-grep 的 `javascript` 解析器不处理 `.vue`，因此需要抽取：

1. **行号对齐**：抽取文件在脚本内容前补等量空行，命中行号与原始 `.vue` / `.html` 一致；`file` 还原为原始路径，并附带 `sfcBlock`（第几个 `<script>`）。
2. **语言分流**：`lang="ts"` / `type="text/typescript"` 归 `ts`；无 `lang`、`lang="js|javascript|babel|ecmascript"`、`type="module"` / `text/javascript` 归 `js`。扫 `js` 跳过 `ts` 块，反之亦然。
3. **不重复上报**：启用抽取后原生扫描会用 `--globs` 排除 `.vue/.html/.htm`，由抽取结果统一提供。
4. **跳过外部脚本**：带 `src` 的 `<script>` 不抽取，其目标 `.js` 仍被原生扫描。
5. **跳过第三方目录**：`.git`、`.svn`、`node_modules`、`dist`、`coverage`、`libs`、`ueditor`、`kindeditor`、`jsoneditor` / `json-editor`、`echarts`。
6. **临时目录**：`/tmp/opencode/code-checklist-sfc/run.XXXXXXXX`，可用 `--tmp-dir` 或 `CODE_CHECKLIST_TMP_DIR` 覆盖。
7. **忽略规则**：`.astgrepignore` 按还原后的原始路径匹配，可直接写 `src/views/**/*.vue`。

抽取能力本身可用 `"$CODE_CHECKLIST_ROOT/scripts/validate-sfc-extract.sh"` 验证（行号对齐、js/ts 分流、临时目录清理）。

> 便捷封装见 `templates/run-cli.sh`，可复制到目标项目 `scripts/` 直接 `./scripts/run-cli.sh java high .`。

### 步骤 4：解读报告

**文本输出格式**（默认）：
```
=== ast-grep 扫描报告 ===
扫描路径: /path/to/project
高级(high): 12 条
中级(medium): 5 条
低级(low): 2 条

--- HIGH 命中明细 ---
src/dao/UserDao.java:42:13:empty-catch-block: catch (Exception e) {}
src/util/Crypto.java:108:25:hardcoded-secret: private String key = "sk-12345";
...
```

每行格式：`<文件>:<行号>:<列号>:<规则ID>: <命中代码行>`

**JSON 输出格式**（`--json`）：
```json
[
  {
    "file": "src/dao/UserDao.java",
    "range": {"byteOffset": 1234, "start": {"line": 41, "column": 12}, "end": {"line": 42, "column": 25}},
    "lines": "catch (Exception e) {}",
    "text": "...AST 节点文本...",
    "ruleId": "empty-catch-block",
    "level": "high",
    "sfcBlock": 2
  },
  ...
]
```

> `sfcBlock` 仅在 `--extract-sfc` 命中 `.vue/.html` 时出现，表示命中的是文件内第几个 `<script>`（1-based）。

详细字段说明与统计命令见 `templates/report-summary.md`。

### 步骤 5：复核 high 命中（必做）

high 命中必须逐条人工确认：

```bash
# 抽取所有 high 命中文件清单
jq -r 'select(.level=="high") | .file' report.json | sort -u > /tmp/high-files.lst

# 查看具体命中规则分布
jq -r 'select(.level=="high") | .ruleId' report.json | sort | uniq -c | sort -rn

# 抽查单文件原始上下文
rg -n -A 3 -B 3 'catch \(' src/dao/UserDao.java
```

对每条 high 命中判定：
- **真实问题** → 立即修复，重新跑步骤 3 验证退出码变为 0
- **规则误报** → 优先优化规则 constraints（修改 rule YAML）；次选登记 `.astgrepignore`

### 步骤 6：误报抑制（兜底）

误报抑制分两层，**优先层**优于**兜底层**：

#### 6a. 优先层：优化规则 constraints

修改规则文件本身（在 `$CODE_CHECKLIST_ROOT/rules/{lang}/{level}/...`），通过 `not`/`has`/`constraints.regex` 等机制缩小命中范围。改后必须验证：

```bash
"$CODE_CHECKLIST_ROOT/scripts/validate-examples.sh"  # 正负样例回归
"$CODE_CHECKLIST_ROOT/scripts/validate-meta.sh"      # 元数据合法性
```

#### 6b. 兜底层：`.astgrepignore`

在**目标项目根**（被扫描的项目，不是规则库）放置 `.astgrepignore`：

```yaml
- rule: hardcoded-secret
  paths:
    - "src/test/resources/**"            # 测试资源目录常含示例密码
    - "**/test/**/*Fixture.java"
- rule: system-out-print
  paths:
    - "**/Main.java"                     # main 入口可打印 banner
```

`run.sh` 会自动读取被扫描项目根的 `.astgrepignore` 并对命中结果过滤。

> 注意：`run.sh` 只在被扫描路径根查找 `.astgrepignore`，所以**必须在目标项目根放置**，不是规则库根。

### 步骤 7：CI 集成

```bash
# CI 流水线片段（GitHub Actions / GitLab CI / Jenkins shell 步骤通用）
- name: ast-grep code-checklist
  run: |
    export CODE_CHECKLIST_ROOT=/path/to/code-checklist
    "$CODE_CHECKLIST_ROOT/scripts/run.sh" \
        --lang java --level high \
        --path . --json > ast-grep-report.json
    # 退出码 1 时 CI 自动失败
```

进阶 CI 模式（多语言、按目录增量、PR 仅扫变更文件）见 `templates/recipes.md`。

## 命令速查

| 场景 | 命令 |
|------|------|
| Java high 扫描 | `run.sh --lang java --level high --path .` |
| C++ 全级别盘点 | `run.sh --lang cpp --all --path .` |
| ANSI C 仅缺陷 | `run.sh --lang ansi_c --level high --path .` |
| Rust 全级别盘点 | `run.sh --lang rust --all --path .` |
| JavaScript 仅缺陷 | `run.sh --lang js --level high --path .` |
| TypeScript 全级别 | `run.sh --lang ts --all --path .` |
| Vue/HTML 内联脚本（js） | `run.sh --lang js --all --path . --extract-sfc` |
| Vue/HTML 内联脚本（ts） | `run.sh --lang ts --all --path . --extract-sfc` |
| JSON 报告 | `run.sh --lang java --all --path . --json > r.json` |
| 仅看 high 命中文件 | `jq -r 'select(.level=="high")\|.file' r.json \| sort -u` |
| 规则分布 Top N | `jq -r '.ruleId' r.json \| sort \| uniq -c \| sort -rn \| head` |
| 校验规则库 | `"$CODE_CHECKLIST_ROOT/scripts/validate-meta.sh" && "$CODE_CHECKLIST_ROOT/scripts/validate-examples.sh"` |
| 校验 SFC 抽取 | `"$CODE_CHECKLIST_ROOT/scripts/validate-sfc-extract.sh"` |

## 输出位置

- 文本报告：默认 stderr + stdout（按 `run.sh` 实现）
- JSON 报告：通过 `--json` 参数，需重定向到文件
- SFC 抽取临时文件：`${CODE_CHECKLIST_TMP_DIR:-/tmp/opencode/code-checklist-sfc}/run.XXXXXXXX`，默认自动清理，`--keep-temp` 保留
- 其他临时输出：本 skill 不创建，由调用方决定保存路径

## 陷阱与故障排除

| 现象 | 原因 | 解决 |
|------|------|------|
| `未找到 ast-grep` | 未安装或不在 PATH | `cargo install ast-grep` 或包管理器安装 |
| `规则库未就绪` | `CODE_CHECKLIST_ROOT` 配错或仓库缺失 | 检查环境变量、clone 仓库 |
| 扫描结果为 0 命中但明显有问题 | 构建产物目录被误排（`build/`）或语言判断错 | 确认 `--lang` 与文件扩展名一致；同时看报告头的"已扫描规则 N 条"，为 0 则是规则侧问题 |
| high 退出码总是 1 | 有 high 命中（正常） | 按步骤 5 修复或登记 `.astgrepignore` |
| 退出码 3 / `规则解析失败` | 规则 YAML 顶层含 ast-grep 不接受的字段（如 `level`），或 ast-grep 版本与规则格式不匹配 | 修规则（扩展字段放 `metadata:`）或对齐 ast-grep 版本，**此时 0 命中不算通过** |
| `.astgrepignore` 不生效 | 放错位置 | 必须放在被扫描项目根，不是规则库根 |
| `.vue` / `.html` 内联脚本 0 命中 | 未启用 `--extract-sfc`，或 `--lang` 与 `<script lang>` 不匹配 | js 项目用 `--lang js --extract-sfc`；ts 块用 `--lang ts --extract-sfc` |
| `.vue` 命中重复上报 | 未启用抽取，ast-grep 自身又解析了 HTML 内联脚本 | 统一用 `--extract-sfc`，原生扫描会自动排除 `.vue/.html/.htm` |
| `--extract-sfc 仅支持 --lang js\|ts` | 语言参数不是 js/ts | 改为 `--lang js` 或 `--lang ts`，其他语言不需要抽取 |
| SFC 抽取失败（退出码 3） | 内联脚本抽取或命中路径还原异常 | 加 `--keep-temp` 保留现场检查，再跑 `validate-sfc-extract.sh` 确认抽取能力正常 |
| 误报泛滥 | 规则太宽 | 优先优化 constraints，次选 ignore |
| 极慢（万级文件） | ast-grep 串行扫描 | 按目录分批跑（见 `templates/recipes.md`） |
| 找不到 `id` 字段 | YAML 损坏 | `validate-meta.sh` 校验 |

## 最佳实践

1. **范围分级**：先小范围试跑（如单模块 `--path src/main/java/com/foo/bar`），验证无误后再全量
2. **先 high 后 all**：先解决 high 阻断项，再盘点 medium/low
3. **构建产物必排**：`build/`、`target/`、`out/`、`cmake-build-*/` 含生成代码会严重噪声
4. **复核必做**：high 命中必须逐条人工确认，不能盲信工具
5. **优先优化规则**：误报优先修 constraints，`.astgrepignore` 仅兜底
6. **结果归档**：JSON 报告归档到 CI artifact，便于跨构建对比
7. **增量扫描**：PR/commit 场景只扫变更文件，避免全量噪音（见 recipes）
8. **环境变量固化**：`CODE_CHECKLIST_ROOT` 配置到 shell rc 或 CI 变量，避免硬编码
9. **前端项目必开抽取**：含 `.vue` / `.html` 内联脚本的项目，`js`/`ts` 扫描统一加 `--extract-sfc`，避免漏报与重复上报
10. **临时目录固定**：SFC 抽取目录放在 `/tmp/opencode` 下，不要污染 `/tmp` 根或仓库工作区

## 适用与限制

**适用**：
- Java / C++ / ANSI C / Rust / JavaScript / TypeScript 六种语言（规则库覆盖范围）
- `.vue` / `.html` / `.htm` 内联 `<script>` 的 JS/TS 片段（需 `--extract-sfc`）
- 字符串字面量、AST 结构可表达的代码模式
- CI/CD 质量门禁、提交前预检、审查前盘点

**不适用**：
- 规则库未覆盖的语言（如 Python/Go/Kotlin）需先扩展规则
- 跨文件数据流分析（需 SonarQube / Infer 等）
- 运行时缺陷（需动态分析）
- 复杂类型推断（ast-grep 是语法层，无类型信息）
- 模板表达式（`.vue` 的 `<template>`、`.html` 的非 `<script>` 内容）不参与扫描

## 模板引用

| 模板文件 | 用途 |
|----------|------|
| `templates/run-cli.sh` | 便捷调用脚本（复制到目标项目即可用） |
| `templates/recipes.md` | 进阶命令配方（增量扫描、多语言、CI 模式、单规则调试） |
| `templates/report-summary.md` | 报告字段说明与统计命令 |

---

**技能版本**: 1.1.0

**核心工具**: code-checklist/scripts/run.sh（CLI 模式，含 `--extract-sfc`）

**依赖外部**: `$CODE_CHECKLIST_ROOT` 规则库

**典型耗时**: Java 5k 文件 high 扫描 ≈ 30s-2min；C++ 5k 文件 ≈ 1-3min；SFC 抽取在 JS/TS 扫描基础上增加一次文件遍历与临时文件写入，通常 < 10s

**输出位置**: stdout/stderr 或重定向 JSON 文件
