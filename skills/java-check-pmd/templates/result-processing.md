# PMD分析结果处理脚本模板

## 结果解析脚本

```bash
#!/bin/bash
# 解析PMD输出，统计问题类型
echo "=== PMD分析报告 ==="
echo "总问题数: $(grep -c ":" pmd.txt)"
echo "空catch块: $(grep -c "EmptyCatchBlock" pmd.txt)"
echo "圈复杂度问题: $(grep -c "CyclomaticComplexity" pmd.txt)"
echo "短变量名: $(grep -c "ShortVariable" pmd.txt)"
```

## 问题严重性分类

```bash
# 高风险问题
grep -E "(HardCodedCryptoKey|InsecureCryptoIv|DataflowAnomalyAnalysis)" pmd.txt

# 代码质量问题
grep -E "(CyclomaticComplexity|GodClass|ExcessiveMethodLength)" pmd.txt

# 代码风格问题
grep -E "(ShortVariable|LongVariable|OnlyOneReturn)" pmd.txt
```

## 生成趋势报告

```bash
# 跟踪问题趋势
echo "日期: $(date)" >> pmd-trend.txt
echo "圈复杂度>10的方法: $(grep "CyclomaticComplexity" pmd.txt | grep -o "[0-9][0-9]" | awk '$1 > 10' | wc -l)" >> pmd-trend.txt
echo "代码行数>100的方法: $(grep "ExcessiveMethodLength" pmd.txt | wc -l)" >> pmd-trend.txt
```
