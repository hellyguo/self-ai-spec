---
name: java-asprof
description: "使用 async-profiler 采集 Java 进程的 CPU、内存分配、锁等运行时数据，生成火焰图或采样报告。适用于 Java 性能瓶颈定位、CPU 与内存热点分析、锁竞争排查。"
---

# Java 运行时采样（async-profiler）

使用 async-profiler 对运行中的 Java 进程采样，采集 CPU、内存分配、锁等事件，用于性能瓶颈定位。

## 前置条件

1. 通过 skill `java-env` 确认 JDK 版本与 mvnd/mvn，保证 `jps`、`asprof` 与目标进程使用同一 JDK。
2. 确认 async-profiler 路径：`${HOME}/app/async-profiler`。
3. 确认目标进程 PID 或可唯一匹配的进程名。

## 执行步骤

1. `jps -l` 列出 Java 进程，确认目标 PID 与主类。
2. 选择采样事件：
   - `cpu`：CPU 热点，最常用
   - `alloc`：内存分配热点
   - `lock`：锁竞争
   - `wall`：墙钟耗时（包含等待）
   - `itimer` / `ctimer`：按定时器采样
3. 执行采样，产物写入 `/tmp/profile.txt`（可按需改为 `.html` 或 `.jfr`）。
4. 读取采样结果，定位热点函数并给出优化建议。

## 命令模板

参数说明：`<event>` 为采样事件，`<duration>` 为采样秒数，`<output>` 为输出文件，`<pattern>` 为进程名或主类关键字。

```bash
# 按进程名匹配 PID
PID=$(jps -l | grep '<pattern>' | cut -d' ' -f1)

# 基础采样
asprof -i 1000 -e <event> -d <duration> -f <output> "$PID"

# 采样线程栈
asprof -i 1000 -e <event> -t -d <duration> -f <output> "$PID"

# 使用 dwarf 解析 C 栈（JVM 内 native 调用较多时）
asprof -i 1000 -e <event> -t -d <duration> --cstack dwarf -f <output> "$PID"
```

## 输出与判读

- 火焰图（`.html`）：横向宽度代表耗时占比，优先关注宽而深的调用链。
- 采样文本：按栈帧聚合的采样计数，计数越高说明该路径越热。
- 内存分配采样：关注 `alloc` 事件中占比高的分配点，结合对象生命周期判断是否为泄漏或高频短命对象。

## 注意事项

- 采样时长应覆盖完整业务周期，过短容易失真。
- 生产环境采样有性能开销，建议使用 `-i` 控制采样间隔并避免长时间采样。
- 采样结果必须结合代码与调用链复核，不能只凭火焰图宽度下结论。
