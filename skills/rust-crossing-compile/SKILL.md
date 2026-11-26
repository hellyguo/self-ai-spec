---
name: rust-crossing-compile
description: "在 Linux/Windows 上用 zig 交叉编译 Rust 到 macOS arm64/x86_64，覆盖 SDK 与框架链接、SDKROOT 陷阱、ad-hoc 签名、Mach-O 校验、.app 打包与常见链接错误排查。适用于无 macOS 构建机、CI 产出 macOS 安装包、Apple Silicon 分发前验证。"
---

# Rust macOS 交叉编译（zig）

> 本文件中的 `scripts/...` 均指本技能目录下的 `scripts/` 子目录。
> 目标：在没有 macOS 构建机的环境下，用 zig 作为链接器产出可运行的 Mach-O 二进制与 `.app`。

## 适用场景

| 场景 | 是否适用 |
|---|---|
| Linux/Windows 交叉编译 macOS arm64 | 适用 |
| CI 中产出 macOS 压缩包 | 适用 |
| 纯 Rust 或少量系统框架依赖的 GUI/CLI | 适用 |
| 大量 Objective-C/Swift 源码、需要 Xcode 工程 | 不适用，改用 macOS 构建机或 osxcross 完整工具链 |
| 需要 Developer ID 签名与公证 | 部分适用，签名与公证仍需额外工具或 macOS 机器 |

## 先决策：是否值得交叉编译

交叉编译的难点通常不在 Rust 代码，而在 C/C++ 依赖与平台预编译产物。先按依赖形态判断：

| 依赖特征 | 建议 | 原因 |
|---|---|---|
| 纯 Rust，或仅 `libc` / 系统框架 | 交叉编译 | zig 足够，成本最低 |
| 含 RocksDB、ONNX Runtime、bundled SQLite、libgit2 | 优先原生 runner 或构建机 | C++ 工具链、预编译二进制、libc++ 版本三者需要同时对齐 |
| 仅 Linux aarch64 | 交叉编译可行 | `gcc-aarch64-linux-gnu` 自带 libstdc++，C++ 依赖可正常链接 |
| 需要公证或 Developer ID | 必须 macOS 机器 | zig 只能做 ad-hoc 签名 |

经验矩阵：Linux x86_64、macOS、Windows 使用原生 runner；只有 Linux aarch64 用交叉工具链。这样既避开 macOS/Windows 的 C++ 依赖问题，又保留了最常见的跨架构发布能力。

## 方案选型

| 方案 | 优点 | 代价 | 建议 |
|---|---|---|---|
| `cargo-zigbuild` + zig | 安装简单、单一链接器、自动 ad-hoc 签名、跨架构 | 需要 macOS SDK 的 tbd 存根；对 C++/ObjC 复杂依赖支持有限 | 首选 |
| osxcross | 完整 clang 工具链、支持 ObjC/C++ | 配置重、编译慢、依赖 SDK 与 cctools | 大型混合工程 |
| GitHub Actions macOS runner | 原生工具链、可直接签名公证 | 受 CI 配额与网络限制 | 发布流水线 |
| 本地 macOS | 最可靠 | 需要硬件 | 最终验收 |

## 前置条件

| 依赖 | 说明 |
|---|---|
| Rust 目标 | `rustup target add aarch64-apple-darwin`（x86_64 同理） |
| cargo-zigbuild | `cargo install cargo-zigbuild`，版本需与 zig 兼容 |
| zig | 加入 PATH；`cargo-zigbuild` 会调用 `zig cc` |
| macOS SDK | 合法的 `MacOSX*.sdk` 目录，提供 `usr/lib/*.tbd` 与 `System/Library/Frameworks` |
| LLVM 工具（可选） | `file`、`llvm-objdump`、`llvm-lipo`，用于静态验证与合并 |

## Rust 重依赖与开关

| 依赖 | 交叉要点 |
|---|---|
| `openssl-sys` | 直接改用 rustls。`fastembed` 默认 `native-tls` 会拉 OpenSSL，需 `default-features = false` 并启用 `ort-download-binaries-rustls-tls`、`hf-hub-rustls-tls`；`reqwest` 用 `rustls-tls-native-roots` |
| `librocksdb-sys` | 需要 libclang/bindgen 与目标 `CC`/`CXX`/`AR`；macOS 交叉还要求 SDK 内 libc++。多数情况下这是放弃交叉、改用原生 runner 的主因 |
| `ort` / ONNX Runtime | 按目标下载预编译库，交叉目标通常没有对应产物。构建后用 `ldd`/`otool -L` 确认是静态链接还是需要随包分发 dylib |
| `rusqlite`（`bundled`） | 目标平台 C 编译器即可；Windows 需 `CC_x86_64_pc_windows_msvc` |
| `zstd-sys` | 部分目标可关 asm 特性，避免交叉汇编器问题 |
| `ring` | 含汇编，交叉 aarch64 容易失败；可考虑整体换到 rustls 体系 |

排查顺序：先看 `cargo tree -i openssl-sys` 有没有非预期引入，再看各 `-sys` crate 是否在调用本机 `cc`/`ar`，最后才怀疑 zig 版本。

## 核心原理

1. `cargo-zigbuild` 把 `zig cc` 包装成 rustc 的链接器，rustc 仍负责编译 Rust 目标代码。
2. zig 内置 libSystem 存根，但 AppKit、OpenGL、CoreFoundation、objc、iconv 等需要 macOS SDK 的 `.tbd` 文件。
3. zig 链接器默认为 Mach-O 写入 ad-hoc 代码签名，满足 Apple Silicon 对未签名 arm64 二进制的运行限制。
4. 部署目标由 `MACOSX_DEPLOYMENT_TARGET` 决定，写入 `LC_BUILD_VERSION.minos`。

## 标准流程

### 1. 设置环境

```bash
export TARGET=aarch64-apple-darwin
export MACOS_SDK_ROOT=/path/to/MacOSX14.5.sdk
export MACOSX_DEPLOYMENT_TARGET=13.0

# 关键：不要设置 SDKROOT，原因见“常见问题”
unset SDKROOT

# 推荐使用目标专属变量，避免污染本机编译
export CARGO_TARGET_AARCH64_APPLE_DARWIN_RUSTFLAGS="\
-C link-arg=-L${MACOS_SDK_ROOT}/usr/lib \
-C link-arg=-F${MACOS_SDK_ROOT}/System/Library/Frameworks"
```

也可以写入 `.cargo/config.toml`，但不要提交包含本机 SDK 绝对路径的配置。

### 2. 构建

```bash
rustup target add "${TARGET}"
cargo zigbuild --release --target "${TARGET}"
```

指定包与产物：

```bash
cargo zigbuild --release --target "${TARGET}" -p <package>
```

### 3. 三平台校验

**macOS**

```bash
file target/${TARGET}/release/<binary>
llvm-objdump --macho --dylibs-used target/${TARGET}/release/<binary>
llvm-objdump --macho --private-headers target/${TARGET}/release/<binary> | grep -A4 LC_BUILD_VERSION
llvm-objdump --macho --private-headers target/${TARGET}/release/<binary> | grep -A2 LC_CODE_SIGNATURE
codesign --verify --verbose=2 target/${TARGET}/release/<binary>
```

也可使用本技能脚本：`scripts/verify-macho.py <binary>`，一次性输出架构、最低系统、依赖库与是否 ad-hoc 签名。

依赖列表里不允许出现构建机绝对路径；随包分发的 dylib 应以 `@loader_path` 或 `@rpath` 引用。

**Linux**

```bash
file <binary>
readelf -d <binary> | grep -E 'RPATH|RUNPATH'
objdump -T <binary> | grep -o 'GLIBC_[0-9.]*' | sort -Vu | tail -1
```

`GLIBC_` 的最高符号版本决定可运行的最低发行版。要在越老的发行版上构建，下界越低；宁可旧构建机，不要用 latest 镜像。不要保留指向构建机目录的 `RUNPATH`。

**Windows**

```powershell
dumpbin /dependents <binary>.exe
dumpbin /headers <binary>.exe | findstr /i "subsystem"
```

确认没有依赖未随包分发的 VC 运行库；优先使用静态 CRT（`+crt-static`）。

### 4. 组装 .app

```text
<App>.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/<executable>
│   └── Resources/
```

要求：

1. 可执行文件必须有执行权限。
2. `Info.plist` 至少包含 `CFBundleExecutable`、`CFBundleIdentifier`、`CFBundleName`、`CFBundlePackageType`、`LSMinimumSystemVersion`。
3. 复制后不要重写二进制，否则会破坏已有签名。

签名顺序是硬约束：

```text
strip → lipo（可选）→ codesign → 打包 → 不再改动二进制
```

`strip` 与 `lipo` 都会让签名失效，所以签名必须是最后一步。`.app` 先签内层可执行文件，再签 bundle；不建议依赖 `codesign --deep`。

打包脚本见 `scripts/build-macos-arm64.sh`，以环境变量注入应用名、包名与 bundle id。

### 5. 压缩与校验

```bash
(cd dist && zip -qry app-macos-arm64.zip <App>.app)
(cd dist && sha256sum app-macos-arm64.zip > app-macos-arm64.zip.sha256)
```

`zip` 会保留执行权限；不要用会丢失权限的归档方式。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
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

## 架构扩展

### x86_64 与通用二进制

```bash
rustup target add x86_64-apple-darwin
cargo zigbuild --release --target x86_64-apple-darwin
llvm-lipo -create \
  target/aarch64-apple-darwin/release/<binary> \
  target/x86_64-apple-darwin/release/<binary> \
  -output dist/<binary>-universal
```

合并后重新校验架构与签名；`lipo` 合并可能使原签名失效，需要重新签名。

### 其他 Apple 平台

iOS/tvOS 等目标需要对应 SDK、签名证书与 entitlements，且通常涉及 Xcode 工程，不适合仅靠 zig 完成，建议使用原生 macOS 构建机。

## CI 建议

1. 缓存 `~/.cargo`、`target`、`~/.cache/cargo-zigbuild` 与 zig 安装目录；`Swatinem/rust-cache` 的 key 必须带目标三元组，否则不同架构互相污染。
2. SDK 不入库，使用私有制品或 CI secret 挂载；固定 zig 与 cargo-zigbuild 版本，二者不兼容时常表现为难以定位的链接错误。
3. 产物统一命名 `<app>-<version>-macos-<arch>.zip`，同时输出 SHA-256。
4. 在 macOS runner 上做最终启动验收；交叉编译只做格式、依赖与签名静态校验。
5. 将 SDK 路径、部署目标、目标三元组作为参数，不要在脚本中硬编码。
6. 矩阵构建使用 `fail-fast: false`，避免一个平台失败掩盖其余平台的真实状态。
7. 原生 runner 与交叉任务可以混编：Linux x86_64、macOS、Windows 走原生，Linux aarch64 走 `gcc-aarch64-linux-gnu` 交叉，并在交叉任务里设置 `CC_/CXX_/AR_<target>`、`CARGO_TARGET_<TARGET>_LINKER`、`PKG_CONFIG_ALLOW_CROSS=1`。
8. 发布前校验 tag 与 workspace 版本一致，并在归档脚本里显式传入平台标识（禁止自动探测）。

## 验收清单

- [ ] `file` 显示 `Mach-O 64-bit arm64`
- [ ] `LC_BUILD_VERSION` 的 `platform` 为 `macos`，`minos` 符合预期
- [ ] 依赖库均为系统路径或随包分发的 `@rpath`，无本机绝对路径
- [ ] 存在 `LC_CODE_SIGNATURE` 且为 ad-hoc
- [ ] Linux 产物最高 `GLIBC_` 符号不超过目标发行版，且无构建机 `RUNPATH`
- [ ] Windows 产物不依赖未分发的 VC 运行库（或已显式声明）
- [ ] `.app` 内可执行文件有执行权限
- [ ] `Info.plist` 可被解析，bundle id 与可执行名正确
- [ ] 归档格式保留执行权限（Unix 优先 `tar.gz`；`zip` 需确认权限位）
- [ ] 归档附 `.sha256`，且与发布版本号一致
- [ ] 在 Apple Silicon 机器上完成启动与核心功能验收

## 安全与合规

1. Apple SDK 受许可约束，不要提交到代码仓库或公开分发。
2. ad-hoc 签名只解决本机运行，不等同于可信任分发；对外发布需 Developer ID 签名与公证。
3. 交叉编译产物含本机路径信息时，检查是否泄露构建环境；必要时使用 `strip` 与可复现构建参数。
