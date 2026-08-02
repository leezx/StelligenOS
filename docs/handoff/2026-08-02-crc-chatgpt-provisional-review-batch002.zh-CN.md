# 任务交接备忘：CRC ChatGPT provisional review Batch 002

- 任务编号：`task_20260802_crc-chatgpt-provisional-review-batch002`
- 前置批准：PR #40，ChatGPT `APPROVE`
- 当前状态：`RESULT_PENDING_CHATGPT_REVIEW`
- 外部输入目录：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_expert_review_20260802T025442Z/batches_20/`
- 外部输入文件：`batch_002.tsv`
- 输入规模：20 条 evidence rows（不含表头）
- compact payload SHA-256：`2fce8677cd8b68b46a44c58f7d74575a90604480ebbd53d0854faa4fd2e86af8`
- 外部结果文件：`batch_002_chatgpt_provisional_review.tsv`
- 结果 SHA-256：`030b45ecfdf18e611e33307c43b6d917b50e26d63d6d46ad8a7eec813e0975d6`

## 执行边界

- 仅允许 ChatGPT 对输入的 20 条 evidence statement 做逐条 provisional decision：`retain`、`downgrade`、`reclassify_unknown`、`conflict_queue` 或 `source_not_verified`。
- 输出必须保持 evidence_id 原顺序，并给出一句话理由及汇总计数。
- 不执行 Gate scoring、ranking、pair generation、recommendation 或 downstream development。
- 不把 ChatGPT provisional review 当成人类专家签字。
- 原始输入和结果只放在外部 `DATA`；StelligenOS 仓库只保存审计元数据。
- Batch 002 结果完成后，必须创建独立结果审核 PR，并取得 ChatGPT `APPROVE` 才能继续使用。

## ChatGPT provisional result

- Input/output：20/20
- Targets：4（CEACAM5、EGFR、ERBB2、ERBB3）
- Decisions：`retain=19`、`downgrade=1`、`reclassify_unknown=0`、`conflict_queue=0`、`source_not_verified=0`
- Local validation：逐条计数与 ChatGPT SUMMARY 一致。

## 下一步

已通过纯文本将 compact Batch 002 payload 发送给 ChatGPT；结果已保存到外部 DATA，计数和 checksum 已核对。下一步创建独立结果审核 PR，提交 ChatGPT 审核。
