# 排错与依赖处理

`SKILL.md` 的主流程在此处不再重复；本页按“先看现象、再定位依赖”的顺序组织。

## 常见问题

| 现象 | 原因 | 处理 |
| :--- | :--- | :--- |
| `unable to find dynamic system library 'objc' / 'iconv' / 'charset'` | 未把 SDK 的 `usr/lib` 加入库搜索路径 | 增加 `-L$SDK/usr/lib` |
| 警告 `unable to open library directory '/sdk/sdk/usr/lib'`，路径被重复拼接 | 设置了 `SDKROOT`，zig 将其作为 sysroot 并给绝对 `-L` 再加前缀 | `unset SDKROOT`，改用显式 `-L` 与 `-F` |
| `warning: invoking xcrun ... failed` | 无 Xcode，无法读取 SDK 版本 | 可忽略；不影响链接与签名，或安装完整 Xcode |
| `framework not found AppKit/OpenGL` | 缺少 `-F` 框架路径 | 增加 `-F$SDK/System/Library/Frameworks` |
| `minos` 高于目标机器 | 默认部署目标过高 | 设置 `MACOSX_DEPLOYMENT_TARGET` |
| Apple Silicon 上提示签名无效或直接退出 | 链接器未写入 ad-hoc 签名 | 使用 zig 链接；其他链接器需 `-Wl,-adhoc_codesign` 或 `rcodesign` |
| 下载后提示“无法验证开发者” | Gatekeeper 隔离属性 | `xattr -dr com.apple.quarantine <App>.app`，或右键打开 |
| 依赖 C/C++ 库时链接失败 | SDK 库版本或 libc++ 不匹配 | 用 `zig c++`，显式指定 SDK；必要时改用 osxcross |
| `ring`、`openssl-sys` 等构建脚本失败 | 构建脚本调用了本机 cc/ar | 设置 `CC_<target>`、`AR_<target>` 指向 zig 包装器，或启用 vendored 特性 |
| `cargo build --target ...` 能编译但链接失败 | 用了 cargo 而非 cargo-zigbuild | 改用 `cargo zigbuild` |
| 运行时报找不到 `libonnxruntime.dylib` / `.so` | 构建时是动态链接，但归档只带主二进制 | 用 `otool -L` / `ldd` 确认，按需把库放进包内并用 `@loader_path`、`@rpath` 或 `$ORIGIN` 引用 |
| macOS 提示“已损坏”而不是“无法验证开发者” | 完全未签名，或签名被 strip/lipo 破坏 | 在打包前最后一步重签，并 `xattr -dr com.apple.quarantine` |
| 产物包名里的架构是构建机架构 | 打包脚本自动探测架构 | 平台标识必须显式传参，交叉构建时禁止自动探测 |
| 发布 tag 与 Cargo.toml 版本不一致 | 手动发版常见 | CI 校验 tag 去掉 `v` 后与 Cargo 版本（去 `-dev`）一致 |

## Rust 重依赖与开关

| 依赖 | 交叉要点 |
| :--- | :--- |
| `openssl-sys` | 直接改用 rustls。`fastembed` 默认 `native-tls` 会拉 OpenSSL，需 `default-features = false` 并启用 `ort-download-binaries-rustls-tls`、`hf-hub-rustls-tls`；`reqwest` 用 `rustls-tls-native-roots` |
| `librocksdb-sys` | 需要 libclang/bindgen 与目标 `CC`/`CXX`/`AR`；macOS 交叉还要求 SDK 内 libc++。多数情况下这是放弃交叉、改用原生 runner 的主因 |
| `ort` / ONNX Runtime | 按目标下载预编译库，交叉目标通常没有对应产物。构建后用 `ldd`/`otool -L` 确认是静态链接还是需要随包分发 dylib |
| `rusqlite`（`bundled`） | 目标平台 C 编译器即可；Windows 需 `CC_x86_64_pc_windows_msvc` |
| `zstd-sys` | 部分目标可关 asm 特性，避免交叉汇编器问题 |
| `ring` | 含汇编，交叉 aarch64 容易失败；可考虑整体换到 rustls 体系 |

## 排查顺序

1. `cargo tree -i openssl-sys`，确认有没有非预期引入。
2. 检查各 `-sys` crate 是否在调用本机 `cc`/`ar`（构建脚本日志里能看到实际命令）。
3. 最后才怀疑 zig 版本；zig 与 cargo-zigbuild 不兼容时通常表现为难以定位的链接错误。
