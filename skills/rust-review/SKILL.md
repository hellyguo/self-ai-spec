---
name: rust-review
description: "该skill没有执行文件，为操作指引：在代码走查时，都需要执行以下流程，确保代码被合理评估"
---

# 代码走查

## 编码规范

授权读取：/disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.rust.md

Read /disk2/helly_data/code/markdown/self-ai-spec/lang-spec/spec.rust.md

## 概述

通过代码走查，找出代码中做得好的部分，找出做得不到位的部分

## 过程

1. 遍历所有的rs，确保对代码之间联系有清晰认识
1. 对设计进行梳理，对使用的设计模式进行整理，对使用合理的进行指出表扬，对使用过度或不合理的进行指出批评
1. 重点走查可被复用/可被抽象的重复代码
1. 重点走查线程问题
   1. 线程创建必须命名
   1. 线程组必须存在关闭入口，且被调用
1. 重点走查代码结构
   1. if分发应优先考虑使用多态，次选switch
   1. if过大应予以抽取，形成独立方法
   1. if判断如果在启动时就能确定的，应予以使用多态
1. 重点检查过长、扇入/扇出过多的方法
1. 重点检查反复调用可缓存变量问题

## 输出

每次结果都以中文输出到 `docs/review/rust-review-{yyyymmdd}-{seq%000}.md` 中

输出文件末尾必须添加署名，格式：`Reviewed by <coding util>+<model name>`，例如：`Reviewed by opencode+GLM5`

## 核心原则

谦逊，目的是治病救人，目的不是羞辱人
