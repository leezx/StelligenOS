# Handoff：Runtime Migration PR E9 —— TGT-03 / MOD-TGT03 Construction Contract

## 任务信息

- 任务编号：`task_20260830_runtime-migration-pr-e9`
- 分支：`task_20260830_runtime-migration-pr-e9`
- 基线：`origin/main` @ `94039e5`（PR E8 —— MOD-TGT02@1.0.0 —— merge `ca0b4ad` +
  approval record `94039e5` 之后）
- PR：待创建
- 时间：`2026-08-30`
- 授权：用户在 PR E8 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed，带 4 个必须在 E9 合同里修正的 scoping 点**，把 E9 冻结为
  **TGT-03 / MOD-TGT03 Construction Contract，design-only**（Module 在 PR E10 才
  实现），并给了 9 个 scoping 决策 E9-1…E9-8 + (a)–(e) + 3 条 headline conclusion。
- 变更定位：`DESIGN_ONLY`（第五层的施工合同 + 施工图 + 17 项验收清单 + parity /
  validation 测试 + manifest / handoff / worklog）。不写实现、不接 provider /
  adapter、不上网、不产 runtime EvidencePackage / proposal / fatal detector、不产
  numeric / ranking score、不产 fold-change / %-positive / H-score /
  down-regulation / context-count cutoff、不建 generic GateModule framework /
  ABC、不重构 MOD-TGT01 / MOD-TGT02 / MOD-TGT05 / MOD-TGT08。**唯一允许触碰的既有
  文件是 append 到 `logs/worklog.md`** —— 不动 binding、registry、任何既有 test
  （那些留到 PR E10）。MOD-TGT03 `primary_module_version` 仍 `0.0.0`；
  `MIGRATION_PENDING` 保持。Module 必须在本合同 APPROVE 之后才开工（CURRENT_SYSTEM
  v5 §6.4）。

## 一、3 条 headline conclusion（审核方原话，冻结在合同顶部）

1. **Baseline expression is not persistence.** TGT-02 evidence cannot discharge
   TGT-03 unless the evidence source itself explicitly measures a qualified
   treatment / metastasis context.
2. **TGT-03 is a bidirectional scientific persistence gate:** qualified
   clinical-context retention supports `POSITIVE`, qualified clinical-context near
   / marked loss supports `NEGATIVE`；`NEGATIVE` is not fatal and not `KILL`.
3. **Reproducible protein-level near / marked loss may trigger only
   `POTENTIAL_FATAL_PATTERN`；** reproducibility requires auditable evidence and
   is not defined solely by a numeric context count. The Module never decides
   fatality.

## 二、4 个必须在合同里修正的 scoping 点（审核方原话，全部已落实）

1. **`TRANSIENT_OR_MINOR_DOWNREGULATION` 不能固定成 `CONTEXTUAL`。** 一个 qualified
   transient / minor down-regulation 只要还证明 expression 在相关 treated /
   metastatic context 里 remains present，就是 `SUPPORTS_PERSISTENCE`（可贡献
   `POSITIVE` Direction）；它**永不**贡献 `NEGATIVE`、**永不**进 `fatal_review`、
   **永不**建立 TGT-04 density；只有当 observation 本身对 retention 都含糊时才
   NONDIRECTIONAL / CONTEXTUAL。「not sufficient for fatal」≠「scientifically
   non-directional」。
2. **「reproducible」不是 `len(context_ids) > 2`。** 两条 sufficient machine
   candidate route —— **Route A**：一个 auditable study / analysis 明确跨 paired /
   multiple patients / samples / contexts 建立 reproducibility（
   `reproducibility_status == QUALIFIED` + auditable `reproducibility_basis`，且
   source / human normalization 明确支持 reproducible marked / near loss）；
   **Route B**：convergent `NEAR_LOSS_OR_MARKED_LOSS` 跨 **AT LEAST TWO**
   independent qualified clinical persistence context identities —— 一条
   deterministic **sufficient** convergence pattern，**不是**「reproducible」的
   词义定义，**不是**新的 biological threshold，**不是**「more than two」/「> 2」。
3. **DIRECT protein measurement 不能被 E9 缩成 3-assay closed whitelist。** PR D
   TGT-03 的 DIRECT class 写的是「protein-level target retention … with
   malignant-cell attribution」，没有 closed assay enum（TGT-02 有，所以 E8 可以做
   typed whitelist）。E9 冻结 DIRECT 为：a protein-level clinical-context
   measurement + a factual `assay_method` type + a
   `protein_measurement_validation_status` / basis。validated IHC / quantitative
   proteomics / validated multiplex IF 是 **admissible examples**，不是 exhaustive
   set；PR E10 不得因为出现另一个可靠 protein-level method 就自动降级。
4. **EvidencePackage 可以写 empirical persistence / loss fact。** 不冻结「an EP
   may never say 'persists' or 'is lost'」—— 允许「source reported retained
   target protein staining after prior therapy」「paired pre-/post biopsies showed
   a marked reduction of target protein」「metastatic liver lesions retained
   target protein」。禁止的是 Gate-relative conclusion（passes TGT-03 / TGT-03
   POSITIVE / TGT-03 NEGATIVE / adequate persistence established / meaningful
   target availability is lost / fatal / should be killed）；即使 literal
   Gate-relative wording 是 source 自己的 claim，Module 也永不把它升级成 Gate
   conclusion。

## 三、9 个 scoping 决策（E9-1…E9-8 + (a)–(e)）

E9-1…E9-8 逐条正文见 `manifests/runtime_migration_pr_e9_manifest.yaml` 的
`scoping_decisions` 与 `four_mandatory_scoping_corrections`。要点：

- **E9-1** 完整施工合同，design-only；文件名对齐 canonical Gate 名
  「Treatment / Metastatic Persistence」（`tgt03_treatment_metastatic_persistence.yaml`
  / `TGT-03_Treatment_Metastatic_Persistence.md` /
  `test_tgt03_module_construction_contract.py`）。10 项禁止全部冻结。MOD-TGT03
  `0.0.0`；其它四个 `1.0.0`；`MIGRATION_PENDING` 保持。
- **E9-2** 17 项模板原样继承 E1（E2/E4/E6/E8 + E7 已验证）。items 03/05/07/08
  与冻结 PR D TGT-03 做 normalized-equality parity；item 04 对 evidence_required
  + ladder union 做 **exact set equality** derived parity。inference_guard 逐字
  pin。
- **E9-3** Direction × Strength —— bidirectional scientific persistence gate。
  Direction 定义冻结（POSITIVE retention / NEGATIVE materially impaired
  persistence / CONFLICTING genuinely incompatible overall claims / INCONCLUSIVE）。
  `persistence_pattern` ∈ {RETAINED, NEAR_LOSS_OR_MARKED_LOSS,
  TRANSIENT_OR_MINOR_DOWNREGULATION, MIXED_OR_UNRESOLVED} upstream-qualified，
  basis ∈ {SOURCE_REPORTED, HUMAN_REVIEWED_NORMALIZATION}，缺失 / drift → HARD。
  **CORRECTION 1** 已落实（见上）。DIRECT qualification = protein-level + CRC +
  explicitly qualified refractory / prior-treated OR metastatic context +
  malignant-cell attribution + QUALIFIED context adequacy + basis；paired
  pre/post 是 high-info DIRECT 但**仍只是 DIRECT**（无 SUPER_DIRECT）；resistance
  model 即使测 protein 也是 INDIRECT_STRONG（context 是 model）。
  INDIRECT_STRONG 严格 PR D。WEAK = treatment-naive primary CRC only /
  different-tumor；WEAK-only → INCONCLUSIVE / UNKNOWN 零 evidence_refs（对齐 PR D
  「Only treatment-naive primary CRC data -> UNKNOWN」）。overall Strength = 最强
  qualifying frozen class（**无** E6-style two-axis rule；四个 mandatory search
  component 是 search-space completeness，**不是** four-axis score）。graded
  INCONCLUSIVE vs UNKNOWN 严格区分。CONFLICTING 不自动等同 qualified context /
  site / time variation —— source 定性 context-dependent / variable 或 variation
  回答不了 overall persistence → graded INCONCLUSIVE；Strength 不自动降级。单条
  observation 永不是 Direction。
- **E9-4** fatal —— machine-local fatal_review，绝不直接 KILL。PR D fatal 逐字。
  fatal candidate 必须**全部满足**：protein-level + CRC + malignant-cell
  attributed + explicitly qualified treated / refractory / metastatic clinical
  persistence context + QUALIFIED context adequacy + auditable basis +
  `persistence_pattern == NEAR_LOSS_OR_MARKED_LOSS`（**不是**
  TRANSIENT_OR_MINOR_DOWNREGULATION）+ auditable basis + completed audited
  persistence landscape + **CORRECTION 2** 的 reproducibility Route A 或 Route B。
  显式排除 fatal trigger：TRANSIENT_OR_MINOR_DOWNREGULATION、transcript-only、
  resistance-model-only、different tumor type、treatment-naive primary CRC。
  human-only：marked-vs-transient loss、context independence、assay / platform
  artifact、reported reproducibility convincingness、meaningful availability
  lost、GateSet fatal policy。machine 永远至多 POTENTIAL_FATAL_PATTERN；永不
  PUBLIC_FATAL_SIGNAL_ESTABLISHED。无 numeric / %-positive / H-score /
  fold-change / context-count 阈值。
- **E9-5** typed `ClinicalPersistenceCompletion`（PR E10 module-local frozen
  dataclass，**非**第七个 core object；字段见 manifest）。四个 component 就是
  `declared_mandatory_search_components`，但**「mandatory 是 search-space
  completeness，不是 evidence prerequisites」**：≠ 每个 component 都要出 evidence、
  ≠ 每个 component 都要 DIRECT、≠ weaker-axis rule；component
  searched / exhausted with zero qualifying records 也算 complete；目的只是防止
  Module 找到一个漂亮 paired study 就停搜 metastatic evidence 并 cherry-pick
  Direction。`metastatic_lesion_search` 必须覆盖 PR D 明写的 liver / CRLM / lung
  / peritoneal，但**不为每个 organ 建一个 completion axis**。
  `public_persistence_search_complete` == `all(四个 component 状态)`；矛盾 →
  E10 HARD。completion ↔ SEARCH_COMPLETION_AUDIT snapshot parity（E6 / E8 gene）
  为 E10 冻结；attempted completion 需**恰好一条** normalized matching audit
  observation **且**恰好一条 emitted / reused provenance-bearing matching audit
  EP；missing / drifted / dedup-lost snapshot → HARD reject。normalized
  observation 概念字段在 drawing 里冻结（observation_kind 8 值、molecular_layer、
  `assay_method`（open set）、`protein_measurement_validation_status`、
  `clinical_context` + basis、`context_adequacy_status` + basis、
  `malignant_cell_attribution` + basis、`persistence_pattern` + basis、
  `reproducibility_status` + basis）。
- **E9-6** source-plan hard locks。**CORRECTION 3** 已落实（见上）。其它 lock：
  transcript / resistance model 永不 DIRECT；protein without malignant
  attribution 永不 DIRECT；treatment-naive primary CRC 永不 persistence claim
  （只作 frozen WEAK class）；different tumor type 是 WEAK context 且永不 CRC
  persistence；baseline TGT-02 coverage 永不 substitute for persistence；
  persistence result 永不 establish TGT-04 surface / density；generic EVGAP-02 /
  CRC-linkage observation 只有 source + context 明确 qualify 为
  treatment / metastasis context 时才贡献。PUBLIC_ONLY 路径。
- **E9-7** stop rule + EXPERIMENT_REQUIRED。precedence：HARD → 拒整个 run；else
  persistence search incomplete → INCONCLUSIVE / UNKNOWN 零 evidence_refs；else
  completed + audited → 按最强 qualifying frozen rung grade。禁止：一组 paired
  biopsy → 早 grade；一个 metastatic cohort → 早 grade；一个 loss observation →
  早 fatal。EXPERIMENT_REQUIRED 允许但**窄**（E8 precedence）：仍有 unresolved
  public item 时 resolution 停在 PUBLIC_RESOLVABLE / CURRENTLY_UNRESOLVABLE，
  **不** auto-add EXPERIMENT_REQUIRED；只有 enumerated public persistence source
  space 耗尽 AND Gate question 需要 NEW clinical-context measurement 时才
  EXPERIMENT_REQUIRED（两个例子见 manifest）。paired pre/post biopsy 只是 one
  possible experimental form，不是唯一要求。potential-fatal trigger 只在必要的
  persistence-search completeness 满足**之后**才停追更弱 proxy —— Module 绝不在
  第一个 loss observation 上停。
- **E9-8** items 10–17 直接继承 E2 / E4 / E6 / E8 runtime genes（context_id /
  context_version HARD pin + `observation.context_key == run.context_key` +
  `completion.search_scope == run.persistence_search_scope`；exact canonical
  reuse 含 observation_id parity + reused-EP canonical-provenance re-check；
  kind / fact-specific study_context；SEARCH_COMPLETION_AUDIT EP 不能被 dedup 吃
  掉；HARD integrity failure → 拒整个 run，绝不降级 accepted UNKNOWN）。
  **CORRECTION 4** 落在 item 11。fatal_review record 按审核方补的 shape 加了
  **`reproducibility_basis_refs`**（detector 依赖「reproducible」，review surface
  需要给 human 的 provenance）。
- **(a)** `ClinicalPersistenceCompletion` 名字 + 四个 component 批准（见 E9-5）。
- **(b)**「reproducible」≠ TGT-02 的 plural logic —— 是 Route A / Route B 两条
  route，`>= 2` 只是其中一条 sufficient route，不是唯一 route（见 E9-4 /
  CORRECTION 2）。
- **(c)** `TRANSIENT_OR_MINOR_DOWNREGULATION` **不**严格 CONTEXTUAL —— 支持
  persistence（见 CORRECTION 1）。
- **(d)** design-only PR，唯一允许的既有文件改动是 **append 到
  `logs/worklog.md`**；contract / drawing / TGT-03 test / manifest / handoff 全
  是新增文件。**不动** `crc_adc_target_gateset.yaml` / `.py`、
  `gate_modules/README.md`、`test_crc_adc_target_gateset.py`、
  `test_gate_modules_boundary.py`、任何既有 gate_modules/tgt01|02|05|08 文件 ——
  留到 E10。
- **(e)** 3 条 headline conclusion 由审核方给（见上）。

## 四、文件

### 新增（design-only deliverable）

| 文件 | 内容 |
|---|---|
| `src/contracts/gate_modules/tgt03_treatment_metastatic_persistence.yaml` | 17 项施工合同 + `headline_conclusions` + `core_chain` + `migration` / `template_provenance` / `kernel_invariant` / `deferred_to_pr_e10_plus` / `repository_policy` |
| `docs/gate_modules/TGT-03_Treatment_Metastatic_Persistence.md` | 施工图：17 行表 + 3 条 headline blockquote + normalized-observation / `ClinicalPersistenceCompletion` conceptual shape + "What PR E9 is NOT" |
| `tests/test_tgt03_module_construction_contract.py` | **66 tests**：ContractShape / Identity / VerbatimFromPrD（parity）/ BidirectionalDirection / Correction1TransientMinorSupportsPersistence / Correction2ReproducibleIsTwoRoutes / Correction3DirectIsNotAClosedWhitelist / Correction4EpMayStateEmpiricalFact / FatalReviewAndProposal / CompletionAndSourcePlan / RuntimeGeneInheritance / NoImplementationInPrE9 / Drawing |
| `manifests/runtime_migration_pr_e9_manifest.yaml` | 本 PR 的 manifest |
| `docs/handoff/2026-08-30-runtime-migration-pr-e9.zh-CN.md` | 本文件 |

### 既有文件（唯一允许改动）

- `logs/worklog.md` —— append E9 build entry。

## 五、验证

- `tests/test_tgt03_module_construction_contract.py` **66 OK**。
- 全量 `unittest discover`：**1274**（E8 收口时 1208；+66 tgt03 construction
  tests）。**全绿**。
- `bash scripts/verify_repository_boundary.sh` —— 只报既有 untracked 杂项
  （`pipelines/`、`STELLIGEN_CONSTRAINTS.md`、`CRC Patient Territory Map.png`、
  `AI_RESULT_ACCEPTANCE.md`），不属本 PR，干净 CI checkout 上不存在。
- `git diff --check` clean；两个 YAML（contract、E9 manifest）合法。
- items 03/05/07/08 normalized-equality parity + item 04 exact set-equality
  parity vs 冻结 PR D TGT-03 —— 全部 PASS。

## 六、状态

8 个 primary Module 施工合同已 APPROVE 5 个（MOD-TGT01/05/08/02 + 本 PR 待审的
MOD-TGT03）；已实现 4 个（MOD-TGT01@1.0.0 E2、MOD-TGT05@1.0.0 E4、
MOD-TGT08@1.0.0 E6、MOD-TGT02@1.0.0 E8）。MOD-TGT03 `primary_module_version` 仍
`0.0.0`（PR E10 bump 到 `1.0.0`）。其余三个 gate（TGT-04 → TGT-06 → TGT-07）属
后续 PR。`MIGRATION_PENDING` 保持。真实 retrieval provider / adapter / dataset
与外部 workspace calibration 各自需 go-ahead。下一步 PR E10 = MOD-TGT03@1.0.0
deterministic implementation（需各自 go-ahead）。
