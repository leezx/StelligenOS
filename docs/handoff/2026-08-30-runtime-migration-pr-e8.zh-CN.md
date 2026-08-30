# Handoff：Runtime Migration PR E8 —— MOD-TGT02@1.0.0 实现

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e8`
- 分支：`task_20260829_runtime-migration-pr-e8`
- 基线：`origin/main` @ `76814c1`（PR #118 merge `9ec30e6` + PR #119 approval
  record `76814c1` 之后 —— PR E7 = TGT-02 施工合同 四轮 APPROVE 收口）
- PR：待创建
- 时间：`2026-08-30`
- 授权：用户在 PR E7 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed，带几处实现级修正**，把 E8 冻结为 **MOD-TGT02@1.0.0
  deterministic implementation**：「E7 已经把 TGT-02 的 science contract 冻得足够
  严，E8 不应再讨论 Gate science，只需要把它翻译成 deterministic runtime」，并给
  了 9 个 scoping 决策 E8-1…E8-8 + (a)(b)(c) + 3 条 headline invariant。审核方补
  的 3 个关键 implementation invariant（audit presence、completion consistency、
  assay typing）已全部落实。E8-6 正文里的「> 2 independent cohort identities」经
  追问确认是笔误，实现与测试均按冻结 E7 的 **AT LEAST TWO（>= 2，明确不是 "> 2"）**。
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-02 primary Evidence Production
  Module 的**确定性科学核心实现**，严格实现冻结的 E7 施工合同。`run()` 纯 Python，
  只调 injected port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID / 不接
  GEO·HPA·CPTAC·scRNA·spatial·TMA retrieval / 不做 ontology·embedding·LLM 推理 /
  不产 canonical Assessment 或 Decision / 不产 numeric·ranking score / 不产
  cohort-size·%-positive·H-score·heterogeneity cutoff / 不把 UNKNOWN 变
  PASS·HOLD·KILL / 不产 PUBLIC_FATAL_SIGNAL_ESTABLISHED。窄修 binding：TGT-02
  `primary_module_version` `0.0.0 → 1.0.0`。不改冻结的 E7 合同正文，不重构
  MOD-TGT01 / MOD-TGT05 / MOD-TGT08，不解除 `MIGRATION_PENDING`）。

## 一、9 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

E8-1…E8-8 + (a)(b)(c) 的逐条正文见
`manifests/runtime_migration_pr_e8_manifest.yaml` 的 `scoping_decisions`。要点：

- **E8-1** 完整确定性 Gate-specific core（同 E2 / E4 / E6），11 文件；`completion.py`
  与 `fatal_review.py` **各自独立小文件**（run-level search-completeness authority
  + audit parity；独立的 machine-local review trigger），不合进 `aggregate.py`。
  `CrcCohortCoverageCompletion` 是 frozen dataclass —— module-local run record，
  **非**第七个 core object。最小 binding 更新（TGT-02 `0.0.0 → 1.0.0`；
  `built_module_versions` / `BUILT_MODULE_VERSIONS` / `gate_modules/README.md` 加
  TGT-02 —— TGT-03 / 04 / 06 / 07 仍 `0.0.0`）。
- **E8-2** 一个 `Tgt02CoverageProviderPort`（本包自己声明
  `EvidenceIdAllocatorPort` / `SourceResolverPort` / `ExistingEvidenceLibraryPort`，
  **不 import** MOD-TGT01/05/08 的 ports）。`assay_method` 是 **typed
  classification-driving fact**（非自由文本）—— `DIRECT` 只能经
  `VALIDATED_IHC` / `QUANTITATIVE_PROTEOMICS` / `VALIDATED_MULTIPLEX_IF`；`cohort_n`
  只是 raw fact，绝不进 rung 逻辑。`SEARCH_COMPLETION_AUDIT` 另带 11 字段结构化
  completion snapshot。
- **E8-3** 确定性 rung 分类。`PROTEIN_COHORT` + `crc_specific` + `MALIGNANT` +
  validated protein assay + `QUALIFIED` cohort adequacy → `DIRECT`,
  `qualifying_for_direct`。sc / spatial malignant-compartment 或 CRC TMA
  transcript+protein concordance → `INDIRECT_STRONG`, `qualifying_for_indirect`
  （TMA concordance 即使 `molecular_layer=BOTH` 也严格 `INDIRECT_STRONG` —— PR D
  冻结）。bulk / pan-cancer → `WEAK`。matched normal-tumor / `NON_MALIGNANT` /
  unresolved-compartment / non-CRC → `CONTEXTUAL`，rung `""`（**非** HARD failure；
  stroma/immune 绝不成 malignant coverage，也不 discharge TGT-02）。hard locks：
  transcript 永不 `DIRECT`；generic / 非 validated protein assay 永不 `DIRECT`；
  protein without malignant attribution 永不 `DIRECT`；`cohort_n` 永不改 rung；
  matched normal-tumor 永不「normal low + tumor high → favorable TI」。**单个
  observation 永不是 Direction** —— classifier 只 rung-class 一个
  direction-SUPPORTING observation。
- **E8-4** 确定性 aggregation，显式 precedence：0. HARD integrity failure → 无
  proposal；1. completion 未 landscape-complete → `INCONCLUSIVE/UNKNOWN`，零
  evidence_refs（合法非错误态，E7 item 13/15）；2. completion complete 但 audit
  invalid/missing → HARD reject，绝不软 UNKNOWN；3. completion complete + audited
  → 评估 qualifying evidence。overall Strength = **最强 qualifying frozen
  evidence class**（`DIRECT` / else `INDIRECT_STRONG` / else `UNKNOWN`）—— **无**
  E6-style two-axis weaker-ceiling rule。Direction：valid audited multi-cohort
  `RARE_HIGHLY_HETEROGENEOUS`（>= 2 cohorts）→ `NEGATIVE`（**不** `CONFLICTING`，
  Strength 不自动降级）；else SUPPORTS + OPPOSES → `CONFLICTING`；else OPPOSES →
  `NEGATIVE`；else SUPPORTS → `POSITIVE`；else（qualifying 但 nondirectional）→
  graded `INCONCLUSIVE` / overall（严格 ≠ `INCONCLUSIVE/UNKNOWN`）。WEAK-only
  completed landscape → `INCONCLUSIVE/UNKNOWN`，**不是** `INCONCLUSIVE/WEAK`。
  「rare / highly heterogeneous」只从 `expression_pattern` +
  `expression_pattern_basis` 消费，Module 绝不计算；缺失 / drift 的 basis → HARD。
- **E8-5** 一个 module-local typed `CrcCohortCoverageCompletion`（`completion.py`
  的 frozen dataclass；字段按 E7-5；**非**第七个 core object）+ **3 个 HARD
  invariant**：(1) **completeness consistency** ——
  `public_crc_coverage_search_complete` 必须等于四个 declared mandatory component
  search 的 `all`；provider 声了 umbrella flag 而某 component 仍 false → 完整性
  矛盾，拒整个 run（绝不软 UNKNOWN）。(2) **audit presence + snapshot parity**
  —— 声了 `public_crc_coverage_search_complete` 的 completion 必须被 **恰好一条**
  `SEARCH_COMPLETION_AUDIT` observation 认证（`observation_id ==
  audit_observation_id`），其 11 字段结构化 snapshot 逐字段等于 typed
  completion；无 audit / 两条 audit / 任何 drift → HARD reject；snapshot 字段也
  进 audit EP exact-reuse parity。(3) **qualifying cohort-set parity** ——
  `qualifying_protein_cohort_ids` / `qualifying_indirect_cohort_ids` 必须（作 set）
  等于 Module 实际分类为 qualifying `DIRECT` / qualifying `INDIRECT_STRONG` 的
  observations 的 cohort identities（只在 completed landscape 上评估，因为
  「qualifying」只在那里有定义）；不一致 → HARD reject。`unresolved_items` 是小型
  typed `CoverageUnresolvedItem(description, kind)`，`kind` ∈
  {`KNOWN_PUBLIC_NOT_YET_RESOLVED`, `ACCESS_OR_ANNOTATION_BLOCKED`} —— internal
  type，非 core object。
- **E8-6** machine-local `fatal_review` review TRIGGER（`FatalReviewRecord`：
  `required` / `status` / `evidence_ids` / `cohort_ids` / `coverage_class` /
  `cohort_adequacy_basis_refs` / `expression_pattern_basis_refs` /
  `landscape_as_of` / `crc_coverage_search_scope`）。`status` 单值
  `POTENTIAL_FATAL_PATTERN`。detector 只消费已过 identity / provenance / rung /
  qualification basis / completion 的 observations。`required=true` 当且仅当，在
  **completed audited landscape** 上，有 DIRECT-class protein-cohort
  observations，每条分类 `OPPOSES_COVERAGE` + `expression_pattern` ∈ {`ABSENT`,
  `RARE_HIGHLY_HETEROGENEOUS`} + auditable `expression_pattern_basis` +
  `basis_detail`，且 `QUALIFIED` cohort adequacy + auditable basis，共同提供
  cross-cohort support —— **AT LEAST TWO independent cohort identities**（distinct
  auditable `cohort_ids`），或一个 declared multi-cohort analysis 带 at least two
  auditable `cohort_ids`。**是 >= 2，明确不是 "> 2" / ">= 3"**（审核方确认 E8-6
  草稿正文的「> 2」是笔误；冻结 E7 item-08
  `across_cohorts_is_plural_cohorts_logic_not_a_new_threshold` 为准）。单个
  negative cohort → `required=false`；同一 cohort 两条 observation 不算
  cross-cohort；transcript-only negative signal 永不贡献。**无** numeric /
  %-positive / H-score / heterogeneity 阈值。raw detector 可内部算，但 actionable
  handoff 只在 **accepted** run 上；machine 永不 `PUBLIC_FATAL_SIGNAL_ESTABLISHED`
  / canonical fatal flag / KILL / HOLD / Decision，也永不判定这个 pattern 是否是
  真的 fatal signal（human review + GateSet fatal policy 才判）。`fatal_review`
  **不在** proposal envelope 上。
- **E8-7** 每个 observation 一个 Gate-NEUTRAL EvidencePackage（PR A shape）+
  exact canonical reuse（同一对象、不调 allocator、不建 body；provenance 取
  resolved canonical SourceIndex；unresolved id 或 provider↔canonical metadata
  冲突 → HARD reject）。non-audit reuse parity keys = always 集合
  （`target_identity` / `context_key` / `landscape_as_of` / `observation_kind` /
  `molecular_layer` / **`assay_method`** / **`crc_specific`** /
  `malignant_cell_attribution` + basis / `cohort_adequacy_status` + basis /
  `expression_pattern` + basis + basis_detail）+ 该 kind 的 cohort key；audit EP
  再加 11 snapshot 字段；缺失 OR drift → HARD。machine acceptance = E7 item-13
  逐条可执行检查。HARD identity / provenance / completion-consistency /
  classification-qualification 失败 → 拒整个 run（`proposal_envelope = None`）
  —— **绝不**降级成 accepted UNKNOWN；genuinely incomplete public CRC coverage
  search 的 UNKNOWN **不是** integrity failure。`critical_unknowns` resolution ∈
  {`PUBLIC_RESOLVABLE`, `EXPERIMENT_REQUIRED`, `CURRENTLY_UNRESOLVABLE`}，**窄**
  确定性映射 —— incomplete public search → `PUBLIC_RESOLVABLE`；access /
  annotation-blocked unresolved item → `CURRENTLY_UNRESOLVABLE`；completed
  landscape 有 qualifying `INDIRECT_STRONG` directional 且无 qualifying `DIRECT`
  protein cohort → same Direction / `INDIRECT_STRONG` + `EXPERIMENT_REQUIRED`
  （protein-level malignant-cell cohort confirmation）；completed WEAK-only →
  `INCONCLUSIVE/UNKNOWN` + `EXPERIMENT_REQUIRED`。graded `INCONCLUSIVE/DIRECT`
  **不**发明 `EXPERIMENT_REQUIRED`（E7 未冻结）。Module 绝不构造
  `CandidateGateAssessment` / `HUMAN_APPROVED` / `Decision`。
- **E8-8** CI 只跑 synthetic / in-memory 场景 —— 无 internet、无真实 GEO / HPA /
  CPTAC / scRNA / spatial / TMA 数据。`TARGET_A` / `CRC_COHORT_A` / `_B` / `_C` /
  `STROMA` / `IMMUNE`；无 HER2 / TROP2 / 真实靶点名。
- **(a)** `completion.py` 与 `fatal_review.py` 各自独立小文件（同 E4/E6），不合进
  `aggregate.py`。
- **(b)** `module.yaml` 必须有，同 E2/E4/E6 型（identity / MOD-TGT02 / 1.0.0 /
  `runtime_migration_pr_e8` / construction contract / drawing / TGT-02 binding /
  `PUBLIC_HYBRID` / current `PUBLIC_ONLY` / ports / owns / does_not_own /
  boundary_flags），不发明新 manifest format。
- **(c)** E8 允许触碰的既有文件完整清单：`src/contracts/crc_adc_target_gateset.yaml`、
  `src/objects/crc_adc_target_gateset.py`、`gate_modules/README.md`、
  `tests/test_crc_adc_target_gateset.py`、`tests/test_gate_modules_boundary.py`、
  `tests/test_tgt02_module_construction_contract.py`（E7 test 迁成 post-E8
  reconciliation：合同仍冻结，实现包必须存在，binding 必须 1.0.0 —— 不是简单删
  测试）。另有 `tests/test_tgt05_module*.py` / `tests/test_tgt08_module*.py` 里
  hard-coded「只允许三个 built package」的 registry / built-list 假设，做**最窄**
  同步。**不改** TGT01/05/08 module files、E7 合同正文、E7 drawing science 正文、
  PR A/B/C、generic boundary scripts。

3 条 headline invariant（审核方原话）：

1. **A single observation is never a Direction.** 只有 `aggregate`，在一个
   completed audited CRC coverage landscape 上，才产 proposed Direction × Strength。
2. **TGT-02 NEGATIVE is a Gate-relative SCIENTIFIC coverage judgement** —— 它
   **绝不**是 fatal flag，**绝不**是 KILL。cross-cohort protein-level
   negative-coverage pattern 至多 surface 成 machine-local `fatal_review =
   POTENTIAL_FATAL_PATTERN`。
3. **The typed `CrcCohortCoverageCompletion` grants the Module its authority to
   grade a population-level Direction** —— 一个自相矛盾、无法被审计、或与
   qualifying evidence 不符的 completion 一文不值，拒整个 run。

## 二、边界一句话

- **MOD-TGT02 判读 refractory mCRC 恶性细胞对靶点的 protein-level、cohort-level
  coverage —— 它不判 target 的 scientific validity（那是 E7 合同冻结的科学），也
  不做 Candidate-level Decision / KILL。**
- **一个漂亮 cohort 不是 population-level 答案。只有 completed / audited CRC
  coverage search 才能把单个 observation 聚合成 cohort-level Gate judgement。**

## 三、文件

### 新增实现包 `gate_modules/tgt02_indication_specific_malignant_cell_coverage/`（11 文件）

| 文件 | 职责 |
|---|---|
| `__init__.py` | 公共导出（identity 常量、enums、dataclasses、`run`、ports） |
| `module.yaml` | 身份 / 版本 / gate binding / purpose / owns / does_not_own / ports / `boundary_flags`（全 false） |
| `completion.py` | `CoverageUnresolvedItem` + `CrcCohortCoverageCompletion` + `completeness_contradiction` / `audit_presence_failure` / `audit_snapshot_mismatch` / `qualifying_set_mismatch`（E8-5 三个 HARD invariant） |
| `contracts.py` | enums + tiny validators + `CanonicalSourceRecord` / `NormalizedCoverageObservation` / `ClassifiedCoverage` / `EmittedEvidence` / `FatalReviewRecord` / `Tgt02ModuleInput` / `AssessmentProposalEnvelope` / `MachineAcceptanceRecord` / `Tgt02ModuleRunResult` / `overall_strength` |
| `ports.py` | `Tgt02CoverageProviderPort` / `EvidenceIdAllocatorPort` / `SourceResolverPort` / `ExistingEvidenceLibraryPort`（Protocol） |
| `classify.py` | `classify_observation` —— 确定性 rung + coverage-support 映射（E8-3） |
| `evidence.py` | `build_evidence_packages` —— Gate-neutral EP 构造 + exact canonical reuse + parity（E8-7） |
| `aggregate.py` | `aggregate` —— 冻结 truth table，precedence，highest-qualifying Strength，heterogeneity precedence，窄 EXPERIMENT_REQUIRED（E8-4 / E8-7） |
| `fatal_review.py` | `detect` —— cross-cohort POTENTIAL_FATAL_PATTERN detector（>= 2 cohorts）（E8-6） |
| `acceptance.py` | `evaluate` —— E7 item-13 可执行检查 |
| `module.py` | `run` —— 纯 Python orchestration，只调 injected port |

### 窄修既有文件

- `src/contracts/crc_adc_target_gateset.yaml` —— TGT-02 binding `0.0.0 → 1.0.0`；
  `built_module_versions` 加 `TGT-02: "1.0.0"`；说明段 3→4 built。
- `src/objects/crc_adc_target_gateset.py` —— `BUILT_MODULE_VERSIONS` 加 TGT-02；
  注释加 PR E8。
- `gate_modules/README.md` —— 注册表加 `MOD-TGT02 … built (PR E8)`；「未建」计数
  5→4。
- `tests/test_crc_adc_target_gateset.py` —— `_BUILT_MODULE_VERSIONS` 加 TGT-02 +
  新 `test_tgt02_module_is_built_in_gate_modules`。
- `tests/test_gate_modules_boundary.py` —— `TGT02` path 常量 +
  `Tgt02ModuleManifestTests`。
- `tests/test_tgt02_module_construction_contract.py` —— `NoImplementationInPrE7Tests`
  迁成 `ContractIsFrozenAndImplementedInPrE8Tests`（合同仍冻结；实现包 11 文件
  必须存在；binding 现 `1.0.0`；`allowed` package list 加 tgt02）。
- `tests/test_tgt05_module.py` / `tests/test_tgt05_module_construction_contract.py`
  / `tests/test_tgt08_module.py` / `tests/test_tgt08_module_construction_contract.py`
  —— hard-coded「只三个 built package」的 built-list / allowed-list 最窄同步。

### 新增测试

- `tests/test_tgt02_module.py` —— 75 tests：BindingAndBoundary、InputContract、
  IdentityProvenanceIntegrity、ExactReuse、RungClassification、
  HardScientificBoundary、CompletionInvariant、AggregateTruthTable、
  Heterogeneity、FatalReview、CriticalUnknown、ForbiddenOutput。

## 四、验证

- `tests/test_tgt02_module.py` **75 OK**。
- 全量 `unittest discover`：**1185**（E7 收口时 1104；+75 tgt02_module + 其余
  reconciliation / registry 同步）。**全绿**。
- `bash scripts/verify_repository_boundary.sh` —— 只报既有 untracked 杂项
  （`pipelines/`、`STELLIGEN_CONSTRAINTS.md`、`CRC Patient Territory Map.png`、
  `AI_RESULT_ACCEPTANCE.md`），不属本 PR，干净 CI checkout 上不存在。
- `git diff --check` clean；两个 YAML（binding、E8 manifest）合法。

## 五、状态

8 个 primary Module 施工合同已 APPROVE 4 个（MOD-TGT01/05/08/02）；已实现 4 个
（MOD-TGT01@1.0.0 E2、MOD-TGT05@1.0.0 E4、MOD-TGT08@1.0.0 E6、MOD-TGT02@1.0.0
E8）。其余四个 gate（TGT-03 → TGT-04 → TGT-06 → TGT-07）属后续 PR，
`primary_module_version` 仍 `0.0.0`。`MIGRATION_PENDING` 保持。真实 retrieval
provider / adapter / dataset 与外部 workspace calibration 各自需 go-ahead。
下一步 PR E9 = MOD-TGT03 施工合同（design-only，需各自 go-ahead）。
