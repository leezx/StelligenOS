# 任务交接备忘：CRC target-level evidence extraction

## 任务信息

- 任务编号：`task_20260802_crc-target-evidence-extraction`
- 分支：`task_20260802_crc-target-evidence-extraction`
- 基线：`task_20260802_crc-target-enumeration-results`，前置结果审核已获批准
- 前置结果审核：PR #29，ChatGPT `APPROVE`
- 当前状态：`CONTRACT_APPROVED_EXTERNAL_RUN_AUTHORIZED`
- 当前 tip：以 PR 页面实时 HEAD 为准；本 handoff 的自引用后续提交不预先自列
- ChatGPT 审核：PR #30，明确 `APPROVE`；允许开始外部 target-level evidence extraction
- 外部运行：已完成，等待独立结果审核 PR
- 外部结果：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_20260801T2235EDT/`

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

## 外部运行摘要

- 输入：已批准枚举结果中的 9 个 indication、36 个 endpoint、41 个 target。
- 输出：292 条 target-level evidence units；88 条 supporting、32 条 opposing、172 条 unknown。
- 结果文件：`target_evidence_units.tsv`、`target_evidence_summary.tsv`、`target_opposing_evidence.tsv`、`target_unknowns.tsv`、`source_manifest.json`、`run_report.md`、`external_run_worklog.md`。
- 边界验证：`scripts/verify_repository_boundary.sh` 通过；仓库未新增数据、cache、数据库、结果表或模型权重。
- 运行限制：未执行 Gate 评分、排序、资产推荐，未扩展 indication/endpoint/pair。
- 审核状态：所有 evidence units 标记为 `machine_extracted_requires_human_review`；结果必须先经独立 PR 审核。
