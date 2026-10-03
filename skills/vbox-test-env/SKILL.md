---
name: vbox-test-env
description: "virtualbox 三机测试环境，可供部分需要集群的系统进行测试"
---

## desc

提供三台 virtualbox 虚拟机，均已做好互信，均有 sudo 高权

- debian001: vboxuser@vboxdeb001
- debian002: vboxuser@vboxdeb002
- debian003: vboxuser@vboxdeb003

### 虚-主单向通讯 IP

- debian001: 10.0.2.15
- debian002: 10.0.2.15
- debian003: 10.0.2.15

### 主-虚单向通讯 IP

- debian001: 172.22.133.251
- debian002: 172.22.133.252
- debian003: 172.22.133.253

### 虚机间通讯 IP

- debian001: 192.168.77.101
- debian002: 192.168.77.102
- debian003: 192.168.77.103

### 环境信息

已安装 gcc/g++/make/cmake/libbpf/libxdp
已安装 java8 (~/lang 下)
已安装 node

## start

```bash
vboxmanage startvm --type=headless debian001 &
vboxmanage startvm --type=headless debian002 &
vboxmanage startvm --type=headless debian003 &
```

## stop

```bash
ssh vboxuser@vboxdeb001 sudo poweroff
ssh vboxuser@vboxdeb002 sudo poweroff
ssh vboxuser@vboxdeb003 sudo poweroff
```

