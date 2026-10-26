---
name: code-detect-dup
description: "使用 Simian 与 JSCPD 检测项目中的重复代码，统计重复率并生成报告。适用于代码重复度专项检查、重构前评估、质量评分中的重复度维度。"
---

# 代码重复度检测

使用 Simian 与 JSCPD 检测项目中的重复代码，按语言选择工具，报告统一归档到 `docs/dup/`。

## 适用场景

- 重构前评估重复代码规模
- `code-detect-problem` 评分中的重复度维度
- 代码审查的重复代码专项检查

## 工具选择

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| Java / C / C++ / C# | Simian | 语义级重复检测，误报低 |
| 前端、Python、Shell 等多语言 | JSCPD | 支持 150+ 语言，HTML 报告直观 |
| 需要可视化报告 | JSCPD | 输出 HTML |
| CI 快速门禁 | Simian | 文本输出，退出码易判定 |

## 工具一：Simian

```bash
java -jar ~/app/simian/simian-4.2.1.jar \
  -language=java -threshold=20 \
  $(fd -H -I -s -c never -t f -e java | grep --color=never -v "\/test\/" | xargs) \
  > docs/dup/dup-{yyyymmdd}-{seq}.txt 2>&1
```

参数说明：

1. `threshold`：重复代码行数阈值，按项目实际调整，Java 建议 15-20。
2. `language`：按项目语言调整，可选 `java` / `cpp` / `csharp` / `javascript`。
3. `seq`：从 `001` 开始按日重置，报告必须 git 留档。

## 工具二：JSCPD

```bash
# 安装
npm install -g jscpd

# 检测并生成 HTML 报告
jscpd src/ --min-lines 15 --reporters html,console --output docs/dup/jscpd-{yyyymmdd}-{seq}

# 排除目录
jscpd src/ --min-lines 15 --ignore "**/test/**,**/node_modules/**" --reporters html,console

# 多语言项目
jscpd . --extensions java,ts,py,cpp --min-lines 15 --reporters html --output docs/dup/jscpd-report
```

参数说明：

1. `--min-lines`：最小重复行数，Java 15-20，Python 10-15，Shell 5-10。
2. `--reporters`：支持 `console` / `html` / `json` / `xml`。
3. `--extensions`：不指定则自动检测。
4. HTML 报告入口：`<output>/index.html`。

## 工具对比

| 特性 | Simian | JSCPD |
| ---- | ------ | ----- |
| 语言 | Java/C/C++/C# | 150+ 语言 |
| 报告 | 文本 | HTML 可视化 |
| 安装 | JAR 包 | npm |
| 退出码 | 存在重复即非 0 | 默认 0，需结合报告判断 |

## 输出与判读

- 报告归档路径：`docs/dup/`，命名 `dup-{yyyymmdd}-{seq}.txt` 或 `jscpd-{yyyymmdd}-{seq}/`。
- 重复率分级（与 `code-detect-problem` 评分口径一致）：
  - 低于 5%：优
  - 5% 至 15%：可接受
  - 15% 至 30%：需重构
  - 高于 30%：严重，优先处理
- 判读时排除测试代码、生成代码与第三方库，避免误判。

## 检查清单

- [ ] 已按语言选择工具
- [ ] 已排除测试、生成代码与第三方库
- [ ] 报告已归档到 `docs/dup/`
- [ ] 重复率与热点文件已记录
- [ ] 已给出重构优先级建议
