# ChatGPT 审核记录：Runtime Migration PR E16 —— MOD-TGT07@1.0.0 implementation + runtime-conformance closeout

- 日期：`2026-09-01`
- PR：#136 `task_20260901_runtime-migration-pr-e16`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求 / 逐轮回复贴入该对话）
- 被审核 HEAD：`798c734`（第一轮修订后）
- Merge 提交：`004dbed`（`Merge pull request #136 from leezx/task_20260901_runtime-migration-pr-e16`）
- 结论：**APPROVE @ `798c734`**。「APPROVE —— PR #136 可以 merge。至此 Runtime
  Migration PR A–E16 implementation sequence 完成；没有 PR E17。merge + 独立
  docs-only approval-record PR 收口后，`MIGRATION_PENDING` 正式解除，PR A–E16
  Blueprint-v1.3 Candidate × Gate × Evidence runtime-conformance migration 与
  八个 primary Module 的 migration 同时 COMPLETE；`migration.deferred` 不删除，
  其余 StelligenOS deferred work 另行推进。」GitHub connector 每轮均
  `403 Resource not accessible by integration`，REQUEST_CHANGES / APPROVE 的
  GitHub review state 未回写；`AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260901_runtime-migration-pr-e16-approval-record`）
中补登，按 PR #95 … #135 先例。本 PR 同时把
`manifests/runtime_migration_pr_e16_manifest.yaml` 补成 approved。不改 PR E16 的
实现代码、测试、handoff 或 binding。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e16_manifest.yaml` 的 `scoping_decisions`
（E16-1…E16-8）与 `seven_required_implementation_tightenings`（逐字），以及
`docs/handoff/2026-09-01-runtime-migration-pr-e16.zh-CN.md`。要点：

- E16 是 **IMPLEMENTATION PR**，与 E2 / E4 / E6 / E8 / E10 / E12 / E14 同型：
  交付 `gate_modules/tgt07_shedding_soluble_antigen_sink_liability/` 的 11 文件
  确定性核心 + `tests/test_tgt07_module.py` + 窄 binding / registry 对账 + runtime-
  conformance 收口。严格照冻结的 PR E15 施工合同实现，**不引入任何新的 science
  或 ladder 语义**。TGT-07 是第八个也是最后一个 primary Evidence Production
  Module —— **PR E16 解除 `MIGRATION_PENDING`**，宣告 PR A–E16 Candidate × Gate ×
  Evidence runtime-conformance migration 与八个 primary Module 的 migration
  COMPLETE；其余 deferred work（quantitative ladder calibration、epitope-layer
  分析、external evaluators、downstream Candidate levels、FTO）保留，
  `migration.deferred` 不删除（`per_gate_primary_modules` key 标记 completed /
  8-of-8）。
- **7 个 required implementation tightening**（审核方 pre-code ruling，逐字冻结在
  manifest 与代码）：
  1. **T1** —— DIRECT 资格判定 **kind-specific**，只在 `classify.py`，无 generic
     predicate。clinical DIRECT 需 `same_target_therapeutic_match_status` +
     `soluble_antigen_attribution_status` + `analysis_validation_status` 均
     `QUALIFIED`（含 basis / ref / method 非空）；TMDD DIRECT 需
     `tmdd_input_adequacy_status` + `analysis_validation_status` `QUALIFIED`。
  2. **T2** —— `MIXED_OR_UNRESOLVED` 是 DIRECT-quality **CONTEXTUAL** 分析
     （`evidence_rung` DIRECT，`qualifying_direct_mixed`）；`NOT_ESTABLISHED`
     永远不是 qualifying DIRECT-rung observation。
  3. **T3** —— `aggregate.py` / `fatal_review.py` **消费** classified 结果，永不
     重判 typed status；`aggregate.py` 直接写冻结的
     `tgt07_specific_aggregation_truth_table.frozen_evaluation_order`
     （step 0–7，stop-at-first-match），按单字符串 `sink_exposure_context_id`
     分组，无 projection helper，无 `IDENTIFIED_MULTI` / 第三态。
  4. **T4** —— completion 增加 `crc_patient_quantitation_subspace_search_complete`
     + `healthy_donor_quantitation_subspace_search_complete` typed facts；
     `soluble_antigen_quantitation_search_complete` **==** 两者严格 AND；
     `SEARCH_COMPLETION_AUDIT` snapshot 以 exact parity 携带两者。
  5. **T5** —— `fatal_review.py` 只做 fatal-specific narrowing：一个 predicate
     + 两条备选 source path（clinical / intended-ADC TMDD）；**无**
     reproducibility 前提；**无** global cancellation 前提；
     `MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE`
     的 DIRECT 是 `POSITIVE / DIRECT` 但 NONFATAL。`module.py` 顺序：
     raw-candidate → acceptance → surface（仅 accepted run）。
     *（round-1 blocker 1 后：typed `sink_materiality_outcome` 是唯一
     machine authority，`documents_clinical_exposure_compromise` 第二 boolean
     已删除 —— 见下 Round 1。）*
  6. **T6** —— `claim` / `sink_exposure_context_id` / basis 字符串 reuse / dedup
     parity 用 **精确**字符串等值（无 `.strip()` / 小写 / 空白规范化）；
     duplicate-`observation_id` preflight 在**任何** injected-port 调用前 HARD
     短路；无 raw-value parity 分支；无 `float()` / `Decimal()` / `int()`。
  7. **T7** —— 收官 machine invariant regression：八个 `built_module_versions`
     key `{TGT-01..TGT-08}` 均 `"1.0.0"`，每个 `gate_binding.primary_module_version`
     均 `"1.0.0"`，八个 primary-module package manifest 均存在且 identity 匹配
     —— 只有此时 live architecture docs 才允许停止写 `MIGRATION_PENDING`。

## 审核往返（2 轮）

### Round 1 —— REQUEST_CHANGES @ `ef9109c`

被审核 HEAD `ef9109c`；exact-head CI run 33506279674 —— verify (3.11) +
verify (3.12) 均 success。

审核方确认主体实现成立、**不要重开**：kind-specific DIRECT classifier；
MIXED vs NOT_ESTABLISHED；冻结的 7-step aggregate；EvidenceRole mapping；
dual-subspace completion；无 `qualifying_indirect_evidence_context_ids` set；
exact audit parity；无 reproducibility fatal gate；无 fatal global cancellation
precondition；raw-candidate → acceptance → surfaced fatal；exact reuse / dedup；
duplicate-`observation_id` preflight；无 raw-value 分支；`treatment_state ==
not_applicable`；TGT-07 binding `1.0.0`；8/8 built machine invariant；其余
deferred work 保留；historical snapshots 未动；`crc_adc_target_gateset.yaml`
的 `migration.deferred` 处理。

**3 个窄 blocker：**

1. **`documents_clinical_exposure_compromise` 是第二 fatal authority** —— 与
   CLOSED typed `sink_materiality_outcome ==
   MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`（按 T5 本身即
   "documented / modelled clinically achievable exposure compromise" 的唯一
   machine authority）并列。非法态：`outcome == WITH_COMPROMISE` +
   `bool == false` → classifier 判 DIRECT / SUPPORTS，而 fatal detector
   `required == false`。**FIX**：从 `contracts.py`（字段 + `_bool(...)` 校验）、
   `evidence.py`（`_KEYS_ALWAYS` reuse / dedup parity）、`fatal_review.py`
   （`_fatal_source_path` 的 `if not o.documents_clinical_exposure_compromise:
   return ""`）、`acceptance.py`（fatal-contributor check 的
   `and e.observation.documents_clinical_exposure_compromise`）、`module.yaml`
   （`purpose` / `owns` / provider port role 提及）、tests（`_clinical` /
   `_tmdd` / `_obs` helper 的 `compromise` 参数）全部删除。fatal narrowing 现在
   只按 typed outcome + `observation_kind`（TMDD 路径再 +
   `exposure_scenario_class == INTENDED_ADC_EXPOSURE`）。新 regression
   `test_the_typed_outcome_alone_is_the_fatal_authority_no_second_boolean`：
   断言该字段已不在 dataclass 上，且 qualified clinical DIRECT +
   `WITH_CLINICAL_EXPOSURE_COMPROMISE` → fatal true（无第二 flag）。

2. **`acceptance.py` 误把携带真实 `sink_exposure_context_id` 的 CONTEXTUAL
   CLINICAL / TMDD observation 整轮 reject** —— 把「没达到 DIRECT」错当成
   「非法输入」。E15 只要求：qualifying DIRECT → context REQUIRED；
   INDIRECT_STRONG / WEAK / SEARCH_COMPLETION_AUDIT → `""`。**FIX**：
   `ctx_on_wrong_rung`（键于 `not e.classified.is_qualifying_direct`）改为
   `ctx_on_wrong_kind`（键于 `e.observation.observation_kind not in
   _DIRECT_AUTHORITY_KINDS`），check 改名
   `only_a_direct_authority_kind_carries_a_sink_exposure_context`；constructor
   已强制非 DIRECT-authority kind 不得携带 context，此处 belt-and-suspenders。
   `missing_ctx` / `canon_collision` 两条 check 不变。新 class
   `ContextualDirectAuthorityObservationTests`（4 tests）：contextual
   clinical / TMDD + factual sink context 是 accepted run、not DIRECT、not
   fatal；INDIRECT_STRONG 携带 sink context 仍 constructor `ValueError`。

3. **`docs/architecture/contract.zh-CN.md` §3.4.3 同时说「runtime implementation
   未变 / migration pending」和「Runtime conformance: COMPLETE」** —— 现时态
   自相矛盾。**FIX（只改 live 文档 —— 冻结的 v5 expert-review 文档与 historical
   snapshots 未动）**：「它已变，但 runtime implementation 未变。」→「它已变，且
   PR A–E16 runtime layer 已完成（见下 Runtime conformance）。」；legacy
   contracts block 降格为「Retained legacy-compatibility snapshots (frozen
   legacy -- compatibility references, NOT the current runtime):」；「`ADC Lead`
   / `Clinical Regimen` 是 `core_objects@1.1` 尚缺、migration 时须新增的
   Candidate Type」→「... 未登记、**仍属 deferred downstream work** ... 不属于
   PR A–E16 runtime migration 的范围」；同节 B 组 blocker →「PR A–E16 runtime
   blockers 已关闭（PR A–E16 已合并），剩余 deferred work 另行推进」；§6
   Source of Truth「核心对象清单（当前实现登记，待 crosswalk）」→「核心对象清单
   （legacy-compatibility snapshot / crosswalk reference）」。
   `MigrationCloseoutInvariantTests.test_migration_pending_is_lifted_in_the_live_docs`
   扩展：断言 `README.md` 含 "runtime conformance = **COMPLETE**"、
   `contract.zh-CN.md` 含 "COMPLETE for the Blueprint-v1.3 Candidate x Gate x
   Evidence runtime migration"，并 assertNotIn「但 runtime implementation 未变」
   /「runtime conformance:\n  MIGRATION_PENDING」/「尚缺、migration 时须新增」。

修订：`contracts.py` / `fatal_review.py` / `evidence.py` / `acceptance.py` /
`module.yaml`、`docs/architecture/contract.zh-CN.md`、
`tests/test_tgt07_module.py`（91 → 96）、`tests/test_gate_modules_boundary.py`、
`manifests/runtime_migration_pr_e16_manifest.yaml`（`review_round_1` block +
`chatgpt_review: REQUEST_CHANGES` + `review_rounds: 1` +
`test_count_after_round_1: 1900`）、`logs/worklog.md` append。本地全量 unittest
1895 → 1900 OK（+5 regression）。提交 `798c734`。CI（exact-head run 33509346532）
—— verify (3.11) + verify (3.12) 均 success。

### Round 2 —— APPROVE @ `798c734`

被审核 HEAD `798c734`；exact-head CI run 33509346532 —— verify (3.11) +
verify (3.12) 均 completed / success（Unit tests、Repository boundary、
working-tree cleanliness 步骤均含）。审核方确认 round-1 三个 blocker **全部
关闭**：

- **Blocker 1（fatal authority）CLOSED** —— `documents_clinical_exposure_compromise`
  已从 observation contract 删除；`fatal_review.py` 现在只消费 classifier 已
  确认的 qualifying material-sink DIRECT，再按唯一 CLOSED
  `sink_materiality_outcome == MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`
  + clinical / intended-ADC TMDD source path 做 fatal-specific narrowing；
  没有第二 boolean、没有 claim / basis semantic parse、没有 reproducibility
  gate、没有 global cancellation；该字段在 observation dataclass 与 acceptance
  的 fatal-contributor 复核中都确实不存在。
- **Blocker 2（contextual CLINICAL / TMDD exposure context）CLOSED** ——
  acceptance 现在正确区分「observation kind 是否有资格携带 local exposure
  context」与「该 observation 最终是否达到 DIRECT」；CONTEXTUAL 的 clinical /
  TMDD observation 可以保留真实 context，不再整轮 reject。
- **Blocker 3（live architecture contract）CLOSED** —— 不再同时说「runtime
  implementation 未变」和「runtime COMPLETE」；legacy contracts 明确降格为
  retained compatibility snapshots；A–E16 runtime blockers 标记关闭；未覆盖的
  Candidate Types 正确归入 deferred downstream work；Source-of-Truth 的
  `core_objects.yaml` 改为 legacy-compatibility / crosswalk reference；
  closeout regression 现在同时覆盖 top README、architecture、contract，并禁止
  三个旧的 active-state stale phrase。

其它观察：round-1 → round-2 修订只有一个 commit，改动集中在上述修复对应的
约 10 个文件；`classify.py` / `aggregate.py` / `completion.py` / GateSet
binding science 及其它已 CLOSED 模块逻辑未重新触碰；`module.yaml` 当前 fatal
ownership 与最终 authority 一致（classifier 单一 scientific qualification
authority，fatal detector 只做 narrowing）。无新的 implementation blocker；
此前 CLOSED 的 T1–T7、EvidenceRole mapping、completion / audit、reuse / dedup、
duplicate-`observation_id` preflight、8/8 migration invariant 均保持成立。

非阻断 housekeeping（merge 前已处理）：GitHub PR #136 description 仍显示旧的
`91 OK` / `1895 OK`，而当前实际是 `96` / `1900`；merge 前顺手更新了 PR body，
不影响 APPROVE。

两轮状态：Round 1 —— 3 narrow blockers → 全部 CLOSED；Round 2 —— 无新 blocker。

**结论：APPROVE —— PR #136 可以 merge。至此 Runtime Migration PR A–E16
implementation sequence 完成；没有 PR E17。**

## Merge

- PR #136 于 `2026-09-01` 以 `--merge` 合入 `main`，merge 提交 `004dbed`。
- 独立 docs-only PR `task_20260901_runtime-migration-pr-e16-approval-record`
  补登：本审核记录（2 轮完整往返 + merge）+
  `manifests/runtime_migration_pr_e16_manifest.yaml` →
  `status: approved` / `chatgpt_review: APPROVE` / `approved_tip: 798c734…` /
  `merge_commit: 004dbed` / `review_rounds: 2` / `test_count_at_approval: 1900` /
  `approval_record_pr` / `review_round_2` block。不改 PR E16 的实现代码、测试、
  handoff 或 binding。
- 状态：**八个 primary Module 施工合同全部 APPROVE（TGT-01…TGT-08），且八个
  primary Module 全部实现 @ `1.0.0`（TGT-01/02/03/04/05/06/07/08）**；每个
  `gate_binding.primary_module_version == "1.0.0"`；**`MIGRATION_PENDING` 已
  解除** —— PR A–E16 Blueprint-v1.3 Candidate × Gate × Evidence runtime-
  conformance migration 与八个 primary Module 的 migration 均 COMPLETE。
  `migration.deferred` 未删除 —— 其余 StelligenOS deferred work（quantitative
  ladder calibration、epitope-layer 分析、external evaluators、downstream
  Candidate levels、FTO）保留。
- Next：**无。** PR E16 是 PR A–E16 runtime migration 的最后一个 implementation
  PR，没有 PR E17。任何进一步的 deferred work 需另行 explicit go-ahead。
