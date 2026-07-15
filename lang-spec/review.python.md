# Python 代码审查规则

## 性能审查规则

### 1. 性能优化模式

#### 审查要点
- **大数据集处理**：使用生成器表达式而非列表推导式处理大数据集
- **高效数据结构**：使用 `collections` 模块的 `defaultdict`、`Counter`、`deque` 等高效数据结构
- **缓存计算结果**：对计算密集型函数使用 `functools.lru_cache` 装饰器
- **循环优化**：避免在循环中重复计算相同表达式
- **字符串拼接**：避免使用 `+` 拼接大量字符串，使用 `join()` 方法

#### 🔴 严重问题
- 循环内重复计算相同表达式，未使用缓存或局部变量
- 使用 `+` 拼接大量字符串导致性能下降
- 对大列表使用列表推导式导致内存爆炸
- 未使用高效数据结构（如 `defaultdict` 替代 `dict.setdefault`）

#### 🟡 警告
- `lru_cache` 缓存大小设置不当（过大浪费内存，过小频繁计算）
- 生成器表达式使用不当，导致多次迭代同一生成器
- 过早优化，牺牲代码可读性

#### 🟢 建议
- 使用 `timeit` 模块测量性能关键路径
- 使用 `cProfile` 或 `py-spy` 进行性能分析
- 考虑使用 `Cython` 或 `PyPy` 对性能关键代码进行优化

#### 代码示例
```python
# ❌ 反模式：循环内重复计算
def process_items(items):
    results = []
    for item in items:
        # 每次循环都计算 len(items)
        if item > len(items) / 2:
            results.append(item)
    return results

# ✅ 推荐：提前计算
def process_items(items):
    results = []
    threshold = len(items) / 2
    for item in items:
        if item > threshold:
            results.append(item)
    return results

# ❌ 反模式：字符串拼接
def build_string(parts):
    result = ""
    for part in parts:
        result += part  # 每次创建新字符串
    return result

# ✅ 推荐：使用 join
def build_string(parts):
    return "".join(parts)

# ❌ 反模式：大数据集使用列表推导式
def process_large_file(file_path):
    with open(file_path) as f:
        # 一次性加载所有行到内存
        lines = [line.strip() for line in f]
        return [process_line(line) for line in lines]

# ✅ 推荐：使用生成器
def process_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield process_line(line.strip())
```

### 2. 内存管理审查

#### 审查要点
- **循环引用**：检查可能导致内存泄漏的循环引用
- **全局变量**：避免大型对象存储在全局变量中
- **缓存管理**：检查缓存大小和淘汰策略
- **文件描述符泄漏**：检查文件、网络连接是否正确关闭

#### 🔴 严重问题
- 存在循环引用且未使用 `weakref` 或手动打破引用
- 缓存无限增长，无淘汰策略
- 未使用 `with` 语句管理资源，导致文件描述符泄漏

#### 🟡 警告
- 过度缓存，内存占用过高
- 使用 `global` 关键字存储大型数据结构
- 未及时释放不再使用的对象引用

#### 代码示例
```python
# ❌ 反模式：循环引用
class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self  # 循环引用

# ✅ 推荐：使用 weakref
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        self._parent = None
    
    @property
    def parent(self):
        return self._parent() if self._parent else None
    
    @parent.setter
    def parent(self, value):
        self._parent = weakref.ref(value) if value else None
```

### 3. 并发安全审查

#### 审查要点
- **GIL 影响**：理解 Python GIL 对多线程性能的影响
- **线程安全**：检查共享数据结构是否线程安全
- **异步编程**：正确使用 `asyncio`，避免阻塞事件循环
- **进程池**：CPU 密集型任务使用 `multiprocessing` 而非 `threading`

#### 🔴 严重问题
- 在协程中使用阻塞 I/O 操作，阻塞事件循环
- 多线程访问非线程安全数据结构（如 `list`、`dict`）未加锁
- CPU 密集型任务使用多线程，受 GIL 限制无法并行

#### 🟡 警告
- 过度创建线程/进程，导致上下文切换开销
- 未正确处理协程异常，导致任务挂起
- 死锁风险：锁获取顺序不一致

#### 代码示例
```python
# ❌ 反模式：CPU 密集型任务使用多线程
import threading

def cpu_intensive_task():
    result = 0
    for i in range(10**7):
        result += i
    return result

threads = []
for _ in range(4):
    t = threading.Thread(target=cpu_intensive_task)
    t.start()
    threads.append(t)

# ✅ 推荐：CPU 密集型任务使用多进程
import multiprocessing

def cpu_intensive_task():
    result = 0
    for i in range(10**7):
        result += i
    return result

with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(cpu_intensive_task, range(4))
```

## 安全审查规则

### 1. 代码注入防护

#### 审查要点
- **命令执行**：检查 `os.system`、`subprocess` 调用是否使用安全参数
- **SQL 注入**：检查数据库查询是否使用参数化查询
- **模板注入**：检查模板渲染是否转义用户输入
- **反序列化**：检查 `pickle`、`yaml` 反序列化是否安全

#### 🔴 严重问题
- 使用字符串拼接构建 SQL 查询
- 直接执行用户提供的命令
- 反序列化不受信任的数据

#### 代码示例
```python
# ❌ 反模式：SQL 注入漏洞
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # 用户输入直接拼接到 SQL
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

# ✅ 推荐：参数化查询
def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
```

### 2. 敏感信息处理

#### 审查要点
- **硬编码密钥**：检查代码中是否有硬编码的 API 密钥、密码
- **日志泄露**：检查日志是否记录敏感信息
- **配置文件**：敏感配置是否从环境变量或安全存储加载

#### 🔴 严重问题
- 源代码中硬编码数据库密码、API 密钥
- 日志中记录用户密码、token 等敏感信息
- 配置文件明文存储敏感信息

#### 代码示例
```python
# ❌ 反模式：硬编码密钥
API_KEY = "sk-live-1234567890abcdef"  # 泄露在代码中

# ✅ 推荐：从环境变量加载
import os
API_KEY = os.environ.get("API_KEY")

# 或从安全存储加载
import keyring
API_KEY = keyring.get_password("myapp", "api_key")
```

## 代码质量审查规则

### 1. 异常处理审查

#### 审查要点
- **裸露的 except**：检查是否存在裸露的 `except:` 语句
- **异常屏蔽**：检查是否捕获异常后未记录或重新抛出
- **资源泄漏**：检查异常发生时资源是否正常释放

#### 🔴 严重问题
- 使用裸露的 `except:` 捕获所有异常
- 捕获异常后静默处理（`except Exception: pass`）
- 异常发生时未释放资源（文件、锁、连接）

#### 代码示例
```python
# ❌ 反模式：异常屏蔽
try:
    risky_operation()
except:
    pass  # 静默处理，问题被隐藏

# ✅ 推荐：适当处理异常
try:
    risky_operation()
except ValueError as e:
    logger.error(f"操作失败: {e}")
    raise  # 重新抛出或处理
```

### 2. 导入与依赖审查

#### 审查要点
- **循环导入**：检查模块间是否存在循环导入
- **未使用导入**：检查是否存在未使用的导入语句
- **版本冲突**：检查依赖版本是否兼容

#### 🔴 严重问题
- 模块间循环导入导致 ImportError
- 导入整个模块仅使用少量函数，增加启动时间
- 依赖版本不兼容导致运行时错误

#### 代码示例
```python
# ❌ 反模式：循环导入
# module_a.py
import module_b
def func_a():
    return module_b.func_b()

# module_b.py  
import module_a  # 循环导入
def func_b():
    return module_a.func_a()

# ✅ 推荐：打破循环导入
# 将公共代码提取到第三个模块
# 或使用延迟导入
def func_b():
    import module_a  # 函数内导入
    return module_a.func_a()
```

## 签名

---
**Python代码审查规则版本**：1.2.0  
**最后更新**：2025-01-01  
**编码规范**：${AI_SPEC_ROOT}/lang-spec/spec.python.md  
**审查规则**：${AI_SPEC_ROOT}/lang-spec/review.python.md  
**关联通用规则**：${AI_SPEC_ROOT}/skills/code-review/SKILL.md  
**适用场景**：企业级Python项目、Web服务、数据科学、自动化脚本