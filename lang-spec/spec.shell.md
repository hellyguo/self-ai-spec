# Shell 编码规范

## 通用规则

1. 对脚本文件有总体注释，对重点代码有详尽注释
2. 使用行尾注释说明复杂逻辑
3. 环境变量名使用大写，局部变量使用小写
4. 函数应遵循单一职责原则，大函数应拆分为多个职责明确的小函数
5. 优先使用函数组合而非全局状态
6. 主脚本代码不得包含测试代码，测试代码应分离

## 代码结构规范

### 文件大小限制

- 单脚本文件源码行数建议不超过 500 行
- 过大脚本必须按功能拆分为多个小脚本
- 脚本应遵循模块化设计，易于维护和测试

### 函数大小限制

- 函数行数不应超过 50 行
- 超过此大小的函数逻辑过于复杂，影响可读性
- 函数过长时应拆分为多个小函数

### 缩进深度限制

- 最大缩进不超过 4 层
- 超过 4 层缩进表明逻辑过于复杂，应重构
- 使用函数封装、早返回等方式减少嵌套

### 依赖深度限制

- 脚本间依赖不应超过 3 层
- 最大不超过 5，过深依赖导致难以调试和维护
- 优先使用函数库模式，避免深层脚本调用

### 错误处理规范

- 必须使用 `set -e` 或 `set -o errexit` 确保脚本在错误时立即退出
- 必须使用 `set -u` 或 `set -o nounset` 确保使用未定义变量时报错
- 必须使用 `set -o pipefail` 确保管道中任一命令失败则整个管道失败

```bash
#!/bin/bash
set -euo pipefail  # 强烈推荐：严格的错误处理模式
```

## Shebang 规范

### 选择合适的解释器

```bash
#!/bin/bash        # Bash 4+ 脚本
#!/usr/bin/env bash # 便携式 Bash 脚本
#!/bin/sh         # POSIX Shell 脚本（确保兼容性）
#!/usr/bin/env sh  # 便携式 POSIX Shell 脚本
```

### Shebang 最佳实践

1. 简单脚本使用 `/bin/sh` 确保最大兼容性
2. 复杂脚本使用 `/bin/bash` 或 `/usr/bin/env bash`
3. 避免使用 `/usr/bin/env` 与参数结合（如 `#!/usr/bin/env bash -e`），某些系统不支持

## 变量管理规范

### 命名约定

```bash
# 环境变量：大写+下划线
export DATABASE_HOST="localhost"
export MAX_RETRY_COUNT=3

# 局部变量：小写+下划线
local file_path="/var/log/app.log"
local user_count=100

# 只读变量：大写
readonly CONFIG_FILE="/etc/app.conf"

# 数组变量：复数形式
declare -a files=("file1.txt" "file2.txt")
declare -A config_map=([host]="localhost" [port]="8080")
```

### 变量作用域

```bash
# 函数内部变量：使用 local 关键字
function process_file() {
    local filename="$1"
    local temp_dir="/tmp/$(basename "$filename")"
    # ... 函数逻辑
}

# 全局变量：谨慎使用，明确声明
readonly GLOBAL_CONFIG="/etc/global.conf"
export APP_VERSION="1.0.0"
```

### 变量引用

```bash
# 正确：双引号保护变量扩展
echo "File: $filename"
echo "Count: ${#array[@]}"

# 正确：大括号明确变量边界
echo "${filename}_backup.txt"

# 错误：未保护的变量
echo $filename  # 如果 filename 包含空格会出错
```

## 函数设计规范

### 函数定义模式

```bash
# 推荐：使用关键字 function（Bash 特有，更清晰）
function log_message() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >&2
}

# 或使用 POSIX 兼容语法
log_info() {
    echo "INFO: $*" >&2
}
```

### 函数参数处理

```bash
# 使用命名参数增强可读性
function connect_to_database() {
    local host="${1:-localhost}"
    local port="${2:-3306}"
    local username="${3:-root}"
    local password="${4:-}"
    
    # 参数验证
    if [[ -z "$password" ]]; then
        echo "Error: Password is required" >&2
        return 1
    fi
    
    # ... 函数逻辑
    return 0
}
```

### 函数返回值

```bash
# 使用 return 返回状态码（0=成功，非0=失败）
function validate_input() {
    local input="$1"
    
    if [[ -z "$input" ]]; then
        echo "Error: Input cannot be empty" >&2
        return 1
    fi
    
    if [[ ! "$input" =~ ^[a-zA-Z0-9_]+$ ]]; then
        echo "Error: Invalid input format" >&2
        return 2
    fi
    
    return 0
}

# 使用 echo 返回数据（通过标准输出）
function get_timestamp() {
    date '+%Y%m%d_%H%M%S'
}

# 调用方式
timestamp=$(get_timestamp)
if validate_input "$username"; then
    echo "Input is valid"
fi
```

## 错误处理与日志规范

### 错误处理模式

```bash
# 使用 trap 处理信号和错误
trap 'cleanup_on_exit' EXIT
trap 'handle_interrupt' INT TERM

function cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script failed with exit code: $exit_code"
    fi
    # 清理临时文件等资源
    rm -rf "$TEMP_DIR"
}

function handle_interrupt() {
    log_warn "Script interrupted by signal"
    exit 1
}
```

### 日志函数模板

```bash
# 日志级别定义
readonly LOG_LEVEL_DEBUG=10
readonly LOG_LEVEL_INFO=20
readonly LOG_LEVEL_WARN=30
readonly LOG_LEVEL_ERROR=40

# 当前日志级别
LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_INFO}

# 日志函数
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        DEBUG) [[ $LOG_LEVEL -le $LOG_LEVEL_DEBUG ]] && echo "[$timestamp] [DEBUG] $message" >&2 ;;
        INFO)  [[ $LOG_LEVEL -le $LOG_LEVEL_INFO ]]  && echo "[$timestamp] [INFO]  $message" >&2 ;;
        WARN)  [[ $LOG_LEVEL -le $LOG_LEVEL_WARN ]]  && echo "[$timestamp] [WARN]  $message" >&2 ;;
        ERROR) [[ $LOG_LEVEL -le $LOG_LEVEL_ERROR ]] && echo "[$timestamp] [ERROR] $message" >&2 ;;
    esac
}

# 快捷函数
log_debug() { log DEBUG "$@"; }
log_info()  { log INFO "$@"; }
log_warn()  { log WARN "$@"; }
log_error() { log ERROR "$@"; }
```

### 命令执行检查

```bash
# 检查命令是否存在
if ! command -v jq >/dev/null 2>&1; then
    log_error "jq command is required but not installed"
    exit 1
fi

# 安全执行命令并检查结果
if ! database_backup; then
    log_error "Database backup failed"
    exit 1
fi

# 捕获命令输出和错误
output=$(some_command 2>&1)
exit_code=$?
if [[ $exit_code -ne 0 ]]; then
    log_error "Command failed: $output"
    exit $exit_code
fi
```

## 文本处理规范

### 字符串操作

```bash
# 字符串长度
length=${#string}

# 子字符串提取
substring=${string:start:length}

# 字符串替换
new_string=${string/pattern/replacement}    # 第一个匹配
new_string=${string//pattern/replacement}   # 所有匹配

# 前缀/后缀匹配
if [[ "$filename" == *.txt ]]; then
    echo "Text file"
fi

if [[ "$var" == prefix* ]]; then
    echo "Starts with prefix"
fi
```

### 正则表达式

```bash
# Bash 4+ 正则表达式匹配
if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo "Valid email"
fi

# 提取匹配组
if [[ "$date" =~ ([0-9]{4})-([0-9]{2})-([0-9]{2}) ]]; then
    year="${BASH_REMATCH[1]}"
    month="${BASH_REMATCH[2]}"
    day="${BASH_REMATCH[3]}"
fi
```

### 数组操作

```bash
# 数组定义
declare -a fruits=("apple" "banana" "cherry")
declare -A user_info=([name]="john" [age]=30 [city]="NYC")

# 数组遍历
for fruit in "${fruits[@]}"; do
    echo "Fruit: $fruit"
done

# 关联数组遍历
for key in "${!user_info[@]}"; do
    echo "$key: ${user_info[$key]}"
done

# 数组长度
fruit_count=${#fruits[@]}
```

## 文件操作规范

### 文件检查

```bash
# 检查文件存在性
if [[ -f "$file_path" ]]; then
    echo "File exists"
fi

# 检查目录存在性
if [[ -d "$dir_path" ]]; then
    echo "Directory exists"
fi

# 检查文件可读性
if [[ -r "$file_path" ]]; then
    echo "File is readable"
fi

# 检查文件可执行性
if [[ -x "$file_path" ]]; then
    echo "File is executable"
fi
```

### 安全文件操作

```bash
# 使用临时文件
temp_file=$(mktemp)
trap 'rm -f "$temp_file"' EXIT

# 安全文件写入
cat > "$temp_file" <<EOF
config_value=123
another_value=abc
EOF

# 原子文件移动（避免部分写入）
mv "$temp_file" "$config_file"
```

### 文件读取

```bash
# 逐行读取文件
while IFS= read -r line; do
    # 处理每一行
    process_line "$line"
done < "$input_file"

# 读取文件到数组
mapfile -t lines < "$input_file"
for line in "${lines[@]}"; do
    echo "Line: $line"
done
```

## 进程管理规范

### 后台进程管理

```bash
# 启动后台进程并获取PID
some_command &
pid=$!

# 等待进程完成（带超时）
timeout=60
if wait $pid 2>/dev/null; then
    echo "Process completed successfully"
else
    exit_code=$?
    if [[ $exit_code -eq 143 ]]; then  # SIGTERM (timeout)
        echo "Process timeout, killing..."
        kill -9 $pid 2>/dev/null || true
    fi
    echo "Process failed with code: $exit_code"
fi
```

### 进程信号处理

```bash
# 优雅关闭处理
function graceful_shutdown() {
    log_info "Received shutdown signal, cleaning up..."
    # 停止后台进程
    kill -TERM "$child_pid" 2>/dev/null || true
    # 等待进程结束
    wait "$child_pid" 2>/dev/null
    log_info "Shutdown complete"
    exit 0
}

trap graceful_shutdown TERM INT
```

### 并发控制

```bash
# 使用 GNU Parallel 或 xargs 进行并行处理
find . -name "*.log" -type f | xargs -P 4 -I {} process_log "{}"

# 或使用背景进程+等待
declare -a pids=()
for file in *.log; do
    process_log "$file" &
    pids+=($!)
done

# 等待所有后台进程
for pid in "${pids[@]}"; do
    wait "$pid"
done
```

## 安全规范

### 输入验证

```bash
# 验证用户输入
function validate_username() {
    local username="$1"
    
    # 非空检查
    if [[ -z "$username" ]]; then
        log_error "Username cannot be empty"
        return 1
    fi
    
    # 长度检查
    if [[ ${#username} -lt 3 || ${#username} -gt 20 ]]; then
        log_error "Username must be 3-20 characters"
        return 1
    fi
    
    # 字符集检查
    if [[ ! "$username" =~ ^[a-zA-Z0-9_]+$ ]]; then
        log_error "Username can only contain letters, numbers, and underscores"
        return 1
    fi
    
    return 0
}
```

### 路径安全

```bash
# 规范化路径，防止目录遍历攻击
function safe_path() {
    local path="$1"
    local base_dir="$2"
    
    # 解析绝对路径
    local absolute_path
    absolute_path=$(realpath -m "$base_dir/$path" 2>/dev/null || echo "")
    
    # 检查是否在基目录内
    if [[ "$absolute_path" == "$base_dir"* ]]; then
        echo "$absolute_path"
        return 0
    else
        log_error "Path traversal attempt detected: $path"
        return 1
    fi
}
```

### 命令注入防护

```bash
# 错误：直接拼接用户输入
# rm -rf "/tmp/$user_input"  # ❌ 危险！

# 正确：使用参数传递
safe_remove() {
    local file="$1"
    
    # 验证文件路径
    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi
    
    # 安全删除
    rm -f -- "$file"
}

# 或使用数组传递参数
cmd_args=("rm" "-rf")
if [[ -n "$user_input" ]]; then
    cmd_args+=("$user_input")
fi
"${cmd_args[@]}"
```

## 性能优化规范

### 避免频繁子进程

```bash
# 错误：在循环中频繁调用外部命令
for i in {1..1000}; do
    date +%s  # 每次循环都创建新进程
done

# 正确：一次性处理或使用内置命令
start_time=$(date +%s)
for i in {1..1000}; do
    # 使用内置算术
    (( i * 2 ))
done
```

### 使用内置命令

```bash
# 内置字符串操作 vs 外部命令
# 错误：使用 cut
first_field=$(echo "$line" | cut -d',' -f1)

# 正确：使用参数扩展
first_field="${line%%,*}"
first_field="${line%% *}"  # 按空格分割

# 内置算术 vs 外部计算
# 错误：使用 expr
result=$(expr "$a" + "$b")

# 正确：使用 $(( ))
result=$(( a + b ))
```

### 减少管道使用

```bash
# 错误：过多管道
count=$(ps aux | grep process | grep -v grep | wc -l)

# 正确：使用 pgrep 或更高效的命令
count=$(pgrep -c process)

# 或使用数组
mapfile -t processes < <(ps aux | grep process)
count=${#processes[@]}
```

## 可移植性规范

### POSIX 兼容性

```bash
# 使用 POSIX 兼容语法
#!/bin/sh

# POSIX 函数定义（不使用 function 关键字）
my_function() {
    echo "POSIX function"
}

# POSIX 字符串替换（不使用 ${var//pattern/replacement}）
result=$(echo "$string" | sed 's/pattern/replacement/g')

# POSIX 算术
result=$(( a + b * c ))
```

### 平台差异处理

```bash
# 检测操作系统
case "$(uname -s)" in
    Linux*)     os="Linux" ;;
    Darwin*)    os="macOS" ;;
    CYGWIN*)    os="Cygwin" ;;
    MINGW*)     os="MinGW" ;;
    *)          os="Unknown" ;;
esac

# 平台特定命令
if [[ "$os" == "Linux" ]]; then
    sed_cmd="sed -i"
elif [[ "$os" == "macOS" ]]; then
    sed_cmd="sed -i ''"
else
    log_error "Unsupported OS: $os"
    exit 1
fi
```

### 路径差异处理

```bash
# 使用 /usr/bin/env 增强可移植性
#!/usr/bin/env bash

# 检测命令路径
if command -v python3 >/dev/null 2>&1; then
    python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
    python_cmd="python"
else
    log_error "Python not found"
    exit 1
fi
```

## 测试与调试规范

### 单元测试框架

```bash
#!/bin/bash
# test_math.sh

set -eu

# 测试函数
function test_addition() {
    result=$(( 2 + 2 ))
    if [[ $result -ne 4 ]]; then
        echo "FAIL: 2 + 2 should be 4, got $result"
        return 1
    fi
    echo "PASS: addition"
}

function test_subtraction() {
    result=$(( 5 - 3 ))
    if [[ $result -ne 2 ]]; then
        echo "FAIL: 5 - 3 should be 2, got $result"
        return 1
    fi
    echo "PASS: subtraction"
}

# 运行所有测试
function run_tests() {
    local tests=("test_addition" "test_subtraction")
    local failures=0
    
    for test_func in "${tests[@]}"; do
        if $test_func; then
            : # 测试通过
        else
            (( failures++ ))
        fi
    done
    
    if [[ $failures -eq 0 ]]; then
        echo "All tests passed!"
        return 0
    else
        echo "$failures test(s) failed"
        return 1
    fi
}

# 主程序
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_tests
fi
```

### 调试技巧

```bash
# 启用调试模式
set -x  # 打印执行的命令
set -v  # 打印读取的输入行

# 在特定部分启用调试
function debug_function() {
    set -x
    # 调试代码
    set +x
}

# 使用 trap 调试
trap 'echo "Line $LINENO: $BASH_COMMAND"' DEBUG
```

## 签名

---
**Shell编码规范版本**：1.2.0  
**最后更新**：2025-01-01  
**规则文件**：${AI_SPEC_ROOT}/lang-spec/spec.shell.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.shell.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Shell脚本、运维自动化、CI/CD脚本

