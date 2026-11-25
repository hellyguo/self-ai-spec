---
name: vbox-test-env
description: "提供 VirtualBox 测试环境：三台 Debian 虚拟机（互信与 sudo）用于集群/分布式测试，以及一台 Windows Server 2019 构建虚拟机（VS2022 + Rust）用于 MSVC 编译；包含启动停止、guestcontrol、scp 文件传输与工具链路径。"
---

# VirtualBox 测试环境

本技能覆盖两类虚拟机：三台 Debian 组成的集群测试环境，以及一台 Windows Server 2019 的 MSVC 构建环境。两者共用宿主机的 VirtualBox 与 host-only 网络（`vboxnet0`，宿主 `172.22.133.1`）。

## 一、Linux 三机集群

提供三台已配置互信与 sudo 的 VirtualBox 虚拟机，用于集群、分布式、主备等需要多节点的测试场景。

### 机器清单

| 主机名    | 登录用户 | SSH 别名   |
| --------- | -------- | ---------- |
| debian001 | vboxuser | vboxdeb001 |
| debian002 | vboxuser | vboxdeb002 |
| debian003 | vboxuser | vboxdeb003 |

### 网络拓扑

每台虚拟机配置三种网络视图，使用时按通信方向选择地址：

#### 虚拟机到宿主机

三台机器均通过 NAT 访问宿主机，虚拟机侧看到的默认地址相同：

| 主机名    | 虚拟机侧地址 | 宿主机侧地址 |
| --------- | ------------ | ------------ |
| debian001 | 10.0.2.15    | 10.0.2.2     |
| debian002 | 10.0.2.15    | 10.0.2.2     |
| debian003 | 10.0.2.15    | 10.0.2.2     |

说明：`10.0.2.15` 是 VirtualBox NAT 为每台虚拟机分配的独立地址，互相不冲突；宿主机侧地址均为 `10.0.2.2`。

#### 宿主机到虚拟机

宿主机通过宿主网络访问各虚拟机：

| 主机名    | 虚拟机侧地址   | 宿主机侧地址 |
| --------- | -------------- | ------------ |
| debian001 | 172.22.133.251 | 172.22.133.1 |
| debian002 | 172.22.133.252 | 172.22.133.1 |
| debian003 | 172.22.133.253 | 172.22.133.1 |

#### 虚拟机之间

虚拟机之间通过内部网络通信：

| 主机名    | 内部网络地址   |
| --------- | -------------- |
| debian001 | 192.168.77.101 |
| debian002 | 192.168.77.102 |
| debian003 | 192.168.77.103 |

### 已安装环境

- 编译工具：gcc、g++、make、cmake
- 内核开发：libbpf、libxdp
- Java 8：位于 `~/lang`
- Node.js

### 启动

```bash
vboxmanage startvm --type=headless debian001
vboxmanage startvm --type=headless debian002
vboxmanage startvm --type=headless debian003
```

启动后等待约 30 秒，使用 `ssh vboxdeb001 true` 验证连通性。

### 停止

```bash
ssh vboxuser@vboxdeb001 sudo poweroff
ssh vboxuser@vboxdeb002 sudo poweroff
ssh vboxuser@vboxdeb003 sudo poweroff
```

## 二、Windows 构建虚拟机

### 机器与网络

| 项目 | 值 |
|------|-----|
| 虚拟机名 | `WinServer2019` |
| 系统 | Windows Server 2019（10.0.17763） |
| Guest Additions | 7.1.4 |
| 登录用户 | `vboxuser`（密码不入库，见“Guest 控制”） |
| Visual Studio | VS2022 Community，`C:\vs\VS22Comm`（主用）；VS2015 仍在但仅作遗留 |
| Rust | 1.100.0，`C:\Users\vboxuser\.cargo\bin`（rustc/cargo/rustup） |
| CPU / 磁盘 | 4 逻辑核；构建前约 13.5GB 可用（以实际为准） |
| host-only 地址 | 当前 `172.22.133.114`，以查询结果为准 |
| NAT 地址 | Guest `10.0.2.15`，宿主机侧 `10.0.2.2` |
| 宿主机服务访问 | Guest 内使用 `ws://10.0.2.2:<port>/...` |

查询当前 host-only 地址：

```bash
VBoxManage guestproperty get WinServer2019 "/VirtualBox/GuestInfo/Net/1/V4/IP"
```

### 启动与关闭

```bash
enable-vboxnet0
vboxmanage startvm --type=headless WinServer2019
```

关闭：

```bash
vboxmanage controlvm WinServer2019 poweroff
```

`poweroff` 为强制断电；正常关机无法在 Guest 内提权执行 `shutdown /s /t 0`。`enable-vboxnet0` 通常位于 `~/LinuxEnv/bin/`，确认已加入 `PATH`。

虚拟机以 GUI 运行时，前端会持有写锁，`VBoxManage sharedfolder add` 会失败；需要共享目录时先关机配置，或使用 `guestcontrol` 与 `scp`(首选)。

### Guest 控制

密码不要写入仓库、公开 dotfiles 或本技能。推荐放在权限为 `600` 的密码文件中：

```bash
printf '%s' '<password>' > "$HOME/.vbox-win.pass"
chmod 600 "$HOME/.vbox-win.pass"
```

以下函数放入私有 shell 配置（不要提交）：

```bash
WIN_VM=WinServer2019
WIN_USER=vboxuser
WIN_PASSFILE=$HOME/.vbox-win.pass

wincmd() {
    VBoxManage guestcontrol "$WIN_VM" run --exe 'C:\Windows\System32\cmd.exe' \
        --username "$WIN_USER" --passwordfile "$WIN_PASSFILE" \
        --wait-stdout --wait-stderr -- /c "$1"
}

winpsh() {
    VBoxManage guestcontrol "$WIN_VM" run --exe 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' \
        --username "$WIN_USER" --passwordfile "$WIN_PASSFILE" \
        --wait-stdout --wait-stderr -- -Command "$1"
}

winpsex() {
    VBoxManage guestcontrol "$WIN_VM" run --exe 'C:\App\SysinternalsSuite\psexec.exe' \
        --username "$WIN_USER" --passwordfile "$WIN_PASSFILE" \
        --wait-stdout --wait-stderr -- "$@"
}
```

用法：

```bash
wincmd "ver"
wincmd "dir C:\work"
winpsh "Get-ChildItem C:\work"
winpsex "whoami"
```

`wincmd`/`winpsh`/`winpsex` 都无法在控制台下以管理员权限运行，因为无法通过 console 命令提权。若宿主机上没有 `--passwordfile` 支持，可临时使用 `--password`，但不要写入脚本或历史记录。

注意：通过 `guestcontrol ... /c "<command>"` 传含引号、花括号或 `&` 的复杂命令时，容易发生二次转义，导致参数被截断。复杂命令建议写成 `.bat` 文件上传到 `C:\Temp` 后执行，例如：

```bat
@echo off
cd /d C:\work\project
cargo build --release
```

```bash
VBoxManage guestcontrol WinServer2019 copyto --username vboxuser --passwordfile "$HOME/.vbox-win.pass" /tmp/build.bat 'C:\Temp\build.bat'
wincmd "C:\Temp\build.bat"
```

### 工具链位置

以下为 2026-11-25 实测值：

| 工具 | 路径/版本 |
|------|-----------|
| Visual Studio（主用） | VS2022 Community，`C:\vs\VS22Comm` |
| vcvars（主用） | `C:\vs\VS22Comm\VC\Auxiliary\Build\vcvars64.bat` |
| cl.exe（x64） | `C:\vs\VS22Comm\VC\Tools\MSVC\14.43.34808\bin\Hostx64\x64\cl.exe` |
| MSVC 版本 | 19.43.34810（C++20/23） |
| Visual Studio 2015（遗留） | `C:\Program Files (x86)\Microsoft Visual Studio 14.0`，仅 C++14，不用于新项目 |
| Rust | 1.100.0（`rustc`/`cargo`/`rustup` 位于 `C:\Users\vboxuser\.cargo\bin`） |
| CMake / Ninja | `C:\App\strawberryperl\c\bin\`（CMake 3.29.2 / Ninja 1.12.0） |
| OpenSSL | `C:\OpenSSL-Win64`（4.0.0，库在 `lib\VC\x64\{MD,MDd,MT,MTd}`） |
| Git | `C:\git4win\bin\git.exe` |
| 7-Zip | `C:\Program Files\7-Zip\7z.exe`（已在 PATH） |
| OpenSSH scp | `C:\Windows\System32\OpenSSH\scp.exe` |
| 源码工作目录示例 | `C:\work\<project>` |

VS2022 已支持 C++20/23；优先使用 `vcvars64.bat`。VS2015 的 MSBuild/VS 生成器不完整，`cmake -G "Visual Studio 14 2015"` 会报 `VCTargetsPath` 错误，新项目不要走 VS2015。

### 文件传输

Guest 已安装 OpenSSH 客户端与 7-Zip，并已配置到宿主机当前用户的免密登录。Guest 访问宿主机使用 NAT 地址 `10.0.2.2`。

Linux 侧打包优先使用 `git archive`，参数可以是任意 git 引用（分支、tag、commit、`HEAD~N`），只包含已提交内容：

```bash
cd <repo>
REF=HEAD
git archive --format=zip -o /tmp/"$REF".zip "$REF"
```

需要包含未提交改动时打包工作区：

```bash
7z a -t7z -mx=3 /tmp/worktree.7z . -x'!build/*' -x'!.git/*' -x'!dist/*'
```

Windows 侧取包（在 Guest 内主动 `scp` 拉取，免密已配置）：

```bash
wincmd "scp -o StrictHostKeyChecking=no <host-user>@10.0.2.2:/tmp/HEAD.zip C:\Temp\src.zip"
wincmd "7z x C:\Temp\src.zip -aoa -oC:\work\<project>"
```

上传产物回宿主（同样由 Guest 侧 `scp` 推送）：

```bash
wincmd "scp -o StrictHostKeyChecking=no C:\work\<project>\target\release\app.exe <host-user>@10.0.2.2:/tmp/app.exe"
```

说明：

- `scp` 方向是 Guest 主动连接宿主机 `10.0.2.2`，宿主无需运行 SSH 服务端；已实测可双向传输。
- `<host-user>` 为宿主机当前登录用户；免密登录已配置，host key 变化时检查宿主机 `sshd` 或清理 Guest 的 `known_hosts`。
- `scp -r` 可传目录，但大量小文件建议先打包。
- 备用方式：`guestcontrol copyto/copyfrom`。`copyto` 的 `--target-directory` 需以反斜杠结尾；直接复制宿主机 `/disk2/...` 可能报 `NS_ERROR_FAILURE`，先放 `/tmp` 再传。`copyfrom` 必须带 VM 名，目标是宿主机文件路径。

### Windows 构建要点

- 优先使用 VS2022：`call C:\vs\VS22Comm\VC\Auxiliary\Build\vcvars64.bat`；`vcvarsall amd64` 也可用。
- VS2022 支持 C++20/23；需要 C++20 的项目（如 qpdf 12 vendored）可直接构建。VS2015 仅 C++14，只用于遗留项目。
- Rust 项目的 MSRV 需注意：flpdf 0.10 要求 rustc ≥1.89；若 cargo 报 MSRV 错误，先 `rustup update stable`（当前为 1.100.0）。
- 需要免 VC++ Redistributable 的 Rust 产物，设置静态 CRT：

```bat
set RUSTFLAGS=-C target-feature=+crt-static
cargo build --release
```

  构建后用 `dumpbin /dependents` 检查，理想情况下只剩 `kernel32.dll`、`ADVAPI32.dll`、`ntdll.dll` 等系统 DLL，不应出现 `MSVCP140.dll` / `VCRUNTIME140.dll`。
- 某些 `-sys` crate 的 vendored C/C++ 构建使用 `cc` crate 而不是 CMake（例如 `qpdf-sys` 直接以 `/std:c++20` 编译），不要假设必须提供 CMake。
- 使用 CMake 的项目，在 vcvars 环境后统一用 `cmake -G Ninja`；不要用 VS2015 生成器。
- Windows 构建默认关闭 zlib 与 permessage-deflate 时，产物不支持 gzip；需要压缩时准备与 MSVC 匹配的 zlib，并打开 `LWS_WITH_ZLIB` 与扩展。
- 32 位最小包可用静态 CRT（`CMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded`）并关闭 SSL，运行依赖只剩 `WS2_32.dll`、`KERNEL32.dll`，但不支持 wss。
- 导出符号验证需在 vcvars 环境运行 `dumpbin`；建议在 Guest 内写一个 `.bat` 调用 `vcvars64.bat` 后再执行 `dumpbin`。

## 使用约束

- 仅用于测试，不得存放生产数据。
- 三台 Debian 虚拟机共享同一宿主资源，压测时注意宿主机 CPU、内存与磁盘上限。
- 修改网络配置前先确认虚拟机间与宿主机到虚拟机的连通性，避免失联。
- Windows 虚拟机密码、宿主机账号等敏感信息不得写入仓库或本技能；使用密码文件并限制权限。
- 远程传输前先确认 Guest 地址（host-only 或 NAT），避免使用过期 IP。
