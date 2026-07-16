# 初始化流程（首次执行）

## Step 1: 模板分类处理

模板文件按是否含项目专属占位符分为两类，区别处理：

| 分类 | 文件 | 占位符情况 | 处理方式 |
| ------ | ------ | ----------- | --------- |
| 直接复制 | `test-code-templates.md` | 无占位符，纯通用模板 | 从 `assets/` 直接复制到 `docs/`，无需分析 |
| 直接复制 | `html-report-template.md` | 无占位符，动态数据在报告生成时填充 | 从 `assets/` 直接复制到 `docs/`，无需分析 |
| 需分析填充 | `MEMORY.md` | 含项目名、技术栈、模块列表、依赖版本等占位符 | 需从项目提取信息 |
| 需分析填充 | `test-framework-cache.md` | 含依赖版本、模块路径、差异化字段等占位符 | 需从项目提取信息 |
| 需分析填充 | `pom-test-xml-template.md` | 含依赖版本占位符 | 需从项目提取信息 |

## Step 2: 项目信息提取（单次扫描，3个 Agent 并行）

3个需填充模板的占位符高度重叠（均依赖 pom.xml 的依赖版本和模块信息），**一次扫描同时填充所有模板**：

```
Agent A ─── 读根 pom.xml ──→ 提取: modules列表、Java版本、全局依赖版本、properties
  │
  ├→ 填充 MEMORY.md 占位符（项目名、技术栈、依赖版本）
  ├→ 填充 test-framework-cache.md 占位符（依赖版本部分）
  └→ 填充 pom-test-xml-template.md 占位符（依赖版本部分）

Agent B ─── 读各模块 pom.xml ──→ 提取: artifactId、parent信息、自定义properties、mainClass
  │
  ├→ 填充 test-framework-cache.md 占位符（模块路径部分）
  └→ 填充 MEMORY.md 占位符（模块结构部分）

Agent C ─── 扫描各模块 src/test/ 目录 ──→ 提取: 测试文件数、pom-test.xml 状态
  │
  └→ 填充 MEMORY.md 占位符（测试目录现状部分）
```

## Step 3: 统一写入

将所有文件写入当前目录：

- Agent A 完成后 → 写入 `MEMORY.md`（依赖版本部分）、`docs/pom-test-xml-template.md`
- Agent B 完成后 → 补充写入 `MEMORY.md`（模块部分）、`docs/test-framework-cache.md`
- Agent C 完成后 → 补充写入 `MEMORY.md`（目录现状部分）
- Step 1 的直接复制文件 → 与 Agent 并行写入（无依赖关系）

## 通用约束

- **写入路径**：所有新增或更新的固化文件统一写入当前目录（项目级，跟随项目走）
- **assets/ 目录**：通用模板，随 skill 分发，不写入项目特定数据
