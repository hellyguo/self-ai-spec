## 常见问题解决

### 问题1: 依赖注入失败

**解决方案**: 使用`@SpringBootTest`进行集成测试

```java
@SpringBootTest
class MyTest {
    @Autowired MyService service; // 自动注入
}
```

### 问题2: 数据库依赖

**解决方案**: 使用H2内存数据库

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

### 问题3: 外部服务依赖

**解决方案**: 使用`@MockBean`

```java
@SpringBootTest
class MyTest {
    @MockBean ExternalService external;
}
```

### 问题4: 私有方法无法测试

**解决方案**:
1. 通过公共方法间接测试
2. 使用反射（不推荐）
3. 重构为可测试的结构

### 问题5: JUnit 5 测试不执行（Tests run: 0）

**根因**: Maven Surefire 默认使用 JUnit 4 provider，无法发现 JUnit 5 测试。

**必须同时满足以下条件**:
1. 添加 `junit-jupiter-engine` 依赖（仅有 `junit-jupiter-api` 不够，engine 是运行时必需的）
2. 配置 `maven-surefire-plugin` 版本 >= 2.22.0（支持 JUnit Platform）

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter-engine</artifactId>
    <version>5.7.0</version>
    <scope>test</scope>
</dependency>

<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>2.22.2</version>
</plugin>
```

### 问题6: JaCoCo 报告未生成（Skipping JaCoCo execution due to missing execution data file）

**根因**: JaCoCo agent 通过 `-javaagent` JVM 参数在 fork 的子进程中工作。

**必须注意**:
1. **不能使用 `forkCount=0`** — 测试必须在独立 JVM 中运行，否则 `argLine` 被忽略
2. 确保 `jacoco-maven-plugin` 的 `prepare-agent` goal 在 `test` 之前执行
3. 确保 `report` goal 绑定在 `test` phase 之后

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.8</version>
    <executions>
        <execution>
            <id>prepare-agent</id>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
    </executions>
</plugin>
```

### 问题7: 构建环境污染导致 Surefire/JaCoCo 崩溃

**症状**: `NoClassDefFoundError (wrong name: target/test-classes/...)` 或 `Can't add different class with same name`

**根因**: `src/test/resources` 中包含了之前构建的 `target/` 目录（含 .class 文件），Maven 将其复制到 `target/test-classes/target/...` 和 `target/classes/target/...`，导致类路径污染。

**解决方案**: 在 pom.xml 中排除嵌套的 target 目录:

```xml
<testResources>
    <testResource>
        <directory>src/test/resources</directory>
        <excludes>
            <exclude>target/**</exclude>
            <exclude>**/surefire-reports/**</exclude>
            <exclude>**/jacoco/**</exclude>
        </excludes>
    </testResource>
</testResources>
<resources>
    <resource>
        <directory>src/test/resources</directory>
        <excludes>
            <exclude>target/**</exclude>
        </excludes>
    </resource>
</resources>
```

### 问题8: Controller 测试 NPE（@InjectMocks 未注入全部依赖）

**根因**: Controller 有多个 `@Autowired` 字段，但测试只 `@Mock` 了部分。未被 mock 的字段为 null。

**解决方案**: 必须为 Controller 中 **所有** `@Autowired` 字段提供 `@Mock`，即使测试方法不直接调用它们，Controller 方法内部可能间接调用。

**检查步骤**: 读取 Controller 源文件，列出所有 `@Autowired` 字段，确保测试中每个都有对应的 `@Mock`。

### 问题9: Java 版本不匹配导致编译失败

**根因**: 项目使用 Java 8，但测试代码使用了 Java 10+ 语法。

**规则**: 编写测试前先确认项目的 Java 版本（检查 pom.xml 中 `maven-compiler-plugin` 的 `<source>` 配置）。常见错误:
- Java 8 禁止使用 `var` 关键字
- Java 8 不支持 `List.of()`、`Map.of()` 等（用 `Arrays.asList()`、`new HashMap<>()` 替代）

### 问题10: 测试方法缺少 throws Exception 声明

**根因**: 当 mock 的方法签名包含 `throws Exception` 时，在 `when().thenReturn()`、`doNothing().when()`、`verify()` 中调用这些方法也需要处理异常。特别是在 lambda 表达式（如 `assertThrows`）内调用。

**规则**: 对所有调用了声明 `throws Exception` 方法的测试方法，统一添加 `throws Exception`。不要省略，Java 编译器对 checked exception 要求严格。

### 问题11: Mock 方法参数签名不匹配

**根因**: `when/verify` 中的参数类型/数量与实际接口方法签名不一致。

**规则**: 编写 mock 前必须先读取源代码，确认:
1. 方法参数的**确切数量**
2. 每个参数的**确切类型**（如 `Long` vs `long`、`Boolean` vs `boolean`）
3. 方法返回类型

**推荐做法**: 对于参数很多的复杂方法，优先使用 `any()` 匹配器而非精确匹配，避免因参数不匹配导致编译失败。

### 问题12: Maven Compiler Plugin 与高版本 JDK 不兼容导致 NPE

**根因**: maven-compiler-plugin 3.1 与 JDK 9+ 不兼容，编译时抛出 `NullPointerException at JavaCompiler.readSourceFile`。旧版插件使用已废弃的内部 API，高版本 JDK 中这些 API 行为不同。

**解决方案**: 运行测试时必须使用与项目编译级别匹配的 JDK 版本。本项目为 Java 1.8，必须使用 JDK 1.8 运行 Maven：

```bash
# 指定 JAVA_HOME 为 JDK 1.8 路径
JAVA_HOME="D:/product/Java/jdk1.8.0_171" "D:/product/apache-maven-3.9.11/bin/mvn" clean test

# 或者在 pom-test.xml 中升级 compiler 插件版本（如需支持高版本 JDK）
# maven-compiler-plugin >= 3.8.1 支持 JDK 11+
# maven-compiler-plugin >= 3.11.0 支持 JDK 17+
```

**规则**: 编写测试前先确认项目的 Java 编译级别（pom.xml 中 `maven-compiler-plugin` 的 `<source>` 配置），确保运行 Maven 的 JDK 版本与编译级别匹配。

### 问题13: 子模块单独构建时父 POM 依赖版本缺失

**根因**: 子模块 pom.xml 通过 `<parent>` 引用父 POM 的 `<dependencyManagement>` 来统一管理依赖版本。当使用 pom-test.xml 替换子模块的 pom.xml 后单独构建时，如果父 POM 未安装到本地 Maven 仓库，所有继承的版本号都会缺失，报 `'dependencies.dependency.version' for xxx:jar is missing`。

**解决方案**: 在替换 pom.xml 并构建子模块前，先从项目根目录安装父 POM：

```bash
# Step 1: 安装父 POM（-N 表示仅安装 POM，不递归构建子模块）
cd {项目根目录}
JAVA_HOME="{JDK_1.8路径}" mvn install -N

# Step 2: 替换子模块 pom.xml 并构建
cd {子模块目录}
cp pom-test.xml pom.xml
JAVA_HOME="{JDK_1.8路径}" mvn clean test
```

**规则**: 每次使用 pom-test.xml 构建子模块前，必须先确保父 POM 已安装到本地 Maven 仓库。

### 问题14: Mockito NoClassDefFoundError: ByteBuddy

**根因**: Mockito 2.x 依赖 ByteBuddy 和 Objenesis 库来创建 Mock 对象。如果 pom-test.xml 中仅声明了 `mockito-core` 而未显式添加 `byte-buddy` 和 `byte-buddy-agent`，Maven 可能无法正确解析这些传递依赖（尤其当项目没有继承 `spring-boot-starter-parent` 时）。

**解决方案**: 在 pom-test.xml 中显式添加 ByteBuddy 和 Objenesis 依赖：

```xml
<dependency>
    <groupId>net.bytebuddy</groupId>
    <artifactId>byte-buddy</artifactId>
    <version>1.9.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>net.bytebuddy</groupId>
    <artifactId>byte-buddy-agent</artifactId>
    <version>1.9.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.objenesis</groupId>
    <artifactId>objenesis</artifactId>
    <version>2.6</version>
    <scope>test</scope>
</dependency>
```

**规则**: 使用 Mockito 2.x 时，必须在 pom-test.xml 中显式添加 ByteBuddy（版本与 Mockito 匹配）和 Objenesis 依赖。Mockito 2.23.4 对应 ByteBuddy 1.9.3。

### 问题15: AssertJ assertThat(boolean) 在 Java 8 中的重载歧义

**根因**: AssertJ 3.11.1 中 `assertThat()` 有多个重载方法，当传入原始类型 `boolean` 时，Java 8 编译器无法区分 `assertThat(IntPredicate)` 和 `assertThat(Predicate<T>)`，导致编译错误。

**解决方案**: 将 boolean 结果存入局部变量（自动装箱为 Boolean），再传入 assertThat：

```java
// 错误写法
assertThat(target.containsInt(array, value)).isTrue();

// 正确写法
boolean result = target.containsInt(array, value);
assertThat(result).isTrue();
```

同样的歧义也可能出现在泛型推断不够明确时（如 `new ArrayList<>()` 传入方法后返回值被 assertThat 接收），需要用显式类型参数或局部变量消除歧义。

**规则**: 在 Java 8 + AssertJ 3.11.1 环境下，对所有返回 boolean 或泛型 T 的方法调用，先用局部变量接收结果再断言，避免 assertThat 重载歧义。

### 问题16: 测试文件中 service/DAO 类的 import 包路径错误

**根因**: 在多模块 Maven 项目中，很多 Service 接口和 DAO 接口分散在不同模块中。编写测试时如果仅凭类名猜测包路径，容易导入错误。例如 `ProjectMemberDao` 可能在 `commons` 模块的 `com.erayt.emis.commons.projectmember.dao` 包下，而不是 `com.erayt.emis.hr.dao`。

**解决方案**: 编写测试前，必须先读取被测源文件的 import 列表，获取每个依赖的精确包路径。

```java
// 错误：凭猜测写 import
import com.erayt.emis.hr.dao.ProjectMemberDao;       // 不存在
import com.erayt.emis.hr.service.RightService;        // 不存在

// 正确：从源文件 import 列表复制
import com.erayt.emis.commons.projectmember.dao.ProjectMemberDao;
import com.erayt.emis.commons.right.inter.RightService;
```

**规则**: 对于多模块项目的测试文件，所有被测类依赖的 import 路径必须从源文件（src/main/java）的 import 列表中获取，不要凭记忆或猜测编写。

### 问题17: 方法依赖链过长导致单元测试 NPE

**根因**: 某些 Service 方法（如流程监听、审批回调）内部调用了 5+ 个依赖服务，形成深度依赖链。仅 mock 部分依赖会导致后续调用时 NPE。

**解决方案**: 对于依赖链过长的方法，应识别为不适合单元测试的场景：

1. 检查方法内部调用了多少个不同的依赖服务
2. 如果超过 4 个且存在级联调用（A 返回值传给 B，B 返回值传给 C），标记为集成测试候选
3. 仅测试该方法的参数校验和简单分支，跳过主流程

```java
// 不要尝试 mock 整个流程：
// when(A.call()).thenReturn(x);
// when(B.call(x)).thenReturn(y);  // A 的返回值要作为 B 的输入
// when(C.call(y)).thenReturn(z);  // 级联依赖太多

// 而是只测试方法的入口校验逻辑，主流程留给集成测试
```

**规则**: 当方法内部调用 4+ 个不同依赖服务且存在级联调用时，不编写单元测试，在报告中标注为"需集成测试覆盖"。

### 问题18: maven.test.skip=true 无法阻止测试文件编译（编译器插件冲突）

**根因**: 当 pom.xml 中 `maven-compiler-plugin` 配置了 `<skip>false</skip>` 时，即使通过 `-Dmaven.test.skip=true` 命令行参数，Maven 仍然会编译 `src/test/java` 下的测试文件。这是因为编译器插件的 `<skip>false</skip>` 配置覆盖了 `maven.test.skip` 属性对测试编译阶段的影响。

**症状**: 执行 `mvn install -Dmaven.test.skip=true` 时，如果 `src/test/java` 下有引用 JUnit 5 等测试框架的文件（但原 pom.xml 未声明这些依赖），会报编译错误：`找不到符号: 类 Test / DisplayName`。

**解决方案**: 安装模块时，将测试文件暂时移到 `src/test/java` 目录之外：

```bash
# Step 1: 临时移走测试文件
mkdir -p /tmp/backup-tests
mv src/test/java/com/erayt/... /tmp/backup-tests/

# Step 2: 安装模块（此时无测试文件，不会编译失败）
mvn install -Dmaven.test.skip=true

# Step 3: 恢复测试文件
mv /tmp/backup-tests/... src/test/java/com/erayt/
```

或者更优的做法：**先创建 pom-test.xml 再安装，安装时直接用 pom-test.xml**（因为 pom-test.xml 已包含测试依赖）。

**规则**: 在原 pom.xml 不含 JUnit 5 依赖的模块中，如果有测试文件存在于 `src/test/java`，安装模块前必须确保测试文件不会被编译。优先使用 pom-test.xml 进行安装。

### 问题19: IBM MQ MQC.MQFMT_NONE 实际值是 8 个空格而非空字符串

**根因**: IBM MQ 的 `MQC.MQFMT_NONE` 常量定义为 `"        "`（8 个空格字符），而非直觉上的空字符串 `""`。这是 IBM MQ 的规范——MQFMT_NONE 表示"无特定格式"，用 8 字符空白填充的 MQCHAR8 类型表示。

**症状**: 测试中 `assertThat(MQC.MQFMT_NONE).isEqualTo("")` 失败，报 `expected: "" but was: "        "`。使用 `isNotBlank()` 也会失败，因为纯空格字符串被 AssertJ 视为 blank。

**解决方案**: 测试 MQ 格式常量时，使用 `isNotEmpty()` 和 `isNotEqualTo()` 而非 `isEqualTo("")` 或 `isNotBlank()`：

```java
// 错误写法
assertThat(MQC.MQFMT_NONE).isEqualTo("");        // 失败：实际是8个空格
assertThat(MQC.MQFMT_NONE).isNotBlank();          // 失败：纯空格算 blank

// 正确写法
assertThat(MQC.MQFMT_NONE).isNotEmpty();           // 通过：非空字符串
assertThat(MQC.MQFMT_NONE).isNotEqualTo(MQC.MQFMT_STRING); // 通过：不等于 STRING 格式
```

**规则**: 测试 IBM MQ 相关常量时，不要假设 `MQFMT_NONE` 为空字符串。应使用 `isNotEmpty()` 和比较断言而非值断言。如需精确值，先打印确认再编写断言。

### 问题20: Mockito 严格模式下 UnnecessaryStubbingException

**根因**: Mockito 3.x 默认启用严格模式（`Strictness.STRICT_STUBS`）。当 mock 了某个方法但测试执行过程中从未调用该 mock 时，Mockito 会抛出 `UnnecessaryStubbingException`。

**典型场景**: 测试 `checkPledgeRule` 方法时，如果 `freezingType` 不是 `PLEDGEFROZEN`，方法内部不会调用 `comCommonParamRepository.getBondsSalesParam()`，但测试中 `when(comCommonParamRepository.getBondsSalesParam(...)).thenReturn(...)` 已经配置了这个 mock。

```java
// 错误：非质押冻结类型时 getBondsSalesParam 不会被调用，导致 UnnecessaryStubbing
kindflowEvent.setFreezingType(FreezingType.NORMALFROZEN.getValue());
when(comCommonParamRepository.getBondsSalesParam(anyString())).thenReturn(params); // 多余的 stub
invokeCheckPledgeRule(kindflowEvent, 20250101, bonds);
```

**解决方案**: 只在测试方法**确实会触发**该 mock 调用时才配置 stub：

```java
// 正确：非质押冻结类型不会进入 checkPledgeFlag，不需要 mock repository
kindflowEvent.setFreezingType(FreezingType.NORMALFROZEN.getValue());
// 不需要 when(...) 配置
invokeCheckPledgeRule(kindflowEvent, 20250101, bonds); // 直接通过
```

或在必要时使用宽松模式：`@MockitoSettings(strictness = Strictness.LENIENT)`

**规则**: 编写 Mockito 测试时，只 mock 被测方法**实际会调用**的依赖。分析方法体逻辑，确保每个 `when()` 配置都有对应的实际调用。避免"以防万一"的多余 mock。

### 问题21: 反射调用私有方法时异常被 InvocationTargetException 包装

**根因**: 通过 `Method.invoke()` 调用私有方法时，如果目标方法内部抛出异常（如 `BizRuntimeException`），Java 反射机制会将其包装为 `InvocationTargetException`，原始异常成为其 `cause`。

**症状**: 测试中使用 `assertThatThrownBy(() -> method.invoke(target, args)).isInstanceOf(BizRuntimeException.class)` 失败，因为实际抛出的是 `InvocationTargetException`，而非 `BizRuntimeException`。

```java
// 错误：直接判断异常类型不匹配
assertThatThrownBy(() -> invokeCheckPledgeFlag(bonds))
    .isInstanceOf(BizRuntimeException.class);  // 失败：实际是 InvocationTargetException
```

**解决方案**: 使用 `hasCauseInstanceOf()` 或 `isInstanceOf(InvocationTargetException.class)` + 检查 cause：

```java
// 正确写法 1：通过 cause 断言
assertThatThrownBy(() -> invokeCheckPledgeFlag(bonds))
    .hasCauseInstanceOf(BizRuntimeException.class);

// 正确写法 2：直接捕获 InvocationTargetException
assertThatThrownBy(() -> invokeCheckPledgeFlag(bonds))
    .isInstanceOf(InvocationTargetException.class)
    .hasRootCauseInstanceOf(BizRuntimeException.class);
```

**规则**: 测试通过反射调用的私有方法时，所有异常断言必须考虑 `InvocationTargetException` 包装。优先使用 `hasCauseInstanceOf()` 或 `hasRootCauseInstanceOf()` 而非 `isInstanceOf()`。

### 问题22: sed 命令修改 pom-test.xml 时副作用风险

**根因**: 使用 `sed -i` 命令对 XML 文件进行批量替换时，可能产生意外的副作用。例如：
1. `sed -i 's|<version>2.19.1</version>|<version>2.22.2</version>|'` 可能替换到其他插件的版本号
2. `sed -i '/<\/dependencies>/i\...'` 可能将内容插入到 `<exclusions>` 内的 `</dependencies>` 标签之前
3. 多条 sed 命令组合可能产生格式问题（如重复的 `<skipTests>` 配置）

**解决方案**: 对于 XML 文件的修改，优先使用 Edit 工具进行精确替换，而非 sed 全局替换。如果必须使用 sed，确保正则表达式足够精确以避免误匹配。

**规则**: 修改 pom-test.xml 等 XML 文件时，使用 Edit 工具精确替换特定内容，避免 sed 全局替换带来的副作用。

---

### 问题23: 子模块 pom.xml 无 surefire 配置导致继承父 pom 的 skip=true 无法被命令行覆盖

**根因**: 当父 pom.xml 在 maven-surefire-plugin 中配置 `<skip>true</skip>` 和 `<skipTests>true</skipTests>` 时，子模块即使执行 `mvn test -Dskip=false -DskipTests=false`，也无法覆盖父 pom 的配置。这是因为 surefire plugin 的 configuration 是在父 pom 中定义的，子模块只是继承，没有自己的配置来覆盖。

**解决方案**: 在子模块 pom.xml 的 `<build><plugins>` 部分添加 surefire plugin 配置：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>2.19.1</version>
    <configuration>
        <skip>false</skip>
        <skipTests>false</skipTests>
        <argLine>-Dfile.encoding=UTF-8 ${surefireArgLine}</argLine>
    </configuration>
</plugin>
```

**重要**: 测试完成后，需要恢复原 pom.xml（如果备份了）。使用 `mv pom-backup.xml pom.xml` 恢复。

**规则**: 当父 pom 配置 `<skip>true</skip>` 导致测试无法执行时，必须在子模块 pom.xml 中添加自己的 surefire plugin 配置来覆盖。命令行参数无法覆盖 plugin configuration。

---

## 最佳实践（从 SKILL.md 迁入）

### 实践1: 反复执行后有大突破时，总结处理方式方法，归总记录

**说明**: 在增量测试的编译-修复循环中，当经过多次尝试终于解决一个复杂问题（如依赖链 NPE、Mock 注入失败等）时，必须将解决方案记录到本错误知识库（error-guide.md）中。这确保后续遇到同类问题时可以直接参考，避免重复探索。

**规则**: 每次成功修复一个编译或运行时错误后，立即记录。记录前先检查是否已存在同类问题，避免重复。