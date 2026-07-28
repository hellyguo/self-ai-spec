---
name: ast-grep-block
description: "基于 ast-grep 的代码审查门禁：使用 code-checklist 规则集对 Java/C++/ANSI C 项目分级扫描（high/medium/low），输出命中清单与 CI 退出码。仅使用 CLI 模式（run.sh），适用于交互式审查、CI 质量门禁、批量检测"
---

# ast-grep-block 代码审查门禁技能

用 [code-checklist](https://github.com/) 规则集对源代码项目进行**分级 AST 静态审查**，输出命中清单与 CI 退出码。

适用场景：
- 提交/合并前的质量门禁（high 命中则阻断）
- 代码审查前的自动化预检（全级别扫描登记问题）
- 重构前的存量问题盘点（按级别/类别统计）
- CI 流水线集成的质量门禁节点

## 核心思路

**单一 CLI 模式**：直接调用 code-checklist 仓库的 `scripts/run.sh`，该脚本封装了规则遍历、`.astgrepignore` 过滤、分级统计、CI 退出码输出。

不使用 ast-grep-mcp，因为：
- 审查语义需要"全规则批量 + ignore 过滤 + 退出码"，这些是 CLI 模式的优势
- MCP 适合"交互式抽查看上下文"，不适合门禁场景

## 工具依赖

| 工具 | 版本 | 用途 |
|------|------|------|
| ast-grep | >= 0.45.0 | AST 匹配引擎 |
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

# 查看当前覆盖（规则数）
for lang in java cpp ansi_c; do
    echo -n "$lang: "
    find "$CODE_CHECKLIST_ROOT/rules/$lang" -name '*.yml' | wc -l
done
```

> 如需切换规则库版本或位置，请在 shell 环境变量中配置 `CODE_CHECKLIST_ROOT`，本 skill 不在仓库内复制规则。

## 分级语义（用户口径）

| 级别 | 含义 | CI 行为 | run.sh 退出码 |
|------|------|---------|---------------|
| **high** | 必须修改，必须本次修改 | 阻断提交/合并 | 1 |
| **medium** | 必须修改，但并非本次修改 | 登记跟踪，下次迭代 | 0 |
| **low** | 可接受不改 | 提示性建议 | 0 |

## 执行流程

### 步骤 1：确定目标范围

先识别项目结构，明确：

- 源代码根目录（如 `src/main/java`、`src/`、`QES3/src`）
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
```

### 步骤 2：选语言与级别

| 参数 | 取值 | 默认 |
|------|------|------|
| `--lang` | `java` / `cpp` / `ansi_c` | 必填 |
| `--level` | `high` / `medium` / `low` | 任选其一 |
| `--all` | 扫描所有级别 | 替代 `--level` |

**推荐顺序**：先跑 `high` 修阻断项，再跑 `--all` 盘点全量。

### 步骤 3：执行扫描（核心命令）

```bash
# 3a. 仅 high 级别（CI 门禁场景）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --level high \
    --path <project_root>
echo "退出码: $?  # 0 通过 / 1 high 命中 / 2 参数错误"

# 3b. 全级别扫描（盘点场景）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --all \
    --path <project_root>

# 3c. JSON 输出（CI/工具对接）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --level high \
    --path <project_root> --json > report.json
echo $?  # 退出码仍正确返回
```

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
    "level": "high"
  },
  ...
]
```

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
| JSON 报告 | `run.sh --lang java --all --path . --json > r.json` |
| 仅看 high 命中文件 | `jq -r 'select(.level=="high")\|.file' r.json \| sort -u` |
| 规则分布 Top N | `jq -r '.ruleId' r.json \| sort \| uniq -c \| sort -rn \| head` |
| 校验规则库 | `"$CODE_CHECKLIST_ROOT/scripts/validate-meta.sh && "$CODE_CHECKLIST_ROOT/scripts/validate-examples.sh"` |

## 输出位置

- 文本报告：默认 stderr + stdout（按 `run.sh` 实现）
- JSON 报告：通过 `--json` 参数，需重定向到文件
- 临时输出：本 skill 不创建临时文件，由调用方决定保存路径

## 陷阱与故障排除

| 现象 | 原因 | 解决 |
|------|------|------|
| `未找到 ast-grep` | 未安装或不在 PATH | `cargo install ast-grep` 或包管理器安装 |
| `规则库未就绪` | `CODE_CHECKLIST_ROOT` 配错或仓库缺失 | 检查环境变量、clone 仓库 |
| 扫描结果为 0 命中但明显有问题 | 构建产物目录被误排（`build/`）或语言判断错 | 确认 `--lang` 与文件扩展名一致 |
| high 退出码总是 1 | 有 high 命中（正常） | 按步骤 5 修复或登记 `.astgrepignore` |
| `.astgrepignore` 不生效 | 放错位置 | 必须放在被扫描项目根，不是规则库根 |
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

## 适用与限制

**适用**：
- Java / C++ / ANSI C 三语言（规则库覆盖范围）
- 字符串字面量、AST 结构可表达的代码模式
- CI/CD 质量门禁、提交前预检、审查前盘点

**不适用**：
- 规则库未覆盖的语言（Python/Go/Rust 等需扩展规则）
- 跨文件数据流分析（需 SonarQube / Infer 等）
- 运行时缺陷（需动态分析）
- 复杂类型推断（ast-grep 是语法层，无类型信息）

## 模板引用

| 模板文件 | 用途 |
|----------|------|
| `templates/run-cli.sh` | 便捷调用脚本（复制到目标项目即可用） |
| `templates/recipes.md` | 进阶命令配方（增量扫描、多语言、CI 模式、单规则调试） |
| `templates/report-summary.md` | 报告字段说明与统计命令 |

---

**技能版本**: 1.0.0
**核心工具**: code-checklist/scripts/run.sh（CLI 模式）
**依赖外部**: `$CODE_CHECKLIST_ROOT` 规则库
**典型耗时**: Java 5k 文件 high 扫描 ≈ 30s-2min；C++ 5k 文件 ≈ 1-3min
**输出位置**: stdout/stderr 或重定向 JSON 文件
