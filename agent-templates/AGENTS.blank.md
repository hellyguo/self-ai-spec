# {project.title placeholder}

## {project.desc placeholder}

## {project.other1 placeholder}

## {project.other2 placeholder}

## {project.other3 placeholder}

## ...

## {project.otherN placeholder}

## AI guide

### 角色定位

{project.role placeholder}

### 工作准则

1. 编码前先读取本文件与语言规范；信息不足时先检索代码库，不臆造接口、配置与依赖。
2. 修改遵循最小范围，不顺手重构，不删除或绕过既有测试。
3. 新增或修改逻辑必须有测试或可复现的验证步骤，并在交付说明中写明验证方式。
4. 禁止用 stdout/stderr 输出调试信息，统一使用日志。
5. 提交遵循约定式提交，仅使用当前 `user.name`，不推送远端。

### 环境变量

`${AI_SPEC_ROOT}` 定义在 bash/zsh 环境变量中，可被读取：`echo ${AI_SPEC_ROOT}`

### 交互规则

必须遵循 `interaction.rules.md` 中描述的规则。

授权读取：${AI_SPEC_ROOT}/rules/interaction.rules.md

### 编码规范

授权读取：${AI_SPEC_ROOT}/lang-spec/spec.{lang}.md
授权读取：${AI_SPEC_ROOT}/lang-spec/review.{lang}.md

### 构建与验证

{project.build placeholder}
