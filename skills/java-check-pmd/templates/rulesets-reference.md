# PMD规则集速查

## 基础规则集（basic.xml）

| 规则 | 描述 | 示例 |
|------|------|------|
| `EmptyCatchBlock` | 空的catch块 | `try { ... } catch (Exception e) {}` |
| `UnnecessaryConversionTemporary` | 不必要的类型转换 | `new String(str.toString())` |
| `OverrideBothEqualsAndHashcode` | 重写equals必须重写hashCode | 缺少hashCode方法 |
| `DoubleCheckedLocking` | 双重检查锁定问题 | 线程安全的单例模式错误实现 |

## 代码风格规则集（codeestyle.xml）

| 规则 | 描述 | 建议 |
|------|------|------|
| `ShortVariable` | 变量名过短 | 使用有意义的变量名 |
| `LongVariable` | 变量名过长 | 简化变量名 |
| `ShortClassName` | 类名过短 | 使用描述性类名 |
| `AvoidFinalLocalVariable` | 避免final局部变量 | 除非必要，否则不用final |
| `OnlyOneReturn` | 方法中只有一个return | 保持方法简单 |
| `EmptyMethodInAbstractClassShouldBeAbstract` | 抽象类中的空方法应为抽象 | 明确方法意图 |

## 设计规则集（design.xml）

| 规则 | 描述 | 影响 |
|------|------|------|
| `UseUtilityClass` | 应使用工具类 | 避免实例化只有静态方法的类 |
| `SimplifyBooleanReturns` | 简化布尔返回值 | 直接返回布尔表达式 |
| `SimplifyBooleanExpressions` | 简化布尔表达式 | 移除不必要的逻辑 |
| `SwitchDensity` | switch语句密度 | switch语句不宜过大 |
| `GodClass` | 上帝类 | 类职责过多，应拆分 |
| `CyclomaticComplexity` | 圈复杂度 | 方法过于复杂，应重构 |
| `ExcessiveClassLength` | 类过长 | 类代码行数过多 |
| `ExcessiveMethodLength` | 方法过长 | 方法代码行数过多 |
| `ExcessiveParameterList` | 参数列表过长 | 方法参数过多 |
| `ExcessivePublicCount` | 公共方法过多 | 类的公共接口过大 |
| `TooManyFields` | 字段过多 | 类包含太多字段 |
| `NcssConstructorCount` | 构造函数复杂度 | 构造函数过于复杂 |
| `NcssMethodCount` | 方法复杂度 | 方法过于复杂 |
| `NcssTypeCount` | 类型复杂度 | 类过于复杂 |

## 安全规则集（security.xml）

| 规则 | 描述 | 风险等级 |
|------|------|----------|
| `HardCodedCryptoKey` | 硬编码加密密钥 | 高危 |
| `InsecureCryptoIv` | 不安全的加密IV | 高危 |
| `DataflowAnomalyAnalysis` | 数据流异常分析 | 中危 |
| `AvoidUsingHardCodedIP` | 避免硬编码IP地址 | 中危 |
| `AvoidUsingHardCodedURL` | 避免硬编码URL | 中危 |

## 性能规则集（performance.xml）

| 规则 | 描述 | 性能影响 |
|------|------|----------|
| `AvoidArrayLoops` | 避免数组循环 | 高 |
| `AvoidInstantiatingObjectsInLoops` | 避免在循环中实例化对象 | 高 |
| `OptimizableToArrayCall` | 可优化的toArray调用 | 中 |
| `RedundantFieldInitializer` | 冗余字段初始化器 | 低 |
