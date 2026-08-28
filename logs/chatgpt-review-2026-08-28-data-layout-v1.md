# ChatGPT 审核记录：StelligenOS Data Layout Spec v1.0

- 日期：`2026-08-28`
- PR：#96 `task_20260828_data-layout-spec-v1`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`
- 被审核 HEAD：`dc8684e`（round-2 修订，关闭唯一剩余 blocker）
- 冻结提交：`b6a4fd0`（`v1.0-draft` → `v1.0` / `APPROVED` + `run_manifest` 措辞收口）
- Merge 提交：`7040f5a`（`Merge pull request #96 from leezx/task_20260828_data-layout-spec-v1`）
- 结论：**APPROVE @ `dc8684e`**

本记录在**独立 docs-only PR**（`task_20260828_data-layout-v1-approval-record`）中
补登。按 PR #95（v5 approval record）先例，审核方的 `APPROVE` 在 PR #96 内容
稳定之后才到；冻结提交 `b6a4fd0` 已随 APPROVE 授权（含审核方点名的 `run_manifest`
文字修正）合入 PR #96，本 PR 不再改 Data Layout 正文/schema，仅补审计记录。

## 三轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `fad39ac`（v1.0-draft 首版：20 节 + 附录 A–D + 8 schema + worked example + scaffold） | `REQUEST_CHANGES`，6 点（contract / provenance / state-safety；方向正确，目录主体不动） |
| 2 | `4a640b2`（第 1 轮 6 点全部关闭） | `REQUEST_CHANGES`，仅剩 1 blocker：immutable record 不得含 forward `superseded_by` |
| 3 | `dc8684e`（新增 §0.4 冻结规则，四类 record supersession 统一） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 6 点及关闭方式

1. **Context 缺 canonical 落点（blocker）。**
   → 新增顶层 `15_CONTEXTS/`（`context_index.csv` + `CTX-*/vNNN.yaml` canonical
   append-only + `latest.yaml` derived 副本）；新增 spec §2b 与
   `src/contracts/data_layout/context.schema.yaml`。`Instantiation` 与
   `Assessment` 增加 `context_version`（pin 到具体 `vNNN.yaml`）。
   `csv_headers.yaml` 增 `context_index`，`registry_instantiation` 增
   `context_version`。「5 类 canonical 文件」改称「5 类 primary product
   outputs」，并明确 `Context` / `Instantiation` / `gate_binding` /
   `gateset_binding` / `run_manifest` 也是 canonical record（配置/绑定/施工层）。

2. **版本引用链未闭合。**
   → `EvidencePackage` 定为 **immutable-by-ID**（被任何 Assessment 引用后内容
   永不原地修改；纠错/新 interpretation → 新 EP）。`evidence.json` 的 `version`
   → `schema_version`（仅结构版本，非内容修订版本）。`Assessment` 的
   `evidence_refs` 因此只需 `evidence_id`。`Decision` 的 `assessment_snapshot`
   从 `{gate: "cell"}` 改为 `{gate: {assessment_id, assessment_version, cell}}`
   或字符串 `"NOT_EVALUATED"`；`triggered_by` 增 `assessment_version`。
   §10.1 / §17 列为冻结项。

3. **Assessment schema 未真正 enforce 状态铁律。**
   → §8.2 新增 `direction × strength` 组合表并在 `assessment.schema.json` 用
   `allOf` 条件强制：`POSITIVE`/`NEGATIVE` 禁 `UNKNOWN` 且需 ≥1 `evidence_ref`；
   `CONFLICTING` 用 `contains`/`minContains` 强制 `evidence_refs` 中 ≥1
   `SUPPORTING` 且 ≥1 `CONTRADICTING`，`key_supporting_evidence` /
   `key_contradicting_evidence` 非空；`INCONCLUSIVE` 有合格证据则带 strength，
   无证据 = 固定 serialization `direction=INCONCLUSIVE, strength=UNKNOWN,
   evidence_refs=[]`；`NOT_APPLICABLE` 单列。canonical `Assessment` 与
   `Decision` JSON 的 `review.status` 固定 `const HUMAN_APPROVED`；proposal 只在
   `RUNS/assessment_proposals.csv`。

4. **Candidate schema 文字禁了机器没禁。**
   → `candidate.schema.json` 的 `not.anyOf` 现禁止 `context_id` /
   `context_version` / `direction` / `strength` / `decision` / `score` /
   `assessment_id` / `evidence_refs` / `gate_id` / `gateset_id`（Level-specific
   生物字段仍允许）。`csv_headers.yaml` 增 `gate_current_assessments`（列与
   `assessments_long` 相同，作用域为单个 Gate）。

5. **scaffold 脚本 repo-boundary 检查顺序 bug。**
   → `scripts/scaffold_data_layout.sh` 现先用 python 走到最近存在的祖先目录并
   `realpath`（跟随 symlink）解析目标 → 判断是否位于 repo 内 → **通过后才
   `mkdir`**。repo 内目标（含尚不存在的路径、含 external symlink 实际指回 repo）
   一律拒绝且不创建任何目录。新增回归测试
   `tests/test_scaffold_data_layout.sh`（A 拒绝 repo 内不存在路径且不创建 /
   B 拒绝 symlink 逃逸 / C 外部只写表头行 / D 拒绝坏 `instantiation_id` /
   E 幂等 / F 只写到外部）。

6. **worked example 违反两条科学语义。**
   → (a) 删除「refractory mCRC 无定量抗原密度数据」被建成 `CONTRADICTING` EP
   的做法（`EP-00000131` / `SRC-00000902` 已移除）；该缺口只进 `TGT-04`
   Assessment 的 `critical_unknowns`（`resolution = EXPERIMENT_REQUIRED`）；
   spec 新增 §10.2「absence of evidence ≠ contradicting evidence」。`TGT-04`
   assessment 现只有 1 条 `SUPPORTING` EP。(b) Matrix 未评估 Gate 与 Decision
   `assessment_snapshot` 一致使用显式机器值 `NOT_EVALUATED`（与「已评估但无
   证据」的 `UNKNOWN` 严格区分），不再使用 em dash。

治理措辞：PR body `NO_ARCHITECTURE_CHANGE` → `NO_CORE_ARCHITECTURE_CHANGE /
NEW_DATA_LAYOUT_CONTRACT`（v5 决策架构未变，但新增并冻结一套 physical data
architecture）。

## 第二轮唯一 blocker 及关闭方式

**问题：** immutable / append-only canonical record 与 forward `superseded_by`
自相矛盾——record 声明「写入后永不原地改」，却又要求旧 record 自己写指向未来
新 record 的 `superseded_by`；`evidence_package.schema.json` 等也仍保留该字段。

**关闭（新增 spec §0.4 冻结规则）：**

> **Immutable canonical records never contain forward pointers that become
> known only in the future.**

| 关系 | 存放位置 |
|---|---|
| 旧 record（永不修改） | immutable record 本体 |
| 新 record → 旧 record 的 backward pointer `supersedes_*`（可选） | 新 record 本体 |
| forward `superseded_by` / `status` | mutable/derived index（`evidence_index.csv`） |
| 「哪一版最新」 | `latest.yaml` / `latest.json` 副本，或 `(id, version)` 推导 |

- `evidence_package.schema.json`：`superseded_by` → backward
  `supersedes_evidence_id`；`not.anyOf` 增禁 `superseded_by` / `status`。
- `assessment.schema.json`：删除 `superseded_by`（`v001 → v002 → v003` +
  `latest.json` 表达）；`not.anyOf` 增禁 `superseded_by`。
- `decision.schema.json`：`superseded_by` → backward `supersedes_decision_id`；
  新增 `not.anyOf` 禁 forward `superseded_by`。
- `context.schema.yaml`：forward `superseded_by` → backward
  `supersedes_version`；`not.anyOf` 增禁 `superseded_by`。
- spec §8.1 / §10.1 / §10.3 / §14 / §17 措辞对齐；`csv_headers.yaml`
  `library_evidence_index` 加注释（forward pointer 的唯一存放处）。
- worked example EP 说明段：纠错 = 新建 `EP-00000124`（可带 backward
  `supersedes_evidence_id`）+ `evidence_index.csv` 标 `status=SUPERSEDED,
  superseded_by=...`；本文件永不编辑。

`evidence_index.csv`（`library_evidence_index` header）保留现有 `status` +
`superseded_by` 列——它是 mutable/derived index，是唯一允许放 forward pointer
的地方（审核方明确同意）。

## 批准范围（审核方原话要点）

- **APPROVE PR #96 @ `dc8684e`。** 上一轮唯一 blocker 关闭；
  `EvidencePackage / Context / Assessment / Decision` 的 supersession 统一遵循
  「immutable record 不存未来才知道的 forward pointer；新 record 可存 backward
  `supersedes_*`；forward lifecycle 状态只在 mutable/derived index」。
- Decision 历史复现链已闭合：每 Gate pin `assessment_id + assessment_version +
  cell`，未评估状态单独用 `NOT_EVALUATED`。满足审核方最关注的 provenance
  requirement。
- **收口文字修正（审核方点名，非 blocker，不需第 4 轮）：** §0.4 原文把
  `run_manifest.json` 一并说成「一经写入就永不修改」；实际其状态机是
  `RUNNING → COMPLETED / FAILED / ABORTED`，到 terminal 后才 immutable
  （`run_manifest.schema.json` 已正确表达）。冻结提交 `b6a4fd0` 已改此句。
- **冻结 `STELLIGENOS_DATA_LAYOUT_SPEC v1.0`**，生成外部真实 workspace。
  **不再继续优化目录结构**，正式进入 runtime migration **PR A**（PR A 属下一
  阶段施工，需 Owner 单独授权后再设计/审核）。
- 已知非 blocker：`tests/test_scaffold_data_layout.sh` 尚未接入
  `.github/workflows/ci.yml`（本会话 gh OAuth token 缺 `workflow` scope）。
  GitHub 上显示的 CI success 不含该组 A–F 测试。负责人在 `git_sync` 步骤后加一行
  `bash tests/test_scaffold_data_layout.sh` 即可。

## 操作层说明

审核方三轮均尝试通过 GitHub connector 直接给 PR #96 写入 review 状态
（`REQUEST_CHANGES` ×2、`APPROVE` ×1），GitHub 每次返回
`403 Resource not accessible by integration`，未能把 review 状态写回 GitHub。
这是 connector 权限问题，不影响审核结论。GitHub 上 PR #96 因此没有 formal
review 记录，实际三轮意见与最终 `APPROVE` 以本文件与 `AI审核方案` 对话为准。

## 边界

本次审核批准的是 **physical data architecture 规范**
（`STELLIGENOS_DATA_LAYOUT_SPEC v1.0` + `src/contracts/data_layout/` schema +
worked example + scaffold 脚本）。它**不是** runtime implementation 批准：
`core_objects.yaml` / `gate_system.yaml` / `src/`（`data_layout/` 契约以外）
仍为 legacy，CURRENT_SYSTEM v5 的 `MIGRATION_PENDING` 未解除。仓库内不保存本
布局下的任何真实数据或 `.csv`；真实数据在 `$STELLIGENOS_DATA`（仓库外部）。

冻结状态汇总：

> Blueprint v1.3：冻结
> CURRENT_SYSTEM v5：冻结（`STELLIGENOS-ARCH-2026.08.27-v5` / `APPROVED`）
> Data Layout Spec v1.0：冻结（`v1.0` / `APPROVED`，PR #96 @ `dc8684e`）
> 下一阶段：Runtime Migration PR A —— 暂不启动，待 Owner 单独授权。
