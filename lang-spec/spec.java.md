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

## 线程与并发规范

### 线程创建与管理

- 禁止使用 `new Thread()` 创建线程，成本极大，性能影响严重
- 必须使用线程池（`ExecutorService`、`ThreadPoolExecutor`）创建线程
- 线程必须命名，方便问题排查：`new ThreadFactory() { ... }` 或 `ThreadBuilder`
- 线程池必须在应用关闭时正确停止，否则造成容器中线程泄漏
- 禁止反复创建线程池，应作为单例或 Spring Bean 复用
- 使用线程池减少线程创建开销

### 线程停止

- 线程必须可停止，不能使用 `while(true)` 无限循环
- 使用 `volatile boolean` 标志位控制循环退出

```java
// 正确写法
private volatile boolean running = true;

public void run() {
    while (running) {
        // do work
    }
}

public void shutdown() {
    running = false;
}
```

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
- 线程安全问题
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