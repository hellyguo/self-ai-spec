---
name: sync-repo-doc
description: "该skill没有执行文件，文件同步，请按步骤执行"
---

基于 git 提交记录同步文件，文件名全大写，默认中文不带后缀，英文以 _en 结尾：

1. README: README.md/README_en.md
2. CHANGELOG: CHANGELOG.md/CHANGELOG_en.md
3. MANUAL: MANUAL.md/MANUAL_en.md

各文档两两互链：

1. README.md      <-> README_en.md
2. CHANGELOG.md   <-> CHANGELOG_en.md
3. MANUAL.md      <-> MANUAL_en.md

特别地，README需引用CHANGELOG/MANUAL(引用各自语言)

1. 文件夹内文件布局与本规划不一致的，以本规划为准
2. 原文件夹下无三份文件的，自动补充 README/CHANGELOG，询问是否补充 MANUAL
3. 原文件夹下无双语模式的，询问是否扩充为双语

