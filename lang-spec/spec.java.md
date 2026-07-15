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
- 参考：<https://dzone.com/articles/log-crlf-injection-with-slf4j>
- 禁止打印大对象，影响性能且无意义

### 异常日志

- 输出异常堆栈必须使用三参数形式：`log.error("msg: {}", e.getMessage(), e)`
- 错误写法：`log.error("msg: {}", e)` 只输出异常类名或消息，无法输出堆栈
- 正确写法：`log.error("msg: {}", e.getMessage(), e)` 可完整输出堆栈信息
- **禁止异常吞没**：catch 块中必须有日志或重新抛出，禁止空 catch 块
- **异常必须处理**：捕获异常后必须有后续处理（重试、通知、降级等），不能只打日志
- **禁止 catch Exception**：应捕获具体异常类型，避免捕获 RuntimeException 等泛型异常

## 线程与并发规范

### 线程创建与管理规范（企业级要求）

#### 1. **禁止直接创建线程**

- **禁止使用 `new Thread()`**：应使用线程池管理线程生命周期
- **禁止使用 `Executors.newCachedThreadPool()`**：无限制创建线程，可能导致OOM
- **正确做法**：使用 `ThreadPoolExecutor` 显式配置线程池参数

```java
// 错误做法：直接创建线程
new Thread(() -> doTask()).start();  // ❌ 禁止

// 错误做法：使用缓存线程池
ExecutorService executor = Executors.newCachedThreadPool();  // ❌ 禁止

// 正确做法：使用有界线程池
private static final ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4, // 核心线程数
    8, // 最大线程数  
    60, // 空闲线程存活时间
    TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100), // 有界队列
    new NamedThreadFactory("business-task"), // 线程命名工厂
    new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
);
```

#### 2. **线程命名要求**

- **所有线程必须命名**：便于问题排查和监控
- **使用自定义 ThreadFactory**：统一线程命名规范

```java
// 线程工厂示例
public class NamedThreadFactory implements ThreadFactory {
    private final AtomicInteger threadNumber = new AtomicInteger(1);
    private final String namePrefix;
    
    public NamedThreadFactory(String poolName) {
        namePrefix = poolName + "-thread-";
    }
    
    @Override
    public Thread newThread(Runnable r) {
        Thread t = new Thread(r, namePrefix + threadNumber.getAndIncrement());
        if (t.isDaemon()) t.setDaemon(false);
        if (t.getPriority() != Thread.NORM_PRIORITY) t.setPriority(Thread.NORM_PRIORITY);
        return t;
    }
}

// 使用命名线程池
ExecutorService executor = Executors.newFixedThreadPool(4, new NamedThreadFactory("data-sync"));
```

#### 3. **线程退出控制**

- **必须提供退出机制**：长时间运行的线程必须有可控的退出方式
- **使用布尔标志或AtomicBoolean控制循环**：避免无限循环
- **必须处理线程中断**：响应中断请求

```java
// 正确做法：可控制退出的线程
public class WorkerThread extends Thread {
    private volatile boolean running = true;
    private final AtomicBoolean stopFlag = new AtomicBoolean(false);
    
    public WorkerThread(String name) {
        super(name); // 线程命名
    }
    
    @Override
    public void run() {
        while (running && !stopFlag.get()) {
            try {
                processTask();
            } catch (InterruptedException e) {
                // 响应中断，优雅退出
                running = false;
                Thread.currentThread().interrupt(); // 恢复中断状态
                break;
            }
        }
        // 清理资源
        cleanup();
    }
    
    public void shutdown() {
        running = false;
        stopFlag.set(true);
        this.interrupt(); // 中断可能阻塞的线程
    }
}
```

#### 4. **长时间运行线程的异常处理**

- **循环内必须捕获 Throwable**：防止线程"跑飞"（因未捕获异常而退出）
- **必须记录异常并继续运行或优雅退出**：不能直接吞掉异常
- **必须有兜底机制**：防止异常导致线程终止影响业务

```java
// 正确做法：长时间运行线程的异常处理
public void run() {
    while (running) {
        try {
            // 业务逻辑
            doBusiness();
            
            // 短暂休眠，防止空转
            try {
                TimeUnit.MILLISECONDS.sleep(100);
            } catch (InterruptedException e) {
                running = false;
                Thread.currentThread().interrupt();
                break;
            }
            
        } catch (Throwable t) {  // 捕获所有异常，包括Error
            // 记录异常，继续运行（或根据策略退出）
            log.error("Worker thread encountered error", t);
            
            // 根据业务决定：继续运行、重启线程或优雅退出
            if (shouldExitOnError(t)) {
                running = false;
                break;
            }
            
            // 避免异常导致无限快速重试
            try {
                TimeUnit.SECONDS.sleep(10); // 重试延迟
            } catch (InterruptedException e) {
                running = false;
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
```

#### 5. **J2EE容器下的线程管理**

- **必须支持优雅停机**：实现 `ServletContextListener` 或 Spring `DisposableBean`
- **确保线程池完全停止**：等待任务完成或设置超时
- **防止线程泄漏**：确保所有线程都能正确终止

```java
// Spring Boot 优雅停机配置
@Configuration
public class GracefulShutdownConfig {
    
    @Bean
    public GracefulShutdown gracefulShutdown() {
        return new GracefulShutdown();
    }
    
    @Bean
    public TomcatServletWebServerFactory tomcatFactory() {
        TomcatServletWebServerFactory factory = new TomcatServletWebServerFactory();
        factory.addConnectorCustomizers(gracefulShutdown());
        return factory;
    }
}

// 线程池优雅停机实现
@Component
public class ThreadPoolManager implements DisposableBean {
    
    private final ExecutorService executorService;
    private volatile boolean shutdownInProgress = false;
    
    @PostConstruct
    public void init() {
        executorService = new ThreadPoolExecutor(...);
    }
    
    @Override
    public void destroy() throws Exception {
        shutdownInProgress = true;
        
        // 1. 停止接受新任务
        executorService.shutdown();
        
        try {
            // 2. 等待现有任务完成（最多30秒）
            if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                // 3. 强制停止未完成的任务
                executorService.shutdownNow();
                
                // 4. 再次等待强制停止
                if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                    log.error("Thread pool did not terminate properly");
                }
            }
        } catch (InterruptedException e) {
            // 5. 重新尝试强制停止
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
```

#### 6. **线程池配置最佳实践**

```java
// 企业级线程池配置模板
public class EnterpriseThreadPool {
    
    // CPU密集型任务
    public static ExecutorService cpuIntensivePool() {
        return new ThreadPoolExecutor(
            Runtime.getRuntime().availableProcessors(), // 核心线程数 = CPU核心数
            Runtime.getRuntime().availableProcessors() * 2, // 最大线程数
            60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(1000),
            new NamedThreadFactory("cpu-intensive"),
            new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }
    
    // IO密集型任务  
    public static ExecutorService ioIntensivePool() {
        return new ThreadPoolExecutor(
            10, // 核心线程数
            50, // 最大线程数
            60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(2000),
            new NamedThreadFactory("io-intensive"),
            new ThreadPoolExecutor.AbortPolicy() // 拒绝时抛出异常
        );
    }
    
    // 定时/调度任务
    public static ScheduledExecutorService scheduledPool() {
        return Executors.newScheduledThreadPool(
            4,
            new NamedThreadFactory("scheduled-task")
        );
    }
}
```

#### 7. **线程泄漏检测与监控**

```java
// 线程泄漏检测工具
public class ThreadLeakDetector {
    
    private static final Map<String, Thread> monitoredThreads = new ConcurrentHashMap<>();
    private static final ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor(
        new NamedThreadFactory("thread-monitor")
    );
    
    static {
        // 每5分钟检查一次线程泄漏
        monitor.scheduleAtFixedRate(() -> {
            try {
                checkThreadLeaks();
            } catch (Exception e) {
                log.error("Thread leak detection failed", e);
            }
        }, 5, 5, TimeUnit.MINUTES);
    }
    
    public static void registerThread(String threadName, Thread thread) {
        monitoredThreads.put(threadName, thread);
    }
    
    public static void unregisterThread(String threadName) {
        monitoredThreads.remove(threadName);
    }
    
    private static void checkThreadLeaks() {
        Map<Thread, StackTraceElement[]> allThreads = Thread.getAllStackTraces();
        for (Map.Entry<String, Thread> entry : monitoredThreads.entrySet()) {
            String threadName = entry.getKey();
            Thread thread = entry.getValue();
            
            if (!allThreads.containsKey(thread)) {
                log.warn("Thread leak detected: {}", threadName);
                // 发送告警、记录堆栈等
            }
        }
    }
}
```

#### 8. **线程安全单例模式**

```java
// 正确的线程安全单例模式（双重检查锁定）
public class ThreadSafeSingleton {
    
    private static volatile ThreadSafeSingleton instance;
    
    private ThreadSafeSingleton() {
        // 私有构造函数
    }
    
    public static ThreadSafeSingleton getInstance() {
        if (instance == null) { // 第一次检查
            synchronized (ThreadSafeSingleton.class) {
                if (instance == null) { // 第二次检查
                    instance = new ThreadSafeSingleton();
                }
            }
        }
        return instance;
    }
}
```

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

### 类初始化死锁（强制禁止）

**问题描述**：JVM 为每个类维护一个初始化锁（`<clinit>`），多线程同时初始化互相依赖的类时，可能导致死锁。Java 标准死锁检测（`ThreadMXBean.findDeadlockedThreads()`）无法检测此类死锁。

**死锁模式**：

| 模式 | 场景 | 死锁原因 |
| -------- | ------ | ------ |
| 父子类初始化 | 父类静态块实例化子类，子类静态块访问父类 | 线程A持有父类锁等待子类，线程B持有子类锁等待父类 |
| 循环依赖 | 类A静态块访问类B，类B静态块访问类A | 线程A持有A锁等待B，线程B持有B锁等待A |
| 静态内部类 | 外部类静态块访问内部类，内部类静态块访问外部类 | 线程A持有外部类锁等待内部类，线程B持有内部类锁等待外部类 |

**禁止的高风险代码模式**：

```java
// 禁止：类A的静态初始化依赖类B
class ClassA {
    static {
        ClassB.someStaticMethod();  // 危险！
    }
}

// 禁止：类B的静态初始化依赖类A
class ClassB {
    static {
        ClassA.someStaticMethod();  // 循环依赖，死锁风险！
    }
}

// 禁止：父子类静态初始化交叉依赖
class Parent {
    static {
        CHILD = new Child();  // 危险！需要初始化Child
    }
}

class Child {
    static {
        int value = Parent.getStaticValue();  // 危险！需要初始化Parent
    }
}

// 禁止：外部类与静态内部类交叉依赖
class OuterClass {
    static {
        StaticInnerClass.getStaticValue();  // 危险！
    }
    
    static class StaticInnerClass {
        static {
            OuterClass.getStaticValue();  // 循环依赖，死锁风险！
        }
    }
}
```

**诊断特征**：

- 堆栈顶有 `<clinit>` 方法调用
- 线程状态显示 RUNNABLE，但实际在等待类初始化锁
- Java 标准死锁检测无法发现

**解决方案**：

1. **避免循环静态初始化依赖**：设计时确保类初始化不形成循环依赖
2. **延迟初始化**：将静态依赖移到实例方法或延迟加载
3. **单一线程初始化**：应用启动时由主线程完成关键类的初始化
4. **重构为依赖注入**：避免静态块中的跨类调用

```java
// 正确写法：延迟初始化
class ClassA {
    private static ClassB instance;
    
    public static ClassB getInstance() {
        if (instance == null) {
            synchronized (ClassA.class) {
                if (instance == null) {
                    instance = new ClassB();
                }
            }
        }
        return instance;
    }
}

// 正确写法：启动时预加载
public class Initializer {
    public static void init() {
        // 主线程单线程初始化所有相关类
        ClassA.getStaticValue();
        ClassB.getStaticValue();
    }
}
```

**审查要点**：

1. 静态初始化块（`static {}`）是否访问其他类的静态成员
2. 静态块中是否实例化其他类（`new OtherClass()`）
3. 是否存在类间的双向静态依赖
4. 父子类、内部类是否存在静态初始化交叉引用

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
- **类初始化死锁风险**：
  - 静态初始化块访问其他类的静态成员
  - 父子类/内外类静态初始化交叉依赖
  - 类间双向静态依赖
- **无限循环风险**：
  - 使用 `while(true)`、`for(;;)` 创建无限循环
  - 循环缺少明确的退出条件，难以优雅停止
  - 线程可能被强制中断，导致资源泄漏
  - 推荐使用明确的退出标志变量
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

## 签名

---
**Java编码规范版本**：1.2.0  
**最后更新**：2025-01-01  
**规则文件**：${AI_SPEC_ROOT}/lang-spec/spec.java.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.java.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Java项目、金融系统、高性能系统
