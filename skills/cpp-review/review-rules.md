## 一、内存管理规则

### R1.1 new/delete 配对规则

| 规则ID | 规则描述 | 严重程度 | 检查方法 |
|--------|----------|----------|----------|
| R1.1.1 | 每个 `new` 必须有对应的 `delete` | P1 | grep 统计 new/delete 数量 |
| R1.1.2 | 禁止跨模块传递裸指针所有权 | P1 | 代码审查 |
| R1.1.3 | 析构函数必须释放所有成员指针 | P1 | 代码审查 |
| R1.1.4 | 循环内 `new` 覆盖指针前必须先 `delete` | P0 | 代码审查 |

**检查命令**:
```bash
# 统计 new/delete 数量
grep -r "new " src/ include/ | wc -l
grep -r "delete " src/ include/ | wc -l

# 查找循环内 new 覆盖
grep -rn "for.*{" src/ -A 5 | grep "new "
```

**典型问题**:
```cpp
// 错误：循环内 new 覆盖指针泄漏
for (int i = 0; i < n; i++) {
    obj = new TObject();  // 前一次的 obj 泄漏
}

// 正确：先 delete 再 new
for (int i = 0; i < n; i++) {
    delete obj;
    obj = new TObject();
}
```

### R1.2 RAII 规则

| 规则ID | 规则描述 | 严重程度 | 适用场景 |
|--------|----------|----------|----------|
| R1.2.1 | 关键路径使用智能指针管理内存 | P1 | 新代码 |
| R1.2.2 | 锁使用 RAII 守卫（std::lock_guard） | P0 | 全部代码 |
| R1.2.3 | 文件句柄使用 RAII 包装 | P2 | 新代码 |
| R1.2.4 | 数据库连接使用 RAII 包装 | P2 | 新代码 |

**典型问题**:
```cpp
// 错误：锁内提前 return 导致锁泄漏
LRWST(PositionSums.lock);
if (!GetRunState()) {
    return;  // 锁未释放！
}
LED;

// 正确：使用 RAII 锁守卫
std::unique_lock<std::shared_mutex> lock(PositionSums.mutex);
if (!GetRunState()) {
    return;  // 锁自动释放
}
```

### R1.3 malloc/free 规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R1.3.1 | malloc 返回值必须检查 NULL | P1 |
| R1.3.2 | malloc/free 必须配对 | P1 |
| R1.3.3 | 禁止 malloc 后用 delete，或 new 后用 free | P0 |

---

## 二、SQL注入防护规则

### R2.1 参数化查询规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R2.1.1 | 禁止字符串拼接构建 SQL | P0 |
| R2.1.2 | 外部输入必须使用参数化查询 | P0 |
| R2.1.3 | 表名、字段名必须白名单校验 | P1 |

**检查命令**:
```bash
# 查找 SQL 拼接
grep -rn "\".*select.*+.*\"" src/ include/
grep -rn "\".*insert.*+.*\"" src/ include/
grep -rn "\".*update.*+.*\"" src/ include/
grep -rn "\".*delete.*+.*\"" src/ include/
```

**典型问题**:
```cpp
// 错误：SQL 拼接
string sql = "SELECT * FROM users WHERE id = '" + userId + "'";

// 正确：参数化查询
PreparedStatement* stmt = conn->prepareStatement(
    "SELECT * FROM users WHERE id = ?");
stmt->setString(1, userId);
```

### R2.2 信任边界规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R2.2.1 | 禁止协议携带 SQL 文本直接执行 | P0 |
| R2.2.2 | 服务端主导 SQL 生成 | P1 |
| R2.2.3 | 操作日志与写库分离 | P1 |

**典型问题**:
```cpp
// 错误：协议携带 SQL 直接执行
ar >> dmlsql >> detailsql;
ExecSQLList(dmlsql);  // 危险！

// 正确：服务端生成 SQL
ar >> operationType >> operationData;
string sql = GenerateSQL(operationType, operationData);
```

---

## 三、线程安全规则

### R3.1 线程命名规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R3.1.1 | pthread_create 后必须调用 pthread_setname_np | P2 |
| R3.1.2 | 线程名长度 ≤ 15 字符（Linux限制） | P3 |
| R3.1.3 | 线程名应能标识模块和功能 | P2 |

**检查命令**:
```bash
# 查找未设置线程名的 pthread_create
grep -rn "pthread_create" src/ -A 5 | grep -v "pthread_setname"
```

**正确示例**:
```cpp
pthread_create(&pt, &attr, &CreateThread, (void*)this);
pthread_setname_np(pt, "WorkThread");  // 设置线程名
```

### R3.2 线程退出规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R3.2.1 | 线程退出必须有序：停止接单 → 排空队列 → 释放资源 | P0 |
| R3.2.2 | 禁止析构函数中投递到错误队列 | P0 |
| R3.2.3 | join 超时必须有 fallback 处理 | P1 |
| R3.2.4 | 线程退出标志必须是 atomic 或 volatile | P1 |

**典型问题**:
```cpp
// 错误：析构投递到错误队列
~TPriceDBWriteThread() {
    FExitFlag = true;
    MultiQueue->PostMessage(msg);  // 线程阻塞在 FQueue！
    pthread_join(pt, &nouse);      // 卡死
}

// 正确：投递到正确的队列
~TPriceDBWriteThread() {
    FExitFlag = true;
    FQueue->PostMessage(msg);      // 投递到线程监听的队列
    pthread_join(pt, &nouse);
}
```

### R3.3 锁规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R3.3.1 | 锁粒度最小化，禁止跨 DB 事务持锁 | P1 |
| R3.3.2 | 禁止在持锁状态下调用外部函数 | P1 |
| R3.3.3 | 读写锁与写锁不可升级 | P2 |
| R3.3.4 | 禁止宏式加解锁，使用 RAII | P1 |

**典型问题**:
```cpp
// 错误：锁跨越 DB 事务
LRWST(PositionSums.lock);
DoPosSum();  // 内部有 DB 操作，可能很慢
LED;

// 正确：只在必要临界区持锁
{
    std::unique_lock lock(PositionSums.mutex);
    // 只保护内存状态
    PreparePosSumData(data);
}
DoPosSum();  // DB 操作在锁外
```

---

## 四、安全规则

### R4.1 密码安全规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R4.1.1 | 禁止明文存储密码 | P0 |
| R4.1.2 | 禁止明文传输密码 | P0 |
| R4.1.3 | 禁止日志打印密码 | P0 |
| R4.1.4 | 使用安全哈希算法（bcrypt/PBKDF2/scrypt） | P1 |

**检查命令**:
```bash
# 查找密码明文
grep -rn "password" src/ include/ --include="*.ini" --include="*.cfg"
grep -rn "passwd" src/ include/ --include="*.ini" --include="*.cfg"
```

### R4.2 输入校验规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R4.2.1 | 所有外部输入必须校验 | P0 |
| R4.2.2 | 报文长度必须校验后再 substr | P0 |
| R4.2.3 | sscanf 必须限制宽度 | P1 |
| R4.2.4 | 禁止固定大小缓冲区接收可变长度输入 | P1 |

**典型问题**:
```cpp
// 错误：未校验长度即 substr
string field = data.substr(0, 10);  // data 长度可能 < 10

// 正确：先校验长度
if (data.length() >= 10) {
    string field = data.substr(0, 10);
}
```

---

## 五、代码质量规则

### R5.1 函数复杂度规则

| 规则ID | 规则描述 | 阈值 | 严重程度 |
|--------|----------|------|----------|
| R5.1.1 | 函数长度 ≤ 200 行 | 200 | P2 |
| R5.1.2 | 圈复杂度 ≤ 15 | 15 | P2 |
| R5.1.3 | 嵌套深度 ≤ 4 | 4 | P2 |
| R5.1.4 | 参数数量 ≤ 5 | 5 | P3 |

### R5.2 扇入/扇出规则

| 规则ID | 规则描述 | 阈值 | 严重程度 |
|--------|----------|------|----------|
| R5.2.1 | 高扇入函数（调用者>50）需重点审查稳定性 | 50 | P2 |
| R5.2.2 | 高扇出函数（调用>20）需拆分重构 | 20 | P2 |
| R5.2.3 | 禁止"上帝函数"（扇入>100 且 扇出>30） | - | P1 |

**已知高扇入函数**:
- SendXNetData: 699+ 调用
- UpdateBankPriceInfo: 126+ 调用
- GetRealPubPriceByRealCalcPrice: 104+ 调用

**已知高扇出函数**:
- OnXNetUpdateMKTFeedPrice: 40+ 调用
- LoadDealWith: 50+ 调用

### R5.3 异常处理规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R5.3.1 | 禁止 catch(...){} 空块 | P0 |
| R5.3.2 | 异常必须传播或记录日志 | P0 |
| R5.3.3 | 异常路径必须释放资源 | P0 |
| R5.3.4 | 禁止在 LED 前 throw | P0 |

**典型问题**:
```cpp
// 错误：空 catch 块
try {
    ProcessRequest();
} catch (...) {
    // 异常被吞没
}

// 正确：记录日志并传播
try {
    ProcessRequest();
} catch (std::exception& e) {
    Logger->AddLog("Exception: %s", e.what());
    throw;
} catch (...) {
    Logger->AddLog("Unknown exception");
    throw;
}
```

---

## 六、架构规则

### R6.1 重复代码规则

| 规则ID | 规则描述 | 阈值 | 严重程度 |
|--------|----------|------|----------|
| R6.1.1 | 重复代码块 ≤ 50 行 | 50 | P2 |
| R6.1.2 | 文件重复率 ≤ 10% | 10% | P2 |
| R6.1.3 | 模块重复必须提取公共实现 | - | P1 |

**已知重复代码**:
- psmansvr/rmbpsmansvr DealAction.cpp: ~2000 行
- svswap/svswaphk priceHandle.cpp: ~500 行

### R6.2 分层规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R6.2.1 | 协议层只负责解包，不执行业务逻辑 | P1 |
| R6.2.2 | 业务层不直接操作 SQL | P1 |
| R6.2.3 | 读线程不执行写 SQL | P1 |
| R6.2.4 | 函数名必须反映真实副作用 | P2 |

### R6.3 异步处理规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R6.3.1 | 禁止"先回成功后处理"模式 | P0 |
| R6.3.2 | 异步落库失败必须有补偿机制 | P0 |
| R6.3.3 | 异步写入前不清除内存更新标记 | P0 |

**典型问题**:
```cpp
// 错误：先回成功，后异步写库
xnetData->SetReturnCode(0);
xnetData->Exchange();
SendDataToMainLand(xnetData);  // 先回成功
AddDBTask(sql);                // 后异步写库，可能失败

// 正确：异步完成后再回包
AddDBTask(sql, callback);      // 异步写库
// 在 callback 中回包
```

### R6.4 容器选择规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R6.4.1 | 禁止在循环内对 vector/list 做 std::find | P1 |
| R6.4.2 | 去重操作使用 set/unordered_set，禁止 O(n²) 去重 | P1 |
| R6.4.3 | 预知数量的 push_back 必须先 reserve | P2 |
| R6.4.4 | 仅需尾部操作时用 vector，不用 list | P2 |
| R6.4.5 | 频繁查找的集合用 set/unordered_set | P1 |
| R6.4.6 | 禁止嵌套循环实现去重/合并 | P1 |

**检查命令**:
```bash
# 查找循环内 std::find
grep -rn "std::find.*begin.*end" src/ --include="*.cpp"

# 查找 O(n²) 去重模式
grep -rn "for.*begin.*end" src/ -A 10 | grep "for.*begin.*end"

# 查找缺少 reserve 的 push_back
grep -rn "push_back" src/ --include="*.cpp" | wc -l
grep -rn "reserve" src/ --include="*.cpp" | wc -l
```

**典型问题**:
```cpp
// 错误：循环内对 vector 做 std::find (O(n²))
for (auto& item : items) {
    if (std::find(seen.begin(), seen.end(), item.key) == seen.end()) {
        seen.push_back(item.key);
    }
}

// 正确：使用 set 提前构建 (O(n))
std::unordered_set<std::string> seenSet;
for (auto& item : items) {
    seenSet.insert(item.key);
}

// 错误：O(n²) 去重
for (auto& item : list) {
    for (auto& seen : result) {
        if (item == seen) break;
    }
}

// 正确：使用 set 去重
std::unordered_set<T> seen;
for (const auto& item : list) {
    seen.insert(item);
}
```

**容器选择指南**:

| 需求 | 推荐容器 | 原因 |
|------|----------|------|
| 随机访问 | std::vector | O(1) 访问，缓存友好 |
| 尾部插入/删除 | std::vector | O(1) 均摊 |
| 中间插入/删除频繁 | std::list | O(1) 插入删除 |
| 查找频繁 | std::set / std::unordered_set | O(log n) / O(1) |
| 键值对查找 | std::map / std::unordered_map | O(log n) / O(1) |
| 去重 | std::set / std::unordered_set | 自动去重 |

### R6.5 架构抽象规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R6.5.1 | 禁止复制整个文件/目录后再修改，必须提取公共基类 | P1 |
| R6.5.2 | 新增产品服务必须继承公共基类，差异通过虚函数实现 | P1 |
| R6.5.3 | 同构函数超过 3 个时必须抽象为模板或基类方法 | P1 |
| R6.5.4 | 地域差异(香港/海外)使用策略模式，禁止复制整个服务 | P1 |
| R6.5.5 | 产品差异通过组合/桥接，禁止复制全部代码 | P2 |

**检查命令**:
```bash
# 检测同构文件
find src/ -name "*.cpp" -exec md5sum {} \; | sort | uniq -w32 -D

# 检测重复函数签名
grep -h "^[a-zA-Z_].*::" src/price/*/priceWorkAction.cpp | sort | uniq -c | sort -rn | head -20
```

**典型问题**:
```cpp
// 错误：复制整个服务，仅修改类型名
// svswap/priceWorkAction.cpp (19000+ 行)
// svswaphk/priceWorkAction.cpp (7000+ 行，90%+ 相同)

// 正确：提取基类
class TPriceServiceBase {
public:
    void OnXNetReqEffectParam(TMsgPkg* msg);  // 通用实现
    void OnThreadBakEffectParam(TMsgPkg& msg);
protected:
    virtual std::string GetProductType() = 0;  // 差异点
    virtual void CalculatePrice(TMode& mode) = 0;
};

class TSwapService : public TPriceServiceBase {
    // 仅实现差异部分，约 2000 行
};
```

**差异模式统计**:

| 差异类型 | 占比 | 处理方式 |
|----------|------|---------|
| 类型名称不同 | 60% | 模板参数化 |
| 配置/参数不同 | 25% | 配置注入 |
| 业务规则微调 | 10% | 策略模式 |
| 真正差异 | 5% | 子类实现 |

**复制代码检测阈值**:

| 指标 | 阈值 | 处理 |
|------|------|------|
| 文件相似度 | > 70% | 必须合并 |
| 函数相似度 | > 80% | 必须提取 |
| 代码块重复 | > 50 行 | 必须重构 |

### R6.6 缓存与性能规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R6.6.1 | 热点计算函数必须有输入变化检测或缓存 | P1 |
| R6.6.2 | 循环内禁止重复查询，移到循环外 | P1 |
| R6.6.3 | 热数据类大小应 < 1KB，超过需拆分冷热数据 | P2 |
| R6.6.4 | 高频访问数据结构需缓存行对齐 (alignas(64)) | P2 |
| R6.6.5 | 工作线程应设置CPU亲和性 (pthread_setaffinity) | P2 |
| R6.6.6 | 批量处理使用连续内存容器 (vector)，避免链表 | P2 |
| R6.6.7 | 大对象优先使用指针而非值拷贝传递 | P1 |

**检查命令**:
```bash
# 查找热点计算函数（无缓存）
grep -rn "Calculate\|Calc\|Compute" src/ --include="*.cpp" | wc -l

# 查找循环内重复查询
grep -rn "for.*{" src/ -A 10 --include="*.cpp" | grep "GetParamByName\|GetData"

# 查找大对象定义
grep -rn "class.*Item" include/ --include="*.h" -A 100 | grep "std::string" | wc -l

# 查找线程亲和性设置
grep -rn "pthread_setaffinity\|cpu_set_t" src/
```

**典型问题**:
```cpp
// 错误：每次都重新计算
void CalculatePrice(TInput& input) {
    // 没有检查输入是否变化
    result = HeavyCalculation(input);
}

// 正确：输入变化检测 + 缓存
class TPriceCache {
    std::map<std::string, double> Cache;
    std::map<std::string, size_t> InputHash;
    
    double GetOrCalculate(const std::string& key, const TInput& input) {
        auto hash = std::hash<TInput>{}(input);
        if (InputHash[key] != hash) {
            Cache[key] = HeavyCalculation(input);
            InputHash[key] = hash;
        }
        return Cache[key];
    }
};
```

**内存布局优化**:
```cpp
// 错误：热数据和冷数据混在一起，大对象
class TBankBaseItem {
    // 热数据（每次计算用）
    double SpotBid, SpotAsk;
    // 冷数据（很少用，但占据内存）
    std::string BankName, ClName;  // 478个字符串...
};

// 正确：分离冷热数据
struct TBankHotData {
    alignas(64) double SpotBid, SpotAsk;
    // 总大小 < 256 字节，缓存友好
};

struct TBankBaseItem {
    TBankHotData HotData;  // 内嵌热点数据
    std::shared_ptr<TColdData> ColdData;  // 冷数据按需加载
};
```

**线程亲和性设置**:
```cpp
// 当前：没有设置线程亲和性
pthread_create(&pt, &attr, &CreateThread, (void*)this);
pthread_setname_np(pt, "WorkThread");

// 正确：绑定到指定CPU核心
#include <sched.h>
void SetThreadAffinity(pthread_t thread, int cpu) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu, &cpuset);
    pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
}

pthread_create(&pt, &attr, &CreateThread, (void*)this);
SetThreadAffinity(pt, thread_id % std::thread::hardware_concurrency());
```

**性能影响量化**:

| 优化项 | 当前 | 优化后 | 改进 |
|--------|------|--------|------|
| 计算缓存 | 每次重算 | 命中返回 | 30-50% CPU |
| L2缓存命中率 | ~30% | ~80% | 2.7x |
| 线程迁移 | 频繁 | 固定核心 | 延迟稳定 |

### R6.7 线程模型规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R6.7.1 | 线程数量应根据CPU核心数动态配置，禁止硬编码 | P1 |
| R6.7.2 | 工作线程应设置CPU亲和性 (pthread_setaffinity) | P2 |
| R6.7.3 | 线程池应支持工作窃取 (Work Stealing) | P2 |
| R6.7.4 | 关键任务应有优先级支持 | P2 |
| R6.7.5 | 新代码使用 std::thread 而非 pthread | P3 |
| R6.7.6 | 线程数 > CPU核心数时需评估必要性 | P2 |

**检查命令**:
```bash
# 检查硬编码线程数
grep -rn "AThreadTotal.*=.*[0-9]\|ThreadCount.*=.*[0-9]" src/ --include="*.cpp"

# 检查CPU亲和性设置
grep -rn "pthread_setaffinity\|cpu_set_t" src/

# 检查现代C++并发使用
grep -rn "std::thread\|std::async\|std::future" src/
```

**典型问题**:
```cpp
// 错误：固定线程数
int threadCount = 1;  // 或从配置文件读取固定值
ThreadPool pool(threadCount);

// 正确：动态计算
int threadCount = std::thread::hardware_concurrency();
ThreadPool pool(std::max(2, threadCount - 1));  // 保留1核给系统

// 错误：无CPU亲和性
pthread_create(&pt, &attr, &CreateThread, (void*)this);

// 正确：绑定到指定CPU核心
pthread_create(&pt, &attr, &CreateThread, (void*)this);
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(core_id, &cpuset);
pthread_setaffinity_np(pt, sizeof(cpu_set_t), &cpuset);
```

**多核利用率影响**:

| CPU核心数 | 固定线程模型 | 动态线程模型 | 性能损失 |
|-----------|-------------|-------------|---------|
| 4核 | ~50% | ~90% | 40% |
| 8核 | ~30% | ~90% | 60% |
| 16核 | ~20% | ~90% | 70% |
| 32核 | ~15% | ~90% | 75% |

---

## 七、协议语义规则

### R7.1 回包规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R7.1.1 | ReturnCode 必须反映真实处理结果 | P0 |
| R7.1.2 | 禁止丢弃错误返回包 | P0 |
| R7.1.3 | 未注册 action 必须回"NoMethod"错误 | P1 |
| R7.1.4 | 异常必须回错误包，不能只记录日志 | P0 |

### R7.2 主从切换规则

| 规则ID | 规则描述 | 严重程度 |
|--------|----------|----------|
| R7.2.1 | 禁止 exit(0) 粗暴退出 | P0 |
| R7.2.2 | 切换前必须排空队列 | P0 |
| R7.2.3 | 切换时必须有 fencing 机制 | P1 |
| R7.2.4 | 清理临时表必须有归属校验 | P1 |

---

## 八、检查清单

### 8.1 新代码提交前检查

- [ ] new/delete 数量匹配
- [ ] 无 SQL 字符串拼接
- [ ] pthread_create 后有 pthread_setname_np
- [ ] 无密码明文
- [ ] 函数长度 ≤ 200 行
- [ ] 无空 catch 块
- [ ] 锁使用 RAII 守卫
- [ ] 异步操作有错误处理
- [ ] 循环内无 std::find 对 vector/list
- [ ] 批量 push_back 有 reserve

### 8.2 重构前检查

- [ ] 高扇入函数稳定性审查
- [ ] 高扇出函数拆分方案
- [ ] O(n²) 算法优化方案
- [ ] 容器选择合理性审查
- [ ] 同构模块差异清单
- [ ] 热点函数缓存策略
- [ ] 内存布局优化方案
- [ ] 测试覆盖

### 8.3 新增服务前检查

- [ ] 是否有可继承的基类
- [ ] 差异点是否可通过虚函数/策略实现
- [ ] 是否需要复制现有服务（禁止）
- [ ] 产品差异是否已参数化

### 8.4 发布前检查

- [ ] P0 问题已修复
- [ ] P1 问题有缓解方案
- [ ] 配置文件无硬编码密码
- [ ] SQL 清单核对
- [ ] 同构模块扫描完成

---

