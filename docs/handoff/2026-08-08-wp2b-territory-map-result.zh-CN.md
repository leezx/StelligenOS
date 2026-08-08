# Handoff：WP2B CRC Opportunity Territory Map — 结果 PR

- 日期：`2026-08-08`
- 任务分支：`task_20260808_wp2b-territory-map-result`
- 基线：`main`
- 交付物类型：**结果 PR（仅仓库侧：哈希、校验状态、reconciliation 摘要；不含任何
  territory 内容、不含任何 CRC 结论）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 消费：`docs/pools/wp2b_crc_territory_map_run.yaml` 的 `authorises_run_count`
  由 `1` 归零为 `0`（`run_count_consumption_is_process_enforced_not_code_enforced: true`，
  本 PR 就是那个流程步骤）。

## 一、本 PR 不包含什么

按 `output.location_in_repository: forbidden`，本 PR **不包含**任何 territory
内容、任何 CRC 分子亚型/靶点/竞品名称、任何 route 分布之外的科学结论。七份必需
交付物（`territory_map.json`、`territories.tsv`、
`search_space_admissions.json`、`sponsor_evidence_advantage.json`、
`source_manifest.json`、`run_report.md`、`verify_package.py`）均只存放于外部
工作区
`DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/wp2b_crc_territory_map_20260807T180000Z/`，
不进入本仓库。

## 二、本 PR 包含什么

1. 本 handoff 文档。
2. 对 `docs/pools/wp2b_crc_territory_map_run.yaml` 的更新：
   - `run.execution_status`: `authorised_not_yet_executed` → `executed_result_delivered`
   - `run.authorises_run_count`: `1` → `0`
   - 新增 `run.result` 小节，记录七份交付物的清单（文件名，不含 SHA-256——哈希
     只保留在外部 `manifest_sha256.json` 一处，避免仓库内出现第二份可能漂移的
     哈希记录）、`VAL-T01`~`VAL-T21` 的通过状态、以及
     `territory_count`/`route_distribution` 这两个**不含 territory 内容**的
     汇总数字。

## 三、校验结果摘要

`verify_package.py`（外部工作区内，独立可运行，无仓库依赖）对
`VAL-T01`–`VAL-T21` 的检查结果：**21/21 通过**。完整逐条结果见外部
`run_report.md` 与 `verify_package.py` 的运行输出；本仓库只记录"21/21 PASS"
这一聚合状态，不复制逐条 detail 文本（避免仓库内出现第二份可能漂移的校验记录）。

## 四、Territory 计数与 route 分布（聚合数字，非内容）

- 25 个编号 Pass A 候选（27 个工作 ID，因 A6/A12 各拆分为二）。
- **17** 个 territory 本次被授予 admission；**1** 个（编号，不公开）作为
  merge-candidate 并入其他 territory；**1** 个（编号，不公开）在 Pass B 被排除；
  **8** 个仍停留在 Pass A 枚举、本次未被 grounding，留待后续。
- Route 分布：`ACTIVE_SEARCH` **0**、`WATCHLIST` **17**、`PARTNER_ONLY` **0**、
  `OUT_OF_MANDATE` **0**。
- `expected_active_band`（4–8，reconciliation reference，非达标要求）未达到；
  运行契约本身声明这不构成失败条件。原因与是否需要后续再评估的建议，记录在外部
  `run_report.md`，不复制到本仓库。

## 五、本 PR 明确不做的事

不生成任何 program wedge；不生成任何 target 或 target-territory pair；不执行
任何 Gate、T-chain 或三重预筛；不解除 `EVGAP-01`/`EVGAP-02`；不复活或修改
Level 01 的 9×41×369 轴；不裁定 `GAP-P07`；不将任何 territory 的 `WATCHLIST`
路由当作 WP3 授权——按冻结的 `OpportunityTerritory@0.1.0`
`downstream_relationship`，WP3 只消费持有有效 `ACTIVE_SEARCH` admission 的
territory，本次运行没有产生任何一个，因此本 PR 不构成、也不暗示任何 WP3 授权。

## 六、审核状态

等待人类负责人 `APPROVE`。本 PR 不适用 `AGENTS.md`「审核豁免」。
