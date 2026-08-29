# ChatGPT 审核记录：Runtime Migration PR E4 —— MOD-TGT05@1.0.0 实现

- 日期：`2026-08-29`
- PR：#112 `task_20260829_runtime-migration-pr-e4`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`bbc630f`（第一轮修订）
- Merge 提交：`b8518d8`（`Merge pull request #112 from leezx/task_20260829_runtime-migration-pr-e4`）
- 结论：**APPROVE @ `bbc630f`**。「MOD-TGT05@1.0.0 可以视为 frozen E3 construction
  contract 的合格 deterministic implementation。本轮聊天结论为 authoritative
  approval。」下一步（真实 provider / adapter + 外部 workspace calibration，或
  下一个 TGT 施工图）各自需要用户的 go-ahead。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e4-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 / #105 / #107 / #109 / #111 先例。本 PR
同时把 `manifests/runtime_migration_pr_e4_manifest.yaml` 补成 approved。不改 PR E4
的实现代码或测试内容。

## 8 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

| # | 决策 |
|---|---|
| E4-1 | 完整 deterministic MOD-TGT05 实现（像 E2 一样是完整 Gate-specific scientific core）。10 文件独立包；`module_version 1.0.0`；最小 binding 更新（TGT-05 `primary_module_version` `0.0.0 → 1.0.0`，`built_module_versions` 加 TGT-05）；冻结的 E3 合同正文一字不改；**不建** generic GateModule framework / abstract base class；**不重构** MOD-TGT01。 |
| E4-2 | 一个 `Tgt05LiabilityProviderPort`；每条 record 带 `evidence_function` ∈ {`LIABILITY_RUNG_EVIDENCE` (A)、`ATTRIBUTION_ADJUDICATION` (B)、`COVERAGE_CONTEXT` (C)}；`NormalizedLiabilityRecord` 只装事实；provider 永不返回 rung 或 direction；N/A 用显式空值。 |
| E4-3 | classification 逐字实现 E3 item-06 truth table；validated human protein atlas NOT_DETECTED → `COVERAGE_CONTEXT`（不是 WEAK、不是 NEGATIVE）；scRNA / RNA-only → WEAK；rodent-only → WEAK；aggregation undisputed DIRECT → `POSITIVE/DIRECT` → else undisputed INDIRECT_STRONG → `POSITIVE/INDIRECT_STRONG` → else WEAK-only → `INCONCLUSIVE/WEAK` → else `INCONCLUSIVE/UNKNOWN`；established liability + coverage gap → 仍 `POSITIVE`（gap → `critical_unknowns`）；**永不 `NEGATIVE`/safe**。 |
| E4-4 | `CONFLICTING` 只按 `liability_event_id`；disputed event = 同一 event id 上一个 admissible source SUPPORTS + 另一个 admissible source REFUTES，且该 event 不是 undisputed established liability；无其它独立 undisputed strong liability → `CONFLICTING`（Strength = disputed obs 可达最强 rung）；有独立 established liability → 整体 `POSITIVE` + dispute → `critical_unknowns`；「ADC-A 有毒、ADC-B 报告没毒」既不是 conflict 也不产 `CONTRADICTING` ref。 |
| E4-5 | `fatal_review` 是独立 machine-local run 输出；`status` 单值 `POTENTIAL_FATAL_PATTERN`（无第二个 status）；`required=true` 当且仅当 ≥2 个不同 `program_id` 的同靶点 ADC clinical toxicity observation，每个都有 `construct_fingerprint` + disclosed `target_attribution_basis` + `SUPPORTS_TARGET_ATTRIBUTION` + EXACT normalized `affected_tissue` key + EXACT `toxicity_phenotype_key`；无 embeddings / LLM / ontology / fuzzy；同一 program 两篇文献 = 一个 program。 |
| E4-6 | `Tgt05SweepCompletionRecord` = 5 sweep 布尔 + per-vital-organ `{search_complete, coverage_result ∈ (ADMISSIBLE_PROTEIN_DATA_FOUND, PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA, NOT_YET_COMPLETE)}`（六器官）。Path A（`fatal_review.required` → provisional stop；ADC construct inventory + attribution sweep 仍须完成）；Path B（存在 DIRECT ADC clinical liability 且 `fatal_review.required==false` → 要求 construct inventory + attribution sweep）；Path C（无 DIRECT ADC clinical liability → 要求 non-ADC + NHP + RNA-supporting + 六器官 protein coverage 全完成；exhausted organ → `critical_unknown` = `EXPERIMENT_REQUIRED`）。 |
| E4-7 | EvidencePackage Gate-neutral + exact canonical reuse（复用同一对象，不调 allocator、不建 body）；negative-atlas observation 也是 EP，其 `does_not_support` 列「absence of a normal-tissue on-target liability / normal-tissue safety / a product-specific therapeutic window」；reuse parity 覆盖该 observation kind 的 classification-driving 字段（缺失 OR drift → HARD reject）；SourceIndex authority 同 E2。 |
| E4-8 | CI 只跑 synthetic / in-memory 验收场景（`TARGET_A` / `PROGRAM_A` / `PROGRAM_B` / `LIVER`(`HEPATIC`) / `PHENO_X`），28 项。 |

两个加粗实现点（审核方原话）：**TGT-05 的「negative data」主要是 coverage
information，不是 safety evidence；`fatal_review` 是一个 machine-generated review
trigger，不是 machine-generated fatal conclusion。**

## 两轮历史（初次提交 + 1 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `1110fe95`（首版：10 文件 MOD-TGT05 实现 + binding 窄修 + 38 module tests，全量 906） | `REQUEST_CHANGES`。**architecture PASS**（standalone core / injected ports only / one-way liability detector / frozen truth table 主体 / negative atlas = coverage context / `fatal_review` 仅 `POTENTIAL_FATAL_PATTERN` trigger / exact tissue+phenotype key convergence / Path A·B·C / Gate-neutral EP + exact reuse 总体机制 / TGT-05 binding 1.0.0、TGT-01 未动、`MIGRATION_PENDING` 保持）。4 个 deterministic evidence-integrity / scientific-equivalence blocker。 |
| 2 | `bbc630f`（第一轮修订，50 module tests / 918 全量） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 4 个 blocker（`1110fe95` → `bbc630f`）

1. **TGT-05 admissibility boundary 未严格等价于 frozen ladder。**
   - NHP 过松：classifier 只查 `observation_kind == "NHP_TOXICITY" and
     translational_relevance`，没要求 `SUPPORTS_TARGET_ATTRIBUTION` / attribution
     basis —— 会把可能是 off-target / construct-specific 的同靶点 NHP toxicity
     误升为 frozen 的 on-target liability。修：NHP INDIRECT_STRONG 现要求
     `translational_relevance=True` + `SUPPORTS_TARGET_ATTRIBUTION` + 非空
     `target_attribution_basis`。
   - clinical (ADC / non-ADC) toxicity 过严：`NormalizedLiabilityRecord.__post_init__`
     对两类都强制 `construct_fingerprint` + `toxicity_phenotype_key` 非空，但那是
     fatal-pattern convergence eligibility 字段，不是 PR D non-ADC
     INDIRECT_STRONG evidence class 的前提。修：record 层只强制 `program_id` +
     `affected_tissue` + attribution stance；缺 `construct_fingerprint` /
     `toxicity_phenotype_key` 仍是 admissible liability rung，只是不能当
     `fatal_review` candidate（`fatal_review.detect` 自己要求这两项非空）。
   - `ATTRIBUTION_ADJUDICATION` 对任意 `observation_kind` 都可成立。修：限定到
     `ADC_CLINICAL_TOXICITY` / `NON_ADC_CLINICAL_TOXICITY` —— atlas / expression /
     rodent observation 不能靠共享 `liability_event_id` 进入 attribution-conflict
     machinery。
   - regressions：NHP translational + 无 attribution → NOT INDIRECT_STRONG；NHP
     translational + supported on-target → INDIRECT_STRONG；non-ADC clinical +
     construct fingerprint 缺失 → still INDIRECT_STRONG / never fatal candidate；
     ADC DIRECT + phenotype key 缺失 → still DIRECT / `fatal_review.required`
     无法触发；non-clinical `ATTRIBUTION_ADJUDICATION` → rejected。

2. **Canonical EP reuse parity 漏掉真正 classification-driving fields。**
   `_KEYS_BY_KIND` 不含 `liability_event_id`，而 `aggregate.py` 正是用它决定
   CONFLICTING 分组 —— canonical EP body 记 `EVT-A`、current record 记 `EVT-B`
   时 parity 仍通过，immutable body 与 current classification semantics 漂移
   （E2 已消灭过的坑）。且 parity 只按 `observation_kind` 固定字段，未纳入
   `evidence_function` 驱动的字段。修：`_reused_package_is_compatible` 改用
   `_parity_keys(record)` = always 集
   (`target_identity`, `observation_kind`, `evidence_function`,
   `liability_event_id`) + kind-specific + evidence_function-specific
   （`ATTRIBUTION_ADJUDICATION` 无论原 kind 加 `target_attribution_stance` +
   `target_attribution_basis`；`COVERAGE_CONTEXT` 加 `vital_organ_class` +
   `finding` + `atlas_validated`）；缺失 OR drift → HARD integrity failure。
   regressions：canonical `EVT-A` 复用给 current `EVT-B` record → HARD reject；
   canonical `SUPPORTS` 复用给 current `REFUTES` record → HARD reject。

3. **CONFLICTING 的 EvidenceRole 会污染别的 event。** 纯 CONFLICTING branch 的
   `for e in attr_ev:` 未检查该 attribution record 的 `liability_event_id` 是否
   在 `disputed_set` —— 一个完全无关的 REFUTES record 也会被标成 `CONTRADICTING`
   （违反 E4-4「CONFLICTING only per liability_event_id」）。且 POSITIVE-with-
   independent-liability branch 仍把 disputed event 的 REFUTES record 标成
   `CONTRADICTING`。修（冻结规则）：
   - overall CONFLICTING：只有 `liability_event_id ∈ disputed_set` 的 refs 才是
     SUPPORTING（disputed rung / support）/ CONTRADICTING（matching refutation）；
     所有 unrelated attribution records + undisputed WEAK rung → `CONTEXTUAL`。
   - overall POSITIVE（存在独立 established liability）：整个 disputed event
     （rung + support/refute adjudication）→ `CONTEXTUAL` + `critical_unknown`；
     POSITIVE assessment 里没有 `CONTRADICTING`。
   - EvidenceRole 始终相对最终 CandidateGateAssessment，而非某个局部 event。
   regression：已存在一个合法 conflict + 一个 unrelated REFUTES attribution
   record → unrelated 那条是 `CONTEXTUAL`、只有一个 `CONTRADICTING`。

4. **Coverage completion 可脱离 EvidencePackage provenance 独立宣称。**
   `_coverage_map()` 只把 `evidence_function == COVERAGE_CONTEXT` 的 EP 填进
   `supporting_evidence_ids`（validated protein DETECTED 的 INDIRECT_STRONG
   liability EP 不进 coverage map）；且 `acceptance` 从不验证
   `ADMISSIBLE_PROTEIN_DATA_FOUND` 是否对应某个 emitted / reused protein EP ——
   `_run([])` 配六器官全 `ADMISSIBLE_PROTEIN_DATA_FOUND` 的 sweep 仍可 accepted，
   破坏 Assessment → EvidencePackage → Source Provenance 链条。修：
   - `_coverage_map` 按器官收录全部 admissible validated-human-PROTEIN 观测
     （DETECTED INDIRECT_STRONG liability EP + NOT_DETECTED COVERAGE_CONTEXT EP）。
   - `acceptance.evaluate` 新增 `coverage_state_is_backed_by_evidence_packages`：
     `search_complete` 器官 `ADMISSIBLE_PROTEIN_DATA_FOUND` 必须 ≥1 backing
     human-protein EP；`PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA` 必须
     0；`NOT_YET_COMPLETE` 不作反向约束。
   regressions：六器官全宣称 `ADMISSIBLE_PROTEIN_DATA_FOUND` + 无 protein EP →
   machine reject；HEPATIC DETECTED protein EP + sweep 说 EXHAUSTED → machine
   reject；HEPATIC validated NOT_DETECTED EP + `ADMISSIBLE_PROTEIN_DATA_FOUND` →
   valid backing。

`fatal_review` 仍是纯 machine review trigger —— 只有满足 exact-key + distinct-
program + attribution/fingerprint 要求的 ADC observations 进入 candidate set，
没有滑回 machine fatal conclusion。

## 第二轮 APPROVE（`bbc630f`）

审核方逐 blocker 复核（不只看摘要，读 classifier / contracts / evidence /
aggregate / acceptance / module 与测试）：4 个 blocker 均 **CLOSED**，无新
blocking issue。

- **Admissibility boundary — CLOSED**：NHP INDIRECT_STRONG 现要
  `translational_relevance` + `SUPPORTS_TARGET_ATTRIBUTION` +
  `target_attribution_basis`；clinical toxicity 不再因缺
  `construct_fingerprint` / `toxicity_phenotype_key` 丢失合法 rung，这两个字段
  只控制 fatal-pattern eligibility；`ATTRIBUTION_ADJUDICATION` 限制在 ADC /
  non-ADC clinical toxicity；regressions 覆盖 NHP attribution 和 non-ADC
  fingerprint 缺失。
- **Canonical reuse semantic parity — CLOSED**：parity = always + kind-specific
  + function-specific；`liability_event_id` 成为 mandatory parity field；
  attribution flow 强制比较 stance + basis；missing / drifted → HARD；
  EVT-A→EVT-B 与 SUPPORTS→REFUTES drift regression 均已加入。
- **CONFLICTING EvidenceRole — CLOSED**：CONFLICTING branch 只有 `disputed_set`
  内的 attribution refs 才能成为 SUPPORTING / CONTRADICTING；unrelated
  attribution records 与 undisputed WEAK evidence → `CONTEXTUAL`；存在独立
  established liability 时整体 POSITIVE、整个 disputed event → `CONTEXTUAL` +
  critical unknown，不再污染最终 Assessment 的 EvidenceRole；unrelated-refutation
  regression 已加入。
- **Coverage ↔ Evidence provenance — CLOSED**：coverage map 同时收录 validated
  human protein DETECTED liability EP 和 NOT_DETECTED coverage EP；machine
  acceptance 强制 `ADMISSIBLE_PROTEIN_DATA_FOUND` → 该 organ 必须有 protein EP、
  `PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA` → 不得有；四个关键
  coverage consistency regressions 均已补齐。

CI（GitHub Actions `verify`，python 3.11 + 3.12）对 `1110fe95` 与 `bbc630f`
均 `success`。全量 `unittest discover`：round 1 后本地 918（唯一本地 FAIL 是既有
`test_assetgenos_modules` 的 `__pycache__` 物理扫描噪音，在 stash 掉本次改动的
pristine tip 上同样 FAIL，CI 干净 checkout 上 GREEN）。

GitHub connector 两轮都返回 `403 Resource not accessible by integration`，
REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
为 authoritative。
