# Kotlin 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 常量（`const val`）使用大写蛇形命名
4. 优先使用 `val`（不可变引用），禁止无理由使用 `var`
5. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
6. 优先使用组合而非继承
7. 测试代码与正式代码分离，主支代码不得包含 `main` 方法或测试代码
8. 优先使用 Kotlin 惯用写法（data class、密封类、扩展函数），避免 Java 式样板代码

## 代码结构规范

### 文件大小限制

- 单文件源码行数建议不超过 2000 行
- 过大文件必须拆分，按职责聚合
- 一个文件原则上只包含一个公开类，与其强相关的私有辅助类可同文件存放

### 文件组织约定

- 文件名与类名一致（帕斯卡命名法），如 `UserService.kt`
- 顶层函数/扩展函数聚集时，文件使用驼峰命名，如 `stringExt.kt`
- 包结构与目录结构保持一致，与 Java 互操作的项目沿用 `xxx.xxx.{模块}.{子包}` 层级

### 方法大小限制

- 方法过长时应拆分为多个小方法
- 单方法超过 80 行时必须评估拆分
- 使用早返回（guard clause）减少嵌套，避免深层嵌套逻辑

### 缩进深度限制

- 最大缩进不超过 4 层
- 超过 4 层缩进表明逻辑过于复杂，应重构
- 使用早返回、密封类多态等方式减少嵌套

### 继承深度限制

- 继承树深度（DIT）不应超过 3，最大不超过 5
- Kotlin 类默认 final，仅当明确需要扩展时使用 `open`
- 优先使用接口 + 委托（`by`）组合行为，而非深继承

### 循环依赖

- 禁止包间循环依赖
- 循环依赖表明设计不清晰、职责不明晰
- 后果：不易单元测试、不易后续调整（蝴蝶效应严重）

### 模块分层

- 遵循分层架构：Controller → Service → Repository/DAO
- Controller 仅负责参数校验与响应封装，禁止业务逻辑
- Service 禁止处理 HTTP/JSON 细节，保持领域纯净

## 命名约定

| 类别 | 规则 | 示例 |
| :--- | :--- | :--- |
| 类名 / 对象名 | 帕斯卡命名法 | `UserService`，`HttpRequest` |
| 函数名 / 属性名 | 驼峰命名法 | `getUserById`，`itemCount` |
| 常量 | 大写蛇形命名法 | `MAX_RETRY_COUNT` |
| 伴生对象常量 | 大写蛇形命名法 | `companion object { const val DEFAULT_PAGE_SIZE = 20 }` |
| 包名 | 小写 | `com.example.module.repository` |
| 布尔属性 | `is` / `has` / `can` 前缀 | `isActive`，`hasPermission` |
| 扩展函数 | 驼峰命名法 | `String.toSnakeCase()` |
| 类型参数 | 单个大写字母 | `T`，`R` |

### 命名细则

- 禁止使用单字母变量名（循环变量 `i`、`j` 除外）
- 项目内命名风格统一：`clientId`/`clientID`/`_clientID` 应统一为一种
- 布尔函数命名应表达含义：`isValid()`，`canSend()`
- 处理器类以 `Handler` 为后缀，执行器类以 `Executor` 为后缀

## 空安全（核心特性）

### 可空类型

- 明确表达可空性：使用 `T?` 表示可空，禁止隐式 null
- 禁止使用 `!!` 非空断言，除非能证明逻辑上不可能为 null 且注释说明原因
- 使用 `?.` 安全调用、`?:` Elvis 运算符处理可空值

```kotlin
// 推荐
val name: String? = user?.name?.takeIf { it.isNotBlank() } ?: "匿名"

// 禁止：!! 断言
val name = user!!.name  // ❌ 可能抛 NPE
```

### lateinit 与懒加载

- `lateinit` 仅用于延迟初始化的 `var`（依赖注入场景），使用前必须保证已赋值
- 禁止对基本类型使用 `lateinit`，使用 `by lazy`
- `by lazy` 默认线程安全（`LazyThreadSafetyMode.SYNCHRONIZED`），无需额外加锁

```kotlin
class UserService(private val dao: UserDao) {
    // 依赖注入延迟初始化
    private lateinit var cache: Cache
    
    // 懒加载：首次访问时初始化
    private val config: AppConfig by lazy { loadConfig() }
}
```

### 平台类型（Java 互操作）

- 从 Java 代码返回的值视为平台类型（`String!`），必须显式声明可空性
- 处理 Java 返回值时默认按可空处理，先判空再使用
- 跨 Java 边界的方法参数/返回值应使用 JVM 注解标注可空性（`@Nullable`/`@NotNull`）

### 前置条件校验

- 使用 `require()` / `check()` 校验前置条件，替代手写 if-throw

```kotlin
fun divide(a: Int, b: Int): Int {
    require(b != 0) { "除数不能为零" }
    return a / b
}
```

## 不可变性与数据类

### 不可变性

- 属性默认 `val`，禁止无理由 `var`
- 集合默认不可变：`listOf`、`mapOf`、`setOf`
- 需要可变集合时显式使用 `mutableListOf` 等，并限制在局部使用
- 集合属性通过 `List<T>` 类型暴露只读视图，底层可变集合私有化

```kotlin
class OrderService {
    // 只读视图对外暴露，内部维护可变状态
    private val orders = mutableListOf<Order>()
    val orderCount: Int get() = orders.size
}
```

### data class

- 主要承载数据的类型使用 `data class`，自动生成 `equals`/`hashCode`/`toString`/`copy`
- data class 属性建议全部为 `val`，保持值语义
- 禁止在 data class 中定义与数据无关的业务方法
- 解构声明仅在使用场景清晰时使用，避免解构顺序错位

```kotlin
data class User(
    val id: Long,
    val name: String,
    val email: String,
)
```

### sealed class / sealed interface

- 有穷状态/类型层次使用 `sealed class` 或 `sealed interface`，配合 `when` 穷尽分支
- 禁止用 `when` 无分支 else 处理可穷尽的密封类型，应穷尽所有分支

```kotlin
sealed interface Result {
    data class Success(val data: String) : Result
    data class Failure(val code: Int, val message: String) : Result
    object Loading : Result
}

fun handle(result: Result) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Failure -> println("${result.code}: ${result.message}")
    Result.Loading -> println("加载中")
}
```

### object / companion object

- 单例使用 `object` 声明（线程安全，惰性初始化）
- 类级常量放入 `companion object`，编译期常量使用 `const val`（必须是基本类型或 String）
- `const val` 仅限顶层或 companion object 中

```kotlin
class UserRepository {
    companion object {
        const val DEFAULT_PAGE_SIZE = 20
        val INSTANCE = UserRepository()  // 运行期常量用 val
    }
}
```

## 函数与函数式编程

### 函数设计

- 参数不超过 5 个，超过使用 data class 参数对象
- 布尔参数过多时使用枚举或参数对象，避免调用处含义不明
- 默认参数值优于重载：`fun query(page: Int = 1, size: Int = 20)`
- 使用命名参数提升调用可读性

### 作用域函数

- `let` / `run` / `apply` / `also` / `with` 使用要克制，避免嵌套滥用
- 同一表达式链中禁止多种作用域函数混用，可读性优先
- 嵌套作用域函数不超过 2 层，更深处使用局部变量

```kotlin
// 推荐：用途明确的链式调用
user?.let { it.name }?.also { log.info("查询用户: {}", it) }

// 避免：多层嵌套作用域函数
user?.let {
    it.orders?.map { order ->
        order.items?.apply { ... }  // ❌ 可读性差
    }
}
```

### 扩展函数

- 扩展函数用于为既有类型补充行为，禁止滥用污染全局命名空间
- 项目内公共扩展函数集中存放于 `ext/` 包，避免散落
- 成员函数优先于扩展函数：类型自有逻辑写为成员
- 禁止为通用类型定义语义含糊的扩展（如 `String.extract()`）

### 高阶函数与内联

- 高频调用路径上的 lambda 参数函数使用 `inline`，减少对象分配
- 禁止 `inline` 修饰大函数（字节码膨胀）
- 非局部返回使用 `crossinline` / `noinline` 明确意图

```kotlin
// 高频调用路径：内联避免 lambda 对象分配
inline fun <T> Iterable<T>.forEachFast(action: (T) -> Unit) {
    for (item in this) action(item)
}
```

### 泛型

- 使用 `out` / `in` 表达协变/逆变，明确类型关系
- `reified` 仅用于需要运行时类型信息的场景，避免滥用
- 类型别名（`typealias`）仅用于简化长泛型签名，禁止掩盖类型语义

## 错误处理

### 异常处理原则

- Kotlin 无受检异常，必须在文档注释中说明可能抛出的异常
- 禁止吞异常：catch 块必须记录日志或重新抛出
- 使用 `require`/`check`/`error` 表达前置条件与非法状态
- 业务异常使用自定义异常类（继承 `Exception` 或 `RuntimeException`），配合错误码

### runCatching 使用约束

- `runCatching` 会吞掉 `CancellationException`，在协程中使用会导致协程无法取消
- 协程代码中禁止使用 `runCatching`，使用 try-catch-finally
- `runCatching` 捕获后必须处理 `onFailure`，禁止忽略结果

```kotlin
// 禁止：协程中吞掉取消异常
suspend fun load() {
    runCatching { api.fetch() }  // ❌ CancellationException 被吞，协程无法取消
}

// 推荐：协程中使用 try-catch
suspend fun load() {
    try {
        api.fetch()
    } catch (e: IOException) {
        log.error("加载失败", e)
    }
}
```

### Result 类型

- 返回结果类场景优先使用密封类表达成功/失败，而非抛异常控制流
- 禁止用异常控制正常业务流程（如用异常做条件分支）

### 错误码设计

- 设计完整的错误码体系，错误码与异常配合使用
- 错误消息应有业务含义，禁止只输出内部异常堆栈给用户

## 协程规范（企业级要求）

### 结构化并发

- **禁止 `GlobalScope`**：生命周期与整个应用绑定，无法取消，导致任务泄漏
- 必须使用结构化并发：`CoroutineScope` 由调用方创建并管理生命周期
- 应用级协程作用域通过依赖注入提供，禁止在代码中随意创建作用域

```kotlin
// 禁止：GlobalScope
GlobalScope.launch { api.fetch() }  // ❌ 无法取消，任务泄漏

// 推荐：注入作用域
class OrderService(private val scope: CoroutineScope) {
    fun submit(order: Order) {
        scope.launch {
            repository.save(order)
        }
    }
}
```

### 取消与异常

- 协程内必须响应取消：禁止吞掉 `CancellationException`
- `withContext` / `suspend` 函数内部检查 `ensureActive()` / `isActive`
- 协程异常必须处理：`SupervisorJob` + `CoroutineExceptionHandler` 或逐层传递
- 一个协程的失败不应影响兄弟协程：父子任务使用 `SupervisorJob`

```kotlin
val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

scope.launch {
    try {
        withTimeout(5000) { api.fetch() }
    } catch (e: TimeoutCancellationException) {
        log.warn("请求超时")
    }
}
```

### Dispatchers 选择

| Dispatcher | 适用场景 |
| :--- | :--- |
| `Dispatchers.Main` | UI 线程更新（Android） |
| `Dispatchers.IO` | 阻塞 IO、网络、数据库访问 |
| `Dispatchers.Default` | CPU 密集型计算 |
| `Dispatchers.Unconfined` | 禁止使用（仅测试场景） |

- **禁止在协程中执行阻塞 IO**（`Thread.sleep`、`InputStream.read`）而不切换调度器
- 数据库/网络访问必须使用 `withContext(Dispatchers.IO)` 包裹
- 自定义线程池使用 `Executors.newFixedThreadPool(...).asCoroutineDispatcher()`，必须统一管理并关闭

### 协程泄漏审查

- 长生命周期对象中启动的协程必须随对象销毁而取消
- `viewModelScope`（Android）/ 注入 scope 随组件销毁自动取消
- 定时循环任务必须可取消：`while (isActive)` 而非 `while (true)`

```kotlin
// 推荐：可取消的循环
fun watch() = scope.launch {
    while (isActive) {
        refresh()
        delay(1000)  // delay 是可取消的挂起点
    }
}
```

### Flow

- 数据流使用 `Flow` / `StateFlow` / `SharedFlow`，禁止用回调传递异步流
- `StateFlow` 适合状态持有，`SharedFlow` 适合事件广播
- 热流与冷流选择：UI 状态用 `StateFlow`，一次性事件用 `SharedFlow`（`extraBufferCapacity` 配置）
- 集合的 `flow { }` 构建器内禁止阻塞操作

## 并发与线程安全

### 共享可变状态

- 多线程共享的可变状态使用 `Mutex`、`AtomicXxx` 或线程安全集合
- 优先使用不可变对象 + `StateFlow` 发布更新，减少加锁
- `synchronized` 与 Java 规则一致：使用固定的锁对象

```kotlin
// 推荐：Mutex 保护共享状态
private val mutex = Mutex()
private var state = 0

suspend fun update() = mutex.withLock {
    state += 1
}
```

### 线程池管理

- **禁止直接创建线程**、**禁止 `Executors.newCachedThreadPool()`**（同 Java 规范）
- 使用有界 `ThreadPoolExecutor`，配置命名线程工厂与拒绝策略
- 线程池必须提供优雅停机机制（`shutdown` → `awaitTermination` → `shutdownNow`）
- 参考 Java 规范的线程池配置模板（`lang-spec/spec.java.md` 线程与并发规范章节）

### 线程不安全类

- `SimpleDateFormat`、`DecimalFormat` 等禁止声明为共享静态变量（Kotlin 中为顶层属性或 companion 属性）
- 使用线程安全的 `DateTimeFormatter`（`java.time`）
- `ThreadLocal` 必须清理：`try-finally` 中 `remove()`，线程池场景必查

## 集合与序列

### 集合操作规范

- 优先不可变集合：`listOf`、`mapOf`、`setOf`
- 需要扩容性能时预估容量：`ArrayList(initialCapacity)`
- 禁止三重循环，复杂度极高
- 避免对同一集合多次循环遍历，一次循环完成所需操作
- 使用 `Set`/`Map` 查找替代循环内线性扫描

### 序列（Sequence）

- 大数据集的多步骤链式处理使用 `Sequence` 惰性求值，避免中间集合分配
- 小数据集（< 万级）使用 `Iterable` 链式操作即可，`Sequence` 有封装开销
- 禁止对无限序列不加 `take` 限制

```kotlin
// 大数据量：Sequence 惰性处理
val result = largeList.asSequence()
    .filter { it.isValid() }
    .map { it.name }
    .take(100)
    .toList()
```

### 集合安全操作

- `getOrElse` / `getOrNull` 替代下标访问，避免越界
- `firstOrNull` 替代 `first()`（可能抛异常），配合 `?:` 处理
- 元素类型转换使用 `filterIsInstance<T>()`

## 字符串与格式化

- 字符串模板优于 `+` 拼接：`"用户: ${user.name}"`
- 字符串模板比 `String.format` 更高效，非必要不使用 format
- 循环中大量拼接使用 `StringBuilder`（Kotlin 的 `buildString { }`）

```kotlin
val sb = buildString {
    append("users: ")
    users.forEach { append(it.name).append(',') }
}
```

## 性能优化规范

### 分配优化

- 高频路径避免不必要对象分配：lambda 用 `inline`、避免装箱
- 避免 `String.split` 多次调用提取信息，使用正则预编译或 `substring`
- 高成本对象缓存复用：正则 `Regex` 必须预编译（顶层 `val`）

```kotlin
// 预编译正则，禁止在高频方法中重新编译
private val PHONE_REGEX = Regex("^1[3-9]\\d{9}$")

fun isValidPhone(phone: String): Boolean = PHONE_REGEX.matches(phone)
```

### 反射优化

- 反射结果（`KClass`、`KFunction`、属性引用）必须缓存
- 序列化框架（kotlinx.serialization、Jackson + Kotlin module）统一选型，禁止混用

### 惰性计算

- 昂贵计算使用 `by lazy` 惰性初始化
- 高频读取的配置启动时加载一次（顶层 `val` 或依赖注入），禁止循环内反复读取

### 协程性能

- 高频协程切换使用 `Dispatchers.Default` 上的 `withContext` 避免过度调度
- 数据流收集使用 `debounce` / `distinctUntilChanged` 减少无效处理

## 测试规范

### 测试框架

- 单元测试使用 JUnit5 + kotlin.test（`@Test`、`assert` 函数）
- Mock 使用 MockK（Kotlin 原生），Java 项目可沿用 Mockito
- 协程测试使用 `kotlinx-coroutines-test`（`runTest`、`StandardTestDispatcher`）

```kotlin
class UserServiceTest {
    private val dao = mockk<UserDao>()

    @Test
    fun `findById 返回用户`() = runTest {
        every { dao.findById(1L) } returns User(1, "张三")
        val user = service.findById(1L)
        assertEquals("张三", user.name)
    }
}
```

### 测试命名

- 使用反引号包裹中文描述：`` fun `登录失败时返回错误码`() ``
- 或遵循 `test_方法名_条件或预期行为` 约定
- 覆盖边界条件、无效输入、并发场景与负面用例

### 测试隔离

- 测试之间必须隔离，禁止共享可变状态
- 使用 `@BeforeEach`/`@AfterEach` 清理资源
- 协程测试使用虚拟时间（`StandardTestDispatcher`），禁止 `delay` 真实等待

## Java 互操作规范

### 互操作注解

- companion object 中需要 Java 静态访问的成员使用 `@JvmStatic`
- 需要 Java 直接读写字段时使用 `@JvmField`
- 默认参数函数需要 Java 重载时使用 `@JvmOverloads`
- 顶层函数经 `@file:JvmName("XxxUtils")` 指定 Java 侧类名

```kotlin
@file:JvmName("StringUtils")

fun String.toSnakeCase(): String = ...
```

### 平台类型边界

- Java 传入的可空性不明的值按可空处理
- 对外 Java API 使用 `@Nullable`/`@NotNull` 标注，防止调用方 NPE
- 数据类跨 Java 边界使用时注意 `copy` 方法名冲突（Kotlin 1.4+ 已有 `copy$default` 处理）

### 集合互操作

- Java 传入的集合可能为 `null`，必须判空
- 可变/不可变集合的转换使用 `toList()`/`toMutableList()`，明确所有权
- 禁止将 Kotlin 只读集合直接传给期望可变集合的 Java API

## 安全规范

### 敏感信息保护

- 密钥、密码等敏感信息禁止硬编码，使用环境变量或密钥管理服务
- 日志中禁止输出敏感信息，敏感字段打码输出
- 配置文件敏感信息写入 `.gitignore`，不提交代码库

### Web 安全（服务端）

- 用户输入必须校验与转义，防止 XSS
- SQL 使用参数绑定（Exposed/MyBatis `#{}`），禁止字符串拼接
- 动态表名/列名/排序字段必须白名单校验
- 文件上传校验类型和大小，接口限制访问频度

### 反序列化安全

- 禁止反序列化不可信输入（Jackson 禁止 `enableDefaultTyping`）
- 限制反序列化类型白名单

## 构建与依赖规范

### 构建工具

- 首选 Gradle + Kotlin DSL（`build.gradle.kts`），次选 Maven
- 版本统一：Gradle 依赖版本集中在 `libs.versions.toml`（Version Catalog）管理
- 插件使用 `kotlin("jvm")` / `kotlin("android")` 等官方插件

### 依赖规范

- 项目内同类库统一选型：序列化、日志、HTTP 客户端各选其一
- 避免深度绑定第三方框架，做薄封装保护自身代码
- 第三方 SDK 通过薄封装隔离，敏感资产不硬编码
- 依赖升级需评估破坏性变更（Kotlin 1.x 内 API 变化频繁）

### 编译器配置

- 开启 `allWarningsAsErrors = true`（或至少评审阶段开启）
- 使用 `-Xjsr305=strict` 严格处理平台类型
- 开启 `freeCompilerArgs` 中的 `-Xexplicit-api=strict`（库项目）强制公开 API 显式标注

## 代码走查关注点

### 必须修正

- 循环依赖、类初始化死锁风险（同 Java 规范）
- **`!!` 非空断言**：可能导致 NPE
- **`GlobalScope` 协程**：任务泄漏、无法取消
- **`runCatching` 吞掉 `CancellationException`**
- 协程未随组件销毁取消（协程泄漏）
- 无限循环：`while (true)` 缺少退出条件（同 Java 规范）
- 吞异常：catch 块无日志无处理
- SQL 注入、XSS、敏感信息泄露
- 线程池使用不当：`newCachedThreadPool`、直接 `new Thread`
- 平台类型未判空导致 NPE

### 应当修正

- 重复代码、过大方法/类/文件
- 过深缩进/继承（DIT > 3）
- 作用域函数嵌套滥用
- 魔幻数值/字符串（应提取为常量）
- 性能问题：循环内分配、正则未预编译、N+1 查询

### 建议改进

- 代码风格统一（ktlint）
- 注释完善（KDoc）
- 架构优化、扩展性提升

## 签名

---
**Kotlin编码规范版本**：1.0.0  
**最后更新**：2026-08-12  
**规则文件**：${AI_SPEC_ROOT}/lang-spec/spec.kotlin.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.kotlin.md  
**构建工具**：${AI_SPEC_ROOT}/lang-spec/ci.kotlin.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Kotlin项目、Android应用、JVM后端服务（Spring Boot / Ktor）
