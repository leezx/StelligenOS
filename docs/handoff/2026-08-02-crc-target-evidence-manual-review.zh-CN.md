# 任务交接备忘：CRC target evidence 人工复核/整理

- 任务编号：`task_20260802_crc-target-evidence-manual-review`
- 前置结果审核：PR #31，ChatGPT `APPROVE`
- 当前状态：`RESULT_PENDING_CHATGPT_REVIEW`
- 输入：外部 evidence extraction 结果目录；固定 292 条 evidence units、41 targets
- 当前 tip：以 PR 页面实时 HEAD 为准；本 handoff 自引用后续提交不预先自列
- ChatGPT 审核：PR #32，明确 `APPROVE`；允许开始外部人工 evidence review/curation
- 外部整理：已完成，等待独立结果审核 PR
- 外部输出：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_manual_review_20260801T2258EDT/`

## 范围

只做来源字段、证据方向、重复/冲突、unknown 语义和人工复核状态的审计整理。不得新增生物学结论，不得执行 Gate 评分、排序、推荐或下游开发。

## 下一步

1. 提交本契约独立 PR 给 ChatGPT 审核。
2. 获 `APPROVE` 后才在外部 DATA 生成人工复核结果。
3. 运行完成后创建独立结果审核 PR。

## 审核门禁

- 每条整理记录必须保留原始值、修改理由、复核者和时间戳。
- 只允许审计来源字段、证据方向、重复/冲突和 review status；不得新增生物学结论。
- unknown 仍表示未解决，不得改写成 negative。
- Gate scoring、ranking、recommendation 和 downstream development 未获授权。

## 外部整理摘要

- 输入：292 条 evidence units、41 targets。
- 保留：292 条；异常队列：0 条；冲突：0 条。
- supporting/opposing/unknown：88/32/172，方向计数未改变。
- Biological statement 和 evidence direction：未修改。
- 原始值：全部保留在 `original_*` 列；`expert_review_status` 全部为 `pending_expert_review`。
- 输出文件：`target_evidence_units_reviewed.tsv`、`target_evidence_review_queue.tsv`、`target_evidence_conflicts.tsv`、`source_manifest.json`、`review_report.md`、`external_review_worklog.md`。
- 运行限制：未执行 Gate scoring、ranking、recommendation、范围扩展或下游开发。
- 独立结果审核：当前分支用于提交外部整理结果的审核门；在 ChatGPT `APPROVE` 前不得将整理结果用于下一阶段。

### 外部输出审计元数据

| 文件 | 行数（不含表头） | SHA-256 |
|---|---:|---|
| `target_evidence_units_reviewed.tsv` | 292 | `a1c6aaeaf76c377ec3edc5f09abe0b747fd72b493d92f74556c51aba570f480a` |
| `target_evidence_review_queue.tsv` | 0 | `a77a3515d2d25deaf3fe6195b1d6bbaa5189d4b240e1cad613b71678a004b471` |
| `target_evidence_conflicts.tsv` | 0 | `a77a3515d2d25deaf3fe6195b1d6bbaa5189d4b240e1cad613b71678a004b471` |
| `source_manifest.json` | JSON | `b7c56330f0156988358aadfef0646ef32d48836ab73b6b7b4d9ecd980a95087e` |
| `review_report.md` | Markdown | `23c72ed3a65770966238b87e55f5aa065817aa5510e4fe9d994835653402ef21` |
| `external_review_worklog.md` | Markdown | `0c112371e6807905063c9d73f9b2490ebbcc4a4be09cf9f06498482edff86daf` |
