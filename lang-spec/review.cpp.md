# C++ 代码审查规则
## 企业级项目专项审查

基于企业级C++项目常见问题，扩展以下专项检查点，适用于代码审查和设计文档生成：

### 1. C++ 异常空处理审查

**问题描述**：C++异常被捕获后仅打印日志，没有恢复或传播处理。
**检测方法**：

```cpp
// 检测模式：try-catch块中仅有日志输出
try {
    // 业务逻辑
} catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl; // 仅打印
    // 缺少：return、throw、recovery处理
}
```

**审查要点**：
1. 异常类型是否被正确区分（std::exception vs 自定义异常）
2. 是否仅打印日志而无后续处理
3. 资源是否在异常路径下正确释放
4. 是否应该重新抛出或传播异常

**重构建议**：
- 使用异常层次结构（如 `NetworkException`、`FileException`）
- 添加异常恢复策略（重试、降级、默认值）
- 实现 RAII 确保资源安全释放
- 重要异常应重新抛出或返回错误码

### 2. C++ 异常仅打日志审查

**问题描述**：异常被吞噬，仅记录日志，业务逻辑继续执行导致未定义行为。
**检测方法**：

```cpp
// 危险模式：catch-all 异常处理
try {
    doCriticalOperation();
} catch (...) { // 捕获所有异常
    LOG_ERROR("Unknown error occurred"); // 仅打日志
    // 业务继续执行，状态可能已损坏
}
```

**审查要点**：
1. `catch (...)` 是否合理使用
2. 日志级别是否适当（ERROR vs WARNING）
3. 异常后状态是否被重置
4. 是否应终止进程而非继续执行

**重构建议**：
- 避免使用 `catch (...)` 除非在最外层
- 异常后应重置对象状态或抛出
- 致命异常应调用 `std::terminate()` 或 `std::abort()`
- 实现异常安全等级（basic、strong、nothrow）

### 3. SQL 拼接点审查

**问题描述**：C++中使用字符串拼接构建SQL语句，存在SQL注入风险。
**检测方法**：

```cpp
// 危险模式：字符串拼接SQL
std::string sql = "DELETE FROM orders WHERE status = '" + status + "'";
```

**审查要点**：
1. 是否存在字符串拼接SQL语句
2. 用户输入是否直接拼入SQL
3. 是否使用参数化查询或预编译语句
4. SQL语句长度是否受控

**重构建议**：
- 使用数据库API的参数化查询
- 使用ORM库避免手动拼接
- 实施输入验证和转义
- 限制动态SQL生成范围

### 4. sprintf 潜在溢出审查

**问题描述**：使用 `sprintf`、`strcpy`、`strcat` 等不安全的C函数导致缓冲区溢出。
**检测方法**：

```cpp
// 缓冲区溢出风险
char buffer[64];
sprintf(buffer, "User: %s, Age: %d", name, age); // 长度未检查
```

**审查要点**：
1. 是否使用已弃用的不安全函数
2. 缓冲区大小是否足够容纳格式化结果
3. 是否对输入长度进行校验
4. 是否存在off-by-one错误

**重构建议**：
- 使用 `snprintf` 替代 `sprintf`
- C++推荐使用 `std::string` 和 `std::stringstream`
- 使用 `std::string::c_str()` 获取C风格字符串
- 实施边界检查宏或包装函数

### 5. 嵌套循环查询审查

**问题描述**：循环内嵌套数据库查询，导致O(n²)复杂度或N+1查询问题。
**检测方法**：

```cpp
// N+1查询问题
for (int i = 0; i < userCount; i++) {
    User user = getUserById(i); // 每次循环发起查询
    processUser(user);
}
```

**审查要点**：
1. 是否存在循环内数据库操作
2. 相同查询是否被重复执行
3. 是否可以使用批量查询优化
4. 查询结果是否可以被缓存

**重构建议**：
- 使用批量查询：`SELECT * FROM users WHERE id IN (...)`
- 实现查询缓存（LRU缓存）
- 使用JOIN替代多次查询
- 预加载相关数据

### 6. 敏感字段输出审查

**问题描述**：密码、密钥、令牌等敏感信息被记录到日志或输出到调试信息。
**检测方法**：

```cpp
// 敏感信息泄露
LOG_DEBUG("Password: " + password); // 明文记录到日志
std::cout << "API Key: " << apiKey; // 输出到控制台
```

**审查要点**：
1. 敏感信息是否被记录到日志文件（所有日志级别）
2. 调试信息是否包含敏感数据
3. 内存中的敏感数据是否被安全清除
4. 是否硬编码敏感信息在源代码中

**重构建议**：
- 使用安全日志宏过滤敏感字段（自动替换为`****`）
- 实现敏感数据封装类（自动清除内存）
- 使用加密存储敏感信息
- 敏感数据只通过安全通道传输（环境变量、密钥管理服务）

### 7. 硬编码业务关键字审查

**问题描述**：业务逻辑中的状态码、类型标识等硬编码为魔数或魔法字符串。
**检测方法**：

```cpp
// 魔数问题
if (status == 1) { // 1代表什么？
    // ...
}

// 魔法字符串
const char* type = "VIP_USER"; // 多处重复
```

**审查要点**：
1. 是否存在硬编码的数值常量
2. 是否存在重复的字符串常量
3. 业务逻辑是否分散在多处
4. 枚举或常量定义是否完整

**重构建议**：
- 使用枚举替代魔数：`enum UserStatus { ACTIVE = 1, INACTIVE = 2 }`
- 集中定义字符串常量
- 使用配置文件和常量类
- 实施命名规范：全大写+下划线

### 8. 代码分支复杂度审查

**问题描述**：函数分支过多，圈复杂度高，可读性和可测试性差。
**检测方法**：

```cpp
// 高圈复杂度示例
void processOrder(Order& order) {
    if (order.type == TYPE_A) {
        if (order.status == STATUS_NEW) {
            // ... 多层嵌套
        } else if (order.status == STATUS_PROCESSING) {
            // ...
        }
    } else if (order.type == TYPE_B) {
        // ... 更多分支
    }
    // 总分支数 > 10
}
```

**审查要点**：
1. 单个函数分支数是否超过10个
2. 嵌套深度是否超过4层
3. 条件表达式是否过于复杂
4. 是否存在重复的条件逻辑

**重构建议**：
- 使用策略模式替代复杂条件分支
- 提取条件判断为独立方法
- 使用多态和虚函数
- 实施圈复杂度检查（McCabe < 15）

### 9. 算法实现缺陷审查

**问题描述**：算法实现存在逻辑错误、边界条件处理不当、效率低下问题。
**检测方法**：

```cpp
// 算法缺陷示例
int binarySearch(int arr[], int n, int target) {
    int left = 0, right = n; // 应为 n-1
    while (left < right) {
        int mid = (left + right) / 2; // 可能溢出
        // ...
    }
    return -1;
}
```

**审查要点**：
1. 边界条件是否正确处理（空数组、单个元素）
2. 整数运算是否可能溢出
3. 浮点数比较是否使用epsilon
4. 递归深度是否可能过大
5. 算法复杂度是否符合预期

**重构建议**：
- 添加单元测试覆盖边界条件
- 使用安全的整数运算函数
- 实现算法正确性证明（注释说明）
- 进行复杂度分析和性能测试

### 10. CMake 构建体系审查

**问题描述**：CMake构建脚本配置不当，导致编译问题、依赖管理混乱。
**检测方法**：

```cmake
# CMake配置问题
project(MyApp)

# 硬编码路径
include_directories("/usr/local/include") # 应使用find_package

# 全局编译选项
set(CMAKE_CXX_FLAGS "-O2 -Wall") # 影响所有目标

# 依赖管理不当
add_executable(app main.cpp util.cpp) # 未分离库
```

**审查要点**：
1. 是否使用现代CMake（3.x+）
2. 依赖管理是否恰当（find_package vs pkg-config）
3. 编译选项是否合理（调试/发布配置）
4. 是否支持交叉编译
5. 安装规则是否完整

**重构建议**：
- 使用目标属性替代全局设置
- 实现依赖版本管理
- 添加测试目标和安装目标
- 支持多种构建类型（Debug/Release/RelWithDebInfo）
- 使用CPack生成安装包

### 11. 时钟回拨攻击审查（金融系统必查）

**问题描述**：使用 `std::chrono::system_clock` 进行超时计算，受NTP同步和系统时间修改影响，时钟回拨可能导致超时逻辑失效。

**适用场景**：
- 高性能低延时系统（金融报价、交易系统、高频交易）
- 分布式锁控、主从选举、心跳检测
- 任何依赖时间间隔判断的分布式系统

**检测方法**：

**C++危险模式**：
```cpp
auto start = std::chrono::system_clock::now(); // 受系统时钟影响
// ... 业务逻辑
auto elapsed = std::chrono::system_clock::now() - start; // 可能倒退
if (elapsed >= timeout) {
    triggerElection(); // 可能永远不触发
}
```

**审查要点**：
1. 检查超时计算、心跳检测、选举超时是否使用系统时钟
2. `std::chrono::system_clock` 是否用于间隔测量
3. 时间差计算是否可能为负数
4. 是否存在 `elapsed >= timeout` 判断逻辑

**技术原理**：

| API | 时间基准 | 受时钟回拨影响 | 适用场景 |
|-----|---------|---------------|----------|
| `std::chrono::system_clock` | 墙钟时间 | ✅ 受影响 | 绝对时间、日志时间戳 |
| `std::chrono::steady_clock` | 单调时钟 | ❌ 不受影响 | 间隔测量、超时计算 |
| `gettimeofday()` | 墙钟时间 | ✅ 受影响 | 绝对时间 |
| `clock_gettime(CLOCK_MONOTONIC)` | 单调时钟 | ❌ 不受影响 | 间隔测量 |

**重构建议**：

**C++正确模式**：
```cpp
auto lastHeartbeat = std::chrono::steady_clock::now();

auto elapsed = std::chrono::steady_clock::now() - lastHeartbeat;
auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
if (elapsedMs >= timeout) {
    triggerElection();
}
```

**注意**：
- `steady_clock` 是单调时钟，不受系统时间调整影响
- 日志时间戳仍应使用 `system_clock` 获取可读时间
- 金融系统必须使用单调时钟防止时钟回拨攻击

### 12. 禁止无限循环审查

**问题描述**：使用 `while(true)`、`while(1)` 或 `for(;;)` 创建无限循环，缺少明确的退出条件。

**检测方法**：
- C++：`while (1)`、`for (;;)`
- 所有语言中都禁止使用 `while(true)` / `while(1)` / `for(;;)` / `while True`

**审查要点**：
1. 必须使用明确的退出条件变量
2. 必须考虑异常路径下的优雅退出机制
3. 长时间运行的循环必须有超时保护
4. 循环退出应确保资源正确释放

**重构建议**：

**C++示例**：
```cpp
// 使用 atomic<bool> + RAII 资源管理
std::atomic<bool> running_{true};
while (running_.load()) {
    auto task = queue_.pop();  // 可超时等待
    if (!task) break;
    process(*task);
}
```

**核心原则**：
- **可控制性**：循环必须能被外部停止
- **资源安全**：退出时必须清理资源
- **异常处理**：异常路径也要能正常退出
- **线程友好**：支持线程中断和超时机制

### 13. Logger 参数空指针风险审查

**问题描述**：在日志输出中直接调用可能为 null 的对象方法，导致二次异常。尤其在 catch 块内，二次异常会逃逸到外层导致线程崩溃。

**检测方法**：
- C++：`LOG_ERROR("错误: {}", obj->getName())`，obj可能为nullptr

**审查要点**：
1. 检查日志参数中是否调用了对象方法（如 `obj->getName()`）
2. 判断该对象是否可能为 nullptr（方法返回值、查找结果）
3. 特别关注 catch 块内的日志输出
4. 对象是否在 try 块前已判空

**重构建议**：

**C++示例**：
```cpp
auto obj = getObject();
if (!obj) {
    LOG_WARN("对象为空");
    return;
}
try {
    obj->process();
} catch (...) {
    LOG_ERROR("处理失败, 名称: {}", obj->getName());
}
```

**注意**：此检查项为**参考级别**，不强制要求修复。原因：
1. 静态分析可能无法准确判断对象是否为 nullptr
2. 需要结合业务逻辑上下文判断
3. 建议在代码审查时人工确认风险

## 通用规则引用

C++代码审查还应参考以下通用规则：

### 1. 坏味道分类
参考 `${AI_SPEC_ROOT}/skills/code-review/SKILL.md` 中的"坏味道分类扩展"章节，包括：
- 架构类坏味道（大泥球、分布式单体等）
- 耦合类坏味道（循环依赖、印记耦合等）
- 内聚类坏味道（上帝对象、霰弹式修改等）
- 设计类坏味道（抽象泄露、SOLID违反等）
- 代码类坏味道（重复代码、长方法等）
- 测试类坏味道（AI时代新增）
- 命名类坏味道和复杂度类坏味道

### 2. AI生成代码审查
参考 `${AI_SPEC_ROOT}/skills/code-review/SKILL.md` 中的"AI生成代码特有审查"章节，重点关注：
- 零测试覆盖问题
- 过度复杂化实现
- 安全漏洞审查
- 性能陷阱检测

### 3. 数据库审查
参考 `${AI_SPEC_ROOT}/skills/code-review/SKILL.md` 中的"数据库审查规则"章节，包含：
- SQL安全性审查
- SQL性能审查  
- 表结构设计审查
- 数据库架构审查

## 审查优先级

### 必须修正（高优先级）
1. 内存泄漏和资源管理问题
2. 指针安全和缓冲区溢出
3. 线程安全和并发问题
4. SQL注入和敏感数据泄露

### 建议改进（中优先级）
1. 代码结构和设计问题
2. 性能优化建议
3. 错误处理完善
4. 代码可维护性改进

### 参考建议（低优先级）
1. 命名规范统一
2. 代码格式优化
3. 注释补充完善

## 签名

---
**C++代码审查规则版本**：1.2.0  
**最后更新**：2025-01-01  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.cpp.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.cpp.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级C++项目、高性能系统、嵌入式系统