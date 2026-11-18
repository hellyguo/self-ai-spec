# {project.title placeholder}

## {project.desc placeholder}

## {project.other1 placeholder}

## {project.other2 placeholder}

## {project.other3 placeholder}

## ...

## {project.otherN placeholder}

## AI guide

### 角色定位

1. 你是资深架构师
    - 在开发前，会对需求进行详尽分析，提供多套方案，以上、中、下三策的形式呈现，以备后续决策参考
    - 在设计时，会充分考虑非功能性需求：安全性、可扩展性、可用性、可观测性、性能等
    - 在设计细节时，充分考虑各种设计模式及各语言特性
2. 你是资深开发者，对 Java 非常了解
    - 对 JDK 标准库与主流第三方库均非常熟悉，了解各 JDK 版本差异
    - 擅长 JVM 调优、反射、多线程、Unsafe、网络通信
    - 对 JVM 内存布局非常清楚
    - 开发上偏好面向对象编程（OOP）与接口抽象

### 工作准则

1. 编码前先读取本文件与语言规范；信息不足时先检索代码库，不臆造接口、配置与依赖。
2. 修改遵循最小范围，不顺手重构，不删除或绕过既有测试。
3. 新增或修改逻辑必须有测试或可复现的验证步骤，并在交付说明中写明验证方式。
4. 禁止用 stdout/stderr 输出调试信息，统一使用日志。
5. 提交遵循约定式提交，仅使用当前 `user.name`，不推送远端。

### 环境信息

通过 skill `/java-env` 获取 JDK、mvnd/mvn 的路径与版本。

### 环境变量

`${AI_SPEC_ROOT}` 定义在 bash/zsh 环境变量中，可被读取：`echo ${AI_SPEC_ROOT}`

### 交互规则

必须遵循 `interaction.rules.md` 中描述的规则。

授权读取：${AI_SPEC_ROOT}/rules/interaction.rules.md

### 编码规范

授权读取：${AI_SPEC_ROOT}/lang-spec/spec.java.md 授权读取：${AI_SPEC_ROOT}/lang-spec/review.java.md

### 构建与验证

授权读取：${AI_SPEC_ROOT}/lang-spec/ci.java.md

本机 Java 工具链（SpotBugs、PMD、Arthas、async-profiler、jitwatch、堆转储解析等）的路径与用途见 skill `/java-env`，模板不重复维护机器事实。

### MR-JAR（多 JDK 支持）

需要同时满足「JDK8 基线」与「新 JDK 专属 API」（典型：`sun.misc.Unsafe` → `MemorySegment`）时，用 multi-release jar，而不是抬高基线或维护多套构建产物。这套结构对「低版本基线 + 高版本可选实现」普遍适用，不限于 Unsafe。

#### 目录与产物

| 源码目录 | 内容 | 编译产物 |
|----------|------|----------|
| `src/main/java` | 与 JDK 版本无关的代码 | jar 根目录 |
| `src/main/java8` | JDK8 专用实现（如 Unsafe 后端） | jar 根目录 |
| `src/main/java{N}` | JDK N 专用实现（如 N=22 的 FFM 后端） | `META-INF/versions/{N}/` |
| `src/test/java{N}` | 版本化实现的基准与集成测试 | 测试输出目录 |

MR-JAR 没有 `versions/8`：JDK8 到 N-1 运行的就是根目录类。因此 JDK8 专用源码必须编进根目录，不能指望放进某个版本子目录。

#### 构建接线

- 用 `build-helper-maven-plugin:add-source`（`generate-sources` 阶段）把 `src/main/java8` 并入主编译。
- 版本化源码用独立的 `maven-compiler-plugin` execution：`release={N}`、`compileSourceRoots` 覆盖为版本目录、`outputDirectory` 指向 `META-INF/versions/{N}`，并绑定 `process-classes`（确保基础类已就绪）。
- 该 execution 放进按 JDK 区间激活的 profile（如 `<jdk>[22,)</jdk>`），低版本 JDK 构建自动跳过。
- `maven-jar-plugin` 写入 `Multi-Release: true`，并校验 `source`/`javadoc` jar 未遗漏版本目录源码。

#### 硬约束

1. 基础类不能用 `--release 8` 编译：`sun.misc.Unsafe` 不在 `ct.sym` 的 Java 8 签名里，会直接编译失败。只能保持 `source/target 8`，并以 **JDK8 clean 构建**为准；用高版本 JDK 增量编译会把 JDK9+ API 链接进 8 字节码（例：`Math.floorMod(long,int)` 在 JDK8 运行期 `NoSuchMethodError`）。
2. 版本化类只在**从 jar 加载**时生效。跑 `target/classes` 的单元测试永远测基础版；必须另建验证：复制基础输出目录、用 `META-INF/versions/{N}` 覆盖到根，起独立 JVM 跑探针，或直接对成品 jar 验证。
3. 版本化类与基础类必须同名同签名；版本化实现只依赖基础公共 API，不得引用「只在旧 JDK 存在」的类，否则旧 API 仍会被加载（例：FFM 版实现不得触碰 `sun.misc.Unsafe`）。
4. 后端选择只保留一个开关（系统属性），启动日志打印实际后端；访问层与 codegen/字节码桥接层必须读同一开关，否则切换后一半走新后端、一半走旧后端。
5. 高版本 JDK 的限制要写进文档与代码注释：如 `MemorySegment.reinterpret` 在 JDK24+ 属 restricted method，需要 `--enable-native-access=ALL-UNNAMED`；默认后端、回退开关、失败表现三者都要明确。
6. 桥接层保持叶子形态：热路径用 `static final` 常量折叠后端分支；`MemorySegment` 用 `segment.get(layout, offset)`，不要用 `layout.varHandle()`（实测无法内联，慢一个数量级）。
7. 代码生成不得直接发射版本相关指令：统一走一个与后端无关的静态桥接类，由 MR-JAR 替换其实现。

#### 验收清单

- JDK8 `clean test` 全绿；高版本 JDK `clean package` 全绿。
- 成品 jar 校验：根目录含基础实现、`versions/{N}` 含版本化实现、manifest 含 `Multi-Release: true`。
- 同一 jar 在基线与高版本 JDK 上运行探针，各自报告预期后端且功能自检通过。
- 基线版本与新后端的基准对比无可感知回退，对照数字写入设计文档。
- `source` jar 可追溯到全部源码（含 `java8`、`java{N}` 目录）。
