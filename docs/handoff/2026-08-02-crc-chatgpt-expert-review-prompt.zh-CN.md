# 任务交接备忘：CRC ChatGPT 专家复核 Prompt

- 任务编号：`task_20260802_crc-chatgpt-expert-review-prompt`
- 前置 Gate 契约：PR #36，ChatGPT `APPROVE`
- 当前状态：`PROMPT_APPROVED_READY_FOR_WEB_EXECUTION`
- 输入：外部专家复核工作包中的 292 条 evidence units、41 targets

## 目的

将原本需要外部专家逐条完成的证据复核，改造成可由网页版 ChatGPT 执行的结构化、可追溯预审流程。模型输出必须明确标记为 `chatgpt_provisional_review`，不得冒充人类专家签字。

## 当前边界

- 本 PR 只新增 Prompt 和审计 handoff，不上传或复制外部 evidence 数据。
- 尚未执行 ChatGPT 逐条复核。
- 尚未修改 evidence direction、statement 或 strength。
- 尚未执行 Gate scoring、ranking、pair generation 或 asset recommendation。

## 下一步

1. PR #37 已获 ChatGPT `APPROVE`。
2. 在网页版 ChatGPT 中附加外部 `expert_review_assignment.tsv`，逐条生成 `chatgpt_provisional_review`。
3. 将 ChatGPT 输出保存到外部 `DATA`，再创建独立结果审核 PR；结果审核批准前不得进入 Gate 评分。
