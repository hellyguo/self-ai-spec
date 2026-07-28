# ast-grep-block 进阶命令配方

> 假设环境变量 `$CODE_CHECKLIST_ROOT` 已配置，`run.sh` = `$CODE_CHECKLIST_ROOT/scripts/run.sh`。

## 1. 增量扫描：仅扫变更文件

### 1a. Git pre-commit 钩子（仅扫 staged 文件）

code-checklist 仓库自带 `.githooks/pre-commit`，启用方式：

```bash
# 在目标项目根
cp "$CODE_CHECKLIST_ROOT/.githooks/pre-commit" .githooks/pre-commit
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

之后每次 `git commit` 时，仅 staged 的 `.java` 文件会跑 high 级别规则，命中则拒绝提交。

### 1b. PR / MR 仅扫变更文件

```bash
# 获取 PR 中变更的 Java 文件清单
mapfile -t CHANGED < <(git diff --name-only --diff-filter=AM origin/main...HEAD -- '*.java')

if [[ ${#CHANGED[@]} -eq 0 ]]; then
    echo "无 Java 变更，跳过扫描"
    exit 0
fi

# 临时目录中 checkout 变更文件，再扫描该目录
TMPDIR_PR=$(mktemp -d)
trap 'rm -rf "$TMPDIR_PR"' EXIT
mkdir -p "$TMPDIR_PR/src"
for f in "${CHANGED[@]}"; do
    mkdir -p "$TMPDIR_PR/$(dirname "$f")"
    cp "$f" "$TMPDIR_PR/$f"
done

"$CODE_CHECKLIST_ROOT/scripts/run.sh" \
    --lang java --level high \
    --path "$TMPDIR_PR" --json > pr-report.json
echo $?
```

### 1c. C++ 变更扫描

```bash
mapfile -t CHANGED < <(git diff --name-only --diff-filter=AM origin/main...HEAD -- '*.cpp' '*.h' '*.hpp')
# 后续同 1b，--lang 改为 cpp
```

## 2. 多语言批量扫描

### 2a. 单项目多语言

```bash
PROJECT=/path/to/project
mkdir -p reports/

for lang in java cpp ansi_c; do
    # 检测该语言是否有源文件
    case "$lang" in
        java)   fd --no-ignore -e java -t f "$PROJECT" | head -1 ;;
        cpp)    fd --no-ignore -e cpp -e h -t f "$PROJECT" | head -1 ;;
        ansi_c) fd --no-ignore -e c -t f "$PROJECT" | head -1 ;;
    esac | grep -q . || { echo "$lang: 无源文件，跳过"; continue; }

    "$CODE_CHECKLIST_ROOT/scripts/run.sh" \
        --lang "$lang" --level high \
        --path "$PROJECT" --json > "reports/$lang-high.json"
    echo "$lang high 退出码: $?"
done
```

### 2b. 聚合多语言报告

```bash
{
    echo "# ast-grep 审查汇总"
    echo
    for r in reports/*-high.json; do
        lang=$(basename "$r" .json | cut -d- -f1)
        count=$(jq 'length' "$r")
        echo "- $lang high: $count 条"
    done
} > reports/SUMMARY.md
```

## 3. 大项目分批扫描

万级文件直接 `--path .` 会极慢（ast-grep 串行遍历规则 × 文件），按目录分批：

```bash
PROJECT=/path/to/huge-project
OUTDIR=reports/
mkdir -p "$OUTDIR"

# 列出顶层源码目录
mapfile -t MODULES < <(fd -t d -d 2 . "$PROJECT/src" 2>/dev/null | sort)

for mod in "${MODULES[@]}"; do
    mod_name=$(basename "$mod")
    echo "[$(date +%T)] 扫描: $mod_name"
    "$CODE_CHECKLIST_ROOT/scripts/run.sh" \
        --lang java --level high \
        --path "$mod" --json > "$OUTDIR/$mod_name.json" 2>"$OUTDIR/$mod_name.err"
done

# 合并
jq -s 'flatten' "$OUTDIR"/*.json > "$OUTDIR/all-high.json"
jq 'length' "$OUTDIR/all-high.json"
```

## 4. 单规则调试

### 4a. 直接用 ast-grep CLI 跑单规则

```bash
RULE_FILE="$CODE_CHECKLIST_ROOT/rules/java/high/0000-0999/empty-catch-block.yml"

# 文本输出
ast-grep scan -r "$RULE_FILE" --lang java <target_dir>

# JSON 输出
ast-grep scan -r "$RULE_FILE" --json <target_dir> | jq 'length'
```

### 4b. 调试 pattern（查看 AST 结构）

```bash
# 查看 Java 代码的 CST 结构，定位正确的 kind/pattern
ast-grep run -p '$X' --lang java --debug-query=cst <file.java>

# 查看 catch 块的 AST 节点
ast-grep run -p 'catch ($E) {$B}' --lang java --debug-query=ast <file.java>
```

### 4c. 找一个规则的具体位置

```bash
RULE_ID=empty-catch-block
find "$CODE_CHECKLIST_ROOT/rules" -name "$RULE_ID.yml"
```

## 5. CI 流水线集成

### 5a. GitHub Actions

```yaml
# .github/workflows/code-checklist.yml
name: code-checklist
on: [pull_request]
jobs:
  ast-grep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/checkout@v4
        with:
          repository: <org>/ast-grep-rules
          path: ast-grep-rules
      - name: Install deps
        run: |
          cargo install ast-grep --locked
          sudo apt-get install -y jq
      - name: Run code-checklist
        env:
          CODE_CHECKLIST_ROOT: ${{ github.workspace }}/ast-grep-rules/code-checklist
        run: |
          "$CODE_CHECKLIST_ROOT/scripts/run.sh" \
            --lang java --level high \
            --path . --json > ast-grep-report.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: ast-grep-report
          path: ast-grep-report.json
```

### 5b. GitLab CI

```yaml
# .gitlab-ci.yml
code-checklist:
  image: rust:latest
  variables:
    CODE_CHECKLIST_ROOT: $CI_PROJECT_DIR/ast-grep-rules/code-checklist
  before_script:
    - cargo install ast-grep --locked
    - apt-get update && apt-get install -y jq python3-pyyaml
    - git clone <rules-repo-url> ast-grep-rules
  script:
    - "$CODE_CHECKLIST_ROOT/scripts/run.sh --lang java --level high --path . --json > report.json"
  artifacts:
    when: always
    paths: [report.json]
```

## 6. 报告对比（趋势）

跨构建对比 high 命中数，监控是否恶化：

```bash
# 基线
"$CODE_CHECKLIST_ROOT/scripts/run.sh" --lang java --level high --path . --json > baseline.json
BASELINE_HIGH=$(jq 'length' baseline.json)

# 当前
"$CODE_CHECKLIST_ROOT/scripts/run.sh" --lang java --level high --path . --json > current.json
CURRENT_HIGH=$(jq 'length' current.json)

# 新增 high 命中（当前有，基线无的 file:line:ruleId 组合）
jq -s '
  .[0] as $base
  | .[1] as $cur
  | $cur
  | map(.key = "\(.file):\(.range.start.line):\(.ruleId)")
  | map(.key) as $cur_keys
  | ($base | map("\(.file):\(.range.start.line):\(.ruleId)") ) as $base_keys
  | $cur_keys - $base_keys
  | "新增 high 命中: \(length) 条"
' baseline.json current.json
```

## 7. 按类别统计

```bash
# 需要关联规则的 category 字段（在规则 YAML 中定义）
jq -r '
    . as $hits
    | reduce $hits[] as $h (
        {};
        .[$h.ruleId] += 1
    )
    | to_entries
    | sort_by(-.value)
    | .[]
    | "\(.value)\t\(.key)"
' report.json
```

## 8. 排除测试目录

`run.sh` 不支持 `--globs` 排除目录，需通过 path 控制或 `.astgrepignore`：

```bash
# 方案 A：在 .astgrepignore 中按规则排除
cat >> .astgrepignore <<'EOF'
- rule: "*"
  paths:
    - "src/test/**"
    - "**/test/**"
    - "**/*Test.java"
EOF

# 方案 B：扫描非测试目录（需手工列出）
"$CODE_CHECKLIST_ROOT/scripts/run.sh" --lang java --level high --path src/main/java
```

> 注意：`.astgrepignore` 的 `rule: "*"` 是否生效取决于 run.sh 实现，未支持时需逐规则列出。

## 9. 输出 SARIF 格式（VSCode 集成）

run.sh 的 `--json` 输出是简化的 SARIF 风格，可直接转 SARIF 2.1.0：

```bash
jq '{
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    version: "2.1.0",
    runs: [{
        tool: { driver: { name: "ast-grep code-checklist", version: "1.0" } },
        results: map({
            ruleId: .ruleId,
            level: (if .level == "high" then "error"
                    elif .level == "medium" then "warning"
                    else "note" end),
            message: { text: .lines },
            locations: [{
                physicalLocation: {
                    artifactLocation: { uri: .file },
                    region: { startLine: .range.start.line + 1, startColumn: .range.start.column }
                }
            }]
        })
    }]
}' report.json > report.sarif
```

VSCode 装 "SARIF Viewer" 插件即可在编辑器中直接定位命中。

## 10. 与其他审查工具联动

ast-grep-block 是**语法层**门禁，建议与以下工具配合（互补，不替代）：

| 工具 | 层次 | 与 ast-grep-block 关系 |
|------|------|----------------------|
| SpotBugs / PMD | 字节码 / 数据流 | 互补：ast-grep 早期拦截，SpotBugs 深度分析 |
| cppcheck | C/C++ 缺陷 | 互补：cppcheck 跨函数分析，ast-grep 模式匹配 |
| SonarQube | 全栈 | 互补：Sonar 整体质量，ast-grep 自定义规则 |
| clang-tidy | C++ 风格 | 重叠：部分规则可由 ast-grep 替代（CI 更快） |

典型组合：`ast-grep-block (high 阻断) + cppcheck (warning 提示) + Sonar (整体趋势)`。
