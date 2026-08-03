# 任务交接备忘：CRC target evidence 专家生物学复核契约

- 任务编号：`task_20260802_crc-target-evidence-expert-review-contract`
- 前置结果审核：PR #33，ChatGPT `APPROVE`
- 当前状态：`CONTRACT_APPROVED_EXTERNAL_EXPERT_REVIEW_AUTHORIZED`
- 输入：外部 `pending_expert_review` evidence package，292 条、41 targets
- 输出边界：只允许外部 `DATA`；本仓库仅保存契约和审计元数据

## 下一步

1. 按 PR #34 的 `APPROVE` 安排或执行外部人工专家生物学复核。
2. 专家复核结果只能写入外部 `DATA`，并记录原始值、复核后值、理由、专家身份/角色、时间戳和来源定位。
3. 专家复核完成后，创建独立结果审核 PR；在结果审核批准前不得进入 Gate 评分、排序或推荐。

## 当前禁止事项

- 不执行专家复核。
- 不新增或修改 evidence unit 的生物学结论。
- 不执行 Gate scoring、ranking、asset recommendation、pair 生成或下游开发。
