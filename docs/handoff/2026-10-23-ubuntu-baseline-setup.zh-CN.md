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

## 当前状态

- Base：`main` at `6f91d8be0b6ae1db914e0e7a0d74757537760825`。
- Branch：`task_20261023_ubuntu_baseline_setup`。
- PR：[PR #148](https://github.com/leezx/StelligenOS/pull/148)，base `main`；scope commit `125fc56ce9c941d4d248b7f1ed4573b3cc3b94f3`；GPT/ChatGPT 审核：待定；尚未运行任何主机命令。
- 下一步：自动提交独立 GPT 审核；批准后按本 handoff 执行并更新本文件与 worklog。
