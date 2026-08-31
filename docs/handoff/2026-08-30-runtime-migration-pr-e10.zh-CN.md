# Handoff：Runtime Migration PR E10 —— MOD-TGT03@1.0.0 实现

## 任务信息

- 任务编号：`task_20260830_runtime-migration-pr-e10`
- 分支：`task_20260830_runtime-migration-pr-e10`
- 基线：`origin/main` @ `80790c8`（PR #122 merge `a2d585d` = PR E9 TGT-03 施工合同
  三轮 APPROVE 收口 + PR #123 approval record `80790c8` 之后）
- PR：待创建
- 时间：`2026-08-30`
- 授权：用户在 PR E9 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E10 冻结为 **MOD-TGT03@1.0.0 deterministic
  implementation**：「整体上 E10-1…E10-8 是正确的，可以开工。我只做 5 个实现级
  收紧 / 修正，都不重开 E9 science。」E9 已把 TGT-03 的 science contract 冻得足够
  严，E10 只把它翻译成 deterministic runtime。
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-03 primary Evidence Production
  Module 的确定性科学核心实现，严格实现冻结的 E9 施工合同）。`run()` 纯 Python，
  只调 injected port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID / 不接
  GEO·HPA·CPTAC·scRNA·spatial·paired-biopsy·resistance-model retrieval /
  **包内不建 normalizer** / 不做 ontology·embedding·LLM 推理 / 不产 canonical
  Assessment 或 Decision / 不产 numeric·ranking score / 不产
  fold-change·%-positive·H-score·down-regulation·context-count cutoff / 不解析
  `reproducibility_basis` 自由文本 / 不把 UNKNOWN 变 PASS·HOLD·KILL / 不产
  PUBLIC_FATAL_SIGNAL_ESTABLISHED。窄修 binding：TGT-03
  `primary_module_version` `0.0.0 → 1.0.0`。不改冻结的 E9 合同正文，不重构
  MOD-TGT01 / MOD-TGT02 / MOD-TGT05 / MOD-TGT08，不解除 `MIGRATION_PENDING`。

## 一、8 个 scoping 决策 + 5 个实现级收紧

见 `manifests/runtime_migration_pr_e10_manifest.yaml` 的 `scoping_decisions`
（E10-1…E10-8）与 `five_implementation_tightenings`（逐字）。要点：

- **E10-1 包结构**：11 文件（`__init__` / `module.yaml` / `contracts` / `ports`
  / `classify` / `evidence` / `aggregate` / `completion` / `fatal_review` /
  `acceptance` / `module`）。`completion.py` 与 `fatal_review.py` 各自独立小文件。
  `ClinicalPersistenceCompletion` 是 module-local run record，**不是**第七个 core
  object。`acceptance.py` 执行 E9 item 13/10/11/12/16 的可执行检查并禁止 item-17
  跨 Gate / Decision 输出 —— **不是** 17 项 YAML parser。
- **E10-2 Provider surface**：一个 `Tgt03PersistenceProviderPort`，包自己声明其余
  三个 port。Provider 只出 **normalized upstream facts**；`assay_method` 是 OPEN
  factual type，`protein_measurement_validation_status` 是 CLOSED
  `{QUALIFIED, NOT_ESTABLISHED}` predicate。Provider 永不出 rung / Direction /
  implication / fatal 标记。**包内没有 normalizer**。
- **E10-3 分类**：`ClassifiedPersistenceObservation`。DIRECT 只给
  clinical-context protein kind + PROTEIN layer +
  `protein_measurement_validation_status == QUALIFIED` + auditable basis +
  `context_adequacy_status == QUALIFIED` + `clinical_context` 与 kind 匹配 +
  `malignant_cell_attribution == MALIGNANT`；`assay_method` **不做 whitelist**。
  transcript / resistance model 永远 INDIRECT_STRONG（即使测蛋白）。
  treatment-naive primary / different tumor 永远 WEAK / CONTEXTUAL。
  pattern → implication：RETAINED→SUPPORTS；NEAR_LOSS_OR_MARKED_LOSS→OPPOSES；
  TRANSIENT_OR_MINOR_DOWNREGULATION + `residual_target_presence_status==PRESENT`
  →SUPPORTS，`==UNRESOLVED`→CONTEXTUAL（**只由该 typed field 决定，永不解析
  basis prose**）；MIXED_OR_UNRESOLVED→CONTEXTUAL。
- **E10-4 聚合**：precedence 0(HARD)→1(incomplete→UNKNOWN, zero refs)→
  2(complete 但 audit 坏→HARD)→3(complete+audited→评估)。Strength = 最强
  qualifying class（无 two-axis / four-axis）。四个 mandatory component 是 **flat
  bool**，search-space completeness。conflict：SUPPORTS+OPPOSES→CONFLICTING，
  除非有 admissible declared multi-context observation（`persistence_context_ids`
  覆盖相关 context 且 `persistence_pattern==MIXED_OR_UNRESOLVED`）→ graded
  INCONCLUSIVE。WEAK-only completed → INCONCLUSIVE / UNKNOWN（never / WEAK）。
- **E10-5 完成态**：`ClinicalPersistenceCompletion` + 3 个 HARD invariant
  （completeness consistency；SEARCH_COMPLETION_AUDIT presence + snapshot parity
  —— snapshot 字段名 = typed completion 字段名；qualifying persistence-context-set
  parity）。`PersistenceUnresolvedItem(description, kind)` 内部类型，
  KNOWN_PUBLIC_NOT_YET_RESOLVED→PUBLIC_RESOLVABLE、
  ACCESS_OR_ANNOTATION_BLOCKED→CURRENTLY_UNRESOLVABLE。
- **E10-6 fatal_review**：消费 **已分类**证据（rung DIRECT + OPPOSES_PERSISTENCE
  + persistence_pattern NEAR_LOSS_OR_MARKED_LOSS）。Route A（一个 eligible
  contributor `reproducibility_status==QUALIFIED` + 非空 auditable basis，
  **永不解析 basis 文字**）OR Route B（eligible contributor 跨 **>= 2** 个
  independent qualified persistence-context identity，**明确不是 "> 2" / ">= 3"**）。
  status 单值 POTENTIAL_FATAL_PATTERN；只在 accepted run 上 actionable；机器永不
  PUBLIC_FATAL_SIGNAL_ESTABLISHED / fatal flag / KILL / HOLD / Decision；不在
  proposal envelope 上。
- **E10-7 EvidencePackage / exact reuse + dedup deviation**：parity keys 含
  `observation_id` / `protein_measurement_validation_status` /
  `residual_target_presence_status` / `persistence_context_id(s)` 等 +
  reused-EP 的 `source_type`/`source_identifier`/`locator` 与 canonical
  SourceIndex 复核。**不盲拷贝 E8 的 `(source_id, claim)` dedup** —— 只有
  `source_id` + `claim` + 所有 classification-driving fact + LOCAL
  persistence-context identity 全一致才算 true duplicate；任何 persistence-context
  差异 → 两个都保留；SEARCH_COMPLETION_AUDIT EP 永不是 dedup loser。HARD
  identity / provenance / completion-consistency / qualification 失败 → 拒整个
  run，绝不降级 accepted UNKNOWN。narrow EXPERIMENT_REQUIRED（E8 precedence）。
- **E10-8 proposal / acceptance / binding**：proposal identity pins 含 canonical
  `context_id CTX-CRC-REFRACTORY-MCRC`，与 LOCAL persistence_context_id 严格两套
  namespace；无 assessment_id / assessment_version / review / fatal flag /
  Decision。legal Direction × Strength 冻结（无 INCONCLUSIVE / WEAK）。binding /
  registry reconciliation 是最小集（见下）。**`MIGRATION_PENDING` 保持**（八个
  primary Module 全建完才讨论解除；余下 TGT-04 → TGT-06 → TGT-07）。

**5 个实现级收紧**（审核方逐字）：(1) 包内不建 normalizer；(2) fatal detector 只
消费已分类证据，不建第二套 qualification engine；(3) Route A 永不解析
`reproducibility_basis` 自由文本；(4) 不盲拷贝 E8 的 `(source_id, claim)` dedup；
(5) E10 必须把 `tests/test_tgt03_module_construction_contract.py` 迁成
post-implementation reconciliation（不是删除）+ 最窄同步其它 hard-code built
roster 的 test。

## 二、三条 headline invariant（写在 `contracts.py` 顶部）

1. Baseline expression is not persistence. Only explicitly qualified
   treatment / metastasis-context evidence can drive TGT-03.
2. A single observation is evidence, never a Direction; grading requires the
   completed and audited persistence landscape, and NEGATIVE remains a
   scientific persistence judgement —— not fatal and not KILL.
3. Only reproducible DIRECT-class protein near / marked loss may surface
   POTENTIAL_FATAL_PATTERN; reproducibility is Route A or Route B, remains
   human-reviewable, and the Module never decides fatality.

## 三、交付物

- `gate_modules/tgt03_treatment_metastatic_persistence/` —— 11 文件确定性核心
  （`completion.py` + `fatal_review.py` 独立；**无 `normalizer.py`**）。
- `src/contracts/crc_adc_target_gateset.yaml` + `src/objects/crc_adc_target_gateset.py`
  —— TGT-03 binding `0.0.0 → 1.0.0`；`built_module_versions` /
  `BUILT_MODULE_VERSIONS` 增 `TGT-03`。
- `gate_modules/README.md` —— MOD-TGT03 注册为 built (PR E10)；未建计数降到三。
- `tests/test_tgt03_module.py` —— 合成 acceptance 套件（78 tests）。
- `tests/test_tgt03_module_construction_contract.py` —— E9 合同 ↔ 仓库对账
  （`ContractIsFrozenAndImplementedInPrE10Tests` —— 包存在、binding 1.0.0、合同
  仍冻结）。
- `tests/test_gate_modules_boundary.py` —— `Tgt03ModuleManifestTests`（5 tests）。
- `tests/test_crc_adc_target_gateset.py` + `tests/test_tgt02_module_construction_contract.py`
  + `tests/test_tgt05_module.py` + `tests/test_tgt05_module_construction_contract.py`
  + `tests/test_tgt08_module.py` + `tests/test_tgt08_module_construction_contract.py`
  —— 最窄同步 hard-code built-roster 断言。
- `manifests/runtime_migration_pr_e10_manifest.yaml`、本 handoff。
- 既有文件唯一非对账改动：append `logs/worklog.md`。

## 四、验证

- `tests/test_tgt03_module.py` **78 OK**；
  `tests/test_tgt03_module_construction_contract.py` **75 OK**。
- 全量 `python3 -B -m unittest discover -s tests -p 'test_*.py'` **1366 OK**
  （PR E9 收口 1283；+83 = 78 新 module 测试 + 5 boundary manifest 测试）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项
  （`AI_RESULT_ACCEPTANCE.md`、`CRC Patient Territory Map.png`、
  `STELLIGEN_CONSTRAINTS.md`、`docs/worklogs/`、`pipelines/`）。
- `git diff --check` clean；无 bytecode artifact；YAML 合法。

## 五、状态与下一步

- 8 个 primary Module 已实现 5 个（TGT-01/02/03/05/08 @ `1.0.0`）。MOD-TGT03
  `primary_module_version` = `1.0.0`。`MIGRATION_PENDING` 保持。
- Next：开 PR、CI 绿后回 `AI审核方案` 贴 E10 review。fatal-first + cheap-first
  余下 TGT-04 → TGT-06 → TGT-07，各自 construction contract / implementation
  PR 需各自 go-ahead。
