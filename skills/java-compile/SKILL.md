---
name: java-compile
description: "使用 mvnd/mvn 编译 Java 项目，并依据 java-env 确定 JDK 与构建工具版本。适用于 Java 项目编译、构建验证、编译失败排查。"
---

# Java 编译

## 执行步骤

1. 通过 skill `java-env` 确认 JDK 版本，以及 mvnd/mvn 的路径与版本。
2. 在项目根目录执行编译：
   - 优先使用 `mvnd`（构建速度更快）
   - `mvnd` 不可用时回退 `mvn`
3. 检查退出码与编译输出，确认无编译错误。

## 常用命令

```bash
# 全量编译（跳过测试）
mvnd -q -DskipTests compile

# 编译并运行测试
mvnd -q test

# 打包
mvnd -q -DskipTests package
```

## 验证

- 退出码为 0。
- 目标目录（`target/classes`）生成对应 class 文件。
- 无新增编译告警；如有告警，记录并在交付说明中标注。
