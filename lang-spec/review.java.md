# Java 代码审查规则

以下规则来自 SpotBugs 和 PMD 静态分析工具，用于代码审查时识别常见问题模式。

## 静态分析规则

### 正确性问题

#### 空指针相关

| 规则ID | 描述 |
| -------- | ------ |
| NP_ALWAYS_NULL | 空指针解引用 |
| NP_NULL_ON_SOME_PATH | 可能的空指针解引用 |
| NP_NULL_PARAM_DEREF | 方法调用传递null给非空参数 |
| NP_EQUALS_SHOULD_HANDLE_NULL_ARGUMENT | equals方法未检查null参数 |
| NP_BOOLEAN_RETURN_NULL | Boolean返回类型方法返回null |
| NP_OPTIONAL_RETURN_NULL | Optional返回类型方法返回null |
| RCN_REDUNDANT_NULLCHECK_WOULD_HAVE_BEEN_A_NPE | 对已解引用的值进行冗余null检查 |
| BrokenNullCheck | null检查逻辑错误 |

#### 类型转换与比较

| 规则ID | 描述 |
| -------- | ------ |
| BC_IMPOSSIBLE_CAST | 不可能的类型转换 |
| BC_IMPOSSIBLE_DOWNCAST | 不可能的向下转型 |
| BC_IMPOSSIBLE_INSTANCEOF | instanceof始终返回false |
| EC_UNRELATED_TYPES | equals比较不同类型 |
| EC_ARRAY_AND_NONARRAY | equals比较数组和非数组 |
| EC_NULL_ARG | 调用equals(null) |
| INT_BAD_COMPARISON_WITH_SIGNED_BYTE | 有符号字节比较错误 |
| CompareObjectsWithEquals | 使用equals比较对象 |

#### equals/hashCode/compareTo

| 规则ID | 描述 |
| -------- | ------ |
| EQ_ALWAYS_TRUE | equals始终返回true |
| EQ_ALWAYS_FALSE | equals始终返回false |
| EQ_SELF_NO_OBJECT | 协变equals方法定义 |
| HE_EQUALS_NO_HASHCODE | 定义equals但未定义hashCode |
| HE_HASHCODE_NO_EQUALS | 定义hashCode但未定义equals |
| CO_SELF_NO_OBJECT | 协变compareTo方法定义 |
| CO_COMPARETO_RESULTS_MIN_VALUE | compareTo返回Integer.MIN_VALUE |
| OverrideBothEqualsAndHashcode | 必须同时重写equals和hashCode |

#### 其他正确性问题

| 规则ID | 描述 |
| -------- | ------ |
| IL_INFINITE_LOOP | 明显的无限循环 |
| IL_INFINITE_RECURSIVE_LOOP | 明显的无限递归循环 |
| IL_CONTAINER_ADDED_TO_ITSELF | 集合添加自身 |
| RV_RETURN_VALUE_IGNORED | 忽略返回值 |
| DMI_ARGUMENTS_WRONG_ORDER | 方法参数顺序错误 |
| UR_UNINIT_READ | 构造函数中读取未初始化字段 |
| RANGE_ARRAY_INDEX | 数组索引越界 |

### 安全问题

#### SQL注入与数据库安全

| 规则ID | 描述 |
| -------- | ------ |
| SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE | 非常量字符串传递给execute方法 |
| SQL_PREPARED_STATEMENT_GENERATED_FROM_NONCONSTANT_STRING | 非常量字符串生成PreparedStatement |
| DMI_CONSTANT_DB_PASSWORD | 硬编码数据库密码 |
| DMI_EMPTY_DB_PASSWORD | 空数据库密码 |
| SQL_BAD_RESULTSET_ACCESS | 尝试访问索引0的结果集字段 |

#### XSS与Web安全

| 规则ID | 描述 |
| -------- | ------ |
| XSS_REQUEST_PARAMETER_TO_SEND_ERROR | Servlet错误页反射型XSS漏洞 |
| XSS_REQUEST_PARAMETER_TO_SERVLET_WRITER | Servlet反射型XSS漏洞 |
| XSS_REQUEST_PARAMETER_TO_JSP_WRITER | JSP反射型XSS漏洞 |
| HRS_REQUEST_PARAMETER_TO_HTTP_HEADER | HTTP响应分割漏洞 |
| PT_ABSOLUTE_PATH_TRAVERSAL | Servlet绝对路径遍历 |
| PT_RELATIVE_PATH_TRAVERSAL | Servlet相对路径遍历 |

#### 加密与密钥安全

| 规则ID | 描述 |
| -------- | ------ |
| HardCodedCryptoKey | 硬编码加密密钥 |
| InsecureCryptoIv | 不安全的加密初始化向量 |
| UNS_UNSAFE_CALL | 调用Unsafe类 |

### 性能问题

#### 资源泄漏

| 规则ID | 描述 |
| -------- | ------ |
| OS_OPEN_STREAM | 方法可能未关闭流 |
| OS_OPEN_STREAM_EXCEPTION_PATH | 异常路径可能未关闭流 |
| ODR_OPEN_DATABASE_RESOURCE | 方法可能未关闭数据库资源 |
| CloseResource | 确保资源关闭 |
| UseTryWithResources | 使用try-with-resources |
| AvoidFileStream | 避免使用FileInputStream/FileOutputStream |

#### 低效操作

| 规则ID | 描述 |
| -------- | ------ |
| DM_STRING_CTOR | 低效的String构造 |
| DM_BOOLEAN_CTOR | 低效的Boolean构造 |
| SBSC_USE_STRINGBUFFER_CONCATENATION | 循环中使用+拼接字符串 |
| WMI_WRONG_MAP_ITERATOR | 低效使用keySet迭代器 |
| StringInstantiation | 避免不必要的String实例化 |
| InefficientStringBuffering | 低效的StringBuffer使用 |
| UseArrayListInsteadOfVector | 使用ArrayList替代Vector |

#### 内存与对象创建

| 规则ID | 描述 |
| -------- | ------ |
| DMI_RANDOM_USED_ONLY_ONCE | Random对象仅使用一次 |
| DM_NEW_FOR_GETCLASS | 仅为了获取class而创建对象 |
| ISC_INSTANTIATE_STATIC_CLASS | 不必要的静态类实例化 |
| SIC_INNER_SHOULD_BE_STATIC | 应该是静态内部类 |
| AvoidInstantiatingObjectsInLoops | 避免循环中创建对象 |

### 并发问题

#### 线程安全

| 规则ID | 描述 |
| -------- | ------ |
| IS2_INCONSISTENT_SYNC | 不一致的同步 |
| IS_FIELD_NOT_GUARDED | 字段未防护并发访问 |
| VO_VOLATILE_REFERENCE_TO_ARRAY | volatile数组引用元素非volatile |
| VO_VOLATILE_INCREMENT | volatile字段自增非原子操作 |
| NonThreadSafeSingleton | 非线程安全单例 |
| UseConcurrentHashMap | 使用ConcurrentHashMap |
| DoubleCheckedLocking | 双重检查锁定问题 |

#### 同步问题

| 规则ID | 描述 |
| -------- | ------ |
| DL_SYNCHRONIZATION_ON_SHARED_CONSTANT | 字符串字面量同步 |
| DL_SYNCHRONIZATION_ON_BOOLEAN | Boolean同步 |
| ESYNC_EMPTY_SYNC | 空同步块 |
| UL_UNRELEASED_LOCK | 方法未在所有路径释放锁 |
| AvoidSynchronizedAtMethodLevel | 避免方法级同步 |

#### 线程操作

| 规则ID | 描述 |
| -------- | ------ |
| RU_INVOKE_RUN | 调用run而非start |
| SC_START_IN_CTOR | 构造函数调用Thread.start() |
| WA_NOT_IN_LOOP | wait不在循环中 |
| NO_NOTIFY_NOT_NOTIFYALL | 使用notify而非notifyAll |
| DontCallThreadRun | 不要直接调用Thread.run() |

### 死锁风险

| 规则ID                   | 描述                 |
|--------------------------|----------------------|
| TLW_TWO_LOCK_WAIT        | 持有两个锁时wait     |
| SWL_SLEEP_WITH_LOCK_HELD | 持有锁时调用sleep    |

### 代码风格

#### 命名规范

| 规则ID | 描述 |
| -------- | ------ |
| NM_CLASS_NAMING_CONVENTION | 类名应以大写字母开头 |
| NM_METHOD_NAMING_CONVENTION | 方法名应以小写字母开头 |
| NM_LCASE_HASHCODE | hashcode应为hashCode |
| NM_LCASE_TOSTRING | tostring应为toString |
| NM_BAD_EQUAL | equal应为equals |
| LongVariable | 变量名过长 |
| ShortVariable | 变量名过短 |
| AvoidDollarSigns | 避免使用$符号 |

#### 导入与修饰符

| 规则ID | 描述 |
| -------- | ------ |
| UnnecessaryImport | 不必要的导入 |
| UnnecessaryModifier | 不必要的修饰符 |
| ModifierOrder | 修饰符顺序 |
| NoPackage | 缺少包声明 |

#### 代码结构

| 规则ID | 描述 |
| -------- | ------ |
| OnlyOneReturn | 方法应只有一个返回点 |
| ControlStatementBraces | 控制语句大括号 |
| EmptyControlStatement | 空控制语句 |
| UnnecessaryReturn | 不必要的return |
| UnnecessarySemicolon | 不必要的分号 |
| UselessParentheses | 无用的括号 |

### 最佳实践

#### 序列化

| 规则ID | 描述 |
| -------- | ------ |
| SE_NO_SERIALVERSIONID | 可序列化类未定义serialVersionUID |
| SE_NONFINAL_SERIALVERSIONID | serialVersionUID非final |
| SE_NONSTATIC_SERIALVERSIONID | serialVersionUID非static |
| SE_NONLONG_SERIALVERSIONID | serialVersionUID非long |
| SE_BAD_FIELD | 非瞬态非可序列化字段 |
| MissingSerialVersionUID | 缺少serialVersionUID |

#### Clone实现

| 规则ID | 描述 |
| -------- | ------ |
| CN_IMPLEMENTS_CLONE_BUT_NOT_CLONEABLE | 定义clone但未实现Cloneable |
| CN_IDIOM_NO_SUPER_CALL | clone方法未调用super.clone() |
| CloneMethodMustImplementCloneable | clone方法必须实现Cloneable |
| CloneMethodMustBePublic | clone方法必须为public |

#### 异常处理

| 规则ID | 描述 |
| -------- | ------ |
| DE_MIGHT_DROP | 方法可能丢弃异常 |
| DE_MIGHT_IGNORE | 方法可能忽略异常 |
| AvoidCatchingGenericException | 避免捕获泛型异常 |
| PreserveStackTrace | 保留堆栈跟踪 |
| ReturnFromFinallyBlock | finally块中返回 |
| EmptyCatchBlock | 空catch块 |

#### 资源与环境

| 规则ID | 描述 |
| -------- | ------ |
| DM_EXIT | 方法调用System.exit() |
| DM_GC | 显式垃圾回收 |
| AvoidPrintStackTrace | 避免printStackTrace |
| SystemPrintln | 使用System.out.println |
| DoNotCallGarbageCollectionExplicitly | 不要显式调用GC |

#### 集合与数组

| 规则ID | 描述 |
| -------- | ------ |
| DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION | 不要用removeAll清空集合 |
| UseCollectionIsEmpty | 使用isEmpty检查集合 |
| UseEnumCollections | 使用EnumSet/EnumMap |
| ReturnEmptyCollectionRatherThanNull | 返回空集合而非null |
| MethodReturnsInternalArray | 方法返回内部数组 |

### 设计问题

#### 复杂度

| 规则ID | 描述 |
| -------- | ------ |
| CyclomaticComplexity | 圈复杂度过高 |
| CognitiveComplexity | 认知复杂度过高 |
| NPathComplexity | NPath复杂度过高 |
| TooManyMethods | 方法过多 |
| TooManyFields | 字段过多 |
| ExcessiveParameterList | 参数列表过长 |
| ExcessivePublicCount | 公共成员过多 |

#### 耦合与内聚

| 规则ID | 描述 |
| -------- | ------ |
| CouplingBetweenObjects | 对象间耦合度过高 |
| LawOfDemeter | 违反迪米特法则 |
| LooseCoupling | 应使用松耦合类型 |
| GodClass | 上帝类 |
| DataClass | 数据类 |

#### 类设计

| 规则ID | 描述 |
| -------- | ------ |
| AbstractClassWithoutAbstractMethod | 抽象类无抽象方法 |
| UseUtilityClass | 应使用工具类 |
| SingularField | 单例字段 |
| AvoidDeeplyNestedIfStmts | 避免深度嵌套if语句 |

### 易错代码

#### 常见错误模式

| 规则ID | 描述 |
| -------- | ------ |
| DMI_BIGDECIMAL_CONSTRUCTED_FROM_DOUBLE | BigDecimal从double构造精度问题 |
| DMI_BAD_MONTH | 错误的月份常量值 |
| DMI_CALLING_NEXT_FROM_HASNEXT | hasNext调用next |
| RV_ABSOLUTE_VALUE_OF_RANDOM_INT | 随机整数绝对值计算错误 |
| FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER | 与NaN比较永假 |
| AvoidDecimalLiteralsInBigDecimalConstructor | 避免BigDecimal使用double字面量 |
| ComparisonWithNaN | 与NaN比较 |

#### Switch与循环

| 规则ID | 描述 |
| -------- | ------ |
| SF_SWITCH_FALLTHROUGH | switch穿透 |
| SF_DEAD_STORE_DUE_TO_SWITCH_FALLTHROUGH | switch穿透导致死存储 |
| ImplicitSwitchFallThrough | 隐式switch穿透 |
| JumbledIncrementer | 混乱的循环增量 |

#### 赋值与比较

| 规则ID | 描述 |
| -------- | ------ |
| SA_FIELD_SELF_ASSIGNMENT | 字段自赋值 |
| SA_LOCAL_SELF_ASSIGNMENT | 局部变量自赋值 |
| SA_FIELD_SELF_COMPARISON | 字段自比较 |
| DLS_DEAD_LOCAL_STORE | 局部变量死存储 |
| DLS_OVERWRITTEN_INCREMENT | 被覆盖的自增 |
| AssignmentInOperand | 操作数中的赋值 |

#### Finalize问题

| 规则ID | 描述 |
| -------- | ------ |
| FI_EMPTY | 空finalizer应删除 |
| FI_MISSING_SUPER_CALL | finalizer未调用父类finalizer |
| FI_EXPLICIT_INVOCATION | 显式调用finalizer |
| EmptyFinalizer | 空finalizer |
| FinalizeDoesNotCallSuperFinalize | finalizer未调用super.finalize |

## 时钟回拨攻击审查（金融系统必查）

**问题描述**：使用 `System.currentTimeMillis()` 进行超时计算，受NTP同步和系统时间修改影响，时钟回拨可能导致超时逻辑失效。

**适用场景**：

- 高性能低延时系统（金融报价、交易系统、高频交易）
- 分布式锁控、主从选举、心跳检测
- 任何依赖时间间隔判断的分布式系统

**检测方法**：

**Java危险模式**：

```java
long start = System.currentTimeMillis();
long elapsed = System.currentTimeMillis() - start; // 可能为负数
if (elapsed >= timeout) {
    triggerElection(); // 永远不触发
}
```

**审查要点**：

1. 检查超时计算、心跳检测、选举超时是否使用墙钟时间
2. `currentTimeMillis()` 是否用于间隔测量
3. 时间差计算是否可能为负数
4. 是否存在 `elapsed >= timeout` 判断逻辑

**技术原理**：

| API | 时间基准 | 受时钟回拨影响 | 适用场景 |
| ----- | --------- | --------------- | ---------- |
| `currentTimeMillis()` | 墙钟时间(UTC) | ✅ 受影响 | 绝对时间、日志时间戳 |
| `nanoTime()` | 单调时钟(JVM启动) | ❌ 不受影响 | 间隔测量、超时计算 |
| `gettimeofday()` | 墙钟时间 | ✅ 受影响 | 绝对时间 |
| `clock_gettime(CLOCK_MONOTONIC)` | 单调时钟 | ❌ 不受影响 | 间隔测量 |

**重构建议**：

**Java正确模式**：

```java
private volatile long lastHeartbeatNanos = System.nanoTime();

long elapsedNanos = System.nanoTime() - lastHeartbeatNanos;
long elapsedMs = TimeUnit.NANOSECONDS.toMillis(elapsedNanos);
if (elapsedMs >= timeout) {
    triggerElection();
}
```

**注意**：

- `nanoTime()` 返回值无绝对意义，仅用于差值计算
- 日志时间戳仍应使用 `currentTimeMillis()` 获取可读时间
- 金融系统必须使用单调时钟防止时钟回拨攻击

## 禁止无限循环审查

**问题描述**：使用 `while(true)`、`for(;;)` 创建无限循环，缺少明确的退出条件，导致以下问题：

1. **线程阻塞**：难以优雅退出，可能需要强制终止线程
2. **资源泄漏**：循环退出路径不明确，资源可能无法正确释放
3. **调试困难**：无法控制循环执行流程，调试时需要打断点
4. **不优雅退出**：缺乏退出条件，必须通过中断信号或外部干预才能退出

**检测方法**：

- Java：`while (true)`、`for (;;)`
- 所有语言中都禁止使用 `while(true)` / `while(1)` / `for(;;)` / `while True`

**审查要点**：

1. 必须使用明确的退出条件变量（布尔变量、计数器、状态标志）
2. 必须考虑异常路径下的优雅退出机制
3. 长时间运行的循环必须有超时保护和心跳检测
4. 循环退出应确保资源正确释放（文件句柄、网络连接、锁等）

**重构建议**：

**Java示例**：

```java
// 使用 volatile boolean 控制循环
private volatile boolean running = true;
while (running) {
    try {
        processRequest();
    } catch (InterruptedException e) {
        running = false;  // 优雅退出
        Thread.currentThread().interrupt();
    }
}
```

**核心原则**：

- **可控制性**：循环必须能被外部停止
- **资源安全**：退出时必须清理资源
- **异常处理**：异常路径也要能正常退出
- **线程友好**：支持线程中断和超时机制

## Logger 参数空指针风险审查

**问题描述**：在日志输出中直接调用可能为 null 的对象方法，导致二次异常。尤其在 catch 块内，二次异常会逃逸到外层导致线程崩溃。

**检测方法**：

- Java：`logger.error("错误: {}", obj.getName(), e)`，obj可能为null

**审查要点**：

1. 检查日志参数中是否调用了对象方法（如 `obj.getName()`）
2. 判断该对象是否可能为 null（方法返回值、查找结果）
3. 特别关注 catch 块内的日志输出
4. 对象是否在 try 块前已判空

**重构建议**：

**Java示例**：

```java
FidDef fiddef = dictionary.getFidDef(id);
if (fiddef == null) {
    logger.warn("字段ID未定义: {}", id);
    return;
}
try {
    process(fiddef.getType());
} catch (Exception e) {
    logger.error("处理失败, 字段: {}", fiddef.getName(), e);
}
```

**注意**：此检查项为**参考级别**，不强制要求修复。原因：

1. 静态分析可能无法准确判断对象是否为 null
2. 需要结合业务逻辑上下文判断
3. 建议在代码审查时人工确认风险

## 敏感字段输出审查（强制要求）

**问题描述**：密码、密钥、令牌等敏感信息被记录到日志或输出到调试信息。

**检测方法**（通用示例）：

```java
// Java示例：敏感信息泄露
logger.debug("Password: " + password); // 明文记录到日志
System.out.println("API Key: " + apiKey); // 输出到控制台
```

**审查要点**：

1. 敏感信息是否被记录到日志文件（所有日志级别）
2. 调试信息是否包含敏感数据
3. 是否硬编码敏感信息在源代码中
4. 是否使用环境变量或密钥管理服务存储敏感配置

**重构建议**：

- 使用安全日志宏过滤敏感字段（自动替换为`****`）
- 使用加密存储敏感信息
- 实施代码审查规则禁止硬编码密钥
- 敏感数据只通过安全通道传输（环境变量、密钥管理服务）

## 坏味道分类扩展（基于 AI 时代新发现）

文章《代码在发臭：一个能"闻"出坏味道的 AI 技能》将坏味道扩展为 8 大类 50+ 种，特别针对 AI 生成代码的常见问题：

### 架构类坏味道

| 坏味道 | 检测方法 | 重构建议 |
| -------- | ---------- | ---------- |
| **大泥球** | 模块职责不清、边界模糊 | 重新划分模块边界 |
| **分布式单体** | 微服务拆分过细、频繁跨服务调用 | 合并相关服务 |
| **贫血模型** | 仅有 getter/setter 的数据对象 | 引入领域行为 |
| **CQRS 滥用** | 查询与命令分离过度复杂 | 简化设计 |
| **层边界违反** | 上层直接依赖底层实现细节 | 引入接口抽象 |
| **过度分层** | 不必要的中间层、层层转发 | 合并或移除冗余层 |
| **过度抽象** | 过早抽象、抽象层次过多 | 延迟抽象时机 |
| **"未来主义"架构** | 为不存在的需求过度设计 | 遵循 YAGNI 原则 |

### 耦合类坏味道

| 坏味道 | 检测方法 | 重构建议 |
| -------- | ---------- | ---------- |
| **循环依赖** | 模块间相互引用形成环 | 引入中间层或接口 |
| **内容耦合** | 模块直接修改对方内部状态 | 封装状态变更 |
| **公共耦合** | 过度使用全局状态 | 引入依赖注入 |
| **印记耦合** | 传递整个对象仅用部分字段 | 传递最小接口 |

### 内聚类坏味道

| 坏味道 | 检测方法 | 重构建议 |
| -------- | ---------- | ---------- |
| **上帝对象** | 单个类 > 500 行、方法 > 20 个 | Extract Class |
| **霰弹式修改** | 修改功能需改动多处代码 | Move Method |
| **依恋情结** | 方法过度访问其他类的数据 | Move Method |
| **数据泥团** | 总是一起出现的字段 | Introduce Parameter Object |
| **发散式变化** | 单个类因不同原因频繁修改 | Extract Class |

### 设计类坏味道

| 坏味道 | 检测方法 | 重构建议 |
| -------- | ---------- | ---------- |
| **抽象泄露** | 实现细节暴露给调用方 | 封装内部实现 |
| **静态粘连** | 过度使用 static 方法/字段 | 引入依赖注入 |
| **服务定位器滥用** | 依赖服务定位器而非注入 | 使用依赖注入 |
| **SOLID 违反** | 违反单一职责等原则 | 按原则重构 |
| **Switch 类型分支** | 基于类型的 switch/case 链 | 用多态替代条件 |

### 代码类坏味道（Fowler 经典）

| 坏味道 | 检测方法 | 重构建议 |
| -------- | ---------- | ---------- |
| **重复代码** | 相同代码模式多处出现 | Extract Method |
| **长方法** | 方法 > 50 行 | Extract Method |
| **基本类型偏执** | 过度使用基本类型而非对象 | Replace Primitive with Object |
| **魔数魔串** | 代码中硬编码的数值/字符串 | Introduce Named Constant |
| **死代码** | 永远不会执行的代码 | 删除 |
| **深层嵌套** | 嵌套层次 > 4（箭头反模式） | Extract Method / Guard Clause |
| **过长参数列表** | 参数 > 5 个 | Introduce Parameter Object |

### 测试类坏味道（AI 时代新增）

| 坏味道 | 检测方法 | 重构建议 |
| -------- | ---------- | ---------- |
| **零测试覆盖** | AI 生成代码无测试 | 补充单元测试 |
| **测试-实现耦合** | 测试依赖具体实现细节 | 面向接口测试 |
| **不稳定测试** | 测试结果随机失败 | 隔离测试环境 |

### 命名类坏味道

- **模糊命名**：Manager/Helper/Util 滥用 → 具体职责命名  
- **命名不一致**：相同概念不同命名 → 统一命名规范

### 复杂度类坏味道（性能热点）

- **嵌套循环 O(n²)**：循环内嵌套循环 → 优化算法复杂度  
- **N+1 查询**：循环内发起查询 → 批量查询 + 预加载  
- **重复线性扫描**：循环内使用线性查找 → 改用 Set/Map  
- **循环内排序**：每次迭代都排序 → 提前排序  
- **渲染重复计算**：UI 渲染中重复计算 → 缓存计算结果  
- **数据结构选错**：使用低效数据结构 → 选择合适的数据结构

## AI 生成代码特有审查

随着 AI 辅助编程普及，需特别关注以下 AI 生成代码的常见问题：

- **零测试覆盖**：检查新代码是否有配套测试 → 强制要求补充测试  
- **过度复杂化**：AI 倾向于生成"聪明"但难懂的代码 → 要求简化实现  
- **魔法字符串/数字**：硬编码的业务逻辑值 → 提取为常量  
- **缺少错误处理**：乐观假设路径，缺少异常处理 → 补充边界检查和异常处理  
- **性能陷阱**：循环内查询、线性查找等 → 使用 `/lets-loop` 技能专门检测  
- **安全漏洞**：字符串拼接 SQL、未转义输出等 → 加强安全审查  
- **硬编码配置**：API key、数据库连接等 → 提取到配置文件中  
- **不符合团队规范**：命名、格式与现有代码不一致 → 按团队规范修正  
- **注释质量**：生成无意义或错误的注释 → 审查并修正注释  
- **过度抽象**：为简单需求生成复杂抽象 → 简化设计

### AI 代码审查建议

1. **必查项**：安全漏洞、零测试覆盖、性能陷阱
2. **建议项**：代码规范、错误处理、配置管理
3. **可忽略项**：个人风格差异（如大括号位置）

## 通用规则补充说明

### 与技能框架的关联

以上"坏味道分类扩展"和"AI生成代码特有审查"章节的内容也作为通用规则定义在技能框架中：

1. **坏味道分类扩展**：参考 `${AI_SPEC_ROOT}/skills/code-review/SKILL.md` 中的"坏味道分类扩展"章节
2. **AI生成代码审查**：参考 `${AI_SPEC_ROOT}/skills/code-review/SKILL.md` 中的"AI生成代码特有审查"章节  
3. **数据库审查规则**：参考 `${AI_SPEC_ROOT}/skills/code-review/SKILL.md` 中的"数据库审查规则"章节

### 审查优先级指导

#### 必须修正（高优先级）

1. 安全漏洞：SQL注入、XSS、敏感数据泄露
2. 内存泄漏和资源管理问题
3. 线程安全和并发问题
4. 企业级专项审查发现的问题（时钟回拨攻击等）

#### 建议改进（中优先级）

1. 代码结构和设计模式问题
2. 性能优化和算法效率
3. 错误处理和异常管理
4. 代码可维护性和可读性

#### 参考建议（低优先级）

1. 命名规范和代码风格
2. 注释质量和文档完整性
3. 测试覆盖和测试质量

## 签名

---
**Java代码审查规则版本**：1.2.0  
**最后更新**：2025-01-01  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.java.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.java.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Java项目、金融系统、高性能系统
