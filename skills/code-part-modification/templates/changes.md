# 修改记录

## 修改1：参数校验增强

- **文件**：src/main/java/.../OrderService.java
- **行号**：45-52
- **修改前**：

```java
public void process(Order order) {
    // 无校验
}
```

- **修改后**：

```java
public void process(Order order) {
    if (order == null || order.getStatus() == null) {
        throw new IllegalArgumentException("订单或状态不能为空");
    }
}
```

- **修改原因**：修复空指针异常
- **影响范围**：仅影响调用方异常处理

## 修改验证

- [ ] 单元测试通过
- [ ] 代码审查通过
- [ ] 无副作用验证通过
