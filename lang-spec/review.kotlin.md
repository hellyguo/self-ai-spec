# Kotlin 代码审查规则

以下规则来自 detekt、ktlint 等 Kotlin 静态分析工具，并结合 JVM 层 SpotBugs/PMD 可适用规则，用于代码审查时识别常见问题模式。

## 静态分析工具

| 工具 | 用途 | 命令 |
| :--- | :--- | :--- |
| **detekt** | Kotlin 代码质量/坏味道检测（复杂度、风格、潜在缺陷） | `./gradlew detekt` |
| **ktlint** | Kotlin 代码风格检查（官方风格指南） | `./gradlew ktlintCheck` |
| **SpotBugs** | JVM 字节码级缺陷检测（对 Kotlin 编译产物同样适用） | 参考 java-check-spotbugs |
| **kover** | Kotlin 测试覆盖率统计 | `./gradlew koverReport` |

审查时结合 detekt 规则集与 Kotlin 语言特性专项审查。

## 空安全审查

### 非空断言（强制禁止）

| 规则ID（detekt） | 描述 |
| :--- | :--- |
| `UnsafeCallOnNullableType` | 对可空类型使用 `!!` |
| `UnnecessaryNotNullOperator` | 冗余的 `!!`（类型已非空） |
| `UnsafeCast` | 使用 `as` 而非 `as?` 强转 |
| `UnnecessarySafeCall` | 冗余的 `?.`（类型已非空） |
| `ReturnCount` | 早返回数量（配合空安全） |

**审查要点**：

1. 代码中是否使用 `!!`，必须确认逻辑上不可能为 null 且注释说明
2. `as` 强转是否可能 ClassCastException，应使用 `as?` + 判空
3. Java 平台类型返回值是否显式判空

```kotlin
// 禁止
val name = user!!.name
val value = map["key"] as String  // 可能 ClassCastException

// 推荐
val name = user?.name ?: ""
val value = map["key"] as? String ?: ""
```

### lateinit 审查

- `lateinit` 属性是否在使用前保证赋值
- 是否误用于基本类型（应使用 `by lazy`）
- 是否在多线程下共享 `lateinit` 可变状态

## 协程审查（强制项目）

### 作用域与生命周期

| 问题模式 | 危害 | 修复建议 |
| :--- | :--- | :--- |
| `GlobalScope.launch` | 协程与应用同生命周期，无法取消，任务泄漏 | 使用注入的 `CoroutineScope` |
| 长生命周期对象中协程未取消 | 组件销毁后协程仍在运行 | scope 随组件销毁自动取消 |
| `CoroutineScope` 随处创建 | 生命周期管理混乱 | 依赖注入统一管理 |
| 协程内阻塞 IO 未切换调度器 | 阻塞线程池 | `withContext(Dispatchers.IO)` |

### 取消与异常

| 问题模式 | 危害 | 修复建议 |
| :--- | :--- | :--- |
| `runCatching` 捕获协程代码 | 吞掉 `CancellationException`，协程无法取消 | try-catch-finally |
| catch 块吞掉 `CancellationException` | 取消不生效 | 捕获后重新抛出或 `ensureActive()` |
| 子协程失败导致父协程整体失败 | 兄弟任务被连带取消 | `SupervisorJob` |
| 协程异常未处理 | 静默失败，难以排查 | `CoroutineExceptionHandler` 或逐层处理 |
| `while(true)` 循环协程 | 无法随取消退出 | `while(isActive)` |

### 调度器

- `Dispatchers.Unconfined` 是否被误用（仅测试场景允许）
- `Dispatchers.IO` 是否用于 CPU 密集计算（应使用 `Default`）
- 自定义线程池是否通过 `asCoroutineDispatcher()` 包装且生命周期受控

## 错误处理审查

### 异常吞没

- catch 块是否为空或有日志无处理（禁止）
- `runCatching` 结果是否被忽略（`onFailure` 必须处理）
- 是否用异常控制正常业务流程（禁止）

### 异常类型

- 是否捕获过于宽泛的 `Exception`（应捕获具体类型）
- 业务异常是否定义错误码体系
- 协程中的 `CancellationException` 是否被误捕获并吞掉

## 代码风格审查（ktlint / detekt）

### 命名与格式

| 规则ID | 描述 |
| :--- | :--- |
| `MatchingDeclarationName` | 文件名与主类名不一致 |
| `ClassNaming` | 类名未使用帕斯卡命名法 |
| `FunctionNaming` | 函数名未使用驼峰命名法 |
| `VariableNaming` | 变量名未使用驼峰命名法 |
| `ConstantNaming` | 常量未使用大写蛇形命名法 |
| `TopLevelPropertyNaming` | 顶层属性命名 |
| `PackageNaming` | 包名包含大写 |

### 代码结构

| 规则ID | 描述 |
| :--- | :--- |
| `MaxLineLength` | 行过长（建议 120 字符） |
| `TooManyFunctions` | 类中函数过多 |
| `TooManyLines` | 函数/文件过长 |
| `LongParameterList` | 参数列表过长（> 5） |
| `ComplexMethod` | 圈复杂度过高 |
| `CyclomaticComplexMethod` | 圈复杂度过高 |
| `NestedBlockDepth` | 嵌套块过深（> 4） |
| `LargeClass` | 类过大（> 500 行） |

### 作用域函数滥用

- `let`/`run`/`apply`/`also` 嵌套超过 2 层
- 同一链式调用混用多种作用域函数
- 无返回值场景使用 `apply`/`also` 而非 `let`（`let` 返回 lambda 结果）

```kotlin
// 审查：以下写法可读性差，应拆分
user?.let {
    it.orders?.forEach { order ->
        order.items?.apply { this.forEach { item -> ... } }
    }
}
```

### 扩展函数滥用

- 是否为通用类型定义了语义模糊的扩展
- 扩展函数是否散落在各处（应集中在 `ext/` 包）
- 成员函数能力是否被扩展函数错误替代

## 性能审查

### 分配与内存

| 问题模式 | 危害 | 修复建议 |
| :--- | :--- | :--- |
| 循环内创建 lambda 未 inline | 高频对象分配，GC 压力 | `inline` 内联 |
| 大集合链式操作中间集合过多 | 内存浪费 | `Sequence` 惰性求值 |
| 正则表达式未预编译 | 每次调用重新编译 | 顶层 `val` 预编译 |
| 循环内字符串 `+` 拼接 | 大量临时对象 | `buildString { }` |
| 集合未指定容量频繁扩容 | 扩容拷贝开销 | 预估初始容量 |
| 反射（KClass/KFunction）未缓存 | 反射开销高 | 缓存反射结果 |

### 协程性能

- 高频协程是否过度切换调度器
- `Flow` 收集是否缺少 `debounce`/`distinctUntilChanged` 过滤
- 是否有 N+1 查询（循环内逐个查询，应批量）

### 数据结构选择

- 循环内线性查找（应使用 `Set`/`Map`）
- 嵌套循环 O(n²) 算法
- 用 `String.split` 反复解析信息（应结构化解析）

## 并发审查

### 共享状态

| 问题模式 | 危害 | 修复建议 |
| :--- | :--- | :--- |
| 共享可变状态无同步 | 数据竞争 | `Mutex`/`Atomic`/`StateFlow` |
| `synchronized` 锁对象不正确 | 锁失效 | 固定锁对象 |
| 顶层 `var` 多线程修改 | 竞态条件 | 封装 + 同步 |
| 线程不安全类（SimpleDateFormat）共享 | 数据错乱 | `DateTimeFormatter` |

### 线程管理

- 是否直接 `Thread { }` 创建线程（应使用线程池）
- 是否使用 `Executors.newCachedThreadPool()`（禁止）
- 线程池是否命名、有界、可优雅停机

### 死锁与阻塞

- 锁获取顺序是否一致
- 协程持有锁时是否执行阻塞操作
- `runBlocking` 是否出现在生产代码（仅测试/入口允许）

## JVM 层通用审查（SpotBugs 可适用规则）

Kotlin 编译为 JVM 字节码，以下 SpotBugs 规则对 Kotlin 项目同样适用：

### 正确性

| 规则ID | 描述 |
| :--- | :--- |
| NP_ALWAYS_NULL | 空指针解引用 |
| NP_NULL_ON_SOME_PATH | 可能的空指针解引用 |
| EQ_ALWAYS_TRUE / EQ_ALWAYS_FALSE | equals 恒真/恒假 |
| HE_EQUALS_NO_HASHCODE | 定义 equals 未定义 hashCode（Kotlin 中 data class 自动生成，重点查自定义） |
| RV_RETURN_VALUE_IGNORED | 忽略返回值 |
| IL_INFINITE_LOOP | 无限循环 |
| DMI_ARGUMENTS_WRONG_ORDER | 方法参数顺序错误 |

### 资源管理

| 规则ID | 描述 |
| :--- | :--- |
| OS_OPEN_STREAM | 流未关闭 |
| ODR_OPEN_DATABASE_RESOURCE | 数据库资源未关闭 |
| CloseResource | 资源未关闭（Kotlin 应使用 `use { }`） |
| DM_STRING_CTOR | 低效 String 构造 |

### 集合与序列化

| 规则ID | 描述 |
| :--- | :--- |
| DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION | 用 removeAll 清空集合 |
| SE_NO_SERIALVERSIONID | 可序列化类未定义 serialVersionUID |
| DMI_BIGDECIMAL_CONSTRUCTED_FROM_DOUBLE | BigDecimal 从 double 构造精度问题 |

## 时钟回拨攻击审查（金融系统必查）

**问题描述**：使用 `System.currentTimeMillis()` 进行超时计算，受 NTP 同步和系统时间修改影响，时钟回拨可能导致超时逻辑失效。

Kotlin 中 `System.currentTimeMillis()`、`Date().time` 均为墙钟时间。

**Kotlin 危险模式**：

```kotlin
val start = System.currentTimeMillis()
val elapsed = System.currentTimeMillis() - start  // 可能为负数
if (elapsed >= timeout) {
    triggerElection()  // 永远不触发
}
```

**审查要点**：

1. 超时计算、心跳检测、选举超时是否使用墙钟时间
2. 时间差计算是否可能为负数

**重构建议**：

```kotlin
private val lastHeartbeatNanos = System.nanoTime()  // 单调时钟

val elapsedMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - lastHeartbeatNanos)
if (elapsedMs >= timeout) {
    triggerElection()
}
```

**注意**：日志时间戳仍应使用墙钟时间获取可读时间；间隔测量必须使用单调时钟（`System.nanoTime()`）。

## 禁止无限循环审查

**问题描述**：`while (true)` / `while(true)` 创建无限循环，缺少明确退出条件。

**审查要点**：

1. 必须使用明确的退出条件变量
2. 协程循环使用 `while (isActive)` 支持取消
3. 长时间运行循环必须有超时保护和心跳检测
4. 异常路径也要能正常退出

**Kotlin 正确模式**：

```kotlin
private var running = true

suspend fun watch() {
    while (running && currentCoroutineContext().isActive) {
        try {
            process()
            delay(100)
        } catch (e: CancellationException) {
            running = false
            throw e  // 重新抛出，保持可取消
        }
    }
}
```

## Logger 参数空指针风险审查

**问题描述**：日志输出中直接调用可能为 null 的对象方法，导致二次异常。Kotlin 中 `logger.error("{}", user.name)` 若 `user` 为 null 会抛 NPE（日志框架调用时才会求值）。

**审查要点**：

1. 日志参数是否调用了可空对象的方法
2. catch 块内的日志输出尤其关注

**Kotlin 正确模式**：

```kotlin
val user = repository.findById(id)
if (user == null) {
    logger.warn("用户不存在: {}", id)
    return
}
try {
    process(user.name)
} catch (e: Exception) {
    logger.error("处理失败, 用户: {}", user.name, e)
}
```

## 敏感字段输出审查（强制要求）

**问题描述**：密码、密钥、令牌等敏感信息被记录到日志或输出到调试信息。

**审查要点**：

1. 敏感信息是否被记录到日志文件（所有日志级别）
2. data class 的 `toString()` 是否泄露敏感字段（data class 自动生成的 toString 会输出所有属性！）

3. 调试信息是否包含敏感数据
4. 是否硬编码敏感信息在源代码中
5. 敏感数据只通过安全通道传输（环境变量、密钥管理服务）

**重点检查**：data class 自动生成的 `toString()` 会输出所有属性，若包含密码等敏感字段将直接泄露：

```kotlin
// 危险：data class 自动 toString 会输出密码
data class User(val name: String, val password: String)  // ❌ toString() 泄露密码

// 修复：敏感字段排除出 toString
data class User(val name: String) {
    var password: String = ""  // 不使用 data class 自动生成，或自定义 toString 打码
        private set
}
```

## 坏味道分类扩展

参考 Java 审查规则与通用技能框架（`${AI_SPEC_ROOT}/skills/code-review/SKILL.md`），Kotlin 项目重点关注：

### 架构类

- 大泥球：模块职责不清
- 贫血模型：data class 纯数据无行为（Kotlin 中 data class 只承载数据，业务行为放 Service/Domain）
- 层边界违反：Controller 直接操作 DAO

### 设计类

- **伴随对象滥用**：`companion object` 承载大量逻辑（应拆为独立类）
- **过度扩展**：大量扩展函数使类型行为分散
- 静态粘连：顶层函数/`object` 承载本应为实例的状态

### 代码类

- **重复代码**：Kotlin 中常表现为多处相同的数据类与转换逻辑
- **长方法**：方法 > 50 行
- **基本类型偏执**：应使用值类（`@JvmInline value class`）或枚举
- **魔数魔串**：应提取为 `const val`

### 复杂度类（性能热点）

- 嵌套循环 O(n²)
- N+1 查询：循环内查询
- 重复线性扫描：应使用 `Set`/`Map`
- 循环内排序

## AI 生成代码特有审查

- **零测试覆盖**：AI 生成代码无测试 → 强制补充
- **过度复杂**：过度使用协程/Flow 实现简单逻辑 → 简化
- **`!!` 泛滥**：AI 倾向用 `!!` 简化空安全 → 改为安全调用
- **魔法字符串**：硬编码业务值 → 提取常量
- **缺少错误处理**：乐观假设路径 → 补充边界检查
- **性能陷阱**：循环内查询、重复分配 → 性能审查
- **安全漏洞**：字符串拼接 SQL、敏感信息输出 → 安全审查
- **注释质量**：无意义注释 → 审查修正

## 审查优先级指导

### 必须修正（高优先级）

1. 空安全：`!!` 滥用、平台类型未判空
2. 协程：`GlobalScope`、取消失效、协程泄漏
3. 安全漏洞：SQL 注入、XSS、敏感数据泄露
4. 并发：共享状态竞争、线程池滥用
5. 资源泄漏与内存问题

### 建议改进（中优先级）

1. 代码结构和设计模式问题
2. 性能优化和算法效率
3. 错误处理和异常管理
4. 代码可维护性和可读性

### 参考建议（低优先级）

1. 命名规范和代码风格（ktlint）
2. 注释质量和文档完整性（KDoc）
3. 测试覆盖和测试质量

## 签名

---
**Kotlin代码审查规则版本**：1.0.0  
**最后更新**：2026-08-12  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.kotlin.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.kotlin.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Kotlin项目、Android应用、JVM后端服务（Spring Boot / Ktor）
