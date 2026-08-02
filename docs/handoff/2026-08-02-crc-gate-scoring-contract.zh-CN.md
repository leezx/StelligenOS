# 任务交接备忘：CRC Gate 评分执行契约

- 任务编号：`task_20260802_crc-gate-scoring-contract`
- 前置状态：PR #35 已批准工作包准备；真实专家复核尚未完成
- 当前状态：`CONTRACT_APPROVED_BLOCKED_ON_EXPERT_REVIEW_RESULT_APPROVAL`
- Gate 拓扑：冻结 45 个既有 Gate，不新增、不改写

## 下一步

1. 等待真实专家完成复核，并通过独立结果审核 PR。
2. PR #36 已获 ChatGPT `APPROVE`；两道门均批准后，才可按冻结拓扑执行外部 Gate 评分。
3. 评分完成后，创建独立结果审核 PR；在该 PR 获批前不得发布排序、推荐或资产决策。

## 禁止事项

- 不提前执行评分或生成任何 Gate 分数。
- 不使用未经过专家审核的 `pending_expert_review` 证据作为最终评分输入。
- 不执行排序、资产推荐、pair 发布或下游开发。
