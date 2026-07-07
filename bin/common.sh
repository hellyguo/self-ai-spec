#!/bin/bash

# AI工具启动脚本公共函数库
# 用于 oc, cdbd, clc 等脚本

# 配置变量
AGENT_TEMPLATE_DIR="$HOME/code/markdown/self-ai-spec/agent-template"

# 检查是否需要复制模板文件
# 参数: $1 - 目标文件路径, $2 - 语言参数
check_and_copy_template() {
    local dst_file="$1"
    local language="$2"
    
    if [ -e "$dst_file" ]; then
        echo "exist define, skip"
        return 0
    fi
    
    echo "cp from defined agent md"
    
    if [ -z "$language" ]; then
        echo "need to set program language"
        exit 1
    fi
    
    case "$language" in
        java)
            src_file="AGENTS.java.md"
            ;;
        ansi_c)
            src_file="AGENTS.ansi_c.md"
            ;;
        cpp)
            src_file="AGENTS.cpp.md"
            ;;
        rust)
            src_file="AGENTS.rust.md"
            ;;
        python)
            src_file="AGENTS.python.md"
            ;;
        js)
            src_file="AGENTS.js.md"
            ;;
        blank)
            src_file="AGENTS.blank.md"
            ;;
        *)
            echo "$language not a valid program language, please set another language"
            exit 1
            ;;
    esac
    
    cp "$AGENT_TEMPLATE_DIR/$src_file" "$dst_file"
    return 0
}

# 检查会话ID并恢复会话
# 参数: $1 - ID文件路径, $2 - 恢复命令前缀, $3 - 工具名称
check_and_resume_session() {
    local id_file="$1"
    local resume_cmd_prefix="$2"
    local tool_name="$3"
    
    if [ -e "$id_file" ]; then
        echo "exist prev id, use the id"
        local ID
        ID=$(cat "$id_file")
        
        # 不同的工具使用不同的恢复命令格式
        case "$tool_name" in
            opencode)
                opencode -s "$ID"
                ;;
            codebuddy)
                codebuddy --resume "$ID"
                ;;
            claudecode)
                claude --resume "$ID"
                ;;
            *)
                echo "Unknown tool: $tool_name"
                exit 1
                ;;
        esac
        
        exit 0
    fi
    
    return 1  # 没有会话ID，需要继续执行新会话流程
}

# 启动新会话
# 参数: $1 - 工具命令, $2 - 工具名称
start_new_session() {
    local tool_cmd="$1"
    local tool_name="$2"
    
    echo "start as new $tool_name"
    
    case "$tool_name" in
        opencode)
            opencode
            ;;
        codebuddy)
            codebuddy
            ;;
        claudecode)
            claude
            ;;
        qodercli)
            qodercli
            ;;
        *)
            echo "Unknown tool: $tool_name"
            exit 1
            ;;
    esac
}

# 验证并保存会话ID
# 参数: $1 - 工具名称 (opencode, codebuddy, claudecode)
validate_and_save_session_id() {
    local tool_name="$1"
    local id_file
    local pattern
    local tool_label
    
    # 从剪贴板获取ID
    local id
    id=$(xclip -o 2>/dev/null)
    
    if [ -z "$id" ]; then
        echo "Error: Clipboard is empty or xclip not available"
        return 1
    fi
    
    # 根据工具配置
    case "$tool_name" in
        opencode)
            id_file=".opencode_id"
            pattern="^ses_"
            tool_label="opencode"
            ;;
        codebuddy)
            id_file=".codebuddy_id"
            pattern=".*-.*-.*-.*-.*"
            tool_label="codebuddy"
            ;;
        claudecode)
            id_file=".claudecode_id"
            pattern="^\([a-z0-9]\+\)\(-\([a-z0-9]\+\)\)\{4\}$"
            tool_label="claudecode"
            ;;
        *)
            echo "Error: Unknown tool: $tool_name"
            return 1
            ;;
    esac
    
    # 验证ID格式
    local cnt
    cnt=$(echo "$id" | grep -c "$pattern")
    
    if [ "$cnt" -eq 1 ]; then
        echo "$id" > "$id_file"
        echo "$id, now is the marked $tool_label id"
        return 0
    else
        echo "not valid $tool_label id: $id"
        return 1
    fi
}

# 显示会话ID更新脚本的使用帮助
show_update_id_usage() {
    local script_name="$1"
    local tool_name="$2"
    
    echo "Usage: $script_name"
    echo ""
    echo "更新 $tool_name 会话ID"
    echo ""
    echo "功能:"
    echo "  - 从剪贴板读取会话ID"
    echo "  - 验证ID格式是否正确"
    echo "  - 保存到 .${tool_name}_id 文件"
    echo ""
    echo "使用步骤:"
    echo "  1. 复制 $tool_name 的 Session ID 到剪贴板"
    echo "  2. 运行 $script_name"
    echo ""
    echo "ID格式要求:"
    case "$tool_name" in
        opencode)
            echo "  - 以 'ses_' 开头"
            ;;
        codebuddy)
            echo "  - 包含4个连字符 (5段)"
            ;;
        claudecode)
            echo "  - 5段字母数字用连字符连接"
            ;;
    esac
}

# 显示使用帮助（启动工具）
show_usage() {
    local script_name="$1"
    local tool_name="$2"
    
    echo "Usage: $script_name [language]"
    echo ""
    echo "启动 $tool_name，支持会话恢复和项目模板配置"
    echo ""
    echo "参数:"
    echo "  language  - 项目语言（可选，恢复会话时不需要）"
    echo "             支持的语言: java, ansi_c, cpp, rust, python, js, blank"
    echo ""
    echo "示例:"
    echo "  $script_name java     # 启动新 Java 项目"
    echo "  $script_name          # 恢复上次会话"
    echo ""
    echo "会话管理:"
    echo "  - 首次启动需要语言参数"
    echo "  - 会话ID保存在 .${tool_name}_id 文件中"
    echo "  - 恢复会话无需参数"
}