---
name: shell-check
description: "ShellCheck静态分析技能：使用ShellCheck进行Shell脚本代码质量分析，检测语法错误、潜在缺陷、代码风格问题"
---

# ShellCheck Shell脚本静态分析技能

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
$SHELLCHECK --format=json script.sh > shellcheck.json
$SHELLCHECK --format=json1 script.sh > shellcheck-detail.json
$SHELLCHECK --format=checkstyle script.sh > shellcheck.xml
$SHELLCHECK --format=gcc script.sh
$SHELLCHECK --format=quiet script.sh
```

### 步骤4：生成报告

使用模板 `templates/report.md` 输出分析报告。

## 常用参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `-s, --shell` | 指定Shell方言 | `--shell=bash` |
| `-S, --severity` | 最小严重级别 | `--severity=error` |
| `-e, --exclude` | 排除特定警告 | `-e SC2086,SC2034` |
| `-i, --include` | 只包含特定警告 | `-i SC2086,SC2034` |
| `-a, --check-sourced` | 检查source的文件 | `--check-sourced` |
| `-x, --external-sources` | 允许外部source | `--external-sources` |
| `-o, --enable` | 启用可选检查 | `--enable=all` |
| `-f, --format` | 输出格式 | `--format=json` |

## 严重级别

| 级别 | 描述 |
|------|------|
| `error` | 错误，必须修复 |
| `warning` | 警告，建议修复 |
| `info` | 信息，可选修复 |
| `style` | 风格，可选修复 |

## 排除警告

### 行内排除

```bash
# shellcheck disable=SC2086
echo $var

# shellcheck disable=SC2086,SC2034
echo $var

# shellcheck disable-next=SC2086
echo $var
```

### 命令行排除

```bash
$SHELLCHECK -e SC2086,SC2034 script.sh
$SHELLCHECK -i SC2086 script.sh
```

### 配置文件（.shellcheckrc）

```text
disable=SC2086
shell=bash
source-path=SCRIPTDIR
enable=require-variable-braces
```

## 常用可选检查

| 检查项 | 描述 |
|--------|------|
| `require-variable-braces` | 要求变量使用大括号 |
| `add-default-case` | case语句需要默认分支 |
| `quote-safe-variables` | 引用安全的变量 |
| `useless-use-of-cat` | 检测无用的cat使用 |

## 典型使用场景

| 场景 | 命令 |
|------|------|
| 快速检查 | `$SHELLCHECK --severity=error script.sh` |
| 完整检查 | `$SHELLCHECK --enable=all --severity=style script.sh` |
| CI集成 | `$SHELLCHECK --format=gcc --severity=warning scripts/*.sh` |
| 检查sourced文件 | `$SHELLCHECK --check-sourced --source-path=scripts script.sh` |

## 最佳实践

1. 始终用双引号引用变量
2. 优先使用`[[ ]]`而非`[ ]`
3. 优先使用`$( )`而非反引号
4. 检查cd等命令的返回值
5. 脚本开头设置`set -e`

---
**技能版本**: 1.0.0
**工具版本**: ShellCheck 0.10.0
**适用项目**: Shell脚本（bash/sh/dash/ksh）
