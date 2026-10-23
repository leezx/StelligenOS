# Ubuntu 新装系统只读审计交接

## 目标

负责人要求检查其新安装的 Ubuntu 主机，判断是否缺少必要的系统组件，并列出必要安装建议。

## 当前阶段与边界

- 当前阶段：远程只读审计的 PR 前置门禁。
- 目标主机：负责人在本任务中指定的 Tailscale SSH 主机 `100.102.142.49`，登录名 `stelligen`。
- 范围：获批后检查系统版本、内核/架构、磁盘与内存、软件源和更新状态、网络、SSH、防火墙及基础管理工具；输出缺项、理由与建议。
- 不在本阶段读取个人文件、凭据或业务数据；不把外部主机结果或数据存入仓库；不安装软件或更改系统配置。
- 在当前 PR 获得 GPT/ChatGPT 明确 `APPROVE` 前，不连接主机。获批后先完成只读审计并报告；如建议涉及安装或配置，将依据结果和现有授权再判断范围。

## 当前状态

- 已按本地 `AGENTS.md` 与 `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` 确认外部 SSH 检查须经 PR 审核。
- 本地主要工作区存在与本任务无关的未提交改动；本任务在隔离 worktree 中准备，未修改或暂存那些改动。
- 当前尚未 SSH 登录目标机，尚无主机检查结果，尚未安装或修改任何东西。
- Base：`main` at `6f91d8be0b6ae1db914e0e7a0d74757537760825`；任务分支：`task_20261023_ubuntu_system_audit`。
- PR：[PR #147](https://github.com/leezx/StelligenOS/pull/147)，base `main`；code commit `6973b4129d7741196b61d7b0154454392a3175d7`；PR tip 为本次记录 PR 创建信息的 metadata-only 提交；GPT/ChatGPT 审核：待定；阶段放行：未批准。

## 验证与后续

- PR 提交前检查仅覆盖本 handoff 和 worklog 的 diff 与边界，不运行 Ubuntu 命令。
- 负责人要求本任务保持独立 PR，并自动提交 GPT 审核；当前 PR #147 由独立 reviewer agent 按当前 GitHub HEAD 审查。
- 收到明确 `APPROVE` 后，立即执行本只读审计并在本 handoff 与 worklog 记录命令类别、脱敏摘要及结果；非 `APPROVE` 则按审核意见留在同一 PR 修订。
