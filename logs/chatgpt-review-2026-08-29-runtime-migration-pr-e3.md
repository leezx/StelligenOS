# ChatGPT 审核记录：Runtime Migration PR E3 —— TGT-05 / MOD-TGT05 Construction Contract

- 日期：`2026-08-29`
- PR：#110 `task_20260829_runtime-migration-pr-e3`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`359744c`（第一轮修订）
- Merge 提交：`b0e452a`（`Merge pull request #110 from leezx/task_20260829_runtime-migration-pr-e3`）
- 结论：**APPROVE @ `359744c`**。E3 construction contract 冻结。下一步 PR E4 =
  MOD-TGT05@1.0.0 deterministic implementation，严格实现 E3，不再重新解释 TGT-05
  scientific semantics。非阻断 note：E4 把 `fatal_review.status` enum 固定成
  `POTENTIAL_FATAL_PATTERN` 即可，`FATAL_REVIEW_REQUIRED` 作为 `required=true`
  的语义说明、不必第二个 status。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e3-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 / #105 / #107 / #109 先例。本 PR 同时
把 `manifests/runtime_migration_pr_e3_manifest.yaml` 补成 approved。不改 PR E3 的
施工合同、drawing 或测试内容。

## 8 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

| # | 决策 |
|---|---|
| E3-1 | 下一 in-repo PR = TGT-05 / MOD-TGT05 Construction Contract（design-only，PR E4 才实现 `MOD-TGT05@1.0.0`）。machine identity `TGT-05@1.0` / `ADC_TARGET_GATESET@1.0` / L04 / `INST-CRC-REFRACTORY-ADC-TARGET-v1` / `MOD-TGT05` / `module_version 0.0.0`；顺序不变；PR D TGT-05 science 一字不改。 |
| E3-2 | 严格 design-only：contract + drawing + 17 项 checklist + validation/parity tests + manifest/handoff/worklog。禁止 implementation / provider / adapter / runner / network / external data / runtime EP 或 proposal / numeric scoring / new ladder semantics。**不建** generic GateModule framework / abstract base class，**不重构** MOD-TGT01。 |
| E3-3 | 17 项模板复用**已批准的 E1 模板**（PR E2 已验证），provenance `not_claimed_verbatim_from_blueprint`。item **03 / 05 / 07 / 08** 与冻结 PR D `crc_adc_target_gateset.yaml:TGT-05` 做 **normalized-equality parity test**。 |
| E3-4 | TGT-05 冻结成**单向 liability detector**，绝不 safety predictor。Direction 描述证据、非 candidate desirability；`NEGATIVE` 在 public path 上基本不可达（HPA/RNA/IHC negative、一个没报毒的临床项目都不能产生 `NEGATIVE = safe`）；Module 不 flip Direction；`HOLD/KILL` 是 GateSet Decision policy 的事。 |
| E3-5 | fatal semantics 把「单产品毒性」（DIRECT liability，非 target-wide fatal）与「target-intrinsic convergence」（≥2 materially distinct 同靶点 ADC construct + convergent target-mediated normal-tissue toxicity）彻底分开。每条 clinical ADC toxicity observation 可审计 construct fingerprint（antibody/binder、linker、payload、format）+ observed severity FOR THIS PRODUCT（不升 target-wide）+ target-attribution basis + primary source。「materially distinct」与「真 target-mediated」保留 human-review。无 numeric severity score、无 KILL。 |
| E3-6 | source plan 显式区分「liability evidence」与「vital-organ coverage completeness」。DIRECT/INDIRECT_STRONG/WEAK source class 按 PR D，硬锁 RNA-only ✗→ protein / whole-tissue protein ✗→ cell-surface accessibility / non-ADC severity ✗→ ADC / negative atlas ✗→ safety。coverage map CNS/cardiac/hepatic/pulmonary/hematopoietic/GI。无 universal threshold。PUBLIC_ONLY path only。 |
| E3-7 | asymmetric fatal-sweep-mandatory stop rule（Path A / Path B / Path C）。核心「absence of public risk evidence is not a stop condition for safety」。 |
| E3-8 | items 10–17 直接**冻结**（不再复制 E2 代码）PR E2 已验证的 runtime genes：single authoritative canonical target identity、canonical SourceIndex provenance authority、Gate-neutral atomic EvidencePackage、exact canonical EP reuse、classification-driving semantic parity on reuse、non-canonical proposal envelope、hard identity/provenance failure → machine reject、`UNKNOWN` ≠ integrity failure、no Decision / KILL / persistence / numeric score。 |

一句话（审核方原话）：**MOD-TGT05 的任务不是证明一个 target"安全"，而是尽可能
可靠地发现 target-level normal-tissue liability；public evidence 可以强力证实
风险，却通常不能证实风险不存在。** 这是 TGT-05 与 TGT-01 最大的科学结构差异。

## 两轮历史（初次提交 + 1 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `0b8ec4f`（首版：TGT-05 construction contract + drawing + 32 tests） | `REQUEST_CHANGES`。**大框架 PASS**（design-only、17 项完整、03/05/07/08 parity、MOD-TGT05 仍 0.0.0、MOD-TGT01@1.0.0 未动、无 provider/persistence/scoring/threshold/therapeutic-window、`MIGRATION_PENDING`）。2 个 E3 construction-contract 自身确定性 blocker。 |
| 2 | `359744c`（第一轮修订，41 E3 tests / 862 全量） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 2 个 blocker（`0b8ec4f` → `359744c`）

1. **item 06 Direction×Strength truth table 自相矛盾。** 同时写「任一 graded
   admissible liability evidence → POSITIVE」与「只有 WEAK RNA-level signal →
   INCONCLUSIVE」，而 PR D WEAK ceiling 是「liability cannot be graded;
   hypothesis only」。修：唯一 `frozen_truth_table`（`DIRECT` liability →
   `POSITIVE / DIRECT`；`INDIRECT_STRONG` → `POSITIVE / INDIRECT_STRONG`；
   `WEAK`-only hypothesis → `INCONCLUSIVE / WEAK`；无 qualifying evidence +
   coverage incomplete/exhausted → `INCONCLUSIVE / UNKNOWN`；never absence-of-risk
   → `NEGATIVE / safe`）+ `positive_precedence_over_coverage_gaps`（已确立的
   DIRECT/INDIRECT_STRONG liability 不因某 vital organ 未覆盖降回 UNKNOWN，
   coverage gap 进 `critical_unknowns`）+ 收紧 CONFLICTING（只针对**同一
   liability observation** 的 target-attribution dispute；CONTRADICTING evidence
   不是新的 safety-negative Evidence Ladder class；refutation 不产 NEGATIVE
   rung）。item 13 / 15 绑定；新增 truth-table regression。
2. **Fatal Path A 越过 human-only boundary。** item 16 Path A 让 machine 依据
   「materially distinct」+「truly target-mediated」（正是 item 08
   `human_review_reserved`）直接 `mark PUBLIC_FATAL_SIGNAL_ESTABLISHED`。修：
   Path A 改成纯 machine detection（≥2 条来自不同 program 的同靶点 ADC toxicity
   observation，每条有 auditable construct fingerprint + disclosed
   target-attribution basis，phenotype apparently convergent）→ 置 **non-canonical
   module-local `fatal_review` record**（`required` / `status`
   `POTENTIAL_FATAL_PATTERN` / `evidence_ids` / `program_ids` /
   `construct_fingerprints` / `affected_tissues` / `target_attribution_basis_refs`）
   → provisional stop → human review。machine 永不 emit
   `PUBLIC_FATAL_SIGNAL_ESTABLISHED`；proposal envelope 不带 fatal flag；
   item 08 新增 `machine_output_is_only_a_potential_pattern`，`human_review_reserved`
   增「biologically meaningful convergence」；item 14 surface `fatal_review`
   record 并把三项判断留给 human；item 13 / 17 明确禁止
   `PUBLIC_FATAL_SIGNAL_ESTABLISHED`。**不改 PR A schema，不建第七个 core
   object。** 新增 `FatalReviewIsHumanOnlyTests` regression。

## APPROVE 时的确认（`359744c`）

- Direction×Strength truth table 冻结为唯一映射，不再给 E4 留解释空间；positive
  precedence 锁住；CONFLICTING 限定为同一 liability observation 的
  target-attribution dispute，不创造新的 safety-negative rung。
- Fatal handoff 改成 human-only adjudication：machine 最多产生 non-canonical
  module-local `fatal_review`；`required=true` 时 status 是
  `POTENTIAL_FATAL_PATTERN`；带 contributing evidence_ids / program_ids /
  construct_fingerprints / affected_tissues / target_attribution_basis_refs；
  proposal envelope 不带 fatal flag；machine 明确禁止
  `PUBLIC_FATAL_SIGNAL_ESTABLISHED`；「materially distinct / truly
  target-mediated / biologically meaningful convergence」全部留给 human review。
- 新增 tests 对 truth table、positive precedence、no-negative-rung conflict、
  machine-only potential fatal pattern 都有 regression protection。
- HEAD `359744c`，open、mergeable，CI `verify (3.11 / 3.12)` success。
- E3-1…E3-8、03/05/07/08 parity、fatal 分层、coverage map、asymmetric-stop 概念、
  PR E2 genes、repository policy、`MIGRATION_PENDING` 全程未改。
- 全量测试 862 OK（821 baseline + 41 E3）。

GitHub connector 写 review（APPROVE / REQUEST_CHANGES）两轮都返回
`403 Resource not accessible by integration`，故 GitHub review state 未写回；
审核结论全文在 `AI审核方案` 对话中转述，并由本记录补登。

## 后续（PR E4+，未启动）

- **PR E4** —— MOD-TGT05 实现：新建顶层
  `gate_modules/tgt05_normal_tissue_fatal_liability/`，单向依赖 `src/`；并把
  TGT-05 gate_binding `primary_module_version` `0.0.0 → 1.0.0`。仅在本合同
  APPROVE 后开工，**需用户单独 go-ahead**。
- **PR E5+** —— 逐 Gate 施工图 + 实现，按 `TGT-08 → 02 → 03 → 04 → 06 → 07`
  顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
