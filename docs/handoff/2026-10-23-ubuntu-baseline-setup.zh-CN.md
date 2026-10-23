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

## 负责人本机执行脚本

本次准备将 `scripts/ubuntu_baseline_setup.sh` 复制到 Ubuntu 用户的 home 目录；只上传文件，不在 SSH 上运行脚本。复制完成后，负责人可在 Ubuntu 的可见终端中自行检查并运行：

```bash
chmod u+x ~/ubuntu_baseline_setup.sh
~/ubuntu_baseline_setup.sh
```

脚本要求交互式终端，在 APT 模拟计划后分别等待负责人确认；模拟失败或计划包含移除项即停止。实际升级与安装命令均使用 `--no-remove`，升级保留现有 dpkg 配置文件，不自动重启、不运行 `full-upgrade` 或 `autoremove`。若系统标记需重启，脚本停止后续安装且不会重启。运行时如遇网络/防火墙组件或配置异常，应停止并汇报。

APT 计划仅保存在 Ubuntu 本机的临时目录。Netplan 检查只列文件路径，不输出 YAML 内容，避免泄露多行证书、私钥或 Wi-Fi 凭据。不要把 APT 日志、配置原文或凭据贴到聊天/仓库；只回传脱敏摘要。认证时只在本机终端输入 sudo 密码。

## 当前状态

- Base：`main` at `6f91d8be0b6ae1db914e0e7a0d74757537760825`。
- Branch：`task_20261023_ubuntu_baseline_setup`。
- PR：[PR #148](https://github.com/leezx/StelligenOS/pull/148)，base `main`；branch `task_20261023_ubuntu_baseline_setup`。对包含本机命令的 HEAD `917b22855209b170151091b01c48062660a02609` 的复审为 `REQUEST_CHANGES`，问题和修复记录见 worklog。脚本 HEAD `41d860a7250b2ac80720bc3cfc1d72851ad1b374` 已获独立 GPT `APPROVE` 后上传。对包含上传留痕的 HEAD `7a75b4be2255d730d0968c94a180838cdd2162f9` 的复审要求修正本状态段中过时的“尚待审核、尚未上传”描述；修正后需对新 exact HEAD 再复审。GitHub 正式 review API 返回 `403 Resource not accessible by integration`，没有平台 review event。未运行任何 apt/安装命令。
- 当前执行状态：脚本已通过独立 GPT 对 PR #148 exact HEAD `41d860a7250b2ac80720bc3cfc1d72851ad1b374` 的 `APPROVE` 后上传至 `/home/stelligen/ubuntu_baseline_setup.sh`，SHA-256 为 `98fec57d28b265b62895299a902476dcddc11f86045f2f832bdbc0f6ba9420f9`，权限 `-rwxr--r--`。仅复制、设置可执行位并核对哈希；未运行脚本、APT 更新或安装。GitHub 正式 review API 返回 403，未创建平台 review event。负责人可在 Ubuntu 本机可见终端运行 `~/ubuntu_baseline_setup.sh`；运行后回传脱敏摘要，由 Codex 在本 PR 留痕并复审。
