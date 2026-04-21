# 测试代码模板（通用）

> 增量测试时直接套用以下模板，无需重新分析测试风格。

## 一、枚举类测试模板

适用于：所有 enum 类的测试（含新增枚举和已有枚举的新增方法）

```java
package {被测枚举所在包};

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import static org.assertj.core.api.Assertions.assertThat;

/**
 * {枚举类名} 增量单元测试
 * diff变更说明：{一句话描述变更}
 */
@DisplayName("{枚举类名} 枚举测试")
class {枚举类名}Test {

    @Nested
    @DisplayName("枚举值基础测试")
    class EnumValueTest {
        @Test
        @DisplayName("{枚举值} 的 intVal 应为 {值}")
        void {枚举值}IntVal() {
            assertThat({枚举类名}.{枚举值}.getIntVal()).isEqualTo({值});
        }
        // 每个枚举值一个测试
    }

    @Nested
    @DisplayName("{静态方法名} 测试")
    class {静态方法名}Test {
        @ParameterizedTest(name = "值 {0} 期望 {1}")
        @CsvSource({"1,true", "2,false"})  // 所有分支
        void check(int value, boolean expected) {
            assertThat({枚举类名}.{方法}(value)).isEqualTo(expected);
        }

        @ParameterizedTest
        @NullSource
        @DisplayName("null 返回 false")
        void nullValue(Integer value) {
            assertThat({枚举类名}.{方法}(value)).isFalse();
        }
    }
}
```

**覆盖要求**：每个枚举值的 getIntVal + 每个静态方法的全部分支 + null + 互斥性

---

## 二、Domain/POJO 类测试模板

适用于：新增字段、getter/setter、日期防御性拷贝

```java
package {被测类所在包};

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import java.util.Date;
import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("{类名} 域对象测试")
class {类名}Test {

    private {类名} target;

    @BeforeEach
    void setUp() { target = new {类名}(); }

    @Nested
    @DisplayName("{新增字段名} 字段测试 - 新增字段")
    class {字段名}Test {
        @Test
        @DisplayName("设置和获取")
        void setAndGet() {
            target.set{字段名}("value");
            assertThat(target.get{字段名}()).isEqualTo("value");
        }

        @Test
        @DisplayName("默认值为 null")
        void defaultNull() {
            assertThat(target.get{字段名}()).isNull();
        }

        @Test
        @DisplayName("设置为 null")
        void setNull() {
            target.set{字段名}("value");
            target.set{字段Name}(null);
            assertThat(target.get{字段名}()).isNull();
        }

        @Test
        @DisplayName("空字符串")
        void setEmpty() {
            target.set{字段名}("");
            assertThat(target.get{字段名}()).isEmpty();
        }
    }

    @Nested
    @DisplayName("日期字段防御性拷贝测试")
    class DateDefensiveCopyTest {
        @Test
        @DisplayName("getter 返回防御性拷贝")
        void getterDefensiveCopy() {
            Date original = new Date(1700000000000L);
            target.set{日期字段}(original);
            Date got = target.get{日期字段}();
            got.setTime(0L);
            assertThat(target.get{日期字段}().getTime()).isEqualTo(1700000000000L);
        }

        @Test
        @DisplayName("setter 做防御性拷贝")
        void setterDefensiveCopy() {
            Date original = new Date(1700000000000L);
            target.set{日期字段}(original);
            original.setTime(0L);
            assertThat(target.get{日期字段}().getTime()).isEqualTo(1700000000000L);
        }
    }
}
```

**覆盖要求**：新增字段的 getter/setter + null + 空值 + 边界值 + 日期防御性拷贝

---

## 三、Service 层测试模板（Mockito）

适用于：新增方法、修改方法、业务逻辑变更

```java
package {被测类所在包};

import {列出必要的 import};
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("{类名} 增量测试")
class {类名}Test {

    @Mock private {依赖1} {依赖1字段名};
    @Mock private {依赖2} {依赖2字段名};
    // 列出被测方法用到的所有依赖

    @InjectMocks
    private {被测类} target;

    @Nested
    @DisplayName("{新增方法名} 测试 - 新增方法")
    class {方法名}Test {

        @Test
        @DisplayName("正常场景描述")
        void normalCase() {
            // Given
            when({依赖}.{方法}({参数})).thenReturn({返回值});

            // When
            {返回类型} result = target.{被测方法}({参数});

            // Then
            assertThat(result).isEqualTo({期望值});
            verify({依赖}).{方法}({参数});  // 验证调用
        }

        @Test
        @DisplayName("null 参数返回 {默认值}")
        void nullParam() {
            {返回类型} result = target.{被测方法}(null);
            assertThat(result).isEqualTo({默认值});
            verify({依赖}, never()).{方法}(any());  // 验证不调用
        }

        // 每个分支一个测试方法
    }
}
```

**覆盖要求**：正常路径 + null 参数 + 空集合 + 边界值 + 异常路径 + verify 交互

---

## 四、工具类方法测试模板（无 Spring 容器）

适用于：DateUtil、StrUtil 等纯逻辑工具方法

```java
@ExtendWith(MockitoExtension.class)
class {工具类}Test {
    @Spy private {依赖Dao} {字段};
    @InjectMocks private {工具类} target;

    @Nested
    @DisplayName("{新增方法} 测试 - 新增方法")
    class {方法名}Test {
        // 对于简单工具方法，直接 new 实例测试
        {工具类} realUtil = new {工具类}();

        @Test
        @DisplayName("同值应返回 true")
        void sameValue() {
            assertThat(realUtil.{方法}(val1, val2)).isTrue();
        }

        @Test
        @DisplayName("null 参数返回 false")
        void nullParam() {
            assertThat(realUtil.{方法}(null, val)).isFalse();
        }
    }
}
```

---

## 五、集成测试模板 — 静态方法依赖（PowerMock）

适用于：分类 C（方法内部调用了不可 Mockito 的静态工具方法，如 `SolarExcelImportUtil.importExcel`）

### pom-test.xml 需添加的依赖

```xml
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit5</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito2</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
```

### 代码模板

```java
package {被测类所在包};

import {列出必要的 import};
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PowerMockIgnore;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit5.PowerMockExtension;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;
import static org.powermock.api.mockito.PowerMockito.*;

@ExtendWith(PowerMockExtension.class)
@PrepareForTest({{StaticUtilClass}.class})       // 列出需要 mock 的静态类
@PowerMockIgnore({"javax.management.*", "javax.crypto.*"})
@DisplayName("{类名} 集成测试")
class {类名}IntegrationTest {

    @Mock private {依赖1} {依赖1字段名};
    @Mock private {依赖2} {依赖2字段名};
    // 列出所有依赖

    @InjectMocks
    private {被测类} target;

    @Nested
    @DisplayName("{方法名} 测试")
    class {方法名}Test {

        @Test
        @DisplayName("正常流程应正确处理数据")
        void shouldProcessWhenValidInput() throws Exception {
            // Step 1: mockStatic 静态方法
            mockStatic({StaticUtilClass}.class);
            when({StaticUtilClass}.{staticMethod}(any(), any(), any()))
                .thenReturn({mockResult});

            // Step 2: mock 其他依赖（与单元测试相同）
            when({依赖}.{方法}({参数})).thenReturn({返回值});

            // Step 3: 执行被测方法
            {返回类型} result = target.{被测方法}({参数});

            // Step 4: 断言 + 验证
            assertThat(result).isNotNull();
            verify({依赖}).{方法}({参数});
        }

        @Test
        @DisplayName("静态方法抛异常应向上传播")
        void shouldPropagateWhenStaticMethodFails() throws Exception {
            mockStatic({StaticUtilClass}.class);
            when({StaticUtilClass}.{staticMethod}(any(), any(), any()))
                .thenThrow(new RuntimeException("导入失败"));

            assertThatThrownBy(() -> target.{被测方法}({参数}))
                .isInstanceOf(Exception.class);
        }
    }
}
```

**关键约束**：
- `@PrepareForTest` 中必须列出所有被 mock 的静态类
- `mockStatic()` 后，该类的**所有**静态方法都会被拦截，未被 when() 配置的返回默认值
- PowerMock 与 Mockito 共存时，普通依赖仍用 `@Mock` + `@InjectMocks`
- 测试文件命名必须以 `IntegrationTest` 结尾，区别于单元测试

---

## 六、集成测试模板 — 深度 Mock 链路

适用于：分类 D/E（depCount ≥ 4 或 cascadeDepth ≥ 3 或存在外部系统多步骤交互）

### 代码模板

```java
package {被测类所在包};

import {列出必要的 import};
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("{类名} 集成测试 - 深度链路")
class {类名}IntegrationTest {

    // 必须列出被测方法调用的【所有】依赖，一个不能少
    @Mock private {依赖1} {依赖1字段名};
    @Mock private {依赖2} {依赖2字段名};
    @Mock private {依赖3} {依赖3字段名};
    @Mock private {依赖4} {依赖4字段名};
    @Mock private {依赖5} {依赖5字段名};
    // ... 所有依赖

    @InjectMocks
    private {被测类} target;

    @Nested
    @DisplayName("{方法名} 测试")
    class {方法名}Test {

        @Test
        @DisplayName("完整正向流程")
        void shouldCompleteFullFlow() throws Exception {
            // ===== 按方法体调用顺序，逐层 mock =====

            // 第 1 层调用：获取任务状态
            when({dep1}.{method}(any())).thenReturn("completed");

            // 第 2 层调用：获取员工信息（依赖第 1 层的某些结果）
            {ReturnType} empInfo = new {ReturnType}();
            // 设置 empInfo 的必要字段...
            when({dep2}.{method}(any())).thenReturn(empInfo);

            // 第 3 层调用：获取业务数据（依赖第 2 层返回的对象）
            {ReturnType2} bizData = new {ReturnType2}();
            when({dep3}.{method}(any())).thenReturn(bizData);

            // 第 4 层调用：查询关联数据
            when({dep4}.{method}(anyString())).thenReturn({关联数据});

            // 第 5 层调用：查询操作人员
            when({dep5}.{method}(anyLong())).thenReturn({操作人员});

            // ===== 执行被测方法 =====
            {返回类型} result = target.{被测方法}({参数});

            // ===== 断言 + 验证 =====
            assertThat(result).isNotNull();
            verify({dep1}).{method}(any());
            verify({dep3}).{method}(any());
        }

        @Test
        @DisplayName("第N层返回null时应抛异常或安全处理")
        void shouldHandleNullAtLayerN() throws Exception {
            // 前 N-1 层正常 mock
            when({dep1}.{method}(any())).thenReturn("status");
            when({dep2}.{method}(any())).thenReturn({正常数据});

            // 第 N 层返回 null
            when({dep3}.{method}(any())).thenReturn(null);

            // 断言行为
            assertThatThrownBy(() -> target.{被测方法}({参数}))
                .isInstanceOf(Exception.class);
        }

        @Test
        @DisplayName("第1层返回特定值时走不同分支")
        void shouldBranchWhenLayer1ReturnsX() throws Exception {
            // 第 1 层返回触发不同分支的值
            when({dep1}.{method}(any())).thenReturn("{不同值}");

            // 该分支需要的后续 mock...
            when({dep2}.{method}(anyString())).thenReturn({数据});

            {返回类型} result = target.{被测方法}({参数});
            assertThat(result).isNotNull();
        }
    }
}
```

**关键约束**：
1. **必须按源代码方法体的实际调用顺序逐层 mock**，跳过任何一层都会导致 NPE
2. 每层 mock 的返回值必须构造完整对象（至少包含下一层会调用的 getter 字段）
3. 被测方法中的 `if/else` 分支，每个分支至少一个测试用例
4. 当中间层返回 null 导致 NPE 时，不视为测试失败，而是标注为"需 null 安全处理"
5. 测试文件命名必须以 `IntegrationTest` 结尾

### 构造级联返回值的技巧

当依赖链为 A→B→C 时，B 的返回值必须是完整对象：

```java
// 错误：只设置了部分字段，后续调用 NPE
EmpInfo info = new EmpInfo();
when(dep.getEmpInfo()).thenReturn(info);
// 方法内部: info.getDeptInfo().getManagerId() → NPE！因为 getDeptInfo() 返回 null

// 正确：级联构造所有中间对象
DeptInfo deptInfo = new DeptInfo();
deptInfo.setManagerId(10L);
deptInfo.setDeptManagerId(20L);
EmpInfo info = new EmpInfo();
info.setDeptInfo(deptInfo);
when(dep.getEmpInfo()).thenReturn(info);
```

---

## 七、测试命名规范

| 场景 | 命名规则 | 示例 |
|------|---------|------|
| 枚举值测试 | `{枚举值}的{属性}应为{期望}` | `svnNormalIntVal` |
| 正常路径 | `正常场景描述` | `validTravelAppIdWithResult` |
| null 参数 | `{参数名}为null时返回{默认值}` | `travelAppIdNull` |
| 边界值 | `{具体边界描述}` | `hourBoundary` |
| 分组 | `@Nested @DisplayName("{方法名} 测试 - {标签}")` | `isAllTravelStartDateBeforeOrEqual 测试 - 新增方法` |
