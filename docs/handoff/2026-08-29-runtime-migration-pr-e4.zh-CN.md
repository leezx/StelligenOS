# Handoff：Runtime Migration PR E4 —— MOD-TGT05@1.0.0 实现

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e4`
- 分支：`task_20260829_runtime-migration-pr-e4`
- 基线：`origin/main`（PR #110 merge + PR #111 approval record 之后，PR E3 收口 @ `14ac39f`）
- PR：待创建
- 时间：`2026-08-29`
- 授权：用户在 PR E3 APPROVE 后追加 "go ahead and"；开工前审核方（ChatGPT
  `AI审核方案`）拍板 **PR E4 = MOD-TGT05@1.0.0 deterministic implementation**，
  「像 E2 一样成为完整的 Gate-specific scientific core，但不接 live provider、不写
  外部 workspace、不做 calibration」，并给了 8 个 scoping 决策 E4-1…E4-8。
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-05 primary Evidence Production
  Module 的**确定性科学核心实现**，严格实现冻结的 E3 施工合同。只调用 injected
  port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID / 不做 ontology·embedding·
  LLM 推理 / 不产 canonical Assessment 或 Decision / 不产 numeric score / 不产
  product-specific therapeutic-window 结论。窄修 binding：TGT-05
  `primary_module_version` `0.0.0 → 1.0.0`。不改冻结的 E3 合同正文，不重构
  MOD-TGT01，不解除 `MIGRATION_PENDING`）。

## 一、8 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

| # | 决策 |
|---|---|
| E4-1 | 真实确定性 MOD-TGT05 实现（同 E2 是完整 Gate-specific scientific core）。文件 `__init__` / `module.yaml` / `contracts` / `ports` / `classify` / `evidence` / `aggregate` / `fatal_review` / `acceptance` / `module`；`module_version 1.0.0`；最小 binding 更新（TGT-05 `primary_module_version` `0.0.0 → 1.0.0`，`built_module_versions` 加 TGT-05）；冻结的 E3 合同正文一字不改；**不建** generic GateModule framework / abstract base class；**不重构** MOD-TGT01。 |
| E4-2 | 一个 normalized `Tgt05LiabilityProviderPort`；每条 record 带 `evidence_function` ∈ {`LIABILITY_RUNG_EVIDENCE` (A)、`ATTRIBUTION_ADJUDICATION` (B)、`COVERAGE_CONTEXT` (C)}；`NormalizedLiabilityRecord` 只装事实（observation_id、liability_event_id、target_identity、observation_kind、claim、provenance，加可选 species / modality / molecular_layer / finding / atlas_validated / vital_organ_class / affected_tissue / program_id / construct_fingerprint / toxicity_phenotype_key / observed_severity / target_attribution_stance+basis / translational_relevance）；provider 永不返回 rung 或 direction；N/A 用显式空值，不用省略。 |
| E4-3 | classification 逐字实现 E3 item-06 truth table —— **validated human protein atlas NOT_DETECTED → `COVERAGE_CONTEXT`**（不是 WEAK，不是 NEGATIVE）；scRNA / RNA-only → WEAK；rodent-only → WEAK；aggregation：undisputed DIRECT → `POSITIVE/DIRECT`，否则 undisputed INDIRECT_STRONG → `POSITIVE/INDIRECT_STRONG`，否则 WEAK-only → `INCONCLUSIVE/WEAK`，否则 `INCONCLUSIVE/UNKNOWN`；已确立的 DIRECT/INDIRECT_STRONG liability + coverage gap → 仍 `POSITIVE`（gap 进 `critical_unknowns`）；**永不 `NEGATIVE`/safe**。 |
| E4-4 | `CONFLICTING` 只按 `liability_event_id` —— disputed event = 一个 admissible source SUPPORTS + 另一个 admissible source REFUTES 同一 event id，且该 event 本身不是 undisputed established liability；若没有其它独立的 undisputed DIRECT/INDIRECT_STRONG liability → `CONFLICTING`，Strength = 该 disputed observation 能达到的最强 rung；若存在独立 established liability → 整体 `POSITIVE`，dispute 进 `critical_unknowns`；「ADC-A 有毒、ADC-B 报告没毒」既不是 conflict 也不产 `CONTRADICTING` ref。 |
| E4-5 | `fatal_review` 是独立的 machine-local run 输出；`status` 单值 `POTENTIAL_FATAL_PATTERN`（无 `FATAL_REVIEW_REQUIRED` status —— `required=true` 表达它）；`required=true` 当且仅当 ≥2 个不同 `program_id` 的同靶点 ADC clinical toxicity observation，每个都有 `construct_fingerprint` + disclosed `target_attribution_basis` + `SUPPORTS_TARGET_ATTRIBUTION` + **EXACT** normalized `affected_tissue` key 匹配 + **EXACT** `toxicity_phenotype_key` 匹配；无 embeddings / LLM / ontology / fuzzy；同一 program 的两篇文献 = 一个 program；「materially distinct」/「truly target-mediated」/「biologically meaningful convergence」是 human-review 判断。 |
| E4-6 | `Tgt05SweepCompletionRecord` = 5 个 sweep 布尔 + per-vital-organ `{search_complete, coverage_result ∈ (ADMISSIBLE_PROTEIN_DATA_FOUND, PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA, NOT_YET_COMPLETE)}`（CNS/CARDIAC/HEPATIC/PULMONARY/HEMATOPOIETIC/GASTROINTESTINAL）。Path A（`fatal_review.required` → provisional stop；更弱的 atlas/RNA sweep 不是前置，但同靶点 ADC construct inventory + attribution sweep 仍必须完成）；Path B（存在一个 DIRECT ADC clinical liability 且 `fatal_review.required==false` → 要求 construct inventory + attribution sweep）；Path C（无 DIRECT ADC clinical liability → 要求 non-ADC + NHP + RNA-supporting + 六个 vital-organ protein coverage 搜索全部完成；exhausted organ → `critical_unknown` = `EXPERIMENT_REQUIRED`）。 |
| E4-7 | EvidencePackage 是 Gate-neutral + exact canonical reuse（已在 Evidence Library 的 observation 复用**同一对象** —— 不调 allocator、不建新 body）；negative-atlas observation **也是**一个 EvidencePackage，其 `does_not_support` 显式列「the absence of a normal-tissue on-target liability」/「normal-tissue safety」/「a product-specific therapeutic window」；reuse parity 覆盖**该 observation kind 的**classification-driving 字段（缺失 OR drift → HARD reject）；SourceIndex authority 完全同 E2（未注册 id 或 provider↔canonical metadata 冲突 → HARD reject）。 |
| E4-8 | CI 只跑 synthetic / in-memory 验收场景 —— 无 internet、无真实 atlas / clinical 数据，synthetic `TARGET_A` / `PROGRAM_A` / `PROGRAM_B` / `LIVER`（`HEPATIC`）/ `PHENO_X`。 |

一句话（审核方原话）：**TGT-05 的「negative data」主要是 coverage information，
不是 safety evidence；`fatal_review` 是一个 machine-generated review trigger，
不是 machine-generated fatal conclusion。**

## 二、边界一句话

- **PR E4 owns**：normalized TGT-05 observations → source / identity QC →
  frozen evidence-class mapping → Gate-neutral EvidencePackages →
  per-vital-organ coverage state → Direction × Strength（frozen truth table）→
  machine-local `fatal_review` review trigger → path-based stop-rule acceptance
  → non-canonical assessment proposal envelope。
- **PR E4 does NOT own**：web / atlas / clinical retrieval；RNA·atlas
  normalisation + phenotype keying + attribution-stance 赋值；source registry /
  provenance ledger；dataset persistence；ontology / LLM 推断 toxicity
  convergence；human target-attribution adjudication；human materially-distinct
  判断；the fatal decision；CandidateGateAssessment approval；GateSet Decision /
  KILL；therapeutic-window prediction。

## 三、交付物

| 文件 | 说明 |
|---|---|
| `gate_modules/tgt05_normal_tissue_fatal_liability/contracts.py`（新） | frozen dataclass 输入/输出契约：`MODULE_ID=MOD-TGT05` / `MODULE_VERSION=1.0.0` / `GATE_ID=TGT-05`；`TGT05_EVIDENCE_CEILING` / `TGT05_GATE_QUESTION` 逐字 PR D；枚举 `EVIDENCE_FUNCTION_VALUES` / `OBSERVATION_KIND_VALUES` / `MOLECULAR_LAYER_VALUES` / `FINDING_VALUES` / `TARGET_ATTRIBUTION_STANCE_VALUES` / `VITAL_ORGAN_CLASSES`（六器官）/ `COVERAGE_RESULT_VALUES` / `FATAL_REVIEW_STATUS_VALUES`（`""` \| `POTENTIAL_FATAL_PATTERN`）；`CanonicalSourceRecord`、`NormalizedLiabilityRecord`（跨字段按 observation kind 校验；`COVERAGE_CONTEXT` 必须是 validated human PROTEIN atlas NOT_DETECTED；一批 factual 谓词）、`Tgt05ModuleInput`（`target_identity` 唯一权威；`evidence_regime == PUBLIC_ONLY`；`identity_pins`）、`ClassifiedLiability`（`rejection_severity` `""`/`HARD`/`SOFT`；`establishes_rung`）、`EmittedEvidence`、`VitalOrganCoverageState`、`Tgt05SweepCompletionRecord`（`path_b_sweeps_complete` / `path_c_sweeps_complete`）、`CoverageMapRecord`、`FatalReviewRecord`（`required` iff `status==POTENTIAL_FATAL_PATTERN`；`required` 时 `len(set(program_ids))>=2`；`none()`）、`AssessmentProposalEnvelope`（8 个 identity pin + `proposed_direction`/`proposed_strength`/`evidence_refs`/`aggregation_rationale`/`critical_unknowns`/`evidence_ceiling`；`NEGATIVE` 直接 raise；`evidence_ceiling` 必须逐字 == `TGT05_EVIDENCE_CEILING`；不带 `assessment_id`/`assessment_version`/`review`，不带 fatal flag）、`MachineAcceptanceRecord`、`Tgt05ModuleRunResult`（hard failure → 无 proposal + not accepted；reused id 不得也作为新 body）。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/ports.py`（新） | `Tgt05LiabilityProviderPort`（`fetch_liability_records` + `sweep_completion`）、`EvidenceIdAllocatorPort`、`SourceResolverPort`（→ `CanonicalSourceRecord \| None`）、`ExistingEvidenceLibraryPort`（→ `EvidencePackage \| None`，复用同一对象）。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/classify.py`（新） | `classify_record(record, *, canonical_target_identity)` → `ClassifiedLiability`。步骤：(1) `not primary_source_resolved` → SOFT；(2) target 身份不匹配 → HARD misbinding；(3) `COVERAGE_CONTEXT` → admit（`covered_vital_organ`）；(4) `ATTRIBUTION_ADJUDICATION` 必须取 SUPPORTS/REFUTES stance → admit；(5) `LIABILITY_RUNG_EVIDENCE` 逐字 frozen ladder：ADC clinical toxicity + attribution_supported → `DIRECT`（否则归 ATTRIBUTION_ADJUDICATION）；non-ADC clinical toxicity + attribution_supported → `INDIRECT_STRONG`；validated human protein DETECTED → `INDIRECT_STRONG`；translationally relevant NHP toxicity → `INDIRECT_STRONG`；RNA-only normal signal → `WEAK`；rodent-only → `WEAK`；其余 → SOFT reject「matches no frozen TGT-05 liability evidence class」。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/evidence.py`（新） | `build_evidence_packages(...)` → `(emitted, extra_rejections, dropped)`。每个 admissible observation 一个 Gate-neutral PR A EvidencePackage；已在 Library 的复用**同一对象**（不调 allocator、不建 body）；provenance 取 resolved canonical SourceIndex record，mismatch → HARD；`_KEYS_BY_KIND` 给每个 observation kind 列 reuse parity 的 classification-driving 字段，缺失 OR drift → HARD；`_NEUTRAL_DOES_NOT_SUPPORT` 含「the absence of a normal-tissue on-target liability」/「normal-tissue safety」/「a product-specific therapeutic window」；(source_id, claim) 去重。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/aggregate.py`（新） | `aggregate(emitted, sweep)` → `AggregationOutcome`。按 `liability_event_id` 分 disputed / undisputed；frozen truth table（undisputed DIRECT → `POSITIVE/DIRECT`；else undisputed INDIRECT_STRONG → `POSITIVE/INDIRECT_STRONG`；else WEAK-only → `INCONCLUSIVE/WEAK`；else `INCONCLUSIVE/UNKNOWN`，无 refs）；positive precedence（established liability + uncovered organ → 仍 POSITIVE，gap 进 `critical_unknowns`）；CONFLICTING 仅当无独立 undisputed strong liability，Strength = disputed obs 可达最强 rung，disputed rung → SUPPORTING、真正撞上 rung 的 REFUTES → CONTRADICTING、其余 REFUTES / SUPPORTS attr → CONTEXTUAL；coverage `NOT_YET_COMPLETE` → `PUBLIC_RESOLVABLE`，`EXHAUSTED` → `EXPERIMENT_REQUIRED`；disputed events（整体非 CONFLICTING 时）→ `CURRENTLY_UNRESOLVABLE`；**永不 `NEGATIVE`/safe**。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/fatal_review.py`（新） | `detect(emitted)` → `FatalReviewRecord`。候选 = ADC_CLINICAL_TOXICITY + LIABILITY_RUNG_EVIDENCE + attribution_supported + 非空 construct_fingerprint + 非空 target_attribution_basis。`<2` → `none()`。按 EXACT `(affected_tissue.strip(), toxicity_phenotype_key.strip())` 分组；某组 ≥2 个不同 `program_id` → `FatalReviewRecord(required=True, status=POTENTIAL_FATAL_PATTERN, …)`。无 fuzzy / embedding / ontology。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/acceptance.py`（新） | `classify_path(emitted, fatal_review)` → `"A"`/`"B"`/`"C"`；`evaluate(*, emitted, outcome, sweep, fatal_review, hard_integrity_failures, path)` → `(checks, reasons)`。E1 item-13 卫生（无 hard integrity failure / one EP per observation / resolved primary source / frozen admissible class / proposed strength ≤ 最强 rung / Direction×Strength 是 frozen truth-table 输出 / never NEGATIVE / (source_id,claim) 去重 / evidence_ref 可解析 / `fatal_review.status` 不越 `POTENTIAL_FATAL_PATTERN`）+ E4-6 path 完成度（Path A/B → adc construct inventory + attribution sweep；Path C → `path_c_sweeps_complete`）。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/module.py`（新） | `run(module_input, *, provider, evidence_id_allocator, source_resolver, evidence_library)` → `Tgt05ModuleRunResult`。纯 Python：classify → build_evidence_packages → `fatal_review.detect` → `aggregate` → 由 sweep + coverage-context EP 拼 `CoverageMapRecord` → `classify_path` → `acceptance.evaluate` → accepted 才建 proposal envelope → 装 run result。**不取** 单独的 `target_identity` 参数（用 `module_input.target_identity`）。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/__init__.py`（新） | 导出 identity 常量、枚举、契约 dataclass、port Protocol、`run`。 |
| `gate_modules/tgt05_normal_tissue_fatal_liability/module.yaml`（新） | identity `MOD-TGT05` / `1.0.0` / `built_in: runtime_migration_pr_e4`；gate binding（`dominant_evidence_regime: PUBLIC_HYBRID` + `current_instantiation_regime: PUBLIC_ONLY`）；`the_one_question` 逐字 PR D；`owns` / `does_not_own`；`ports`；保守 `boundary_flags`（network / subprocess / repo write / fs-id / canonical assessment / decision / established fatal signal / ontology-embedding / numeric scoring / negative-or-safe / therapeutic-window / frozen-science / lifts-migration-pending 全 `false`）。 |
| `gate_modules/README.md`（改） | Module 注册表加 `MOD-TGT05@1.0.0`（built, PR E4）；「其余六个」措辞。 |
| `src/contracts/crc_adc_target_gateset.yaml`（改） | TGT-05 `primary_module_version` `0.0.0 → 1.0.0` + 注释；`primary_module_binding.built_module_versions` 加 `TGT-05: "1.0.0"`；`primary_module_binding.rule` 措辞（E4 built MOD-TGT05；其余六个仍 `0.0.0`）。 |
| `src/objects/crc_adc_target_gateset.py`（改） | `BUILT_MODULE_VERSIONS` 加 `"TGT-05": "1.0.0"` + 注释。 |
| `tests/test_tgt05_module.py`（新，38 tests） | 见 §四。 |
| `tests/test_gate_modules_boundary.py`（改） | 新增 `Tgt05ModuleManifestTests`（manifest ↔ package 常量 ↔ gateset binding parity；`built_module_versions["TGT-05"]=="1.0.0"`；boundary flags 全 falsey；README 注册）。 |
| `tests/test_crc_adc_target_gateset.py`（改） | `_BUILT_MODULE_VERSIONS` 加 `"TGT-05": "1.0.0"`；新增 `test_tgt05_module_is_built_in_gate_modules`。 |
| `tests/test_tgt05_module_construction_contract.py`（改） | E3「尚无实现」的 3 个 guard 改成：目录存在则其 `module.yaml` 必须 `built_in: runtime_migration_pr_e4` 且 `construction_contract` 指向 E3 合同；TGT-05 binding version 跟随 built manifest；`gate_modules/` 下只允许 `tgt01_*` / `tgt05_*` 的 `.py`（仍禁 generic framework）。 |
| `manifests/runtime_migration_pr_e4_manifest.yaml`（新） | `chatgpt_review: PENDING`、8 个 `scoping_decisions`、boundary 声明、artifact 清单。 |

## 四、测试（`tests/test_tgt05_module.py`，38 tests，全部 synthetic）

- `TruthTableTests`（9）：supported ADC clinical toxicity → `POSITIVE/DIRECT`；
  validated human protein atlas → `POSITIVE/INDIRECT_STRONG`；translationally
  relevant NHP toxicity → `INDIRECT_STRONG`；非 translational NHP → 不成 rung（SOFT
  drop，run 仍 accepted）；RNA-only atlas → `INCONCLUSIVE/WEAK`；rodent-only →
  `WEAK`；无 admissible evidence → `INCONCLUSIVE/UNKNOWN`（never auto-PASS、never
  NEGATIVE、无 refs）；validated protein NOT_DETECTED → `COVERAGE_CONTEXT`（是 EP
  但不成 rung、方向非 NEGATIVE、`coverage_map` 该器官有 supporting EP）；每个
  accepted 的 Direction×Strength 都是 frozen truth-table 输出。
- `PositivePrecedenceTests`（2）：DIRECT liability + 某器官 `NOT_YET_COMPLETE` →
  仍 `POSITIVE/DIRECT` 且 `critical_unknowns` 提及该器官；无 liability + 全部
  sweep 完成 + 某器官 `EXHAUSTED` → `INCONCLUSIVE/UNKNOWN` +
  `EXPERIMENT_REQUIRED`。
- `ConflictingTests`（3）：同一 `liability_event_id` support + refute 且无独立
  liability → `CONFLICTING`（refs 同时含 SUPPORTING 与 CONTRADICTING）；dispute +
  独立 undisputed `INDIRECT_STRONG` → `POSITIVE/INDIRECT_STRONG` + dispute 进
  `critical_unknowns`；「另一个 ADC 报告没毒」（不同 event 的 REFUTES）→ 仍
  `POSITIVE/DIRECT`，绝无 `CONTRADICTING` ref。
- `FatalReviewTests`（6）：单个 DIRECT liability → `fatal_review.required==False` /
  `status==""`；2 个不同 program 同 tissue+phenotype → `required==True` /
  `POTENTIAL_FATAL_PATTERN` / `program_ids=={A,B}` / `LIVER` in
  `affected_tissues` / run accepted；同一 program 两个 source → 不成 pattern；
  不同 tissue/phenotype → 不成 pattern；machine 永不 emit
  `PUBLIC_FATAL_SIGNAL_ESTABLISHED`（不在枚举、不在 checks/reasons）；
  `fatal_review` 不是 proposal / canonical 字段（envelope field 名不含
  `fatal`/`review`，无 `assessment_id`/`assessment_version`/`review`）。
- `StopRuleTests`（4）：Path B attribution sweep 未完 → machine reject（无
  envelope，有 reasons）；Path C sweep set 未完 → machine reject；Path A（fatal
  pattern）仍要求 ADC construct inventory sweep；DIRECT positive 不 bypass 前置。
- `EvidenceReuseAndIntegrityTests`（7）：exact library package 复用 → allocator
  0 次调用 / `evidence_packages==()` / `reused_evidence_ids` 命中 / envelope
  引用它；canonical EP 某 classification-driving 字段 drift → HARD reject；
  canonical EP 缺某 driving 字段 → HARD reject；source 不在 SourceIndex → HARD
  reject；canonical source metadata 冲突 → HARD reject；unresolved lead → SOFT
  drop（run 仍 accepted，`UNKNOWN`）。
- `BoundaryTests`（5）：包内无 network/DB/subprocess import；`run` 无单独
  `target_identity` 参；核心 6 文件正则扫无 biological threshold / numeric
  score（count guard 如 `< 2` 允许）+ `module.yaml` `numeric_scoring: false`；
  无 product-specific therapeutic-window 结论（rationale / EP `directly_supports`
  不含，`does_not_support` 含）；不构造 canonical Assessment / Decision。
- `BindingTests`（3）：TGT-05 binding `1.0.0`、TGT-01 `1.0.0`、其余六个
  `0.0.0`；`built_module_versions` 与 `BUILT_MODULE_VERSIONS` 一致
  `{TGT-01, TGT-05}`；`MIGRATION_PENDING` 保持（README、`module.yaml`
  `lifts_migration_pending: false`、`migration.deferred` 含
  `per_gate_primary_modules`）。

## 五、明确未改 / 未做

- **未接** 任何 retrieval provider / dataset（只有 normalized port Protocol +
  测试里的确定性 fake）；**未上网 / 未开 subprocess / 未连 DB / 未写仓库 /
  未自增 ID**；**无** ontology / embedding / LLM 相似度；**无** numeric score /
  biological threshold；**无** product-specific therapeutic-window 结论；
  **不产** canonical `CandidateGateAssessment` / `Decision` / `KILL`。
- **未改** PR A / B / C 合同；**未改** PR D 的 TGT-05 Gate science；**未改**
  冻结的 E3 施工合同正文
  （`src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml`）；
  **未重构** MOD-TGT01（`gate_modules/tgt01_*/` 代码未动，binding 仍 `1.0.0`）；
  **未建** generic GateModule framework / abstract base class。
- **未解除** `MIGRATION_PENDING`（8 个 primary Module 已建 2 个：TGT-01、TGT-05）。
  无新依赖（仍只 PyYAML）。
- 其余 6 个 TGT primary Module（TGT-08 → 02 → 03 → 04 → 06 → 07）属后续 PR。

## 六、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_tgt05_module.py' -v
# -> Ran 38 tests ... OK
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 906 tests ... 1 pre-existing local FAIL
#    (test_assetgenos_modules.test_migration_does_not_include_legacy_runtime_state:
#     它物理扫描 genmodules/*/__pycache__，在本机 py3.12 上 -B 仍偶发落盘；
#     在 CI 的干净 checkout 上 GREEN。E3 approval 时基线为 862，E4 +44。)
git diff --check                              # clean
bash scripts/verify_repository_boundary.sh    # 干净 tracked-tree 上 gate_modules/ 合规（未跟踪的 pipelines/ 等是既有噪音）
python3 -c "import yaml; yaml.safe_load(open('src/contracts/crc_adc_target_gateset.yaml'))"  # 结构合法
```

## 七、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入）。审核重点：8 个 scoping 决策 E4-1…E4-8 是否逐条落实；item-06
  frozen truth table 是否逐字实现（validated protein NOT_DETECTED 是
  coverage、不是 rung、不是 NEGATIVE）；CONFLICTING 是否严格按
  `liability_event_id`、「ADC-B 没毒」不产 CONTRADICTING；`fatal_review` 是
  machine trigger 而非 conclusion（`status` 单值、machine 永不
  `PUBLIC_FATAL_SIGNAL_ESTABLISHED`、不进 envelope）；E4-6 三条 path 的
  mandatory-completion 是否正确；Gate-neutral EP + exact reuse + HARD identity
  gate 是否等价 E2；是否确实无 IO / framework / MOD-TGT01 改动；binding 只动
  TGT-05 一处、`MIGRATION_PENDING` 保持。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一
  对话复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #95/#97/#99/#101/#103/#105/#107/#109/#111 先例）。

## 八、后续（未启动）

- 真实 provider / adapter（Human Protein Atlas / GTEx / Tabula Sapiens / PubMed /
  ClinicalTrials.gov / FDA / ADCdb resolution，live behind the port）+ 外部
  workspace calibration run —— 属外部 workspace，非 in-repo PR，各自需 go-ahead。
- 逐 Gate 施工图 + 实现，按 `TGT-08 → 02 → 03 → 04 → 06 → 07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
