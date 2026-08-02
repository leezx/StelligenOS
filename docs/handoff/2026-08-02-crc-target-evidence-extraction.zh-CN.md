# 任务交接备忘：CRC target-level evidence extraction

## 任务信息

- 任务编号：`task_20260802_crc-target-evidence-extraction`
- 分支：`task_20260802_crc-target-evidence-extraction`
- 基线：`task_20260802_crc-target-enumeration-results`，前置结果审核已获批准
- 前置结果审核：PR #29，ChatGPT `APPROVE`
- 当前状态：`CONTRACT_PENDING_CHATGPT_REVIEW`
- 当前 tip：以 PR 页面实时 HEAD 为准；本 handoff 的自引用后续提交不预先自列

## 本次范围

- 只定义 target-level 公共证据提取契约。
- 固定 9 个 CRC indication、36 条 endpoint 和 41 个 target 候选作为输入边界。
- 定义九类证据维度、来源审计字段、unknown/opposing-evidence 语义和外部输出目录。
- 不抓取文献、不下载公共数据、不执行 Gate 评分或排序。

## 下一步

1. 验证仓库边界和契约文档。
2. 显式提交、推送并创建独立 PR。
3. 在 ChatGPT“GitHub PR 信息”对话中提交本契约审核。
4. 只有明确 `APPROVE` 后，才开始外部 target-level evidence extraction。
