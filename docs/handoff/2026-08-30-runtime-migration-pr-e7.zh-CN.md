# Handoff：Runtime Migration PR E7 —— TGT-02 / MOD-TGT02 Construction Contract

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e7`
- 分支：`task_20260829_runtime-migration-pr-e7`
- 基线：`origin/main` @ `97ad48d`（PR E6 —— MOD-TGT08@1.0.0 —— merge `c03fa34` +
  approval record `97ad48d` 之后）
- PR：待创建
- 时间：`2026-08-30`
- 授权：用户在 PR E6 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E7 冻结为 **TGT-02 / MOD-TGT02 Construction
  Contract，design-only**（Module 在 PR E8 才实现），并给了 9 个 scoping 决策
  E7-1…E7-9 + 3 条 headline conclusion。
- 变更定位：`DESIGN_ONLY`（第五层的施工合同 + 施工图 + 17 项验收清单 + parity /
  validation 测试 + manifest / handoff / worklog）。不写实现、不接 provider /
  adapter、不上网、不产 runtime EvidencePackage 或 proposal、不产 fatal detector
  runtime、不产 numeric / ranking score、不产 cohort-size / %-positive / H-score /
  heterogeneity cutoff、不建 generic GateModule framework / abstract base class、
  不重构 MOD-TGT01 / MOD-TGT05 / MOD-TGT08。MOD-TGT02 `primary_module_version`
  仍 `0.0.0`；`MIGRATION_PENDING` 保持。Module 必须在本合同 APPROVE 之后才开工
  （CURRENT_SYSTEM v5 §6.4）。

## 一、3 条 headline conclusion（审核方原话）

1. **TGT-02 的 NEGATIVE 可达，而且是真正的 scientific NEGATIVE** ——「当前合格证据
   显示，refractory mCRC malignant cells 对该 target 缺乏足够的 population-level
   expression coverage」。它不是 TGT-08 那种商业 NEGATIVE，也不是 TGT-05 的
   liability-positive 反向解释。
2. **NEGATIVE ≠ fatal ≠ KILL。** `NEGATIVE / DIRECT` 可以出现，但只有满足 PR D
   fatal condition 的跨 cohort protein-level pattern 才进入一个 machine-local
   `fatal_review = POTENTIAL_FATAL_PATTERN`。Module 永远不输出 canonical fatal
   flag / KILL；最终 fatal policy 属于 GateSet Decision layer。
3. **TGT-02 需要一个 typed `CrcCohortCoverageCompletion`**（E6-style gene，但科学
   语义不同）：只有 completed / audited CRC coverage search 才能把单个 observation
   聚合成 cohort-level Gate judgement —— 一个漂亮 cohort 绝不是 population-level
   答案。

## 二、9 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

| # | 决策 |
|---|---|
| E7-1 | 完整施工合同，design-only。文件 `tgt02_indication_specific_malignant_cell_coverage.yaml` + drawing + `test_tgt02_module_construction_contract.py` + manifest / handoff / worklog。禁止 `gate_modules/tgt02.../` runtime / provider / adapter / GEO·HPA·CPTAC·scRNA·spatial retrieval / EvidencePackage runtime / proposal runtime / fatal detector runtime / numeric·ranking score / cohort-size·%-positive·H-score·heterogeneity cutoff / generic framework·ABC / 新依赖 / 外部数据 / MOD-TGT01·MOD-TGT05·MOD-TGT08 refactor。MOD-TGT02 `0.0.0`；其它三个 `1.0.0`；`MIGRATION_PENDING` 保持。 |
| E7-2 | 17 项模板原样继承 E1（E2/E4/E6 已验证）。items 03/05/07/08 与冻结 PR D TGT-02 做 normalized-equality parity；item 04 对 `evidence_required` + ladder union 做 derived parity。`inference_guard` 逐字 pin：「EVGAP-02 primarily contributes TGT-02; generic CRC linkage does NOT discharge TGT-03.」 |
| E7-3 | Direction × Strength —— TGT-02 是 **bidirectional scientific coverage gate**。Direction relative to Gate question：`POSITIVE`（支持 malignant-cell coverage）/ `NEGATIVE`（支持 lack of adequate coverage：absent, or rare and highly heterogeneous）/ `CONFLICTING`（admissible observations 真正互斥、无 auditable pattern 化解）/ `INCONCLUSIVE`（不解析）。`DIRECT` 需 protein-level + CRC + malignant-cell attributed + adequately-powered cohort qualification + completed audited landscape → `POSITIVE/DIRECT`（broad consistent presence）、`NEGATIVE/DIRECT`（absent / rare+highly heterogeneous）。**「rare / highly heterogeneous」不由 Module 从 %/H-score/n 计算** —— 来自 auditable upstream qualification（`expression_pattern` ∈ {ABSENT, RARE_HIGHLY_HETEROGENEOUS}，`expression_pattern_basis` ∈ {SOURCE_REPORTED, HUMAN_REVIEWED_NORMALIZATION}）；缺失 / drift 的 basis → HARD。`INDIRECT_STRONG` = qualifying sc/spatial malignant-compartment 或 CRC TMA transcript+protein concordance → `POSITIVE/INDIRECT_STRONG` 或 `NEGATIVE/INDIRECT_STRONG`；transcript-only 永不升 DIRECT，quantity 永不提 ceiling。**WEAK-only public landscape → `INCONCLUSIVE/UNKNOWN`，不是 `INCONCLUSIVE/WEAK`**（TGT-02-specific；PR A：`INCONCLUSIVE/UNKNOWN` 零 evidence_refs，graded INCONCLUSIVE 带 CONTEXTUAL refs）。graded INCONCLUSIVE = qualifying DIRECT/INDIRECT_STRONG 证据存在、landscape 完整，但方向 MIXED / 不解析。**overall Strength = 最强 qualifying evidence class**，**无** E6-style two-axis weaker-ceiling rule。CONFLICTING 不自动等同真实 biological heterogeneity：valid audited multi-cohort 把 coverage 定性为 RARE_HIGHLY_HETEROGENEOUS → `NEGATIVE`，不是 `CONFLICTING`。 |
| E7-4 | fatal —— machine-local `fatal_review`，绝不直接 KILL。machine 至多在以下情况 surface candidate：protein-level observations，每个带 CRC malignant-cell attribution、`QUALIFIED` cohort_adequacy_status + auditable basis、negative coverage class（ABSENT / RARE_HIGHLY_HETEROGENEOUS）+ auditable basis，且在 completed audited landscape 上，且 cross-cohort support —— **at least two independent cohort identities**（或一个 declared multi-cohort analysis 带 at least two auditable cohort_ids）。「across cohorts」是 plural-cohorts 逻辑（at least two，不是 "more than two" / "> 2"），**不是新阈值**。machine 永远至多 `POTENTIAL_FATAL_PATTERN`；永不 `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / canonical fatal flag / KILL / HOLD / Decision。human-only：cohort adequacy basis 是否可信、cohorts 是否真正独立、rare-highly-heterogeneous 是否成立、assay/platform 差异是否解释 convergence、是否满足 GateSet fatal policy。无 numeric / %-positive / H-score / heterogeneity 阈值。 |
| E7-5 | typed `CrcCohortCoverageCompletion`（PR E8 module-local frozen dataclass，**非**第七个 core object）：`attempted` / `landscape_as_of` / `search_scope` / `sources_searched` / `public_crc_coverage_search_complete` / `protein_cohort_search_complete` / `malignant_compartment_sc_spatial_search_complete` / `tma_concordance_search_complete` / `matched_normal_tumor_search_complete` / `unresolved_items` / `qualifying_protein_cohort_ids` / `qualifying_indirect_cohort_ids` / `audit_observation_id`。**无 E6-style 两个 mandatory axes**。completion ↔ `SEARCH_COMPLETION_AUDIT` snapshot parity（E6 gene）为 E8 冻结：search_scope / sources_searched / landscape_as_of / per-component completion states / unresolved_items / qualifying cohort ids；缺失 / drift → HARD。normalized observation 概念字段在 drawing 里冻结（observation_kind 7 值、molecular_layer、malignant_cell_attribution + basis、cohort_adequacy_status + basis、expression_pattern + basis 等）。provider 只给事实，不给 rung / direction / pass-fail。 |
| E7-6 | source-plan hard locks。`DIRECT` = validated CRC IHC / quantitative proteomics / validated multiplex IF in annotated malignant cells across adequately powered CRC cohort。**永不** scRNA / spatial RNA / bulk RNA → DIRECT；**永不** protein without malignant attribution → DIRECT。`INDIRECT_STRONG` = scRNA / spatial RNA + malignant compartment resolved，或 CRC TMA transcript+protein concordance + malignant-cell attribution。`WEAK` = bulk CRC RNA without deconvolution，或 pan-cancer unresolved to CRC。compartment hard lock：stroma / immune / mixed-tissue expression ≠ CRC malignant-cell expression（可作 contextual observation，**不** discharge TGT-02）。transcript ≠ protein（醒目）：transcript 能支持 malignant-compartment expression，但不能建立 protein-level malignant-cell coverage；quantity（多个强数据集）不提 class ceiling。matched normal-vs-tumor 在 PR D evidence_required 里，但**不得**被误用成「normal low + tumor high → favorable therapeutic index」—— 在 TGT-02 只 contextualise CRC malignant-cell expression（TGT-05 才管 normal-tissue liability）。PUBLIC_ONLY 路径。 |
| E7-7 | stop rule + EXPERIMENT_REQUIRED。target-specific CRC coverage search 已开始但某 mandatory declared component 未完成 → `INCONCLUSIVE/UNKNOWN`；不因中间搜到漂亮结果提前 grade（completion state 的用途）。public search complete → 最强 qualifying evidence：DIRECT directional / else INDIRECT_STRONG directional / else `INCONCLUSIVE/UNKNOWN`；WEAK-only 仍 UNKNOWN。TGT-02 **可以且应该**用 `EXPERIMENT_REQUIRED`，但只有 enumerated public CRC coverage source space completed / exhausted **且** 未解的 Gate question 需要**新的** malignant-cell-resolved protein / adequately powered cohort measurement 时（例：public sc/spatial 一致支持 malignant-cell expression 但无 adequate protein cohort → `POSITIVE/INDIRECT_STRONG` + critical_unknown 「protein-level malignant-cell cohort confirmation」= `EXPERIMENT_REQUIRED`；只有 bulk RNA + source space exhausted → `INCONCLUSIVE/UNKNOWN` + `EXPERIMENT_REQUIRED`）。known-but-unfetched public dataset / incomplete public cohort search → `PUBLIC_RESOLVABLE`；source 存在但 access/annotation 当前无法解析 → `CURRENTLY_UNRESOLVABLE`。到 `EXPERIMENT_REQUIRED` 后 public Module 停止追更弱 proxy。potential-fatal trigger 只能在 cohort coverage completeness 满足**之后**停止追更弱 bulk / pan-cancer proxy —— Module **永不**在第一条 negative cohort 就停。 |
| E7-8 | items 10-17 直接继承 E2/E4/E6 runtime genes。Item 10 instantiation pins / context·version / Gate·GateSet version / PUBLIC_ONLY / run_id·code_commit / landscape_as_of / declared CRC coverage search scope / existing evidence ids；无第二个 drift-prone target argument；无 implicit default context。Item 11 atomic Gate-neutral immutable-by-ID EvidencePackage，一 observation 一 EP，canonical SourceIndex provenance，exact canonical reuse；EP 只陈述中性事实，绝不「passes TGT-02 / adequate coverage / is fatal / should be killed」；SEARCH_COMPLETION_AUDIT EP 带 completion snapshot；复用时缺失 / drift 的 classification / snapshot 字段 → HARD。Item 12 non-canonical proposal envelope（无 assessment_id / assessment_version / review）；`fatal_review` 是 run result 上的独立 module-local record（required / status POTENTIAL_FATAL_PATTERN / evidence_ids / cohort_ids / coverage_class / basis refs / landscape_as_of / crc_coverage_search_scope），只有 accepted run 才 actionable。Item 13 machine acceptance（identity / source / EP reuse / completion-audit snapshot parity；only frozen classes；transcript 永不 above INDIRECT_STRONG；protein without malignant attribution 永不 DIRECT；每个 QUALIFIED / negative-coverage class 有 auditable basis；mandatory CRC coverage landscape 完整、无 early one-cohort grade；Direction×Strength == item-06 truth table；WEAK-only → `INCONCLUSIVE/UNKNOWN` 零 refs；fatal_review 至多 POTENTIAL_FATAL_PATTERN 且不是 proposal 字段；无 numeric·ranking score / cohort-size·%-positive·H-score·heterogeneity 阈值；无 TGT-03·TGT-04·TGT-05 结论；无 PUBLIC_FATAL_SIGNAL_ESTABLISHED·KILL·HOLD·Decision）；HARD identity / provenance / completion-consistency / classification-qualification failure 拒**整个** run —— 绝不降级成 accepted `UNKNOWN`；incomplete public CRC coverage search 的 `UNKNOWN` **不是** integrity failure。Item 14 human review surface + human-only judgements。Item 15 weak-only bulk/pan-cancer → UNKNOWN；incomplete search → UNKNOWN；high-quality nondirectional → graded INCONCLUSIVE；incompatible claims → CONFLICTING；qualified rare-highly-heterogeneous multi-cohort → NEGATIVE（不自动 CONFLICTING）。Item 16 E7-7 完整-before-grade stop rule。Item 17 两条路：HUMAN_APPROVED CandidateGateAssessment → MatrixView / decision layer / TGT-03 as context only（永不 via generic CRC linkage）；module-local fatal_review → human Gate review / GateSet fatal policy；禁止 fatal_review → Module KILL。 |
| E7-9 | synthetic construction acceptance 测试，fixtures `TARGET_A` / `CRC_COHORT_A/B/C` / `STROMA` / `IMMUNE`，不固化真实 target / dataset。E7 交付 parity / shape / boundary 测试（ruling 里列的 ~40 个 synthetic run-level 场景属 PR E8 的 implementation acceptance suite）。见 §四。 |

## 三、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/gate_modules/tgt02_indication_specific_malignant_cell_coverage.yaml`（新） | 冻结的 MOD-TGT02 construction contract，17 项 acceptance checklist。items 01/02 identity；03/05/07/08 与冻结 PR D TGT-02 逐字 parity + 07 `inference_guard` 逐字；04 `evidence_required_from_pr_d` + `admissible`（含 ladder classes）+ `not_admissible_into_this_gate`（排除另外七个 Gate）；06 `direction_definitions` + `strength_is_the_highest_qualifying_evidence_class`（无 two-axis）+ `rare_or_highly_heterogeneous_is_upstream_qualified` + `frozen_truth_table` + `weak_vs_unknown` + `graded_inconclusive_vs_unknown` + `conflicting_vs_qualified_heterogeneity`；08 `potential_fatal_signal`（逐字）+ `framing` + `single_cohort_vs_cross_cohort_pattern` + `across_cohorts_is_plural_cohorts_logic_not_a_new_threshold` + `machine_detection_criteria` + `human_review_reserved` + `machine_output_is_only_a_potential_pattern`；09 `source_classes` / `source_authority_rules`（hard locks）/ `crc_cohort_coverage_landscape`（四个 mandatory components + typed record）/ `no_universal_threshold`；10-17 E2/E4/E6 runtime genes + `fatal_review` 字段清单 + machine acceptance 清单 + stop rule + handoff。`deferred_to_pr_e8_plus` + `repository_policy`（全 forbidden + `migration_pending: remains`）。 |
| `docs/gate_modules/TGT-02_Indication_Specific_Malignant_Cell_Coverage.md`（新） | human-readable 施工图：17-row 表 + 三条 headline blockquote（bidirectional coverage gate；NEGATIVE ≠ fatal ≠ KILL；one pretty cohort ≠ population-level answer）+ frozen normalized-observation / `CrcCohortCoverageCompletion` 概念 shape。 |
| `tests/test_tgt02_module_construction_contract.py`（新，49 tests） | 见 §四。 |
| `manifests/runtime_migration_pr_e7_manifest.yaml`（新） | `chatgpt_review: PENDING`、9 个 `scoping_decisions` E7-1…E7-9、3 条 headline conclusion、boundary 声明、artifact 清单。 |
| `docs/handoff/2026-08-30-runtime-migration-pr-e7.zh-CN.md`（新） | 本文件。 |

## 四、测试（`tests/test_tgt02_module_construction_contract.py`，49 tests）

- `ContractShapeTests`（5）：version / migration block（pr `runtime_migration_pr_e7`、
  next `runtime_migration_pr_e8`、order 含 `TGT-08 -> TGT-02 -> TGT-03`）；
  template provenance 复用 E1；kernel invariant（`src/` 永不 import
  `gate_modules/`；bidirectional coverage gate；NEGATIVE 不是 fatal flag 不是
  KILL；`POTENTIAL_FATAL_PATTERN`；never PASSES never KILLs）；17 项 checklist
  齐全有序；checklist keys 与 E1 模板一致。
- `IdentityTests`（3）：item 01 gate identity；item 02 `MOD-TGT02` /
  `module_implementation_version: 0.0.0` / rule 提「PR E8 builds it」。
- `VerbatimFromPrDTests`（8）：item 03 gate_question normalized-equality；item 05
  ladder + ceiling parity；item 07 allowed / forbidden parity；item 07
  `inference_guard` 逐字；item 08 `potential_fatal_signal` parity；item 04
  `evidence_required_from_pr_d` parity + admissible ⊇ ladder classes ⊇
  evidence_required；item 04 排除另外七个 Gate；PR D `unknown_behavior` ==
  「only bulk rna available -> unknown, not a pass.」。
- `BidirectionalDirectionTests`（8）：Direction relative to Gate question；
  NEGATIVE reachable 且是 scientific finding（truth table 行）；strength =
  highest qualifying class 且无 two-axis；rare / highly heterogeneous
  upstream-qualified 从不计算；WEAK-only → `INCONCLUSIVE/UNKNOWN` 不是
  `/WEAK`；graded INCONCLUSIVE vs UNKNOWN 严格区分；CONFLICTING 不自动等同
  heterogeneity；ladder rule 写死 transcript never exceeds INDIRECT_STRONG。
- `FatalBoundaryTests`（5）：single cohort ≠ cross-cohort fatal pattern；
  「across cohorts」= plural logic 不是阈值；machine 至多
  `POTENTIAL_FATAL_PATTERN`（never PUBLIC_FATAL_SIGNAL_ESTABLISHED / KILL /
  HOLD / Decision；`fatal_gate_policy_ref` 独立）；fatal rule 无 numeric /
  %-positive / H-score / heterogeneity 阈值；human_review_reserved 含
  independence + justification + fatal policy。
- `CompletionAndSourcePlanTests`（4）：regime `PUBLIC_HYBRID` / 当前
  `PUBLIC_ONLY` / 不接 provider；source hard locks（transcript ≠ protein、
  bulk/pan-cancer 永不 malignant-cell attributed、stroma/immune ≠ malignant、
  normal-vs-tumor ≠ therapeutic index、weak-only 永不 above ceiling）；四个
  mandatory components + typed `CrcCohortCoverageCompletion`（非第七个 core
  object）；`no_universal_threshold`。
- `RuntimeGeneAndProposalTests`（8）：item 10 single authoritative target /
  no implicit context / declared search scope；item 11 Gate-neutral + exact
  reuse + audit snapshot + 「may_not_say」清单；item 12 non-canonical envelope
  never carries assessment_id / review.status / fatal flag + `fatal_review`
  字段（cohort_ids、expression_pattern_basis_refs）+ 只在 accepted run
  actionable；item 13 machine acceptance hard locks（completion↔audit snapshot
  parity、transcript 永不 above INDIRECT_STRONG、protein without malignant
  attribution 永不 DIRECT、WEAK-only → `INCONCLUSIVE/UNKNOWN` 零 refs、无
  numeric·ranking·阈值、无 TGT-03/04/05 结论、无 PUBLIC_FATAL_SIGNAL_ESTABLISHED /
  KILL / HOLD / Decision、HARD failure 拒整个 run 不降级 UNKNOWN）；item 15
  WEAK / incomplete → UNKNOWN + EXPERIMENT_REQUIRED 窄触发 +「scientific NEGATIVE
  never a fatal flag never a KILL」；item 16 never stops on first negative
  cohort；item 17 never KILL / never discharges TGT-03 / never grades before
  landscape complete。
- `NoImplementationInPrE7Tests`（6）：repository_policy 全 forbidden +
  `migration_pending: remains`；`gate_modules/tgt02_...` 目录不存在；TGT-02
  binding 仍 `0.0.0`、TGT-01/05/08 `1.0.0`、`per_gate_primary_modules` deferred；
  deferred 块指名 E8 实现 + `CrcCohortCoverageCompletion`；`gate_modules/` 下
  只允许 tgt01/tgt05/tgt08 的 `.py`；合约无 numeric threshold（`> 2` 是
  plural-cohorts 逻辑不是阈值）。
- `DrawingTests`（4）：drawing 存在、指名 MOD-TGT02 / PR E7 / `MIGRATION_PENDING`
  remains；17 行齐全；「a TGT-02 `NEGATIVE` is not a fatal flag and not a `KILL`」
  / bidirectional / one pretty cohort ≠ population-level answer；冻结
  `CrcCohortCoverageCompletion` + no E6-style two mandatory axes +
  `expression_pattern_basis` + `EXPERIMENT_REQUIRED`。

## 五、明确未改 / 未做

- **未写**任何实现代码 / provider / adapter / retrieval / runner /
  EvidencePackage·proposal·fatal-detector runtime；**未上网 / 未连 dataset**；
  **无** numeric / ranking score；**无** cohort-size / %-positive / H-score /
  heterogeneity 阈值；**未建** generic GateModule framework / abstract base
  class。
- **未改** PR A / B / C 合同；**未改** PR D 的 TGT-02 Gate science；**未重构**
  MOD-TGT01 / MOD-TGT05 / MOD-TGT08（代码未动，binding 仍 `1.0.0`）。
- **未解除** `MIGRATION_PENDING`（8 个 primary Module 已建 3 个：TGT-01、TGT-05、
  TGT-08；TGT-02 施工合同已交付，Module 未建 `0.0.0`）。无新依赖（仍只 PyYAML）。
- 其余 4 个 TGT primary Module（TGT-03 → 04 → 06 → 07）属后续 PR。

## 六、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_tgt02_module_construction_contract.py' -v
# -> Ran 49 tests ... OK
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 1102 tests ... 1 pre-existing local FAIL
#    (test_assetgenos_modules.test_migration_does_not_include_legacy_runtime_state:
#     它物理扫描 genmodules/*/__pycache__，本机偶发落盘；CI 干净 checkout 上 GREEN。
#     E6 approval 时基线 1053，E7 +49。)
git diff --check                              # clean
bash scripts/verify_repository_boundary.sh    # 干净 tracked-tree 上合规（未跟踪的 pipelines/ 等是既有噪音）
python3 -c "import yaml; yaml.safe_load(open('src/contracts/gate_modules/tgt02_indication_specific_malignant_cell_coverage.yaml'))"  # 结构合法
```

## 七、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入）。审核重点：9 个 scoping 决策 E7-1…E7-9 是否逐条落实；3 条 headline
  conclusion 是否成立（NEGATIVE 可达且是 scientific finding 不是 KILL；
  fatal 只是 machine-local trigger；typed completion 阻止 one-cohort grade）；
  items 03/05/07/08 是否逐字 parity + `inference_guard` 逐字；bidirectional
  Direction 与 frozen truth table；「rare / highly heterogeneous」upstream-qualified
  never computed；WEAK-only → `INCONCLUSIVE/UNKNOWN`（不是 `/WEAK`）；graded
  INCONCLUSIVE vs UNKNOWN；CONFLICTING vs heterogeneity；transcript ≠ protein、
  stroma/immune ≠ malignant、bulk/pan-cancer = WEAK、normal-vs-tumor ≠ TI 的
  hard locks；`CrcCohortCoverageCompletion` + **无** E6-style two-axis rule；
  `EXPERIMENT_REQUIRED` 窄触发（与 TGT-08 不同）；E2/E4/E6 gene 继承；无
  implementation / framework / MOD-TGT01·05·08 改动；binding 仍 `0.0.0`；
  `MIGRATION_PENDING` 保持。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一
  对话复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #111 / #113 / #115 / #117 先例）。

## 八、后续（未启动）

- **PR E8 = MOD-TGT02@1.0.0 deterministic implementation** —— 新建顶层
  `gate_modules/tgt02_indication_specific_malignant_cell_coverage/`，严格实现本
  合同 + E7-1…E7-9，加 `CrcCohortCoverageCompletion` typed record 与
  `fatal_review` detector，并把 TGT-02 `primary_module_version` `0.0.0 → 1.0.0`。
  需用户 go-ahead。
- 真实 provider / adapter（GEO / HPA / CPTAC / single-cell / spatial / TMA
  repositories）—— 属外部 workspace，各自需 go-ahead。
- 逐 Gate 施工图 + 实现，按 `TGT-03 → 04 → 06 → 07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
