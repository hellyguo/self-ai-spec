# 策略模式重构模板

## 五步法

1. **识别变体** — 找到所有if-else分支，提取变化维度，统计出现频次
2. **定义接口** — 抽象公共行为，定义supports()方法，提供default实现
3. **实现策略** — 每个分支一个策略类，添加@Component注解，实现supports()判断
4. **注入策略** — Service注入List<Strategy>，构建查找方法
5. **替换判断** — 删除if-else，多态调用strategy.method()

## 策略接口设计规范

```java
public interface XxxStrategy {

    boolean supports(String type);

    default void execute(Context ctx) {
        // 默认实现或空
    }

    default boolean isXxx() {
        return false;
    }
}
```

## 策略查找优化

```java
// ❌ 避免：每次遍历
private Strategy getStrategy(String type) {
    return strategies.stream()
        .filter(s -> s.supports(type))
        .findFirst()
        .orElseThrow();
}

// ✅ 推荐：启动时构建Map
private Map<String, Strategy> strategyMap;

@PostConstruct
public void init() {
    strategyMap = strategies.stream()
        .collect(Collectors.toMap(
            Strategy::getType,
            Function.identity()
        ));
}

public Strategy getStrategy(String type) {
    return strategyMap.get(type);  // O(1)
}
```

## 提交规范

```
refactor(模块): 批次N-简要描述

- 改动点1
- 改动点2
- 消除N处运行时判断

影响文件：File1.java, File2.java
```

分批原则：每批次3-5个文件，独立可编译；顺序：接口定义 → 策略实现 → Service改造
