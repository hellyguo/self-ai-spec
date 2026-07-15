# ANSI C 代码审查规则

## 企业级项目专项审查

基于企业级C项目常见问题，扩展以下专项检查点，适用于代码审查和设计文档生成：

### 1. SQL 拼接点审查

**问题描述**：C语言中使用字符串拼接构建SQL语句，存在SQL注入风险。
**检测方法**：

```c
// 危险模式：sprintf/strcat拼接SQL
char sql[256];
sprintf(sql, "SELECT * FROM users WHERE id = %s", userInput); // 直接拼接
```

**审查要点**：

1. 是否存在字符串拼接SQL语句
2. 用户输入是否直接拼入SQL
3. 是否使用参数化查询或预编译语句
4. SQL语句长度是否受控

**重构建议**：

- 使用数据库API的参数化查询（如MySQL C API的 `mysql_stmt_prepare`）
- 实施输入验证和转义（如 `mysql_real_escape_string`）
- 使用查询构建器库避免手动拼接
- 限制动态SQL生成范围

### 2. sprintf 潜在溢出审查

**问题描述**：使用 `sprintf`、`strcpy`、`strcat` 等不安全的C函数导致缓冲区溢出。
**检测方法**：

```c
// 缓冲区溢出风险
char buffer[64];
sprintf(buffer, "User: %s, Age: %d", name, age); // 长度未检查

char dest[32];
strcpy(dest, source); // 未检查源长度
```

**审查要点**：

1. 是否使用已弃用的不安全函数
2. 缓冲区大小是否足够容纳格式化结果
3. 是否对输入长度进行校验
4. 是否存在off-by-one错误

**重构建议**：

- 使用 `snprintf` 替代 `sprintf`
- 使用 `strncpy` 并手动添加空终止符
- 实施边界检查宏或包装函数
- 使用安全的字符串处理库

### 3. 嵌套循环查询审查

**问题描述**：循环内嵌套数据库查询，导致O(n²)复杂度或N+1查询问题。
**检测方法**：

```c
// N+1查询问题
for (int i = 0; i < userCount; i++) {
    User* user = getUserById(i); // 每次循环发起查询
    processUser(user);
}

// 循环内连表查询
for (int i = 0; i < orderCount; i++) {
    User* user = getUser(orders[i].userId); // 重复查询相同用户
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

### 4. 敏感字段输出审查

**问题描述**：密码、密钥、令牌等敏感信息被记录到日志或输出到调试信息。
**检测方法**：

```c
// 敏感信息泄露
log_debug("Password: %s", password); // 明文记录到日志
printf("API Key: %s\n", apiKey); // 输出到控制台
```

**审查要点**：

1. 敏感信息是否被记录到日志文件（所有日志级别）
2. 调试信息是否包含敏感数据
3. 内存中的敏感数据是否被安全清除（使用memset清零）
4. 是否硬编码敏感信息在源代码中
5. 是否使用安全字符串处理函数

**重构建议**：

- 使用安全日志宏过滤敏感字段（自动替换为`****`）
- 实现敏感数据封装函数（自动清除内存）
- 使用加密存储敏感信息
- 实施代码审查规则禁止硬编码密钥
- 敏感数据只通过安全通道传输（环境变量、密钥管理服务）

### 5. 硬编码业务关键字审查

**问题描述**：业务逻辑中的状态码、类型标识等硬编码为魔数或魔法字符串。
**检测方法**：

```c
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
- 使用配置文件和常量头文件
- 实施命名规范：全大写+下划线

### 6. 代码分支复杂度审查

**问题描述**：函数分支过多，圈复杂度高，可读性和可测试性差。
**检测方法**：

```c
// 高圈复杂度示例
void process_order(order_t* order) {
    if (order->type == TYPE_A) {
        if (order->status == STATUS_NEW) {
            // ... 多层嵌套
        } else if (order->status == STATUS_PROCESSING) {
            // ...
        }
    } else if (order->type == TYPE_B) {
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

- 使用函数指针表替代复杂条件分支
- 提取条件判断为独立函数
- 使用状态机模式
- 实施圈复杂度检查（McCabe < 15）

### 7. 算法实现缺陷审查

**问题描述**：算法实现存在逻辑错误、边界条件处理不当、效率低下问题。
**检测方法**：

```c
// 算法缺陷示例
int binary_search(int arr[], int n, int target) {
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

### 8. 表结构设计审查

**问题描述**：数据库表设计不合理，影响查询性能和扩展性。
**检测方法**：

```sql
-- 设计问题示例
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    product_details TEXT, -- JSON blob，难以查询
    created_at DATETIME,
    INDEX idx_user (user_id) -- 单字段索引
);
```

**审查要点**：

1. 表是否满足第三范式（3NF）
2. 索引设计是否合理（覆盖索引、联合索引）
3. 字段类型选择是否适当
4. 是否缺少必要的约束（外键、非空）
5. 大字段（BLOB/TEXT）是否单独存储

**重构建议**：

- 实施数据库规范化（1NF, 2NF, 3NF）
- 设计覆盖常用查询的索引
- 使用合适的数据类型（INT vs BIGINT）
- 分离热数据和冷数据
- 实施分表分库策略

### 9. Makefile 构建体系审查

**问题描述**：Makefile构建脚本配置不当，导致编译问题、依赖管理混乱。
**检测方法**：

```makefile
# Makefile配置问题

# 硬编码编译器路径
CC = /usr/bin/gcc  # 应使用环境变量

# 未定义标准规则
all: app  # 缺少clean、install等

# 未处理头文件依赖
app: main.c util.c  # 未列出.h文件

# 未设置编译标志
CFLAGS =  # 应包含-Wall -Wextra等
```

**审查要点**：

1. 是否使用标准Makefile结构
2. 依赖管理是否恰当（头文件依赖）
3. 编译选项是否合理（调试/发布配置）
4. 是否支持交叉编译
5. 安装规则是否完整

**重构建议**：

- 使用自动依赖生成（-MMD -MP）
- 实现依赖版本管理
- 添加测试目标和安装目标
- 支持多种构建类型（Debug/Release）
- 使用pkg-config管理外部依赖

### 10. 运维脚本体系审查

**问题描述**：部署、监控、备份脚本存在安全风险、健壮性不足、可维护性差。
**检测方法**：

```bash
#!/bin/bash
# 问题脚本示例

# 硬编码密码
DB_PASSWORD="secret123" # 明文密码

# 未处理错误
rm -rf /tmp/* # 可能失败但继续执行

# 权限问题
chmod 777 /app/data # 过度授权
```

**审查要点**：

1. 脚本是否包含硬编码的敏感信息
2. 错误处理是否充分（set -e, trap）
3. 权限设置是否最小化
4. 是否缺少输入验证
5. 日志记录是否完整

**重构建议**：

- 使用环境变量或密钥管理服务
- 实施严格的错误处理：`set -euo pipefail`
- 添加输入参数验证
- 实现详细的日志记录
- 编写单元测试和集成测试

### 11. 内存泄漏和资源管理审查

**问题描述**：未正确释放内存、文件句柄、数据库连接等资源。
**检测方法**：

```c
// 内存泄漏示例
char* buffer = malloc(1024);
// ... 使用buffer
// 缺少free(buffer)

// 文件句柄泄漏
FILE* fp = fopen("data.txt", "r");
// ... 读取文件
// 缺少fclose(fp)

// 数据库连接泄漏
MYSQL* conn = mysql_init(NULL);
mysql_real_connect(conn, host, user, pass, db, 0, NULL, 0);
// ... 使用连接
// 缺少mysql_close(conn)
```

**审查要点**：

1. 每个malloc/calloc是否都有对应的free
2. 每个fopen是否都有对应的fclose
3. 每个数据库连接是否都正确关闭
4. 异常路径下的资源是否被释放
5. 是否使用RAII模式管理资源

**重构建议**：

- 使用goto清理模式处理复杂资源管理
- 实现资源管理器封装类
- 使用valgrind进行内存泄漏检测
- 添加资源引用计数
- 实施严格的资源获取/释放配对检查

### 12. 指针安全审查

**问题描述**：空指针解引用、悬垂指针、未初始化指针使用等安全问题。
**检测方法**：

```c
// 空指针解引用
char* ptr = NULL;
*ptr = 'a';  // 运行时错误

// 悬垂指针
char* get_local_ptr() {
    char local[100];
    return local;  // 返回局部变量指针
}

// 未初始化指针
int* p;
*p = 10;  // 使用未初始化的指针
```

**审查要点**：

1. 指针在使用前是否检查是否为NULL
2. 是否返回局部变量的地址
3. 指针是否在使用前初始化
4. 是否释放后继续使用指针
5. 是否存在类型转换导致的指针对齐问题

**重构建议**：

- 实施严格的NULL指针检查
- 避免返回局部变量指针
- 使用静态分析工具检测指针问题
- 实施指针生命周期管理
- 使用智能指针模式（引用计数）

### 13. 时钟回拨攻击审查（金融系统必查）

**问题描述**：使用 `gettimeofday()` 或 `time()` 进行超时计算，受NTP同步和系统时间修改影响，时钟回拨可能导致超时逻辑失效。

**适用场景**：

- 高性能低延时系统（金融报价、交易系统、高频交易）
- 分布式锁控、主从选举、心跳检测
- 任何依赖时间间隔判断的分布式系统

**检测方法**：

**C危险模式**：

```c
struct timeval start;
gettimeofday(&start, NULL); // 受系统时钟影响
// ... 业务逻辑
struct timeval now;
gettimeofday(&now, NULL);
long elapsed = (now.tv_sec - start.tv_sec) * 1000 + 
               (now.tv_usec - start.tv_usec) / 1000; // 可能为负数
if (elapsed >= timeout) {
    trigger_election(); // 可能永远不触发
}
```

**审查要点**：

1. 检查超时计算、心跳检测、选举超时是否使用墙钟时间
2. `gettimeofday()` 是否用于间隔测量
3. 时间差计算是否可能为负数
4. 是否存在 `elapsed >= timeout` 判断逻辑

**技术原理**：

| API | 时间基准 | 受时钟回拨影响 | 适用场景 |
| ----- | --------- | --------------- | ---------- |
| `gettimeofday()` | 墙钟时间 | ✅ 受影响 | 绝对时间 |
| `clock_gettime(CLOCK_REALTIME)` | 墙钟时间 | ✅ 受影响 | 绝对时间 |
| `clock_gettime(CLOCK_MONOTONIC)` | 单调时钟 | ❌ 不受影响 | 间隔测量 |
| `clock_gettime(CLOCK_MONOTONIC_RAW)` | 原始单调时钟 | ❌ 不受影响 | 高精度间隔测量 |

**重构建议**：

**C正确模式**：

```c
#include <time.h>

struct timespec last_heartbeat;
clock_gettime(CLOCK_MONOTONIC, &last_heartbeat);

struct timespec now;
clock_gettime(CLOCK_MONOTONIC, &now);
long elapsed_ms = (now.tv_sec - last_heartbeat.tv_sec) * 1000 + 
                  (now.tv_nsec - last_heartbeat.tv_nsec) / 1000000;
if (elapsed_ms >= timeout) {
    trigger_election();
}
```

**注意**：

- `CLOCK_MONOTONIC` 是单调时钟，不受系统时间调整影响
- 日志时间戳仍应使用 `gettimeofday()` 获取可读时间
- 金融系统必须使用单调时钟防止时钟回拨攻击
- 对于嵌入式系统，可能需要硬件支持的单调计数器

### 14. 禁止无限循环审查

**问题描述**：使用 `while(1)` 或 `for(;;)` 创建无限循环，缺少明确的退出条件。

**检测方法**：

- C：`while (1)`、`for (;;)`
- 所有语言中都禁止使用 `while(true)` / `while(1)` / `for(;;)` / `while True`

**审查要点**：

1. 必须使用明确的退出条件变量
2. 必须考虑异常路径下的优雅退出机制
3. 长时间运行的循环必须有超时保护
4. 循环退出应确保资源正确释放

**重构建议**：

**C示例**：

```c
// 使用条件变量 + 线程同步
volatile int running = 1;
while (running) {
    struct timespec timeout;
    clock_gettime(CLOCK_REALTIME, &timeout);
    timeout.tv_sec += 1;  // 1秒超时
    
    pthread_cond_timedwait(&worker->cond, &worker->lock, &timeout);
    // 处理任务
}
```

**核心原则**：

- **可控制性**：循环必须能被外部停止
- **资源安全**：退出时必须清理资源
- **异常处理**：异常路径也要能正常退出
- **线程友好**：支持线程中断和超时机制

### 15. Logger 参数空指针风险审查

**问题描述**：在日志输出中直接调用可能为 NULL 的函数或访问可能为 NULL 的指针，导致二次异常。尤其在错误处理块内，二次异常会逃逸到外层导致程序崩溃。

**检测方法**：

- C：`log_error("错误: %s", obj->name)`，obj可能为NULL

**审查要点**：

1. 检查日志参数中是否调用了可能为 NULL 的函数指针
2. 判断该指针是否可能为 NULL（函数返回值、查找结果）
3. 特别关注错误处理块内的日志输出
4. 指针是否在调用前已判空

**重构建议**：

**C示例**：

```c
struct object* obj = get_object();
if (obj == NULL) {
    log_warn("对象为空");
    return;
}
if (process_object(obj) != 0) {
    log_error("处理失败, 名称: %s", obj->name);
}
```

**注意**：此检查项为**参考级别**，不强制要求修复。原因：

1. 静态分析可能无法准确判断指针是否为 NULL
2. 需要结合业务逻辑上下文判断
3. 建议在代码审查时人工确认风险

## 通用规则引用

ANSI C代码审查还应参考以下通用规则：

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

1. 内存泄漏和缓冲区溢出
2. 指针安全和悬垂指针
3. 线程安全和竞争条件
4. SQL注入和敏感数据泄露
5. Makefile构建体系安全问题

### 建议改进（中优先级）

1. 代码结构和模块化设计
2. 性能优化和算法效率
3. 错误处理和安全退出
4. 代码可维护性和可移植性

### 参考建议（低优先级）

1. 命名规范一致性
2. 代码格式和注释质量
3. 文档完整性和准确性

## 签名

---
**ANSI C代码审查规则版本**：1.2.0  
**最后更新**：2025-01-01  
**规则来源**：${AI_SPEC_ROOT}/lang-spec/spec.ansi_c.md  
