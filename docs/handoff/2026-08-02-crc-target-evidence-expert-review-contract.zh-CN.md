# 任务交接备忘：CRC target evidence 专家生物学复核契约

- 任务编号：`task_20260802_crc-target-evidence-expert-review-contract`
- 前置结果审核：PR #33，ChatGPT `APPROVE`
- 当前状态：`CONTRACT_PENDING_CHATGPT_REVIEW`
- 输入：外部 `pending_expert_review` evidence package，292 条、41 targets
- 输出边界：只允许外部 `DATA`；本仓库仅保存契约和审计元数据

## 下一步

1. 提交本 contract-only PR 给 ChatGPT 审核。
2. 只有获得 `APPROVE` 后，才允许安排或执行人工专家生物学复核。
3. 专家复核完成后，创建独立结果审核 PR；在结果审核批准前不得进入 Gate 评分、排序或推荐。

## 当前禁止事项

- 不执行专家复核。
- 不新增或修改 evidence unit 的生物学结论。
- 不执行 Gate scoring、ranking、asset recommendation、pair 生成或下游开发。

