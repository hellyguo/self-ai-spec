#!/usr/bin/env bash
# ast-grep-block 便捷调用脚本
# 用法: ./run-cli.sh <lang> <level|all> <path> [--json] [--out <file>]
# 示例:
#   ./run-cli.sh java high .                # 仅扫 high，文本输出
#   ./run-cli.sh cpp all . --json --out r.json  # 全级别 JSON 报告
#   ./run-cli.sh ansi_c high src/           # 只扫 src/ 子目录
#
# 设计原则:
#   - 不重新实现 run.sh，仅做参数包装 + 报告归档
#   - 自动定位 $CODE_CHECKLIST_ROOT
#   - 退出码透传 run.sh（0 通过 / 1 high 命中 / 2 参数错误）
set -euo pipefail

# ---- 锚定规则库 ----
if [[ -z "${CODE_CHECKLIST_ROOT:-}" ]]; then
    CODE_CHECKLIST_ROOT=/disk2/helly_data/code/ast-grep-rules/code-checklist
fi
if [[ ! -x "$CODE_CHECKLIST_ROOT/scripts/run.sh" ]]; then
    echo "[run-cli] 规则库未就绪: $CODE_CHECKLIST_ROOT/scripts/run.sh 不存在或不可执行" >&2
    echo "         请设置 CODE_CHECKLIST_ROOT 环境变量指向 code-checklist 仓库根" >&2
    exit 2
fi

# ---- 参数解析 ----
if [[ $# -lt 3 ]]; then
    cat <<EOF
用法: $0 <lang> <level|all> <path> [--json] [--out <file>]
参数:
  lang    java | cpp | ansi_c
  level   high | medium | low | all
  path    被扫描的项目根（绝对或相对路径）
选项:
  --json            输出 SARIF 风格 JSON（默认文本）
  --out <file>      将输出保存到文件（默认 stdout）
  --help, -h        显示帮助
环境变量:
  CODE_CHECKLIST_ROOT  规则库根（默认 $CODE_CHECKLIST_ROOT）
EOF
    exit 2
fi

LANG_ARG="$1"
LEVEL_ARG="$2"
PATH_ARG="$3"
shift 3

JSON_OUTPUT=0
OUT_FILE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_OUTPUT=1; shift ;;
        --out)  OUT_FILE="$2"; shift 2 ;;
        -h|--help) sed -n '5,25p' "$0"; exit 0 ;;
        *) echo "[run-cli] 未知参数: $1" >&2; exit 2 ;;
    esac
done

# 校验 lang
case "$LANG_ARG" in
    java|cpp|ansi_c) ;;
    *) echo "[run-cli] 不支持的语言: $LANG_ARG（仅 java/cpp/ansi_c）" >&2; exit 2 ;;
esac

# 校验 level
case "$LEVEL_ARG" in
    high|medium|low|all) ;;
    *) echo "[run-cli] 非法级别: $LEVEL_ARG（high/medium/low/all）" >&2; exit 2 ;;
esac

# 校验 path
if [[ ! -d "$PATH_ARG" ]]; then
    echo "[run-cli] 路径不存在: $PATH_ARG" >&2; exit 2
fi
PATH_ARG="$(cd "$PATH_ARG" && pwd)"

# ---- 构造 run.sh 参数 ----
RUN_ARGS=(--lang "$LANG_ARG" --path "$PATH_ARG")
if [[ "$LEVEL_ARG" == "all" ]]; then
    RUN_ARGS+=(--all)
else
    RUN_ARGS+=(--level "$LEVEL_ARG")
fi
[[ "$JSON_OUTPUT" -eq 1 ]] && RUN_ARGS+=(--json)

# ---- 执行 + 输出归档 ----
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
if [[ -n "$OUT_FILE" ]]; then
    # 保存到文件，stdout 静默
    "$CODE_CHECKLIST_ROOT/scripts/run.sh" "${RUN_ARGS[@]}" > "$OUT_FILE" 2>/tmp/run-cli-$TIMESTAMP.err
    rc=$?
    [[ -s /tmp/run-cli-$TIMESTAMP.err ]] && cat /tmp/run-cli-$TIMESTAMP.err >&2
    rm -f /tmp/run-cli-$TIMESTAMP.err
    echo "[run-cli] 报告已保存: $OUT_FILE (退出码=$rc)"
    exit $rc
else
    # 直接输出到 stdout
    exec "$CODE_CHECKLIST_ROOT/scripts/run.sh" "${RUN_ARGS[@]}"
fi
