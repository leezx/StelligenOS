# ChatGPT 审核记录：Runtime Migration PR E5 —— TGT-08 / MOD-TGT08 Construction Contract

- 日期：`2026-08-29`
- PR：#114 `task_20260829_runtime-migration-pr-e5`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`3e5a551`（第三轮修订）
- Merge 提交：`f9b4ddd`（`Merge pull request #114 from leezx/task_20260829_runtime-migration-pr-e5`）
- 结论：**APPROVE @ `3e5a551`**。「PR E5 的 TGT-08 construction contract 可以冻结。
  下一步按既定流程进入 PR E6 = MOD-TGT08@1.0.0 deterministic implementation。」
  GitHub connector 每轮均 `403 Resource not accessible by integration`，
  REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
  为 authoritative。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e5-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 / #105 / #107 / #109 / #111 / #113
先例。本 PR 同时把 `manifests/runtime_migration_pr_e5_manifest.yaml` 补成
approved。不改 PR E5 的施工合同、drawing 或测试内容。

## 8 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

| # | 决策 |
|---|---|
| E5-1 | 完整施工合同，不写实现。文件 `tgt08_target_opportunity_competition_ip_whitespace.yaml` + drawing + `test_tgt08_module_construction_contract.py` + manifest/handoff/worklog。禁止 `gate_modules/tgt08.../` / provider / adapter / trial·patent retrieval / runtime classifier / EvidencePackage generation / proposal runtime / sponsor decision runtime / FTO engine / numeric·ranking score / 新依赖 / 外部数据。MOD-TGT08 `primary_module_version` 仍 `0.0.0`；MOD-TGT01 = `1.0.0`；MOD-TGT05 = `1.0.0`；`MIGRATION_PENDING` 保持。TGT-08 是 `PUBLIC_PRIMARY`。 |
| E5-2 | **最关键边界：TGT-08 ≠ scientific de-risking，也 ≠ sponsor decision。** 三层分离：Scientific Gates TGT-01…07（target biology / ADC feasibility / liability）→ TGT-08（external opportunity landscape —— competition / target-specific differentiation / IP-whitespace **SIGNALS**）→ Sponsor axis（v5 §7，`OUT_OF_MANDATE` / `STOP_FOR_SPONSOR` 都不是 `KILL`）。TGT-08 **可以**输出 canonical `NEGATIVE` Assessment，语义只能是「current public opportunity evidence weighs against a differentiated entry for this target in refractory mCRC」——**不是** scientifically bad target / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE / FTO blocked / no viable molecule。TGT-08 `POSITIVE` ≠ TGT-01…07 de-risked。Sponsor capability / cash runway / risk appetite / company mandate 不允许进入 Module Direction。 |
| E5-3 | 17 项模板原样继承 E1（已被 E2 / E4 验证）；items **03 / 05 / 07 / 08** 与冻结 PR D `crc_adc_target_gateset.yaml:TGT-08` 做 **normalized-equality parity**；item **04** 对 `evidence_required` + ladder `admissible_evidence_classes` 做 derived parity。 |
| E5-4 | **Direction × Strength：TGT-08 的 `NEGATIVE` 必须真正可达**（与 TGT-05 相反）。Module 把 atomic fact 归入 `SUPPORTS_OPPORTUNITY` / `OPPOSES_OPPORTUNITY` / `CONTEXTUAL`；provider 只给事实。frozen truth table（coverage-complete landscape 上）：只有 material supporting → `POSITIVE`；只有 material opposing → `NEGATIVE`；两者都有 → `CONFLICTING`。indication-level unmet-need-only → `INCONCLUSIVE / WEAK`（永不「grim indication → good opportunity」），且不参与 target-specific `CONFLICTING`。materially incomplete landscape → `INCONCLUSIVE / UNKNOWN`；永不 `UNKNOWN` → attractive / uncrowded / whitespace；永不 favorable commercial picture → TGT-01…07 de-risked。 |
| E5-5 | **DIRECT 是「两轴完成的 evidence bundle」，不是单条 EvidencePackage。** A. Competitive / clinical landscape 轴 COMPLETE（PUBLIC_PRIMARY authority —— trial registries / regulatory filings / company primary disclosures / primary clinical publications；覆盖 approved / registrational / active / discontinued-failed programs、same-target ADC 与 non-ADC targeted programs、refractory-mCRC relevance；pipeline DB 是 index → 至多 `INDIRECT_STRONG`）**AND** B. Composition-level patent 轴 COMPLETE（真实 patent publications / families / legal-status records；relevant composition claim families / assignees / status / declared jurisdiction / claim-category mapping / congestion-whitespace signals；target-level（非 composition-level）patent search 至多 `INDIRECT_STRONG`；Lens / PATENTSCOPE / Google Patents / EPO 是 discovery / metadata 工具，claim fact 的 canonical provenance 是 actual patent publication / official status source —— index 不是 evidence authority，与 TGT-01 的 ADCdb 规则相同；composition-level patent landscape **不是** FTO judgement）。**新 invariant：absence inference 需要 completion provenance** —— 「no competitor / no patent → whitespace」只有在 complete audited search 返回 no qualifying competitor 时才成立，永不 `records == []`；未来 E6 携带 module-local typed `CompetitiveLandscapeCompletion` / `PatentLandscapeCompletion`（pin `as_of` date / search scope / sources searched / context / unresolved items / completion status）—— run-level machine records，**不是第七个 core object**。 |
| E5-6 | **fatal 不是 scientific fatal：冻结独立的 module-local `sponsor_review` 记录**（与 TGT-05 的 `fatal_review` 不同名、不同路由）。`status` 单值 `POTENTIAL_SPONSOR_FATAL_PATTERN`；字段 `required` / `status` / `evidence_ids` / `competitor_program_ids` / `patent_family_ids` / `landscape_as_of` / `patent_scope`；**不是** EvidencePackage / CandidateGateAssessment / Decision / Gate fatal flag / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE。machine 至多检测 candidate pattern（same target + ADC + same mCRC context + approved OR registrational + primary-source verified + composition-level patent congestion present）→ `required = true`。machine 永不断言 "dominant" / "well protected" / "no differentiation path" / "this sponsor should stop" —— 全部 human / sponsor-governance reserved。`sponsor_review` 路由到 external sponsor governance（`SearchSpaceAdmission` / `ProgramCommitmentReview`）on the sponsor-relative axis，绝不走 scientific `fatal_gate_policy`。 |
| E5-7 | **stop rule：两轴 completeness + freshness；不是「搜到一个 competitor 就停」。** item 10 pin `landscape_as_of` / `retrieval_window` / mCRC context / canonical target identity / patent search scope-jurisdictions。competitive-landscape 轴与 composition-level patent 轴都必须达到 coverage completeness；某一轴没搜（且 target-specific assessment 已 attempt）→ `INCONCLUSIVE / UNKNOWN`。DIRECT 要求两轴都到 DIRECT authority。sponsor-review provisional stop：发现 approved / registrational same-target mCRC ADC + strong composition-level congestion pattern → 置 `sponsor_review`、暂停追更弱证据、handoff —— 但两个 core 轴的 completeness 仍必须满足。TGT-08 **不用** `EXPERIMENT_REQUIRED` —— FTO 不是实验问题。 |
| E5-8 | items 10–17 直接继承 E2 / E4 runtime genes —— Item 10 canonical target identity（single authoritative、no separate drift-prone arg）+ Instantiation identity / refractory mCRC context / PUBLIC_ONLY / run_id / `landscape_as_of` / retrieval-search scope / existing evidence refs；Item 11 atomic Gate-neutral immutable-by-ID EvidencePackage + full provenance + exact canonical reuse（competition EP 陈述 program fact，patent EP 陈述 claim / status fact，永不 Gate-relative conclusion）；Item 12 non-canonical proposal envelope（无 assessment_id / assessment_version / review），`sponsor_review` 独立；Item 13 machine acceptance（source / EP refs 可解析、无 duplicate source-claim、frozen ladder classes only、Strength ≤ ceiling、two-axis completeness、absence-based whitespace claim 有 completion provenance、无 FTO wording / conclusion、无 TGT-01…07 scientific inference、无 sponsor Decision / KILL；hard identity-provenance inconsistency → machine reject / proposal = None）；Item 14 human review；Item 15 / 16 / 17 见 E5-4…E5-7；禁止 `sponsor_review` → canonical scientific fatal → KILL。 |

一句话（审核方原话，放在施工图醒目位置）：
- **TGT-08 evaluates the external opportunity landscape; it does not evaluate the
  target's scientific validity and it does not decide whether this sponsor
  should proceed.**
- **IP whitespace is an evidence-backed landscape signal. It is not freedom to
  operate.**

## 四轮历史（初次提交 + 3 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `502bc4f2`（首版：TGT-08 construction contract + drawing + 45 tests，全量 963） | `REQUEST_CHANGES`。**大部分 PASS**（design-only scope、E1 17-item template、03/05/07/08 PR D parity、三层边界、`NEGATIVE` 可达但不等于 KILL / sponsor stop、FTO 边界、DIRECT 双轴、absence inference 需 completion provenance、`sponsor_review` 独立 module-local trigger、E2/E4 genes、MOD-TGT08 仍 `0.0.0`、`MIGRATION_PENDING`）。2 个 narrow Direction × Strength / two-axis blocker。 |
| 2 | `c65990e`（第一轮修订，48 tests / 全量 966） | `REQUEST_CHANGES`。上一轮 2 blocker 均关闭。1 个 residual —— WEAK unmet-need exception 与 two-axis completion rule 冲突。 |
| 3 | `e8d409e`（第二轮修订，49 tests / 全量 967） | `REQUEST_CHANGES`。上一轮 blocker 已在 item 06/15/16 + drawing 关闭。1 个极窄残余 —— item 13 machine acceptance 还保留旧的广义 UNKNOWN 规则。 |
| 4 | `3e5a551`（第三轮修订，49 tests / 全量 967） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 2 个 blocker（`502bc4f2` → `c65990e`）

1. **Drawing item 06 把 "two-axis coverage complete" 错写成 "DIRECT"**
   （"at DIRECT if both axes complete, else INDIRECT_STRONG"），与同施工图
   item 16 自相矛盾。修：冻结正确规则 —— overall Strength = **weaker required
   axis ceiling**（competitive DIRECT + patent DIRECT → overall DIRECT；任一只到
   INDIRECT_STRONG → overall capped INDIRECT_STRONG）。新增 item 06
   `strength_is_the_weaker_required_axis_ceiling`；item 13（overall
   proposed_strength == weaker required axis ceiling；"both axes searched" alone
   never DIRECT）；item 16 `direct_requires`（"at DIRECT authority"）+
   `coverage_complete_is_not_direct_quality`；drawing item 06/13/16 行同步；
   3 个 regression。
2. **Frozen truth table 缺「landscape 完整、有有效 grade、但没有 directional
   signal」这个合法状态**（既无 material SUPPORTS_OPPORTUNITY 也无 material
   OPPOSES_OPPORTUNITY）。修：新增 **graded INCONCLUSIVE** ——
   `INCONCLUSIVE / DIRECT` 或 `INCONCLUSIVE / INDIRECT_STRONG`（按 overall
   rung），带非空 evidence_refs（CONTEXTUAL landscape packages）；item 06
   `graded_inconclusive_vs_unknown` 严格区分二者（"we could not look" vs "we
   looked well and the evidence does not resolve direction"，引用 PR A 允许
   INCONCLUSIVE + graded strength + evidence_refs）；items 13 / 15 + drawing
   更新；truth table incomplete key 改名；1 个 regression。

## 第二轮 REQUEST_CHANGES 的 blocker（`c65990e` → `e8d409e`）

**WEAK unmet-need exception 与 two-axis completion rule 冲突。** 第一轮修订写的
"two coverage-complete axes are the PRECONDITION for a graded (non-UNKNOWN)
assessment" 与冻结的 item 06 "indication-level unmet need only → INCONCLUSIVE /
WEAK"（一个不需要任何轴完成的 graded 非-UNKNOWN 状态）冲突。修（不改任何 Gate
science）：冻结显式 precedence —— two-axis mandatory completion 是
**target-specific DIRECT / INDIRECT_STRONG** opportunity assessment 的前提，
**不是** frozen unmet-need-only WEAK hypothesis 的前提。(a) 只有 indication-level
unmet-need evidence、没有 attempt 任何 target-specific competitive/IP read →
`INCONCLUSIVE / WEAK`；(b) attempt 了 target-specific landscape assessment 且某
mandatory axis incomplete → `INCONCLUSIVE / UNKNOWN`。新增 item 06
`unmet_need_only_vs_incomplete_target_landscape`；改写 item 06
`strength_is_the_weaker_required_axis_ceiling`（WEAK exempt）+ item 16
`one_axis_not_done`（EXCEPTION 子句）+ `coverage_complete_is_not_direct_quality`
+ item 15 `weak_unmet_need_only` / `incomplete_landscape` + drawing item
06/15/16 行；truth table 两行 key 改名；never 加 "unmet-need-only with no
target-specific read attempted → UNKNOWN"；1 个 regression。

## 第三轮 REQUEST_CHANGES 的 blocker（`e8d409e` → `3e5a551`）

**item 13 machine acceptance 还保留旧的广义 UNKNOWN 规则。** item 13 的
truth-table 判定句同时写 "unmet-need-only → INCONCLUSIVE / WEAK" 与 "a
materially incomplete landscape or an unsearched mandatory axis → INCONCLUSIVE
/ UNKNOWN"，没有像 item 06/15/16 那样加 "only when a target-specific landscape
assessment was attempted"。修（只改 item 13 一句 + regression）：改成
"unmet-need-only WITH NO target-specific competitive/IP read attempted →
INCONCLUSIVE / WEAK；a target-specific landscape assessment WAS attempted and a
mandatory axis is incomplete, OR there is no admissible evaluable landscape →
INCONCLUSIVE / UNKNOWN"（与 item 06/15/16 precedence 一致）；drawing item 13 行
同步；`test_unmet_need_only_weak_is_exempt_from_the_two_axis_completion_rule` 扩展
一条 item 13 断言。

## 第四轮 APPROVE（`3e5a551`）

审核方逐条复核：最后一个 residual blocker 已关闭 —— item 13 machine acceptance
现在与 items 06/15/16 使用同一 precedence（unmet-need-only 且没有开始
target-specific competitive/IP read → INCONCLUSIVE / WEAK；一旦 target-specific
landscape assessment 已开始、而 mandatory axis 不完整或不存在 admissible
evaluable landscape → INCONCLUSIVE / UNKNOWN）；对应 regression 也同时锁住两条
路径，防止以后再次退回泛化的 "unsearched axis → UNKNOWN" 规则。

**APPROVE PR #114。可以 merge。** PR E5 的 TGT-08 construction contract 到此冻结。
下一步按既定流程进入 **PR E6 = MOD-TGT08@1.0.0 deterministic implementation**，
严格实现 E5，不再重新解释 TGT-08 semantics。

CI（GitHub Actions `verify`，python 3.11 + 3.12）对 `502bc4f2` / `c65990e` /
`e8d409e` / `3e5a551` 均 `success`。全量 `unittest discover`：round 3 后本地 967
（唯一本地 FAIL 是既有 `test_assetgenos_modules` 的 `__pycache__` 物理扫描噪音，
在 stash 掉本次改动的 pristine tip 上同样 FAIL，CI 干净 checkout 上 GREEN）。

GitHub connector 四轮都返回 `403 Resource not accessible by integration`，
REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
为 authoritative。
