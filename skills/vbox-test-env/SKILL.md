---
name: vbox-test-env
description: "virtualbox 三机测试环境，可供部分需要集群的系统进行测试"
---

## desc

提供三台 virtualbox 虚拟机，均已做好互信，均有 sudo 高权

- vboxuser@vboxdeb001
- vboxuser@vboxdeb002
- vboxuser@vboxdeb003

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

