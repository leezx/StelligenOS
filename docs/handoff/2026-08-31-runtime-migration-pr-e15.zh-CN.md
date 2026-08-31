# Handoff：Runtime Migration PR E15 —— TGT-07 / MOD-TGT07 construction contract

## 任务信息

- 任务编号：`task_20260831_runtime-migration-pr-e15`
- 分支：`task_20260831_runtime-migration-pr-e15`
- 基线：`origin/main` @ `bbfb1f1`（PR #132 merge `d65a5a7` = PR E14
  MOD-TGT06@1.0.0 三轮 APPROVE 收口 + PR #133 approval record `bbfb1f1` 之后）
- PR：待创建
- 时间：`2026-08-31`
- 授权：用户在 PR E14 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E15 冻结为 **TGT-07 / MOD-TGT07 Construction
  Contract, design-only**，并给了 **7 个 required tightening** + 逐条 E15-1…E15-8
  修正 + 3 条 headline conclusion。
- 变更定位：`CONTRACT_ADD`（设计冻结，与 E1 / E3 / E5 / E7 / E9 / E11 / E13
  同型）。只交 17 项施工合同 + human-readable drawing + parity / validation
  tests + 17 项验收清单 + manifest + handoff + worklog append；**不含任何实现**。
  Module 在 PR E16 才开工，且必须在本合同 APPROVE 之后。
  `primary_module_version` 保持 `0.0.0`；binding / registry / README /
  built-roster test 一律不动（唯一既有文件改动是 append `logs/worklog.md`）；
  `MIGRATION_PENDING` 保持（TGT-07 是**第八也是最后一个** primary Module —— PR
  E16 才解除 `MIGRATION_PENDING`）。

## 一、7 个 required tightening（审核方 closing summary，逐字冻结在合同）

1. **Option A** —— positive `INDIRECT_STRONG` 传播成 `POSITIVE / INDIRECT_STRONG`；
   legal Direction × Strength pair 恰好 **6 个**；无 `NEGATIVE / INDIRECT_STRONG`。
2. **below-detection / below-quantitation-limit soluble-antigen quantitation 是
   `CONTEXTUAL`** —— 既不是 positive `INDIRECT_STRONG` 也不是 `NEGATIVE`；新增
   CLOSED `circulating_soluble_target_status` typed enum
   （`QUANTIFIED_PRESENT` / `BELOW_DETECTION_OR_QUANTITATION_LIMIT` /
   `MIXED_OR_UNRESOLVED` / `NOT_ESTABLISHED`）承载它。
3. **canonical `NEGATIVE / DIRECT` 只由 qualified
   `SOLUBLE_ANTIGEN_TMDD_ANALYSIS` + `exposure_scenario_class ==
   INTENDED_ADC_EXPOSURE` + `sink_materiality_outcome ==
   NO_MATERIAL_SOLUBLE_SINK` 产生**；"某 same-target therapeutic 没看到 sink"
   永远不能直接产出 `NEGATIVE / DIRECT`。
4. **fatal 不用 TGT-06 式 Route A / Route B convergence** —— 一个 qualifying
   DIRECT observation（`sink_materiality_outcome ==
   MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`）满足 clinical
   source path **或** TMDD source path 即触发 `POTENTIAL_FATAL_PATTERN`；
   clinical / TMDD 是两条**可选 source path**，不是两条 convergence route；
   clinical path 自带 per-observation `reproducibility_status == QUALIFIED`
   gate（**不是** independent-replication / cross-study convergence 要求），此外
   无额外 reproducibility 要求；**无 global cancellation precondition**
   （fatal signal 是 `POSITIVE / DIRECT` 的严格子集，`POSITIVE / DIRECT`
   不取消 fatal trigger）。
5. **引入轻量单串 `sink_exposure_context_id`**（配 `sink_exposure_context_basis`），
   仅 qualifying DIRECT observation 必填；same-context material-vs-no-material
   才 `CONFLICTING`；**无 TGT-06 `declared_multi` / `IDENTIFIED_MULTI` /
   第三态机制，无 set-projection helper**（TGT-07 无 convergence 语义，不需要）。
6. **TMDD / clinical DIRECT 与 fatal authority 由 typed status 承载** ——
   `tmdd_input_adequacy_status`、`same_target_therapeutic_match_status`、
   `soluble_antigen_attribution_status`、`analysis_validation_status`、
   `exposure_scenario_class` —— E16 **永不** semantic-parse prose 来取得 DIRECT
   或 fatal authority。
7. **`SolubleAntigenEvidenceCompletion` 恰好 4 个 search-completion 轴**
   （`soluble_antigen_quantitation_search_complete` /
   `sheddase_processing_search_complete` /
   `secreted_isoform_search_complete` /
   `same_target_pk_pd_or_tmdd_search_complete`），**无**
   `qualifying_indirect_evidence_context_ids` set；
   `soluble_antigen_quantitation_search_complete` 为真当且仅当 CRC-patient 与
   healthy-donor 两个 serum / plasma search subspace 都完成；第 4 轴明确覆盖
   clinical PK / PD 和 target-mediated-disposition analyses。

## 二、E15-1…E15-8 scoping 决策（逐字见 manifest `scoping_decisions`）

- **E15-1 Scope / files（批准）**：文件名
  `tgt07_shedding_soluble_antigen_sink_liability.yaml` /
  `TGT-07_Shedding_Soluble_Antigen_Sink_Liability.md` /
  `test_tgt07_module_construction_contract.py`。canonical Gate 名
  "Shedding / Soluble-Antigen / Sink Liability"。`MIGRATION_PENDING` 保持
  （八个 Module 全建完才解除；TGT-07 是最后一个，PR E16 解除）。main 当前 built
  7 个（TGT-01/02/03/04/05/06/08）。
- **E15-2 Template / parity（批准）**：items 03/05/07/08 normalized-equality
  parity vs 冻结 PR D TGT-07；item 04 EXACT set-equality。**确认：frozen PR D
  TGT-07 无 `inference_guard` 字段** —— EVGAP-01 是 TGT-04 专属，TGT-07 无等价
  external guard，Module 不得自造。
- **E15-3 Direction × Strength（Option A + truth table）**：见 tightening 1/2/3
  与合同 item 06 `tgt07_specific_aggregation_truth_table`。**Existence-proof
  dominance** —— 一个 CLEAN material-sink DIRECT sink-exposure context 压过另一
  context 的 no-material-sink DIRECT（后者作 `CONTEXTUAL`）。**Different
  sink-exposure contexts 表现不同 ≠ CONFLICTING**（HARD lock）。**No
  cross-observation synthesis of DIRECT** —— quantitation EP + 另一个 model EP
  不合成 DIRECT，即使同一 target；DIRECT 必须来自 ONE upstream-qualified
  INTEGRATED observation。`sink_materiality_direction_mapping`：
  `MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE` /
  `MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE` →
  SUPPORTS_SINK_LIABILITY；`NO_MATERIAL_SOLUBLE_SINK` → OPPOSES_SINK_LIABILITY
  （仅 qualified intended-ADC TMDD，否则 CONTEXTUAL）；`MIXED_OR_UNRESOLVED` /
  `NOT_ESTABLISHED` → CONTEXTUAL。
- **E15-4 Fatal review（一个 predicate + 两条 source path）**：见 tightening 4。
  无 global precondition；一个 qualifying DIRECT observation（`sink_materiality_outcome
  == MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`）满足
  clinical source path（`CLINICAL_ANTIGEN_SINK_PK_EFFECT` +
  `same_target_therapeutic_match_status == QUALIFIED` +
  `same_target_therapeutic_ref` + `soluble_antigen_attribution_status ==
  QUALIFIED` + `analysis_validation_status == QUALIFIED` +
  `reproducibility_status == QUALIFIED` + documented clinically achievable
  exposure compromise）**或** TMDD source path（`SOLUBLE_ANTIGEN_TMDD_ANALYSIS`
  + `tmdd_input_adequacy_status == QUALIFIED` + `analysis_validation_status ==
  QUALIFIED` + `analysis_method != ""` + `exposure_scenario_class ==
  INTENDED_ADC_EXPOSURE` + 模型明确得出 material clinically achievable exposure
  compromise）即可。status 单值 `POTENTIAL_FATAL_PATTERN`；仅 accepted run
  actionable；机器永不 `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / fatal flag / KILL /
  HOLD / Decision；不在 proposal envelope 上。
- **E15-5 SolubleAntigenEvidenceCompletion（名称批准，第 4 轴改名）**：见
  tightening 7。umbrella `public_soluble_antigen_search_complete == all(four)`；
  矛盾 → HARD。**只有一个** qualifying context set ——
  `qualifying_direct_evidence_context_ids`（单串 `sink_exposure_context_id` 的并集；
  **没有** `qualifying_indirect_evidence_context_ids`）。completion ↔
  `SEARCH_COMPLETION_AUDIT` snapshot parity（E6/E8/E10/E14 gene）。
- **E15-6 Source-plan hard locks（批准 + 3 extra）**：predicted cleavage site →
  WEAK；family analogy → WEAK；quantified CRC-patient circulating soluble target
  （无 TMDD analysis）→ INDIRECT_STRONG ceiling；documented sheddase-substrate
  status / validated secreted isoform → INDIRECT_STRONG。**Extra hard lock 1**
  —— below-detection / below-quantitation-limit measurement 是 factual
  CONTEXTUAL。**Extra hard lock 2** —— 无 reported PK sink 的 same-target
  therapeutic **不**自动成 DIRECT NEGATIVE。**Extra hard lock 3** ——
  `NO_MATERIAL_SOLUBLE_SINK` 只有从 qualified intended-ADC TMDD 才是 canonical
  NEGATIVE authority。cross-gate —— TGT-01..TGT-06 / TGT-08 各 ≠ TGT-07；
  soluble-antigen sink ≠ efficacy / dose recommendation。
- **E15-7 Stop rule + EXPERIMENT_REQUIRED（方向批准）**：precedence
  0(HARD)→1(incomplete → INCONCLUSIVE/UNKNOWN, zero refs)→2(complete 但 audit
  invalid → HARD)→3(complete+audited → 按 item-06 truth table)。Option A 后区分
  4 个 completed state：(A) IS-only → `POSITIVE / INDIRECT_STRONG`（public 空间
  exhausted 时加 `EXPERIMENT_REQUIRED`）；(B) WEAK / below-assay-limit / no
  qualifying evidence → `INCONCLUSIVE / UNKNOWN`, zero refs（exhausted 时加
  `EXPERIMENT_REQUIRED`）；(C) DIRECT-quality `MIXED_OR_UNRESOLVED` analysis →
  `INCONCLUSIVE / DIRECT`，DIRECT EP 作 CONTEXTUAL；(D) 尚有 unresolved public
  path → `PUBLIC_RESOLVABLE` / `CURRENTLY_UNRESOLVABLE`，**不**自动加
  `EXPERIMENT_REQUIRED`。
- **E15-8 Items 10–17 runtime genes + E16 conceptual shape**：8 observation
  kinds（`CLINICAL_ANTIGEN_SINK_PK_EFFECT` / `SOLUBLE_ANTIGEN_TMDD_ANALYSIS` /
  `SOLUBLE_ANTIGEN_QUANTITATION` / `SHEDDASE_SUBSTRATE_STATUS` /
  `SECRETED_ISOFORM` / `PREDICTED_CLEAVAGE_SITE_INFERENCE` /
  `FAMILY_ANALOGY_SHEDDING_INFERENCE` / `SEARCH_COMPLETION_AUDIT`）；
  `sink_materiality_outcome` CLOSED enum（前两个 enum 名按审核方要求改精确 ——
  第二个是"material sink 已成立、clinical exposure compromise 尚未建立"）；新
  `circulating_soluble_target_status` / `tmdd_input_adequacy_status` /
  `same_target_therapeutic_match_status` / `soluble_antigen_attribution_status` /
  `exposure_scenario_class` typed status（各带 basis）；`cohort_class`
  {CRC_PATIENT_SERUM, HEALTHY_DONOR_SERUM, SAME_TARGET_THERAPEUTIC_PK,
  WELL_MATCHED_MODEL, NON_CRC_CONTEXT, UNRESOLVED}；轻量单串
  `sink_exposure_context_id`（DIRECT 必填，其它 `""`；无 declared_multi /
  第三态 / set-projection）；**无 raw-value 分支**（source-reported number 进
  neutral claim string，Module 永不比 threshold）；frozen proposal-relative
  EvidenceRole mapping（CONTRADICTING 仅 `CONFLICTING / DIRECT`）；item 13
  machine acceptance = executable checks，`proposed_strength == WEAK` HARD，
  HARD integrity failure 整轮 reject 不降级为 accepted UNKNOWN。

## 三、三条 headline conclusion（写在合同顶部，审核方原话）

1. A measurable soluble form is not the same thing as a material antigen sink.
   Quantified circulating soluble target, documented sheddase processing or a
   validated secreted isoform may support the presence of a soluble-antigen
   sink-liability class at INDIRECT_STRONG, but materiality requires DIRECT
   evidence from a documented same-target PK / PD sink effect or a qualified
   quantitative TMDD analysis; a concentration value, including a low or
   below-assay-limit value, is never converted by the Module into a universal
   material-sink threshold.
2. Soluble-antigen materiality is exposure-context dependent. DIRECT observations
   are bound to an auditable local sink-exposure context; one clean DIRECT
   material-sink context is sufficient for POSITIVE / DIRECT, while a canonical
   NEGATIVE / DIRECT requires a qualified intended-ADC TMDD analysis
   demonstrating no material soluble sink. Opposite DIRECT conclusions are
   CONFLICTING only when they refer to the same sink-exposure context; the
   machine has no conflict resolver in v1.
3. The TGT-07 potential-fatal signal is a strict subset of POSITIVE / DIRECT,
   not a convergence rule. One qualifying DIRECT observation may surface
   POTENTIAL_FATAL_PATTERN when soluble antigen is documented or quantitatively
   modelled to materially compromise the clinically achievable exposure of a
   target-directed antibody. Clinical and TMDD evidence are alternative qualified
   source paths; the machine never decides fatality, KILL, HOLD, therapeutic
   efficacy or the Candidate-level consequence.

## 四、交付物

- `src/contracts/gate_modules/tgt07_shedding_soluble_antigen_sink_liability.yaml`
  —— 17 项施工合同。
- `docs/gate_modules/TGT-07_Shedding_Soluble_Antigen_Sink_Liability.md`
  —— 17 行 drawing + 3 条 headline blockquote + normalized-observation /
  `SolubleAntigenEvidenceCompletion` conceptual shape。8 observation kinds：
  `CLINICAL_ANTIGEN_SINK_PK_EFFECT` / `SOLUBLE_ANTIGEN_TMDD_ANALYSIS` /
  `SOLUBLE_ANTIGEN_QUANTITATION` / `SHEDDASE_SUBSTRATE_STATUS` /
  `SECRETED_ISOFORM` / `PREDICTED_CLEAVAGE_SITE_INFERENCE` /
  `FAMILY_ANALOGY_SHEDDING_INFERENCE` / `SEARCH_COMPLETION_AUDIT`。
- `tests/test_tgt07_module_construction_contract.py` —— **78 tests**（11 类；
  checklist completeness + E1-template reuse；items 03/05/07/08
  normalized-equality parity + item 04 **exact set equality** derived parity +
  no-inference_guard confirmation；exposure-context / highest-qualifying-rung
  grading authority + 六个 legal pair + aggregation truth table +
  existence-proof dominance + no-cross-observation-synthesis-of-DIRECT；7 个
  required tightening 冻结 + E16 conceptual shape（8 observation kind、CLOSED
  `sink_materiality_outcome` + `circulating_soluble_target_status` enum）；
  fatal single-predicate / two-source-path —— 无 convergence、无 global
  cancellation precondition；source hard locks；E2/E4/E6/E8/E10/E12/E14 gene
  inheritance；no-implementation reconciliation —— 包 dir 不存在、binding 仍
  0.0.0、binding / registry / 既有 test 未动、只 append worklog；drawing 覆盖
  17 项）。
- `manifests/runtime_migration_pr_e15_manifest.yaml`、本 handoff。

## 五、验证

- `tests/test_tgt07_module_construction_contract.py` **78 OK**；全量
  **1791 OK**（PR E14 收口 1713）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项
  （`AI_RESULT_ACCEPTANCE.md`、`CRC Patient Territory Map.png`、
  `STELLIGEN_CONSTRAINTS.md`、`pipelines/`、`.claude/scheduled_tasks.lock`）。
- `git diff --check` clean；contract + manifest YAML 合法且无
  list-element-parsed-as-dict。
- `src/` 不 import `gate_modules/`。

## 六、状态与下一步

- 8 个 primary Module 施工合同已 APPROVE 7 个（TGT-01/05/08/02/03/04/06 + 本 PR
  待审）；已实现 7 个（TGT-01/02/03/04/05/06/08 @ 1.0.0）。MOD-TGT07
  `primary_module_version` 仍 `0.0.0`。`MIGRATION_PENDING` 保持。
- Next：开 PR、CI 绿后回 `AI审核方案` 贴 E15 review。APPROVE 后 PR E16 =
  MOD-TGT07@1.0.0 实现（第八也是最后一个 primary Module；PR E16 解除
  `MIGRATION_PENDING`），需各自 go-ahead。
