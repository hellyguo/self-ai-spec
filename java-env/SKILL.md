---
name: java-env
description: "该skill没有执行文件，为信息输入：Java开发需要的环境信息"
---

# 环境配置

## jvm dir:

- 系统查找目录，/usr/lib/jvm ，其下有多个jvm
- 用户查找目录，/home/helly/lang ，其下有多个jvm

## mvnd dir:

/home/helly/app/maven-mvnd-1.0.2-linux-amd64

## mvn dir:

/home/helly/app/apache-maven-3.9.9

## spotbug dir:

/home/helly/app/spotbugs-4.7.3

## pmd dir:

/home/helly/app/pmd-bin-6.19.0

## 核心原则

- 基于pom.xml的配置查找jdk合适版本 
- 优先使用mvnd
