# Rust 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 静态不可变变量名使用大写
4. 静态可变变量名使用小写
5. 类型与模块设计遵循单一职责原则，大型结构体或模块应拆分为职责明确的小单元
6. 优先使用组合而非继承

## 命名约定

- 模块名：小写蛇形命名（`user_service`）
- 类型名（struct/enum/trait）：帕斯卡命名法（`UserService`，`HttpRequest`）
- 函数名：小写蛇形命名（`get_user_by_id`，`process_request`）
- 变量名：小写蛇形命名（`user_name`，`item_count`）
- 常量：全大写蛇形命名（`MAX_CONNECTION_COUNT`）
- 静态变量：小写蛇形命名或大写蛇形命名（根据可变性）
- 生命周期参数：短小写字母（`'a`，`'b`，`'ctx`）

## 变量声明（高优先级）

- 禁止单行多声明：不得在同一行用分号并列写多条 `let` 声明
- 每个变量独占一行，便于单独注释、调试与版本对比
- 模式解构（`let (a, b) = tuple;`、`if let Some((a, b)) = ...`）是一次赋值的模式匹配，不视为单行多声明

```rust
// 禁止：同一行多条声明
let host = "localhost"; let port = 8080;

// 推荐：每个变量单独一行
let host = "localhost";
let port = 8080;

// 允许：解构是一次赋值的模式匹配
let (width, height) = (1920, 1080);
```

## 所有权与借用

- 理解所有权规则：每个值有唯一所有者，离开作用域自动释放
- 优先使用借用（`&T`）而非移动，减少克隆开销
- 可变借用使用 `&mut T`，同一时刻只能有一个可变引用
- 使用 `Cow<str>` 或 `Cow<[T]>` 延迟克隆

```rust
// 推荐：使用借用
fn process_data(data: &str) -> usize {
    data.len()
}

// 避免：不必要的克隆
fn process_data(data: String) -> usize {
    data.len()
}
```

## 错误处理

- 禁止 `unwrap()` 、`panic()` 和 `expect()` 在生产代码中使用
- 使用 `Result<T, E>` 处理可恢复错误
- 使用 `?` 运算符传播错误
- 使用 `thiserror` 或 `anyhow` 库简化错误定义
- 使用 `Option<T>` 表示可能为空的值

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("用户不存在: {0}")]
    UserNotFound(u64),
    #[error("数据库错误: {0}")]
    DatabaseError(#[from] sqlx::Error),
}

pub fn find_user(id: u64) -> Result<User, AppError> {
    // ...
}
```

## 内存安全

- 遵循 RAII 模式，资源在析构时自动释放
- 使用 `Drop` trait 实现自定义清理逻辑
- 避免内存泄漏，确保资源正确释放
- 使用 `Rc<T>` / `Arc<T>` 实现共享所有权

```rust
use std::sync::Arc;

struct SharedState {
    data: Arc<Vec<u8>>,
}

impl Drop for SharedState {
    fn drop(&mut self) {
        println!("清理资源");
    }
}
```

## 并发与异步

- 使用 `Arc<Mutex<T>>` 或 `Arc<RwLock<T>>` 实现线程安全共享
- 使用 `tokio` 或 `async-std` 运行异步代码
- 使用 `Send` 和 `Sync` trait 标记线程安全类型
- 避免死锁，注意锁的获取顺序

```rust
use std::sync::{Arc, Mutex};
use tokio::sync::RwLock;

// 同步场景
let counter = Arc::new(Mutex::new(0));

// 异步场景
let data = Arc::new(RwLock::new(vec![]));
```

## 文档注释

- 使用 `///` 编写文档注释
- 使用 `//!` 编写模块级文档
- 包含示例代码、参数说明、panic 条件、错误条件

```rust
/// 计算两数之和.
///
/// # Examples
///
/// ```
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// ```
///
/// # Errors
///
/// 当结果溢出时返回 `AddOverflow`.
pub fn add(a: i32, b: i32) -> Result<i32, AddError> {
    a.checked_add(b).ok_or(AddError::AddOverflow)
}
```

## 测试规范

- 单元测试放在同一文件的 `#[cfg(test)]` 模块中
- 集成测试放在 `tests/` 目录
- 使用 `#[test]` 标记测试函数
- 使用 `#[should_panic]` 测试 panic 情况
- 使用 `cargo test` 运行测试

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    #[should_panic(expected = "溢出")]
    fn test_add_overflow() {
        add(i32::MAX, 1);
    }
}
```

## 性能优化

- 使用 `&[T]` 切片而非 `Vec<T>` 作为函数参数
- 使用迭代器而非循环，编译器可优化
- 使用 `Cow` 延迟克隆
- 使用 `Box::leak` 创建 `'static` 生命周期（谨慎使用）
- 使用 `cargo bench` 进行性能测试

```rust
// 推荐：使用切片
fn process(items: &[Item]) -> usize {
    items.len()
}

// 迭代器优于循环
let sum: i32 = (1..=100).sum();
```

## 计算与分支规范

- 尽量预计算：在程序初始化、类初始化、模块初始化等阶段完成可提前确定的计算，减少运行时计算
- 循环内不变量：循环体内每次迭代结果不变的表达式，提取到循环外，仅计算一次
- 整体循环不变量：贯穿整个循环保持不变的量，尽量提取到循环外部，不在循环内计算
- 分支以正向（肯定）阅读为主，尽量不反向（否定），反向条件增加阅读难度

## 签名

---
**Rust编码规范版本**：1.4.0  
**最后更新**：2026-10-23  
**规则文件**：${AI_SPEC_ROOT}/lang-spec/spec.rust.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.rust.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Rust项目、系统编程、高性能服务
