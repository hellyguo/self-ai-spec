---
name: java-env
description: "该skill没有执行文件，为信息输入：Java开发需要的环境信息"
---

# 环境配置

## jvm dir:

- 系统查找目录，/usr/lib/jvm ，其下有多个jvm
- 用户查找目录，${HOME}/lang ，其下有多个jvm

## mvnd dir:

${HOME}/app/maven-mvnd

## mvn dir:

${HOME}/app/apache-maven

## spotbug dir:

${HOME}/app/spotbugs

## pmd dir:

${HOME}/app/pmd

## arthas dir:

${HOME}/app/arthas

## async-profiler dir:

${HOME}/app/async-profiler

## jitwatch dir:

${HOME}/app/jitwatch

## dump parser:

${HOME}/.cargo/bin/hprof-slurp
${HOME}/.cargo/bin/jhh

## 核心原则

- 基于pom.xml的配置查找jdk合适版本 
- 优先使用mvnd

## java bash profile 设置及别名

```bash
env | grep JAVA
alias | grep java
```

