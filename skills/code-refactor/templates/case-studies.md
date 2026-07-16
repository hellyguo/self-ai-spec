# 应用案例

## 类型退化修复案例

**问题识别**：

- 信号：`if (IndexationType.FLOAT.getValue().equals(type))` 出现12次
- 位置：BondsServiceImpl, BondInstCflServiceImpl 等7个Service
- 模式：运行时字符串比较

**三问分析**：

- Q1: 为什么出现？ — BondsIncome.indexation字段是String类型，类型信息丢失
- Q2: 本质是什么？ — 类型退化，枚举退化成字符串常量
- Q3: 正确设计？ — 字段改为枚举类型，用策略模式分发行为

**解决方案**：

1. 创建IndexationTypeStrategy接口
2. 实现4个策略类：Fixed/Float/Segmented/Discount
3. Service注入策略列表
4. 删除所有if-else判断

**效果**：运行时判断 12→0，类型安全 无→编译期检查，可扩展性 差→优

## 数据退化修复案例

**问题识别**：

- 信号：嵌套Stream filter，三层循环
- 位置：FixingServiceImpl
- 模式：O(n³)复杂度

**三问分析**：

- Q1: 为什么出现？ — 数据用List存储，却需要按ID关联查找
- Q2: 本质是什么？ — 数据结构与访问模式不匹配
- Q3: 正确设计？ — 预构建Map索引，O(1)查找

**解决方案**：

```java
Map<Integer, Cashflow> cashflowMap = cashflows.stream()
    .collect(Collectors.toMap(Cashflow::getId, Function.identity()));

Map<Integer, List<Reset>> resetMap = resets.stream()
    .collect(Collectors.groupingBy(Reset::getCashflowId));

Cashflow cf = cashflowMap.get(cashflowId);
List<Reset> resetList = resetMap.get(cashflowId);
```

**效果**：时间复杂度 O(n³)→O(n)，性能提升约50倍
