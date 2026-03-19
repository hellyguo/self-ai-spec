# Java 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 静态不可变变量名使用大写
4. 静态可变变量名使用小写
5. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
6. 优先使用组合而非继承

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

```java
// 推荐
static final String SQL_DML_QUERY = 
    "SELECT ENUM_CLASS, CODE, NAME, DESCRIPTION FROM SYS_ENUM WHERE ENUM_CLASS = ?";

// 禁止
stmt.executeQuery("SELECT * FROM table");  // ❌ 内联SQL
```

## 包结构和导入规范

- 遵循包层次结构：`xxx.xxx.{模块}.{子包}`
- 分组导入：先标准 Java 库，再第三方库，用空行分隔
- 导入整个类，而不是单个静态方法（例如：`import java.util.Objects`）
- 在 `@throws` JavaDoc 中引用异常时使用完全限定类名
- 从内部常量类导入常量时使用 `static import`

## 格式化规范

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

## 类型系统

- 正确使用泛型：`<T extends DyEnum>`
- 尽可能指定泛型类型
- 在实用情况下使用具体返回类型而非通配符
- 字段不可变时标记为 `final`（BaseDyEnum 中的所有类字段）
- 高并发计数时使用 `LongAdder` 而非 `AtomicLong`

## 错误处理

- 尽早使用 `Objects.requireNonNull()` 验证输入参数
- 为无效状态抛出适当的异常（`IllegalArgumentException`，`IllegalStateException`）
- 使用描述性的异常消息："ParameterName 不能为空" 或 "Code 不能为空"
- 遵循快速失败原则 - 在构造函数和公共方法中验证前置条件
- 必要时使用防御性复制

## 文档风格

- 在 JavaDoc 中包含 `@author` 和 `@since` 标签
- 使用清晰详细的方法描述
- 记录所有方法参数、返回值和抛出的异常
- 用 `<p>` 分隔类描述和构造函数注释
- 在 JavaDoc 中包含相关的使用示例

## 设计模式

- 使用工厂模式通过一致的 `fromValueString(String, String)` 方法创建枚举
- 使用 ConcurrentHashMap 实现线程安全的注册表模式
- 实现适当的 equals/hashCode/toString 方法，考虑继承和值比较
- 保持接口小而专注（DyEnum 接口）
- 使用抽象基类共享实现（BaseDyEnum）
- 通过保持实例变量为 `protected final` 来遵循不可变原则
- 将大型方法拆分为更小、更专注的类（单一职责原则）

## 测试指南

- 编写全面的单元测试，覆盖边界条件、无效输入和并发场景
- 遵循命名约定：`test_方法名_条件或预期行为()`
- 必要时使用正确的 `@Before`/`@After` 方法设置
- 包含负面测试用例（无效参数、不存在的值）
- 使用多线程测试并发场景（如 `testConcurrentRegistration`）
- 使用 setUp/clear/tearDown 保持适当的测试隔离

## 日志记录（SLF4J）

- 使用适当的日志级别（重要操作用 info，跟踪用 debug，问题用 warn/error）
- 在日志消息中使用占位符：`logger.info("已注册 {}: {}", enumClass.getSimpleName(), code)`
- 对于批量处理中的可恢复错误，使用 `warn` 而非 `error`
- 调试日志输出对象时，确保对象类重写了 `toString()` 方法，否则只能输出 `Xxx@12345678` 无效信息
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
- 在特定的注册表映射上同步，以允许对不同枚举类型进行并行操作
- 优先使用 ConcurrentHashMap 进行线程安全存储
- 创建新注册表条目时始终同步，以防止竞态条件
- 高并发计数使用 `LongAdder` 而非 `AtomicLong`

## 事务管理规范

### Spring 事务管理

- 禁止在 Spring 事务管理体系下自行编码接管事务
- 自行管理事务会扰乱 Spring 事务管理，造成严重事务干扰
- 禁止使用 `Connection.setAutoCommit(false)` 等原始 JDBC 事务操作

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

### 纯内存计算服务

- 纯内存计算不应封装为 Service（Service 默认有事务开销）
- 应封装为工具类（`XxxUtils`）或独立组件
- 如 `GlMathServiceImpl` 中的数学计算应提取为 `MathUtils`

## 性能优化规范

### 缓存策略

- 启动后不变的配置信息，启动时加载一次，后续复用
- 系统日期等变化频率低的数据，切日时维护一次，后续复用
- 禁止在循环或频繁调用的方法中反复读取配置
- 使用 `static final` 或 `@PostConstruct` 初始化配置缓存

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

### 配置化

- 可配置化的内容禁止写死在代码中
- 如文件路径、URL、超时时间、阈值等应提取到配置文件
- 使用 `@Value` 或 `@ConfigurationProperties` 注入配置

## 数据库与兼容性规范

### Oracle 与 GaussDB 兼容

- SQL 语句应考虑 Oracle 和 GaussDB 双库兼容
- 避免使用 Oracle 特有函数（如 `NVL`、`DECODE`），使用标准 SQL 或双库兼容写法
- 分页查询使用 `ROWNUM`（Oracle）或 `LIMIT`（GaussDB）时需条件判断
- 自增主键策略需适配双库

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

## API 使用规范

### JDK 内部 API

- 禁止使用 `com.sun.*` 包下的类
- 这些包是 JDK 内部 API，版本升级时可能变化或移除
- 如需替代方案，使用标准 JDK API 或第三方库

### 公共代码复用

- 明显公共性质的代码必须抽取为公共工具类
- 如月末最后一天、季末最后一天等日期计算
- 禁止在多个类中重复实现相同逻辑