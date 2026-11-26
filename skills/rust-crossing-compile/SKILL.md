---
name: rust-crossing-compile
description: "在 Linux/Windows 上用 zig 交叉编译 Rust 到 macOS arm64/x86_64，覆盖 SDK 与框架链接、SDKROOT 陷阱、ad-hoc 签名、Mach-O 校验、.app 打包与常见链接错误排查。适用于无 macOS 构建机、CI 产出 macOS 安装包、Apple Silicon 分发前验证。"
---

# Rust macOS 交叉编译（zig）

> 本文件中的 `scripts/...` 与 `references/...` 均指本技能目录下的对应子目录。
>
> 目标：在没有 macOS 构建机的环境下，用 zig 作为链接器产出可运行的 Mach-O 二进制与 `.app`。

## 适用场景与选型

适用：没有 macOS 构建机，需要产出 arm64/x86_64 的 Mach-O 二进制、`.app` 或 CI 压缩包；依赖以纯 Rust 或少量系统框架为主。

部分适用：需要 Developer ID 签名与公证时，二进制可以交叉产出，但签名与公证仍需额外工具或 macOS 机器。

不适用：大量 Objective-C/Swift 源码且需要 Xcode 工程。

交叉编译的难点通常不在 Rust 代码，而在 C/C++ 依赖与平台预编译产物，因此先按依赖形态判断，再选方案。

| 依赖特征 | 建议 | 原因 |
| :--- | :--- | :--- |
| 纯 Rust，或仅 `libc` / 系统框架 | 交叉编译 | zig 足够，成本最低 |
| 含 RocksDB、ONNX Runtime、bundled SQLite、libgit2 | 优先原生 runner 或构建机 | C++ 工具链、预编译二进制、libc++ 版本三者需要同时对齐 |
| 仅 Linux aarch64 | 交叉编译可行 | `gcc-aarch64-linux-gnu` 自带 libstdc++，C++ 依赖可正常链接 |
| 需要公证或 Developer ID | 必须 macOS 机器 | zig 只能做 ad-hoc 签名 |

经验矩阵：Linux x86_64、macOS、Windows 使用原生 runner；只有 Linux aarch64 用交叉工具链。这样既避开 macOS/Windows 的 C++ 依赖问题，又保留了最常见的跨架构发布能力。

| 方案 | 优点 | 代价 | 建议 |
| :--- | :--- | :--- | :--- |
| `cargo-zigbuild` + zig | 安装简单、单一链接器、自动 ad-hoc 签名、跨架构 | 需要 macOS SDK 的 tbd 存根；对 C++/ObjC 复杂依赖支持有限 | 首选 |
| osxcross | 完整 clang 工具链、支持 ObjC/C++ | 配置重、编译慢、依赖 SDK 与 cctools | 大型混合工程 |
| GitHub Actions macOS runner | 原生工具链、可直接签名公证 | 受 CI 配额与网络限制 | 发布流水线 |
| 本地 macOS | 最可靠 | 需要硬件 | 最终验收 |

## 前置条件

| 依赖 | 说明 |
| :--- | :--- |
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

## 执行步骤

### 步骤1：设置环境

```bash
export TARGET=aarch64-apple-darwin
export MACOS_SDK_ROOT=/path/to/MacOSX14.5.sdk
export MACOSX_DEPLOYMENT_TARGET=13.0

# 关键：不要设置 SDKROOT，原因见 references/troubleshooting.md
unset SDKROOT

# 推荐使用目标专属变量，避免污染本机编译
export CARGO_TARGET_AARCH64_APPLE_DARWIN_RUSTFLAGS="\
-C link-arg=-L${MACOS_SDK_ROOT}/usr/lib \
-C link-arg=-F${MACOS_SDK_ROOT}/System/Library/Frameworks"
```

也可以写入 `.cargo/config.toml`，但不要提交包含本机 SDK 绝对路径的配置。

### 步骤2：构建

```bash
rustup target add "${TARGET}"
cargo zigbuild --release --target "${TARGET}"
```

指定包与产物：

```bash
cargo zigbuild --release --target "${TARGET}" -p <package>
```

### 步骤3：校验产物

```bash
file target/${TARGET}/release/<binary>
llvm-objdump --macho --dylibs-used target/${TARGET}/release/<binary>
codesign --verify --verbose=2 target/${TARGET}/release/<binary>
```

也可使用本技能脚本 `scripts/verify-macho.py <binary>`，一次性输出架构、最低系统、依赖库与是否 ad-hoc 签名。

硬性要求：依赖列表里不允许出现构建机绝对路径；随包分发的 dylib 应以 `@loader_path` 或 `@rpath` 引用。

Linux/Windows 产物的校验命令与 11 项验收清单见 `references/verification.md`。

### 步骤4：组装 .app

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

签名顺序是硬约束：`strip → lipo（可选）→ codesign → 打包`，之后不再改动二进制。`strip` 与 `lipo` 都会让签名失效，所以签名必须是最后一步。`.app` 先签内层可执行文件，再签 bundle；不建议依赖 `codesign --deep`。

打包脚本见 `scripts/build-macos-arm64.sh`，以环境变量注入应用名、包名与 bundle id。

### 步骤5：归档与校验

```bash
(cd dist && zip -qry app-macos-arm64.zip <App>.app)
(cd dist && sha256sum app-macos-arm64.zip > app-macos-arm64.zip.sha256)
```

`zip` 会保留执行权限；不要用会丢失权限的归档方式。

## 输出物

| 产物 | 位置 | 说明 |
| :--- | :--- | :--- |
| Mach-O 二进制 | `target/<triple>/release/<binary>` | 已含 ad-hoc 签名，`minos` 等于部署目标 |
| 应用包 | `dist/<App>.app` | 内含 `Info.plist`、可执行文件与 Resources |
| 归档 | `dist/<app>-<version>-macos-<arch>.zip` | 保留执行权限，附同名 `.sha256` |
| 校验记录 | 终端输出或报告文件 | `file`、`llvm-objdump`、`codesign` 三项输出的留存 |

## 完成标准

1. `file` 显示 `Mach-O 64-bit arm64`（x86_64 目标则为 `x86_64`）。
2. `LC_BUILD_VERSION` 的 `platform` 为 `macos`，`minos` 符合 `MACOSX_DEPLOYMENT_TARGET`。
3. 依赖库均为系统路径或随包分发的 `@rpath`，无本机绝对路径。
4. 存在 `LC_CODE_SIGNATURE` 且为 ad-hoc。
5. 归档可解压、保留执行权限，且 `.sha256` 与发布版本一致。

完整 11 项验收清单见 `references/verification.md`。

## 参考索引

| 文件 | 内容 |
| :--- | :--- |
| `references/troubleshooting.md` | 常见链接/签名/运行时问题的原因与处理，Rust 重依赖（openssl-sys、rocksdb、ort、rusqlite、zstd、ring）的交叉要点与排查顺序 |
| `references/verification.md` | macOS/Linux/Windows 三平台校验命令与验收清单 |
| `references/ci-release.md` | CI 缓存的坑、SDK 与版本固定、产物命名、通用二进制合并、安全与合规 |
| `scripts/build-macos-arm64.sh` | `.app` 组装与归档脚本 |
| `scripts/verify-macho.py` | Mach-O 架构、`minos`、依赖与签名的静态校验 |
