#!/usr/bin/env python3
"""校验 Mach-O 产物：架构、最低系统、依赖库与 ad-hoc 签名。

用法：
    python3 verify-macho.py <binary> [--expect-arch arm64]

只依赖 Python 标准库；不执行目标二进制，适合 Linux/CI 静态验收。
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

MH_MAGIC_64 = 0xFEEDFACF
LC_CODE_SIGNATURE = 0x1D
LC_LOAD_DYLIB = 0x0C
LC_LOAD_WEAK_DYLIB = 0x80000018
LC_BUILD_VERSION = 0x32
LC_VERSION_MIN_MACOSX = 0x24

CPU_ARCH_ABI64 = 0x01000000
CPU_TYPE_X86 = 7
CPU_TYPE_ARM = 12
CPU_TYPE_X86_64 = CPU_TYPE_X86 | CPU_ARCH_ABI64
CPU_TYPE_ARM64 = CPU_TYPE_ARM | CPU_ARCH_ABI64
CPU_TYPE_ARM64_32 = CPU_TYPE_ARM | 0x02000000

PLATFORMS = {
    1: "macos",
    2: "ios",
    3: "tvos",
    4: "watchos",
    5: "bridgeos",
    6: "maccatalyst",
    7: "iossimulator",
    8: "tvossimulator",
    9: "watchossimulator",
}


def decode_version(value: int) -> str:
    return f"{value >> 16}.{(value >> 8) & 0xFF}.{value & 0xFF}"


def arch_name(cputype: int) -> str:
    return {
        CPU_TYPE_ARM64: "arm64",
        CPU_TYPE_X86_64: "x86_64",
        CPU_TYPE_ARM64_32: "arm64_32",
    }.get(cputype, f"cputype={cputype:#x}")


def read_cstr(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("utf-8", errors="replace")


def parse_signature(data: bytes, offset: int, size: int) -> tuple[bool, str]:
    if size <= 0 or offset + size > len(data):
        return False, "签名数据越界"
    blob = data[offset : offset + size]
    magic, _, count = struct.unpack_from(">III", blob, 0)
    if magic != 0xFADE0CC0:
        return False, f"非 SuperBlob（magic={magic:#x}）"
    if count < 1:
        return False, "签名索引为空"
    _, code_offset = struct.unpack_from(">II", blob, 12)
    directory = blob[code_offset:]
    if len(directory) < 24:
        return False, "CodeDirectory 过短"
    cd_magic, _, _, flags = struct.unpack_from(">IIII", directory, 0)
    if cd_magic != 0xFADE0C02:
        return False, f"非 CodeDirectory（magic={cd_magic:#x}）"
    return bool(flags & 0x2), "ad-hoc" if flags & 0x2 else "非 ad-hoc"


def inspect(path: Path) -> int:
    data = path.read_bytes()
    if len(data) < 32:
        print("不是有效的 Mach-O：文件过短")
        return 2
    magic, cputype, _, _, ncmds, _, _, _ = struct.unpack_from("<IiiIIIII", data, 0)
    if magic != MH_MAGIC_64:
        print(f"不是 64 位 Mach-O（magic={magic:#x}）")
        return 2

    platform_minos = None
    platform_sdk = None
    platform_name = None
    dylibs: list[str] = []
    signature = None

    offset = 32
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", data, offset)
        if cmdsize < 8:
            print("加载命令长度非法")
            return 2
        if cmd == LC_BUILD_VERSION:
            platform, minos, sdk, _ = struct.unpack_from("<IIII", data, offset + 8)
            platform_name = PLATFORMS.get(platform, str(platform))
            platform_minos = decode_version(minos)
            platform_sdk = decode_version(sdk)
        elif cmd == LC_VERSION_MIN_MACOSX:
            version, sdk = struct.unpack_from("<II", data, offset + 8)
            platform_name = "macos"
            platform_minos = decode_version(version)
            platform_sdk = decode_version(sdk)
        elif cmd in (LC_LOAD_DYLIB, LC_LOAD_WEAK_DYLIB):
            name_offset = struct.unpack_from("<I", data, offset + 8)[0]
            dylibs.append(read_cstr(data, offset + name_offset))
        elif cmd == LC_CODE_SIGNATURE:
            data_offset, data_size = struct.unpack_from("<II", data, offset + 8)
            signature = (data_offset, data_size)
        offset += cmdsize

    print(f"文件      {path}")
    print(f"架构      {arch_name(cputype)}")
    print(f"平台      {platform_name or '未知'}")
    print(f"最低系统  {platform_minos or '未知'}")
    print(f"SDK       {platform_sdk or '未知'}")
    print("依赖库:")
    for dylib in dylibs:
        print(f"  - {dylib}")
    if signature:
        ok, detail = parse_signature(data, *signature)
        print(f"代码签名  {'存在' if ok else '存在但非 ad-hoc'}（{detail}）")
    else:
        print("代码签名  缺失")

    expected = None
    if "--expect-arch" in sys.argv:
        index = sys.argv.index("--expect-arch")
        if index + 1 < len(sys.argv):
            expected = sys.argv[index + 1]
    if expected and arch_name(cputype) != expected:
        print(f"架构不符合预期：需要 {expected}")
        return 1
    return 0


def main() -> int:
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"文件不存在：{path}")
        return 2
    return inspect(path)


if __name__ == "__main__":
    raise SystemExit(main())
