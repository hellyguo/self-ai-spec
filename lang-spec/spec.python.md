# Python 编码规范

## 通用规则

1. 对文件有总体注释，对重点代码有详尽注释
2. 不使用行尾注释
3. 静态不可变变量名使用大写
4. 静态可变变量名使用小写
5. 类设计遵循单一职责原则，一个大类应拆分为多个职责明确的小类
6. 优先使用组合而非继承

## 命名约定

- 模块名：小写蛇形命名（`user_service.py`）
- 包名：小写蛇形命名（`my_package`）
- 类名：帕斯卡命名法（`UserService`，`HttpClient`）
- 函数名：小写蛇形命名（`get_user_by_id`，`process_request`）
- 变量名：小写蛇形命名（`user_name`，`item_count`）
- 常量：全大写蛇形命名（`MAX_CONNECTION_COUNT`，`DEFAULT_TIMEOUT_MS`）
- 私有属性/方法：单下划线前缀（`_internal_value`）
- 强私有属性/方法：双下划线前缀（`__private_value`）

## 类型注解

- Python 3.6+ 使用类型注解提高代码可读性
- 函数参数和返回值应添加类型注解
- 使用 `typing` 模块的泛型类型（`List`、`Dict`、`Optional` 等）

```python
from typing import List, Optional

def get_user_by_id(user_id: int) -> Optional[User]:
    ...

def process_items(items: List[str]) -> Dict[str, int]:
    ...
```

## 文档字符串

- 使用三引号文档字符串描述模块、类、函数
- 遵循 Google 或 NumPy 文档风格
- 包含参数描述、返回值描述、异常说明

```python
def calculate_total(items: List[Item]) -> float:
    """计算订单总金额.
    
    Args:
        items: 订单项列表
        
    Returns:
        订单总金额
        
    Raises:
        ValueError: 当 items 为空时
    """
    if not items:
        raise ValueError("items cannot be empty")
    return sum(item.price for item in items)
```

## 导入规范

- 导入顺序：标准库 -> 第三方库 -> 本地模块，每组之间空一行
- 避免使用 `from module import *`
- 使用绝对导入优先于相对导入

```python
import os
import sys
from typing import List, Optional

import requests
import numpy as np

from myproject.utils import helper
from myproject.models import User
```

## 错误处理

- 使用具体的异常类型，避免裸露的 `except:`
- 尽早验证输入参数，快速失败
- 使用描述性错误消息
- 区分可恢复错误和不可恢复错误

```python
# 推荐
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"操作失败: {e}")
    raise

# 避免
try:
    result = risky_operation()
except:
    pass
```

## 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 最大行长度 79 字符（文档字符串/注释 72 字符）
- 使用 `black` 或 `autopep8` 格式化代码
- 使用 `ruff` 或 `flake8` 进行代码检查

## 日志记录

- 使用 `logging` 模块而非 `print`
- 使用适当的日志级别（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- 使用占位符而非字符串拼接

```python
import logging

logger = logging.getLogger(__name__)

logger.info("处理用户 %s", user_id)
logger.error("操作失败: %s", error, exc_info=True)
```



## 测试规范

- 使用 `pytest` 作为测试框架
- 测试文件以 `test_` 前缀命名
- 测试函数以 `test_` 前缀命名
- 使用 `pytest.fixture` 管理测试资源
- 测试覆盖率目标 80% 以上

```python
import pytest

@pytest.fixture
def sample_user():
    return User(id=1, name="test")

def test_user_name(sample_user):
    assert sample_user.name == "test"
```