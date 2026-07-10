---
name: shell-check
description: "ShellCheck静态分析技能：使用ShellCheck进行Shell脚本代码质量分析，检测语法错误、潜在缺陷、代码风格问题"
---

# ShellCheck Shell脚本静态分析技能

## 概述

ShellCheck是Shell脚本静态分析工具，可检测脚本中的：

- **语法错误**：无效语法、未闭合引号
- **潜在缺陷**：未引用变量、错误的条件判断
- **代码风格**：可读性问题、不符合最佳实践
- **兼容性**：不同Shell方言的兼容性问题

## 工具位置

```bash
SHELLCHECK=/usr/bin/shellcheck
# 版本: ShellCheck 0.10.0
```

## 执行流程

### 步骤1：确定脚本文件

```bash
SCRIPT_FILE=script.sh  # 单个文件
SCRIPT_DIR=scripts/    # 目录下的所有脚本
```

### 步骤2：执行分析

```bash
# 基础检查
$SHELLCHECK script.sh

# 检查多个文件
$SHELLCHECK script1.sh script2.sh script3.sh

# 检查目录下所有脚本
$SHELLCHECK scripts/*.sh

# 指定Shell方言
$SHELLCHECK --shell=bash script.sh
$SHELLCHECK --shell=sh script.sh
$SHELLCHECK --shell=dash script.sh
$SHELLCHECK --shell=ksh script.sh
```

### 步骤3：指定输出格式

```bash
# 终端格式（默认）
$SHELLCHECK script.sh

# GCC格式
$SHELLCHECK --format=gcc script.sh

# JSON格式
$SHELLCHECK --format=json script.sh > shellcheck.json

# JSON1格式（更详细）
$SHELLCHECK --format=json1 script.sh > shellcheck.json

# Checkstyle格式（CI集成）
$SHELLCHECK --format=checkstyle script.sh > shellcheck.xml

# Quiet格式（只显示错误）
$SHELLCHECK --format=quiet script.sh
```

## 常用参数

| 参数                    | 描述                 | 示例                              |
|-------------------------|----------------------|-----------------------------------|
| `-s, --shell`           | 指定Shell方言        | `--shell=bash`                    |
| `-S, --severity`        | 最小严重级别         | `--severity=error`                |
| `-e, --exclude`         | 排除特定警告         | `-e SC2086,SC2034`                |
| `-i, --include`         | 只包含特定警告       | `-i SC2086,SC2034`                |
| `-a, --check-sourced`   | 检查source的文件     | `--check-sourced`                 |
| `-x, --external-sources`| 允许外部source       | `--external-sources`              |
| `-P, --source-path`     | source搜索路径       | `--source-path=SCRIPTDIR`         |
| `-o, --enable`          | 启用可选检查         | `--enable=all`                    |
| `-f, --format`          | 输出格式             | `--format=json`                   |
| `--norc`                | 不读取配置文件       | `--norc`                          |
| `--rcfile`              | 指定配置文件         | `--rcfile=.shellcheckrc`          |
| `-C, --color`           | 颜色输出             | `--color=always`                  |
| `-W`                    | Wiki链接数量         | `-W 3`                            |

## 严重级别

| 级别      | 描述           |
|-----------|----------------|
| `error`   | 错误，必须修复 |
| `warning` | 警告，建议修复 |
| `info`    | 信息，可选修复 |
| `style`   | 风格，可选修复 |

## 常见检查项

### 1. 变量引用（SC2086）

```bash
# 错误：变量未引用
echo $var
ls $dir

# 正确：变量已引用
echo "$var"
ls "$dir"
```

### 2. 条件判断（SC2164）

```bash
# 错误：cd失败可能导致后续命令在错误目录执行
cd /some/path
rm -rf *

# 正确：检查cd是否成功
cd /some/path || exit 1
rm -rf *
```

### 3. 命令替换（SC2006）

```bash
# 旧语法
var=`date`

# 推荐语法
var=$(date)
```

### 4. 条件测试（SC2166）

```bash
# 错误：&& 应该在 [] 外面
[ $a -gt 1 && $a -lt 10 ]

# 正确：使用 -a 或 [[ ]]
[ $a -gt 1 ] && [ $a -lt 10 ]
[[ $a -gt 1 && $a -lt 10 ]]
```

### 5. 循环读取（SC2013）

```bash
# 错误：for循环处理文件名可能出错
for f in $(cat files.txt); do
    echo "$f"
done

# 正确：使用while read
while IFS= read -r f; do
    echo "$f"
done < files.txt
```

### 6. 函数定义（SC2034）

```bash
# 错误：函数名与内置命令冲突
function cd() {
    echo "changing dir"
}

# 正确：使用不同名称
function mycd() {
    echo "changing dir"
}
```

## 排除警告

### 行内排除

```bash
# 排除单个警告
var="hello world" # shellcheck disable=SC2086
echo $var

# 排除多个警告
# shellcheck disable=SC2086,SC2034
echo $var

# 排除下一行
# shellcheck disable-next=SC2086
echo $var

# 对整个文件禁用
# shellcheck disable=SC2086
```

### 命令行排除

```bash
# 排除特定警告
$SHELLCHECK -e SC2086,SC2034 script.sh

# 只检查特定警告
$SHELLCHECK -i SC2086 script.sh
```

### 配置文件（.shellcheckrc）

```text
# 排除特定警告
disable=SC2086
disable=SC2034

# 指定Shell方言
shell=bash

# 外部source路径
source-path=SCRIPTDIR

# 启用可选检查
enable=require-variable-braces
```

## 可选检查

```bash
# 列出所有可选检查
$SHELLCHECK --list-optional

# 启用所有可选检查
$SHELLCHECK --enable=all script.sh

# 启用特定检查
$SHELLCHECK --enable=require-variable-braces,add-default-case script.sh
```

### 常用可选检查

| 检查项                     | 描述                 |
|----------------------------|----------------------|
| `require-variable-braces`  | 要求变量使用大括号   |
| `add-default-case`         | case语句需要默认分支 |
| `avoid-nullary-conditions` | 避免空条件测试       |
| `quote-safe-variables`     | 引用安全的变量       |
| `useless-use-of-cat`       | 检测无用的cat使用    |

## 与构建系统集成

### Makefile集成

```makefile
SHELLCHECK=/usr/bin/shellcheck

shellcheck:
 $(SHELLCHECK) --shell=bash scripts/*.sh
```

### CI集成（GitHub Actions）

```yaml
name: ShellCheck
on: [push, pull_request]
jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run ShellCheck
        run: shellcheck --shell=bash scripts/*.sh
```

### pre-commit集成

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.10.0
    hooks:
      - id: shellcheck
        args: ["--shell=bash"]
```

## 分析结果处理

### 统计问题类型

```bash
$SHELLCHECK --format=json script.sh | jq -r '.[].code' | sort | uniq -c | sort -nr
```

### 提取高危问题

```bash
$SHELLCHECK --format=json script.sh | jq -r '.[] | select(.level == "error")'
```

### 生成摘要报告

```bash
#!/bin/bash
echo "=== ShellCheck分析报告 ==="
echo "分析时间: $(date)"
echo "---"
echo "总问题数: $($SHELLCHECK --format=json script.sh | jq 'length')"
echo "错误: $($SHELLCHECK --format=json script.sh | jq '[.[] | select(.level == "error")] | length')"
echo "警告: $($SHELLCHECK --format=json script.sh | jq '[.[] | select(.level == "warning")] | length')"
```

## 典型使用场景

### 场景1：快速检查

```bash
# 只显示错误级别
$SHELLCHECK --severity=error script.sh
```

### 场景2：完整检查

```bash
# 启用所有检查
$SHELLCHECK --enable=all --severity=style script.sh
```

### 场景3：CI集成

```bash
# 输出GCC格式便于CI解析
$SHELLCHECK --format=gcc --severity=warning scripts/*.sh
```

### 场景4：检查sourced文件

```bash
# 递归检查source引入的文件
$SHELLCHECK --check-sourced --source-path=scripts script.sh
```

## 最佳实践

1. **变量引用**：始终用双引号引用变量
2. **使用`[[ ]]`**：优先使用`[[ ]]`而非`[ ]`
3. **使用`$( )`**：优先使用`$( )`而非反引号
4. **检查返回值**：检查cd等命令的返回值
5. **使用`set -e`**：脚本开头设置错误退出

---
**技能版本**: 1.0.0
**工具版本**: ShellCheck 0.10.0
**适用项目**: Shell脚本（bash/sh/dash/ksh）
**输出位置**: 标准输出或指定文件
