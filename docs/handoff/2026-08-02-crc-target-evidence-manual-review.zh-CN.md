# 任务交接备忘：CRC target evidence 人工复核/整理

- 任务编号：`task_20260802_crc-target-evidence-manual-review`
- 前置结果审核：PR #31，ChatGPT `APPROVE`
- 当前状态：`CONTRACT_PENDING_CHATGPT_REVIEW`
- 输入：外部 evidence extraction 结果目录；固定 292 条 evidence units、41 targets
- 当前 tip：以 PR 页面实时 HEAD 为准；本 handoff 自引用后续提交不预先自列

## 范围

只做来源字段、证据方向、重复/冲突、unknown 语义和人工复核状态的审计整理。不得新增生物学结论，不得执行 Gate 评分、排序、推荐或下游开发。

## 下一步

1. 提交本契约独立 PR 给 ChatGPT 审核。
2. 获 `APPROVE` 后才在外部 DATA 生成人工复核结果。
3. 运行完成后创建独立结果审核 PR。
