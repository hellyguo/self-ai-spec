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

## 核心原则

- 基于pom.xml的配置查找jdk合适版本 
- 优先使用mvnd

## java bash profile 设置及别名

```bash
# 注意：bash 工具需先加载 .bashrc 以获取 alias
source ~/.bashrc && env | grep JAVA
source ~/.bashrc && alias | grep java
```

### Java 版本切换 Alias

```bash
java7='JAVA_HOME=$JAVA_HOME7 PATH=$JAVA_HOME7/bin:$NOJAVA_HOME_PATH java'
java8='JAVA_HOME=$JAVA_HOME8 PATH=$JAVA_HOME8/bin:$NOJAVA_HOME_PATH java'
java11='JAVA_HOME=$JAVA_HOME11 PATH=$JAVA_HOME11/bin:$NOJAVA_HOME_PATH java'
java17='JAVA_HOME=$JAVA_HOME17 PATH=$JAVA_HOME17/bin:$NOJAVA_HOME_PATH java'
java21='JAVA_HOME=$JAVA_HOME21 PATH=$JAVA_HOME21/bin:$NOJAVA_HOME_PATH java'
java23='JAVA_HOME=$JAVA_HOME23 PATH=$JAVA_HOME23/bin:$NOJAVA_HOME_PATH java'
java25='JAVA_HOME=$JAVA_HOME25 PATH=$JAVA_HOME25/bin:$NOJAVA_HOME_PATH java'
```

