# 任务交接备忘：全局 PR 审核与 Worklog 门禁

## 任务信息

- 任务编号：`task_20260801_global-review-worklog-rules`
- 当前分支：`task_20260801_gen-iet-phase9-freeze-release`
- PR：将在本分支更新后提交现有任务 PR 供 GPT/ChatGPT 审核
- 当前状态：`PENDING_CHATGPT_APPROVAL`
- 时间：`2026-08-01 America/New_York`

## 本次变更

- 将 PR 审核门禁提升为所有工作类型的全局规则，不再只适用于代码或 Phase。
- 明确 GPT/ChatGPT `APPROVE` 前不得进入下一工作、下一 Phase、依赖性外部运行或范围扩展。
- 明确 `REQUEST_CHANGES` 后必须留在同一个 PR 内最小修订并重新审核。
- 明确所有读取、决策、命令、修改、验证、外部运行、失败、修正和审核反馈都必须带时间戳记录到 worklog。
- 明确外部数据/结果不得进入仓库，PR 通过软件契约、manifest、摘要、校验信息和外部路径引用保持可审计性。

## 明确未改动

- 未修改业务 Gate、Model、Rule、Registry 或数据处理逻辑。
- 未新增数据、数据库、cache、result、weights 或临时产物。
- 未修改 `Zhixins-KB`。

## 验证与审核门

- 待运行 `scripts/verify_repository_boundary.sh`、相关规范测试和 `git diff --check`。
- 待推送当前任务分支并更新 PR aggregate diff。
- 在 ChatGPT 明确返回 `APPROVE` 前，本任务不得作为已生效全局配置继续推进依赖工作；当前 PR 是唯一审核表面。

## 下一步

1. 提交当前规则变更到 PR。
2. 通过 GitHub 插件把 PR 完整 diff、协议、handoff、worklog 和验证结果交给 ChatGPT 审核。
3. 若 `REQUEST_CHANGES`，只在同一 PR 修订；若 `APPROVE`，由负责人决定 merge。

## 数据边界声明

本仓库只保存架构系统文档、代码和治理文本；本次没有新增任何数据、缓存或结果文件。
