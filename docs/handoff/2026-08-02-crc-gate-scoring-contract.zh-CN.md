# 任务交接备忘：CRC Gate 评分执行契约

- 任务编号：`task_20260802_crc-gate-scoring-contract`
- 前置状态：PR #35 已批准工作包准备；真实专家复核尚未完成
- 当前状态：`CONTRACT_PENDING_CHATGPT_REVIEW_BLOCKED_ON_EXPERT_REVIEW`
- Gate 拓扑：冻结 45 个既有 Gate，不新增、不改写

## 下一步

1. 提交本 contract-only PR 给 ChatGPT 审核。
2. 同时等待真实专家完成复核，并通过独立结果审核 PR。
3. 两道门都获得 `APPROVE` 后，才可按冻结拓扑执行外部 Gate 评分。

## 禁止事项

- 不提前执行评分或生成任何 Gate 分数。
- 不使用未经过专家审核的 `pending_expert_review` 证据作为最终评分输入。
- 不执行排序、资产推荐、pair 发布或下游开发。

