#!/bin/bash
# tscancode-check.sh - TscanCode analysis wrapper

TSCANCODE=/home/helly/app/TscanCode.linux/tscancode
SRC_DIR=${1:-src}
OUTPUT=${2:-tscancode-report.txt}

echo "=== TscanCode 分析开始 ==="
echo "源代码目录: $SRC_DIR"
echo "输出文件: $OUTPUT"

$TSCANCODE --enable=all --quiet -j 4 $SRC_DIR 2> "$OUTPUT"

echo "=== 分析完成 ==="
echo "问题数量: $(grep -c '\[' "$OUTPUT" 2>/dev/null || echo 0)"
