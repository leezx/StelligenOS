# Handoff：Runtime Migration PR E12 —— MOD-TGT04@1.0.0 实现

## 任务信息

- 任务编号 / 分支：`task_20260831_runtime-migration-pr-e12`
- 基线：`origin/main` @ `be72c15`（PR #126 merge `499cf3a` = PR E11 TGT-04 施工合同
  三轮 APPROVE 收口 + PR #127 approval record `be72c15` 之后）
- PR：待创建
- 时间：`2026-08-31`
- 授权：用户在 PR E11 收口后 "go ahead"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E12 冻结为 **MOD-TGT04@1.0.0 deterministic
  implementation**：「E12-1…E12-8 总体可以直接开工。它与已冻结 E11 contract 一致。
  我建议再冻结 4 个 required implementation tightenings，它们都不修改 E11 science，
  只是让 E12 deterministic core 不留解释空间。」
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-04 primary Evidence Production Module
  的确定性科学核心实现，严格实现冻结的 PR E11 施工合同）。`run()` 纯 Python，
  只调 injected port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID / 不接
  absolute-quantitation flow·QIFIKIT·mass-cytometry·surfaceomics·membranous-IHC·
  cell-surface-proteomics·subcellular-localization retrieval / **包内不建
  normalizer** / **不对 raw density value 做 numeric coercion / unit conversion**
  / 不做 ontology·embedding·LLM 推理 / 不产 canonical Assessment 或 Decision /
  不产 numeric·ranking score / 不产 antigen-density·molecules-per-cell·ABC·
  %-positive·H-score cutoff / 不发明 ADC-effective density range / 不解析
  `reproducibility_basis` 自由文本 / 不把 UNKNOWN 变 PASS·HOLD·KILL / 不产
  PUBLIC_FATAL_SIGNAL_ESTABLISHED。窄修 binding：TGT-04
  `primary_module_version` `0.0.0 → 1.0.0`。不改冻结的 E11 合同正文，不重构
  MOD-TGT01 / MOD-TGT02 / MOD-TGT03 / MOD-TGT05 / MOD-TGT08，不解除
  `MIGRATION_PENDING`（8 个 primary Module 建成 6 个）。

## 一、8 个 scoping 决策 + 4 个 required tightening

见 `manifests/runtime_migration_pr_e12_manifest.yaml` 的 `scoping_decisions`
（E12-1…E12-8）与 `four_required_implementation_tightenings`（逐字）。要点：

- **E12-1 包结构**：11 文件（`__init__` / `module.yaml` / `contracts` / `ports`
  / `classify` / `evidence` / `aggregate` / `completion` / `fatal_review` /
  `acceptance` / `module`）。`completion.py` 与 `fatal_review.py` 各自独立小文件。
  `SurfaceAvailabilityCompletion` 是 module-local run record，**不是**第七个 core
  object。`acceptance.py` 执行 E11 item 13/10/11/12/16 的可执行检查并禁止 item-17
  跨 Gate / Decision 输出。
- **E12-2 Provider surface**：一个 `Tgt04SurfaceAvailabilityProviderPort`，包自己
  声明其余三个 port。Provider 只出 **normalized upstream facts**：8 个
  `observation_kind`；`assay_method` OPEN，`measurement_validation_status` CLOSED
  `{QUALIFIED, NOT_ESTABLISHED}`；`surface_context_class` /
  `context_adequacy_status` / `malignant_cell_attribution` /
  `surface_localization_status` / `density_plausibility_status`（+ typed basis
  `{SOURCE_REPORTED, HUMAN_REVIEWED_NORMALIZATION}`）/ `surface_antigen_level` /
  `reproducibility_status`，各 + basis；LOCAL `surface_context_id(s)` +
  `declared_multi_context_analysis`；OPAQUE raw `reported_density_value` /
  `_unit` / `_summary`（空串 = absent）。basis hygiene 按 E10 规则（QUALIFIED /
  MALIGNANT / 已断言的 localization·density·antigen-level·QUALIFIED reproducibility
  都要 basis；sentinel NOT_ESTABLISHED / UNRESOLVED 可无 basis，除非 provider 实际
  断言了 factual interpretation；在 NOT_ESTABLISHED 上出现非空 basis 是 drift）。
  Provider 永不出 rung / direction / density-implication / fatal trigger。
- **E12-3 rung 分类**（`classify.py`，含 tightening 1）：
  - **DIRECT** —— `QUANTITATIVE_SURFACE_DENSITY` + PROTEIN 层 +
    `measurement_validation_status == QUALIFIED` + basis + 非空 `assay_method`
    + `surface_context_class ∈ {CRC_MALIGNANT_CELLS, WELL_MATCHED_CRC_MODEL}` +
    `context_adequacy_status == QUALIFIED` + `surface_context_basis` +
    `context_adequacy_basis` + `malignant_cell_attribution == MALIGNANT` + basis。
    另加 factual-coherence HARD guard：CRC / well-matched-model `surface_context_class`
    要求 `crc_specific == true`（`crc_specific` 本身永不赋 rung）。
  - **INDIRECT_STRONG** —— `MEMBRANOUS_IHC` / `SURFACE_PROTEOMICS` +
    `surface_context_class == CRC_MALIGNANT_CELLS` **only**（永不 model）+
    `context_adequacy_status == QUALIFIED` + basis + `malignant_cell_attribution
    == MALIGNANT` + basis + `surface_localization_status == SURFACE_LOCALIZED`。
    well-matched model 的 localization 观测 → CONTEXTUAL，永不成 IS rung。
  - **WEAK** —— `SUBCELLULAR_LOCALIZATION` / `TOPOLOGY_OR_GO_PREDICTION` /
    `NON_CRC_SURFACE_EVIDENCE` / `RNA_SURFACE_PROXY`，即使带很漂亮的 non-CRC 线
    membranous IHC 也不上升；`RNA_SURFACE_PROXY` 永不成 surface-protein /
    surface-density claim。
  - **density_direction_mapping**（只对 qualifying DIRECT，按序）：
    `NEGLIGIBLE_OR_UNDETECTABLE → OPPOSES`；else `PLAUSIBLY_ADEQUATE → SUPPORTS`；
    `NOT_PLAUSIBLY_ADEQUATE → OPPOSES`；`MIXED_OR_UNRESOLVED / NOT_ESTABLISHED →
    CONTEXTUAL`。qualifying INDIRECT_STRONG 观测 = CONTEXTUAL，永不带 directional
    density_implication。`LOW_BUT_PRESENT` 单独不决定方向。
- **E12-4 aggregate —— TWO-TIER / SINGLE-TIER grading authority**（TGT-04 runtime
  的核心，**直接写死**，不写 generic highest-rung aggregator）：
  precedence 0/1/2/3；complete + audited 时 —— **没有 qualifying DIRECT →
  INCONCLUSIVE / UNKNOWN，零 evidence_refs**（100 个 qualifying INDIRECT_STRONG +
  0 DIRECT 仍然 INCONCLUSIVE / UNKNOWN，localization 永不把 Strength 抬过 UNKNOWN）；
  有 qualifying DIRECT → overall Strength = DIRECT，**只在 qualifying DIRECT 集合上**
  按 density_direction_mapping 定方向：material SUPPORTS + material OPPOSES 无
  resolver → CONFLICTING / DIRECT，除非有一个 qualifying DIRECT 观测满足
  `declared_multi_context_analysis == true` AND `density_plausibility_status ==
  MIXED_OR_UNRESOLVED` AND auditable `density_plausibility_basis` AND
  `surface_context_ids` 覆盖所有 material SUPPORTING / OPPOSING context → INCONCLUSIVE
  / DIRECT（tightening 2 —— `NOT_ESTABLISHED` 不是 resolver；不 semantic-parse
  prose）。legal pairs 恰好 5：`POSITIVE/DIRECT`、`NEGATIVE/DIRECT`、
  `CONFLICTING/DIRECT`、`INCONCLUSIVE/DIRECT`、`INCONCLUSIVE/UNKNOWN`。
  well-matched model DIRECT quantitative 观测和 CRC malignant-cell 一样能驱动
  ordinary Direction，但永不进 fatal_review。
- **E12-5 typed `SurfaceAvailabilityCompletion`**（frozen dataclass；3 个 HARD
  invariant）：completeness consistency（umbrella == all(四个 FLAT boolean)）；
  audit presence + snapshot parity（exactly one `SEARCH_COMPLETION_AUDIT` +
  exactly one provenance-bearing audit EP；snapshot 字段名 == typed completion
  字段名；含 `qualifying_direct_surface_context_ids` /
  `qualifying_indirect_surface_context_ids` 两组）；qualifying-set parity（只在
  completed landscape 上作最终权威；indirect set 只是 audit-integrity，不授予
  grading authority）。tightening 3 —— `attempted == False` 是冻结的严格空状态。
- **E12-6 fatal_review**（`fatal_review.py`，消费已分类证据）：eligible contributor
  = `evidence_rung == DIRECT` AND `density_implication == OPPOSES_DENSITY_PLAUSIBILITY`
  AND `surface_antigen_level == NEGLIGIBLE_OR_UNDETECTABLE` AND
  `surface_context_class == CRC_MALIGNANT_CELLS`（`WELL_MATCHED_CRC_MODEL`
  **明确不 eligible**）。detector 不重判 assay_method / measurement validation /
  context adequacy / malignant attribution（classifier authority）。Route A =
  `reproducibility_status == QUALIFIED` + 非空 basis（basis 文本永不解析）；
  Route B = 跨 `>= 2` independent qualified CRC **malignant-cell** surface-context
  identity（非 `> 2` 非 `>= 3`；1 CRC + 1 model、2 model 都不满足）。status 至多
  `POTENTIAL_FATAL_PATTERN`；只在 accepted run 上 actionable；永不产 canonical
  fatal flag / KILL / HOLD / Decision。不在 proposal envelope 上。
- **E12-7 EvidencePackage + reuse + dedup**：Gate-neutral PR A EP；exact canonical
  reuse（无 allocator call，parity drift HARD）；分类驱动 parity key 含
  `observation_id` + 全部 typed fact + basis + LOCAL `surface_context_id(s)`；对
  `QUANTITATIVE_SURFACE_DENSITY` 观测，raw `reported_density_value` / `_unit` /
  `_summary` 是 **对称 presence-and-value parity key**（任一侧单独存在、或值 / 单位
  / summary 不同 → HARD；两侧相同或两侧都无 → compatible）。dedup 用改进的 TGT-03
  规则（非 blind `(source_id, claim)`）；`observation_id` 是权威身份，重复
  `observation_id` 在 semantic dedup **之前**就 HARD reject；distinct
  `surface_context_id` 的观测都保留；audit EP 永不 dedup loser。HARD identity /
  provenance / completion-consistency / classification-qualification failure →
  整轮 reject（`proposal_envelope = None`），永不降级为 accepted UNKNOWN；
  genuinely incomplete public search → INCONCLUSIVE / UNKNOWN 不是 integrity
  failure。narrow EXPERIMENT_REQUIRED（有未解 public item 时不加；public 穷尽 +
  localization-only / WEAK-only 完成 → 加）。
- **E12-8 proposal envelope + binding reconciliation**：non-canonical
  `AssessmentProposalEnvelope`（canonical identity pin，含 `context_id`
  `CTX-CRC-REFRACTORY-MCRC`；无 `assessment_id` / `assessment_version` / `review`
  / fatal flag / Decision / density threshold）。binding reconciliation 最小集：
  `src/contracts/crc_adc_target_gateset.yaml` + `src/objects/crc_adc_target_gateset.py`
  （TGT-04 `0.0.0 → 1.0.0`；`built_module_versions` / `BUILT_MODULE_VERSIONS`
  加 TGT-04）、`gate_modules/README.md`（注册 MOD-TGT04）、
  `tests/test_crc_adc_target_gateset.py`（sample gate → TGT-06）、
  `tests/test_gate_modules_boundary.py`（`Tgt04ModuleManifestTests`）、
  `tests/test_tgt02/03/05/08_module*.py`（最窄 built-roster 同步）、
  `tests/test_tgt04_module_construction_contract.py`
  （`NoImplementationInPrE11Tests` → `ContractIsFrozenAndImplementedInPrE12Tests`，
  保留全部 contract / science regression）。`MIGRATION_PENDING` 保持。

## 二、交付物

- `gate_modules/tgt04_tumor_surface_availability_density_plausibility/` —— 11 文件。
- `tests/test_tgt04_module.py` —— 71 个合成 in-memory 测试。
- binding / registry 协调 6 文件（见上）+ `Tgt04ModuleManifestTests` 5 个。
- `manifests/runtime_migration_pr_e12_manifest.yaml`、本 handoff、`logs/worklog.md` append。

## 三、验证

- `tests/test_tgt04_module.py` **71 OK**；`tests/test_tgt04_module_construction_contract.py`
  **71 OK**（`NoImplementationInPrE11Tests` 已迁移）；全量 **1526 OK**（E11 收口 1450）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项；
  `git diff --check` clean；YAML 合法且无 list-element-parsed-as-dict。
- `src/` 不 import `gate_modules/`；包内无 `float(reported_density_*)` /
  `Decimal(...)` / `int(...)`。

## 四、状态

8 个 primary Module 施工合同已 APPROVE 6 个（TGT-01/02/03/04/05/08），已实现
**6 个**（+ MOD-TGT04@1.0.0）。TGT-06 `primary_module_version` 仍 `0.0.0`。
`MIGRATION_PENDING` 保持。下一步 PR = MOD-TGT06，需各自 go-ahead。

## 五、下一步

开 PR、CI 绿后回 ChatGPT `AI审核方案` 贴 E12 review 请求。
