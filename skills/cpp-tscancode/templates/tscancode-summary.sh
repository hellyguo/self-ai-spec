#!/bin/bash
# tscancode-summary.sh - Generate TscanCode analysis summary report

echo "=== TscanCode 分析报告 ==="
echo "分析时间: $(date)"
echo "源代码目录: $SRC_DIR"
echo "---"
echo "总问题数: $(grep -c '\[' tscancode.txt)"
echo "错误: $(grep -c '(error)' tscancode.txt)"
echo "警告: $(grep -c '(warning)' tscancode.txt)"
echo "风格: $(grep -c '(style)' tscancode.txt)"
echo "性能: $(grep -c '(performance)' tscancode.txt)"
