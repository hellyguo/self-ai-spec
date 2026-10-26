# JavaScript/TypeScript 代码审查规则

## 严重度口径

与 `code-review` 统一为三级，本文件中的 🔴/🟡/🟢 仅作为视觉标记，报告必须写出 P 级别：

| 级别 | 标记 | 判定标准 | 处理要求 |
|------|------|----------|----------|
| P0 | 🔴 | 安全漏洞、数据错误、崩溃、内存泄漏、主线程长时间阻塞 | 本次修改必须修复 |
| P1 | 🟡 | 性能隐患、资源未清理、类型不安全、可维护性问题 | 下次迭代修复并登记 |
| P2 | 🟢 | 风格、命名、可选优化 | 选择性修复 |

## 静态分析工具

审查前先执行自动化检查，人工审查聚焦工具无法覆盖的语义问题：

```bash
npx tsc --noEmit                     # 类型检查
npx eslint . --max-warnings 0        # 规范与缺陷
npm audit --omit=dev                 # 依赖漏洞
npx vitest run --coverage            # 行为与覆盖率
```

## 性能审查规则

### 1. 防抖与节流（Debounce/Throttle）

#### 审查要点

- **全局事件监听器**：`window.addEventListener('click', ...)` 等全局监听器必须使用防抖/节流
- **用户交互**：高频用户操作（click、input、submit）应添加防抖或节流
- **搜索/筛选**：输入触发搜索必须使用防抖（推荐 200-300ms）
- **提交按钮**：表单提交需添加防抖或禁用锁定（`disabled` + `loading` 状态）

#### 🔴 严重问题

- 高频点击按钮触发多次 API 调用，未使用防抖或禁用锁定
- 全局事件监听器执行重计算或 API 调用，无防抖/节流
- 搜索输入每次按键触发 API 调用

#### 🟡 警告

- 防抖时间设置不当（过短无效，过长影响体验）
- 防抖函数闭包依赖过期状态值

#### 🟢 建议

- 简单的导航/切换操作无需防抖
- 已使用 `disabled` + `loading` 锁定的提交按钮视为已防护

#### 代码示例

```typescript
// ❌ 反模式：无防抖的全局点击监听
window.addEventListener('click', (e) => {
  if (e.target.matches('.special')) {
    heavyCalculation(); // 每次点击都执行
  }
});

// ✅ 推荐：防抖全局监听
const debouncedHandler = debounce((e: Event) => {
  if (e.target.matches('.special')) {
    heavyCalculation(); // 防抖后执行
  }
}, 100);
window.addEventListener('click', debouncedHandler);

// ✅ 推荐：提交按钮锁定
const submitting = ref(false);
const handleSubmit = async () => {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await api.submit(data);
  } finally {
    submitting.value = false;
  }
};

// ✅ 推荐：搜索防抖
const search = debounce((query: string) => {
  api.search(query);
}, 300);
```

### 2. 深拷贝优化（Deep Copy Optimization）

#### 审查要点

- **热路径**：避免在消息回调、watch 处理函数、渲染函数中执行深拷贝
- **大对象**：避免对大数组/对象进行不必要的深拷贝
- **替代方案**：优先使用 `Object.assign()`、展开运算符、`shallowRef`、局部更新

#### 🔴 严重问题

- 高频消息回调（如 WebSocket、事件总线）中使用 `JSON.parse(JSON.stringify(...))`
- Watch 处理函数中对大对象执行深拷贝
- 模板/渲染函数中内联深拷贝操作

#### 🟡 警告

- 一次性的 DTO 转换使用深拷贝（可接受但应评估）
- 跨 iframe/Web Worker 通信需要深拷贝

#### 🟢 建议

- 使用 `Object.freeze()` 冻结不可变数据
- 使用 `markRaw()` 标记不需要响应式的大对象

#### 代码示例

```typescript
// ❌ 反模式：高频回调中的深拷贝
ws.onmessage = (data) => {
  state.list = JSON.parse(JSON.stringify(data.list)); // 🔴 阻塞主线程
};

// ✅ 推荐：局部更新
ws.onmessage = (data) => {
  const index = state.list.findIndex(item => item.id === data.id);
  if (index >= 0) {
    Object.assign(state.list[index], data); // 局部更新
  } else {
    state.list.push(data);
  }
};

// ❌ 反模式：watch 中的深拷贝
watch(someLargeObject, (newVal) => {
  state.copy = JSON.parse(JSON.stringify(newVal)); // 🔴 大对象拷贝
});

// ✅ 推荐：使用 shallowRef + 手动触发
const largeList = shallowRef([]);
watch(someLargeObject, (newVal) => {
  largeList.value = mergeInPlace(largeList.value, newVal);
  triggerRef(largeList); // 显式触发更新
});
```

### 3. 事件与订阅管理（Event & Subscription Management）

#### 审查要点

- **清理机制**：所有事件监听器、定时器、订阅必须在组件卸载时清理
- **资源泄漏**：检查 WebSocket、EventEmitter、BroadcastChannel 的订阅泄漏
- **生命周期**：在 `onUnmounted`、`onDeactivated`、`beforeDestroy` 中清理资源

#### 🔴 严重问题

- 未清理的事件监听器导致内存泄漏
- 未关闭的 WebSocket 连接
- 未清除的定时器（`setInterval`、`setTimeout`）

#### 🟡 警告

- 未清理的全局事件总线监听器
- 未清理的 `BroadcastChannel` 监听器

#### 🟢 建议

- 使用 `useEventListener` 等组合式 API 自动清理
- 封装资源管理类自动处理清理

#### 代码示例

```typescript
// ❌ 反模式：未清理的订阅
onMounted(() => {
  window.addEventListener('resize', handleResize);
  timer = setInterval(updateData, 1000);
  channel.addEventListener('message', handleMessage);
});

// ✅ 推荐：完整清理
let resizeListener: EventListener;
let timer: number;
let channel: BroadcastChannel;

onMounted(() => {
  resizeListener = () => handleResize();
  window.addEventListener('resize', resizeListener);
  
  timer = setInterval(updateData, 1000);
  
  channel = new BroadcastChannel('app-channel');
  channel.addEventListener('message', handleMessage);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeListener);
  clearInterval(timer);
  channel?.close();
});

// ✅ 推荐：使用组合式函数
function useInterval(callback: () => void, delay: number) {
  const intervalRef = ref<number>();
  
  onMounted(() => {
    intervalRef.value = setInterval(callback, delay);
  });
  
  onUnmounted(() => {
    clearInterval(intervalRef.value);
  });
  
  return intervalRef;
}
```

### 4. 消息驱动架构（Message-Driven Architecture）

#### 审查要点

- **局部更新**：消息回调应执行局部更新，而非全量数据拉取
- **消息源区分**：`BroadcastChannel` 等通道需区分消息来源（用户操作 vs 系统推送）
- **避免雪崩**：高频消息不应触发后端 API 雪崩

#### 🔴 严重问题

- 消息回调中触发全量 `fetch`、`reload`、`refresh`
- 未区分消息来源导致重复处理
- 高频消息（>10条/秒）触发同步重计算

#### 🟡 警告

- 消息处理函数中执行复杂计算
- 未对消息进行节流/防抖处理

#### 🟢 建议

- 使用节流控制全量更新频率（如 5秒一次）
- 标记脏数据状态，由用户操作触发实际更新

#### 代码示例

```typescript
// ❌ 反模式：消息触发全量拉取
ws.onmessage = () => {
  fetchFullData(); // 🔴 每条消息都拉取全量
};

// ✅ 推荐：局部更新
ws.onmessage = (data) => {
  updateItemInList(data.id, data); // 只更新单项
};

// ❌ 反模式：未区分消息来源
channel.onmessage = (msg) => {
  // 无法区分是用户点击还是系统推送
  fetchData(); // 可能重复拉取
};

// ✅ 推荐：区分消息来源
channel.onmessage = (msg) => {
  if (msg.data.source === 'user-click') {
    fetchData(); // 用户主动刷新
  } else if (msg.data.source === 'system-push') {
    applyPatch(msg.data.payload); // 系统推送，局部更新
  }
};

// ✅ 推荐：脏标记 + 节流更新
const dirty = ref(false);
ws.onmessage = () => {
  dirty.value = true; // 标记脏数据
};

// 5秒内只触发一次全量更新
watch(dirty, debounce((isDirty) => {
  if (isDirty) {
    fetchData();
    dirty.value = false;
  }
}, 5000));
```

### 5. 高频更新优化（High-Frequency Updates）

#### 审查要点

- **局部更新**：优先使用 `Object.assign()`、数组索引更新而非全量替换
- **响应式优化**：对大列表使用 `shallowRef` + `triggerRef` 减少代理开销
- **批量更新**：使用 `nextTick`、`requestAnimationFrame` 批量 DOM 更新

#### 🔴 严重问题

- 高频更新（>10次/秒）中使用全量数组替换
- 大列表（>100项）使用 `reactive` 导致性能问题
- 同步执行重计算阻塞主线程

#### 🟡 警告

- 未使用 `shallowRef` 包装大数组
- 在热路径中创建新对象而非复用现有对象

#### 🟢 建议

- 使用 `Object.freeze()` 冻结配置数据
- 使用 `markRaw()` 标记不需要响应式的对象

#### 代码示例

```typescript
// ❌ 反模式：全量数组替换
ws.onmessage = (data) => {
  list.value = data.list; // 🔴 高频下全量替换
};

// ✅ 推荐：局部更新
ws.onmessage = (data) => {
  const index = list.value.findIndex(item => item.id === data.id);
  if (index >= 0) {
    // 局部更新，保持引用
    Object.assign(list.value[index], data);
  }
};

// ❌ 反模式：大列表使用 reactive
const largeList = reactive([]); // 🔴 1000+ 项性能差

// ✅ 推荐：大列表使用 shallowRef
const largeList = shallowRef([]);
ws.onmessage = (data) => {
  largeList.value = mergeInPlace(largeList.value, data);
  triggerRef(largeList); // 手动触发更新
};

// ✅ 推荐：批量更新
const updates: Data[] = [];
ws.onmessage = (data) => {
  updates.push(data);
  if (updates.length > 10) {
    batchUpdate(updates);
    updates.length = 0;
  }
};
```

### 6. 严重度评级指南

| 等级 | 含义 | 触发条件 | 修复优先级 |
| ------ | ------ | ---------- | ------------ |
| 🔴 严重 | 必须修复，发布阻塞 | 性能问题导致主线程阻塞 > 50ms/秒；内存泄漏；未防护的高频 API 调用 | P0（本迭代修复） |
| 🟡 警告 | 应当修复，存在隐患 | 潜在性能问题；不合理的深拷贝；未优化的更新模式 | P1（下迭代修复） |
| 🟢 建议 | 可优化，长期改进 | 代码风格优化；建议性改进；非关键路径优化 | P2（选择性修复） |

### 7. 审查输出格式

#### 问题报告模板

````text
问题 [序号]: [简短描述]
- 严重度: P0/P1/P2（对应 🔴/🟡/🟢）
- 文件: path/to/file:line
- 代码片段: ...
- 问题描述: ...
- 量化影响: [如：推送频率 X 条/秒时主线程占用 Y ms]
- 修复建议:
  ```typescript
  // 修复代码
  ```
- 修复难度: 低/中/高
````

#### 报告结构

````markdown
# 性能审查报告

## 审查范围
- 文件数: N
- 代码行数: M
- 审查时间: YYYY-MM-DD

## P0 严重问题（必须修复）
[问题列表]

## P1 警告（应当修复）
[问题列表]

## P2 建议（可优化）
[问题列表]

## 性能统计
- 主线程长任务 (>50ms) 预估减少: X%
- 内存使用预估减少: Y%
- API 调用频率预估减少: Z%
````

### 8. 工具与自动化

#### 推荐工具

- **Lighthouse**: 网页性能分析
- **Chrome DevTools Performance**: 运行时性能分析
- **Webpack Bundle Analyzer**: 包大小分析
- **ESLint**: 代码规范检查

#### 自定义规则示例

```javascript
// ESLint 规则示例：禁止热路径中的深拷贝
module.exports = {
  rules: {
    'no-json-parse-stringify-in-hot-path': {
      create(context) {
        return {
          CallExpression(node) {
            if (node.callee.type === 'MemberExpression' &&
                node.callee.object?.name === 'JSON' &&
                node.callee.property?.name === 'parse' &&
                node.arguments[0]?.type === 'CallExpression' &&
                node.arguments[0].callee.object?.name === 'JSON' &&
                node.arguments[0].callee.property?.name === 'stringify') {
              context.report({
                node,
                message: 'Avoid JSON.parse(JSON.stringify(...)) in hot paths'
              });
            }
          }
        };
      }
    }
  }
};
```

## 正确性审查

- **相等比较**：禁止 `==` / `!=`，统一使用 `===` / `!==`；仅 `x == null` 用于同时判断 `null` 与 `undefined` 时有明确意图，需注释。
- **空值处理**：访问可能为空的对象前使用可选链或显式判空；禁止用非空断言 `!` 掩盖类型错误。
- **异步完整性**：`async` 函数调用必须 `await`、`return` 或显式 `.catch()`；浮动的 Promise 为 P0。
- **类型逃逸**：禁止 `as any`、`@ts-ignore`、`@ts-expect-error` 无说明使用；必要时使用 `unknown` 加类型收窄。
- **数值精度**：金额与高精度计算禁止直接使用 `number` 浮点运算，使用整数最小单位或 decimal 库。
- **闭包与状态**：事件回调、定时器中引用的状态必须确认是否为最新值，避免闭包捕获过期值。
- **可变共享**：导出的对象、数组不得被外部直接修改；使用只读类型或返回副本。

## 安全审查

- **XSS**：禁止将未净化内容写入 `innerHTML`、`v-html`、`dangerouslySetInnerHTML`、`document.write`。
- **动态执行**：禁止 `eval`、`new Function`、字符串形式 `setTimeout`。
- **原型污染**：合并外部 JSON 时过滤 `__proto__`、`constructor`、`prototype` 键。
- **依赖安全**：新增依赖必须通过 `npm audit`，禁止引入长期无人维护的包。
- **凭据存储**：令牌不得存放在 `localStorage`（XSS 可读取）；敏感 Cookie 必须 `HttpOnly`、`Secure`、`SameSite`。
- **请求伪造**：写操作需携带 CSRF 防护或使用 SameSite Cookie。
- **敏感信息**：不得在源码、日志、错误上报中输出密钥、令牌、个人信息。

## 代码质量审查

- **类型质量**：禁止隐式 `any`；公共 API 必须标注参数与返回值类型；联合类型需穷尽处理。
- **组件规模**：单文件建议不超过 500 行，超过 1000 行必须拆分；组件职责单一。
- **副作用管理**：`useEffect` / `watch` 必须声明完整依赖，禁止通过禁用 lint 规则掩盖依赖缺失。
- **资源清理**：事件监听、定时器、订阅、请求必须在卸载时清理或取消。
- **重复代码**：相同逻辑出现三次以上应抽取；避免为消除重复引入过度抽象。
- **变量声明**：禁止同一行多声明（`const a = 1, b = 2;`），每个变量独占一行。
- **错误处理**：`catch` 不得为空或仅 `console.log`，必须记录上下文并给出用户可见的失败反馈。

## 坏味道

| 坏味道 | 检测信号 | 建议 |
|--------|----------|------|
| 巨型组件 | 单文件超 500 行、JSX 层级过深 | 拆分子组件与自定义 Hook |
| 状态散乱 | 同一状态在多个组件重复维护 | 上提状态或引入状态管理 |
| 副作用耦合 | 一个 effect 同时做请求、订阅、DOM 操作 | 按职责拆分 effect |
| 魔法值 | 硬编码字符串、数字、URL | 提取常量或配置 |
| 复制粘贴 | 多个组件结构高度相似 | 抽象通用组件 |
| 过度抽象 | 为单一场景封装多层 Hook/HOC | 回归直接实现 |

## 审查优先级

| 优先级 | 审查内容 |
|--------|----------|
| 必须修正（P0） | XSS、动态执行、凭据泄露、浮动 Promise、类型断言掩盖错误、未清理的资源泄漏 |
| 应当修正（P1） | 高频更新性能问题、依赖数组缺失、`any` 滥用、错误处理缺失、组件过大 |
| 建议改进（P2） | 命名、注释、常量提取、目录组织、可选性能优化 |

## 签名

---
**JavaScript/TypeScript代码审查规则版本**：1.3.0  
**最后更新**：2026-10-26  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.js.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.js.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级JavaScript/TypeScript项目、Node.js服务、前端应用
