# ChatGPT 审核记录：Runtime Migration PR B —— canonical Gate / GateSet / EvidenceLadder / Decision

- 日期：`2026-08-28`
- PR：#100 `task_20260828_runtime-migration-pr-b`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`
- 被审核 HEAD：`51bfadb`（REQUEST_CHANGES 第一轮修订）
- Merge 提交：`d18974b`（`Merge pull request #100 from leezx/task_20260828_runtime-migration-pr-b`）
- 结论：**APPROVE @ `51bfadb`**

本记录在**独立 docs-only PR**（`task_20260828_runtime-migration-pr-b-approval-record`）
中补登，按 PR #95 / #97 / #99 先例——审核记录不落在被批准的 PR branch 上。本 PR
同时把 `manifests/runtime_migration_pr_b_manifest.yaml` 的 `status` /
`chatgpt_review` / `approved_tip` / `review_rounds` / `test_count_at_approval`
补成 approved，并对齐 `defers` 里 CRC specialization 的命名。不改 PR B 的 runtime
合同或测试逻辑。PR body 首版遗留的 `byte-for-byte mirror / 37 tests / 646`
已在 merge 前直接编辑 PR body 修正（审核方点名的两个非 blocker 之一），无新 commit。

## 两轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `6ff2420`（PR B 首版：`gate_contracts.yaml` + `gate_model.py` + `legacy_gate_map.py` + 37 tests） | `REQUEST_CHANGES`，架构方向 / scope 正确、无越界；3 个 runtime-contract correctness 问题 + 2 个非 blocker |
| 2 | `51bfadb`（同一 PR 一轮修订，49 tests） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 3 点及关闭方式

### 1. canonical GateSet identity 不是 invariant（blocker）

`CANONICAL_GATESET_IDS`（15 个 canonical id）只是常量，未被使用。`Gate` /
`GateSet` 只校验 `gateset_id` 正则 + `candidate_level ∈ L00–L14`，因此
`GateSet(gateset_id="ADC_TARGET_GATESET", candidate_level="L05")` 与
`GateSet(gateset_id="FOO_GATESET", candidate_level="L04")` 都能通过。`GateSet.gates`
不检查 member `gate_id` 唯一。`CRC-ADC-TARGET-GATESET-v1` 在 `gate_contracts.yaml`
里被当成一个"具体第二 gateset_id"。

→ `gate_model.py` 新增 `_require_canonical_gateset(candidate_level, gateset_id,
where)`，在 `Gate` / `GateSet` / `Decision` 三处 `__post_init__` 强制
`gateset_id == CANONICAL_GATESET_IDS[candidate_level]`；`Decision` 从
`candidate_id`（`CAND-Lnn-nnnnnn` → `Lnn`）解析 level 后做同样约束。`GateSet`
增 member `gate_id` 唯一性校验（同 GateSet 下 `TGT-04` v1 + `TGT-04` v2 raise），
理由：Decision `assessment_snapshot` 是 `gate_id → 单个 assessment`，重复
`gate_id` 无法无歧义决策。`gate_contracts.yaml`：`migration.deferred` 键
`concrete_gateset_CRC_ADC_TARGET_GATESET_v1` →
`crc_adc_target_specialization_of_ADC_TARGET_GATESET`，正文明确
"CRC-ADC-TARGET-GATESET-v1 是 program / specialization 概念，**NOT a new
canonical gateset_id**；`gateset_id` 永远是 15 个 canonical id 之一；
context-specific specialization 由 `Instantiation`（如
`INST-CRC-REFRACTORY-ADC-TARGET-v1`）+ 针对同一 canonical `ADC_TARGET_GATESET`
的 context-specific `gateset_binding` / `gate_binding` refs 表达 —— 正是冻结
Data Layout v1 的物理结构"。新增顶层 `gateset_identity` 块（`rule` /
`candidate_level_source` / `member_uniqueness`），Gate / GateSet / Decision
各加对应 invariant。PR D 冻结 CRC-specific binding refs 与 TGT-01..TGT-08
ladder，不再发明第二套 GateSet identity。
新增测试：三对象非 canonical 配对 raise、canonical 配对通过、GateSet 重复
`gate_id` raise、Decision 从 `candidate_id` 解析 level 并强制 canonical、
specialization key 已改名且正文含 "NOT a new canonical gateset_id"。

### 2. Decision `triggered_by` ↔ `assessment_snapshot` 无 cross-field 一致性（blocker）

历史 provenance 可自相矛盾：一个 Decision 可以 `triggered_by` 某个 gate 的某个
assessment，而 `assessment_snapshot` 对同一 gate pin 的是另一个 assessment、
甚至 `NOT_EVALUATED`。

→ `Decision.__post_init__` 对每个 `TriggeredBy t` 要求：`t.gate_id ∈
assessment_snapshot`；`snapshot[t.gate_id] != "NOT_EVALUATED"`；
`snapshot[t.gate_id].assessment_id == t.assessment_id`；
`.assessment_version == t.assessment_version`。不要求 snapshot 的每个 gate
都出现在 `triggered_by`（snapshot 是完整状态，`triggered_by` 是决策关键原因）。
这是 Decision 对象的 intrinsic invariant，不是 decision engine。
新增 reject 测试：trigger gate 不在 snapshot → invalid；trigger gate =
`NOT_EVALUATED` → invalid；trigger `assessment_id` 或 `assessment_version`
与 snapshot pin 不符 → invalid；外加 "snapshot 含未出现在 `triggered_by` 的
gate" 正例。

### 3. "exact parity" 措辞不真实（blocker）

文档 / 测试声称 Decision 与 `decision.schema.json` "byte-for-byte / exact
parity"，但 runtime 实际更严：schema 无 `minProperties`，`assessment_snapshot:
{}` 是 schema-shape-valid，runtime 拒绝；schema `triggered_by[].gate_id` 只是
string，runtime `_require_text` 要求非空；schema `gateset_version` 只是
string，runtime 要求非空。

→ 保留所有 runtime 更严的 invariant（不放松任何 validator，不改冻结
`decision.schema.json`）。`migration.parity.Decision.kind`：`exact` →
`schema_shape_exact_runtime_semantics_stricter`，加
`relationship: runtime_valid_is_a_strict_subset_of_schema_valid` 与 `rule`：
"Runtime MUST NOT accept anything the frozen schema rejects on an intrinsic
shape / type / enum / pattern constraint, but MAY additionally impose
cross-field and domain invariants the persistence schema cannot express"。
延续 PR A 的 "Python executable mirror + parity test" 原则。`Decision.parity`
行、`gate_model.py` 模块 docstring 与 section 注释同步。新增
`SchemaRuntimeRelationshipTests`：断言 `kind != "exact"` 且有
`relationship` / `rule`；断言 `assessment_snapshot: {}` 是 schema-shape-valid
（schema 无 `minProperties`）但 runtime raise；`gateset_version: ""` 同理；
`gateset_identity` 块存在且 `rule` 提及 canonical、含 `member_uniqueness`。

## 两个非 blocker（未再开审核轮）

1. **PR body 首版描述过期**（`byte-for-byte mirror / 37 tests / 646`）。
   已在 merge 前直接编辑 PR #100 body 为 stricter runtime semantics / 49 new /
   658，无新 commit。
2. `LadderRung.admissible_evidence_classes` 应拒绝 `("",)`（顺手改）；handoff
   "不 import / 不改 `gates.py`" 表述不准确 → 改为 "只读 import，不修改"
   （`legacy_gate_map.py` 的 compatibility self-check 确实 import
   `GATE_CATALOG` / `GATE_GROUPS` / `GATE_IDS`，代码行为本身正确）。

## 批准范围（审核方原话要点）

- **APPROVE PR #100 @ `51bfadb`。可以 merge。** 上一轮 3 个 blocker 均已关闭，
  且没有引入新的 PR-B scope 问题。
- Canonical GateSet identity 已成为 runtime invariant：`Gate` / `GateSet` 按
  `candidate_level` 强制唯一 canonical `gateset_id`，`Decision` 从 `candidate_id`
  的 `Lnn` 解析 level 后做相同约束；GateSet member `gate_id` 也要求唯一。
- CRC specialization 的身份问题已收敛：`CRC-ADC-TARGET-GATESET-v1` 明确定义为
  program / specialization 概念，不再 mint 第二套 `gateset_id`；实际表示为
  `Instantiation + canonical ADC_TARGET_GATESET + context-specific binding
  refs`，与已冻结的 Data Layout 物理结构一致。
- Decision provenance 已闭合：每个 `triggered_by` gate 必须存在于
  `assessment_snapshot`，不能是 `NOT_EVALUATED`，且 `assessment_id +
  assessment_version` 必须与 snapshot pin 完全一致。
- schema / runtime 关系现在表述正确：不再错误宣称 `schema-valid ⇔
  runtime-valid`，而是明确 `runtime_valid_is_a_strict_subset_of_schema_valid`
  —— 冻结 schema 管 persistence intrinsic shape，runtime 可以增加
  cross-field / domain invariant。
- Evidence Ladder 仍保持纯 evidence-class ceiling 模型，无 numeric quantity
  score；空 evidence-class string 已被拒绝。
- Legacy 45-Gate 继续保持 `FROZEN_LEGACY`，无 conversion-in-place 或重计数；
  PR B 的新 lineage 与旧 `GateModelOutput.score / status` 保持隔离。
- **非 blocker（不再开轮）：** PR body 首版描述过期（已在 merge 前编辑）；
  generic `Gate` 当前没有全局强制 `gate_id → Candidate Level` 的映射 ——
  **不应在 PR B 扩大；PR D 在实例化 `ADC_TARGET_GATESET` 时必须严格锁死
  TGT-01–TGT-08 的 membership、level 和版本，不能让 Module 自由造 Gate ID。**
- Merge 后可进入 **PR C —— Matrix / provenance / reusable EvidencePackage
  references**。PR B 不需要继续优化。

## 操作层说明

审核方尝试通过 GitHub connector 直接给 PR #100 写入 review 状态
（`REQUEST_CHANGES`、`APPROVE` anchor 到 `51bfadb`），GitHub 每次返回
`403 Resource not accessible by integration`，未能写回 GitHub。GitHub 上 PR
#100 因此没有 formal review 记录，实际两轮意见与最终 `APPROVE` 以本文件与
`AI审核方案` 对话为准。

## 边界

本次批准的是 **canonical Gate 系统的 runtime 合同**
（`src/contracts/gate_contracts.yaml` + `src/objects/gate_model.py` +
`src/objects/legacy_gate_map.py` + 49 tests）与第六个决策层对象 `Decision`
（PR A 延后的对象）。它是四个 runtime-migration PR 的第二个，没有 decision
engine、没有 concrete Evidence Ladder、没有 concrete CRC GateSet
specialization（分别属 PR D / PR C）。合并后 `gate_system.yaml` 的 45-Gate
拓扑 + `GateModelOutput.score` 仍 `FROZEN_LEGACY`，CURRENT_SYSTEM v5 的
`MIGRATION_PENDING` 未解除——到 PR E 合并前 repository runtime 不得声称已实现
Blueprint v1.3 conformance。仓库内不保存运行数据或 `.csv`。

冻结与进度状态：

> Blueprint v1.3：冻结
> CURRENT_SYSTEM v5：冻结
> Data Layout Spec v1.0：冻结
> Runtime Migration PR A（core decision objects）：已合并（PR #98 @ `f225e9f`，`cbab012`）
> Runtime Migration PR B（canonical Gate / GateSet / EvidenceLadder / Decision）：**已合并**（PR #100 @ `51bfadb`，`d18974b`）
> 下一步：Runtime Migration PR C —— Matrix / provenance / reusable EvidencePackage references
