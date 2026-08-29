# ChatGPT 审核记录：Runtime Migration PR C —— Matrix view / reusable EvidencePackage references / provenance walk

- 日期：`2026-08-28`
- PR：#102 `task_20260828_runtime-migration-pr-c`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（本轮改由
  Claude 通过浏览器自动化把审核请求贴入该对话，审核方回复亦在该对话）
- 被审核 HEAD：`d16b634`（REQUEST_CHANGES 第三轮修订）
- Merge 提交：`91a8e5b`（`Merge pull request #102 from leezx/task_20260828_runtime-migration-pr-c`）
- 结论：**APPROVE @ `d16b634`**

本记录在**独立 docs-only PR**（`task_20260828_runtime-migration-pr-c-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 先例——审核记录不落在被批准的 PR branch 上。本
PR 同时把 `manifests/runtime_migration_pr_c_manifest.yaml` 的 `status` /
`chatgpt_review` / `approved_tip` / `review_rounds` / `test_count_at_approval` 补成
approved，并把 `delivers` 里的 provenance-walk checks 更新为两层（derived-index
integrity + canonical-record integrity）。不改 PR C 的 runtime 合同或测试逻辑。PR
body 首版遗留的 `48 tests / 705 OK` 与旧 `status SUPERSEDED ⇔ superseded_by set`
描述已在 merge 前直接编辑 PR #102 body 修正（审核方点名的唯一非 blocker），无新
commit。

## 四轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `bd60748`（PR C 首版：`evidence_reference.yaml` + `evidence_reference_model.py` + 47 tests） | `REQUEST_CHANGES`，三个设计决策与 scope 控制均认可；3 个 PR-C-local blocker |
| 2 | `98d1f9d`（同一 PR，第一轮修订，56 tests） | `REQUEST_CHANGES`，blocker 2 / 3 关闭；blocker 1（canonical provenance chain）仍差两个 layer-2 checker 自身的 false-pass |
| 3 | `d611598`（同一 PR，第二轮修订，58 tests） | `REQUEST_CHANGES`，只剩 `check_evidence_index_against_packages` 的两处 identity gap |
| 4 | `d16b634`（同一 PR，第三轮修订，58 tests / 716 total） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 3 点（`bd60748`）及关闭方式

### 1. canonical GateSet identity 不是 invariant —— 主 blocker（provenance chain 声明 ≠ 实际 checker）

`evidence_reference.yaml` 声明的链是 `Matrix cell → CandidateGateAssessment →
evidence_refs[].evidence_id → EvidencePackage.provenance.source_id →
SourceIndexEntry → external_ref`，并称 PR C enforce 这条 referential-integrity
chain。但首版三个 checker 只在三张 derived index 之间查"有没有对应 ID"，从不读
canonical `CandidateGateAssessment` / `EvidencePackage`。因此存在 false-pass：stale
的 per-gate `evidence_index.csv` 行、或 `EvidenceIndexEntry.primary_source_id` 与
canonical `EvidencePackage.provenance.source_id` 不一致，都能通过。验证的是
"indexes are internally connected"，不是"canonical provenance chain is intact"。

→ 保留原三个 checker 作 **layer 1（derived-index integrity）**，新增 **layer 2
（canonical-record integrity）**（纯引用比对，不算 direction/strength/decision，
不是 engine）：`serialized_matrix_cell(assessment)`（Data Layout Spec §4.1 宽表
cell 序列化）、`check_matrix_against_assessments`（每个非 `NOT_EVALUATED` cell 必须
有当前 canonical Assessment，`candidate_id` / `gate_id` / `instantiation_id` /
`gateset_id` 与 Matrix 一致，`serialized_matrix_cell(assessment) == cell`；
`NOT_EVALUATED` cell ⟺ 无当前 Assessment）、`check_gate_index_against_assessments`
（每个 per-gate index 行的 `assessment_id` 必须 == 当前 Assessment，
`(evidence_id, role)` 必须是其 `evidence_refs` 之一；且该 gate 下每个 current
Assessment 的每个 `evidence_ref` 都必须是一行 index —— 第二轮补上 zero-row 漏检）、
`check_assessment_evidence_refs_against_packages`（每个 `evidence_ref` 解析到
canonical `EvidencePackage`）、`check_evidence_index_against_packages`（第二/三轮
补：每个 `EvidenceIndexEntry` 都有同 `evidence_id` 的 canonical `EvidencePackage`，
且 `entry.primary_source_id == package.provenance["source_id"]`，并镜像
`schema_version` / `candidate_refs`）、`check_packages_against_sources`（每个
`EvidencePackage.provenance.source_id` 在 `SourceIndex` 内）、
`check_supersession_consistency`（`EvidenceIndexEntry.superseded_by` 与新
`EvidencePackage.supersedes_evidence_id` **两边都存在时**才要求一致 —— frozen 里
backward pointer 是 optional，不强制对称，审核方明确认可）。
`evidence_reference.yaml` `provenance_walk` 加 `checks`（layer_1 / layer_2）+
`acceptance`（"a provenance chain is valid only when it passes THROUGH the
canonical CandidateGateAssessment and EvidencePackage, not merely because the
derived indexes are mutually self-consistent"）。

### 2. MatrixView 未保证 row Candidate 属于 Matrix 的 candidate_level

`MatrixView` 检查了 `candidate_level ↔ gateset_id` / `member_gate_ids` / cell 覆盖
/ row 唯一，但没检查 `row.candidate_id` 的 `Lnn` == `candidate_level`。
`candidate_level=L04` + row `CAND-L05-000001` 只要 cells 正确就通过。intrinsic
Matrix contract bug。

→ `MatrixView.__post_init__` 遍历 row 时加
`row.candidate_id.split("-")[1] != self.candidate_level → raise`。registry 加
invariant `every_row_candidate_id_level_matches_the_matrix_candidate_level`。

### 3. EvidenceIndex lifecycle 比冻结 spec 更窄；boundary wording 对 status 过宽

首版 `EvidenceIndexEntry` 实为 `SUPERSEDED ⇔ superseded_by 有值`，因此
`RETRACTED + superseded_by` 被拒；但冻结 Data Layout §10.1 明文允许旧 EP 行
`status → SUPERSEDED（或 RETRACTED）` + `superseded_by = 新 EP`。PR C 既然
"不改 frozen spec"，就不能在 runtime 静默缩窄。另外 `immutable_record_boundary`
原文说"canonical record 不接受 `superseded_by` or `status`；`status` 只住
`EvidenceIndexEntry`"，但 PR A 的 canonical `Context` 本身就有 `status`。

→ `EvidenceIndexEntry` 改为 `ACTIVE → superseded_by 必须空` / `SUPERSEDED → 必须有
pointer` / `RETRACTED → pointer 可选（有则表示有 replacement EP）` /
`非空 superseded_by ⇒ status ∈ {SUPERSEDED, RETRACTED}`；保留 no self / target
exists / no cycle。registry 加 `lifecycle_rule`、改 invariants。
`immutable_record_boundary.rule` 收窄为"EvidencePackage lifecycle status
（`ACTIVE/SUPERSEDED/RETRACTED`）与 forward `superseded_by` 只住
`EvidenceIndexEntry`；canonical `evidence.json` 两者都没有；其它 canonical 对象
（如 PR A 的 `Context/Instantiation/Candidate`）保留其自身合同定义的 intrinsic
status —— PR C 不碰"。

## 第二 / 第三轮的收尾修点

- **第二轮（`98d1f9d` → `d611598`）：** blocker 2 / 3 确认关闭。blocker 1 的
  layer-2 checker 自身两处 false-pass：(a) `check_packages_against_sources` 只查
  EP 自己的 `provenance.source_id` 在 `SourceIndex`，从不比
  `EvidenceIndexEntry.primary_source_id == EvidencePackage.provenance.source_id`
  → 新增 `check_evidence_index_against_packages`（镜像 `primary_source_id` blocker
  + `schema_version` + `candidate_refs`）；(b) `check_gate_index_against_assessments`
  反向检查先由 index 行构造 `named`，再 `if (candidate_id, assessment_id) not in
  named: continue` → `evidence_refs` 非空但该 gate index 零行的 current Assessment
  被跳过 → 删 `named` guard，遍历该 gate 每个 current Assessment 要求每个
  `evidence_ref` 都在 `covered`。
- **第三轮（`d611598` → `d16b634`）：** `check_evidence_index_against_packages`
  体为 `package = packages.get(entry.evidence_id); if package is None: continue`
  → (a) 索引行无 canonical `EvidencePackage` 直接跳过（应 reject——第二轮验收
  条件已写"entry.evidence_id exists as canonical EvidencePackage"）；(b) 从不比
  `package.evidence_id == entry.evidence_id` → `if package is None:` 改 `raise`，
  加 `if package.evidence_id != entry.evidence_id: raise`。

## 批准范围（审核方原话要点，`d16b634`）

- **APPROVE PR #102 @ `d16b634`。可以 merge。** 最后一个 provenance identity gap
  已关闭。PR HEAD `d16b634fe2ef...`，open、mergeable，pull-request CI success。
- 本轮两条最终验收条件均已 machine-enforced：`EvidenceIndexEntry` 找不到同
  `evidence_id` 的 canonical `EvidencePackage` 时直接 `raise`，不再 `continue`；
  即便 mapping key 正确，若 `package.evidence_id != entry.evidence_id` 也会拒绝；
  之后才继续核对 `primary_source_id ↔ provenance.source_id` / `schema_version` /
  `candidate_refs`。对应 regression tests 已覆盖"canonical package 完全缺失"和
  "key 指向错误 `evidence_id` 对象"两种情况。
- 前几轮修复也仍然保持成立，没有被这次修改破坏：Matrix 仍只是
  derived/rebuildable view，没有 schema、ID 或独立 lineage；Matrix row Candidate
  Level 已锁定；`GateEvidenceIndex` zero-row coverage 已锁定；`Matrix → canonical
  Assessment → evidence_refs → canonical EP → Source` 的 provenance chain 已真正
  穿过 canonical records；`RETRACTED + superseded_by` 仍允许；supersession backward
  pointer 保持 optional，不错误强制双向同时存在；PR A/B contracts、冻结 Data
  Layout、legacy gate system 都没有被重新打开；没有 decision engine / matrix
  rebuild engine / provenance graph object。没有新的 blocker。
- **非 blocker（本 PR 已修 body，不再开 runtime 轮）：** GitHub PR body 首版
  遗留 `48 tests / 705 OK` 与旧 `status SUPERSEDED ⇔ superseded_by set` 描述，
  实际 head 已是本轮最终语义。已直接编辑 PR body，无新 commit，不影响 merge。
- **最终结论：APPROVE PR #102 @ `d16b634`。可以 merge。** PR C 到此收口，不需要
  继续优化。下一步可以进入 **Runtime Migration PR D —— `ADC_TARGET_GATESET` 的
  CRC-specific binding + TGT-01…TGT-08 concrete Evidence Ladders/contracts**。

## 操作层说明

本轮起，审核请求由 Claude 通过 Chrome 浏览器自动化直接贴入网页版 ChatGPT
`Biotech ideas` → `AI审核方案` 对话（用户 2026-08-28 明确指示"把任何需要审核的
全部提交给 ChatGPT 的 Biotech ideas - AI审核方案 对话框审核"）。审核方四轮均
尝试通过 GitHub connector 直接给 PR #102 写入 review 状态（`REQUEST_CHANGES` /
`APPROVE` anchor 到对应 HEAD），GitHub 每次返回
`403 Resource not accessible by integration`，未能写回 GitHub。GitHub 上 PR #102
因此没有 formal review 记录，实际四轮意见与最终 `APPROVE` 以本文件与
`AI审核方案` 对话为准。

## 边界

本次批准的是 **Matrix 派生视图合同 + 可复用证据引用层 + provenance walk**
（`src/contracts/evidence_reference.yaml` + `src/objects/evidence_reference_model.py`
+ 58 tests）。它是四个 runtime-migration PR 的第三个，没有 decision engine、
没有 matrix-rebuild engine、没有被持久化的 provenance graph object，没有新增
`src/contracts/data_layout/` schema（Matrix / evidence index / source index 仍
只由冻结 `csv_headers.yaml` 定义）。合并后 PR A 的 `decision_objects.yaml` /
`decision_model.py` / `legacy_adapters.py`、PR B 的 `gate_contracts.yaml` /
`gate_model.py` / `legacy_gate_map.py`、`gate_system.yaml` 的 45-Gate 拓扑均
不变，CURRENT_SYSTEM v5 的 `MIGRATION_PENDING` 未解除——到 PR E 合并前
repository runtime 不得声称已实现 Blueprint v1.3 conformance。仓库内不保存运行
数据或 `.csv`。

冻结与进度状态：

> Blueprint v1.3：冻结
> CURRENT_SYSTEM v5：冻结
> Data Layout Spec v1.0：冻结
> Runtime Migration PR A（core decision objects）：已合并（PR #98 @ `f225e9f`，`cbab012`）
> Runtime Migration PR B（canonical Gate / GateSet / EvidenceLadder / Decision）：已合并（PR #100 @ `51bfadb`，`d18974b`）
> Runtime Migration PR C（Matrix view / reusable EP references / provenance walk）：**已合并**（PR #102 @ `d16b634`，`91a8e5b`）
> 下一步：Runtime Migration PR D —— CRC-ADC-TARGET-GATESET-v1（`ADC_TARGET_GATESET` 的 context-specific binding + TGT-01…TGT-08 Evidence Ladders / Gate contracts；需科学审核）
