#!/bin/bash

# markdown 排版检查：一个逻辑块一行 + 表格前空行
#
# 依据 rules/interaction.rules.md 的 markdown 排版条款。本仓库不使用 markdownlint 等
# 按行宽计算的检查，唯一验收标准是本脚本。
#
# 检查项：
#   1. WRAP  —— 段内换行：同一段落、同一列表项、同一引用块被拆成多行。判据是“同块连续文本”，
#               与句号无关，因此“一句一换行”同样会被判出；整段写成一行、句号后继续写则不判。
#   2. TABLE —— 表格块紧贴上一段落，缺空行（GFM 下会被并入段落）。
#
# 注意：
#   1. 本脚本只认结构信号，不判断“逻辑归类”是否合理；归类由作者决定，脚本只保证“一个逻辑块占一行”。
#   2. code fence、YAML 前置数据、HTML 注释、缩进代码块内的内容一律跳过；缩进代码块以空行起始识别。
#   3. 行尾两个空格或反斜杠视为显式硬换行（签名/元数据区用法），不判违规。
#   4. 符号链接文件默认跳过，避免改写外部仓库。
#   5. 退出码：0 无违规，1 存在违规，2 参数或环境错误。
#
# 用法：bin/check-md-wrap.sh [选项] [路径...]
#   默认只检查变更集（与 HEAD 的差异 + 未跟踪文件），无 git 时退化为全仓
#   -a, --all       检查仓库全部受控 markdown（会暴露存量问题）
#   -q, --quiet     只输出按文件聚合的计数
#   -h, --help      显示帮助

set -u

QUIET=0
SCOPE=changed

usage() {
    sed -n '3,26p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
}

while [ $# -gt 0 ]; do
    case "$1" in
        -a|--all) SCOPE=all; shift ;;
        -q|--quiet) QUIET=1; shift ;;
        -h|--help) usage ;;
        --) shift; break ;;
        -*) echo "未知选项: $1" >&2; exit 2 ;;
        *) break ;;
    esac
done

TARGETS=("$@")

FILES=()
if [ ${#TARGETS[@]} -gt 0 ]; then
    for t in "${TARGETS[@]}"; do
        if [ -d "$t" ]; then
            while IFS= read -r f; do FILES+=("$f"); done < <(find "$t" -name '*.md' -type f | sort)
        elif [ -f "$t" ]; then
            FILES+=("$t")
        else
            echo "路径不存在: $t" >&2
            exit 2
        fi
    done
elif git rev-parse --git-dir >/dev/null 2>&1; then
    if [ "$SCOPE" = all ]; then
        while IFS= read -r f; do [ -n "$f" ] && FILES+=("$f"); done < <(git ls-files -- '*.md')
    else
        while IFS= read -r f; do [ -n "$f" ] && FILES+=("$f"); done < <(
            {
                git diff --name-only --diff-filter=ACMR HEAD -- '*.md' 2>/dev/null
                git ls-files -o --exclude-standard -- '*.md'
            } | sort -u
        )
    fi
else
    while IFS= read -r f; do FILES+=("$f"); done < <(find . -name '*.md' -type f | sed 's|^\./||' | sort)
fi

# 过滤：物理文件存在、非符号链接、排除本地记忆文件
CHECK=()
for f in "${FILES[@]}"; do
    [ -f "$f" ] || continue
    [ -L "$f" ] && continue
    case "$(basename "$f")" in MEMORY.md) continue ;; esac
    CHECK+=("$f")
done

if [ ${#CHECK[@]} -eq 0 ]; then
    echo "markdown 排版检查通过：无待检查文件（范围: $SCOPE）"
    exit 0
fi

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

awk '
function is_fence(s)    { return s ~ /^[ \t]*(```|~~~)/ }
function is_heading(s)  { return s ~ /^[ \t]*#{1,6}[ \t]/ }
function is_hr(s)       { return s ~ /^[ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*$/ }
function is_table(s)    { return s ~ /^[ \t]*\|/ }
function is_quote(s)    { return s ~ /^[ \t]*>/ }
function is_list(s)     { return s ~ /^[ \t]*([-*+]|[0-9]+[.)])[ \t]+/ }
function is_html(s)     { return s ~ /^[ \t]*</ }
function is_linkdef(s)  { return s ~ /^[ \t]*\[[^]]+\]:[ \t]/ }
function is_indented(s) { return s ~ /^(\t|  )/ }
function is_blank(s)    { return s ~ /^[ \t]*$/ }

function starts_block(s) {
    return is_fence(s) || is_heading(s) || is_hr(s) || is_table(s) || is_quote(s) ||
           is_list(s) || is_html(s) || is_linkdef(s)
}
function explicit_break(s) {
    # 行尾两个空格或反斜杠：显式硬换行，仅签名/元数据区允许
    return (s ~ /[ \t][ \t]$/ || s ~ /\\$/)
}
function same_block(p, c) {
    # 段落续段落、列表项续正文、引用续引用属于同一逻辑块；跨块不判
    if (is_quote(p) && is_quote(c))      return 1
    if (is_quote(p) || is_quote(c))      return 0
    if (is_table(p) || is_table(c))      return 0
    if (is_heading(p) || is_heading(c))  return 0
    if (is_hr(p) || is_hr(c))            return 0
    if (is_linkdef(p) || is_linkdef(c))  return 0
    if (is_html(p) || is_html(c))        return 0
    if (is_fence(p) || is_fence(c))      return 0
    return 1
}
function trim(s) { sub(/[ \t]+$/, "", s); return s }
function preview(s) {
    s = trim(s)
    if (length(s) > 60) s = substr(s, 1, 60) "..."
    return s
}

FNR == 1 {
    in_front = 0; in_fence = 0; in_comment = 0; in_code = 0
    if ($0 ~ /^---[ \t]*$/) in_front = 1
    prev = ""; prev_no = 0; prev_blank = 1; table_open = 0
    next
}

{
    line = $0
    no = FNR

    if (in_front) {
        if (no > 1 && line ~ /^(---|\.\.\.)[ \t]*$/) in_front = 0
        prev = line; prev_no = no; prev_blank = 0
        next
    }

    if (in_comment) {
        if (line ~ /-->/) in_comment = 0
        prev = line; prev_no = no; prev_blank = is_blank(line)
        next
    }
    if (line ~ /^[ \t]*<!--/ && line !~ /-->/) {
        in_comment = 1
        prev = line; prev_no = no; prev_blank = 0
        next
    }

    if (is_fence(line)) {
        in_fence = !in_fence
        prev = line; prev_no = no; prev_blank = 0; table_open = 0
        next
    }
    if (in_fence) {
        prev = line; prev_no = no; prev_blank = 0
        next
    }

    # 缩进代码块：空行之后出现缩进行即为开始，遇到非空非缩进行结束
    if (in_code) {
        if (is_blank(line) || is_indented(line)) {
            prev = line; prev_no = no; prev_blank = is_blank(line)
            next
        }
        in_code = 0
    }
    if (prev_blank && is_indented(line)) {
        in_code = 1
        prev = line; prev_no = no; prev_blank = 0
        next
    }

    if (is_table(line)) {
        if (!table_open) {
            table_open = 1
            if (prev_no > 0 && !prev_blank && !is_table(prev)) printf "%s:%d: TABLE 表格前缺空行\n", FILENAME, no
        }
    } else {
        table_open = 0
    }

    if (is_blank(line)) {
        prev = line; prev_no = no; prev_blank = 1
        next
    }

    if (prev_no > 0 && !prev_blank && prev_no == no - 1) {
        # 新块起始行（标题/列表/表格/围栏等）与上一行不同块，不判段内换行
        if (!starts_block(line)) {
            if (same_block(prev, line) && !explicit_break(prev)) {
                printf "%s:%d: WRAP 段内换行：本行与上一行同属一个逻辑块，应并入上一行或以空行分隔 -> %s\n", FILENAME, no, preview(line)
            }
        } else if (is_quote(line) && is_quote(prev) && !explicit_break(prev)) {
            printf "%s:%d: WRAP 段内换行：引用块被拆成多行，应写成一个逻辑行 -> %s\n", FILENAME, no, preview(line)
        }
    }

    prev = line; prev_no = no; prev_blank = 0
}
' "${CHECK[@]}" > "$TMP"

TOTAL=$(grep -c . "$TMP" 2>/dev/null || true)
TOTAL=${TOTAL:-0}

if [ "$TOTAL" -eq 0 ]; then
    echo "markdown 排版检查通过：${#CHECK[@]} 个文件无违规（范围: $SCOPE）"
    exit 0
fi

if [ "$QUIET" -eq 1 ]; then
    cut -d: -f1 "$TMP" | sort | uniq -c | sort -rn
else
    cat "$TMP"
fi

echo "违规合计: $TOTAL 处（范围: $SCOPE；修法：续行并入上一行，或补空行拆成独立段落）" >&2
exit 1
