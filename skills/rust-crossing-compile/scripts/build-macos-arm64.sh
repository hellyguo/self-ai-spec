#!/usr/bin/env bash
# 通用模板：在 Linux/Windows 上交叉编译 Rust 应用到 macOS arm64。
#
# 必填环境变量：
#   MACOS_SDK_ROOT  macOS SDK 目录，例如 /path/to/MacOSX14.5.sdk
# 可选环境变量：
#   APP_NAME        应用名，默认 MyApp
#   BIN_NAME        可执行文件名，默认 myapp
#   BUNDLE_ID       Bundle Identifier，默认 com.example.myapp
#   PACKAGE         cargo 包名，留空表示当前包
#   TARGET          默认 aarch64-apple-darwin
#   DEPLOYMENT      最低系统版本，默认 13.0
#   VERSION         版本号，默认 0.1.0
set -euo pipefail

APP_NAME="${APP_NAME:-MyApp}"
BIN_NAME="${BIN_NAME:-myapp}"
BUNDLE_ID="${BUNDLE_ID:-com.example.myapp}"
PACKAGE="${PACKAGE:-}"
TARGET="${TARGET:-aarch64-apple-darwin}"
DEPLOYMENT="${MACOSX_DEPLOYMENT_TARGET:-13.0}"
VERSION="${VERSION:-0.1.0}"
SDK_ROOT="${MACOS_SDK_ROOT:?请设置 MACOS_SDK_ROOT 指向 MacOSX*.sdk}"

if [[ ! -d "${SDK_ROOT}" ]]; then
    echo "找不到 macOS SDK：${SDK_ROOT}" >&2
    exit 1
fi
if ! command -v cargo-zigbuild >/dev/null 2>&1; then
    echo "缺少 cargo-zigbuild：cargo install cargo-zigbuild" >&2
    exit 1
fi
if ! command -v zig >/dev/null 2>&1; then
    echo "缺少 zig，请安装并加入 PATH" >&2
    exit 1
fi

rustup target add "${TARGET}" >/dev/null 2>&1 || true

# 关键：不要设置 SDKROOT，否则 zig 会把绝对 -L 路径按 sysroot 二次拼接。
unset SDKROOT
export MACOSX_DEPLOYMENT_TARGET="${DEPLOYMENT}"
TARGET_UPPER="$(echo "${TARGET}" | tr 'a-z-' 'A-Z_')"
export "CARGO_TARGET_${TARGET_UPPER}_RUSTFLAGS=-C link-arg=-L${SDK_ROOT}/usr/lib -C link-arg=-F${SDK_ROOT}/System/Library/Frameworks"

BUILD_ARGS=(--release --target "${TARGET}")
if [[ -n "${PACKAGE}" ]]; then
    BUILD_ARGS+=(-p "${PACKAGE}")
fi
cargo zigbuild "${BUILD_ARGS[@]}"

BINARY="target/${TARGET}/release/${BIN_NAME}"
if [[ ! -f "${BINARY}" ]]; then
    echo "构建产物不存在：${BINARY}" >&2
    exit 1
fi

DIST_DIR="dist"
APP_DIR="${DIST_DIR}/${APP_NAME}.app"
rm -rf "${APP_DIR}"
mkdir -p "${APP_DIR}/Contents/MacOS" "${APP_DIR}/Contents/Resources"
cp "${BINARY}" "${APP_DIR}/Contents/MacOS/${BIN_NAME}"
chmod +x "${APP_DIR}/Contents/MacOS/${BIN_NAME}"

cat > "${APP_DIR}/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>${BUNDLE_ID}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleExecutable</key>
    <string>${BIN_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>${DEPLOYMENT}</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# zig 已写入 ad-hoc 签名；本机存在 codesign 时再做一次深度签名。
if command -v codesign >/dev/null 2>&1; then
    codesign --force --deep --sign - "${APP_DIR}"
fi

ARCHIVE="${DIST_DIR}/$(echo "${APP_NAME}" | tr 'A-Z' 'a-z')-${VERSION}-macos-${TARGET%%-*}.zip"
rm -f "${ARCHIVE}"
(cd "${DIST_DIR}" && zip -qry "$(basename "${ARCHIVE}")" "${APP_NAME}.app")

if command -v shasum >/dev/null 2>&1; then
    (cd "${DIST_DIR}" && shasum -a 256 "$(basename "${ARCHIVE}")" > "$(basename "${ARCHIVE}").sha256")
else
    (cd "${DIST_DIR}" && sha256sum "$(basename "${ARCHIVE}")" > "$(basename "${ARCHIVE}").sha256")
fi

echo "构建完成："
echo "  二进制：${BINARY}"
echo "  应用包：${APP_DIR}"
echo "  压缩包：${ARCHIVE}"
