# JavaScript/TypeScript 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 静态不可变变量名使用大写
4. 静态可变变量名使用小写
5. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
6. 优先使用组合而非继承

## 命名约定

- 文件名：小写蛇形命名（`user_service.ts`）或小写短横线命名（`user-service.ts`）
- 类名/接口名/类型名：帕斯卡命名法（`UserService`，`IHttpClient`）
- 函数名/方法名：小写驼峰命名（`getUserById`，`processRequest`）
- 变量名：小写驼峰命名（`userName`，`itemCount`）
- 常量：全大写蛇形命名（`MAX_CONNECTION_COUNT`）
- 私有属性/方法：`#` 前缀（ES2022+）或 `_` 前缀
- 布尔变量/方法：使用 `is`、`has`、`can`、`should` 前缀（`isActive`，`hasPermission`）

## TypeScript 类型

- 优先使用 `interface` 定义对象类型
- 使用 `type` 定义联合类型、交叉类型、工具类型
- 避免使用 `any`，使用 `unknown` 替代
- 函数参数和返回值必须添加类型注解
- 使用泛型提高代码复用性

```typescript
// 接口定义
interface User {
  id: number;
  name: string;
  email?: string;
}

// 泛型函数
function getById<T>(id: number): Promise<T | null> {
  // ...
}

// 避免 any
function process(data: unknown) {
  if (typeof data === 'string') {
    // data 是 string 类型
  }
}
```

## 异步编程

- 使用 `async/await` 而非 `.then()/.catch()`
- 正确处理错误，使用 `try/catch`
- 并行操作使用 `Promise.all()`
- 使用 `Promise.race()` 实现超时控制

```typescript
// 推荐
async function fetchUser(id: number): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    logger.error('获取用户失败', error);
    throw error;
  }
}

// 并行请求
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
]);
```

## 模块导入

- 使用 ES Module 语法（`import`/`export`）
- 按 TypeScript/JavaScript 规范组织导入顺序
- 使用 `export default` 仅当模块有单一主要导出

```typescript
// 标准库
import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';

// 第三方库
import axios from 'axios';

// 本地模块
import { UserService } from './services/user';
import type { User } from './types';
```

## 代码风格

- 使用 2 空格缩进（或遵循项目配置）
- 使用 `const` 声明不可变变量，`let` 声明可变变量
- 避免使用 `var`
- 使用模板字符串拼接字符串
- 使用 `===` 而非 `==`

```typescript
// 推荐
const message = `用户 ${userName} 已登录`;
if (status === 'active') { }

// 避免
var message = '用户 ' + userName + ' 已登录';
if (status == 'active') { }
```

## 错误处理

- 使用自定义错误类区分错误类型
- 避免静默失败，记录或抛出错误
- 使用 `try/catch` 包装可能失败的代码

```typescript
class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

function validateUser(user: unknown): User {
  if (!isValidUser(user)) {
    throw new ValidationError('Invalid user data');
  }
  return user;
}
```

## React/Vue 组件规范

- 组件名使用帕斯卡命名法
- Props 使用 TypeScript 接口定义
- 使用函数组件和 Hooks（React）
- 保持组件职责单一

```typescript
// React 组件
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function Button({ label, onClick, disabled = false }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}
```

## 测试规范

- 使用 `Jest` 或 `Vitest` 作为测试框架
- 测试文件命名：`*.test.ts` 或 `*.spec.ts`
- 使用 `describe`/`it` 组织测试用例
- 测试覆盖率目标 80% 以上

```typescript
describe('UserService', () => {
  it('should return user by id', async () => {
    const user = await userService.getById(1);
    expect(user).toBeDefined();
    expect(user.id).toBe(1);
  });
});
```