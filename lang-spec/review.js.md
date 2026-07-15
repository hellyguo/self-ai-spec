# JavaScript/TypeScript 代码审查规则

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

```
问题 [序号]: [简短描述]
- 严重度: 🔴/🟡/🟢
- 文件: path/to/file:line
- 代码片段: ...
- 问题描述: ...
- 量化影响: [如：推送频率 X 条/秒时主线程占用 Y ms]
- 修复建议: 
  ```typescript
  // 修复代码
  ```

- 修复难度: 低/中/高

```

#### 报告结构
```markdown
# 性能审查报告

## 审查范围
- 文件数: N
- 代码行数: M
- 审查时间: YYYY-MM-DD

## 🔴 严重问题 (必须修复)
[问题列表]

## 🟡 警告 (应当修复)  
[问题列表]

## 🟢 建议 (可优化)
[问题列表]

## 性能统计
- 主线程长任务 (>50ms) 预估减少: X%
- 内存使用预估减少: Y%
- API 调用频率预估减少: Z%
```

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

## 签名

---
**JavaScript/TypeScript代码审查规则版本**：1.2.0  
**最后更新**：2025-01-01  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.js.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.js.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级JavaScript/TypeScript项目、Node.js服务、前端应用

```
