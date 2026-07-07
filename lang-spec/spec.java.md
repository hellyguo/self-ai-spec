# Java 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 静态不可变变量名使用大写
4. 静态可变变量名使用小写
5. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
6. 优先使用组合而非继承
7. 测试代码与正式代码分离，主支代码不得包含 `main` 方法或 `test` 代码

## 代码结构规范

### 文件大小限制

- 单文件源码行数建议不超过 2000 行
- 过大文件必须拆分，按职责聚合
- 前端 JS 文件同样适用，避免单文件超 3000 行

### 方法大小限制

- 方法字节码长度不应超过 325 字节（JVM JIT 编译分界线）
- 超过此大小的方法无法被 JIT 优化，影响性能
- 方法过长时应拆分为多个小方法

### 缩进深度限制

- 最大缩进不超过 4 层
- 超过 4 层缩进表明逻辑过于复杂，应重构
- 使用早返回、策略模式等方式减少嵌套

### 继承深度限制

- 继承树深度(DIT)不应超过 3
- 最大不超过 5，过深继承导致代码难以理解和维护
- 优先使用组合而非继承

### 循环依赖

- 禁止包间循环依赖
- 循环依赖表明设计不清晰、职责不明晰
- 后果：不易单元测试、不易后续调整（蝴蝶效应严重）
- 可通过 IDEA 菜单 `Code -> Analyze Code -> Cyclic Dependencies` 检查

### CK 度量指标

- **CBO**（对象类间耦合）：控制类的合作数量
- **DIT**（继承树深度）：不超过 3
- **LCOM**（方法聚合不足）：关注类内聚性
- **NOC**（子类数量）：合理控制
- **RFC**（类的响应）：控制方法调用复杂度
- **WMC**（加权方法数）：控制类方法数量

## 类设计规范

### 工具类模式

```java
// 工具类：final class + 私有构造函数
final class DbSqlExecutor {
    private DbSqlExecutor() {
    }
    
    static void execSql(...) { }
}
```

### 常量类模式

```java
// 常量类：final class + 私有构造函数 + static final 字段
final class DbEnumConsts {
    static final String SQL_DDL = "...";
    static final String[] FORBIDDEN_SQL_OP = {...};
    
    private DbEnumConsts() {
    }
}
```

### 函数式接口

```java
// 使用 @FunctionalInterface 标注单一方法接口
@FunctionalInterface
interface ResultSetHandler<T> {
    void process(ResultSet resultSet) throws SQLException;
}
```

### 避免巨型类

- 雷同代码较多、巨型方法较多时应重构
- 数据类字段重复时，设立聚合数据类作为聚合根
- 通过组合排列适应变化，提高后续扩展性

## 访问控制规范

1. **公共 API**：使用 `public` 修饰，暴露给外部使用
2. **内部工具类**：使用包级私有（无修饰符），仅包内可见
3. **常量类**：使用包级私有，通过 `static import` 引入

```java
// 内部工具类 - 包级私有
final class EnumLoader {
    static int loadFromPropertiesInternal(...) { }
}

// 外部使用
import static cn.itcraft.dyenums.config.file.EnumLoader.loadFromPropertiesInternal;
```

## 常量管理规范

1. 模块级常量集中在专门的常量类中（如 `DbEnumConsts`）
2. 类级常量定义在类的开头
3. SQL 语句必须定义为常量，禁止内联字符串
4. SQL 中固定值必须注释说明
5. 魔幻数值、魔幻字符串必须常量化

```java
// 推荐
static final String SQL_DML_QUERY = 
    "SELECT ENUM_CLASS, CODE, NAME, DESCRIPTION FROM SYS_ENUM WHERE ENUM_CLASS = ?";

// 禁止
stmt.executeQuery("SELECT * FROM table");  // ❌ 内联SQL
if (status == 1) { }  // ❌ 魔幻数值
```

## 包结构和导入规范

- 遵循包层次结构：`xxx.xxx.{模块}.{子包}`
- 包命名使用小写，不得包含大小写混用
- 分组导入：先标准 Java 库，再第三方库，用空行分隔
- 导入整个类，而不是单个静态方法（例如：`import java.util.Objects`）
- 在 `@throws` JavaDoc 中引用异常时使用完全限定类名
- 从内部常量类导入常量时使用 `static import`

## 格式化规范

- 统一代码格式化，项目组内保持一致
- 4 空格缩进，不使用制表符
- 花括号与语句在同一行（`public void method() {`）
- 最大行长度为 120 个字符，超长则换行
- 方法可见性修饰符放在最前：`public static final`
- 在开括号后、闭括号前、类/方法注释周围使用空行

## 命名约定

- 类名：帕斯卡命名法（`UserStatus`，`EnumRegistry`）
- 方法名：驼峰命名法（`valueOf`，`registerAll`）
- 变量名：驼峰命名法（`enumClass`，`enumValue`）
- 常量名：大写蛇形命名法（`private static final long serialVersionUID`）
- 布尔方法：以 `is` 或 `has` 为前缀（`isActive`，`isBlocked`，`requiresAdminAction`）
- 处理器类：以 `Handler` 为后缀（`ResultSetHandler`，`DyEnumQueryHandler`）
- 执行器类：以 `Executor` 为后缀（`DbSqlExecutor`）
- 常量类：以 `Consts` 为后缀（`DbEnumConsts`）
- 项目内命名风格统一：`_clientID`/`clientID`/`clientId` 应统一为一种

## 类型系统

- 正确使用泛型：`<T extends DyEnum>`
- 尽可能指定泛型类型
- 在实用情况下使用具体返回类型而非通配符
- 字段不可变时标记为 `final`
- 高并发计数时使用 `LongAdder` 而非 `AtomicLong`
- 避免使用 `Map` 传参，导致类型不灵活、hash 成本高

## 错误处理

### 异常处理原则

- 统一用异常代替返回 `null`，避免空指针风险
- 尽早使用 `Objects.requireNonNull()` 验证输入参数
- 为无效状态抛出适当的异常（`IllegalArgumentException`，`IllegalStateException`）
- 使用描述性的异常消息："ParameterName 不能为空" 或 "Code 不能为空"
- 遵循快速失败原则 - 在构造函数和公共方法中验证前置条件
- 必要时使用防御性复制
- 异常不能只打日志，需要后续处理（重试、通知、记录等）

### 错误码设计

- 设计完整的错误码体系
- 错误码与异常配合使用
- 错误消息应有业务含义

## 文档风格

- 在 JavaDoc 中包含 `@author` 和 `@since` 标签
- 使用清晰详细的方法描述
- 记录所有方法参数、返回值和抛出的异常
- 用 `<p>` 分隔类描述和构造函数注释
- 在 JavaDoc 中包含相关的使用示例
- `toString()` 风格统一，使用 `StringBuilder` 而非 `+` 拼接

## 设计模式

### 接口设计

- 业务接口应具备通用性，不带业务特性
- 接口扇出不应受限
- 保持接口小而专注
- 使用抽象基类共享实现
- 通过保持实例变量为 `protected final` 来遵循不可变原则

### 多态替代条件

- 避免大量 `if-else` 堆砌
- 使用策略模式、工厂模式替代复杂条件判断
- 实现数据驱动编程

```java
// 推荐：使用枚举+处理器模式
public enum CurrFlag {
    CONTAINS_JPY(new JpyFlagHandler()),
    NON_JPY(new NonJpyFlagHandler());
    
    private final CurrFlagHandler handler;
    
    public void handle() { handler.handle(); }
}
```

### 工厂与注册表模式

- 使用工厂模式创建对象
- 使用 ConcurrentHashMap 实现线程安全的注册表模式
- 实现适当的 equals/hashCode/toString 方法

## 测试指南

- 编写全面的单元测试，覆盖边界条件、无效输入和并发场景
- 遵循命名约定：`test_方法名_条件或预期行为()`
- 必要时使用正确的 `@Before`/`@After` 方法设置
- 包含负面测试用例（无效参数、不存在的值）
- 使用多线程测试并发场景
- 使用 setUp/clear/tearDown 保持适当的测试隔离

## 日志记录（SLF4J）

### 日志级别

- 使用适当的日志级别：`debug`、`info`、`warn`、`error`
- 重要操作用 `info`，跟踪用 `debug`，问题用 `warn`/`error`
- 对于批量处理中的可恢复错误，使用 `warn` 而非 `error`

### 日志格式

- 在日志消息中使用占位符：`logger.info("已注册 {}: {}", name, code)`
- 调试日志输出对象时，确保对象类重写了 `toString()` 方法
- 日志要有意义，能帮助问题排查
- 日志中明确打印服务器信息，便于分布式环境定位

### 日志安全

- 日志中禁止添加回车换行符（`\r`、`\n`）
- 多线程情况下，回车换行导致日志错位，影响分析判断
- 参考：https://dzone.com/articles/log-crlf-injection-with-slf4j
- 禁止打印大对象，影响性能且无意义

### 异常日志

- 输出异常堆栈必须使用三参数形式：`log.error("msg: {}", e.getMessage(), e)`
- 错误写法：`log.error("msg: {}", e)` 只输出异常类名或消息，无法输出堆栈
- 正确写法：`log.error("msg: {}", e.getMessage(), e)` 可完整输出堆栈信息
- **禁止异常吞没**：catch 块中必须有日志或重新抛出，禁止空 catch 块
- **异常必须处理**：捕获异常后必须有后续处理（重试、通知、降级等），不能只打日志
- **禁止 catch Exception**：应捕获具体异常类型，避免捕获 RuntimeException 等泛型异常

## 线程与并发规范

### ForkJoinPool 使用规范

#### 1. **CompletableFuture 异步执行器**
- **`CompletableFuture.runAsync()` / `supplyAsync()`** 默认使用 `ForkJoinPool.commonPool()`
- **`thenApplyAsync()` / `thenAcceptAsync()` / `whenCompleteAsync()`** 等 Async 后缀方法，未指定 Executor 时都使用公共池
- **必须指定独立线程池**：高并发场景下，公共池可能成为性能瓶颈
```java
// 错误写法：使用默认公共池
CompletableFuture.runAsync(() -> heavyTask());

// 正确写法：指定独立线程池
ExecutorService customExecutor = new ThreadPoolExecutor(...);
CompletableFuture.runAsync(() -> heavyTask(), customExecutor);
```

#### 2. **Stream 并行流**
- **`parallelStream()`** 默认使用 `ForkJoinPool.commonPool()`
- **阻塞任务危害**：并行流中任何阻塞操作（IO、sleep、锁等待）都会拖慢所有使用公共池的并行流
- **必须隔离高风险并行流**：包含 IO、网络、数据库等阻塞操作的并行流必须使用独立线程池
```java
// 错误写法：可能阻塞公共池
list.parallelStream().map(item -> {
    db.query(item);  // 阻塞操作
    return result;
});

// 正确写法1：使用独立 ForkJoinPool
ForkJoinPool customPool = new ForkJoinPool(4);
customPool.submit(() -> list.parallelStream().map(...)).join();

// 正确写法2：使用 CompletableFuture 包装
list.parallelStream()
    .map(item -> CompletableFuture.supplyAsync(() -> process(item), ioExecutor))
    .collect(Collectors.toList());
```

#### 3. **JDK 8 内部使用 ForkJoinPool 的位置**
- **java.util.concurrent.CompletableFuture**：所有 Async 方法默认使用公共池
- **java.util.stream 并行流**：`parallel()` 操作使用公共池
- **java.util.Arrays.parallelSort()**：并行排序使用公共池
- **java.util.concurrent.CountedCompleter**：CompletableFuture 内部使用
- **java.util.concurrent.Phaser**：与 ForkJoinPool.managedBlock() 集成

#### 4. **ForkJoinPool.commonPool() 特性**
- **懒加载**：首次使用时才创建，任何上述使用场景都会触发初始化
- **共享性**：所有使用默认配置的并行流、CompletableFuture 等都共享同一个池
- **默认配置**：`Runtime.getRuntime().availableProcessors() - 1` 个线程
- **守护线程**：公共池使用守护线程，不会阻止 JVM 退出
- **任务排队风险**：即使没有阻塞操作，当大量任务竞争公共池时，任务排队会导致单位耗时和延时上升超出预期
  ```java
  // 风险场景：大量并行流同时执行，即使每个任务都是纯CPU计算
  list1.parallelStream().forEach(item -> cpuIntensiveTask1(item));  // 使用公共池
  list2.parallelStream().forEach(item -> cpuIntensiveTask2(item));  // 排队等待公共池线程
  
  // 结果：list2 的执行会等待 list1 释放线程资源
  // 延时 = list1处理时间 + 线程切换开销 + 任务调度延迟
  ```
- **默认池容量有限**：默认只有 CPU核数-1 个线程，很容易被多个并发任务耗尽
- **隐式竞争**：不同业务模块、不同服务调用可能都在不知不觉中使用了公共池

#### 5. **最佳实践**
1. **IO密集型任务**：使用独立线程池（`ThreadPoolExecutor`），不要用 `parallelStream()`
2. **CPU密集型任务**：可使用 `parallelStream()`，但必须考虑任务排队风险
3. **混合型任务**：使用 `CompletableFuture` + 独立线程池组合
4. **资源隔离**：不同业务模块使用不同的线程池，避免相互影响
5. **容量规划**：根据并发任务数量配置独立的 `ForkJoinPool` 线程数
6. **监控**：监控线程池使用情况，及时发现瓶颈

#### 6. **性能风险场景**
```java
// 场景1：大量并行流同时执行，竞争公共池资源（即使任务无阻塞）
list1.parallelStream().forEach(item -> cpuIntensiveTask1(item));
list2.parallelStream().forEach(item -> cpuIntensiveTask2(item));  // 排队等待，延时上升

// 场景2：阻塞操作拖慢公共池
list.parallelStream().map(item -> {
    TimeUnit.SECONDS.sleep(1);  // ❌ 阻塞公共池线程
    return process(item);
});

// 场景3：递归任务占用所有公共池线程
class RecursiveTask extends ForkJoinTask { ... }
pool.invoke(new RecursiveTask());  // 可能占用所有公共池线程

// 场景4：CompletableFuture 默认使用公共池
CompletableFuture.runAsync(() -> task1());
CompletableFuture.runAsync(() -> task2());  // 与所有使用默认配置的任务竞争公共池
```

#### 7. **任务排队与延时风险**
- **核心问题**：公共池默认线程数有限（CPU核数-1），大量并发任务会排队等待
- **延时公式**：任务总延时 = 任务执行时间 + 队列等待时间 + 线程切换开销
- **排队放大效应**：少量任务排队就会显著放大整体延时
```java
// 示例：4核CPU，公共池默认3个线程
for (int i = 0; i < 10; i++) {
    list.parallelStream().forEach(item -> {
        // 每个任务执行时间10ms
        Thread.sleep(10);
    });
}
// 结果：后面7个任务需要等待前3个完成，总延时远超预期
```

- **隐蔽性风险**：
  - 代码中没有阻塞操作，看起来"安全"
  - 单次测试可能无法发现问题
  - 随着业务增长，并发量增加时突然暴露
  - 不同模块、不同服务不自觉地共用公共池，相互影响

- **诊断指标**：
  - 监控 `ForkJoinPool.commonPool()` 的活跃线程数、队列长度
  - 观察任务执行时间的 P95/P99 延迟分布
  - 识别并发任务数超过 CPU 核心数的场景

- **防范措施**：
  1. **容量隔离**：关键业务使用独立 `ForkJoinPool`
  2. **流量控制**：限制并发并行流数量
  3. **超时保护**：为异步任务设置超时时间
  4. **熔断降级**：检测到公共池繁忙时降级为串行处理
  5. **容量规划**：预估峰值并发量，配置足够的独立线程池容量

### CountDownLatch 使用规范

- `latch.await()` 必须处理线程中断，否则导致线程僵死
- 正确写法：
```java
try {
    latch.await();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    log.warn("线程被中断", e);
}
```
- Latch 对象应使用局部变量，避免多线程下成员变量被反复赋值的线程安全问题

### 同步与锁

- `synchronized(hash)` 无法正确加锁，每次 hash 计算可能产生新对象
- 应使用固定的锁对象或 `ConcurrentHashMap`

```java
// 错误写法
synchronized (hash) { }  // hash 每次计算可能是新对象

// 正确写法
private final Object lock = new Object();
synchronized (lock) { }
```

### 线程不安全类

- `SimpleDateFormat`、`DecimalFormat` 等类禁止声明为全局静态变量
- 如需性能优化，使用 `ThreadLocal` 包装：
```java
private static final ThreadLocal<SimpleDateFormat> DATE_FORMAT = 
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));
```
- 或使用 Java 8+ 的 `DateTimeFormatter`（线程安全）
- **ThreadLocal 必须清理**：ThreadLocal 未清理会导致内存泄漏，尤其在线程池场景
```java
// 推荐：使用 try-finally 确保 ThreadLocal 清理
try {
    threadLocalVar.set(value);
    // 使用 threadLocalVar
} finally {
    threadLocalVar.remove();
}
```

### 并发模式

- 使用双重检查锁定进行延迟初始化
- 优先使用 ConcurrentHashMap 进行线程安全存储
- 创建新注册表条目时始终同步，以防止竞态条件
- 高并发计数使用 `LongAdder` 而非 `AtomicLong`

### 多线程陷阱

- 静态变量在多线程下存在线程安全问题
- 成员变量被多线程反复赋值存在竞态条件
- 赋值和使用必须原子化或加锁

## 事务管理规范

### Spring 事务管理

- 禁止在 Spring 事务管理体系下自行编码接管事务
- 自行管理事务会扰乱 Spring 事务管理，造成严重事务干扰
- 禁止使用 `Connection.setAutoCommit(false)` 等原始 JDBC 事务操作
- 新启线程不继承事务上下文，需单独处理
- **事务方法必须正确回滚**：默认只回滚 RuntimeException，checked exception 需显式配置
```java
// 回滚所有异常
@Transactional(rollbackFor = Exception.class)

// 回滚指定异常
@Transactional(rollbackFor = {SQLException.class, IOException.class})
```
- **禁止事务中执行 DDL**：DDL 会隐式提交事务，破坏事务完整性
  - TRUNCATE、CREATE、ALTER、DROP 等 DDL 语句会自动提交
  - 事务中途执行 DDL 会导致前面的事务无法回滚

### 审计日志事务

- 审计日志必须使用独立事务，确保记录成功/失败都有日志
- 使用 `@Transactional(propagation = Propagation.REQUIRES_NEW)` 独立事务
- 或使用 try-finally 结构保证审计日志写入：
```java
try {
    businessOperation();
} finally {
    auditLogService.saveLog(logEntry);
}
```
- 审计日志不能依赖业务事务，业务失败回滚时审计日志应保留

### 事务与 DDL

- 事务过程中禁止执行 DDL 命令（如 `TRUNCATE`）
- DDL 会隐式提交事务，破坏事务完整性

## 分层架构规范

### Controller 层职责

- 仅负责接收请求、参数校验、调用 Service、返回响应
- 禁止在 Controller 中编写业务逻辑
- 禁止 Controller 直接操作 DAO，必须通过 Service 层
- Controller 层应只做基础数据校验，业务逻辑下沉到 Service

### Service 层职责

- 封装业务逻辑，协调多个 Repository/DAO
- 提供事务边界，保证业务操作的原子性
- 禁止在 Service 层处理 HTTP 相关对象（如 `HttpServletRequest`、`HttpServletResponse`）
- 禁止在 Service 层处理 JSON 序列化/反序列化
- HTTP/URL/JSON 相关代码应隔离在 Controller 层，避免污染 Service 层

### DAO/Repository 层职责

- 仅负责数据访问，执行 SQL 操作
- 禁止在 DAO 层编写业务逻辑
- 查询结果映射为实体对象返回给 Service
- Handler/Filter 等不应直接操作 DAO，应调用 Service

### 纯内存计算服务

- 纯内存计算不应封装为 Service（Service 默认有事务开销）
- 应封装为工具类（`XxxUtils`）或独立组件
- 如数学计算、日期计算等应提取为工具类

## 性能优化规范

### 缓存策略

- 启动后不变的配置信息，启动时加载一次，后续复用
- 系统日期等变化频率低的数据，切日时维护一次，后续复用
- 禁止在循环或频繁调用的方法中反复读取配置
- 使用 `static final` 或 `@PostConstruct` 初始化配置缓存
- 高成本对象（如反射结果）应缓存复用
- **Pattern 必须预编译**：`Pattern.compile()` 成本极高，禁止在循环或高频方法中调用
```java
// 正确写法
private static final Pattern PHONE_PATTERN = Pattern.compile("^1[3-9]\\d{9}$");

// 错误写法：每次调用都编译
public boolean isValid(String phone) {
    return Pattern.matches("^1[3-9]\\d{9}$", phone);  // ❌
}
```
- **BeanCopier 必须缓存**：`BeanCopier.create()` 涉及字节码生成，禁止重复创建
```java
// 正确写法：使用 ConcurrentHashMap 缓存
private static final ConcurrentHashMap<String, BeanCopier> COPIER_CACHE = new ConcurrentHashMap<>();

public static BeanCopier getCopier(Class<?> src, Class<?> dest) {
    String key = src.getName() + "_" + dest.getName();
    return COPIER_CACHE.computeIfAbsent(key, k -> BeanCopier.create(src, dest, false));
}
```
- **枚举查找必须缓存**：`Enum.values()` 每次调用都会创建新数组，禁止在循环中调用
```java
// 错误写法
for (int i = 0; i < MyEnum.values().length; i++) { }  // ❌ 每次循环都创建数组

// 正确写法
private static final MyEnum[] VALUES = MyEnum.values();  // 缓存
for (MyEnum e : VALUES) { }
```
- **网络接口信息必须缓存**：`NetworkInterface.getNetworkInterfaces()` 耗时秒级，禁止频繁调用
- **拼音转换必须缓存**：汉字转拼音耗时，应使用 LRU 缓存热门词汇

### Redis 缓存优化

- 缓存 key 设计：短小、有意义、避免 JSON 字符串
- 缓存 value：只存必要数据，避免大对象
- 序列化优化：使用 Kryo 等高效序列化工具，避免 JDK 默认序列化
- 合理使用 Redis 数据结构，不仅是 key-value
- 批量操作使用 pipeline

### 批量操作

- 批量保存/更新/删除必须真正批量执行，禁止逐笔操作
- 批量更新替代逐条更新
- 分页读取大数据，避免一次性加载导致 OOM

### 正则表达式优化

- 正则表达式必须预编译，禁止运行时反复编译
- 错误写法：每次调用 `Pattern.matches(regex, input)`
- 正确写法：
```java
private static final Pattern PHONE_PATTERN = Pattern.compile("^1[3-9]\\d{9}$");
// 使用时
PHONE_PATTERN.matcher(input).matches();
```

### 字符串拼接

- 循环中字符串拼接使用 `StringBuilder`，而非 `StringBuffer`
- `StringBuilder` 非线程安全但性能更高，单线程场景优先使用
- `StringBuffer` 线程安全但有同步开销，仅在多线程场景使用

### 字符串处理

- 避免大量使用 `split` 切割获取信息：慢、冗余、可读性差
- 避免频繁使用 `String.format`，非必要不格式化
- 枚举类型避免使用字符串，存在不必要的解析成本

### 集合操作

- 避免频繁 `Array` 与 `List` 互转，造成内存浪费
- 选择合适的查找算法，避免循环遍历代替查找
- 避免对同一集合多次循环
- 禁止三重循环，复杂度极高
- **集合初始化必须指定容量**：避免频繁扩容
```java
// 错误写法：频繁扩容
List<String> list = new ArrayList<>();  // 初始容量10，频繁扩容

// 正确写法：预估容量
List<String> list = new ArrayList<>(expectedSize);
Map<String, String> map = new HashMap<>(expectedSize);
```

### 配置化

- 可配置化的内容禁止写死在代码中
- 如文件路径、URL、超时时间、阈值等应提取到配置文件
- 使用 `@Value` 或 `@ConfigurationProperties` 注入配置

### 面向 JVM GC 编程

- 对内存的管理要谨慎，避免 GC 压力过大
- 减少临时对象创建
- 大对象及时释放
- 使用性能检测工具分析热点

## 数据库与兼容性规范

### SQL 规范

- SQL 语句不宜过长，超过 4000 字符应拆分
- SQL 不应参与业务逻辑判定，只做简单检索
- SQL 语句必须定义为常量
- 固定值必须注释说明

### 分页查询

- 大数据查询必须分页
- 避免一次性加载全部数据导致内存溢出

### 模糊查询

- 禁止使用全模糊查询（`LIKE '%xxx%'`），性能极差
- 至少使用前缀匹配（`LIKE 'xxx%'`）

### Oracle 与 GaussDB 兼容

- SQL 语句应考虑 Oracle 和 GaussDB 双库兼容
- 避免使用 Oracle 特有函数（如 `NVL`、`DECODE`），使用标准 SQL 或双库兼容写法
- 分页查询使用 `ROWNUM`（Oracle）或 `LIMIT`（GaussDB）时需条件判断
- 自增主键策略需适配双库

### SQL 注入防护

- iBatis/MyBatis 中避免使用 `$` 符号拼接 SQL
- 使用 `#` 符号进行参数绑定
- 对用户输入进行校验
- **禁止拼接动态表名、列名**：必须使用白名单校验，禁止直接拼接用户输入
```java
// 错误写法：直接拼接用户输入
String sql = "SELECT * FROM " + tableName;  // ❌ SQL注入风险

// 正确写法：白名单校验
private static final Set<String> ALLOWED_TABLES = Set.of("user", "order", "product");
public void query(String tableName) {
    if (!ALLOWED_TABLES.contains(tableName)) {
        throw new IllegalArgumentException("非法表名");
    }
    String sql = "SELECT * FROM " + tableName;
}
```
- **动态排序字段必须白名单**：ORDER BY 后的字段名禁止直接拼接
- **WHERE 条件拼接必须校验**：禁止将用户输入直接拼接到 WHERE 子句

### 大文件处理

- 文件处理必须考虑大文件场景，避免内存溢出
- 小文件（如 < 10MB）：可使用 `byte[]` 全量读取
- 大文件：使用临时文件 + 流式读取
```java
// 大文件处理示例
try (InputStream is = new FileInputStream(tempFile)) {
    // 流式处理，避免全量加载到内存
}
```
- 文件上传/下载时设置大小限制，防止恶意大文件攻击

## 依赖与库规范

### 库统一

- 项目内 JSON 处理库统一：`fastjson`、`jackson`、`gson` 选其一
- 项目内 Excel 处理库统一：`poi`、`EasyExcel` 选其一
- 避免一个项目内同时存在多个同类库

### 第三方依赖

- 避免深度绑定特定框架（如 `fastjson`、`mybatis`），应进行封装
- 对第三方公司 SDK 进行薄封装，保护自身代码
- 整合开源代码时，优先使用 jar 包方式，而非源码引入
- 敏感资产（密钥、密码）禁止硬编码在代码中
- 配置文件中的敏感信息不应提交到代码库，写入 `.gitignore`

### Lombok 使用

- 根据公司规范决定是否使用
- 如禁止使用，需手动生成 getter/setter/toString 等

## API 使用规范

### JDK 内部 API

- 禁止使用 `com.sun.*` 包下的类
- 这些包是 JDK 内部 API，版本升级时可能变化或移除
- 如需替代方案，使用标准 JDK API 或第三方库

### 公共代码复用

- 明显公共性质的代码必须抽取为公共工具类
- 如月末最后一天、季末最后一天等日期计算
- 禁止在多个类中重复实现相同逻辑
- 使用 Lambda 表达式时注意嵌套深度

### 反射优化

- 反射操作应缓存 `Method`/`Field` 对象
- 使用 Spring 或 CGLib 的 `BeanUtils` 替代手动反射
- 可构建 LRU 缓存加速反射调用
- **String.intern() 慎用**：会占用 JVM 字符串常量池（PermGen/Metaspace），大量调用可能导致内存泄漏
  - 仅用于有限、收敛的枚举值（如业务类型、状态码）
  - 禁止用于用户输入、动态生成的字符串
  - intern() 的字符串会一直占用内存直到 JVM 退出

## 安全规范

### XSS 防护

- 前端不信任后端返回数据
- 用户输入必须转义处理
- 避免直接拼接 HTML

### SQL 注入防护

- 使用参数化查询，禁止字符串拼接 SQL
- 对用户输入进行校验

### 敏感信息保护

- 密钥、密码等敏感信息禁止硬编码
- 配置文件敏感信息不提交代码库
- 日志中禁止输出敏感信息

### 接口防护

- 短信验证码等接口需限制频度，防止短信炸弹
- 文件上传需校验类型和大小

## 代码走查关注点

### 必须修正

- 循环依赖
- **线程安全问题**：
  - `CompletableFuture.runAsync()/supplyAsync()` 未指定独立线程池
  - `parallelStream()` 中包含阻塞操作
  - `ForkJoinPool.commonPool()` 被多个并行流/异步任务竞争，造成任务排队延时
  - 未考虑大量并发任务在公共池中的排队风险
  - 未处理 `CountDownLatch.await()` 的线程中断
- SQL 注入风险
- 敏感信息泄露
- 内存溢出风险

### 应当修正

- 重复代码
- 过大方法/类/文件
- 过深缩进/继承
- 魔幻数值
- 性能问题

### 建议改进

- 代码风格统一
- 注释完善
- 架构优化
- 扩展性提升

## SpotBugs 与 PMD 规则参考

以下规则来自 SpotBugs 和 PMD 静态分析工具，用于代码审查时识别常见问题模式。

### 正确性问题

#### 空指针相关

| 规则ID | 描述 |
|--------|------|
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
|--------|------|
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
|--------|------|
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
|--------|------|
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
|--------|------|
| SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE | 非常量字符串传递给execute方法 |
| SQL_PREPARED_STATEMENT_GENERATED_FROM_NONCONSTANT_STRING | 非常量字符串生成PreparedStatement |
| DMI_CONSTANT_DB_PASSWORD | 硬编码数据库密码 |
| DMI_EMPTY_DB_PASSWORD | 空数据库密码 |
| SQL_BAD_RESULTSET_ACCESS | 尝试访问索引0的结果集字段 |

#### XSS与Web安全

| 规则ID | 描述 |
|--------|------|
| XSS_REQUEST_PARAMETER_TO_SEND_ERROR | Servlet错误页反射型XSS漏洞 |
| XSS_REQUEST_PARAMETER_TO_SERVLET_WRITER | Servlet反射型XSS漏洞 |
| XSS_REQUEST_PARAMETER_TO_JSP_WRITER | JSP反射型XSS漏洞 |
| HRS_REQUEST_PARAMETER_TO_HTTP_HEADER | HTTP响应分割漏洞 |
| PT_ABSOLUTE_PATH_TRAVERSAL | Servlet绝对路径遍历 |
| PT_RELATIVE_PATH_TRAVERSAL | Servlet相对路径遍历 |

#### 加密与密钥安全

| 规则ID | 描述 |
|--------|------|
| HardCodedCryptoKey | 硬编码加密密钥 |
| InsecureCryptoIv | 不安全的加密初始化向量 |
| UNS_UNSAFE_CALL | 调用Unsafe类 |

### 性能问题

#### 资源泄漏

| 规则ID | 描述 |
|--------|------|
| OS_OPEN_STREAM | 方法可能未关闭流 |
| OS_OPEN_STREAM_EXCEPTION_PATH | 异常路径可能未关闭流 |
| ODR_OPEN_DATABASE_RESOURCE | 方法可能未关闭数据库资源 |
| CloseResource | 确保资源关闭 |
| UseTryWithResources | 使用try-with-resources |
| AvoidFileStream | 避免使用FileInputStream/FileOutputStream |

#### 低效操作

| 规则ID | 描述 |
|--------|------|
| DM_STRING_CTOR | 低效的String构造 |
| DM_BOOLEAN_CTOR | 低效的Boolean构造 |
| SBSC_USE_STRINGBUFFER_CONCATENATION | 循环中使用+拼接字符串 |
| WMI_WRONG_MAP_ITERATOR | 低效使用keySet迭代器 |
| StringInstantiation | 避免不必要的String实例化 |
| InefficientStringBuffering | 低效的StringBuffer使用 |
| UseArrayListInsteadOfVector | 使用ArrayList替代Vector |

#### 内存与对象创建

| 规则ID | 描述 |
|--------|------|
| DMI_RANDOM_USED_ONLY_ONCE | Random对象仅使用一次 |
| DM_NEW_FOR_GETCLASS | 仅为了获取class而创建对象 |
| ISC_INSTANTIATE_STATIC_CLASS | 不必要的静态类实例化 |
| SIC_INNER_SHOULD_BE_STATIC | 应该是静态内部类 |
| AvoidInstantiatingObjectsInLoops | 避免循环中创建对象 |

### 并发问题

#### 线程安全

| 规则ID | 描述 |
|--------|------|
| IS2_INCONSISTENT_SYNC | 不一致的同步 |
| IS_FIELD_NOT_GUARDED | 字段未防护并发访问 |
| VO_VOLATILE_REFERENCE_TO_ARRAY | volatile数组引用元素非volatile |
| VO_VOLATILE_INCREMENT | volatile字段自增非原子操作 |
| NonThreadSafeSingleton | 非线程安全单例 |
| UseConcurrentHashMap | 使用ConcurrentHashMap |
| DoubleCheckedLocking | 双重检查锁定问题 |

#### 同步问题

| 规则ID | 描述 |
|--------|------|
| DL_SYNCHRONIZATION_ON_SHARED_CONSTANT | 字符串字面量同步 |
| DL_SYNCHRONIZATION_ON_BOOLEAN | Boolean同步 |
| ESYNC_EMPTY_SYNC | 空同步块 |
| UL_UNRELEASED_LOCK | 方法未在所有路径释放锁 |
| AvoidSynchronizedAtMethodLevel | 避免方法级同步 |

#### 线程操作

| 规则ID | 描述 |
|--------|------|
| RU_INVOKE_RUN | 调用run而非start |
| SC_START_IN_CTOR | 构造函数调用Thread.start() |
| WA_NOT_IN_LOOP | wait不在循环中 |
| NO_NOTIFY_NOT_NOTIFYALL | 使用notify而非notifyAll |
| DontCallThreadRun | 不要直接调用Thread.run() |

#### 死锁风险

| 规则ID | 描述 |
|--------|------|
| TLW_TWO_LOCK_WAIT | 持有两个锁时wait |
| SWL_SLEEP_WITH_LOCK_HELD | 持有锁时调用sleep |

### 代码风格

#### 命名规范

| 规则ID | 描述 |
|--------|------|
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
|--------|------|
| UnnecessaryImport | 不必要的导入 |
| UnnecessaryModifier | 不必要的修饰符 |
| ModifierOrder | 修饰符顺序 |
| NoPackage | 缺少包声明 |

#### 代码结构

| 规则ID | 描述 |
|--------|------|
| OnlyOneReturn | 方法应只有一个返回点 |
| ControlStatementBraces | 控制语句大括号 |
| EmptyControlStatement | 空控制语句 |
| UnnecessaryReturn | 不必要的return |
| UnnecessarySemicolon | 不必要的分号 |
| UselessParentheses | 无用的括号 |

### 最佳实践

#### 序列化

| 规则ID | 描述 |
|--------|------|
| SE_NO_SERIALVERSIONID | 可序列化类未定义serialVersionUID |
| SE_NONFINAL_SERIALVERSIONID | serialVersionUID非final |
| SE_NONSTATIC_SERIALVERSIONID | serialVersionUID非static |
| SE_NONLONG_SERIALVERSIONID | serialVersionUID非long |
| SE_BAD_FIELD | 非瞬态非可序列化字段 |
| MissingSerialVersionUID | 缺少serialVersionUID |

#### Clone实现

| 规则ID | 描述 |
|--------|------|
| CN_IMPLEMENTS_CLONE_BUT_NOT_CLONEABLE | 定义clone但未实现Cloneable |
| CN_IDIOM_NO_SUPER_CALL | clone方法未调用super.clone() |
| CloneMethodMustImplementCloneable | clone方法必须实现Cloneable |
| CloneMethodMustBePublic | clone方法必须为public |

#### 异常处理

| 规则ID | 描述 |
|--------|------|
| DE_MIGHT_DROP | 方法可能丢弃异常 |
| DE_MIGHT_IGNORE | 方法可能忽略异常 |
| AvoidCatchingGenericException | 避免捕获泛型异常 |
| PreserveStackTrace | 保留堆栈跟踪 |
| ReturnFromFinallyBlock | finally块中返回 |
| EmptyCatchBlock | 空catch块 |

#### 资源与环境

| 规则ID | 描述 |
|--------|------|
| DM_EXIT | 方法调用System.exit() |
| DM_GC | 显式垃圾回收 |
| AvoidPrintStackTrace | 避免printStackTrace |
| SystemPrintln | 使用System.out.println |
| DoNotCallGarbageCollectionExplicitly | 不要显式调用GC |

#### 集合与数组

| 规则ID | 描述 |
|--------|------|
| DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION | 不要用removeAll清空集合 |
| UseCollectionIsEmpty | 使用isEmpty检查集合 |
| UseEnumCollections | 使用EnumSet/EnumMap |
| ReturnEmptyCollectionRatherThanNull | 返回空集合而非null |
| MethodReturnsInternalArray | 方法返回内部数组 |

### 设计问题

#### 复杂度

| 规则ID | 描述 |
|--------|------|
| CyclomaticComplexity | 圈复杂度过高 |
| CognitiveComplexity | 认知复杂度过高 |
| NPathComplexity | NPath复杂度过高 |
| TooManyMethods | 方法过多 |
| TooManyFields | 字段过多 |
| ExcessiveParameterList | 参数列表过长 |
| ExcessivePublicCount | 公共成员过多 |

#### 耦合与内聚

| 规则ID | 描述 |
|--------|------|
| CouplingBetweenObjects | 对象间耦合度过高 |
| LawOfDemeter | 违反迪米特法则 |
| LooseCoupling | 应使用松耦合类型 |
| GodClass | 上帝类 |
| DataClass | 数据类 |

#### 类设计

| 规则ID | 描述 |
|--------|------|
| AbstractClassWithoutAbstractMethod | 抽象类无抽象方法 |
| UseUtilityClass | 应使用工具类 |
| SingularField | 单例字段 |
| AvoidDeeplyNestedIfStmts | 避免深度嵌套if语句 |

### 易错代码

#### 常见错误模式

| 规则ID | 描述 |
|--------|------|
| DMI_BIGDECIMAL_CONSTRUCTED_FROM_DOUBLE | BigDecimal从double构造精度问题 |
| DMI_BAD_MONTH | 错误的月份常量值 |
| DMI_CALLING_NEXT_FROM_HASNEXT | hasNext调用next |
| RV_ABSOLUTE_VALUE_OF_RANDOM_INT | 随机整数绝对值计算错误 |
| FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER | 与NaN比较永假 |
| AvoidDecimalLiteralsInBigDecimalConstructor | 避免BigDecimal使用double字面量 |
| ComparisonWithNaN | 与NaN比较 |

#### Switch与循环

| 规则ID | 描述 |
|--------|------|
| SF_SWITCH_FALLTHROUGH | switch穿透 |
| SF_DEAD_STORE_DUE_TO_SWITCH_FALLTHROUGH | switch穿透导致死存储 |
| ImplicitSwitchFallThrough | 隐式switch穿透 |
| JumbledIncrementer | 混乱的循环增量 |

#### 赋值与比较

| 规则ID | 描述 |
|--------|------|
| SA_FIELD_SELF_ASSIGNMENT | 字段自赋值 |
| SA_LOCAL_SELF_ASSIGNMENT | 局部变量自赋值 |
| SA_FIELD_SELF_COMPARISON | 字段自比较 |
| DLS_DEAD_LOCAL_STORE | 局部变量死存储 |
| DLS_OVERWRITTEN_INCREMENT | 被覆盖的自增 |
| AssignmentInOperand | 操作数中的赋值 |

#### Finalize问题

| 规则ID | 描述 |
|--------|------|
| FI_EMPTY | 空finalizer应删除 |
| FI_MISSING_SUPER_CALL | finalizer未调用父类finalizer |
| FI_EXPLICIT_INVOCATION | 显式调用finalizer |
| EmptyFinalizer | 空finalizer |
| FinalizeDoesNotCallSuperFinalize | finalizer未调用super.finalize |

### 静态分析工具集成

#### 推荐配置

```xml
<!-- Maven pom.xml 配置示例 -->
<plugin>
    <groupId>com.github.spotbugs</groupId>
    <artifactId>spotbugs-maven-plugin</artifactId>
    <version>4.8.0</version>
    <configuration>
        <effort>Max</effort>
        <threshold>Medium</threshold>
    </configuration>
</plugin>
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-pmd-plugin</artifactId>
    <version>3.21.0</version>
    <configuration>
        <rulesets>
            <ruleset>/rulesets/java/quickstart.xml</ruleset>
        </rulesets>
    </configuration>
</plugin>
```

#### CI 流程集成

- 在 CI 流水线中集成 SpotBugs 和 PMD 检查
- 设置质量门禁，阻止新增问题合并
- 定期分析技术债务，优先处理高危问题