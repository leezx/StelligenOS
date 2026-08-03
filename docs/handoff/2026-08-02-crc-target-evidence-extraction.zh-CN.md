# 任务交接备忘：CRC target-level evidence extraction

## 任务信息

- 任务编号：`task_20260802_crc-target-evidence-extraction`
- 分支：`task_20260802_crc-target-evidence-extraction`
- 基线：`task_20260802_crc-target-enumeration-results`，前置结果审核已获批准
- 前置结果审核：PR #29，ChatGPT `APPROVE`
- 当前状态：`CONTRACT_APPROVED_EXTERNAL_RUN_AUTHORIZED`
- 当前 tip：以 PR 页面实时 HEAD 为准；本 handoff 的自引用后续提交不预先自列
- ChatGPT 审核：PR #30，明确 `APPROVE`；允许开始外部 target-level evidence extraction

## 本次范围

- 只定义 target-level 公共证据提取契约。
- 固定 9 个 CRC indication、36 条 endpoint 和 41 个 target 候选作为输入边界。
- 定义九类证据维度、来源审计字段、unknown/opposing-evidence 语义和外部输出目录。
- 本 PR 阶段不抓取文献、不下载公共数据、不执行 Gate 评分或排序。

## 下一步

1. 从已批准的 PR #29 外部枚举结果固定 9 indications、36 endpoints、41 targets 输入。
2. 仅将外部输入、缓存、证据中间文件和结果写入指定 `DATA` 结果目录。
3. 运行九类 target-level evidence extraction，不执行 Gate 评分、排序、资产推荐或范围扩展。
4. 运行完成后创建独立结果审核 PR，提交 ChatGPT 审核；未获批准前不得把结果用于下一阶段。
