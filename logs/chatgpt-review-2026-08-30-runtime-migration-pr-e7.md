# ChatGPT 审核记录：Runtime Migration PR E7 —— TGT-02 / MOD-TGT02 Construction Contract

- 日期：`2026-08-30`
- PR：#118 `task_20260829_runtime-migration-pr-e7`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`a1d00b1`（第三轮修订 —— 治理记录 + PR body 同步）
- Merge 提交：`9ec30e6`（`Merge pull request #118 from leezx/task_20260829_runtime-migration-pr-e7`）
- 结论：**APPROVE @ `a1d00b1`**。「APPROVE —— TGT-02 construction contract 可以
  merge。下一步按既定流程进入 PR E8 = MOD-TGT02@1.0.0 deterministic
  implementation。」GitHub connector 每轮均 `403 Resource not accessible by
  integration`，REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；
  `AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e7-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 / #105 / #107 / #109 / #111 / #113 /
#115 / #117 先例。本 PR 同时把 `manifests/runtime_migration_pr_e7_manifest.yaml`
补成 approved。不改 PR E7 的施工合同、drawing 或测试内容。

## 9 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板，E7-1…E7-9）

见 `manifests/runtime_migration_pr_e7_manifest.yaml` 的 `scoping_decisions`
与 `three_headline_conclusions` / `owns_boundary_one_liner`，以及
`docs/handoff/2026-08-30-runtime-migration-pr-e7.zh-CN.md` §一 / §二。要点：

- **E7-1** 完整施工合同，design-only。10 项禁止：`gate_modules/tgt02.../`
  runtime、provider / adapter、GEO·HPA·CPTAC·scRNA·spatial retrieval、
  EvidencePackage runtime、proposal runtime、fatal detector runtime、
  numeric·ranking score、cohort-size·%-positive·H-score·heterogeneity cutoff、
  generic GateModule framework·ABC、新依赖·外部数据、MOD-TGT01·MOD-TGT05·
  MOD-TGT08 refactor。MOD-TGT02 `primary_module_version` 仍 `0.0.0`；其它三个
  `1.0.0`；`MIGRATION_PENDING` 保持。Module 在 PR E8 才实现，且只在本合同
  APPROVE 之后。
- **E7-2** 17 项模板原样继承 E1（E2 / E4 / E6 已验证）；items **03 / 05 / 07 /
  08** 与冻结 PR D `crc_adc_target_gateset.yaml:TGT-02` 做 normalized-equality
  parity；item **04** 对 `evidence_required` + ladder union 做 derived parity；
  `inference_guard` 逐字 pin：「EVGAP-02 primarily contributes TGT-02; generic
  CRC linkage does NOT discharge TGT-03.」
- **E7-3** Direction × Strength —— TGT-02 是 **bidirectional scientific
  coverage gate**。`POSITIVE` / `NEGATIVE`（absent, or rare and highly
  heterogeneous）/ `CONFLICTING` / `INCONCLUSIVE`。`DIRECT` 需 protein-level +
  CRC + malignant-cell attributed + adequately-powered cohort qualification +
  completed audited landscape。「rare / highly heterogeneous」**不由 Module 从
  %/H-score/n 计算** —— 来自 auditable upstream qualification（`expression_pattern`
  ∈ {ABSENT, RARE_HIGHLY_HETEROGENEOUS}，`expression_pattern_basis` ∈
  {SOURCE_REPORTED, HUMAN_REVIEWED_NORMALIZATION}）；缺失 / drift 的 basis 是
  HARD integrity failure。`INDIRECT_STRONG` = qualifying sc / spatial
  malignant-compartment 或 CRC TMA transcript+protein concordance；transcript-only
  永不升 DIRECT，quantity 永不提 ceiling。**WEAK-only public landscape →
  `INCONCLUSIVE / UNKNOWN`，不是 `INCONCLUSIVE / WEAK`**（TGT-02-specific）。
  overall Strength = **最强 qualifying evidence class**，**无** E6-style
  two-axis weaker-ceiling rule。valid audited multi-cohort 把 coverage 定性为
  RARE_HIGHLY_HETEROGENEOUS → `NEGATIVE`，不自动 `CONFLICTING`。
- **E7-4** fatal —— machine-local `fatal_review`，绝不直接 KILL。PR D fatal =
  「protein-level evidence of absent, or rare and highly heterogeneous, target
  expression in CRC malignant cells across cohorts」。machine 至多在满足以下条件
  时 surface candidate pattern：protein-level observations，每个带 CRC
  malignant-cell attribution、`QUALIFIED` cohort_adequacy_status + auditable
  basis、negative coverage class（ABSENT / RARE_HIGHLY_HETEROGENEOUS）+
  auditable basis，且在 completed audited landscape 上，且 cross-cohort support
  —— **at least two independent cohort identities**（或一个 declared
  multi-cohort analysis 带 at least two auditable cohort_ids）。「across
  cohorts」是 plural-cohorts 逻辑（at least two，**不是** "more than two" /
  "> 2"），不是新阈值。machine 永远至多 `POTENTIAL_FATAL_PATTERN`；永不
  `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / canonical fatal flag / KILL / HOLD /
  Decision。cohort adequacy basis 是否可信、cohorts 是否真正独立、
  rare-highly-heterogeneous 是否成立、assay/platform 差异是否解释 convergence、
  是否满足 GateSet fatal policy —— 全部 human-only。
- **E7-5** typed `CrcCohortCoverageCompletion`（PR E8 module-local frozen
  dataclass，**非**第七个 core object）：`attempted` / `landscape_as_of` /
  `search_scope` / `sources_searched` / 5 个 per-component
  `*_search_complete` / `unresolved_items` / `qualifying_protein_cohort_ids` /
  `qualifying_indirect_cohort_ids` / `audit_observation_id`。**无 E6-style 两个
  mandatory axes**。completion ↔ `SEARCH_COMPLETION_AUDIT` snapshot parity（E6
  gene）为 E8 冻结；缺失 / drift → HARD reject。normalized observation 概念字段
  在 drawing 里冻结（`observation_kind` 7 值、`molecular_layer`、
  `malignant_cell_attribution` + basis、`cohort_adequacy_status` + basis、
  `expression_pattern` + basis 等）。provider 只给事实，不给 rung / direction /
  pass-fail。
- **E7-6** source-plan hard locks。`DIRECT` = validated CRC IHC / quantitative
  proteomics / validated multiplex IF in annotated malignant cells across an
  adequately powered CRC cohort。**永不** scRNA / spatial RNA / bulk RNA →
  DIRECT；**永不** protein without malignant attribution → DIRECT。
  `INDIRECT_STRONG` = scRNA / spatial RNA + malignant compartment resolved，或
  CRC TMA transcript+protein concordance + malignant-cell attribution。`WEAK` =
  bulk CRC RNA without malignant deconvolution，或 pan-cancer unresolved to
  CRC。compartment hard lock：stroma / immune / mixed-tissue expression ≠ CRC
  malignant-cell expression（可作 contextual observation，**不** discharge
  TGT-02）。transcript ≠ protein（醒目）。matched normal-vs-tumor 在 PR D
  evidence_required 里，但**不得**误用成「normal low + tumor high → favorable
  therapeutic index」（TGT-05 才管 normal-tissue liability）。PUBLIC_ONLY 路径。
- **E7-7** stop rule + `EXPERIMENT_REQUIRED`。mandatory declared component 未
  complete → `INCONCLUSIVE / UNKNOWN`，不在漂亮 intermediate result 上早 grade
  （这正是 completion state 的用途）。public search complete → strongest
  qualifying evidence。TGT-02 **可以且应该**用 `EXPERIMENT_REQUIRED`，但**窄**
  —— enumerated public CRC coverage source space 完成 / 耗尽 **AND** unresolved
  Gate question 需要 NEW malignant-cell-resolved protein / adequately powered
  cohort measurement。known-but-unfetched public dataset / incomplete public
  cohort search 是 `PUBLIC_RESOLVABLE`；access / annotation 当前阻碍解析的
  existing source 是 `CURRENTLY_UNRESOLVABLE`。potential-fatal trigger 只在
  cohort coverage completeness 满足**之后**才停止追更弱的 bulk / pan-cancer
  proxy —— Module 绝不在第一个 negative cohort 上停。
- **E7-8** items 10–17 直接继承 E2 / E4 / E6 runtime genes —— Item 10
  instantiation pins / context / version / PUBLIC_ONLY / run_id / code_commit /
  `landscape_as_of` / declared CRC coverage search scope / existing evidence
  ids，无第二个 drift-prone target 参数、无隐式 default context；Item 11 atomic
  Gate-neutral immutable-by-ID EvidencePackage + canonical SourceIndex
  provenance + exact canonical reuse，EP 可陈述 neutral empirical fact 但绝不
  「passes TGT-02 / has adequate coverage / is fatal / should be killed」，
  `SEARCH_COMPLETION_AUDIT` EP 带结构化 completion snapshot，reuse 时缺 /
  drift 的 classification / snapshot 字段 → HARD；Item 12 non-canonical
  proposal envelope（无 assessment_id / assessment_version / review），
  `fatal_review` 是 run result 上独立的 module-local record，只有 accepted run
  才 actionable；Item 13 machine acceptance（identity / source / EP reuse /
  completion-audit snapshot parity；只 frozen classes；transcript 永不 >
  INDIRECT_STRONG；protein without malignant attribution 永不 DIRECT；每个
  QUALIFIED / negative-coverage class 有 auditable basis；mandatory CRC
  coverage landscape complete，无早 one-cohort grade；Direction × Strength ==
  item-06 truth table；WEAK-only → `INCONCLUSIVE / UNKNOWN` 零 evidence_refs；
  `fatal_review` 至多 `POTENTIAL_FATAL_PATTERN` 且不在 proposal 上；无 numeric /
  ranking score，无 cohort-size / %-positive / H-score / heterogeneity
  threshold；无 TGT-03 / 04 / 05 conclusion；无 `PUBLIC_FATAL_SIGNAL_ESTABLISHED`
  / KILL / HOLD / Decision；HARD identity / provenance / completion-consistency
  / classification-qualification 失败 → 拒**整个 run**，绝不降级成 accepted
  UNKNOWN；genuinely incomplete public search 的 UNKNOWN **不是** integrity
  failure）；Item 14 human review surface + human-only judgements；Item 15
  weak-only / incomplete → UNKNOWN，high-quality nondirectional → graded
  INCONCLUSIVE，incompatible claims → CONFLICTING，qualified
  rare-highly-heterogeneous multi-cohort → NEGATIVE；Item 16 E7-7
  completion-before-grade stop rule；Item 17 两条路由（HUMAN_APPROVED
  CandidateGateAssessment → MatrixView / decision layer / TGT-03 只作 context，
  绝不 via generic CRC linkage；module-local `fatal_review` → human Gate review
  / GateSet fatal policy），禁止 `fatal_review` → Module KILL。
- **E7-9** synthetic construction acceptance tests，fixtures `TARGET_A` /
  `CRC_COHORT_A` / `_B` / `_C` / `STROMA` / `IMMUNE`，无真实 target 或 dataset。
  E7 只交 parity / shape / boundary 测试（ruling 里列的 ~40 个 synthetic
  run-level 场景是 PR E8 implementation acceptance suite 的）。

3 条 headline conclusion（审核方原话）：

1. **TGT-02 NEGATIVE is reachable and a genuine SCIENTIFIC NEGATIVE** ——
   *"current admissible evidence shows refractory-mCRC malignant cells lack
   adequate population-level target expression coverage"*. 不是 TGT-08 的
   commercial NEGATIVE，也不是 TGT-05 的 inverted liability。
2. **NEGATIVE ≠ fatal ≠ KILL.** `NEGATIVE / DIRECT` 可以出现，但只有满足 PR D
   fatal condition 的 cross-cohort protein-level pattern 才进入 machine-local
   `fatal_review = POTENTIAL_FATAL_PATTERN`；Module 永不输出 canonical fatal
   flag / KILL；Candidate-level consequence 由 GateSet fatal policy 决定。
3. **TGT-02 needs a typed `CrcCohortCoverageCompletion`**（E6-style gene，科学
   语义不同）：只有 completed / audited CRC coverage search 才能把单个
   observation 聚合成 cohort-level Gate judgement —— 一个漂亮 cohort 绝不是
   population-level 答案。

## 四轮历史（初次提交 + 3 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `61c2db9`（首版：TGT-02 construction contract + drawing + 49 tests，全量 1102） | `REQUEST_CHANGES`。**整体设计全部 PASS**（design-only scope、E1 17-item template、03/05/07/08 PR D parity + `inference_guard` verbatim、bidirectional NEGATIVE scientific semantics、NEGATIVE ≠ fatal ≠ KILL、typed `CrcCohortCoverageCompletion` + no-two-axis rule、WEAK-only → `INCONCLUSIVE / UNKNOWN`、narrow `EXPERIMENT_REQUIRED`、source hard locks、E2/E4/E6 runtime-gene 继承、MOD-TGT02 binding `0.0.0`、`MIGRATION_PENDING`）。4 个 narrow blocker。 |
| 2 | `8876533`（第一轮修订，51 tests / 全量 1104） | `REQUEST_CHANGES`。4 个 blocker 在 machine contract / drawing / tests 里**全部确认关闭**。唯一残余：3 个被 git 跟踪的治理产物仍以「当前规则」口吻保留旧的 `> 2` / `MORE THAN TWO` 文案。 |
| 3 | `a1d00b1`（第二轮修订，51 tests / 全量 1104） | `REQUEST_CHANGES`。governance-record 已同步；唯一残余：PR #118 **description body** 里 "Other frozen rulings" 还写 `> 2`，测试数字还是旧的 `49` / `1102`。 |
| 4 | `a1d00b1`（第三轮 —— 仅 PR body edit，无新 commit） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 4 个 blocker（`61c2db9` → `8876533`）

不改 PR D、NEGATIVE/fatal 总体架构、completion concept、`EXPERIMENT_REQUIRED`、
source plan、MOD-TGT01 / MOD-TGT05 / MOD-TGT08、binding、`MIGRATION_PENDING`。

### Blocker 1 —— "qualifying" 不是 rung-specific

item 06 `frozen_truth_table.note` 把 "qualifying" 定义成 protein-level /
malignant-cell attributed / CRC-specific，与它自己的
`qualifying_sc_spatial_or_tma_concordance` 行（sc / spatial 不是 protein-level）
自相矛盾，让 E8 无法判断 sc / spatial 到底算不算 qualifying。**修：** 加 item 06
`qualifying_is_rung_specific` —— 一个 qualifying observation 满足其**适用的**
Evidence-Ladder rung 的 frozen admissibility 并属于 completed landscape；DIRECT
额外要求 protein-level + CRC + malignant attribution + QUALIFIED cohort adequacy
status，INDIRECT_STRONG 额外要求 sc / spatial malignant-compartment 或 TMA
transcript+protein concordance predicates；sc / spatial 可以是 qualifying
INDIRECT_STRONG observation 而不必是 protein-level。truth-table note 引用它。
+1 regression。

### Blocker 2 —— "across cohorts" 被写成 `> 2` / MORE THAN TWO（隐式 ≥ 3 阈值）

冻结的 plural 逻辑是 **≥ 2**（一个 cohort 不是 cross-cohort，两个独立 qualifying
cohort 就是 cross-cohort candidate pattern）。**修：** 全局改成 "at least two
independent [qualifying] cohort identities"，覆盖 item 08
（`across_cohorts_is_plural_cohorts_logic_not_a_new_threshold`、
`machine_detection_criteria`、`single_cohort_vs_cross_cohort_pattern`）、item 12
`fatal_review` fields + `required_is_true_iff`、item 13、drawing；合同明确写出
「NOT "more than two" / "> 2"」。regression 断言 "at least two"、无 "more than
two"、合同里无 "> 2 independent"。

### Blocker 3 —— observation-level evidence class 与 final Gate Direction 混写

item 08 还写「a single negative protein cohort IS "DIRECT NEGATIVE evidence"」，
把 observation class 与 final Gate Direction 混写。**修：** 加 item 06
`direction_is_an_aggregate_not_an_observation` —— 单个 observation 永不是
Direction；classifier 只产 Gate-neutral、rung-classed、direction-SUPPORTING
observation；aggregate 只在 **completed audited CRC coverage landscape** 上产
proposed Direction × Strength，未完成前 final Assessment 仍 `INCONCLUSIVE /
UNKNOWN`。item 08 framing + `single_cohort_vs_cross_cohort_pattern` 改成
「DIRECT-class, NEGATIVE-supporting observation —— NOT yet a NEGATIVE / DIRECT
proposal, NOT fatal」。加 3 条 truth-table 行：single DIRECT-class negative
cohort + landscape incomplete → `INCONCLUSIVE / UNKNOWN`；completed audited
landscape（highest rung DIRECT、material negative、no unresolved incompatible
positive）→ `NEGATIVE / DIRECT`；completed landscape 有 incompatible positive +
negative 且无 qualified heterogeneity pattern → `CONFLICTING / DIRECT`。
+1 regression。

### Blocker 4 —— item 04 derived parity 只是 superset 检查

item 04 测试只检查每个 ladder / `evidence_required` class ∈ admissible，新的
unfrozen class 可以偷加而测试仍绿。**修：** 改成
`set(item04.admissible) == set(evidence_required ∪ DIRECT ∪ INDIRECT_STRONG ∪
WEAK)`。

第一轮修订后 `test_tgt02_module_construction_contract.py` 51 tests（+2）；全量
1104。

## 第二轮 REQUEST_CHANGES（`8876533` → `a1d00b1`）—— 仅治理记录同步

审核方确认 4 个 blocker 在 machine contract / drawing / tests 里**全部关闭**，
不要求任何 science / scope / architecture 改动。唯一 blocker：3 个被 git 跟踪的
治理产物仍以「当前规则」口吻保留第一轮的 `> 2` / `MORE THAN TWO` 文案 ——
`manifests/runtime_migration_pr_e7_manifest.yaml` 的 `scoping_decisions.E7-4`、
`docs/handoff/2026-08-30-runtime-migration-pr-e7.zh-CN.md` 的 E7-4 scoping 行、
`logs/worklog.md` 的 E7 首版条目，以及一行 stale test comment。**修：** 全部
同步成 "at least two independent cohort identities"，并补
「plural-cohorts logic（at least two，NOT "more than two" / "> 2"）」注释；
明确标注「round-1 old bug」的历史记录（worklog 第一轮修订条目、blocker-2
regression）按审核方许可保留原样。无任何测试断言 / test-science 改动。manifest
增 `review_round_2` block + `review_rounds: 2`。

## 第三轮 REQUEST_CHANGES（`a1d00b1`，无新 commit）—— 仅 PR body 同步

审核方确认 tracked governance artifacts 已同步正确、contract-head CI success。
唯一残余是纯 PR #118 **description body** metadata：

- "Other frozen rulings" 段仍写 `"across cohorts" = plural-cohorts logic (> 2
  independent cohort identities)` → 改成 `at least two independent cohort
  identities（explicitly NOT "> 2"）`。
- 测试数字仍是旧的 `49 tests` / `1102 full suite` → 同步为 `51 contract tests`
  / `1104 full suite`。

`gh pr edit 118 --body` 完成，不动任何文件或 science。

## 第四轮 APPROVE（`a1d00b1`）

审核方逐条复核（exact-HEAD `a1d00b1e…` CI `verify (3.11)` / `verify (3.12)` 均
`success`）：

- 第一轮 4 个 substantive blocker 继续保持关闭：qualifying 已 rung-specific；
  "across cohorts" 已是 at-least-two（明确不是 `> 2`）；Direction 是 completed
  audited landscape 上的 aggregate，绝非单个 observation；item-04 derived
  parity 是 exact set equality。
- 第二轮 governance-record blocker 已关闭：manifest E7-4 / handoff E7-4 已同步为
  "AT LEAST TWO"，worklog / test comment 同步；历史「round-1 old bug」记录保留。
- 第三轮 PR-body blocker 已关闭：PR #118 body 现在写 "at least two independent
  cohort identities, explicitly NOT > 2"，contract tests = 51，full suite =
  1104。
- 没有新问题。尤其没有理由再动 frozen PR D TGT-02 contract / TGT-02 Gate
  science / NEGATIVE-vs-fatal 架构 / `CrcCohortCoverageCompletion` concept /
  no-two-axis strength rule / source hard locks / `EXPERIMENT_REQUIRED` 边界 /
  E2·E4·E6 runtime-gene 继承 / MOD-TGT01·MOD-TGT05·MOD-TGT08 / MOD-TGT02
  binding `0.0.0` / `MIGRATION_PENDING` / provider·IO·framework boundary。

**APPROVE —— TGT-02 construction contract 可以 merge。** 下一步按既定流程进入
PR E8 = MOD-TGT02@1.0.0 deterministic implementation（需要各自的 go-ahead）。

CI（GitHub Actions `verify`，python 3.11 + 3.12）对 `61c2db9` / `8876533` /
`a1d00b1` 均 `success`（含 unit tests / repository boundary /
no-bytecode-artifacts / working-tree-clean）。全量 `unittest discover`：
`test_tgt02_module_construction_contract.py` 首版 49 → 第一轮修订后 51（+2
blocker regression）；本地全量 1104。

GitHub connector 每轮都返回 `403 Resource not accessible by integration`，
REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
为 authoritative。

## 状态

8 个 primary Module 施工合同已 APPROVE 4 个：MOD-TGT01（E1）、MOD-TGT05（E3）、
MOD-TGT08（E5）、MOD-TGT02（E7）。已实现 3 个：MOD-TGT01@1.0.0（E2）、
MOD-TGT05@1.0.0（E4）、MOD-TGT08@1.0.0（E6）。MOD-TGT02 `primary_module_version`
仍 `0.0.0`（PR E8 bump 到 `1.0.0`）。其余四个 gate（TGT-03 → TGT-04 → TGT-06 →
TGT-07）属后续 PR。`MIGRATION_PENDING` 保持。真实 provider / adapter 与外部
workspace calibration 各自需 go-ahead。
