# CRC Target Evidence 专家生物学复核执行契约

- 任务分支：`task_20260802_crc-target-evidence-expert-review-contract`
- 前置结果审核：PR #33，ChatGPT `APPROVE`
- 输入：外部整理后的 292 条 evidence units、41 targets
- 输入目录：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_manual_review_20260801T2258EDT/`
- 当前阶段：contract-only，等待 ChatGPT 审核

## 目的

定义由具备相应领域资质的人工专家对外部 evidence package 进行生物学有效性复核的边界。此 PR 只定义流程，不执行专家复核，不产生新的生物学结论，不修改外部数据。

## 允许范围

- 核对每条证据的来源、研究对象、实验系统、疾病背景和结论是否被原始来源支持。
- 标记证据是否需要降级、保留、转为 unknown 或进入冲突队列，但不得静默覆盖原始字段。
- 对每个决定记录原始值、复核后值、理由、专家身份/角色、时间戳和来源定位。
- 保留 `supporting`、`opposing`、`unknown` 三类语义；`unknown` 不等于 `negative`。

## 明确禁止

- 不新增 indication、endpoint、target 或 pair。
- 不执行 Gate scoring、ranking、asset recommendation 或 downstream development。
- 不把 ADC 先例、表达或内吞证据解释为 CRC 疗效或安全窗结论。
- 不把外部数据、结果、cache、数据库或原始文献复制进 `StelligenOS`。

## 输出与审核

- 专家复核输出只能写入外部 `DATA` 结果目录。
- 仓库只保留契约、handoff、worklog 和审核记录等小型文本。
- 完成外部复核后必须另建独立结果审核 PR；在 ChatGPT `APPROVE` 前不得进入 Gate 或推荐阶段。

