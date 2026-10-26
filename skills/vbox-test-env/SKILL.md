---
name: vbox-test-env
description: "提供 VirtualBox 三机测试环境（含互信与 sudo），用于集群、分布式与主备类系统测试。适用于需要多节点环境的联调与验证。"
---

# VirtualBox 三机测试环境

提供三台已配置互信与 sudo 的 VirtualBox 虚拟机，用于集群、分布式、主备等需要多节点的测试场景。

## 机器清单

| 主机名 | 登录用户 | SSH 别名 |
|--------|----------|----------|
| debian001 | vboxuser | vboxdeb001 |
| debian002 | vboxuser | vboxdeb002 |
| debian003 | vboxuser | vboxdeb003 |

## 网络拓扑

每台虚拟机配置三种网络视图，使用时按通信方向选择地址：

### 虚拟机到宿主机

三台机器均通过 NAT 访问宿主机，虚拟机侧看到的默认地址相同：

| 主机名 | 虚拟机侧地址 |
|--------|--------------|
| debian001 | 10.0.2.15 |
| debian002 | 10.0.2.15 |
| debian003 | 10.0.2.15 |

说明：`10.0.2.15` 是 VirtualBox NAT 为每台虚拟机分配的独立地址，互相不冲突；宿主机侧地址均为 `10.0.2.2`。

### 宿主机到虚拟机

宿主机通过宿主网络访问各虚拟机：

| 主机名 | 宿主机侧地址 |
|--------|--------------|
| debian001 | 172.22.133.251 |
| debian002 | 172.22.133.252 |
| debian003 | 172.22.133.253 |

### 虚拟机之间

虚拟机之间通过内部网络通信：

| 主机名 | 内部网络地址 |
|--------|--------------|
| debian001 | 192.168.77.101 |
| debian002 | 192.168.77.102 |
| debian003 | 192.168.77.103 |

## 已安装环境

- 编译工具：gcc、g++、make、cmake
- 内核开发：libbpf、libxdp
- Java 8：位于 `~/lang`
- Node.js

## 启动

```bash
vboxmanage startvm --type=headless debian001 &
vboxmanage startvm --type=headless debian002 &
vboxmanage startvm --type=headless debian003 &
```

启动后等待约 30 秒，使用 `ssh vboxdeb001 true` 验证连通性。

## 停止

```bash
ssh vboxuser@vboxdeb001 sudo poweroff
ssh vboxuser@vboxdeb002 sudo poweroff
ssh vboxuser@vboxdeb003 sudo poweroff
```

## 使用约束

- 仅用于测试，不得存放生产数据。
- 三台机器共享同一宿主资源，压测时注意宿主机 CPU、内存与磁盘上限。
- 修改网络配置前先确认虚拟机间与宿主机到虚拟机的连通性，避免失联。
