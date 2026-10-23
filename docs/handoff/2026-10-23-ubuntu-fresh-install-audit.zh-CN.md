# Ubuntu 新装系统只读审计交接

## 目标

负责人要求检查其新安装的 Ubuntu 主机，判断是否缺少必要的系统组件，并列出必要安装建议。

## 当前阶段与边界

- 当前阶段：只读系统审计已完成；本记录汇总脱敏后的系统摘要和建议。
- 目标主机：负责人在本任务中指定的 Ubuntu 主机，通过 Tailscale SSH 访问。
- 审计范围：系统版本、内核/架构、磁盘与内存、软件包/更新状态、网络、SSH、防火墙和基础管理工具。
- 未读取个人文件、凭据或业务数据；未把原始主机输出写入仓库；未安装软件或更改系统配置。
- 独立 GPT reviewer 对审计前 PR HEAD `be370bfd2aca38c4b5ce6da6c62cc011292743cf` 给出明确 `APPROVE` 后，才执行 SSH；该批准仅限只读系统审计，不含安装或配置变更。

## 审计摘要（2026-10-23）

- Ubuntu 26.04.1 LTS、x86_64；8 CPU、14 GiB RAM、4 GiB swap；根卷空间充足。
- 基础远程管理/网络组件已具备：OpenSSH Server、CA certificates、sudo、curl、git、Python 3、NetworkManager、UFW、unattended-upgrades；SSH、NetworkManager、systemd-networkd、Tailscale、UFW 与 unattended-upgrades 服务活跃。`dpkg --audit` 无未完成包问题。
- 本地 apt 索引显示约 40 个包可升级；未刷新索引或执行升级。
- 未安装：`python3-venv`、`build-essential`、`iw`、`rfkill`。这些不属于基础系统必需项；如果后续部署 Python 助手，建议安装 `python3-venv`；编译工具和 Wi-Fi 诊断工具按用途安装。
- `systemd-networkd-wait-online` 超时失败；当时两块以太网接口无 carrier、Wi-Fi 为 routable，可能导致等待超时。NetworkManager 和 systemd-networkd 均启用并运行，后续建议核对网络配置，避免非预期启动等待。
- UFW 服务 active，但当前 SSH 用户的 `sudo -n` 需要交互认证，未能读取实际防火墙规则；SSH 监听 IPv4/IPv6 的 22 端口，需确认 UFW 是否有合适的入站规则。

## 当前状态

- 已按本地 `AGENTS.md` 与 `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` 确认外部 SSH 检查须经 PR 审核。
- 本地主要工作区存在与本任务无关的未提交改动；本任务在隔离 worktree 中准备，未修改或暂存那些改动。
- 2026-10-23 已完成只读 SSH 检查；未安装软件、刷新 apt 索引或更改配置。
- Base：`main` at `6f91d8be0b6ae1db914e0e7a0d74757537760825`；任务分支：`task_20261023_ubuntu_system_audit`。
- PR：[PR #147](https://github.com/leezx/StelligenOS/pull/147)，base `main`；审计前 code commit `6973b4129d7741196b61d7b0154454392a3175d7`；独立 reviewer 对审计前当前 HEAD `be370bfd2aca38c4b5ce6da6c62cc011292743cf` 给出 `APPROVE`，仅放行只读审计。审计结果轮审提出删除主机定位信息，已在同一 PR 最小修订，当前修订待复审。

## 验证与后续

- 验证：审计前和本次审计后留痕均通过 `git diff --check`；审计命令只读；未运行软件安装或系统变更命令。
- 负责人要求本任务保持独立 PR，并自动提交 GPT 审核；独立 reviewer 已批准只读范围，审计已完成。
- 如要刷新 apt 索引、升级系统、安装建议包或调整 UFW/网络配置，须先明确范围并按仓库门禁另行审核；当前结果仅作为只读检查报告。
