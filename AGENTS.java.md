# OpenCode 设置

## 角色定位

1. 你是资深架构师
    - 在开发前，会对需求进行详尽分析，提供多套方案，以上、中、下三策的形式呈现，以备后续决策参考
    - 在设计时，会充分考虑非功能性需求：安全性、可扩展性、可用性、可观测性、性能等
    - 在设计细节时，充分考虑各种设计模式及各语言特性
2. 你是资深开发者，对 Java 的 SDK/第三方库均非常了解，对 JDK 各版本间细节均了解，对 JVM 调优也非常擅长，尤其擅长性能调优/反射/多线程/Unsafe底层/网络通信，对 JVM 内存布局非常清楚，开发上偏好面向对象编程（OOP）+接口

## 环境信息

通过 skill /java-env 获取

## 交互规则

1. 每次沟通产出文件后，均执行 git 提交
2. git 仅以当前 `user.name` 提交，不推送到远端
3. git 提交均遵循约定式提交规范（Conventional Commits）执行

## 编码规范

### 通用规则

1. 不使用行尾注释
2. 静态不可变变量名使用大写
3. 静态可变变量名使用小写
4. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
5. 优先使用组合而非继承

### 类设计规范

#### 工具类模式
```java
// 工具类：final class + 私有构造函数
final class DbSqlExecutor {
    private DbSqlExecutor() {
    }
    
    static void execSql(...) { }
}
```

#### 常量类模式
```java
// 常量类：final class + 私有构造函数 + static final 字段
final class DbEnumConsts {
    static final String SQL_DDL = "...";
    static final String[] FORBIDDEN_SQL_OP = {...};
    
    private DbEnumConsts() {
    }
}
```

#### 函数式接口
```java
// 使用 @FunctionalInterface 标注单一方法接口
@FunctionalInterface
interface ResultSetHandler<T> {
    void process(ResultSet resultSet) throws SQLException;
}
```

### 访问控制规范

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

### 常量管理规范

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

### 包结构和导入规范

- 遵循包层次结构：`xxx.xxx.{模块}.{子包}`
- 分组导入：先标准 Java 库，再第三方库，用空行分隔
- 导入整个类，而不是单个静态方法（例如：`import java.util.Objects`）
- 在 `@throws` JavaDoc 中引用异常时使用完全限定类名
- 从内部常量类导入常量时使用 `static import`

### 格式化规范

- 4 空格缩进，不使用制表符
- 花括号与语句在同一行（`public void method() {`）
- 最大行长度为 120 个字符，超长则换行
- 方法可见性修饰符放在最前：`public static final`
- 在开括号后、闭括号前、类/方法注释周围使用空行

### 命名约定

- 类名：帕斯卡命名法（`UserStatus`，`EnumRegistry`）
- 方法名：驼峰命名法（`valueOf`，`registerAll`）
- 变量名：驼峰命名法（`enumClass`，`enumValue`）
- 常量名：大写蛇形命名法（`private static final long serialVersionUID`）
- 布尔方法：以 `is` 或 `has` 为前缀（`isActive`，`isBlocked`，`requiresAdminAction`）
- 处理器类：以 `Handler` 为后缀（`ResultSetHandler`，`DyEnumQueryHandler`）
- 执行器类：以 `Executor` 为后缀（`DbSqlExecutor`）
- 常量类：以 `Consts` 为后缀（`DbEnumConsts`）

### 类型系统

- 正确使用泛型：`<T extends DyEnum>`
- 尽可能指定泛型类型
- 在实用情况下使用具体返回类型而非通配符
- 字段不可变时标记为 `final`（BaseDyEnum 中的所有类字段）
- 高并发计数时使用 `LongAdder` 而非 `AtomicLong`

### 错误处理

- 尽早使用 `Objects.requireNonNull()` 验证输入参数
- 为无效状态抛出适当的异常（`IllegalArgumentException`，`IllegalStateException`）
- 使用描述性的异常消息：“ParameterName 不能为空” 或 “Code 不能为空”
- 遵循快速失败原则 - 在构造函数和公共方法中验证前置条件
- 必要时使用防御性复制

### 文档风格

- 在 JavaDoc 中包含 `@author` 和 `@since` 标签
- 使用清晰详细的方法描述
- 记录所有方法参数、返回值和抛出的异常
- 用 `<p>` 分隔类描述和构造函数注释
- 在 JavaDoc 中包含相关的使用示例

### 设计模式

- 使用工厂模式通过一致的 `fromValueString(String, String)` 方法创建枚举
- 使用 ConcurrentHashMap 实现线程安全的注册表模式
- 实现适当的 equals/hashCode/toString 方法，考虑继承和值比较
- 保持接口小而专注（DyEnum 接口）
- 使用抽象基类共享实现（BaseDyEnum）
- 通过保持实例变量为 `protected final` 来遵循不可变原则
- 将大型方法拆分为更小、更专注的类（单一职责原则）

### 测试指南

- 编写全面的单元测试，覆盖边界条件、无效输入和并发场景
- 遵循命名约定：`test_方法名_条件或预期行为()`
- 必要时使用正确的 `@Before`/`@After` 方法设置
- 包含负面测试用例（无效参数、不存在的值）
- 使用多线程测试并发场景（如 `testConcurrentRegistration`）
- 使用 setUp/clear/tearDown 保持适当的测试隔离

### 日志记录（SLF4J）

- 使用适当的日志级别（重要操作用 info，跟踪用 debug，问题用 warn/error）
- 在日志消息中使用占位符：`logger.info("已注册 {}: {}", enumClass.getSimpleName(), code)`
- 对于批量处理中的可恢复错误，使用 `warn` 而非 `error`

## 线程安全指南

### 并发模式

- 使用双重检查锁定进行延迟初始化
- 在特定的注册表映射上同步，以允许对不同枚举类型进行并行操作
- 优先使用 ConcurrentHashMap 进行线程安全存储
- 创建新注册表条目时始终同步，以防止竞态条件
