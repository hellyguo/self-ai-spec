---
name: java-gen-unittest
description: "该skill没有执行文件，为操作指引：生成Java单元测试代码"
---

# 生成单元测试代码

## 概述

读取现有的Java代码，生成单元测试代码，

## 过程

1. 遍历所有的java，确保对代码之间联系有清晰认识
1. 对java文件解析，进行构建单元测试
1. 对可能需要外部数据的外部依赖的，进行mock，保证代码可执行，可使用库：mockito/powermock
1. 最终生成一个suite，包裹所有单元测试，可一次性执行所有测试(如已存在suite，将生成的单元测试补入其中)

## 输出

按 Java 的 maven 约定，写入 src/test/java 对应的 package 下

## 核心原则

尽可能测试到所有的方法，所有的分支，保证方法覆盖率/分支覆盖率
