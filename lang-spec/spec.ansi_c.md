# ANSI C 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 静态不可变变量名使用大写
3. 静态可变变量名使用小写
4. 模块设计遵循单一职责原则
5. 优先使用组合而非继承（通过结构体包含）

## 命名约定

- 文件名：小写蛇形命名（`user_service.c`、`user_service.h`）
- 结构体名：小写蛇形命名 + `_t` 后缀（`user_service_t`、`http_request_t`）
- 函数名：小写蛇形命名，模块前缀（`user_service_create`、`http_request_send`）
- 变量名：小写蛇形命名（`user_name`、`item_count`）
- 常量/宏：全大写蛇形命名（`MAX_CONNECTION_COUNT`、`DEFAULT_TIMEOUT_MS`）
- 类型定义：使用 `typedef` 创建类型别名

```c
// 结构体定义
typedef struct user_service {
    int connection_count;
    char* config_path;
} user_service_t;

// 函数命名
int user_service_init(user_service_t* service);
void user_service_destroy(user_service_t* service);
int user_service_get_user(user_service_t* service, int user_id, user_t* out_user);
```

## 头文件规范

- 使用 `#ifndef`/`#define`/`#endif` 保护
- 头文件只声明接口，不暴露实现细节
- 使用 `extern "C"` 支持 C++ 调用

```c
// user_service.h
#ifndef USER_SERVICE_H
#define USER_SERVICE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct user_service user_service_t;

user_service_t* user_service_create(const char* config_path);
void user_service_destroy(user_service_t* service);
int user_service_get_user(user_service_t* service, int user_id, void* out_user);

#ifdef __cplusplus
}
#endif

#endif // USER_SERVICE_H
```

## 内存管理

- 使用 `malloc`/`calloc` 分配，`free` 释放
- 每个分配必须对应一个释放
- 提供 `create`/`destroy` 或 `init`/`fini` 函数对管理资源
- 检查分配返回值是否为 `NULL`
- 使用 `valgrind` 检测内存泄漏

```c
// 创建/销毁模式
user_service_t* user_service_create(const char* config_path) {
    user_service_t* service = (user_service_t*)malloc(sizeof(user_service_t));
    if (service == NULL) {
        return NULL;
    }
    service->config_path = strdup(config_path);
    if (service->config_path == NULL) {
        free(service);
        return NULL;
    }
    return service;
}

void user_service_destroy(user_service_t* service) {
    if (service != NULL) {
        free(service->config_path);
        free(service);
    }
}
```

## 错误处理

- 使用返回值表示错误（0 成功，非 0 失败）
- 使用错误码枚举定义错误类型
- 提供错误消息获取函数

```c
// 错误码定义
typedef enum {
    USER_SERVICE_OK = 0,
    USER_SERVICE_ERR_NULL_PTR = -1,
    USER_SERVICE_ERR_NOT_FOUND = -2,
    USER_SERVICE_ERR_NO_MEMORY = -3,
} user_service_error_t;

// 错误消息
const char* user_service_error_string(int error_code) {
    switch (error_code) {
        case USER_SERVICE_OK: return "Success";
        case USER_SERVICE_ERR_NULL_PTR: return "Null pointer";
        case USER_SERVICE_ERR_NOT_FOUND: return "Not found";
        case USER_SERVICE_ERR_NO_MEMORY: return "No memory";
        default: return "Unknown error";
    }
}

// 使用
int result = user_service_get_user(service, id, &user);
if (result != USER_SERVICE_OK) {
    fprintf(stderr, "Error: %s\n", user_service_error_string(result));
    return result;
}
```

## 代码风格

- 使用 4 空格缩进（或遵循项目配置）
- 左花括号不换行（K&R 风格）
- 最大行长度 80 或 120 字符
- 使用 `clang-format` 格式化代码

```c
int process_data(const char* input, char* output, size_t output_size) {
    if (input == NULL || output == NULL) {
        return USER_SERVICE_ERR_NULL_PTR;
    }
    
    size_t len = strlen(input);
    if (len >= output_size) {
        return USER_SERVICE_ERR_BUFFER_TOO_SMALL;
    }
    
    strncpy(output, input, output_size - 1);
    output[output_size - 1] = '\0';
    return USER_SERVICE_OK;
}
```

## 函数指针与回调

- 使用函数指针实现多态和回调
- 函数指针类型使用 `typedef` 定义

```c
// 回调类型定义
typedef void (*event_callback_t)(int event_type, void* user_data);

typedef struct event_handler {
    event_callback_t on_event;
    void* user_data;
} event_handler_t;

// 注册回调
void event_handler_set_callback(event_handler_t* handler, 
                                 event_callback_t callback, 
                                 void* user_data) {
    handler->on_event = callback;
    handler->user_data = user_data;
}
```

## 并发编程（POSIX）

- 使用 `pthread` 库进行线程操作
- 使用 `pthread_mutex_t` 保护共享数据
- 使用 `pthread_cond_t` 进行线程同步
- 确保锁的正确初始化和销毁

```c
#include <pthread.h>

typedef struct thread_safe_queue {
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    // ... 其他成员
} thread_safe_queue_t;

int thread_safe_queue_init(thread_safe_queue_t* queue) {
    if (pthread_mutex_init(&queue->mutex, NULL) != 0) {
        return -1;
    }
    if (pthread_cond_init(&queue->cond, NULL) != 0) {
        pthread_mutex_destroy(&queue->mutex);
        return -1;
    }
    return 0;
}

void thread_safe_queue_destroy(thread_safe_queue_t* queue) {
    pthread_mutex_destroy(&queue->mutex);
    pthread_cond_destroy(&queue->cond);
}
```

## 测试规范

- 使用简单的测试框架或自行实现
- 测试文件命名：`*_test.c`
- 每个测试函数独立运行
- 测试覆盖率目标 80% 以上

```c
// 简单测试框架
#include <stdio.h>
#include <assert.h>

#define TEST(name) static void test_##name()
#define RUN_TEST(name) do { \
    printf("Running %s...\n", #name); \
    test_##name(); \
    printf("  PASSED\n"); \
} while(0)

TEST(user_service_create) {
    user_service_t* service = user_service_create("config.ini");
    assert(service != NULL);
    user_service_destroy(service);
}

int main() {
    RUN_TEST(user_service_create);
    return 0;
}
```

## 签名

---
**ANSI C编码规范版本**：1.2.0  
**最后更新**：2025-01-01  
**规则文件**：${AI_SPEC_ROOT}/lang-spec/spec.ansi_c.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.ansi_c.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级C项目、嵌入式系统、高性能系统
