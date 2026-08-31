# ChatGPT 审核记录：Runtime Migration PR E13 —— MOD-TGT06 施工合同（design-only）

- 日期：`2026-08-31`
- PR：#130 `task_20260831_runtime-migration-pr-e13`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`0ab57b9`（第三轮修订后）
- Merge 提交：`aa57640`（`Merge pull request #130 from leezx/task_20260831_runtime-migration-pr-e13`）
- 结论：**APPROVE @ `0ab57b9`**。「PR #130 @ `0ab57b9` 可以 merge，E13
  construction contract 可以正式冻结。下一步进入 PR E14 = MOD-TGT06@1.0.0
  deterministic implementation。」GitHub connector 每轮均 `403 Resource not
  accessible by integration`，REQUEST_CHANGES / APPROVE 的 GitHub review state
  未回写；`AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260831_runtime-migration-pr-e13-approval-record`）
中补登，按 PR #95 … #129 先例。本 PR 同时把
`manifests/runtime_migration_pr_e13_manifest.yaml` 补成 approved。不改 PR E13 的
合同、drawing、测试或 handoff 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e13_manifest.yaml` 的 `scoping_decisions`
（E13-1…E13-8）、`seven_key_freeze_points` 与 `three_headline_conclusions`，以及
`docs/handoff/2026-08-31-runtime-migration-pr-e13.zh-CN.md`。要点：

- E13 是 **CONSTRUCTION_CONTRACT_ADD**，与 E1 / E3 / E5 / E7 / E9 / E11 同型：
  只交付
  `src/contracts/gate_modules/tgt06_internalization_trafficking_addressability.yaml`
  的 17 项施工合同 + human-readable drawing + parity / validation 测试 + 17 项
  验收清单 + manifest / handoff / worklog append。**不交付任何实现**。canonical
  Gate 名 "Internalization / Trafficking Addressability"。`MOD-TGT06`
  `primary_module_version` 保持 `0.0.0`（PR E14 才 bump 到 `1.0.0`）；binding /
  registry / README / built-roster test 一律不动（唯一既有文件改动是
  `logs/worklog.md` append）；`MIGRATION_PENDING` 保持。main 当前 built 6 个
  （TGT-01/02/03/04/05/08）。
- **7 个关键 freeze point**（审核方 closing summary，逐字冻结在合同）：
  1. **Option A** —— qualifying `INDIRECT_STRONG` addressability landscape 传播
     成 `POSITIVE / INDIRECT_STRONG`；TGT-06 **不是** TGT-04 那种 single-tier
     gate。
  2. **Legal Direction × Strength pair 恰好 6 个**：`POSITIVE/DIRECT`、
     `POSITIVE/INDIRECT_STRONG`、`NEGATIVE/DIRECT`、`CONFLICTING/DIRECT`、
     `INCONCLUSIVE/DIRECT`、`INCONCLUSIVE/UNKNOWN`。
  3. **一个** independent DIRECT-quality failure configuration + 无 productive
     DIRECT → `INCONCLUSIVE / DIRECT`，**不是** `NEGATIVE`（PR D
     forbidden_inference）。
  4. `NEGATIVE / DIRECT` 与 potential fatal 都需要 **multiple independent
     antibody / epitope configurations**。
  5. **Route A 本身**必须是 declared multi-configuration analysis（`>= 2` unique
     configuration id）。
  6. **`WELL_MATCHED_CRC_MODEL` 可以进 fatal contributor**（与 TGT-04 相反）；
     **但**任何 qualifying productive DIRECT existence proof 都取消 target-wide
     surface-static machine fatal trigger。
  7. Completion **不建立** `qualifying_indirect_configuration_ids`；DIRECT
     integrated evidence 永远不能靠不同 observations / configurations 拼接产生。
- 3 条 headline conclusion（逐字冻结在合同顶部）：Internalization is
  configuration-specific, not a target-intrinsic constant（一个 qualifying
  disease-relevant configuration 即足够 DIRECT existence proof；一个
  configuration 的 failure 永不确立 target-wide non-internalization）；DIRECT
  productive-addressability authority requires an auditable INTEGRATED
  observation（surface localization / receptor-family inference / constitutive
  endocytosis / internalization without confirmed lysosomal delivery / non-CRC
  internalization / successful same-target ADC precedent 均是 lower-ceiling，
  不得跨 unrelated observations / configurations 合成 DIRECT）；a target-wide
  surface-static potential fatal pattern requires failure across MULTIPLE
  INDEPENDENT qualified configurations AND no qualifying productive DIRECT
  existence proof（机器至多 `POTENTIAL_FATAL_PATTERN`，永不裁决 fatality / ADC
  efficacy / KILL / HOLD / Decision）。
- items 03/05/07/08 对冻结 PR D TGT-06 做 normalized-equality parity；item 04
  做 EXACT set-equality。确认 frozen PR D TGT-06 **无 `inference_guard` 字段**
  （EVGAP-01 是 TGT-04 专属）。8 observation kinds、CLOSED
  `internalization_outcome` enum（保留 `_OR_TRAFFICKING`）、
  `declared_multi_configuration_analysis` single-vs-multi identity pattern、
  **无 dedicated raw-value reuse-parity 分支**。

## 审核往返（4 轮）

### Round 1 —— REQUEST_CHANGES @ `1a199c2`

审核方确认主体合同成立（design-only boundary 干净；PR D items 03/05/07/08 parity
+ item 04 exact-set parity；Option A；6 legal pairs；existence-proof aggregation；
multi-configuration fatal；well-matched model fatal eligibility；productive DIRECT
cancels fatal；四轴 completion；无 indirect configuration set；no-cross-observation
synthesis；8 observation kinds；无 dedicated raw-number parity branch）。**4 个窄
construction-contract blocker**：

1. **`declared_multi_configuration_analysis` identity shape 自相矛盾** —— item 06
   只冻结 SINGLE / IDENTIFIED_MULTI，但 E13-8 要求 constitutive endocytosis /
   same-target-ADC precedent / receptor-family inference / surface-localization
   inference / audit / non-CRC internalization（source 未披露 configuration 时）
   在**无 config id**下仍合法。修复：冻结**三个** identity state —— SINGLE /
   IDENTIFIED_MULTI / IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE；第三种只允许非
   DIRECT-quality observation kind；任何 DIRECT-quality observation 处于第三种
   state 即 HARD。item 13 check 同步。
2. **aggregation truth table 无冻结的 evaluation ORDER** —— existence-proof
   dominance 与 same-config CONFLICTING 的交互未定。修复：冻结
   `frozen_evaluation_order`（stop-at-first-match）；step 2（CLEAN productive
   DIRECT configuration）先于 step 3（same-config CONFLICTING），conflicted A +
   clean productive B → 仍 `POSITIVE / DIRECT`。
3. **item 03 `tgt06_framing.answers` 把整个 Gate 错写成 DIRECT existence-proof
   question**，与 E13-3（no DIRECT + qualifying INDIRECT_STRONG →
   `POSITIVE / INDIRECT_STRONG`）矛盾。修复：重写 answers，Gate question 与
   DIRECT ceiling 区分。
4. **`TRAFFICKING_OR_RECYCLING_ONLY` 是 observation kind 却无
   productive-trafficking-failure / fatal authority** —— antibody internalizes 但
   receptor rapidly recycles、无 productive lysosomal trafficking 跨 `>= 2`
   independent configurations 重复，正是 PR D 的 "fails productive ...
   trafficking"。修复：冻结 `trafficking_or_recycling_only_authority`（非对称）——
   正向至多 INDIRECT_STRONG / supporting、永不合成 positive DIRECT；负向
   （configuration-resolved + disease-relevant + QUALIFIED assay + FAILS outcome）
   IS 一个 DIRECT-quality failure observation，参与 truth table 与 Route A /
   Route B fatal。item 08 / item 09 / item 13 同步。

修订：合同 items 03/06/08/09/13；drawing rows 3/6；
`tests/test_tgt06_module_construction_contract.py` 73 → 81（新增
`ReviewRound1RegressionTests`）；manifest `review_rounds: 1` + `review_round_1`
block；worklog append。全量 1611 → 1619。提交 `8e695ce`。

### Round 2 —— REQUEST_CHANGES @ `8e695ce`

审核方判定 round-1 的 4 个 blocker **全部 CLOSED**。**3 个窄 consistency
blocker**：

1. **item 12 `fatal_review.required_is_true_iff` 漏同步 `TRAFFICKING_OR_RECYCLING_ONLY`**
   —— item 08 / item 13 已用三-kind contributor set，item 12 仍只列前两类。
   修复：item 12 用同一三-kind set；测试收紧为 item 08 / 12 / 13 exact
   contributor-set parity。
2. **same-configuration conflict 依赖不存在的 typed resolver** —— truth table
   反复允许「typed / auditable characterization resolve」，而 conceptual shape
   无任何 typed field。修复（最小、不扩架构）：v1 **无 machine conflict
   resolver** —— 同一 configuration identity 同时带 qualifying productive DIRECT
   与 qualifying DIRECT-quality failure observation 即 `CONFLICTING / DIRECT`；
   「typed / auditable characterization resolves it」措辞从 6 处移除；CONFLICTING
   row key 改名。
3. **`IDENTIFIED_MULTI` 的 config-id SET 如何进入 grouping / counting 未锁** ——
   E14 可把 `{A,B}` 当一个 tuple identity 或展开成 A、B。修复：冻结
   deterministic helper `configuration_identity_projection(observation)` ——
   SINGLE → `{internalization_configuration_id}`；IDENTIFIED_MULTI →
   `set(internalization_configuration_ids)`；IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE
   → `{}`。ALL grouping / CLEAN detection / same-configuration conflict
   detection / DIRECT-quality failure counting / `>= 2` independent test /
   Route B convergence / `completion.qualifying_direct_configuration_ids` 都用
   这一个 projection；`{A,B}` 贡献 both A 和 B。

修订：合同 item 06（direction_definitions.CONFLICTING + existence_proof_dominance
+ different_configurations_differ_is_not_a_conflict + truth-table note / 新
`configuration_identity_projection` / frozen_evaluation_order step 3 / CONFLICTING
row key）、item 08 route_b、item 09 typed_completion_record、item 12
required_is_true_iff、item 13 aggregation check；drawing row 6；测试 81 → 88
（新增 `ReviewRound2RegressionTests`）；manifest `review_rounds: 2` +
`review_round_2` block；worklog append。全量 1619 → 1626。提交 `bfe82ba`。

### Round 3 —— REQUEST_CHANGES @ `bfe82ba`

审核方判定 round-2 的 3 个 blocker **全部 CLOSED**，7/7 original freeze point
intact。**1 个窄 Route A/B consistency blocker**：

- **fatal Route B 允许单个 `IDENTIFIED_MULTI {A,B}` observation 仅凭 projection
  cardinality 满足 convergence，绕过 Route A 的 `reproducibility_status ==
  QUALIFIED` gate**。修复：Route B 现在要求**同时** (1) `>= 2` DISTINCT eligible
  DIRECT-quality failure **OBSERVATIONS** 且 (2) 它们的
  `configuration_identity_projection` set 并集 size `>= 2`。逐字锁「A single
  IDENTIFIED_MULTI observation, regardless of its projection cardinality, does
  NOT satisfy Route B」+「A single multi-configuration observation may establish
  the fatal pattern ONLY through Route A, which additionally requires
  `reproducibility_status == QUALIFIED` + an auditable `reproducibility_basis`」。
  ordinary Gate-level aggregation（item 06）**不变** —— 单个 `IDENTIFIED_MULTI
  {A,B}` failure observation 仍 project 成两个 failure configuration identity、
  仍可支撑 `NEGATIVE / DIRECT`；Gate NEGATIVE scientific assessment ≠ machine
  `POTENTIAL_FATAL_PATTERN`。item 08 route_b / item 12 required_is_true_iff /
  item 13 fatal acceptance wording 同步。

修订：合同 item 08 route_b_independent_convergence + item 12
required_is_true_iff + item 13 fatal acceptance check；drawing row 8（Route B +
三-kind fatal contributor set）；测试 88 → 91（新增 `ReviewRound3RegressionTests`）；
manifest `review_rounds: 3` + `review_round_3` block；worklog append。全量
1626 → 1629。提交 `0ab57b9`。

### Round 4 —— APPROVE @ `0ab57b9`

审核方确认 round-3 的唯一 blocker 已关闭（Route B 现在同时要求 `>= 2` distinct
eligible failure observations 与 projected configuration union `>= 2`；单个
`IDENTIFIED_MULTI {A,B}` observation 无论 projection cardinality 都不能走 Route
B，只能在 `reproducibility_status == QUALIFIED` + basis 时通过 Route A；item 12
与 item 13 已同步相同 Route A/B 定义，没有第二套 fatal semantics；ordinary Gate
aggregation 被明确隔离；regression 已锁 Route B two-distinct-observations 条件与
ordinary NEGATIVE 不变）。exact-head CI run `33432029477` Python 3.11 / 3.12
verification 均 success。

E13 最终冻结状态：Option A / POSITIVE / INDIRECT_STRONG；exactly 6 legal
Direction × Strength pairs；existence-proof ordered aggregation；v1 无 machine
conflict resolver；unified `configuration_identity_projection`；four completion
axes、无 `qualifying_indirect_configuration_ids`；no cross-observation synthesis
of positive DIRECT；design-only；MOD-TGT06 `0.0.0`；`MIGRATION_PENDING` 保持。

四轮状态：Round 1 —— 4 blockers → CLOSED；Round 2 —— 3 consistency blockers →
CLOSED；Round 3 —— 1 Route A/B blocker → CLOSED；Round 4 —— 无新 blocker。

**结论：APPROVE —— PR E13 可以 merge。下一步进入 PR E14 = MOD-TGT06@1.0.0
deterministic implementation。**

## Merge

- PR #130 于 `2026-08-31` 以 `--merge` 合入 `main`，merge 提交 `aa57640`。
- 8 个 primary Module 施工合同已 APPROVE 7 个（TGT-01/02/03/04/05/08 + 本 PR）；
  已实现 6 个（TGT-01/02/03/04/05/08 @ 1.0.0）。MOD-TGT06
  `primary_module_version` 仍 `0.0.0`，PR E14 才 bump。`MIGRATION_PENDING` 保持
  （八个 primary Module 全部建成前不解除；剩余 TGT-07 属后续 PR）。
