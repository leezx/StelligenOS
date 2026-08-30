# Handoff：Runtime Migration PR E6 —— MOD-TGT08@1.0.0 实现

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e6`
- 分支：`task_20260829_runtime-migration-pr-e6`
- 基线：`origin/main` @ `14b7ac5`（PR #114 merge + PR #115 approval record 之后，
  PR E5 —— TGT-08 施工合同 —— 收口 @ `f9b4ddd` / 补登 `14b7ac5`）
- PR：待创建
- 时间：`2026-08-29`
- 授权：用户在 PR E5 APPROVE 后追加 "go ahead"；开工前审核方（ChatGPT
  `AI审核方案`）拍板 **PR E6 = MOD-TGT08@1.0.0 deterministic implementation**，
  「像 E2 / E4 一样成为完整的 Gate-specific scientific core，严格实现冻结的 E5
  施工合同，不接 live provider、不写外部 workspace、不做 calibration」，并给了 8 个
  scoping 决策 E6-1…E6-8 + 3 条 headline invariant。
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-08 primary Evidence Production
  Module 的**确定性科学核心实现**，严格实现冻结的 E5 施工合同。只调用 injected
  port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID / 不做 ontology·embedding·
  LLM 推理 / 不产 canonical Assessment 或 Decision / 不产 numeric·ranking score /
  不产 freedom-to-operate·legal 结论 / 不产 sponsor routing·KILL·STOP_FOR_SPONSOR·
  OUT_OF_MANDATE。窄修 binding：TGT-08 `primary_module_version` `0.0.0 → 1.0.0`。
  不改冻结的 E5 合同正文，不重构 MOD-TGT01 / MOD-TGT05，不解除
  `MIGRATION_PENDING`）。

## 一、8 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

| # | 决策 |
|---|---|
| E6-1 | 真实确定性 MOD-TGT08 实现（同 E2 / E4 是完整 Gate-specific scientific core）。文件 `__init__` / `module.yaml` / `contracts` / `ports` / `classify` / `evidence` / `aggregate` / `sponsor_review` / `acceptance` / `module`；`module_version 1.0.0`；两个 typed completion state（`CompetitiveLandscapeCompletion`、`PatentLandscapeCompletion`）是 `contracts.py` 里的 frozen dataclass —— module-local run record，**不是**第七个 core object；最小 binding 更新（TGT-08 `primary_module_version` `0.0.0 → 1.0.0`，`built_module_versions` + `BUILT_MODULE_VERSIONS` 加 TGT-08 —— 其余五个 TGT gate 仍 `0.0.0`）；冻结的 E5 合同正文一字不改；加 `module.yaml` + manifest + handoff + worklog + `tests/test_tgt08_module.py`；**不建** generic GateModule framework / abstract base class；**不重构** MOD-TGT01 / MOD-TGT05。 |
| E6-2 | 一个 normalized `Tgt08OpportunityProviderPort`。每条 `NormalizedOpportunityRecord` 带 `evidence_axis` ∈ {`COMPETITIVE`、`PATENT`、`UNMET_NEED`} + `observation_kind` ∈ {`COMPETITOR_PROGRAM`、`PATENT_CLAIM`、`UNMET_NEED_CONTEXT`、`SEARCH_COMPLETION_AUDIT`} + `source_authority_kind` + 只装事实（program stage / status / modality / indication context；patent family / publication / jurisdiction / claim_category / legal_status / composition_level；unmet-need outcome；audited-search completion）。provider **永不**设 axis authority ceiling、Direction 或 opportunity implication。N/A 用显式空值，不用省略。 |
| E6-3 | 两个 module-local typed completion state + 派生 per-axis authority ceiling。competitive：`primary_source_landscape_complete` → `DIRECT`，否则 `pipeline_inventory_complete` → `INDIRECT_STRONG`（pipeline DB 是 index），否则 `NOT_EVALUABLE`。patent：`composition_level_review_complete` → `DIRECT`，否则 `target_level_search_complete` → `INDIRECT_STRONG`，否则 `NOT_EVALUABLE`。overall Strength = **较弱的 required axis ceiling**（overall `DIRECT` 需两轴都在 `DIRECT` authority；「两轴都搜过」本身绝不产 `DIRECT`）。冻结的 E5 truth table，逐字 —— 两个 target-specific 轴都没开始 + admissible unmet need → `INCONCLUSIVE/WEAK`（唯一的两轴豁免，CONTEXTUAL refs）；target-specific assessment 已开始 + 某 mandatory 轴 incomplete / not evaluable OR 无 admissible evaluable landscape → `INCONCLUSIVE/UNKNOWN`（无 refs）；两轴都 evaluable → 只有 material SUPPORTS → `POSITIVE/overall`，只有 material OPPOSES → `NEGATIVE/overall`，两者都有 → `CONFLICTING/overall`，都没有 → graded `INCONCLUSIVE/overall`（CONTEXTUAL refs，严格区别于 `INCONCLUSIVE/UNKNOWN`）。合法 Direction×Strength = {POSITIVE, NEGATIVE, CONFLICTING}×{DIRECT, INDIRECT_STRONG} ∪ INCONCLUSIVE×{DIRECT, INDIRECT_STRONG, WEAK, UNKNOWN}。 |
| E6-4 | 确定性 Gate-relative opportunity implication。`COMPETITOR_PROGRAM` 同靶点 + 同 refractory-mCRC context —— `APPROVED` / `REGISTRATIONAL` / `ACTIVE_CLINICAL` → `OPPOSES_OPPORTUNITY`（qualifying）；`DISCONTINUED` / `FAILED` → `CONTEXTUAL`（竞品失败绝不自动利好 —— 那是 scientific inference）；其它 indication / early / preclinical → `CONTEXTUAL`。`PATENT_CLAIM` 同靶点 —— live + relevant composition-level target-directed ADC claim → `OPPOSES_OPPORTUNITY`（qualifying，DIRECT-eligible 轴）；live + relevant target-level-only hit → `OPPOSES_OPPORTUNITY`（qualifying，patent 轴 cap 在 `INDIRECT_STRONG`）；expired / abandoned / cancelled / `IRRELEVANT` → `CONTEXTUAL`（一个过期专利不是 whitespace）。`UNMET_NEED_CONTEXT` → `CONTEXTUAL`（WEAK 假设）。absence SUPPORT **只**来自 attempted + coverage-complete + evaluable + audited completion 且 qualifying set 为空，支持它的 evidence 是那个 `SEARCH_COMPLETION_AUDIT` EvidencePackage —— **绝不**「`if not records: supports_opportunity = True`」。completion 一致性是 **HARD** 检查 —— `competitive_completion.qualifying_program_ids` 必须等于实际 emit 的 qualifying competitor EP 集合，`patent_completion.qualifying_patent_family_ids` 必须等于实际 emit 的 qualifying patent-family EP 集合。 |
| E6-5 | machine-local `sponsor_review` review TRIGGER（`SponsorReviewRecord`：`required` / `status` / `evidence_ids` / `competitor_program_ids` / `patent_family_ids` / `landscape_as_of` / `patent_scope`）。`status` 单值 `POTENTIAL_SPONSOR_FATAL_PATTERN`。`required=true` 当且仅当，在已过 identity / provenance / classification 的 emitted / reused evidence 里，至少有一条 competitive observation（exact target + ADC + exact refractory-mCRC context + `APPROVED` 或 `REGISTRATIONAL` + primary-source verified authority —— `TRIAL_REGISTRY` / `REGULATORY_SOURCE` / `COMPANY_PRIMARY_DISCLOSURE` / `PRIMARY_CLINICAL_PUBLICATION`，不是 `PIPELINE_DATABASE` + 分类 `OPPOSES_OPPORTUNITY`）**且**至少有一条 patent observation（exact target + live relevant composition-level target-directed ADC claim + official / primary patent provenance —— `PATENT_PUBLICATION` / `OFFICIAL_PATENT_STATUS` + 分类 `OPPOSES_OPPORTUNITY`）。**无阈值、无 ownership-linkage 推断**。machine **永不**断言「dominant」/「well protected」/「no differentiation path」/「this sponsor should stop」，**永不**产 canonical fatal flag / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE。`sponsor_review` **不在** proposal envelope 上；只有 **accepted** run 的 trigger 才是可执行的 handoff。 |
| E6-6 | 每个 observation 一个 Gate-NEUTRAL EvidencePackage（PR A shape）+ exact canonical reuse。已在 Evidence Library 的 observation 复用**同一 canonical 对象** —— 不调 allocator、不建新 body；provenance 取 resolved canonical SourceIndex record（未注册 id 或 provider↔canonical metadata 冲突 → HARD reject）。reuse parity 覆盖 `_parity_keys(record)` = always 集合（`target_identity`、`evidence_axis`、`observation_kind`、`context_key`、`landscape_as_of`、`source_authority_kind`）+ **该 observation kind 的** classification-driving key；返回的 canonical package 上缺失 OR drift 的 classification / absence driving 字段 → HARD integrity failure。competition EP 说 program fact，patent EP 说 claim / status fact，unmet-need EP 说 outcome fact，audit EP 说 completed-search fact —— package **绝不**带「good / bad opportunity」「TGT-08 NEGATIVE」「crowded target」「FTO blocked」「dominant competitor」「no design around」「no differentiation path」；其 `does_not_support` 显式声明不含 FTO / infringement / validity / design-around 结论、「no differentiation path」结论、TGT-01…07 的任何 scientific de-risking、sponsor Decision / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE。 |
| E6-7 | machine acceptance = E5 item-13 清单的可执行检查。HARD identity / provenance / completion-consistency / absence-provenance 失败 → 拒**整个** run（`proposal_envelope = None`）—— **绝不**降级成 accepted `UNKNOWN`。真实 public landscape 不完整 → `INCONCLUSIVE/UNKNOWN` **不是** integrity failure。`critical_unknowns` 的 resolution 是 `PUBLIC_RESOLVABLE` / `CURRENTLY_UNRESOLVABLE` —— **绝不** `EXPERIMENT_REQUIRED`（FTO 不是实验）。accepted run 的输出面 = EvidencePackages + 两个 typed completion state + `sponsor_review` record + 一个 non-canonical `AssessmentProposalEnvelope`（无 `assessment_id` / `assessment_version` / `review`，无 FTO / legal / no-differentiation-path 结论，无 fatal flag）+ 一个 `MachineAcceptanceRecord`；module **绝不**构造 `CandidateGateAssessment`。 |
| E6-8 | CI 只跑 synthetic / in-memory 验收场景 —— 无 internet、无真实 competitor / patent 数据。synthetic `TARGET_A` / `PROGRAM_A` / `PROGRAM_B` / `PATENT_FAMILY_A` / `PATENT_FAMILY_B` / `REFRACTORY_MCRC` context；无 HER2 / TROP2 / 真实靶点名。 |

3 条 headline invariant（审核方原话）：

1. **Empty results are not whitespace.** 只有一个 AUDITED completion（attempted +
   coverage_complete + 一条带 provenance 的 `SEARCH_COMPLETION_AUDIT` observation +
   qualifying set == 0）才能支撑 absence inference。
2. **TGT-08 NEGATIVE 是 Gate-relative opportunity judgement** —— 当前 public
   opportunity evidence 不利于一个 differentiated entry。它**绝不**是 KILL /
   STOP_FOR_SPONSOR / OUT_OF_MANDATE / FTO-blocked / 对靶点的 scientific verdict。
3. **`sponsor_review` 是 review TRIGGER。** machine 检出一个 pattern；sponsor 决定
   它意味着什么。machine 永不断言 dominant / well protected / no differentiation
   path / this sponsor should stop。

## 二、边界一句话

- **PR E6 owns**：normalized TGT-08 landscape facts → source / identity QC →
  frozen E5 competitive / patent classification + Gate-relative opportunity
  implication → Gate-neutral EvidencePackages → 两个 typed completion state +
  派生 per-axis authority ceiling → weaker-axis Direction × Strength（frozen
  truth table；NEGATIVE reachable；graded INCONCLUSIVE ≠ UNKNOWN；absence
  SUPPORT 只来自 audited completion）→ machine-local `sponsor_review` review
  TRIGGER → machine acceptance → non-canonical assessment proposal envelope。
- **PR E6 does NOT own**：live ClinicalTrials / FDA / company / trial-registry
  retrieval；live patent retrieval / Lens / PATENTSCOPE / Google Patents / EPO
  adapter；trial / regulatory / patent normalisation + source-authority keying +
  provider 侧的 opportunity-implication 赋值；entity resolution / source
  registry / provenance ledger；dataset persistence；freedom-to-operate /
  infringement / validity / enforceability / design-around opinion；TGT-01…07
  的任何 scientific de-risking / re-risking；strategic materiality /「dominant」
  /「well protected」判断；sponsor routing / capital-allocation 决策；human
  `CandidateGateAssessment` approval；GateSet Decision / KILL / STOP_FOR_SPONSOR
  / OUT_OF_MANDATE。

## 三、交付物

| 文件 | 说明 |
|---|---|
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/contracts.py`（新） | frozen dataclass 输入/输出契约：`MODULE_ID=MOD-TGT08` / `MODULE_VERSION=1.0.0` / `GATE_ID=TGT-08` / `INSTANTIATION_ID=INST-CRC-REFRACTORY-ADC-TARGET-v1`；`TGT08_EVIDENCE_CEILING` / `TGT08_GATE_QUESTION` 逐字 PR D；枚举 `EVIDENCE_AXIS_VALUES` / `OBSERVATION_KIND_VALUES` / `SOURCE_AUTHORITY_KIND_VALUES`（+ `_COMPETITIVE_PRIMARY_AUTHORITIES` / `_PATENT_PRIMARY_AUTHORITIES`）/ `MODALITY_VALUES` / `PROGRAM_STAGE_VALUES`（+ `_OPPOSING_STAGES`）/ `PROGRAM_STATUS_VALUES`（+ `_DEAD_STATUSES`）/ `LEGAL_STATUS_VALUES`（+ live/dead 集合）/ `CLAIM_CATEGORY_VALUES`（+ `_ADC_COMPOSITION_CLAIM_CATEGORIES`）/ `OPPORTUNITY_IMPLICATION_VALUES`（+ `_IMPLICATION_TO_ROLE`）/ `AXIS_CEILING_VALUES` / `SPONSOR_REVIEW_STATUS_VALUES` / `CANONICAL_ONLY_FIELDS` / `LEGAL_DIRECTION_STRENGTH_PAIRS`（10 元 frozenset）/ `_CEILING_RANK`；`CanonicalSourceRecord`、`NormalizedOpportunityRecord`（按 observation kind 跨字段校验；factual 谓词 `is_same_indication_context` / `is_adc` / `competitor_stage_opposes` / `competitor_status_dead` / `patent_is_live` / `patent_is_dead` / `patent_is_composition_level_adc_claim` / `competitive_axis_primary_authority` / `patent_axis_primary_authority`）、`CompetitiveLandscapeCompletion` + `PatentLandscapeCompletion`（`axis_ceiling` / `evaluable` property；未 attempted 时禁止 complete/qualifying/sources；coverage-complete 需 `audit_observation_id` + `sources_searched`）、`Tgt08ModuleInput`（`target_identity` 唯一权威；`landscape_as_of` 强制 ISO —— 无 as_of 的 landscape 不 admissible；`evidence_regime == PUBLIC_ONLY`；`identity_pins`）、`ClassifiedOpportunity`（`rejection_severity` `""`/`HARD`/`SOFT`；`opportunity_implication`；`qualifying_for_axis`；`is_directional`）、`EmittedEvidence`、`SponsorReviewRecord`（`required` iff `status==POTENTIAL_SPONSOR_FATAL_PATTERN`；`required` 时 ≥1 competitor + ≥1 patent + ≥1 evidence；`none()`）、`AssessmentProposalEnvelope`（8 个 identity pin + `proposed_direction`/`proposed_strength`/`evidence_refs`/`aggregation_rationale`/`critical_unknowns`/`evidence_ceiling`；`(direction,strength)` 必须 ∈ `LEGAL_DIRECTION_STRENGTH_PAIRS`；`EXPERIMENT_REQUIRED` 直接 raise；POSITIVE 需 SUPPORTING、NEGATIVE 需 CONTRADICTING、CONFLICTING 需两者、graded/WEAK INCONCLUSIVE 需 CONTEXTUAL、INCONCLUSIVE/UNKNOWN 无 refs；`evidence_ceiling` 必须逐字 == `TGT08_EVIDENCE_CEILING`；不带 `assessment_id`/`assessment_version`/`review`；`field_names()`）、`MachineAcceptanceRecord`、`Tgt08ModuleRunResult`（hard failure → 无 proposal + not accepted；`sponsor_review.required` 需 accepted run；reused id 不得也作为新 body）。module 级 `overall_strength(competitive_ceiling, patent_ceiling)`。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/ports.py`（新） | `Tgt08OpportunityProviderPort`（`fetch_records` + `competitive_completion` + `patent_completion`）、`EvidenceIdAllocatorPort`、`SourceResolverPort`（→ `CanonicalSourceRecord \| None`）、`ExistingEvidenceLibraryPort`（→ `EvidencePackage \| None`，复用同一对象）。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/classify.py`（新） | `classify_record(record, *, canonical_target_identity)` → `ClassifiedOpportunity`。步骤：(1) `not primary_or_official_source_resolved` → SOFT（discovery / index lead 不成 landscape fact）；(2) target 身份不匹配 → HARD misbinding；(3) `SEARCH_COMPLETION_AUDIT` → admit `CONTEXTUAL`（neutral 已完成搜索事实）；(4) `UNMET_NEED_CONTEXT` → admit `CONTEXTUAL`（WEAK 假设）；(5) `COMPETITOR_PROGRAM` —— 非同 context → CONTEXTUAL；`competitor_status_dead` → CONTEXTUAL；`competitor_stage_opposes` → `OPPOSES_OPPORTUNITY` qualifying；否则 → CONTEXTUAL；(6) `PATENT_CLAIM` —— `IRRELEVANT` → CONTEXTUAL；`patent_is_dead` → CONTEXTUAL；live + composition-level ADC claim → `OPPOSES_OPPORTUNITY` qualifying（DIRECT-eligible）；live target-level-only → `OPPOSES_OPPORTUNITY` qualifying（轴 cap INDIRECT_STRONG）；否则 → CONTEXTUAL。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/evidence.py`（新） | `build_evidence_packages(...)` → `(emitted, extra_rejections, dropped)`。每个 admissible observation 一个 Gate-neutral PR A EvidencePackage；已在 Library 的复用**同一对象**（不调 allocator、不建 body）；provenance 取 resolved canonical SourceIndex record，mismatch → HARD；`_KEYS_ALWAYS` + `_KEYS_BY_KIND` 给每个 observation kind 列 reuse parity 的 classification-driving 字段，缺失 OR drift → HARD；`_NEUTRAL_DOES_NOT_SUPPORT` 含「a freedom-to-operate … conclusion」/「a 'no differentiation path' conclusion」/「any scientific de-risking of TGT-01 through TGT-07」/「a sponsor Decision / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE」；`study_context` 写全 parity key + `observation_id` + 全部 competitive / patent 字段；(source_id, claim) 去重。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/aggregate.py`（新） | `aggregate(emitted, competitive, patent)` → `AggregationOutcome`。per-axis ceiling 取自 completion；`overall = overall_strength(comp, pat)`（较弱轴）。frozen precedence：(a) 两 target-specific 轴都没 attempt + unmet-need → `INCONCLUSIVE/WEAK`（CONTEXTUAL refs，两轴豁免）；(b) attempt 了但某 mandatory 轴 not evaluable OR 无 admissible evaluable landscape → `INCONCLUSIVE/UNKNOWN`（无 refs）；(c) 两轴都 evaluable → 只 SUPPORTS → `POSITIVE/overall`、只 OPPOSES → `NEGATIVE/overall`、两者 → `CONFLICTING/overall`、都没有 → graded `INCONCLUSIVE/overall`（CONTEXTUAL refs）。absence SUPPORT：competitive / patent completion attempted + coverage_complete + evaluable + `len(qualifying_*_ids)==0` + 对应 audit EP 存在 → 该 audit EP 成 SUPPORTING ref。`unresolved_items` → `CURRENTLY_UNRESOLVABLE`；不完整轴（UNKNOWN 分支）→ `PUBLIC_RESOLVABLE`。**永不** `EXPERIMENT_REQUIRED`；NEGATIVE 的 rationale 明写「NOT a KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE / FTO-blocked / scientific verdict」。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/sponsor_review.py`（新） | `detect(emitted, *, landscape_as_of, patent_scope)` → `SponsorReviewRecord`。`_SPONSOR_TRIGGER_STAGES = ("APPROVED", "REGISTRATIONAL")`。competitor 候选 = `COMPETITOR_PROGRAM` + `OPPOSES_OPPORTUNITY` + `is_adc` + `is_same_indication_context` + stage ∈ `_SPONSOR_TRIGGER_STAGES` + `competitive_axis_primary_authority`；patent 候选 = `PATENT_CLAIM` + `OPPOSES_OPPORTUNITY` + `patent_is_composition_level_adc_claim` + `patent_is_live` + `patent_axis_primary_authority`。两者都非空 → `SponsorReviewRecord(required=True, status=POTENTIAL_SPONSOR_FATAL_PATTERN, evidence_ids=排序并集, competitor_program_ids / patent_family_ids=排序去重, landscape_as_of, patent_scope)`；否则 `none()`。无 fuzzy / embedding / ownership-linkage / 阈值。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/acceptance.py`（新） | `evaluate(*, emitted, outcome, competitive, patent, sponsor_review, hard_integrity_failures, module_input)` → `(checks, reasons)`。E5 item-13 卫生（无 hard integrity failure / one EP per observation / resolved primary source / frozen class only / 无重复 (source_id,claim) / evidence_ref 可解析）+ freshness（input record & completion 的 `landscape_as_of` 与 run 一致）+ completion↔emitted 一致性（`qualifying_program_ids` / `qualifying_patent_family_ids`）+ absence provenance（absence SUPPORT 必须有 backing `SEARCH_COMPLETION_AUDIT` EP）+ frozen precedence（WEAK-vs-UNKNOWN；两轴 completion；overall == 较弱轴 ceiling；DIRECT 需两轴 DIRECT authority；Direction×Strength 合法对）+ EvidenceRole 一致性（POSITIVE→SUPPORTING、NEGATIVE→CONTRADICTING、CONFLICTING→两者、graded/WEAK INCONCLUSIVE→CONTEXTUAL、UNKNOWN→无 refs；unmet-need EP 绝不 CONTRADICTING）+ sponsor_review 边界（`status` 不越 `POTENTIAL_SPONSOR_FATAL_PATTERN`；envelope field 名不含 sponsor/fatal/kill/review）+ 输出无 FTO / infringement / design-around 结论、无 dominant / well-protected / no-differentiation-path、无 TGT-01…07 scientific inference、无 KILL / Decision / STOP_FOR_SPONSOR / OUT_OF_MANDATE、无 numeric / ranking score（count guard 允许）。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/module.py`（新） | `run(module_input, *, provider, evidence_id_allocator, source_resolver, evidence_library)` → `Tgt08ModuleRunResult`。纯 Python：`classify_record` → `build_evidence_packages` → `aggregate` → `sponsor_review.detect` → `acceptance.evaluate` → accepted 才建 proposal envelope → 装 run result。`run_sponsor_review = sponsor_review if accepted else SponsorReviewRecord.none()`。**不取**单独的 `target_identity` 参（用 `module_input.target_identity`）。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/__init__.py`（新） | 导出 identity 常量、枚举、契约 dataclass、port Protocol、`run`。 |
| `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/module.yaml`（新） | identity `MOD-TGT08` / `1.0.0` / `built_in: runtime_migration_pr_e6`；gate binding（`dominant_evidence_regime: PUBLIC_PRIMARY` + `current_instantiation_regime: PUBLIC_ONLY`）；`the_one_question` 逐字 PR D；`owns` / `does_not_own`；`ports`；保守 `boundary_flags`（network / subprocess / repo write / fs-id / canonical assessment / decision / sponsor stop-or-out-of-mandate / FTO-or-legal-logic / scientific-de-risking-of-other-gates / ontology-embedding / numeric-or-ranking-scoring / absence-inference-without-audited-completion / frozen-science / modifies-mod-tgt01-or-mod-tgt05 / lifts-migration-pending 全 `false`）。 |
| `gate_modules/README.md`（改） | Module 注册表加 `MOD-TGT08@1.0.0`（built, PR E6）；「其余五个」措辞（TGT-02 → 03 → 04 → 06 → 07）。 |
| `src/contracts/crc_adc_target_gateset.yaml`（改） | TGT-08 `primary_module_version` `0.0.0 → 1.0.0` + 注释；`primary_module_binding.built_module_versions` 加 `TGT-08: "1.0.0"`；`primary_module_binding.rule` 措辞（E6 built MOD-TGT08；其余五个仍 `0.0.0`）。 |
| `src/objects/crc_adc_target_gateset.py`（改） | `BUILT_MODULE_VERSIONS` 加 `"TGT-08": "1.0.0"` + 注释。 |
| `tests/test_tgt08_module.py`（新，69 tests） | 见 §四。 |
| `tests/test_gate_modules_boundary.py`（改） | 新增 `Tgt08ModuleManifestTests`（manifest ↔ package 常量 ↔ gateset binding parity；`built_module_versions["TGT-08"]=="1.0.0"`；boundary flags 全 falsey；README 注册）。 |
| `tests/test_crc_adc_target_gateset.py`（改） | `_BUILT_MODULE_VERSIONS` 加 `"TGT-08": "1.0.0"`；新增 `test_tgt08_module_is_built_in_gate_modules`。 |
| `tests/test_tgt05_module.py`（改） | `BindingTests`：TGT-08 现在断言 `1.0.0`（从 0.0.0 循环里移出）；`built_module_versions` / `BUILT_MODULE_VERSIONS` 期望映射加 TGT-08。 |
| `tests/test_tgt05_module_construction_contract.py`（改） | `test_no_generic_gate_module_framework_or_base_class_added` 的 `allowed` 包列表加 `tgt08_target_opportunity_competition_ip_whitespace`。 |
| `manifests/runtime_migration_pr_e6_manifest.yaml`（新） | `chatgpt_review: PENDING`、8 个 `scoping_decisions` E6-1…E6-8、3 条 headline invariant、boundary 声明、artifact 清单。 |
| `docs/handoff/2026-08-29-runtime-migration-pr-e6.zh-CN.md`（新） | 本文件。 |

## 四、测试（`tests/test_tgt08_module.py`，69 tests，全部 synthetic）

- `BindingReconciliationTests`（5）：`module.yaml` identity；TGT-08 binding
  `0.0.0 → 1.0.0` + `built_module_versions`；`BUILT_MODULE_VERSIONS ==
  {TGT-01, TGT-05, TGT-08}`；其余五个 TGT gate 仍 `0.0.0`；`MIGRATION_PENDING`
  保持（`migration.deferred` 含 `per_gate_primary_modules`；boundary flags 全
  falsey）。
- `ModuleBoundaryTests`（5）：包内无 network / subprocess / persistence import；
  不 import sibling outer layer；源码无 `open(` / `write_text` / `os.system` /
  `eval` / `exec`；`run` 只取 injected port（5 参）；无 generic GateModule
  framework / ABC base class。
- `InputContractTests`（4）：`landscape_as_of` 缺失 / 非 ISO → reject；
  `evidence_regime != PUBLIC_ONLY` → reject；`instantiation_id` 非
  `INST-CRC-REFRACTORY-ADC-TARGET-v1` → reject。
- `IdentityProvenanceGateTests`（5）：candidate↔record target 不匹配 → HARD /
  not accepted / proposal None；source 不在 SourceIndex → HARD；canonical source
  metadata drift → HARD；一条 misbound record 让整个 audited 干净 landscape 也
  被拒（never 降级成 accepted UNKNOWN；`sponsor_review.required` False）；
  `primary_or_official_source_resolved=False` → **SOFT** drop（run 仍 accepted）。
- `ExactCanonicalReuseTests`（5）：library 命中 → 复用同一对象、`allocator.calls
  == 0`、`evidence_packages == ()`、`reused_evidence_ids` 命中；reused competitor
  EP `program_stage` drift → HARD；reused patent EP `legal_status` drift → HARD；
  reused EP 缺 classification-driving 字段 → HARD；reused EP `claim` drift → HARD。
- `CompetitiveClassificationTests`（7）：APPROVED / REGISTRATIONAL /
  ACTIVE_CLINICAL 同 context → `OPPOSES_OPPORTUNITY` qualifying；DISCONTINUED /
  FAILED → `CONTEXTUAL` never SUPPORTS；other-indication → `CONTEXTUAL` not
  qualifying；PRECLINICAL → `CONTEXTUAL`。
- `PatentClassificationTests`（6）：live composition-level ADC claim →
  `OPPOSES_OPPORTUNITY` qualifying（`patent_is_composition_level_adc_claim`）；
  live target-level-only → `OPPOSES_OPPORTUNITY` qualifying 但
  `patent_is_composition_level_adc_claim` False；EXPIRED / ABANDONED →
  `CONTEXTUAL` never whitespace；`IRRELEVANT` → `CONTEXTUAL`；`UNMET_NEED_CONTEXT`
  → `CONTEXTUAL` not qualifying。
- `AggregationTruthTableTests`（14）：unmet-need-only 两轴都没 attempt →
  `INCONCLUSIVE/WEAK` + CONTEXTUAL refs + accepted；完全无 admissible landscape →
  `INCONCLUSIVE/UNKNOWN` 无 refs；target-specific attempted 但 patent 轴未搜 /
  competitive 轴 incomplete → `INCONCLUSIVE/UNKNOWN`；两轴 INDIRECT_STRONG +
  只 SUPPORTS（audited absence）→ `POSITIVE/INDIRECT_STRONG`；competitive DIRECT +
  patent INDIRECT_STRONG → overall `INDIRECT_STRONG`；两轴 DIRECT + 只 SUPPORTS →
  `POSITIVE/DIRECT`；只 OPPOSES → `NEGATIVE/overall`（rationale 含 "not a kill"；
  `sponsor_review.required` False；accepted）；SUPPORTS + OPPOSES →
  `CONFLICTING/overall`；两轴 coverage-complete 但只有 CONTEXTUAL observation +
  无 clean-absence audit EP → graded `INCONCLUSIVE/DIRECT`（resp.
  `INCONCLUSIVE/INDIRECT_STRONG`），CONTEXTUAL refs；每个 accepted 的
  Direction×Strength 都是合法对；unmet need 绝不把 strong opposing landscape
  变成 `CONFLICTING`（仍 `NEGATIVE`）。
- `AbsenceInferenceTests`（6）：audited complete competitive 且 zero qualifying →
  SUPPORTS via `SEARCH_COMPLETION_AUDIT` EP（SUPPORTING ref ⊆ audit EP id）；
  `records == []` 且无 audit → never SUPPORTS（`INCONCLUSIVE/UNKNOWN`）；patent 轴
  从没搜过 → 空 patent set 绝不变成 `POSITIVE`/whitespace；completion 说 zero
  competitor 但存在 qualifying competitor EP → run rejected + reason 含
  `qualifying_program_ids`；completion 说 zero patent family 但存在 qualifying
  live patent EP → run rejected + reason 含 `qualifying_patent_family_ids`；
  completion-audit EP 带 canonical SourceIndex provenance。
- `SponsorReviewTests`（8）：APPROVED ADC + exact refractory-mCRC + primary
  source + live composition-level patent → `required=True` /
  `POTENTIAL_SPONSOR_FATAL_PATTERN` / `competitor_program_ids` /
  `patent_family_ids` / pinned `landscape_as_of` + `patent_scope` /
  `evidence_ids` 非空；`ACTIVE_CLINICAL`（非 registrational）ADC 单独 → 不 trigger；
  non-ADC APPROVED competitor 可 OPPOSE 但不 trigger（仍 `NEGATIVE`）；qualifying
  ADC competitor 但无 composition-level patent → 不 trigger；`PIPELINE_DATABASE`
  competitor（非 primary authority）→ 不 trigger；pattern 在但 run 被拒
  （completion 不一致）→ `sponsor_review == none()`；envelope field 名不含
  sponsor / fatal / kill / review，且不含 `CANONICAL_ONLY_FIELDS`；machine 永不
  在 directly_supports / rationale 里断言 dominant / well protected / no
  differentiation path / crowded target / fto blocked。
- `OutputSurfaceTests`（5）：accepted run 输出面 = EvidencePackages（全
  `EvidencePackage`）+ 两个 typed completion state + `sponsor_review` +
  `AssessmentProposalEnvelope` + `MachineAcceptanceRecord`（reasons 空）；module
  绝不构造 `CandidateGateAssessment`；`evidence_ceiling` 在 envelope 上、逐字 ==
  `TGT08_EVIDENCE_CEILING`，EP 的 `interpretation_boundary.evidence_ceiling` 是
  中性句、不等于它；`critical_unknowns` 的 resolution ⊆ {`PUBLIC_RESOLVABLE`,
  `CURRENTLY_UNRESOLVABLE`}（never `EXPERIMENT_REQUIRED`）；one EP per
  observation。

## 五、明确未改 / 未做

- **未接**任何 retrieval provider / dataset（只有 normalized port Protocol +
  测试里的确定性 fake）；**未上网 / 未开 subprocess / 未连 DB / 未写仓库 /
  未自增 ID**；**无** ontology / embedding / LLM 相似度；**无** numeric /
  ranking score；**无** freedom-to-operate / infringement / validity /
  design-around 结论；**无** sponsor routing / capital-allocation 决策；
  **不产** canonical `CandidateGateAssessment` / `Decision` / `KILL` /
  `STOP_FOR_SPONSOR` / `OUT_OF_MANDATE`。
- **未改** PR A / B / C 合同；**未改** PR D 的 TGT-08 Gate science；**未改**
  冻结的 E5 施工合同正文
  （`src/contracts/gate_modules/tgt08_target_opportunity_competition_ip_whitespace.yaml`
  与 `docs/gate_modules/TGT-08_...md`）；**未重构** MOD-TGT01 / MOD-TGT05
  （代码未动，binding 仍 `1.0.0`）；**未建** generic GateModule framework /
  abstract base class。
- **未解除** `MIGRATION_PENDING`（8 个 primary Module 已建 3 个：TGT-01、
  TGT-05、TGT-08）。无新依赖（仍只 PyYAML）。
- 其余 5 个 TGT primary Module（TGT-02 → 03 → 04 → 06 → 07）属后续 PR。

## 六、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_tgt08_module.py' -v
# -> Ran 69 tests ... OK
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 1042 tests ... 1 pre-existing local FAIL
#    (test_assetgenos_modules.test_migration_does_not_include_legacy_runtime_state:
#     它物理扫描 genmodules/*/__pycache__，在本机 py3.12 上 -B 仍偶发落盘；
#     在 CI 的干净 checkout 上 GREEN。E5 approval 时基线为 967，E6 +75。)
git diff --check                              # clean
bash scripts/verify_repository_boundary.sh    # 干净 tracked-tree 上 gate_modules/ 合规（未跟踪的 pipelines/ 等是既有噪音）
python3 -c "import yaml; yaml.safe_load(open('src/contracts/crc_adc_target_gateset.yaml'))"  # 结构合法
```

## 七、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入）。审核重点：8 个 scoping 决策 E6-1…E6-8 是否逐条落实；3 条
  headline invariant 是否成立（audited completion 之外绝无 absence inference；
  NEGATIVE 是 opportunity judgement 不是 KILL / sponsor stop；`sponsor_review`
  是 trigger 不是 conclusion）；frozen E5 truth table 是否逐字实现（weaker-axis
  overall ceiling；graded INCONCLUSIVE ≠ UNKNOWN；unmet-need-only WEAK 两轴豁免）；
  competitive / patent classification 是否逐字 E6-4（discontinued competitor 不
  自动利好；expired patent 不是 whitespace；target-level-only patent 轴 cap
  INDIRECT_STRONG）；`sponsor_review` 触发条件是否严格（primary authority、ADC、
  exact context、APPROVED/REGISTRATIONAL、composition-level live patent；无阈值 /
  无 ownership linkage）且不进 envelope、只在 accepted run 可执行；completion↔EP
  一致性是 HARD；Gate-neutral EP + exact reuse + HARD identity gate 是否等价
  E2 / E4；是否确实无 IO / framework / MOD-TGT01·MOD-TGT05 改动；binding 只动
  TGT-08 一处、`MIGRATION_PENDING` 保持。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一
  对话复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #111 / #113 / #115 先例）。

## 八、后续（未启动）

- 真实 provider / adapter（ClinicalTrials.gov / FDA / trial registries / company
  disclosures / primary clinical publications；Lens / PATENTSCOPE / Google
  Patents / EPO → 实际 patent publication / official legal-status source，live
  behind the port）+ 外部 workspace calibration run —— 属外部 workspace，非
  in-repo PR，各自需 go-ahead。
- 逐 Gate 施工图 + 实现，按 `TGT-02 → 03 → 04 → 06 → 07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
