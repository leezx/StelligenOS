# ChatGPT 审核记录：Runtime Migration PR E6 —— MOD-TGT08@1.0.0 实现

- 日期：`2026-08-29`（APPROVE `2026-08-30` EDT）
- PR：#116 `task_20260829_runtime-migration-pr-e6`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`9a033e8`（第一轮修订）
- Merge 提交：`c03fa34`（`Merge pull request #116 from leezx/task_20260829_runtime-migration-pr-e6`）
- 结论：**APPROVE @ `9a033e8`**。「PR E6 MOD-TGT08@1.0.0 implementation 可以
  merge。」GitHub connector 两轮均 `403 Resource not accessible by integration`，
  REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
  为 authoritative。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e6-approval-record`）
中补登，按 PR #95 … #113 / #115 先例。本 PR 同时把
`manifests/runtime_migration_pr_e6_manifest.yaml` 补成 approved。不改 PR E6 的
实现、测试或 handoff 内容。

## 8 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e6_manifest.yaml` 的 `scoping_decisions`
（E6-1…E6-8）与 `three_headline_invariants`，以及
`docs/handoff/2026-08-29-runtime-migration-pr-e6.zh-CN.md` §一。要点：

- **E6-1** 完整确定性 Gate-specific core（同 E2 / E4），10 文件的 standalone 包；
  两个 typed completion state 是 `contracts.py` 里的 frozen dataclass（module-local
  run record，非第七个 core object）；binding 只把 TGT-08
  `primary_module_version` `0.0.0 → 1.0.0`（+ `BUILT_MODULE_VERSIONS` /
  README），其余五个 TGT gate 仍 `0.0.0`；冻结的 E5 合同正文一字不改；不建
  generic framework / ABC；不重构 MOD-TGT01 / MOD-TGT05。
- **E6-2** 一个 `Tgt08OpportunityProviderPort`；`NormalizedOpportunityRecord`
  带 `evidence_axis` ∈ {COMPETITIVE, PATENT, UNMET_NEED} + `observation_kind`
  ∈ {COMPETITOR_PROGRAM, PATENT_CLAIM, UNMET_NEED_CONTEXT,
  SEARCH_COMPLETION_AUDIT} + `source_authority_kind` + 只装事实；provider 永不
  设 axis ceiling / direction / opportunity implication。
- **E6-3** 每轴 authority ceiling 由 completion state 派生（competitive
  primary_source_landscape_complete → DIRECT / else pipeline_inventory_complete
  → INDIRECT_STRONG / else NOT_EVALUABLE；patent
  composition_level_review_complete → DIRECT / else target_level_search_complete
  → INDIRECT_STRONG / else NOT_EVALUABLE）；overall Strength = 较弱的 required
  axis ceiling；frozen E5 truth table 逐字（WEAK 两轴豁免、incomplete →
  UNKNOWN、graded INCONCLUSIVE ≠ UNKNOWN、POSITIVE / NEGATIVE / CONFLICTING）；
  合法 Direction × Strength 对固定。
- **E6-4** 确定性 opportunity implication mapping（approved / registrational /
  active-clinical same-context competitor → OPPOSES；discontinued / failed →
  CONTEXTUAL never auto-favorable；live composition-level ADC claim → OPPOSES；
  live target-level-only → OPPOSES，patent 轴 cap INDIRECT_STRONG；expired
  patent → CONTEXTUAL never whitespace；unmet need → CONTEXTUAL WEAK
  hypothesis）；absence SUPPORT 只来自 audited completion（never `records == []`）；
  completion ↔ emitted-EP 一致性是 HARD 检查。
- **E6-5** machine-local `sponsor_review` review TRIGGER（status 单值
  `POTENTIAL_SPONSOR_FATAL_PATTERN`；无阈值 / 无 ownership-linkage；machine 永不
  断言 dominant / well-protected / no-differentiation-path / stop；永不 canonical
  fatal flag / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE；不在 proposal envelope
  上；只有 accepted run 的 trigger 可执行）。
- **E6-6** Gate-neutral PR A EvidencePackage per observation + exact canonical
  reuse（同一对象、不调 allocator、不建 body）；provenance 取 resolved canonical
  SourceIndex，mismatch → HARD；reuse parity `_parity_keys` = always +
  kind-specific，缺失 OR drift → HARD；package 绝不带 good/bad opportunity /
  crowded target / FTO blocked / dominant competitor / no design around / no
  differentiation path。
- **E6-7** machine acceptance = E5 item-13 可执行检查；HARD
  identity/provenance/completion-consistency/absence-provenance 失败 → 拒整个
  run（proposal=None），绝不降级成 accepted UNKNOWN；`critical_unknowns`
  resolution ∈ {PUBLIC_RESOLVABLE, CURRENTLY_UNRESOLVABLE}，绝无
  EXPERIMENT_REQUIRED；module 绝不构造 CandidateGateAssessment。
- **E6-8** CI 全 synthetic / in-memory；`TARGET_A` / `PROGRAM_A` / `PROGRAM_B`
  / `PATENT_FAMILY_A` / `PATENT_FAMILY_B` / `REFRACTORY_MCRC`；无 HER2 / TROP2。

3 条 headline invariant（审核方原话）：

1. Empty results are not whitespace. Only an AUDITED completion can support an
   absence inference.
2. TGT-08 NEGATIVE is a Gate-relative opportunity judgement, not a scientific
   KILL and not a sponsor decision.
3. `sponsor_review` is a review trigger. The machine detects a pattern; the
   sponsor decides what it means.

## 两轮历史（初次提交 + 1 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `d1c2da4`（首版：MOD-TGT08 10 文件 + binding + 69 tests，全量 1042） | `REQUEST_CHANGES`。**主链全部 PASS**（standalone package、无 shared framework、binding 只构建 TGT-08、weaker-axis truth table、WEAK 豁免、graded INCONCLUSIVE、NEGATIVE 边界、competitive/patent classification、Gate-neutral EP、exact canonical reuse 主机制、HARD source/identity gate、严格 sponsor pattern detection criteria、accepted-run 才 surface `sponsor_review`、无 live IO/FTO/Decision runtime）。2 个 evidence-integrity / sponsor-handoff blocker。 |
| 2 | `9a033e8`（第一轮修订，80 tests / 全量 1053） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 2 个 blocker（`d1c2da4` → `9a033e8`）

两个 blocker 本质同一原则：**机器不能因为 provider 给了一个布尔声明就获得本不该
有的 authority。** 不改 frozen E5 truth table、sponsor detector criteria、
TGT-08 science、binding scope、MOD-TGT01 / MOD-TGT05。

### Blocker 1 —— `SEARCH_COMPLETION_AUDIT` 没真正证明 completion；headline invariant 1 可被绕过

两个 completion object 本身携带丰富的结构化事实（`coverage_complete` /
`primary_source_landscape_complete` / `pipeline_inventory_complete` /
`search_scope` / `sources_searched` / `unresolved_items` / `qualifying_program_ids`
/ `audit_observation_id`，patent 类似），但作为 provenance-bearing EvidencePackage
的 `SEARCH_COMPLETION_AUDIT` observation 不带这些事实，`aggregate._audit_ep_for()`
只按 `observation_id` + axis 存在性匹配，`acceptance` 只验证「audit EP 存在」，
`_KEYS_BY_KIND["SEARCH_COMPLETION_AUDIT"] = ()` 让 reuse parity 对 audit EP 只查
通用字段。→ provider 可把任意「audit」记录配给一个 DIRECT / zero-hit completion
伪造 whitespace。

**修（不重构 architecture，只把 completion snapshot 与 audit observation 结构化
绑定）：**

- `contracts.NormalizedOpportunityRecord` 给 audit kind 加 axis-specific
  structured snapshot：`audit_search_scope` / `audit_sources_searched` /
  `audit_coverage_complete` / `audit_unresolved_items`；competitive 再带
  `audit_primary_source_landscape_complete` / `audit_pipeline_inventory_complete`
  / `audit_qualifying_program_ids`；patent 再带 `audit_jurisdictions` /
  `audit_composition_level_review_complete` / `audit_target_level_search_complete`
  / `audit_qualifying_patent_family_ids`。`__post_init__`：audit kind 必须带非空
  `audit_search_scope` + `audit_sources_searched`；cross-axis 字段禁止；非 audit
  kind 一个 audit 字段都不能带。
- 新 `aggregate.audit_snapshot_mismatch(record, competitive, patent)`：当一条
  audit record 的 `observation_id == completion.audit_observation_id` 时，逐字段
  比对（scope / sources(set) / coverage_complete / unresolved(set) / authority
  flags / qualifying set(set) / jurisdictions(set)），任一 drift 返回 reason。
- `module.run()`：对每个 emitted `SEARCH_COMPLETION_AUDIT` EP 调该函数，drift →
  加入 `hard_integrity_failures`（拒整个 run、`proposal = None`、绝不降级成
  accepted UNKNOWN）。
- `acceptance` 加 `completion_audit_evidence_snapshots_its_typed_completion`。
- `evidence._KEYS_BY_KIND["SEARCH_COMPLETION_AUDIT"]` 从 `()` 改成列全 11 个
  snapshot 字段，`build_evidence_packages` 把它们写进 `study_context` → reused
  canonical audit EP 缺字段或 drift → HARD（走已验证的 exact-reuse parity gene）。
- **未**强制「每个 attempted / coverage_complete completion 都必须有 audit EP」。
  审核方接受此 reconciliation：一个 snapshot-consistent 的 audit EP + audited
  zero-qualifying landscape 按定义就是 material audited absence（按冻结 truth
  table 的 `completed_landscape_only_material_opportunity_supporting_signals` 行
  → POSITIVE / CONFLICTING）；若同时强制 audit EP 必须 present，则
  `completed_landscape_no_material_directional_signal → INCONCLUSIVE /
  DIRECT|INDIRECT_STRONG` 这一冻结行会被部分压缩掉。E5 item 09/13 的原文要求是
  「absence-based whitespace / no-competitor claim 必须有 explicit
  completed-search provenance record」，不是「所有 graded landscape 都必须有
  audit EP」。因此三态区分是干净的：completion incomplete → `INCONCLUSIVE /
  UNKNOWN`；completion complete + contextual evidence + 无 clean-absence audit EP
  → graded `INCONCLUSIVE / overall rung`；completion complete + zero qualifying
  + matching provenance-bearing audit EP → material absence SUPPORT →
  `POSITIVE` / `CONFLICTING`。bypass 方向（伪 audit → 伪 whitespace）由 snapshot
  parity 完全关闭。
- +7 regression：audit snapshot 的 `search_scope` / `sources` / `coverage` flag
  / DIRECT-authority flag / `qualifying_program_ids` / patent `jurisdiction`
  drift → HARD reject；reused canonical audit EP snapshot drift → HARD reject；
  snapshot-consistent audit → accepted（control）。

### Blocker 2 —— `sponsor_review` 可在 incomplete landscape 上成为 accepted actionable trigger

`sponsor_review.detect()` 的 pattern criteria 正确（审核方不要求改 detector
science），但它完全不看两个 completion state，`acceptance` 也没有
`sponsor_review.required ⇒ both core axes complete` 检查，`module.run()` 只做
`run_sponsor_review = sponsor_review if accepted else none()`。于是存在路径：
APPROVED ADC primary-source competitor + live composition-level primary patent
→ `sponsor_review.required = true`；但 competitive 或 patent completion
incomplete → aggregate = `INCONCLUSIVE / UNKNOWN`（合法 accepted state）→
`sponsor_review` 被 surface。违反冻结 E5 item 16：sponsor-review provisional
stop 可以停止追逐弱证据，但「the two core axes' completeness still must be
satisfied」。

**修：**

- `acceptance` 加 `sponsor_review_requires_both_core_landscape_axes_complete`：
  `not sponsor_review.required or (competitive.coverage_complete and
  patent.coverage_complete)`。
- 不满足 → check fail → run not accepted → `module.run()` 把
  `run_sponsor_review = SponsorReviewRecord.none()`（raw detector 仍在内部算出
  candidate pattern，但不是 actionable handoff），`proposal_envelope = None`。
- **未**要求两轴都 DIRECT —— 审核方确认这一点也正确：E5 item 16 冻结的是
  completeness requirement，不是 evidence-authority requirement；overall Strength
  继续由 weaker-axis ceiling 独立决定。
- +3 regression：valid pattern + competitive axis incomplete → not accepted /
  surfaced `sponsor_review` none；valid pattern + patent axis incomplete → 同上；
  valid pattern + both axes complete → accepted `POTENTIAL_SPONSOR_FATAL_PATTERN`
  （保留）。

## 第二轮 APPROVE（`9a033e8`）

审核方逐条复核（exact-HEAD `9a033e82…` CI `verify (3.11)` / `verify (3.12)` 均
`success`，含 unit tests / repository boundary / no-bytecode-artifacts /
working-tree-clean）：

- **Blocker 1 已关闭。** `SEARCH_COMPLETION_AUDIT` 不再只是「名字叫 audit 的
  EP」，而是真正携带 typed completion 的结构化 snapshot（scope / sources /
  coverage / unresolved / authority flags / qualifying sets / patent
  jurisdiction 都结构化固定）；`module.run()` 对命中
  `completion.audit_observation_id` 的 audit record 做 snapshot parity，任何
  drift 进入 `hard_integrity_failures`、整个 run 被拒；11 个 snapshot 字段全部
  进入 canonical EP reuse parity，旧 canonical audit EP 的缺字段或 drift 同样
  无法绕过。审核方明确接受「不强制所有 completed completion 都有 audit EP」的
  reconciliation，并评价其「比强制每个 completed axis 都有 audit EP 更忠实于 E5
  truth table」。
- **Blocker 2 已关闭。** 之前危险路径（strong competitor + patent pattern +
  one core axis incomplete → accepted UNKNOWN + actionable `sponsor_review`）
  已截断为 machine acceptance FAIL → `proposal = None` → surfaced
  `sponsor_review = none()`；两轴 complete 后才允许 handoff，与冻结 E5 item 16
  完全一致。没有错误地升级为「两轴必须 DIRECT」。
- Regression 锁到真正的错误路径而非只测 happy path，足够覆盖两个 blocker。
- 其余没有需要修改的地方；尤其没有理由再动 frozen E5 contract / TGT-08 Gate
  science / frozen truth table / sponsor detector criteria / MOD-TGT01 /
  MOD-TGT05 / TGT-08 binding scope / `MIGRATION_PENDING` / provider·IO·framework
  boundary。

**APPROVE — PR E6 MOD-TGT08@1.0.0 implementation 可以 merge。**

CI（GitHub Actions `verify`，python 3.11 + 3.12）对 `d1c2da4` / `9a033e8` 均
`success`。全量 `unittest discover`：round 1 后本地 1053（`test_tgt08_module.py`
80，`AuditCompletionSnapshotParityTests` 8 + `SponsorReviewTests` blocker-2
regression 3）；唯一本地 FAIL 是既有 `test_assetgenos_modules` 的 `__pycache__`
物理扫描噪音，CI 干净 checkout 上 GREEN。

GitHub connector 两轮都返回 `403 Resource not accessible by integration`，
REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
为 authoritative。

## 状态

8 个 primary Module 已建 3 个：MOD-TGT01@1.0.0、MOD-TGT05@1.0.0、
MOD-TGT08@1.0.0。其余五个（TGT-02 → 03 → 04 → 06 → 07）属后续 PR。
`MIGRATION_PENDING` 保持。真实 provider / adapter 与外部 workspace calibration
各自需 go-ahead。
