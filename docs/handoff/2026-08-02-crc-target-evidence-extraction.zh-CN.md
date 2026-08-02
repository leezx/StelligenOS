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

## 外部结果可审计元数据

以下是外部结果目录的审计记录，不是结果数据副本。审核者可用相同路径和 SHA-256 对外部文件复核；原始数据、cache 和结果表仍不进入仓库。

| 文件 | 行数（不含表头） | 列结构 | SHA-256 |
|---|---:|---|---|
| `target_evidence_units.tsv` | 292 | `evidence_id`, `gene_symbol`, `target_name`, `dimension`, `evidence_direction`, `evidence_strength`, `statement`, `source_id`, `source_path_or_url`, `source_title_or_project`, `source_year`, `evidence_locator`, `retrieved_at`, `review_status` | `adc8fff738d9747f413aa2bcec7d95034782ed8cb9806bd5d32b6fe7de35124d` |
| `target_evidence_summary.tsv` | 41 | `gene_symbol`, `target_name`, `input_evidence_class`, `clinical_adc_names`, `dimensions_with_units`, `supporting_unit_count`, `opposing_unit_count`, `unknown_unit_count`, `gate_score_status`, `gate_pass_status`, `human_review_status` | `6426fac0c23a91ccccaa68ac4fcd13078e4535470eae5e3fbd2cdcd0256e6bb6` |
| `target_opposing_evidence.tsv` | 32 | 与 `target_evidence_units.tsv` 相同 | `72bc0701f42988c0e5eee3ea7d3ccdcc9594b5c289067365c0c55bd06ef6c1f6` |
| `target_unknowns.tsv` | 172 | 与 `target_evidence_units.tsv` 相同 | `e957dd3ae38da3ba06352a1bc8ca62bd7a5f8d3a09e73456dcc47d2bd2066e12` |
| `source_manifest.json` | JSON | `run_id`, `retrieved_at`, `sources[]`（含 `source_id`, `path`, `sha256`, `role`） | `59e17e1285b25864386e2955d9a9027f9a5bf2a7843c87e566e1130274e683d3` |
| `run_report.md` | Markdown | 运行摘要、计数、边界和限制 | `a37da34d8c75678c6a4f8753a82a99b7671a333e8511f273e0fae1a7d6e41f09` |
| `external_run_worklog.md` | Markdown | 外部运行步骤和门禁记录 | `b2eaa60fe528ba01f5b016e51fb0fa6eab9924ac15b75795a8dda071fd16420d` |

统计校验：`target_evidence_units.tsv` 292 行 = supporting 88 + opposing 32 + unknown 172；`target_evidence_summary.tsv` 41 行，按行计数合计 supporting 88、opposing 32、unknown 172；`target_opposing_evidence.tsv` 与 `target_unknowns.tsv` 分别为 32/172 行。所有 summary 行的 `gate_score_status=not_executed`、`gate_pass_status=not_assessed`。
