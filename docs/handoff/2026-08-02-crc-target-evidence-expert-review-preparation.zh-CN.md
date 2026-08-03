# 任务交接备忘：CRC target evidence 专家复核工作包准备

- 任务编号：`task_20260802_crc-target-evidence-expert-review-preparation`
- 前置契约：PR #34，ChatGPT `APPROVE`
- 当前状态：`PREPARATION_APPROVED_PENDING_REAL_EXPERT`
- 外部输出：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_expert_review_20260802T025442Z/`

## 已完成

- 从已批准的外部 manual-review package 准备 292 条 evidence units 的专家复核工作表。
- 固定 41 个 targets，supporting/opposing/unknown 保持 `88/32/172`。
- 保留全部原始字段，仅追加空白专家复核字段。
- 生成复核说明、统计和 SHA-256 审计信息。

## 尚未完成

- 尚未进行专家生物学复核。
- 尚未填写专家决定、理由、身份/角色、时间戳或来源定位。
- 尚未修改任何生物学 statement 或 evidence direction。

## 边界

- 工作包只写入外部 `DATA`，不复制到 `StelligenOS`。
- 不执行 Gate scoring、ranking、asset recommendation、pair generation 或 downstream development。
- PR #35 已获 ChatGPT `APPROVE`。获得真实专家复核结果后，必须创建独立结果审核 PR；在该 PR 获 ChatGPT `APPROVE` 前不得进入下一阶段。
