# CRC target evidence 人工复核/整理执行契约

## 前置批准

- 外部 evidence extraction contract：PR #30，ChatGPT `APPROVE`。
- 外部结果审核：PR #31，ChatGPT `APPROVE`，仅授权人工复核/整理。
- 输入目录：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_20260801T2235EDT/`

## 目标

对 292 条 target-level evidence units 做可追溯人工复核/整理，修正字段映射、重复记录、证据方向、来源定位和 review status；不创造新的生物学结论。

## 允许操作

- 核对 `source_id`、URL/路径、标题/项目、年份、evidence locator、retrieved_at 和 review status。
- 标记重复、冲突、来源不可定位、证据方向不清和需要专家复核的记录。
- 保留 supporting、opposing、unknown 三种语义；unknown 不得改写成 negative。
- 生成外部整理结果和审计日志，仅写入新的外部 `DATA/.../result/...` 目录。

## 禁止操作

- 不执行 Gate scoring、pass/fail、ranking、portfolio/asset recommendation 或下游开发决策。
- 不新增 indication、endpoint、target、pair 或证据来源之外的推断。
- 不把原始数据、缓存、结果表或整理结果写入 `StelligenOS`。
- 不用人工判断替代来源；所有修改必须保留原始值、修改理由和复核者/时间戳。

## 计划输出

写入外部目录 `.../result/gen_iet_crc_target_evidence_manual_review_<run_id>/`：

- `target_evidence_units_reviewed.tsv`
- `target_evidence_review_queue.tsv`
- `target_evidence_conflicts.tsv`
- `source_manifest.json`
- `review_report.md`
- `external_review_worklog.md`

人工复核完成后，必须再提交独立结果审核 PR；未获 ChatGPT `APPROVE` 前不得进入 Gate 或任何排序/推荐阶段。
