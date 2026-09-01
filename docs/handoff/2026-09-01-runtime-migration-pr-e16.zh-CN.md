# Handoff：Runtime Migration PR E16 —— MOD-TGT07@1.0.0 实现 + runtime conformance 收口

## 任务信息

- 任务编号 / 分支：`task_20260901_runtime-migration-pr-e16`
- 基线：`origin/main` @ `a706a47`（PR E15 approval-record PR #135 merge）
- PR：待创建
- 授权：用户 "go on" + ChatGPT `AI审核方案` 开工前 scoping **APPROVE-to-proceed**，
  把 E16 冻结为「MOD-TGT07@1.0.0 deterministic implementation + runtime
  conformance closeout」，含 E16-1…E16-8 修正与 **7 个 required implementation
  tightenings**。
- 变更定位：**RUNTIME_IMPL_ADD + MIGRATION_CLOSEOUT**，与 E2 / E4 / E6 / E8 /
  E10 / E12 / E14 同型的 implementation PR，外加 runtime-conformance 收口。
  `run()` 纯 Python，只调 injected port；包内无 network / subprocess / repo
  write / id self-increment / retrieval / normalizer / numeric coercion /
  free-text basis parsing / UNKNOWN→PASS·HOLD·KILL / `PUBLIC_FATAL_SIGNAL_ESTABLISHED`；
  窄 binding bump `0.0.0 → 1.0.0`；不改冻结的 PR E15 施工合同 / drawing、
  MOD-TGT01…TGT06 / TGT08、PR A/B/C 合同、PR D TGT-07 science。
  **TGT-07 是第八也是最后一个 primary Module —— 本 PR 解除 `MIGRATION_PENDING`。**

## 一、E16-1…E16-8 scoping + 7 个 required tightening

见 `manifests/runtime_migration_pr_e16_manifest.yaml` 的 `scoping_decisions`
（E16-1…E16-8）、`seven_required_implementation_tightenings`（逐字）与
`frozen_proposal_relative_evidence_role_mapping`。要点：

- **E16-1** 11 文件 `gate_modules/tgt07_shedding_soluble_antigen_sink_liability/`；
  `SolubleAntigenEvidenceCompletion` 是 module-local run record，非第七个 core
  object；`acceptance.py` 执行 E15 item-13 executable checks，**不是** 17-item
  YAML parser（runtime 永不解析 `src/contracts/gate_modules/tgt07...yaml` 自然
  语言）。`MIGRATION_PENDING` 在本 PR 解除，但收口**只**宣告 PR A–E16
  Candidate × Gate × Evidence runtime-conformance migration 与 8-primary-Module
  migration 完成；其它 deferred work 仍在，`migration.deferred` 不删除
  （`per_gate_primary_modules` 标记为 completed / 8-of-8 built）。
- **T1** DIRECT qualification 按 observation kind 分开，classify.py 是唯一 scientific
  qualification authority（clinical：same-target match + soluble-antigen
  attribution + analysis validation 均 QUALIFIED；TMDD：TMDD input adequacy +
  analysis validation QUALIFIED）；无 generic predicate。
- **T2** `MIXED_OR_UNRESOLVED` → DIRECT-rung CONTEXTUAL；`NOT_ESTABLISHED` 永不
  是 qualifying DIRECT-rung observation。
- **T3** `aggregate.py` / `fatal_review.py` 消费已 classified 结果，永不重判
  typed status；aggregate 直接写死 frozen_evaluation_order，grouping 只在单字符串
  `sink_exposure_context_id` 上（无 projection helper / 第三态）。
- **T4** completion 加 `crc_patient_quantitation_subspace_search_complete` +
  `healthy_donor_quantitation_subspace_search_complete` 两个 typed fact；
  `soluble_antigen_quantitation_search_complete == strict AND`；
  `SEARCH_COMPLETION_AUDIT` snapshot 逐字段 parity 携带这两个 fact。
- **T5** `fatal_review.py` 只做 fatal-specific narrowing；one predicate + two
  alternative source paths（clinical / intended-ADC TMDD）；无强制
  reproducibility predicate；无 global cancellation precondition；
  `MATERIAL_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE` DIRECT 是
  POSITIVE / DIRECT 但 NONFATAL。`module.py` 顺序 raw-candidate → acceptance →
  surface（仅 accepted run）。
- **T6** claim / `sink_exposure_context_id` / basis 用 EXACT string equality
  做 reuse / dedup parity（无 `.strip()` / lowercase / whitespace normalize）；
  duplicate `observation_id` preflight 在所有 side-effect / injected-port call
  之前 HARD short-circuit。
- **T7** 最终 machine closeout invariant regression：8 个 built_module_versions
  key `{TGT-01…TGT-08}` 均 `1.0.0`、每个 gate_binding `primary_module_version`
  均 `1.0.0`、8 个 package manifest 存在且 module_id / version / gate_id 匹配 ——
  否则 migration-complete 失败。

## 二、frozen_evaluation_order（aggregate.py 直接硬编码，stop-at-first-match）

0. not completed / audit-invalid → item-16 stop rule；1. 按 `sink_exposure_context_id`
group qualifying DIRECT；2. ≥1 CLEAN material-sink DIRECT context → POSITIVE /
DIRECT（existence-proof dominance）；3. 同一 context 同时带 material-sink DIRECT
与 no-material-sink DIRECT → CONFLICTING / DIRECT（v1 无 conflict resolver）；
4. ≥1 qualifying intended-ADC no-material-sink TMDD 且无 material-sink DIRECT →
NEGATIVE / DIRECT；5. ≥1 DIRECT-quality MIXED_OR_UNRESOLVED 且无 material-sink /
canonical no-material-sink DIRECT → INCONCLUSIVE / DIRECT（该 DIRECT EP
CONTEXTUAL）；6. 无 DIRECT-rung 但 ≥1 qualifying positive INDIRECT_STRONG →
POSITIVE / INDIRECT_STRONG；7. else → INCONCLUSIVE / UNKNOWN（zero refs）。
6 legal Direction × Strength pair；不同 sink-exposure context 表现不同**永不**
CONFLICTING。

## 三、fatal_review（fatal_review.py）

completed + audited landscape 上，一个 classified qualifying DIRECT observation
`sink_materiality_outcome == MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`
且 `documents_clinical_exposure_compromise`，满足 clinical source path
（`observation_kind == CLINICAL_ANTIGEN_SINK_PK_EFFECT`）**或** TMDD source path
（`observation_kind == SOLUBLE_ANTIGEN_TMDD_ANALYSIS` +
`exposure_scenario_class == INTENDED_ADC_EXPOSURE`）→ `required = True`，
`status = POTENTIAL_FATAL_PATTERN`。ONE observation on EITHER path 即够；无
convergence pair、无 reproducibility predicate、无 global cancellation
precondition。机器只出 `POTENTIAL_FATAL_PATTERN`，只在 accepted run actionable，
不是 proposal envelope 字段。

## 四、binding / registry 窄修 + runtime conformance 收口（E16-8）

- `src/contracts/crc_adc_target_gateset.yaml`：TGT-07 `primary_module_version`
  `"0.0.0" → "1.0.0"` + 「Built in Runtime Migration PR E16」注释；
  `primary_module_binding.rule` 措辞（8/8 built）；`built_module_versions` 加
  `TGT-07: "1.0.0"`；`migration.deferred.per_gate_primary_modules` 改为
  completed / 8-of-8 built（key 保留）。
- `src/objects/crc_adc_target_gateset.py`：`BUILT_MODULE_VERSIONS` 加
  `"TGT-07": "1.0.0"` + docstring。
- `gate_modules/README.md`：Module 注册表加 MOD-TGT07 行；`MIGRATION_PENDING`
  段 → 「Runtime conformance: **COMPLETE** for the Blueprint-v1.3 Candidate ×
  Gate × Evidence runtime migration (PR A–E16)」。
- `README.md` / `architecture.md` / `docs/architecture/contract.zh-CN.md`：live
  `MIGRATION_PENDING` → runtime conformance COMPLETE（历史 version snapshot /
  archived approval record 不动）。
- 测试：`tests/test_gate_modules_boundary.py` 加 `Tgt07ModuleManifestTests` +
  `MigrationCloseoutInvariantTests` + `TGT07` path const；
  `tests/test_crc_adc_target_gateset.py` `_BUILT_MODULE_VERSIONS` +
  `TgtGateContractTests` 翻转（TGT-07 now built）；`test_tgt02…08_module.py` /
  `test_tgt02…08_module_construction_contract.py` 的 built-roster / allowed-package
  tuple 最窄同步（TGT-07 now built）；`test_tgt07_module_construction_contract.py`
  `ContractIsFrozenAndDeferredToPrE16Tests` → `ContractIsFrozenAndImplementedInPrE16Tests`，
  翻转 package-exists / binding-1.0.0 / migration 断言，其余 11 个 content class
  全部 contract / science regression 保留。未触碰 PR A/B/C 合同、PR D TGT-07
  science、E15 施工合同正文、其它 Module 的 package。

## 五、测试

- `tests/test_tgt07_module.py` = 91 synthetic in-memory tests（binding + boundary
  + migration closeout；classify T1/T2 kind-specific DIRECT；direction mapping；
  frozen_evaluation_order 6 legal pair；completion T4 dual subspace + audit
  parity；fatal_review T5；evidence T6 reuse / dedup / exact-string / no
  raw-value branch；duplicate observation_id preflight；hard integrity；output
  surface）。
- 全量 `python3 -B -m unittest discover -s tests -p 'test_*.py'` = **1895 OK**
  （PR E15 收口 1796；+91 test_tgt07_module +8 test_gate_modules_boundary）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项；
  `git diff --check` clean；YAML 合法；`src/` 不 import `gate_modules/`。

## 六、状态与下一步

- **8 个 primary Module 施工合同全部 APPROVE、8 个全部实现**
  （TGT-01…TGT-08 @ `1.0.0`）。`MIGRATION_PENDING` **已解除**；runtime
  conformance = COMPLETE for the PR A–E16 Candidate × Gate × Evidence migration。
- Next：开 PR、CI（python 3.11 + 3.12 matrix）绿后回 ChatGPT `AI审核方案` 贴
  implementation-level review 请求；APPROVE 后 merge + 建独立 docs-only
  approval-record PR（review log + manifest → approved）+ 收口 worklog。
  **本 PR 是这一轮 runtime migration 的最后一个 implementation PR，没有 PR E17。**
  其它 deferred work（quantitative ladder calibration、epitope-layer 分析、
  external evaluators、下游 Candidate level、FTO 任务）属后续、独立授权。
