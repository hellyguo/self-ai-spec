---
name: java-env
description: "该skill没有执行文件，为信息输入：Java开发需要的环境信息"
---

# 环境配置

## jvm dir:

- 系统查找目录，/usr/lib/jvm ，其下有多个jvm
- 用户查找目录，/home/helly/lang ，其下有多个jvm

## mvnd dir:

/home/helly/app/maven-mvnd

## mvn dir:

/home/helly/app/apache-maven

## spotbug dir:

/home/helly/app/spotbugs-4.7.3

## pmd dir:

/home/helly/app/pmd-bin-6.19.0

## 核心原则

- 基于pom.xml的配置查找jdk合适版本 
- 优先使用mvnd

## java bash profile 设置及别名

```bash
# java
export JAVA_HOME7=$HOME/lang/jdk7
export JAVA_HOME8=$HOME/lang/jdk8
export JAVA_HOME11=$HOME/lang/jdk11
export JAVA_HOME17=$HOME/lang/jdk17
export JAVA_HOME21=$HOME/lang/jdk21
export JAVA_HOME23=$HOME/lang/jdk23
export JAVA_HOME25=$HOME/lang/jdk25
export JAVA_HOME=$JAVA_HOME25
export CLASSPATH=.
export ANT_HOME=$HOME/app/apache-ant
export MAVEN_HOME=$HOME/app/apache-maven
export MVND_HOME=$HOME/app/maven-mvnd
export GRADLE_HOME=$HOME/app/gradle
export GRADLE_USER_HOME=$HOME/.gradle
export GRADLE_SCANS_ACCEPT=no
export BTRACE_HOME=$HOME/app/btrace
export AGENT_HOME=$HOME/java-agent

# alias
alias java7="JAVA_HOME=$JAVA_HOME7 PATH=$JAVA_HOME7/bin:$NOJAVA_PATH java"
alias java8="JAVA_HOME=$JAVA_HOME8 PATH=$JAVA_HOME8/bin:$NOJAVA_PATH java"
alias java11="JAVA_HOME=$JAVA_HOME11 PATH=$JAVA_HOME11/bin:$NOJAVA_PATH java"
alias java17="JAVA_HOME=$JAVA_HOME17 PATH=$JAVA_HOME17/bin:$NOJAVA_PATH java"
alias java21="JAVA_HOME=$JAVA_HOME21 PATH=$JAVA_HOME21/bin:$NOJAVA_PATH java"
alias java23="JAVA_HOME=$JAVA_HOME23 PATH=$JAVA_HOME23/bin:$NOJAVA_PATH java"
alias java25="JAVA_HOME=$JAVA_HOME25 PATH=$JAVA_HOME25/bin:$NOJAVA_PATH java"
alias mvn8="JAVA_HOME=$JAVA_HOME8 PATH=$JAVA_HOME8/bin:$NOJAVA_PATH mvn -T 8"
alias mvnd8="JAVA_HOME=$JAVA_HOME8 PATH=$JAVA_HOME8/bin:$NOJAVA_PATH mvnd"
alias mvn11="JAVA_HOME=$JAVA_HOME11 PATH=$JAVA_HOME11/bin:$NOJAVA_PATH mvn -T 8"
alias mvnd11="JAVA_HOME=$JAVA_HOME11 PATH=$JAVA_HOME11/bin:$NOJAVA_PATH mvnd"
alias mvn17="JAVA_HOME=$JAVA_HOME17 PATH=$JAVA_HOME17/bin:$NOJAVA_PATH mvn -T 8"
alias mvnd17="JAVA_HOME=$JAVA_HOME17 PATH=$JAVA_HOME17/bin:$NOJAVA_PATH mvnd"
alias mvn21="JAVA_HOME=$JAVA_HOME21 PATH=$JAVA_HOME21/bin:$NOJAVA_PATH mvn -T 8"
alias mvnd21="JAVA_HOME=$JAVA_HOME21 PATH=$JAVA_HOME21/bin:$NOJAVA_PATH mvnd"
alias mvn23="JAVA_HOME=$JAVA_HOME23 PATH=$JAVA_HOME23/bin:$NOJAVA_PATH mvn -T 8"
alias mvnd23="JAVA_HOME=$JAVA_HOME23 PATH=$JAVA_HOME23/bin:$NOJAVA_PATH mvnd"
alias mvn25="JAVA_HOME=$JAVA_HOME25 PATH=$JAVA_HOME25/bin:$NOJAVA_PATH mvn -T 8"
alias mvnd25="JAVA_HOME=$JAVA_HOME25 PATH=$JAVA_HOME25/bin:$NOJAVA_PATH mvnd"
alias gradle8="JAVA_HOME=$JAVA_HOME8 PATH=$JAVA_HOME8/bin:$NOJAVA_PATH gradle"
alias gradle11="JAVA_HOME=$JAVA_HOME11 PATH=$JAVA_HOME11/bin:$NOJAVA_PATH gradle"
alias gradle17="JAVA_HOME=$JAVA_HOME17 PATH=$JAVA_HOME17/bin:$NOJAVA_PATH gradle"
alias gradle21="JAVA_HOME=$JAVA_HOME21 PATH=$JAVA_HOME21/bin:$NOJAVA_PATH gradle"
alias gradle23="JAVA_HOME=$JAVA_HOME23 PATH=$JAVA_HOME23/bin:$NOJAVA_PATH gradle"
alias gradle25="JAVA_HOME=$JAVA_HOME25 PATH=$JAVA_HOME25/bin:$NOJAVA_PATH gradle"
```

