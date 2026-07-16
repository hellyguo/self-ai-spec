# PMD输出格式模板

## 文本格式（默认）

```text
src/main/java/com/example/Test.java:10:  EmptyCatchBlock: Avoid empty catch blocks
src/main/java/com/example/Test.java:25:  ShortVariable: Avoid variables with short names like 'i'
src/main/java/com/example/Test.java:45:  CyclomaticComplexity: The method 'process' has a cyclomatic complexity of 12
```

## XML格式（用于集成）

```bash
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f xml -r pmd.xml
```

## CSV格式（表格数据）

```bash
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f csv -r pmd.csv
```

## HTML报告（可视化）

```bash
$PMD_CLI pmd -d $SRC_DIR -R rulesets/java/quickstart.xml -f html -r pmd.html
```
