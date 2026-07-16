# 执行脚本模板

## 脚本内容

```bash
#!/bin/bash
# 增量测试一键执行脚本
# 生成日期: YYYY-MM-DD
# 基线: git diff HEAD~N
# Java版本要求: {项目要求的JDK版本}
# ============================================

# [1] 环境检查
# - 检查 JAVA_HOME 是否指向正确版本
# - 检查 Maven 是否可用

# [2] 备份原 pom.xml（按模块逐个执行）
# cp pom.xml pom-backup.xml
# cp src/test/resources/pom-test.xml pom.xml

# [3] 执行测试 + 生成覆盖率
# mvn clean test
# mvn jacoco:report

# [4] 恢复原 pom.xml
# cp pom-backup.xml pom.xml && rm pom-backup.xml

# [5] 测试结果汇总
# 输出每个模块的: Tests run / Failures / Errors / Skipped

# [6] 报告路径提示
# 单元测试报告: report/YYYY-MM-DD_增量单元测试报告.html
# 覆盖率报告: report/YYYY-MM-DD_增量覆盖率报告.html
# JaCoCo原始报告: {模块}/target/site/jacoco/index.html
```

## 脚本特性

- 支持传入参数指定模块名（只测试指定模块）或 `all`（测试全部）
- 支持失败继续（一个模块失败不影响其他模块）
- 最终返回非零退出码（如果有任何测试失败）
- 自动备份和恢复 pom.xml
- **采用并行构建优化**：分析模块依赖图后，无依赖关系的模块并行执行
- **支持增量构建模式**：`--incremental` 参数跳过 `clean`，仅重编译变更的测试文件
