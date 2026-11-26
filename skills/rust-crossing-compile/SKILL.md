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

### 3. 校验

```bash
file target/${TARGET}/release/<binary>
llvm-objdump --macho --dylibs-used target/${TARGET}/release/<binary>
llvm-objdump --macho --private-headers target/${TARGET}/release/<binary> | grep -A4 LC_BUILD_VERSION
llvm-objdump --macho --private-headers target/${TARGET}/release/<binary> | grep -A2 LC_CODE_SIGNATURE
```

也可使用本技能脚本：`scripts/verify-macho.py <binary>`，一次性输出架构、最低系统、依赖库与是否 ad-hoc 签名。

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

1. 缓存 `~/.cargo`、`target`、`~/.cache/cargo-zigbuild` 与 zig 安装目录。
2. SDK 不入库，使用私有制品或 CI secret 挂载。
3. 产物统一命名 `<app>-<version>-macos-<arch>.zip`，同时输出 SHA-256。
4. 在 macOS runner 上做最终启动验收；交叉编译只做格式、依赖与签名静态校验。
5. 将 SDK 路径、部署目标、目标三元组作为参数，不要在脚本中硬编码。

## 验收清单

- [ ] `file` 显示 `Mach-O 64-bit arm64`
- [ ] `LC_BUILD_VERSION` 的 `platform` 为 `macos`，`minos` 符合预期
- [ ] 依赖库均为系统路径，无本机绝对路径
- [ ] 存在 `LC_CODE_SIGNATURE` 且为 ad-hoc
- [ ] `.app` 内可执行文件有执行权限
- [ ] `Info.plist` 可被解析，bundle id 与可执行名正确
- [ ] 压缩包解压后权限不变
- [ ] 在 Apple Silicon 机器上完成启动与核心功能验收

## 安全与合规

1. Apple SDK 受许可约束，不要提交到代码仓库或公开分发。
2. ad-hoc 签名只解决本机运行，不等同于可信任分发；对外发布需 Developer ID 签名与公证。
3. 交叉编译产物含本机路径信息时，检查是否泄露构建环境；必要时使用 `strip` 与可复现构建参数。
