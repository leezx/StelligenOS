# Ubuntu wait-online 超时修复交接

## 目标

修复 Ubuntu 启动时 `systemd-networkd-wait-online.service` 因未插网线的以太网口等待 120 秒后失败的问题，同时保留 Wi-Fi 网络和以太网口可用性。

## 观测依据

- 2026-10-23 17:20 EDT 通过 SSH 只读读取 wait-online/networkd journal、`networkctl`、`nmcli`、接口地址和 resolver 状态；原始输出保存在执行端 `/tmp/ubuntu-network-diagnostics-20261023.txt`（权限 600），未写入仓库。
- Wi-Fi `wlo1` 显示 `routable/configured`，持有 DHCP 地址。
- `enp1s0`、`enp3s0` 均显示 `no-carrier/configuring`，生成的 `.network` 配置对两口都设置 `Required For Online: yes`。
- NetworkManager service 为 active，但其设备显示 unmanaged；systemd-networkd 管理相关网络接口。UFW 为 inactive，与 wait-online 超时无直接关联。
- systemd wait-online 默认等待所有被 networkd 管理且 required 的接口；Netplan 的 `optional: true` 会让 networkd 不等待对应设备启动，但仍会正常启用设备。参考 [Netplan YAML optional](https://netplan.readthedocs.io/en/latest/netplan-yaml/) 与 [Ubuntu systemd-networkd-wait-online 手册](https://manpages.ubuntu.com/manpages/noble/man8/systemd-networkd-wait-online.service.8.html)。

## 修复范围与安全边界

- 新脚本 `scripts/ubuntu_wait_online_fix.sh` 仅在 Wi-Fi `wlo1` 当前 routable、`enp1s0`/`enp3s0` 当前无 carrier 且 Netplan 中各自恰好有一个对应定义时，才提出将这两个 Ethernet 定义设为 optional。
- 不打印或保存 Wi-Fi 密码、证书、Netplan 原文；脚本在内存中解析合并后的 Ethernet 配置，仅输出 interface ID 映射。
- 修改前在 root-only `/root` 下备份 `/etc/netplan`，使用独立 Netplan overlay；先 `netplan generate` 校验，再通过交互式 `netplan try --timeout 120` 应用。若未确认、Wi-Fi 未恢复 routable 或 wait-online 仍失败，脚本移除 overlay 并恢复原配置。
- 负责人要求修复该故障；但 Codex 的 SSH sudo 非交互检查返回 `interactive authentication is required`。不从聊天收集 sudo 凭据；因此由负责人在机器可见终端运行脚本以便看到并确认 sudo/netplan 提示。
- PR exact HEAD 独立 GPT `APPROVE` 前不上传脚本；当前没有 Ubuntu 网络配置变更或脚本运行。

## 负责人运行方法（PR 审核和上传后）

```bash
chmod u+x ~/ubuntu_wait_online_fix.sh
~/ubuntu_wait_online_fix.sh
```

脚本会输出保护性备份目录，并要求两次交互确认。只有 Wi-Fi 仍连通且 wait-online service 启动成功后才保留修改；否则恢复旧配置。

## 当前状态

- Branch：`task_20261023_ubuntu_wait_online_fix`，初始脚本提交已推送；PR 独立审核完成前不会上传至 Ubuntu 或更改目标机配置。
- 目标主机配置、服务和防火墙尚未修改；脚本没有在 Ubuntu 上运行。
