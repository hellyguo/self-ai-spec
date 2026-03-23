---
name: java-g2m
description: "该skill没有执行文件，为操作要求：从 gradle 转 maven"
---

# gradle 转 maven

## java env:

通过 skill /java-env

## 要求

1. 将 gradle 转 maven，除非有明确输入切换jdk，否则保持jdk要求不变
2. 将所有的dependency都正确无误地迁移到pom.xml中，不重不漏
3. 其中若有特别的gradle任务，尽可能满足。如果无法做到，可以舍弃，但需要最终输出未能成功转化的任务清单详情

