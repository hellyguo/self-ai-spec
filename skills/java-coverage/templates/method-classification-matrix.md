# 方法分类判定矩阵

## 指标定义

| 指标 | 定义 | 计算方法 |
| ------ | ------ | --------- |
| `depCount` | 方法内部调用的**不同**依赖服务/DAO 数量 | 统计 `@Autowired` 字段在方法体内的调用次数（去重） |
| `cascadeDepth` | 级联调用深度 | A 返回值直接作为 B 的参数 → depth=2；B 返回值传给 C → depth=3；无级联 → depth=1 |
| `staticCalls` | 调用静态工具方法的数量 | 统计非本类的静态方法调用（如 `SolarExcelImportUtil.importExcel`、`StringUtils.isEmpty`） |
| `externalApiCalls` | 调用外部系统 API 的数量 | 统计 Eflow、Jenkins、企业微信等外部系统接口调用 |

## 分类矩阵

| 分类 | 条件 | 测试类型 | 模板 |
| ------ | ------ | --------- | ------ |
| **A. 简单方法** | `depCount ≤ 3` **且** `cascadeDepth = 1` **且** `staticCalls = 0` | 单元测试 | 模板三（Mockito） |
| **B. 复杂方法** | `depCount ≤ 3` **且** `cascadeDepth ≤ 2` **且** `staticCalls = 0` | 单元测试 | 模板三（Mockito），逐层 mock |
| **C. 静态依赖方法** | `staticCalls > 0` **且** `depCount ≤ 3` | 集成测试 | 模板六（PowerMock） |
| **D. 深度链路方法** | `depCount ≥ 4` **或** `cascadeDepth ≥ 3` | 集成测试 | 模板七（深度 Mock 链路） |
| **E. 外部系统方法** | `externalApiCalls ≥ 2` **且** 存在多步骤交互 | 集成测试 | 模板七（深度 Mock 链路） |

**判断优先级**：E > D > C > B > A（从严格到宽松）

## 分类结果输出格式

```
| 源方法 | depCount | cascadeDepth | staticCalls | externalApis | 分类 | 测试类型 |
|--------|----------|-------------|-------------|-------------|------|---------|
| isHasRight | 2 | 1 | 0 | 0 | A | 单元测试 |
| getTerminationTypeName | 2 | 1 | 0 | 0 | A | 单元测试 |
| resignRequestListen | 7 | 3 | 0 | 2 | D+E | 集成测试 |
| batchImpInventories | 3 | 1 | 1 | 0 | C | 集成测试 |
```

## 分类后执行规则

**单元测试（分类 A/B）**：

- 使用模板三（Service 层 Mockito 测试）
- `@ExtendWith(MockitoExtension.class)` + `@Mock` + `@InjectMocks`
- 每个 `@Mock` 必须覆盖被测方法的所有依赖路径
- 编写到与源文件同包的测试目录

**集成测试（分类 C/D/E）**：

- 分类 C（静态依赖）→ 使用模板六（PowerMock）
- 分类 D/E（深度链路）→ 使用模板七（深度 Mock 链路）
- 集成测试文件命名：`{ClassName}IntegrationTest.java`
- 集成测试放置位置：与单元测试同目录
- **必须按方法体内调用顺序逐层 mock**，不能跳过任何中间调用
- 如果某个中间依赖无法 mock（如私有构造器、final 类），在报告中标注为"无法覆盖"并说明原因

## 集成测试依赖配置（pom-test.xml）

当源方法被分类为 C/D/E 时，需要在 pom-test.xml 中添加以下可选依赖：

```xml
<!-- PowerMock（分类 C：静态方法 mock） -->
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit5</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito2</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
```

**注意**：仅在模块中存在分类 C/D/E 的方法时才添加，不影响纯单元测试模块。
