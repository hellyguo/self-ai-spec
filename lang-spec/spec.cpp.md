# C++ 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 静态不可变变量名使用大写
3. 静态可变变量名使用小写
4. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
5. 优先使用组合而非继承

## 命名约定

- 文件名：小写蛇形命名（`user_service.cpp`）或小写短横线命名（`user-service.cpp`）
- 类名/结构体名：帕斯卡命名法（`UserService`，`HttpRequest`）
- 函数名：小写驼峰命名（`getUserById`）或小写蛇形命名（`get_user_by_id`）
- 变量名：小写驼峰命名或小写蛇形命名（`userName` 或 `user_name`）
- 常量：全大写蛇形命名（`MAX_CONNECTION_COUNT`）或 `k` 前缀（`kMaxConnections`）
- 成员变量：`m_` 前缀或 `_` 后缀（`m_count` 或 `count_`）
- 宏定义：全大写蛇形命名（`MAX_BUFFER_SIZE`）

## 现代 C++ 特性

- 使用 C++11/14/17/20 特性提高代码质量
- 优先使用 `auto` 推导类型
- 使用智能指针管理内存（`std::unique_ptr`、`std::shared_ptr`）
- 使用范围 for 循环
- 使用 `constexpr` 编译期计算

```cpp
// 智能指针
auto user = std::make_unique<User>();
auto shared = std::make_shared<Resource>();

// 范围 for
for (const auto& item : items) {
    process(item);
}

// constexpr
constexpr int kBufferSize = 1024;
```

## 内存管理

- 避免裸指针（`new`/`delete`），使用智能指针
- 使用 RAII 管理资源
- 使用 `std::vector` 而非 C 数组
- 避免内存泄漏，确保资源正确释放

```cpp
// 推荐：使用智能指针
class UserService {
public:
    UserService() : m_connection(std::make_unique<DbConnection>()) {}
private:
    std::unique_ptr<DbConnection> m_connection;
};

// 避免：裸指针
class UserService {
    DbConnection* m_connection; // 不推荐
};
```

## 错误处理

- 使用异常处理错误（非性能关键路径）
- 使用 `std::expected`（C++23）或 `std::optional` 表示可能失败的操作
- 避免 C 风格的错误码返回

```cpp
#include <optional>

std::optional<User> findUser(int id) {
    if (id <= 0) {
        return std::nullopt;
    }
    return User{id, "name"};
}

// 使用
if (auto user = findUser(1)) {
    std::cout << user->name << std::endl;
}
```

## 头文件规范

- 使用 `#pragma once` 或传统头文件保护
- 头文件中尽量减少 include，使用前向声明
- 源文件中 include 顺序：对应头文件 -> 系统头文件 -> 第三方库 -> 项目头文件

```cpp
// user_service.h
#pragma once

#include <memory>
#include <string>

class User;  // 前向声明

class UserService {
public:
    std::unique_ptr<User> findUser(const std::string& id);
};
```

## 代码风格

- 使用 4 空格缩进（或遵循项目配置）
- 左花括号不换行（K&R 风格）
- 最大行长度 120 字符
- 使用 `clang-format` 格式化代码

```cpp
class Example {
public:
    void process(int value) {
        if (value > 0) {
            doSomething();
        }
    }
};
```

## 并发编程

- 使用 `std::thread` 创建线程
- 使用 `std::mutex`、`std::lock_guard`、`std::unique_lock` 保护共享数据
- 使用 `std::atomic` 进行原子操作
- 使用 `std::condition_variable` 进行线程同步

```cpp
#include <mutex>
#include <atomic>

class Counter {
    std::atomic<int> m_count{0};
    std::mutex m_mutex;
    
public:
    void increment() {
        m_count.fetch_add(1, std::memory_order_relaxed);
    }
    
    void processWithLock() {
        std::lock_guard<std::mutex> lock(m_mutex);
        // 临界区代码
    }
};
```

## 测试规范

- 使用 Google Test 或 Catch2 作为测试框架
- 测试文件命名：`*_test.cpp` 或 `*_spec.cpp`
- 测试函数命名：`TEST(TestSuite, TestCase)`
- 测试覆盖率目标 80% 以上

```cpp
#include <gtest/gtest.h>

TEST(UserServiceTest, FindUserById) {
    UserService service;
    auto user = service.findUser(1);
    EXPECT_TRUE(user.has_value());
    EXPECT_EQ(user->id, 1);
}
```

## 签名

---
**C++编码规范版本**：1.2.0  
**最后更新**：2025-01-01  
**规则文件**：${AI_SPEC_ROOT}/lang-spec/spec.cpp.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.cpp.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级C++项目、高性能系统、嵌入式系统
