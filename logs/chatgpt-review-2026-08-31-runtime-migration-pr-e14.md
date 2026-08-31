# ChatGPT 审核记录：Runtime Migration PR E14 —— MOD-TGT06@1.0.0 deterministic implementation

- 日期：`2026-08-31`
- PR：#132 `task_20260831_runtime-migration-pr-e14`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求 / 逐轮回复贴入该对话）
- 被审核 HEAD：`7b87a58`（第二轮修订后）
- Merge 提交：`d65a5a7`（`Merge pull request #132 from leezx/task_20260831_runtime-migration-pr-e14`）
- 结论：**APPROVE @ `7b87a58`**。「APPROVE — MOD-TGT06@1.0.0 implementation 可以
  merge。合并后 7 / 8 primary Modules implemented，MIGRATION_PENDING 继续保留；
  下一步进入最后一个 TGT-07 / MOD-TGT07 的 design-contract → implementation
  流程。」GitHub connector 每轮均 `403 Resource not accessible by integration`，
  REQUEST_CHANGES / APPROVE 的 GitHub review state 未回写；`AI审核方案` 对话结论
  为 authoritative。

本记录在**独立 docs-only PR**（`task_20260831_runtime-migration-pr-e14-approval-record`）
中补登，按 PR #95 … #131 先例。本 PR 同时把
`manifests/runtime_migration_pr_e14_manifest.yaml` 补成 approved。不改 PR E14 的
package、测试或 handoff 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e14_manifest.yaml` 的 `scoping_decisions`
（E14-1…E14-8）、`six_required_implementation_tightenings`（逐字）与
`frozen_proposal_evidence_role_mapping`，以及
`docs/handoff/2026-08-31-runtime-migration-pr-e14.zh-CN.md`。要点：

- E14 是 **RUNTIME_IMPL_ADD**，与 E2 / E4 / E6 / E8 / E10 / E12 同型：交付
  `gate_modules/tgt06_internalization_trafficking_addressability/` 的 11 文件
  确定性科学核心 + `tests/test_tgt06_module.py` + 窄 binding / registry
  reconciliation + manifest / handoff / worklog append。严格实现冻结的 PR E13
  施工合同，不改 E13 science。
- **APPROVE-to-proceed** + **6 个 required implementation tightenings**（T1 outcome-aware
  INDIRECT_STRONG；T2 single classifier authority；T3 configuration id
  canonicalise at provider boundary；T4 exact audit identity；T5 reuse / dedup
  parity 加 antibody / epitope / affinity / conjugation identity fields；T6
  neutral-claim number 不是 threshold）+ frozen proposal-relative EvidenceRole
  mapping。
- `run()` 纯 Python，只调 injected port；包内不建 normalizer / scorer /
  threshold / generic framework；不对 source-reported internalization number 做
  numeric coercion。TGT-06 `primary_module_version` `0.0.0 → 1.0.0`；
  `MIGRATION_PENDING` 保持（8 个 primary Module 建成 7 个，余 TGT-07）。

## 提交与 CI

- 分支 `task_20260831_runtime-migration-pr-e14`，基线 `origin/main` @ `aa80865`。
- 初始提交 `0b1907f`：11-file package + 67-test suite + binding reconciliation +
  manifest + handoff + worklog。本地全量 unittest 1702 OK。PR #132，CI（python
  3.11 + 3.12 matrix）绿。

## Review round 1 → REQUEST_CHANGES（3 窄 runtime blocker，全部 CLOSED）

被审核 HEAD `0b1907f`；exact-head CI run 33438218339 success。

1. **classifier authority over-expansion**：`classify.py` 的 generic positive
   fallback（`outcome ∈ {PRODUCTIVE, DELIVERY_UNRESOLVED} → INDIRECT_STRONG /
   SUPPORTS`）会把 disease-relevant PRODUCTIVE 但 `assay_validation_status` /
   `context_adequacy_status` `NOT_ESTABLISHED` 的 observation 自动升成 positive
   INDIRECT_STRONG，与 classifier 自己的注释矛盾。→ 删除 generic fallback，正向
   INDIRECT_STRONG rung 改为 kind / context / outcome specific：disease-relevant
   PRODUCTIVE + assay / context 未 QUALIFIED → `CONTEXTUAL`, non-qualifying；
   `NON_CRC_CONTEXT` PRODUCTIVE → `INDIRECT_STRONG`；`DELIVERY_UNRESOLVED` →
   `INDIRECT_STRONG`（frozen lower ceiling）；`FAILS` 永不 positive IS。加 regression。

2. **proposal EvidenceRole mapping drift**：(2A) `POSITIVE / DIRECT` 把
   conflicted-config productive EP 标 `SUPPORTING`；(2B) `NEGATIVE / DIRECT` 把
   DIRECT-quality failure EP 标 `CONTRADICTING`，且
   `AssessmentProposalEnvelope` + `acceptance.py` 强制「NEGATIVE 必须含
   CONTRADICTING」= 第二套 role semantics。→ `aggregate.py` + `contracts.py`
   `AssessmentProposalEnvelope` + `acceptance.py` 三处同步冻结 proposal-relative
   mapping：`POSITIVE / DIRECT` 仅 CLEAN productive → `SUPPORTING`，conflicted-config
   productive 与 other-config failure → `CONTEXTUAL`；`NEGATIVE / DIRECT` failure
   EP → `SUPPORTING`（不要求 `CONTRADICTING`）；`CONFLICTING / DIRECT` 保留
   same-config productive `SUPPORTING` + same-config failure `CONTRADICTING`；
   `CONTRADICTING` 只出现在 `CONFLICTING / DIRECT`。不改 Direction science。

3. **IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE allowed-kind boundary 未执行**：
   contract 冻结了三个结构态但没执行 E13 的科学适用范围（第三态在当成
   「恰好没达到 DIRECT」的通用 fallback）。→ constructor 现在强制第三态只允许
   `CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY` /
   `SAME_TARGET_ADC_DELIVERY_PRECEDENT` / `RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE`
   / `SURFACE_LOCALIZATION_ONLY_INFERENCE` / `SEARCH_COMPLETION_AUDIT`，或
   `NON_CRC_CONTEXT` 的 internalization / trafficking family kind。disease-relevant
   / unresolved family observation 无 disclosed `SINGLE` / `IDENTIFIED_MULTI`
   identity → HARD `ValueError`。删除 `classify.py` 中已冗余的 HARD 分支；按
   frozen identity boundary 修正 `test_trafficking_only_asymmetric_authority`。

修订提交 `44ad6da`（触及 `classify.py` / `contracts.py` / `aggregate.py` /
`acceptance.py` / `tests/test_tgt06_module.py` / manifest / worklog；`completion.py`
/ `fatal_review.py` / `evidence.py` / binding / PR D+E13 science / 其它 Module
未动）。tests 67 → 77（+10 regression）。本地全量 1712 OK。CI（exact-head run
33441561489）绿。

本轮 ChatGPT 明确判定正确、不要改：11-file package、`treatment_state`
`not_applicable`、三种 failure kind 统一 `DIRECT` + `OPPOSES`、ordered 7-step
aggregation、`configuration_identity_projection` helper、six legal pairs、v1 no
conflict resolver、completion 四轴、exact audit identity、no
`qualifying_indirect_configuration_ids`、fatal productive-DIRECT cancellation、
Route A / B、TGT-06 binding 1.0.0、7 / 8 built、`MIGRATION_PENDING`、其它 Module
不重构、binding reconciliation APPROVE。

## Review round 2 → REQUEST_CHANGES（round-1 Blocker 1 / 2 CLOSED + 1 residual，CLOSED）

被审核 HEAD `44ad6da`；exact-head CI run 33441561489 success。Round-1 的 Blocker
1（classifier authority）与 Blocker 2（EvidenceRole mapping）判定 CLOSED。

- **residual — third-state NON_CRC exception 仍过宽**：constructor 的 NON_CRC
  第三态 exception 用 `_DIRECT_QUALITY_FAILURE_KINDS`（含
  `TRAFFICKING_OR_RECYCLING_ONLY`），于是 `NON_CRC_CONTEXT` +
  `TRAFFICKING_OR_RECYCLING_ONLY` + 无 config id 仍被接受。frozen E13 的 exception
  只覆盖「non-CRC **antibody-induced internalization** observation whose source
  does not identify the tested configuration」——`TRAFFICKING_OR_RECYCLING_ONLY`
  按定义不是 antibody-induced internalization observation。→ 新增
  `_THIRD_STATE_NON_CRC_EXCEPTION_KINDS = (ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING,
  ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY)`，NON_CRC exception 改用它。
  `NON_CRC_CONTEXT` + `TRAFFICKING_OR_RECYCLING_ONLY` 无 disclosed identity →
  HARD `ValueError`。加 regression；`NON_CRC` +
  `ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY` undisclosed-config 路径保持 valid。

修订提交 `7b87a58`（触及 `contracts.py` + `tests/test_tgt06_module.py` +
manifest + worklog，one-line authority narrowing + one regression，无重构）。
tests 77 → 78。本地全量 1713 OK。CI（exact-head run 33444465000）绿。

## Review round 3 → APPROVE @ `7b87a58`

被审核 HEAD `7b87a58`；exact-head CI run 33444465000 success。Round-2 residual
完整关闭：`_THIRD_STATE_NON_CRC_EXCEPTION_KINDS` 严格只有两种 antibody-induced
internalization kind；constructor 用这个窄 tuple；`TRAFFICKING_OR_RECYCLING_ONLY`
+ `NON_CRC_CONTEXT` + no config 不再进入 third state；新 regression 锁定；non-CRC
antibody-induced internalization 未披露 configuration 的合法路径保留。Round-1 的
classifier authority over-expansion 与 proposal-relative EvidenceRole mapping
两个 blocker 保持 CLOSED。

**结论：APPROVE — MOD-TGT06@1.0.0 implementation 可以 merge。**

## Merge

- PR #132 `task_20260831_runtime-migration-pr-e14` 于 `2026-08-31` 以 `--merge`
  合入 `main`，merge 提交 `d65a5a7`。
- 独立 docs-only PR `task_20260831_runtime-migration-pr-e14-approval-record`
  补登：本审核记录（3 轮完整往返 + merge）+
  `manifests/runtime_migration_pr_e14_manifest.yaml` →
  `status: approved` / `chatgpt_review: APPROVE` / `approved_tip: 7b87a58…` /
  `merge_commit: d65a5a7` / `review_rounds: 3` / `test_count_at_approval: 1713` /
  `approval_record_pr` / `review_round_1/2/3` block。不改 PR E14 的 package、
  测试或 handoff 内容。
- 状态：8 个 primary Module 施工合同已 APPROVE 7 个；**已实现 7 个**
  （TGT-01/02/03/04/05/06/08 @ 1.0.0）。`MIGRATION_PENDING` 保持。
- Next：fatal-first 余下 **TGT-07**：PR E15 = 施工合同（需独立 go-ahead），
  PR E16 = 实现。8 个 primary Module 全部建成后才解除 `MIGRATION_PENDING`。
