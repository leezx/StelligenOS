# 任务交接备忘：ChatGPT 分 batch 上传测试

- 任务编号：`task_20260802_crc-chatgpt-expert-review-batch-upload-test`
- 前置 Prompt：PR #37，ChatGPT `APPROVE`
- 当前状态：`BATCH_UPLOAD_TEST_BLOCKED_BROWSER_FILE_POLICY`
- 外部 batch 目录：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_expert_review_20260802T025442Z/batches_20/`

## 测试设计

- 每批 20 条 evidence units，最后一批 12 条。
- 共 15 个 batch，合计 292 条。
- 每批保留完整 TSV 表头和原始字段；`manifest.tsv` 记录行数与 SHA-256。

## 测试结果

- 第 1 批 `batch_001.tsv`（20 条）上传测试失败。
- 浏览器安全层拒绝自动设置本地文件；没有文件被发送给 ChatGPT。
- 未生成 provisional review，未修改 evidence，未执行 Gate scoring、ranking 或 recommendation。

## 下一步

用户在 ChatGPT 对话中手动附加 `batch_001.tsv`，并使用已批准的 Prompt；完成后按 batch 顺序继续。

