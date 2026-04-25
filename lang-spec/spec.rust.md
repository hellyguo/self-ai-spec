# Rust 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 静态不可变变量名使用大写
4. 静态可变变量名使用小写
5. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
6. 优先使用组合而非继承

## 命名约定

- 模块名：小写蛇形命名（`user_service`）
- 类型名（struct/enum/trait）：帕斯卡命名法（`UserService`，`HttpRequest`）
- 函数名：小写蛇形命名（`get_user_by_id`，`process_request`）
- 变量名：小写蛇形命名（`user_name`，`item_count`）
- 常量：全大写蛇形命名（`MAX_CONNECTION_COUNT`）
- 静态变量：小写蛇形命名或大写蛇形命名（根据可变性）
- 生命周期参数：短小写字母（`'a`，`'b`，`'ctx`）

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

- 禁止 `unwrap()` 和 `expect()` 在生产代码中使用
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
/// # Panics
///
/// 当结果溢出时会 panic.
pub fn add(a: i32, b: i32) -> i32 {
    a.checked_add(b).expect("溢出")
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
