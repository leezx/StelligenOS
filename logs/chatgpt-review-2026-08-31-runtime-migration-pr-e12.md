# ChatGPT 审核记录：Runtime Migration PR E12 —— MOD-TGT04@1.0.0 deterministic implementation

- 日期：`2026-08-31`
- PR：#128 `task_20260831_runtime-migration-pr-e12`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`14fba32`（第二轮修订后）
- Merge 提交：`f09ab3d`（`Merge pull request #128 from leezx/task_20260831_runtime-migration-pr-e12`）
- 结论：**APPROVE @ `14fba32`**。「PR #128 @ `14fba32` 可以 merge，MOD-TGT04@1.0.0
  可以冻结。下一步进入 TGT-06 construction contract / PR E13。」GitHub connector
  每轮均 `403 Resource not accessible by integration`，REQUEST_CHANGES / APPROVE
  的 GitHub review state 未回写；`AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260831_runtime-migration-pr-e12-approval-record`）
中补登，按 PR #95 … #127 先例。本 PR 同时把
`manifests/runtime_migration_pr_e12_manifest.yaml` 补成 approved。不改 PR E12 的
实现、测试或 handoff 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e12_manifest.yaml` 的 `scoping_decisions`
（E12-1…E12-8）、`four_required_implementation_tightenings` 与
`three_headline_invariants`，以及
`docs/handoff/2026-08-31-runtime-migration-pr-e12.zh-CN.md`。要点：

- E12 是 **IMPLEMENTATION PR**，与 E2 / E4 / E6 / E8 / E10 同型：交付
  `gate_modules/tgt04_tumor_surface_availability_density_plausibility/` 的 11 文件
  deterministic Gate-specific scientific core（`__init__` / `module.yaml` /
  `contracts` / `ports` / `classify` / `evidence` / `aggregate` / `completion` /
  `fatal_review` / `acceptance` / `module`），`module_version` `0.0.0` → `1.0.0`，
  加最小 binding / registry / built-roster reconciliation。`run()` 是 pure
  Python，只调注入的 port —— 无 network / subprocess / filesystem-derived id /
  repository write / db / cache / retrieval adapter / LLM / raw density 数值化。
  包内无 `normalizer.py`（surface qualification 由 provider 从 UPSTREAM 给）。
  `src/` 不 import `gate_modules/`。frozen E11 施工合同正文不动。
- 3 条 headline invariant（逐字冻结在 `contracts.py` 顶部）：surface localization
  is not antigen density（INDIRECT_STRONG localization 观测支持「抗原在细胞表面」
  但永不授予 Gate-level proposed Strength；localization-only 的 completed
  landscape 在 density 问题上是 `INCONCLUSIVE / UNKNOWN`）；quantitative values
  are evidence, not thresholds（raw `reported_density_value` / `_unit` /
  `_summary` 是 opaque factual string + symmetric exact-reuse identity key，永不
  被数值化，永不与任何 threshold / cutoff / invented "clinically effective range"
  比较；density plausibility 只以 auditable upstream `density_plausibility_status`
  到达）；单个 quantitative `NEGLIGIBLE_OR_UNDETECTABLE` 观测是 DIRECT-class
  OPPOSES 观测，尚不是 `NEGATIVE / DIRECT` proposal、也不是 reproducible fatal
  pattern；只有 reproducible（Route A / Route B）的 CRC malignant-cell
  quantitative `NEGLIGIBLE_OR_UNDETECTABLE` 才可能浮出 `POTENTIAL_FATAL_PATTERN`；
  well-matched CRC model 观测可驱动普通 DIRECT Direction 但永不是 fatal
  contributor；`LOW_BUT_PRESENT` 永不 fatal；Module 永不裁决 fatality / ADC
  efficacy / KILL。
- 4 个 required implementation tightening（审核方逐字，冻结在代码）：
  1. DIRECT 必须显式要求 malignant-cell attribution（`malignant_cell_attribution
     == MALIGNANT` + 非空 auditable `malignant_attribution_basis`，`CRC_MALIGNANT_
     CELLS` 与 `WELL_MATCHED_CRC_MODEL` 都要）；外加 factual-coherence HARD guard
     （CRC / well-matched-model 的 `surface_context_class` 要求 `crc_specific ==
     true`；`crc_specific` 本身不授予 rung）。
  2. 加 `declared_multi_context_analysis`；conflict resolver 全 typed ——
     SUPPORTS + OPPOSES → `CONFLICTING / DIRECT`，除非某个 qualifying DIRECT
     观测有 `declared_multi_context_analysis == true` AND `density_plausibility_
     status == MIXED_OR_UNRESOLVED` AND auditable `density_plausibility_basis`
     AND `surface_context_ids` 覆盖所有 material context → `INCONCLUSIVE /
     DIRECT`。`NOT_ESTABLISHED` 不是 resolver；`density_plausibility_basis` /
     `claim` / `reported_density_summary` 永不 semantic-parse。
  3. `SurfaceAvailabilityCompletion.attempted == False` 是 frozen strict-empty
     state（无 `search_scope` / `sources_searched` / qualifying context id /
     `audit_observation_id` / component 或 umbrella flag）。`attempted == true`
     要求 `search_scope`、`sources_searched`、合法 `audit_observation_id`、恰好一
     个 normalized `SEARCH_COMPLETION_AUDIT` 与恰好一个 emitted / reused
     provenance-bearing audit EP。qualifying-set parity 只在 completed landscape
     上是最终 qualifying-set 权威。
  4. raw density 在 Module 内保持 opaque factual string（`reported_density_value`
     / `_unit` / `_summary` 是 `str`，空 == absent）；无 `float()` / `Decimal()`
     / `int()`，无 unit conversion / normalization / cross-assay rescaling；reuse
     只做 symmetric exact presence-and-value equality。未来的 density-unit
     normalization 属 shared preprocessing，不是 TGT-04 Gate authority。
- E12-4 是与 E10 最大的分歧：`aggregate.py` **直接**写 TWO-TIER / SINGLE-TIER
  grading authority（不是 generic highest-rung aggregator）—— 无 qualifying
  DIRECT quantitative antigen-density 观测 → `INCONCLUSIVE / UNKNOWN`（100
  qualifying INDIRECT_STRONG + 0 DIRECT 仍是 `INCONCLUSIVE / UNKNOWN`）；否则
  Strength = DIRECT，只在 qualifying DIRECT 集合上按 `density_direction_mapping`
  grade。legal Direction × Strength pair 恰好 5 个：`POSITIVE/DIRECT`、
  `NEGATIVE/DIRECT`、`CONFLICTING/DIRECT`、`INCONCLUSIVE/DIRECT`、
  `INCONCLUSIVE/UNKNOWN`。
- `MIGRATION_PENDING` 保持（八个 primary Module 全部建成前不解除）；E12 后已实现
  6 个（TGT-01/02/03/04/05/08 @ 1.0.0），剩余顺序 TGT-06 → TGT-07。

## 审核往返（3 轮）

### Round 1 —— REQUEST_CHANGES @ `28ddff6`

审核方确认主体实现与 E12 scoping 对齐；binding / 6-of-8 built /
`MIGRATION_PENDING` / package boundary 无 blocker；无 E11 science 重开、无 11-file
重构。**3 个窄 runtime blocker**：

1. **合法 raw quantitative fact 被 `acceptance.py` 错杀成 numeric threshold**。
   `evidence.py` 正确把 raw factual `reported_density_value` / `_unit` /
   `_summary` 放进 Gate-neutral EP 的 `directly_supports`（E11 item 11），但
   `acceptance.py` 把 `directly_supports` 拼进 scanned text，`_SCORE_RE` 命中
   `"12000 molecules per cell by QIFIKIT"` → 整轮拒。修复：新增
   `_scannable_ep_fact_text()`，扫描前逐 EP 剔除 verbatim raw
   `reported_density_*` payload；`_SCORE_RE` 收窄为 DECISION language（cutoff /
   threshold / clinically effective range / `score=` / ranking / fold-change /
   `above|below <number> molecules|abc|%`）。
2. **`aggregate.py` 的 typed multi-context conflict resolver 可被实际 OPPOSES
   观测冒充**。frozen density mapping 里 `surface_antigen_level ==
   NEGLIGIBLE_OR_UNDETECTABLE → OPPOSES_DENSITY_PLAUSIBILITY` 优先级更高，一个
   `NEGLIGIBLE_OR_UNDETECTABLE` + `density_plausibility_status ==
   MIXED_OR_UNRESOLVED` + `declared_multi_context_analysis` 的观测经 classifier
   后是 OPPOSES，却仍满足 resolver 条件。修复：resolver 额外要求
   `e.classified.density_implication == "CONTEXTUAL"`（消费 classifier
   authority，不重建第二条解释路径）。
3. **raw-density exact-reuse parity 对 canonical-missing-key 单向**。
   `evidence.py._reused_package_is_compatible()` 对每个 `_parity_key` 执行
   `if key not in existing.study_context: return HARD`，而
   `QUANTITATIVE_SURFACE_DENSITY` 的 `_parity_keys()` 总含三个 raw key，导致
   current `""` + canonical 缺 key → 误 HARD。修复：对 raw density key 用
   `existing.study_context.get(key, "")`，按 presence AND value 比较 —— missing
   key ↔ `""` = 两侧都 absent = compatible；一侧有一侧无 = HARD；value / unit /
   summary 不同 = HARD。

审核方明确「不要改」：DIRECT 显式 MALIGNANT attribution；CRC / model
factual-coherence guard；INDIRECT_STRONG 仅 CRC malignant-cell localization；
well-matched model ordinary DIRECT Direction + fatal exclusion；100 IS + 0 DIRECT
→ `INCONCLUSIVE / UNKNOWN`；5 个 legal pair；completion direct + indirect
context-set parity；`attempted == False` strict-empty state；Route A / Route B；
1 CRC + 1 model 不构成 fatal Route B；duplicate `observation_id` 在 semantic
dedup 前 HARD；raw density 无 numeric coercion；completion / fatal science；其他
Modules。

修订：`acceptance.py`（`_scannable_ep_fact_text` + `_SCORE_RE` 收窄）、
`aggregate.py`（resolver 加 `classified.density_implication == "CONTEXTUAL"`）、
`evidence.py`（raw density key 对称 presence-and-value parity）；
`tests/test_tgt04_module.py` 71 → 77（新增 `ReviewRound1RegressionTests`）；
manifest `review_rounds: 1` + `review_round_1` block；worklog append。全量
1526 → 1532。提交 `11528ed`。

### Round 2 —— REQUEST_CHANGES @ `11528ed`

审核方判定 round-1 的 scientific / runtime semantics **基本 CLOSED**（typed
conflict resolver 现在确实要求 `classified.density_implication == CONTEXTUAL`；
`NEGLIGIBLE_OR_UNDETECTABLE` 经 classifier 映射为 OPPOSES，不能再冒充 resolver）。
剩 **3 个窄 residual integrity blocker**：

1. **`acceptance._scannable_ep_fact_text()` 的 raw-density redaction 是
   order-dependent**。按 value → unit → summary 顺序 `text.replace(raw, " ")`，
   若 `value == "12000"` 且是 summary 子串，第一步会把 summary 里的 "12000" 也
   删掉，summary 碎成 `" molecules per cell below assay detection threshold"`，
   随后 `replace(full_summary, ...)` 匹配不到，残留的 `threshold` 被 `_SCORE_RE`
   命中。修复：按**长度降序**先删最长的 raw string（`sorted(raws, key=len,
   reverse=True)`），使之 order-independent。Regression：value "12000" + summary
   "12000 molecules per cell below assay detection threshold" → ACCEPTED；
   Module-authored "density threshold of 5000" 仍 FAIL。
2. **`evidence.py` 的 raw-density reuse parity 不再是严格 EXACT opaque-string
   parity** —— 两侧都做了 `str(...).strip()`，导致 canonical int `12000` 或带尾
   空格 `"12000 "` 误等于 current `"12000"`。修复：对 raw density key ——
   `key not in study_context → canonical_value = ""`；否则 `canonical_value =
   study_context[key]`，非 `str` 即 HARD；`current_value = current[key]`（已
   contract-validated `str`）；missing key 与 `""` = 两侧都 absent = compatible；
   否则 EXACT string 相等，**不 `strip()`、不 `str()`**。Regression：canonical
   int 12000 vs "12000" → HARD；canonical "12000 " vs "12000" → HARD；canonical
   缺 key + current 全 "" → reuse allowed；identical string → reuse allowed。
3. **duplicate `observation_id` 的 authoritative-identity precedence 没真正
   实现** —— run 仍先跑 semantic dedup、resolve source / evidence、消耗 Evidence
   ID、构造 transient EP，之后才记录 duplicate。修复：在 `module.run()` 里、
   `build_evidence_packages()` **之前**做 observation-id preflight；存在
   duplicate 时 run 短路进入 whole-run HARD rejection（`emitted = []`，不调用
   `build_evidence_packages()`，不调用 allocator）。Regression：duplicate
   `observation_id` → `accepted == False` AND `proposal_envelope is None` AND
   `allocator.calls == 0` AND `evidence_packages == ()` AND `reused_evidence_ids
   == ()`。

审核方明确「不要改」：conflict resolver 的 CONTEXTUAL classifier authority；
single-tier grading；DIRECT / IS rung boundary；completion direct + indirect set
parity；fatal Route A / B + model exclusion；`MIGRATION_PENDING`；TGT-04 1.0.0 /
6-of-8 built；frozen E11 science。

修订：`acceptance.py`（redact longest-first）、`evidence.py`（raw density key
EXACT opaque-string parity，non-str canonical → HARD）、`module.py`（duplicate
`observation_id` preflight BEFORE `build_evidence_packages()`）；
`tests/test_tgt04_module.py` 77 → 83（新增 `ReviewRound2RegressionTests` +
`test_duplicate_observation_id_is_hard` 收紧为
`test_duplicate_observation_id_is_hard_before_any_allocation`，锁 `allocator.calls
== 0`）；manifest `review_rounds: 2` + `review_round_2` block；worklog append。
全量 1532 → 1538。提交 `14fba32`。

### Round 3 —— APPROVE @ `14fba32`

审核方确认 PR 当前 open / mergeable、HEAD 正确；exact-head CI run `33418240815`
的 verify (3.11) / verify (3.12) 都 success，unit tests / repository boundary /
no-bytecode / working-tree checks 全通过。round-2 的 3 个 residual integrity
blocker 已全部关闭：

- raw-density acceptance redaction 现在按 raw string 长度降序处理，summary 先整体
  移除，不再被较短的 value / unit 提前打碎 ——
  `"12000 molecules per cell below assay detection threshold"` regression 正常
  accepted `POSITIVE / DIRECT`。
- canonical reuse 对 raw density 已是真正的 opaque-string exact parity ——
  canonical 非 `str` 直接 HARD；不再 `str()` coercion、不再 `strip()`
  normalization；missing key 与 `""` 才表示双方 absent。integer-vs-string 与
  trailing-space drift regression 都存在。
- duplicate `observation_id` 现在确实在 `build_evidence_packages()` 前 preflight；
  命中后不做 source resolution / semantic dedup / EP construction / Evidence ID
  allocation。regression 锁了 `allocator.calls == 0`、无 emitted / reused EP、
  `proposal_envelope is None`。

E12 关键 frozen semantics 一致性确认：two-tier evidence / single-tier grading；
localization-only → `INCONCLUSIVE / UNKNOWN`；DIRECT requires quantitative
protein + qualified context + MALIGNANT attribution；well-matched model 可
ordinary DIRECT Direction 但不能进入 fatal；conflict resolver 只接受真正
classified CONTEXTUAL 的 typed multi-context characterization；fatal Route A /
Route B 保持 CRC malignant-cell only；raw density 是 evidence 不是 threshold；
exact reuse / dedup / completion audit authority 均闭合；TGT-04 binding = 1.0.0；
当前 6/8 primary Modules implemented；`MIGRATION_PENDING` 继续保留。

三轮状态：Round 1 —— 3 blockers → CLOSED；Round 2 —— 3 residual integrity
blockers → CLOSED；Round 3 —— 无新 blocker。

**结论：APPROVE —— PR E12 可以 merge。下一步进入 TGT-06 construction contract /
PR E13。**

唯一非阻断 metadata housekeeping：PR #128 body 仍显示 71 / 1526（提交时数字），
实际收口是 83 个 TGT-04 test / 1538 full-suite test；审核方判定不值得为此再开一
轮，此处补记正确数字为准。

## Merge

- PR #128 于 `2026-08-31` 以 `--merge` 合入 `main`，merge 提交 `f09ab3d`。
- 8 个 primary Module 施工合同已 APPROVE 7 个（TGT-01/02/03/04/05/08 + E11
  TGT-04 contract）；已**实现 6 个**（TGT-01/02/03/04/05/08 @ 1.0.0）。MOD-TGT04
  `primary_module_version` 已 `0.0.0` → `1.0.0`。`MIGRATION_PENDING` 保持
  （六 of 八 primary Module built；剩余顺序 TGT-06 → TGT-07）。TGT-06 →
  TGT-07 属后续 PR（E13 起），各需独立 go-ahead。
