---
name: sync-repo-docs
description: "基于 git 提交记录同步仓库文档：README、CHANGELOG、MANUAL 的中英双语版本与互链。适用于文档滞后于代码、生成或更新发布说明与使用手册。"
---

# 仓库文档同步

基于 git 提交记录同步仓库文档，保持文件名、双语版本与互链一致。

## 文件规划

文件名全大写，中文版不带语言后缀，英文版以 `_en` 结尾：

| 文档 | 中文版 | 英文版 |
|------|--------|--------|
| 项目说明 | `README.md` | `README_en.md` |
| 变更记录 | `CHANGELOG.md` | `CHANGELOG_en.md` |
| 使用手册 | `MANUAL.md` | `MANUAL_en.md` |

## 互链规则

1. `README.md` 与 `README_en.md` 互链。
2. `CHANGELOG.md` 与 `CHANGELOG_en.md` 互链。
3. `MANUAL.md` 与 `MANUAL_en.md` 互链。
4. `README` 需引用同语言的 `CHANGELOG` 与 `MANUAL`：中文 README 引用中文版，英文 README 引用英文版。

## 执行流程

1. 读取 git 提交记录，确定本次需要同步的变更范围（可用 `git log` 或 `git diff`）。
2. 盘点目标文件夹现有文档，与文件规划比对。
3. 按规划重命名、补充或更新文档内容：
   - 中文版为主体，英文版与中文版语义一致。
   - 版本号、日期、变更条目保持双语一致。
4. 补齐互链。
5. 输出变更清单，包含新增、修改、重命名的文件。

## 冲突处理

1. 文件夹内布局与本规划不一致时，以本规划为准。
2. 原文件夹缺少三份文件时，自动补充 `README` 与 `CHANGELOG`，并询问是否补充 `MANUAL`。
3. 原文件夹无双语模式时，询问是否扩充为双语，不得擅自创建英文版。

## 检查清单

- [ ] 三份文档均存在，命名符合规划
- [ ] 双语版本内容语义一致
- [ ] 互链完整且指向正确语言
- [ ] README 已引用 CHANGELOG 与 MANUAL
- [ ] 变更条目与 git 提交记录对应
- [ ] 已输出变更清单
