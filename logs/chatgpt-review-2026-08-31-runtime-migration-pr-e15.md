# ChatGPT 审核记录：Runtime Migration PR E15 —— TGT-07 / MOD-TGT07 施工合同（design-only）

- 日期：`2026-08-31`
- PR：#134 `task_20260831_runtime-migration-pr-e15`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求 / 逐轮回复贴入该对话）
- 被审核 HEAD：`3747f8e`（第一轮修订后）
- Merge 提交：`7684d27`（`Merge pull request #134 from leezx/task_20260831_runtime-migration-pr-e15`）
- 结论：**APPROVE @ `3747f8e`**。「APPROVE —— PR E15 可以 merge，E15 construction
  contract 可以正式冻结。merge + 独立 approval-record PR 收口后，下一阶段是 PR E16 =
  MOD-TGT07@1.0.0 implementation，即第八个也是最后一个 primary Module；E16 需另行
  做 pre-code scoping，且只有 E16 implementation 真正通过后才解除
  `MIGRATION_PENDING`。」GitHub connector 每轮均 `403 Resource not accessible by
  integration`，REQUEST_CHANGES / APPROVE 的 GitHub review state 未回写；
  `AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260831_runtime-migration-pr-e15-approval-record`）
中补登，按 PR #95 … #133 先例。本 PR 同时把
`manifests/runtime_migration_pr_e15_manifest.yaml` 补成 approved。不改 PR E15 的
合同、drawing、测试或 handoff 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e15_manifest.yaml` 的 `scoping_decisions`
（E15-1…E15-8）、`seven_required_tightenings`（逐字）与
`three_headline_conclusions`，以及
`docs/handoff/2026-08-31-runtime-migration-pr-e15.zh-CN.md`。要点：

- E15 是 **CONSTRUCTION_CONTRACT_ADD**，与 E1 / E3 / E5 / E7 / E9 / E11 / E13
  同型：只交付
  `src/contracts/gate_modules/tgt07_shedding_soluble_antigen_sink_liability.yaml`
  的 17 项施工合同 + human-readable drawing + parity / validation 测试 + 17 项
  验收清单 + manifest / handoff / worklog append。**不交付任何实现**。canonical
  Gate 名 "Shedding / Soluble-Antigen / Sink Liability"。`MOD-TGT07`
  `primary_module_version` 保持 `0.0.0`（PR E16 才 bump 到 `1.0.0`）；binding /
  registry / README / built-roster test 一律不动（唯一既有文件改动是
  `logs/worklog.md` append）；`MIGRATION_PENDING` 保持。main 当前 built 7 个
  （TGT-01/02/03/04/05/06/08），TGT-07 未实现 —— TGT-07 是第八个也是最后一个。
- **7 个 required tightening**（审核方 closing summary，逐字冻结在合同）：
  1. **Option A** —— 正向 `INDIRECT_STRONG` 传播成 `POSITIVE / INDIRECT_STRONG`；
     legal Direction × Strength pair 恰好 6 个；无 `NEGATIVE / INDIRECT_STRONG`。
  2. **below-detection / below-quantitation-limit** 的 soluble-antigen 定量是
     `CONTEXTUAL` —— 既不是正向 `INDIRECT_STRONG` 也不是 `NEGATIVE`；新 CLOSED
     `circulating_soluble_target_status` typed enum
     {`QUANTIFIED_PRESENT`, `BELOW_DETECTION_OR_QUANTITATION_LIMIT`,
     `MIXED_OR_UNRESOLVED`, `NOT_ESTABLISHED`} 承载它。
  3. canonical `NEGATIVE / DIRECT` **只能**由一个 qualified
     `SOLUBLE_ANTIGEN_TMDD_ANALYSIS`（`exposure_scenario_class ==
     INTENDED_ADC_EXPOSURE`，结论 `NO_MATERIAL_SOLUBLE_SINK`）产生；「某个
     same-target 药没看到 sink」永远不能直接产生 `NEGATIVE / DIRECT`。
  4. fatal **不用** TGT-06 式 Route A / Route B convergence —— 一个 qualifying
     DIRECT observation，`sink_materiality_outcome ==
     MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`，且满足 clinical
     source path **或** TMDD source path，即触发 `POTENTIAL_FATAL_PATTERN`；
     clinical 与 TMDD 是两条备选 source path，不是两条 convergence route；
     **v1 单观测 clinical fatal path 无强制 `reproducibility_status` predicate**
     —— `reproducibility_status` 保持 optional factual metadata，永不是 fatal 或
     machine-acceptance gate（`reproducibility_status == NOT_ESTABLISHED` 的
     clinical observation，只要满足其余全部条款，仍然 fatal-eligible）；无 global
     cancellation precondition（fatal 信号是 `POSITIVE / DIRECT` 的严格子集）。
  5. 引入 lightweight 单字符串 `sink_exposure_context_id`（配
     `sink_exposure_context_basis`），**仅**在 qualifying DIRECT observation 上
     REQUIRED；同一 sink-exposure context 的 material-vs-no-material 才是
     `CONFLICTING`；**无** TGT-06 式 `declared_multi` / `IDENTIFIED_MULTI` /
     第三态机制，**无** set-projection helper。
  6. TMDD / clinical 的 DIRECT 与 fatal authority 由 typed status 承载 ——
     `tmdd_input_adequacy_status` / `same_target_therapeutic_match_status` /
     `soluble_antigen_attribution_status` / `analysis_validation_status` /
     `exposure_scenario_class` —— E16 **永不** semantic-parse prose 去获得 DIRECT
     或 fatal authority。
  7. `SolubleAntigenEvidenceCompletion` 恰好 **4 条** search-completion 轴
     （`soluble_antigen_quantitation_search_complete` /
     `sheddase_processing_search_complete` / `secreted_isoform_search_complete` /
     `same_target_pk_pd_or_tmdd_search_complete`），**无**
     `qualifying_indirect_evidence_context_ids` set；定量轴为 true 当且仅当
     CRC-patient 与 healthy-donor 两个 serum / plasma 子空间都已 search / exhaust；
     第 4 轴明确覆盖 clinical PK / PD 与 target-mediated-disposition 分析。
- 3 条 headline conclusion（逐字冻结在合同顶部，测试断言与 manifest 等值）：
  可测量的 soluble form ≠ material antigen sink（quantified circulating soluble
  target / documented sheddase processing / validated secreted isoform 至多在
  INDIRECT_STRONG 支撑 sink-liability class；materiality 需 DIRECT —— documented
  same-target PK / PD sink effect 或 qualified quantitative TMDD analysis；一个
  浓度值，包括低值或 below-assay-limit 值，永不被 Module 转成 universal material-
  sink threshold）；soluble-antigen materiality 依赖 exposure context（DIRECT
  observation 绑定 auditable local sink-exposure context；一个 clean DIRECT
  material-sink context 足以 `POSITIVE / DIRECT`，canonical `NEGATIVE / DIRECT`
  需 qualified intended-ADC TMDD 证明无 material soluble sink；相反 DIRECT 结论
  只有指向同一 sink-exposure context 时才 CONFLICTING；v1 无 conflict resolver）；
  TGT-07 potential-fatal 信号是 `POSITIVE / DIRECT` 的严格子集，不是 convergence
  rule（一个 qualifying DIRECT observation 即可 surface `POTENTIAL_FATAL_PATTERN`；
  clinical 与 TMDD 是备选 qualified source path；机器永不裁决 fatality / KILL /
  HOLD / 疗效 / Candidate-level 后果）。
- items 03/05/07/08 对冻结 PR D TGT-07 做 normalized-equality parity；item 04
  做 EXACT set-equality。确认 frozen PR D TGT-07 **无 `inference_guard` 字段**
  （EVGAP-01 是 TGT-04 专属）。8 observation kinds、CLOSED
  `sink_materiality_outcome` enum（5 值）、单字符串 `sink_exposure_context_id`
  身份、**无 dedicated raw-value reuse-parity 分支**。

## 审核往返（2 轮）

### Round 1 —— REQUEST_CHANGES @ `11922dc`

被审核 HEAD `11922dc`；exact-head CI run 33450076820 —— verify (3.11) +
verify (3.12) 均 success。

审核方确认主体合同成立、**不要重开**：design-only boundary；PR D items
03/05/07/08 parity + item 04 exact-set parity；Option A；恰好 6 legal Direction ×
Strength pairs；无 `NEGATIVE / INDIRECT_STRONG`；below-LOD/LOQ → CONTEXTUAL；
canonical `NEGATIVE / DIRECT` 只来自 intended-ADC TMDD；frozen ordered
aggregation；same-context only CONFLICTING；v1 无 machine conflict resolver；无
cross-observation DIRECT synthesis；lightweight 单字符串
`sink_exposure_context_id`；四轴 completion + CRC / healthy dual-subspace 定量
要求；无 `qualifying_indirect_evidence_context_ids`；无 raw numeric threshold /
parity branch；proposal-relative EvidenceRole mapping；fatal = one predicate +
two alternative source paths；无 fatal global cancellation precondition；3 条
headline conclusion。

**1 个窄 blocker：**

- **clinical fatal source path 误加了强制 `reproducibility_status == QUALIFIED`
  predicate** —— 该 drift 传播进 item 08 clinical_source_path、item 12
  `required_is_true_iff`、item 13 machine acceptance、`seven_required_tightenings`、
  manifest `E15-4`，测试也直接断言 clinical path 必须含该 predicate。这与 pre-code
  ruling 矛盾：frozen PR D fatal 是 singular authority（"circulating soluble
  antigen demonstrated, or quantitatively modelled ... to materially compromise
  clinically achievable exposure"）—— 一个 clinical observation，只要
  same-target / attribution / analysis-validation 均 QUALIFIED 且已直接 documented
  `MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`，即足以 surface
  machine-local `POTENTIAL_FATAL_PATTERN`；第二道 reproducibility gate 会造成
  false negative（一个强的单次 clinical PK observation，
  `reproducibility_status == NOT_ESTABLISHED`，会得到 `fatal_review.required ==
  false`）。**FIX**：删除 `reproducibility_status == QUALIFIED` 作为 clinical
  source path 的 fatal / machine-acceptance 前提；`reproducibility_status` /
  `reproducibility_basis` 保留为 **optional factual metadata**（上游给出时携带、
  展示给人工 reviewer，永不是 gate）。把误冻结的「no extra reproducibility beyond
  the clinical path's own per-observation `reproducibility_status == QUALIFIED`
  gate」重写为「There is NO mandatory reproducibility predicate for the
  single-observation clinical fatal path in v1」。regression：qualified clinical
  sink-effect observation + `MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`
  + `reproducibility_status == NOT_ESTABLISHED` → 仍 fatal-eligible；
  attribution / same-target-match / analysis-validation `NOT_ESTABLISHED` → 仍
  阻断 fatal。

修订：合同 item 06 `upstream_qualified_factual_states`、item 08
`clinical_source_path` + `two_source_paths_not_routes`、item 12
`fatal_review.required_is_true_iff` + `clinical_attribution_basis_refs`、item 13
classification-driving basis list + fatal acceptance check、
`seven_required_tightenings` 4；drawing row 8 + normalized-observation
conceptual shape；`tests/test_tgt07_module_construction_contract.py` 78 → 83
（新增 `ReviewRound1RegressionTests`）；manifest `E15-4` scoping decision +
`seven_required_tightenings` 4 + `chatgpt_review: REQUEST_CHANGES` +
`review_rounds: 1` + `test_count_after_round_1: 1796` + `review_round_1` block；
worklog append。本地全量 unittest 1791 → 1796 OK。提交 `3747f8e`。CI（exact-head
run 33451531965）—— verify (3.11) + verify (3.12) 均 success。

### Round 2 —— APPROVE @ `3747f8e`

被审核 HEAD `3747f8e`；exact-head CI run 33451531965 success。审核方确认 round-1
唯一 blocker **已完整关闭**：

- clinical fatal source path 已删除 mandatory `reproducibility_status == QUALIFIED`；
- 合同明确规定 `reproducibility_status == NOT_ESTABLISHED` 的 clinical
  observation，只要其它 attribution / validation / material-compromise 条件全部
  成立，仍然 fatal-eligible；
- `reproducibility_status` 已明确降为 optional factual metadata，不再是
  classification-driving、fatal 或 machine-acceptance predicate；
- item 12 `required_is_true_iff`、item 13 acceptance、`seven_required_tightenings`
  4 均已同步成「no mandatory reproducibility predicate」；
- regression tests 锁住这一修复，并确认 `same_target_therapeutic_match_status` /
  `soluble_antigen_attribution_status` / `analysis_validation_status` 等真正
  需要的 clinical qualification gate 仍然存在。

此前已经通过的 E15 science / architecture 没有被重新打开，因此 E15 construction
contract 可以正式冻结。

非阻断 housekeeping（merge 前已处理）：GitHub PR #134 description 曾保留旧的
「clinical path's own `reproducibility_status == QUALIFIED` gate」措辞；仓库内
contract / manifest / tests 已是正确的新语义，merge 前顺手更新了 PR body，不影响
APPROVE。

E15 最终冻结状态：Option A / `POSITIVE / INDIRECT_STRONG` 传播；恰好 6 legal
Direction × Strength pairs；existence-proof ordered aggregation（step 表 0–7，
stop-at-first-match）；v1 无 machine conflict resolver；single-string
`sink_exposure_context_id`（无 declared_multi / 第三态 / set-projection）；四轴
`SolubleAntigenEvidenceCompletion` + CRC / healthy dual-subspace 定量、无
`qualifying_indirect_evidence_context_ids`；no cross-observation synthesis of
positive DIRECT；below-detection → CONTEXTUAL；canonical `NEGATIVE / DIRECT` 只
来自 intended-ADC TMDD；fatal = one predicate + two alternative source paths、
无 global cancellation precondition、**无强制 reproducibility predicate**；
design-only；MOD-TGT07 `0.0.0`；`MIGRATION_PENDING` 保持。

两轮状态：Round 1 —— 1 narrow blocker → CLOSED；Round 2 —— 无新 blocker。

**结论：APPROVE —— PR E15 可以 merge。下一步进入 PR E16 = MOD-TGT07@1.0.0
deterministic implementation（第八个也是最后一个 primary Module；PR E16 解除
`MIGRATION_PENDING`）—— 需另行 go-ahead。**

## Merge

- PR #134 于 `2026-08-31` 以 `--merge` 合入 `main`，merge 提交 `7684d27`。
- 独立 docs-only PR `task_20260831_runtime-migration-pr-e15-approval-record`
  补登：本审核记录（2 轮完整往返 + merge）+
  `manifests/runtime_migration_pr_e15_manifest.yaml` →
  `status: approved` / `chatgpt_review: APPROVE` / `approved_tip: 3747f8e…` /
  `merge_commit: 7684d27` / `review_rounds: 2` / `test_count_at_approval: 1796` /
  `approval_record_pr` / `review_round_2` block。不改 PR E15 的合同、drawing、
  测试或 handoff 内容。
- 状态：8 个 primary Module 施工合同已全部 APPROVE（TGT-01…TGT-08）；**已实现
  7 个**（TGT-01/02/03/04/05/06/08 @ 1.0.0）。MOD-TGT07 `primary_module_version`
  仍 `0.0.0`，PR E16 才 bump。`MIGRATION_PENDING` 保持（八个 primary Module
  全部建成前不解除；余 TGT-07 属 PR E16）。
- Next：**PR E16 = MOD-TGT07@1.0.0** deterministic implementation —— 第八个也是
  最后一个 primary Module，PR E16 解除 `MIGRATION_PENDING`。需另行 go-ahead 且
  先做 pre-code scoping。
