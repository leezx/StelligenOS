# ChatGPT 审核记录：Runtime Migration PR E10 —— MOD-TGT03@1.0.0 实现

- 日期：`2026-08-31`（build 于 `2026-08-30`）
- PR：#124 `task_20260830_runtime-migration-pr-e10`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`6445ae5`（第一轮修订后）
- Merge 提交：`551a938`（`Merge pull request #124 from leezx/task_20260830_runtime-migration-pr-e10`）
- 结论：**APPROVE @ `6445ae5`**。「PR #124 @ `6445ae5` 可以 merge，MOD-TGT03@1.0.0
  deterministic implementation 可以冻结。下一步进入 TGT-04 construction contract /
  PR E11。」GitHub connector 每轮均 `403 Resource not accessible by integration`，
  REQUEST_CHANGES / APPROVE 的 GitHub review state 未回写；`AI审核方案` 对话结论
  为 authoritative。

本记录在**独立 docs-only PR**（`task_20260830_runtime-migration-pr-e10-approval-record`）
中补登，按 PR #95 … #123 先例。本 PR 同时把
`manifests/runtime_migration_pr_e10_manifest.yaml` 补成 approved。不改 PR E10 的
实现、测试或 handoff 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e10_manifest.yaml` 的 `scoping_decisions`
（E10-1…E10-8）、`five_implementation_tightenings` 与 `three_headline_invariants`，
以及 `docs/handoff/2026-08-30-runtime-migration-pr-e10.zh-CN.md`。要点：

- E10 是 **RUNTIME_IMPL_ADD**，与 E2 / E4 / E6 / E8 同型：11-file 确定性 Gate-specific
  scientific core，严格实现冻结的 E9 施工合同；`run()` 纯 Python，只调 injected
  port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID / 不接
  retrieval / **包内不建 normalizer** / 不做 ontology·embedding·LLM 推理 /
  不产 canonical Assessment 或 Decision / 不产 numeric·ranking score / 不解析
  `reproducibility_basis` 自由文本。窄修 binding：TGT-03
  `primary_module_version` `0.0.0 → 1.0.0`。不改冻结的 E9 合同正文；不重构
  MOD-TGT01 / MOD-TGT02 / MOD-TGT05 / MOD-TGT08；不解除 `MIGRATION_PENDING`。
- 3 条 headline invariant（写在 `contracts.py` 顶部）：baseline expression ≠
  persistence；single observation is evidence never a Direction（NEGATIVE 是
  scientific persistence judgement，非 fatal 非 KILL）；只有 reproducible
  DIRECT-class protein near / marked loss 可 surface POTENTIAL_FATAL_PATTERN
  （Route A / Route B，human-reviewable，Module 永不裁决 fatality）。
- 5 个实现级收紧（审核方逐字）：(1) 包内不建 normalizer；(2) fatal detector 只
  消费已分类证据，不建第二套 qualification engine；(3) Route A 永不解析
  `reproducibility_basis` 自由文本（`reproducibility_status == QUALIFIED` + 非空
  auditable basis 即机器 predicate）；(4) 不盲拷贝 E8 的 `(source_id, claim)`
  dedup（distinct persistence_context_id 的观察都保留；audit EP 永不 dedup
  loser）；(5) E10 必须把 `tests/test_tgt03_module_construction_contract.py` 迁成
  post-implementation reconciliation（不删除）+ 最窄同步其它 hard-code built
  roster 的 test。

## 审核往返（2 轮）

### Round 1 —— REQUEST_CHANGES @ `35d9564`

主体实现成立（11-file package、无 normalizer、PUBLIC_ONLY pure-Python ports、
highest-class aggregation、completion / audit gene、TGT-03 dedup deviation、
Route A / B fatal-review、binding TGT-03→1.0.0、5/8 built、`MIGRATION_PENDING`
保持、binding reconciliation 本身）。**5 个窄 runtime correctness /
factual-integrity blocker**，都不重开 frozen E9 contract body / Direction truth
table / highest-class Strength / four-component completion / Route A/B / ">= 2"
语义 / dedup deviation / EXPERIMENT_REQUIRED precedence / binding 1.0.0 /
MIGRATION_PENDING / MOD-TGT01/02/05/08：

1. **INDIRECT_STRONG qualification 过宽**。`classify.py` 对
   TREATED_METASTATIC_TRANSCRIPT / RESISTANCE_MODEL 只查 crc_specific +
   (attribution) + persistence_pattern 就给 INDIRECT_STRONG，没要求 treatment /
   metastasis context 被 qualified。修复：TREATED_METASTATIC_TRANSCRIPT 需
   `clinical_context == "METASTATIC_CRC"` + `context_adequacy_status == QUALIFIED`；
   RESISTANCE_MODEL 需 `clinical_context == "RESISTANCE_MODEL"` +
   `context_adequacy_status == QUALIFIED`。
2. **LOCAL `persistence_context_id` identity authority 没闭环**：可缺失、可与
   canonical `CTX-CRC-REFRACTORY-MCRC` 撞 namespace。修复：`contracts.py`
   constructor 拒绝任何 local id == canonical；`module.py` 对「local id ==
   canonical」与「qualifying DIRECT/IS 观察无 local persistence context id」各做
   whole-run HARD reject。
3. **只有 loss / transient pattern 要求 auditable basis**：RETAINED /
   MIXED_OR_UNRESOLVED + basis "" 仍能驱动 Direction；transient branch 只在
   PRESENT 时要 residual basis。修复：`contracts.py` —— 任何非空
   `persistence_pattern` 都需非空 `persistence_pattern_basis`；transient 观察
   PRESENT 与 UNRESOLVED 都需非空 `residual_target_presence_basis`。fixtures 同步。
4. **`protein_measurement_validation_status` 有 "" 非冻结状态 + DIRECT 不查
   `assay_method` 非空**：修复：`contracts.py` enum 严格
   `{QUALIFIED, NOT_ESTABLISHED}`，non-protein / audit 观察用 NOT_ESTABLISHED；
   `classify.py` DIRECT 增 `assay_method.strip()` 非空要求（仍非 assay whitelist）。
5. **Gate-neutral EP 的 `study_context.treatment_state` 统一写 "not_applicable"，
   把明确 treated / refractory / paired 证据错误改写**：修复：`evidence.py` 加
   kind → treatment_state 非膨胀映射（refractory_or_prior_treated /
   metastatic_context / paired_pre_post / resistance_model / treatment_naive /
   source_reported / not_applicable）。

新增 `Round1RegressionTests`（13）锁上述五处。

### Round 2 —— APPROVE @ `6445ae5`

5 个 round-1 blocker 全部实质关闭。审核方确认：HEAD 正确、open、mergeable；
exact-head CI run `33355366653` 两个 matrix legs（3.11 / 3.12）unit tests +
repository boundary + no-bytecode + working-tree checks 全过；13 个新 regression
覆盖对应错误路径。无新 substantive blocker。frozen semantics 确认未被修复过程
破坏：`NEGATIVE != fatal != KILL`；Route A OR Route B；Route B == `>= 2` 不是
`> 2`；highest qualifying class Strength；四 component = completeness 不是 score；
incomplete landscape → accepted `INCONCLUSIVE / UNKNOWN`；WEAK-only →
`INCONCLUSIVE / UNKNOWN`；TGT-03 dedup 保留不同 persistence contexts；fatal
trigger 仅 accepted run actionable；`MIGRATION_PENDING` 继续保留；E10 后 built
Modules = TGT-01/02/03/05/08 = 5/8。

## 验证（被审核 HEAD `6445ae5`）

- `tests/test_tgt03_module.py` **91 OK**（round-1 前 78；round 1 +13
  Round1RegressionTests）；`tests/test_tgt03_module_construction_contract.py`
  **75 OK**（`ContractIsFrozenAndImplementedInPrE10Tests`）。
- 全量 `python3 -B -m unittest discover -s tests -p 'test_*.py'` **1379 OK**
  （PR E9 收口 1283；round-1 提交 1366）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项
  （`AI_RESULT_ACCEPTANCE.md`、`CRC Patient Territory Map.png`、
  `STELLIGEN_CONSTRAINTS.md`、`docs/worklogs/`、`pipelines/`）。
- `git diff --check` clean；无 bytecode artifact；YAML 合法。
- exact-head CI（`33354038379` → `33355366653`）两个 matrix leg 全 success。

## 冻结事实

- `chatgpt_review: APPROVE`，`approved_tip: 6445ae5f12496f34758065bc075b473a86b660db`，
  `merge_commit: 551a938739cabc1736a80fd42a6c27fc8b728a8f`，`review_rounds: 2`，
  `test_count_at_approval: 1379`。
- MOD-TGT03 `primary_module_version` = `1.0.0`；`BUILT_MODULE_VERSIONS` =
  TGT-01/02/03/05/08（5/8）；binding / registry / boundary tests 已对账；
  `MIGRATION_PENDING` 保持。
- 下一步：PR E11 = TGT-04 construction contract（fatal-first + cheap-first 顺序
  余下 TGT-04 → TGT-06 → TGT-07），需各自 go-ahead。
