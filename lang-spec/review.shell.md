# Shell 代码审查规则
## ShellCheck 规则参考

以下规则来自 ShellCheck 静态分析工具，用于代码审查时识别常见问题。

### 正确性问题

| 规则ID | 描述 |
| -------- | ------ |
| SC1007 | 删除字面 CR，使用 "$var" |
| SC2001 | 使用 ${var//find/replace} 替代 sed |
| SC2004 | $/${} 在算术上下文外不必要 |
| SC2006 | 使用 $(..) 替代反引号 |
| SC2015 | 注意命令替换中的换行符 |
| SC2016 | 单引号中的表达式不展开 |
| SC2028 | echo 可能不支持 -e |
| SC2034 | 未使用的变量 |
| SC2046 | 引号防止单词拆分 |
| SC2086 | 双引号防止单词拆分 |
| SC2094 | 确保参数传递给命令 |
| SC2162 | read -p 不带 -r 会删除反斜杠 |
| SC2166 | 防止 cd 失败 |

### 安全性问题

| 规则ID | 描述 |
| -------- | ------ |
| SC2035 | 使用 ./*glob* 或 -- *glob* 避免隐藏文件被误解析 |
| SC2038 | 使用 find -print0 \| xargs -0 |
| SC2048 | 使用 "$@" 替代 $* |
| SC2059 | 不要在 printf 格式字符串中使用变量 |
| SC2068 | 使用数组正确传递参数 |
| SC2087 | 引号防止 glob 扩展 |
| SC2145 | 参数拼接到数组中 |
| SC2155 | 声明和赋值分开进行 |
| SC2164 | 使用 cd ... \| \| exit |
| SC2181 | 检查直接退出状态，而非 $? |

### 可移植性问题

| 规则ID | 描述 |
| -------- | ------ |
| SC1001 | \`\\\`\` 不是 POSIX |
| SC1019 | 此 shebang 是非标准的 |
| SC1117 | 反斜杠转义在 shebang 中无效 |
| SC2002 | 使用 UUOC（useless use of cat） |
| SC2003 | 使用 $(command) 替代 \`command\` |
| SC2009 | 使用 pgrep -f 替代 ps \| grep |
| SC2010 | 不要将 ls 输出用于任何事情 |
| SC2012 | 使用 cd \| 避免子shell |
| SC2013 | 使用 read -r 替代循环 |
| SC2016 | 使用 $'..' 替代 echo -e |
| SC2018 | 使用 sed 's/..//' 替代 sed 's/..//g' |
| SC2019 | 使用 awk 替代 sed 处理列 |
| SC2020 | tr 可能不支持字符类 |
| SC2021 | printf %q 替代 echo -e |

### 性能问题

| 规则ID | 描述 |
| -------- | ------ |
| SC2045 | 在 for 循环中迭代 ls 输出 |
| SC2090 | 使用 while read 处理 find 输出 |
| SC2126 | 考虑使用 grep -c 替代 grep \| wc -l |
| SC2129 | 考虑使用 awk 替代多个 grep |

### 代码风格

| 规则ID | 描述 |
| -------- | ------ |
| SC1000 | $/${} 在正则表达式外不必要 |
| SC1017 | 可读的十六进制数字 |
| SC1072 | 意外的 shebang 行 |
| SC1073 | 可读的 shebang 错误消息 |
| SC1090 | 无法找到源文件 |
| SC1091 | 无法找到源文件 |
| SC1113 | 使用 # 作为注释 |
| SC2005 | 使用 Useless echo？ |
| SC2008 | 使用 $() 替代反引号 |
| SC2011 | 使用 while read 替代 for 循环 |
| SC2014 | 使用 mkdir -p 创建目录 |
| SC2017 | 使用 sed -n 替代 head/tail |
| SC2030 | 使用 set -o pipefail |
| SC2031 | 使用 set -u |
| SC2039 | 在 POSIX sh 中，echo 中的 -n 未定义 |

### 最佳实践集成

```bash
#!/bin/bash
# .shellcheckrc 配置示例
# 启用所有检查
enable=all

# 排除特定检查
exclude=SC1090,SC1091  # 排除源文件找不到警告

# 自定义严重级别
severity=style    # 默认严重级别

# 脚本头部推荐配置
#!/bin/bash
set -euo pipefail  # 严格模式
IFS=$'\n\t'       # 改进的字段分隔符
```

### CI 集成

```bash
# GitHub Actions 示例
name: ShellCheck
on: [push, pull_request]
jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run ShellCheck
      uses: ludeeus/action-shellcheck@1.1.0
      with:
        scandir: 'scripts/'
        severity: error
        exclude: SC1090,SC1091
```

## 签名

---
**Shell代码审查规则版本**：1.2.0  
**最后更新**：2025-01-01  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.shell.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.shell.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Shell脚本、运维自动化、CI/CD脚本
