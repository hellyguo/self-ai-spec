---
name: code-detect-dup
description: "代码重复度检测技能：使用 Simian 和 JSCPD 检测项目中的重复代码"
---

# 工具一：Simian

```bash
java -jar ~/app/simian/simian-4.2.1.jar \
  -language=java -threshold=20 \
  $(fd -H -I -s -c never -t f -e java | grep --color=never -v "\/test\/" | xargs) \
  > docs/dup-{yyyy-mm-dd}-{seq}.txt 2>&1
```

1. threshold 代表重复代码的行数，应根据实际情况调整
2. language 根据实际情况调整：java/cpp/csharp/javascript
3. fd0='fd -H -I -s -c never', grep0='grep --color=never'
4. seq 应从 001 开始，按日重置，报告应 git 留档

# 工具二：JSCPD

```bash
# 安装
npm install -g jscpd

# 检测并生成 HTML 报告
jscpd src/ --min-lines 15 --reporters html,console --output docs/jscpd-{yyyy-mm-dd}-{seq}

# 排除目录
jscpd src/ --min-lines 15 --ignore "**/test/**,**/node_modules/**" --reporters html,console

# 多语言项目
jscpd . --extensions java,ts,py,cpp --min-lines 15 --reporters html --output docs/jscpd-report
```

1. --min-lines 最小重复行数，建议 Java 15-20，Python 10-15，Shell 5-10
2. --reporters 支持console/html/json/xml
3. --extensions 指定语言，不指定则自动检测
4. HTML 报告在 output/index.html

# 工具对比

| 特性 | Simian | JSCPD |
| --- | --- | --- |
| 语言 | Java/C/C++/C# | 150+语言 |
| 报告 | 文本 | HTML可视化 |
| 安装 | JAR包 | npm |
