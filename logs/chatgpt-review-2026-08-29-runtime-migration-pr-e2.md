# ChatGPT 审核记录：Runtime Migration PR E2 —— MOD-TGT01 Implementation

- 日期：`2026-08-29`
- PR：#108 `task_20260829_runtime-migration-pr-e2`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`72546a3`（第四轮修订）
- Merge 提交：`5b92dee`（`Merge pull request #108 from leezx/task_20260829_runtime-migration-pr-e2`）
- 结论：**APPROVE @ `72546a3`**。`MOD-TGT01@1.0.0` 视为 E1 frozen construction
  contract 的合格 deterministic implementation。`MIGRATION_PENDING` 继续保持。
  下一步进入真实 provider / external calibration，或按既定顺序开 TGT-05 的
  construction drawing —— 各自需单独 go-ahead。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e2-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 / #105 / #107 先例。本 PR 同时把
`manifests/runtime_migration_pr_e2_manifest.yaml` 补成 approved。不改 PR E2 的
Module 实现、合同或测试。

## 8 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

| # | 决策 |
|---|---|
| E2-1 | E2 是真正的确定性实现（非 skeleton），`module_version 1.0.0`；无 CLI / crawler / DB / 后台任务 / review UI。 |
| E2-2 | Module 内无 source-specific live provider，只有 normalized `Tgt01PrecedentProviderPort`；`failure_attribution` 的 target-attributable 类必须来自明确 primary-source disclosure，Module 不做 NLP 推断。 |
| E2-3 | ADCdb 在 port 之后；未解析行是 retrieval lead，永不确立 ladder rung。 |
| E2-4 | 输出全是 in-memory `Tgt01ModuleRunResult`；`evidence_id` 由 injected allocator 给；零 persistence。 |
| E2-5 | Direction × Strength 确定性、严格 E1 语义、无 score、无第四套 ladder；adverse pattern 只有满足冻结 item 08（≥2 独立同靶点 program、consistent frozen adverse class）才成立；单个 failed ADC 永不 NEGATIVE / fatal。 |
| E2-6 | stop rule 是 machine-enforced prerequisite：`same_target_program_inventory_complete` 与 `failure_reason_sweep_complete` 都为真才可产可接受 proposal，positive ceiling 不能提前停。 |
| E2-7 | 一次极窄的 repository-policy reconciliation：允许顶层 `gate_modules/` 源码；live retrieval / execution / persistence 仍 forbidden；TGT-01 `primary_module_version` `0.0.0 → 1.0.0`。E1 施工合同正文与 TGT-01…08 Gate science 一字不动。 |
| E2-8 | CI 只跑 synthetic / in-memory 用例，synthetic `TARGET_A` / `PROGRAM_A`。 |

边界一句话：PR E2 owns「normalized evidence → Gate-specific interpretation →
EvidencePackages → proposal envelope」；不 own「web retrieval → database / cache
→ source registry persistence → human approval → canonical persistence」。

## 五轮历史（初次提交 + 4 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `57d0c99`（首版：`gate_modules/` + 33 tests） | `REQUEST_CHANGES`。**外层 architecture PASS**；4 个 deterministic-core correctness blocker。 |
| 2 | `decaec7`（第一轮修订，44 tests） | `REQUEST_CHANGES`。#1 / #2 / #4 关闭；#3 只关闭一半。 |
| 3 | `1be6bb2`（第二轮修订，45 tests） | `REQUEST_CHANGES`。3b（hard integrity → machine reject）+ exact canonical EP reuse 主体关闭；剩 canonical-reuse semantic identity。 |
| 4 | `a7a91f7`（第三轮修订，46 tests） | `REQUEST_CHANGES`。classification-parity 主体 + 三条 drift regression 正确；剩 1 个边界条件（缺字段）。 |
| 5 | `72546a3`（第四轮修订，47 E2 tests / 821 全量） | **`APPROVE`** |

## 首轮 4 个 deterministic-core blocker（`57d0c99` → `decaec7`）

1. **Candidate ↔ target identity 未锁死。** `run()` 收独立可漂移的
   `target_identity` 直接给 provider，未与 candidate canonical target 校验；
   record/EP 只存 `target_relation` 布尔。修：`target_identity` 移到
   `Tgt01ModuleInput`（唯一权威），`run()` 去掉该参数；record 加
   `program_target_identity` +（ADJACENT 必填）`adjacency_basis`；
   `classify_record` 拒 misbinding 与错标 adjacency；EP `study_context` 保留三者。
2. **冻结 item-08 fatal 只实现一半。** 只查 `TARGET_MEDIATED`，缺
   "intrinsically unachievable therapeutic window" branch；"consistent" 被约化。
   修：`FAILURE_ATTRIBUTION_VALUES` 显式 `TARGET_MEDIATED_TOXICITY` /
   `INTRINSIC_THERAPEUTIC_WINDOW`（+ `CONSTRUCT_SPECIFIC` / `NON_TARGET` /
   `UNDISCLOSED`），仍要求 primary-source attribution；`aggregate()` 只有「同一
   frozen class 且 ≥2 个独立同靶点 program」才成 pattern。
3. **PR C reusable EvidencePackage 语义未实现。** `existing_evidence_ids` 没用，
   每条 observation 新建 EP；EP 写成 TGT-01-specific；`SourceRegistryPort` 只返
   bool。修：新增 `ExistingEvidenceLibraryPort`；`SourceRegistryPort` →
   `SourceResolverPort.resolve() -> CanonicalSourceRecord | None`；EP 改为
   Gate-NEUTRAL。
4. **`program_id → evidence_id` 数据模型错误，会静默串错 EvidenceRef。**
   修：`build_evidence_packages` 返回 `list[EmittedEvidence]`（一条 observation
   → 一个 EP），`program_id` 只用于 fatal pattern 的 independent-programs 去重。

## 第二轮（`decaec7` → `1be6bb2`）—— blocker 3 的两个剩余问题

- **3a：仍是「复用 EP ID」不是「复用 canonical EvidencePackage」。**
  `ExistingEvidenceLibraryPort.resolve()` 改为返回 `EvidencePackage | None`；
  命中即原样复用（不调 allocator、不建新 body），run result 只按 id 引用。
- **3b：hard identity/provenance failure 被降级成「accepted UNKNOWN」。**
  区分 A（合法「无证据」→ UNKNOWN 可成立）与 B（数据完整性错误 → MACHINE
  REJECT）。`ClassifiedPrecedent` 加 `rejection_severity`（HARD/SOFT）；
  `Tgt01ModuleRunResult` 加 `hard_integrity_failures`；`acceptance.evaluate`
  强制 `len(hard) == 0`。

## 第三轮（`1be6bb2` → `a7a91f7`）—— reused EP classification parity

`_reused_package_is_compatible` 之前只比 `source_id` / `claim` /
`candidate_refs`。修：增补对全部 7 个 classification-driving observation 字段
（`program_target_identity` / `target_relation` / `adjacency_basis` /
`program_stage` / `program_status` / `clinical_activity_disclosed` /
`failure_attribution`）的比对；任一 drift → HARD integrity failure。newly-created
EP 的 `study_context` 补 `clinical_activity_disclosed`。三条 drift regression。

## 第四轮（`a7a91f7` → `72546a3`）—— presence + equality

`if key in existing.study_context and ... != ...` 会让**缺失**某
classification-driving key 的 canonical EP 被静默复用。修：改成 presence +
equality —— key 不在 canonical `study_context` → HARD integrity failure。
regression：canonical EP 缺 `clinical_activity_disclosed` → run rejected。

## APPROVE 时的确认（`72546a3`）

- 最终 blocker 已关闭：reused canonical EP 的每个 classification-driving field
  现在都必须存在且与 current normalized observation 相等；缺字段直接视为
  incompatibility → HARD integrity failure。
- HEAD `72546a3`，open、mergeable，CI `verify (3.11 / 3.12)` success。
- 此前所有 blocker（#1～#4、hard-failure machinery、classification parity）均
  关闭；E2-1…E2-8、Gate id/question、冻结 ladder、allowed/forbidden inference、
  UNKNOWN 语义、repository layout、no-live-provider 边界、no persistence、
  no numeric score、no canonical Assessment/Decision、`MIGRATION_PENDING`、
  TGT-01 `primary_module_version = 1.0.0` 治理方向全程未改。
- 全量测试 821 OK（774 baseline + 47 E2）。

GitHub connector 写 review（APPROVE / REQUEST_CHANGES）五轮都返回
`403 Resource not accessible by integration`，故 GitHub review state 未写回；
审核结论全文在 `AI审核方案` 对话中转述，并由本记录补登。

## 后续（PR E3+，未启动）

- **真实 provider / external calibration** —— 在 `Tgt01PrecedentProviderPort`
  之后接真实只读 provider（ClinicalTrials.gov / PubMed / FDA / patent / ADCdb
  primary-source resolution），external workspace 跑真实 calibration run。
- **PR E3+** —— 逐 Gate 施工图 + 实现，按 `TGT-05 → 08 → 02 → 03 → 04 → 06 →
  07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
