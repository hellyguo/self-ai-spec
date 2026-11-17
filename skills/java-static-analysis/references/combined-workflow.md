# 双引擎串联工作流（PMD + SpotBugs）

用于提交前体检或 CI 全量门禁，需要同时覆盖源码规范与字节码缺陷。目标是一份去重、分级的报告，而不是两份工具输出。

## 前置条件

- 源码可读，且能完成一次成功编译（`mvn -q compile` 或等价命令）。
- PMD 与 SpotBugs 的路径按各自 references 页确认可用。
- 归并需要一个稳定的定位键：`文件相对路径:行号` + 规则族。

## 执行步骤

### 步骤1：PMD 先跑（快，覆盖广）

```bash
$PMD_CLI pmd -d src/main/java -R rulesets/java/basic.xml,rulesets/java/design.xml,rulesets/java/security.xml -f xml -r pmd-all.xml
```

用 XML 而非 text，便于后续按 `rule`/`priority` 字段归并。

### 步骤2：编译并跑 SpotBugs

```bash
mvn -q compile
java -jar $SPOTBUGS_JAR -xml -output spotbugs-all.xml \
  -pluginList $FIND_SEC_BUGS_JAR:$FB_CONTRIB_JAR -effort:max target/classes/
```

### 步骤3：归并

| 归并动作 | 规则 |
| :--- | :--- |
| 同一 `文件:行号` + 同一缺陷语义（如空指针） | 保留 SpotBugs 条目（字节码证据更直接），PMD 条目降为附注 |
| 同为安全类且指向同一 sink（SQL/命令/反序列化） | 保留 Find Security Bugs 条目，PMD 条目并入其“同源告警”栏 |
| 仅 PMD 有（规范、复杂度、命名、重复） | 直接进入报告 |
| 仅 SpotBugs 有（资源、并发、字节码缺陷） | 直接进入报告 |
| CPD 重复片段 | 单列一节，不计入 P0/P1/P2 数量口径 |

### 步骤4：输出报告

报告表结构：

| 级别 | 文件:行号 | 规则/模式 | 引擎 | 问题摘要 | 修复方向 |
| :--- | :--- | :--- | :--- | :--- | :--- |

表后追加两节：`抑制项及理由`、`引擎与版本`（PMD 版本、SpotBugs 版本、插件版本、运行用 JDK 版本）。

## 输出物

- `pmd-all.xml`、`spotbugs-all.xml`（原始证据，保留以便复核）
- 归并报告 Markdown（按上表结构）
- CI 场景下的失败判据：P0 > 0 失败；仅 P1/P2 输出摘要并告警

## 注意事项

1. 先 PMD 后 SpotBugs：PMD 不依赖编译，能在编译失败时仍给出规范结论，避免整轮卡死。
2. 不要在归并阶段按规则名去重，两套规则名体系不可映射。
3. 若项目 JDK 高于 17，SpotBugs 需用 JDK 17 运行，报告里必须写明这一点，否则结论不可复现。
