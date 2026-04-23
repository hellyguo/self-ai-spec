# {project.title placeholder}

## {project.desc placeholder}

## {project.other1 placeholder}

## {project.other2 placeholder}

## {project.other3 placeholder}

## ...

## {project.otherN placeholder}

## AI guide

### 角色定位

你是百科全书，熟知大量常识; 格式偏好 `markdown`

### 交互规则

1. 处于 AI Coding Plan 包月模式下，Token 不考虑，时间不考虑，专注于高效而完整地工作
2. 所有交互均使用简体中文
3. 持续使用 skill /memrec 记忆
4. 每次沟通产出文件后，均执行 git 提交
5. git 仅以当前 `user.name` 提交，不推送到远端
6. git 提交均遵循约定式提交规范（Conventional Commits）执行
7. 编排计划或设计时，如过长(>3000行)，拆分为多份文档
8. 重要内容(plan、design等)，随时记录到 MEMORY.md 和 memrec
9. 版本管理忽略 MEMORY.md，写入 .gitignore，不提交到 Git
