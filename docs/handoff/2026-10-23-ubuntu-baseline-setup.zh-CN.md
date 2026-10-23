# Ubuntu 基线更新与 Python 环境准备交接

## 目标

在负责人要求下，为其新装 Ubuntu 主机应用已发现的安全/系统包更新，并安装 `python3-venv` 作为后续部署 Python 助手的基础；同时复查防火墙和网络等待状态。

## 范围

- 刷新 APT 软件索引。
- 应用普通升级 `apt-get upgrade` 可完成的更新；不执行 `full-upgrade`、`autoremove` 或自动重启。
- 安装 `python3-venv`。
- 以只读方式查看 UFW 规则、Netplan 配置和 `systemd-networkd-wait-online` 状态。
- 若 APT 要移除包，或需要更改防火墙/网络配置、重启系统，则停止并报告，不自行扩大范围。
- 不安装 `build-essential`、`iw`、`rfkill`，除非实际发现本任务必需且负责人另行确认。

## 操作授权与前置条件

- 负责人最近指令“开始做”按上述更新与安装范围执行。
- 由于仓库硬性门禁，本次更改需通过独立 GitHub PR 与 GPT/ChatGPT 审核；PR #147 只覆盖只读审计，不复用该 PR。
- 获得本 PR 当前 HEAD 的明确 `APPROVE` 后才 SSH 执行。
- sudo 凭据不在聊天中收集；如需认证，使用 Codex 本地终端交互输入。若无法提供交互认证则停止。

## 风险与验证

- 普通包升级可能重启个别服务并短暂中断 SSH；不自动重启整机。若连接中断，重新连接后先检查 dpkg/apt 状态，再决定后续动作。
- 完成后检查 `dpkg --audit`、`python3-venv` 安装状态、剩余可升级项、UFW 状态、网络服务状态和 reboot-required 标记。
- 不将凭据、原始主机输出或个人文件写入仓库；只记录必要的脱敏摘要。

## 负责人本机执行命令

Codex SSH 终端面板未在负责人界面中显示，因此负责人选择在自己的可见终端执行。按顺序运行，每一步先检查结果再继续：

```bash
sudo apt-get update
sudo apt-get -s upgrade | tee /tmp/ubuntu-upgrade-plan.txt
grep -E '^(Remv |The following packages will be REMOVED:)' /tmp/ubuntu-upgrade-plan.txt
```

若最后一条命令有任何输出，停止，不运行升级。若没有移除项：

```bash
sudo apt-get upgrade
```

出现确认提示后输入 `Y`。遇到配置文件替换提示，保留当前本地版本；若提示需要改网络/防火墙配置或重启，停止并汇报，不自动重启。升级结束后先查重启标志：

```bash
if [ -e /var/run/reboot-required ]; then
  echo 'STOP: reboot required; do not continue or reboot automatically'
  cat /var/run/reboot-required.pkgs 2>/dev/null || true
else
  echo 'No reboot required'
fi
```

只有显示 `No reboot required` 才继续模拟和安装 venv：

```bash
sudo apt-get -s install python3-venv | tee /tmp/python3-venv-plan.txt
grep -E '^(Remv |The following packages will be REMOVED:)' /tmp/python3-venv-plan.txt
```

若有移除项停止；否则运行：

```bash
sudo apt-get install python3-venv
```

安装完成后核验并执行只读检查：

```bash
dpkg --audit
dpkg-query -W -f='${Status}\n' python3-venv
python3 -m venv --help >/dev/null && echo 'venv module available'
apt list --upgradable
sudo ufw status verbose
systemctl is-active NetworkManager.service systemd-networkd.service systemd-networkd-wait-online.service || true
systemctl --no-pager --full status systemd-networkd-wait-online.service || true
sudo sh -c 'for f in /etc/netplan/*.yaml; do [ -f "$f" ] || continue; echo "--- $f"; sed -E "/(password|psk|passphrase|private-key|client-key|identity):/s/:.*/: [REDACTED]/I" "$f"; done'
if [ -e /var/run/reboot-required ]; then echo 'Reboot required (do not reboot automatically)'; else echo 'No reboot required'; fi
```

Netplan YAML 可能包含 Wi-Fi 密码或证书信息；不要把未脱敏配置原文贴到聊天或仓库。认证时只在本机终端输入 sudo 密码。

## 当前状态

- Base：`main` at `6f91d8be0b6ae1db914e0e7a0d74757537760825`。
- Branch：`task_20261023_ubuntu_baseline_setup`。
- PR：[PR #148](https://github.com/leezx/StelligenOS/pull/148)，base `main`；branch `task_20261023_ubuntu_baseline_setup`。独立 GPT reviewer 对 exact HEAD `cf8e1b220b0c87839499534a97cd5e0bdf1223ac` 明确 `APPROVE`，范围及停止条件如上；GitHub 正式 review API 返回 `403 Resource not accessible by integration`，所以平台 review event 未创建。PR 在本次更新前仍为该获批 HEAD；本次添加本机执行命令与状态记录会产生新 HEAD，须再次审查文档后再视为当前 PR 放行。尚未运行任何 apt/安装命令。
- 当前执行状态：未执行 APT 更新/安装。负责人在本机可见终端按上方顺序运行；若遇到停止条件，先停止并汇报。完成后只需回传脱敏摘要（升级包数、`python3-venv` 状态、UFW/网络服务状态、是否需重启），由 Codex 在本 PR 更新留痕并复审。
