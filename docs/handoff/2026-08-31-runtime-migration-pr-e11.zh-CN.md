# Handoff：Runtime Migration PR E11 —— TGT-04 / MOD-TGT04 construction contract

## 任务信息

- 任务编号：`task_20260831_runtime-migration-pr-e11`
- 分支：`task_20260831_runtime-migration-pr-e11`
- 基线：`origin/main` @ `c9748b1`（PR #124 merge `551a938` = PR E10 MOD-TGT03@1.0.0
  两轮 APPROVE 收口 + PR #125 approval record `c9748b1` 之后）
- PR：待创建
- 时间：`2026-08-31`
- 授权：用户在 PR E10 收口后 "go ahead"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E11 冻结为 **TGT-04 / MOD-TGT04 Construction Contract,
  design-only**，并给了 **4 个关键修正**（前两个最重要）+ 3 条 headline conclusion。
- 变更定位：`CONTRACT_ADD`（设计冻结，与 E1 / E3 / E5 / E7 / E9 同型）。只交 17 项
  施工合同 + human-readable drawing + parity / validation tests + 17 项验收清单 +
  manifest + handoff + worklog append；**不含任何实现**。Module 在 PR E12 才开工，
  且必须在本合同 APPROVE 之后。`primary_module_version` 保持 `0.0.0`；binding /
  registry / README / built-roster test 一律不动（唯一既有文件改动是 append
  `logs/worklog.md`）；`MIGRATION_PENDING` 保持。

## 一、8 个 scoping 决策 + 4 个关键修正

见 `manifests/runtime_migration_pr_e11_manifest.yaml` 的 `scoping_decisions`
（E11-1…E11-8）与 `four_key_scoping_corrections`（逐字）。要点：

- **E11-1 Scope / files（批准）**：文件名
  `tgt04_tumor_surface_availability_density_plausibility.yaml` /
  `TGT-04_Tumor_Surface_Availability_Density_Plausibility.md` /
  `test_tgt04_module_construction_contract.py`。canonical Gate 名 "Tumor Surface
  Availability / Density Plausibility"。`MIGRATION_PENDING` 保持（八个 Module 全
  建完才解除；余下 TGT-04 → TGT-06 → TGT-07）。
- **E11-2 Template / parity（批准，无修正）**：items 03/05/07/08 normalized-equality
  parity vs 冻结 PR D TGT-04；item 04 EXACT set-equality；EVGAP-01 inference_guard
  逐字 pin。
- **E11-3 Direction × Strength**：
  - **修正 1（最重要）**：Localization-only 最终必须是 `INCONCLUSIVE / UNKNOWN`，
    **不能**是 `INCONCLUSIVE / INDIRECT_STRONG`。TGT-04 是 **two-tier evidence
    architecture**（LOCALIZATION: INDIRECT_STRONG membranous IHC / surfaceomics；
    DENSITY: DIRECT quantitative antigen density）但 **single-tier grading
    authority** —— 只有 qualifying DIRECT quantitative antigen-density observation
    在 completed audited landscape 上才 grant graded Direction。INDIRECT_STRONG 是
    observation-level rung / localization authority，**永不**传递成 Gate-level
    proposed Strength。E12 **不得**照抄 E10 的 "highest qualifying rung == overall
    Strength"。TGT-04 Strength rule（冻结）：`if qualifying DIRECT density evidence
    exists → overall Strength = DIRECT`；`else → INCONCLUSIVE / UNKNOWN, zero
    evidence_refs`。legal Direction × Strength pairs（冻结，恰好 5 个）：
    `POSITIVE/DIRECT`、`NEGATIVE/DIRECT`、`CONFLICTING/DIRECT`、
    `INCONCLUSIVE/DIRECT`、`INCONCLUSIVE/UNKNOWN`。无 INDIRECT_STRONG graded pair，
    无 INCONCLUSIVE/WEAK。`INCONCLUSIVE/DIRECT` 在有 qualifying quantitative
    density 但 `density_plausibility_status` 为 MIXED_OR_UNRESOLVED /
    NOT_ESTABLISHED 时合法。
  - **修正 2（最重要）**：**不要**用一个 status 同时表达 measurement validity 和
    density direction。三个 **分离的** typed upstream fact：
    `measurement_validation_status ∈ {QUALIFIED, NOT_ESTABLISHED}` + basis（该
    quantitative measurement 是否有资格进 DIRECT —— QUALIFIED **不是** positive
    density conclusion）；`density_plausibility_status ∈ {PLAUSIBLY_ADEQUATE,
    NOT_PLAUSIBLY_ADEQUATE, MIXED_OR_UNRESOLVED, NOT_ESTABLISHED}` + basis
    （upstream-qualified scientific interpretation，basis ∈ {SOURCE_REPORTED,
    HUMAN_REVIEWED_NORMALIZATION}，**永不**由 Module 根据数字算）；
    `surface_antigen_level ∈ {QUANTITATIVELY_PRESENT, LOW_BUT_PRESENT,
    NEGLIGIBLE_OR_UNDETECTABLE, MIXED_OR_UNRESOLVED, NOT_ESTABLISHED}` + basis
    （为 fatal path 单独冻结，使 `LOW_BUT_PRESENT` 永不被偷偷等同于
    `NOT_PLAUSIBLY_ADEQUATE`）。density direction mapping（对 qualifying DIRECT
    observation，按序）：`surface_antigen_level == NEGLIGIBLE_OR_UNDETECTABLE` →
    OPPOSES；else `density_plausibility_status == PLAUSIBLY_ADEQUATE` → SUPPORTS；
    `NOT_PLAUSIBLY_ADEQUATE` → OPPOSES；`MIXED_OR_UNRESOLVED / NOT_ESTABLISHED` →
    NONDIRECTIONAL / CONTEXTUAL。`LOW_BUT_PRESENT` alone → **不**自动 NEGATIVE，
    **不** fatal。`SURFACE_LOCALIZED` + qualifying IHC / surfaceomics → 一个
    INDIRECT_STRONG localization observation，永不贡献 Gate-level Direction /
    Strength；`NOT_SURFACE_LOCALIZED` alone → **不**产 NEGATIVE Gate Direction。
- **E11-4 Fatal review（Route A / Route B 批准）**：
  - **修正 3**：raw quantitative density value / unit **是** admissible factual
    evidence（`reported_density_value` / `reported_density_unit` /
    `reported_density_summary`）—— 禁止的是 Module 拿它们和 ANY threshold / cutoff
    / invented "clinically effective range" 比较。没有可靠的跨 target universal
    ADC-effective density range。
  - fatal contributor 必须：DIRECT-class quantitative cell-surface antigen
    density observation；CRC malignant cells OR QUALIFIED well-matched CRC model；
    explicitly qualified CRC surface context（`surface_context_class ∈
    {CRC_MALIGNANT_CELLS, WELL_MATCHED_CRC_MODEL}`）+ QUALIFIED
    `context_adequacy_status` + auditable basis；`measurement_validation_status
    == QUALIFIED` + auditable basis + 非空 factual `assay_method`；
    `surface_antigen_level == NEGLIGIBLE_OR_UNDETECTABLE`（**不是**
    `LOW_BUT_PRESENT`）+ auditable basis；completed + audited surface landscape。
  - **修正 4**：Route A（一个 auditable study 显式建立 negligible / undetectable
    结果的 reproducibility —— `reproducibility_status == QUALIFIED` + auditable
    `reproducibility_basis`；E12 **不得** semantic-parse basis 文字）OR Route B
    （convergent `NEGLIGIBLE_OR_UNDETECTABLE` 跨 **至少两个** independent qualified
    CRC `surface_context` identity —— local identity 名 `surface_context_id(s)`；
    deterministic SUFFICIENT convergence pattern，**不是** "reproducible" 的唯一
    词义，**不是** `> 2`）。status 单值 `POTENTIAL_FATAL_PATTERN`；只在 accepted
    run 上 actionable；机器永不 `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / fatal flag /
    KILL / HOLD / Decision；不在 proposal envelope 上。
- **E11-5 SurfaceAvailabilityCompletion（名称批准）**：module-local run record，
  **不是**第七个 core object。四个 mandatory search-completion axes
  （quantitative_surface_density / membranous_ihc / surface_proteomics /
  subcellular_localization —— 最后一个覆盖 topology / GO prediction / non-CRC /
  RNA proxy）—— **search-completion axes，不是 evidence prerequisites，不是
  grading axes**；searched / exhausted with zero qualifying records still counts
  complete。`public_surface_search_complete == all(four)`；矛盾 → HARD。completion
  ↔ SEARCH_COMPLETION_AUDIT snapshot parity（E6 / E8 / E10 gene），snapshot 字段
  名 == typed completion 字段名；只有 DIRECT quantitative density observation 产
  `qualifying_direct_surface_context_ids`（localization 无 qualifying context
  set）。
- **E11-6 Source-plan hard locks（批准）**：RNA / bulk → WEAK only, never surface
  protein, never density；localization（membranous IHC / surface proteomics）→
  INDIRECT_STRONG ceiling，never discharges quantitative antigen-density，never
  lifts Gate Strength above UNKNOWN；topology / GO prediction → WEAK；non-CRC
  surface evidence → WEAK；well-matched CRC MODEL quantitative density 可 DIRECT
  （只在 `surface_context_class == WELL_MATCHED_CRC_MODEL` + QUALIFIED context +
  auditable basis，永不凭 crc_specific alone）；EVGAP-01 = localization only；
  cross-gate —— TGT-02 coverage / TGT-03 persistence / TGT-06 internalization
  各不等于 TGT-04 surface / density。
- **E11-7 Stop rule + EXPERIMENT_REQUIRED（方向批准，与 E11-3 同步）**：precedence
  0(HARD)→1(incomplete → INCONCLUSIVE/UNKNOWN, zero refs)→2(complete 但 audit
  invalid → HARD)→3(complete+audited → **不是** highest-qualifying-rung，而是
  `if qualifying DIRECT exists: grade Direction/DIRECT; else: INCONCLUSIVE/UNKNOWN`)。
  localization-only completed landscape → INCONCLUSIVE/UNKNOWN, ZERO proposal
  evidence_refs, critical_unknown EXPERIMENT_REQUIRED（a quantitative
  cell-surface antigen density measurement）；EP 仍保留 localization facts 供
  human drilldown。unresolved item kind —— KNOWN_PUBLIC_NOT_YET_RESOLVED →
  PUBLIC_RESOLVABLE；ACCESS_OR_ANNOTATION_BLOCKED → CURRENTLY_UNRESOLVABLE。有
  unresolved public path 时 **不** auto-add EXPERIMENT_REQUIRED。
- **E11-8 Items 10-17 runtime genes（批准）+ 在 E11 冻结 E12 normalized
  observation conceptual shape**：observation kinds 8 种（见 drawing）；local
  context 用 `surface_context_id` / `surface_context_ids`（**非**裸 context_id），
  与 canonical `CTX-CRC-REFRACTORY-MCRC` 两套 namespace，qualifying DIRECT/IS 必须
  有 auditable `surface_context_id(s)`，local id == canonical → HARD；typed
  context qualification（`surface_context_class` / `context_adequacy_status` +
  basis，DIRECT/IS 不凭 crc_specific alone —— E10 round-1 gene）；typed
  `surface_localization_status`；`measurement_validation_status` closed enum +
  DIRECT 需非空 `assay_method`（assay vocabulary open）；所有 classification-driving
  qualified status 有 basis；Item 11 EP 继承 E8/E10 hardened genes + improved
  TGT-03 dedup（same source + same claim + different `surface_context_id` → 两个
  都保留；audit EP 永不 dedup loser；raw density number 可保留为 factual
  measurement，Module 永不 threshold calculation）；Item 12 non-canonical proposal
  envelope + separate fatal_review record；Item 13 machine acceptance —— Gate-level
  `proposed_strength` 为 DIRECT iff qualifying DIRECT quantitative observation
  存在，否则 UNKNOWN（`proposed_strength == INDIRECT_STRONG` 或 `WEAK` 是 HARD
  failure）；Item 17 —— HUMAN_APPROVED CandidateGateAssessment → MatrixView /
  ADC_TARGET_GATESET decision layer / TGT-06 as context only（TGT-04 never
  discharges TGT-06 internalization）+ module-local fatal_review → human Gate
  review / GateSet fatal policy。

## 二、三条 headline conclusion（写在合同顶部，审核方原话）

1. Surface localization is not antigen density. INDIRECT_STRONG localization
   evidence may establish that the antigen is on the membrane, but only
   quantitative DIRECT evidence can answer the TGT-04 density-plausibility
   question.
2. Quantitative values are evidence, not thresholds. MOD-TGT04 may preserve
   measured antigen-density values and units, but it never derives a universal
   ADC-effective density cutoff; density plausibility must arrive as an auditable
   upstream qualification.
3. Reproducible quantitative NEGLIGIBLE_OR_UNDETECTABLE surface antigen may
   surface only POTENTIAL_FATAL_PATTERN; low-but-present antigen is not
   automatically negative or fatal, and the Module never decides fatality or ADC
   efficacy.

## 三、交付物

- `src/contracts/gate_modules/tgt04_tumor_surface_availability_density_plausibility.yaml`
  —— 17 项施工合同。
- `docs/gate_modules/TGT-04_Tumor_Surface_Availability_Density_Plausibility.md`
  —— 17 行表 + 3 条 headline blockquote + normalized-observation /
  `SurfaceAvailabilityCompletion` conceptual shape。
- `tests/test_tgt04_module_construction_contract.py` —— **58 tests**（10 类；
  checklist completeness + E1-template reuse；items 03/05/07/08 normalized-equality
  parity + item 04 **exact set equality** derived parity + inference_guard
  verbatim；two-tier / single-tier grading authority + 五个 legal pair；4 个
  correction 冻结；fatal Route A / Route B + LOW_BUT_PRESENT never fatal；source
  hard locks；E2/E4/E6/E8/E10 gene inheritance 含五个 E10-review correction；
  no-implementation reconciliation —— 包 dir 不存在、binding 仍 0.0.0、
  binding / registry / 既有 test 未动、只 append worklog；drawing 覆盖 17 项）。
- `manifests/runtime_migration_pr_e11_manifest.yaml`、本 handoff。

## 四、验证

- `tests/test_tgt04_module_construction_contract.py` **58 OK**；全量
  **1437 OK**（PR E10 收口 1379）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项
  （`AI_RESULT_ACCEPTANCE.md`、`CRC Patient Territory Map.png`、
  `STELLIGEN_CONSTRAINTS.md`、`docs/worklogs/`、`pipelines/`）。
- `git diff --check` clean；contract + manifest YAML 合法且无
  list-element-parsed-as-dict。

## 五、状态与下一步

- 8 个 primary Module 施工合同已 APPROVE 6 个（TGT-01/05/08/02/03 + 本 PR 待审）；
  已实现 5 个（TGT-01/02/03/05/08 @ 1.0.0）。MOD-TGT04 `primary_module_version`
  仍 `0.0.0`。`MIGRATION_PENDING` 保持。
- Next：开 PR、CI 绿后回 `AI审核方案` 贴 E11 review。APPROVE 后 PR E12 =
  MOD-TGT04@1.0.0 实现，需各自 go-ahead。fatal-first 余下 TGT-06 → TGT-07。
