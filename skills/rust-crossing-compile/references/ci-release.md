# CI、发布与架构扩展

## CI 建议

1. 缓存 `~/.cargo`、`target`、`~/.cache/cargo-zigbuild` 与 zig 安装目录；`Swatinem/rust-cache` 的 key 必须带目标三元组，否则不同架构互相污染。
2. SDK 不入库，使用私有制品或 CI secret 挂载；固定 zig 与 cargo-zigbuild 版本，二者不兼容时常表现为难以定位的链接错误。
3. 产物统一命名 `<app>-<version>-macos-<arch>.zip`，同时输出 SHA-256。
4. 在 macOS runner 上做最终启动验收；交叉编译只做格式、依赖与签名静态校验。
5. 将 SDK 路径、部署目标、目标三元组作为参数，不要在脚本中硬编码。
6. 矩阵构建使用 `fail-fast: false`，避免一个平台失败掩盖其余平台的真实状态。
7. 原生 runner 与交叉任务可以混编：Linux x86_64、macOS、Windows 走原生，Linux aarch64 走 `gcc-aarch64-linux-gnu` 交叉，并在交叉任务里设置 `CC_/CXX_/AR_<target>`、`CARGO_TARGET_<TARGET>_LINKER`、`PKG_CONFIG_ALLOW_CROSS=1`。
8. 发布前校验 tag 与 workspace 版本一致，并在归档脚本里显式传入平台标识（禁止自动探测）。

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

## 安全与合规

1. Apple SDK 受许可约束，不要提交到代码仓库或公开分发。
2. ad-hoc 签名只解决本机运行，不等同于可信任分发；对外发布需 Developer ID 签名与公证。
3. 交叉编译产物含本机路径信息时，检查是否泄露构建环境；必要时使用 `strip` 与可复现构建参数。
