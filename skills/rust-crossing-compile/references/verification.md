# 三平台校验与验收

`SKILL.md` 只保留 macOS 的最短校验链；本页给出完整命令与验收清单。

## macOS

```bash
file target/${TARGET}/release/<binary>
llvm-objdump --macho --dylibs-used target/${TARGET}/release/<binary>
llvm-objdump --macho --private-headers target/${TARGET}/release/<binary> | grep -A4 LC_BUILD_VERSION
llvm-objdump --macho --private-headers target/${TARGET}/release/<binary> | grep -A2 LC_CODE_SIGNATURE
codesign --verify --verbose=2 target/${TARGET}/release/<binary>
```

也可使用本技能脚本 `scripts/verify-macho.py <binary>`，一次性输出架构、最低系统、依赖库与是否 ad-hoc 签名。

依赖列表里不允许出现构建机绝对路径；随包分发的 dylib 应以 `@loader_path` 或 `@rpath` 引用。

## Linux

```bash
file <binary>
readelf -d <binary> | grep -E 'RPATH|RUNPATH'
objdump -T <binary> | grep -o 'GLIBC_[0-9.]*' | sort -Vu | tail -1
```

`GLIBC_` 的最高符号版本决定可运行的最低发行版。要在越老的发行版上构建，下界越低；宁可旧构建机，不要用 latest 镜像。不要保留指向构建机目录的 `RUNPATH`。

## Windows

```powershell
dumpbin /dependents <binary>.exe
dumpbin /headers <binary>.exe | findstr /i "subsystem"
```

确认没有依赖未随包分发的 VC 运行库；优先使用静态 CRT（`+crt-static`）。

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
