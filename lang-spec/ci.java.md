# Java 构建工具

相关工具路径，见 skill /java-env
首选 mvnd，次选 mvn；下列命令以 `mvnd` 为例，`mvnd` 不可用时替换为 `mvn`。

## 构建/测试命令

```bash
# 编译项目
mvnd compile

# 运行所有测试
mvnd test

# 运行单个测试类
mvnd test -Dtest=XxxTest

# 运行单个测试方法
mvnd test -Dtest=XxxTest#testYyy

# 打包（跳过测试）
mvnd package -DskipTests

# 清理并编译
mvnd clean compile

# 完整构建流程
mvnd clean test package

# 静态分析与覆盖率（按项目已配置的插件执行）
mvnd spotbugs:check
mvnd pmd:check
mvnd jacoco:report
```

## 验证

- 命令退出码为 0。
- 测试报告位于 `target/surefire-reports/`。
- 覆盖率报告位于 `target/site/jacoco/`（如已配置）。

## 签名

---
**Java构建工具说明版本**：1.1.0  
**最后更新**：2026-10-26  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.java.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.java.md  
**关联环境**：${AI_SPEC_ROOT}/skills/java-env/SKILL.md
