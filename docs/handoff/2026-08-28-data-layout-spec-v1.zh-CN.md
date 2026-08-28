# Handoff：StelligenOS Data Layout Spec v1.0（目录层次 + 规范）

## 任务信息

- 任务编号：`task_20260828_data-layout-spec-v1`
- 分支：`task_20260828_data-layout-spec-v1`
- 基线：`origin/main` @ `95e2ad1`（PR #95 merge）
- PR：待创建
- 时间：`2026-08-28`
- 交付物类型：**新增数据布局规范文档 + 机器可读 schema + worked example + 外部
  骨架生成脚本**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（不改核心对象、不改 `core_objects.yaml`
  / `gate_system.yaml` / CURRENT_SYSTEM v5 / 任何现有合同；不启动 runtime
  migration PR A–E）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用「审核豁免」。**

## 一、为什么做

用户提供 KB 设计文档 `2.Biotech/StelligenOS/StelligenOS工作目录设计.md`
（把"产品数据层"与"施工运行层"分开的物理布局提案，ChatGPT 输出），指令：
把这套目录层次和规范做出来，提交 PR 审核。设计文档自己的结论也是"下一步是把
它写成正式的 `STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md` + 所有 CSV/JSON/YAML schema
+ 一个 `TGT-04 × CEACAM5` 完整样例"。

它是 CURRENT_SYSTEM v5 §16 B 组 runtime migration（PR A–E）的**物理层依据**：
Candidate / Context / Instantiation / Matrix / Assessment / EvidencePackage /
Decision / Module run 在**仓库外部工作区**的固定磁盘布局。

## 二、改了什么（全部新增）

| 路径 | 内容 |
|---|---|
| `docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md` | 规范正文：§0 版本/来源/边界 · §0.2 四条核心原则（CSV=视图；Assessment JSON=canonical；EvidencePackage 全局复用不复制；一 Gate 一 workspace）· §0.3 五类 canonical 文件冻结 · §1 顶层 `00_REGISTRY … 90_ARCHIVE` · §2 Candidate 分 Level CSV + 统一 identity 字段（**无 `context_id`**）· §3 Instantiation `instantiation.yaml` · §4 Matrix 宽表（cell = `DIRECTION/STRENGTH`，禁数字）+ 4.1 取值枚举 · §5 `assessments.csv` long-format · §6 GateSet→Gate folder + `gateset_binding.yaml` · §7 Gate folder 三层（`gate_binding.yaml` / `CURRENT/` / `ASSESSMENTS/<cand>/vNNN.json`+`latest.json` / `RUNS/` immutable）· §8 Assessment JSON 字段规范 + 正交性/聚合铁律 · §9–14 EvidencePackage folder（`evidence.json`+`summary.md`+`artifacts/`）、全局存储、Gate 内只放 `evidence_index.csv` 引用、`source_index.csv` · §10 EP 中性、**不带 direction/strength/grade** · §15 run_manifest immutable · §16 proposal↔human-approved 分离 · §17 Decision 在 GateSet 层不在 Gate 层 · §18 数据流链 · §19 五类文件 · §20 建筑图 · 附录 A ID 命名规范（`CAND-Lnn-nnnnnn` / `EP-nnnnnnnn` / `SRC-nnnnnnnn` / `ASMT-nnnnnn` / `DEC-nnnn` / `MOD-<GATE>` / `RUN-<GATE>-<date>-nnn`）· 附录 B schema 索引 · 附录 C 仓库边界 · 附录 D 版本维护 |
| `src/contracts/data_layout/README.md` | schema 目录说明 |
| `src/contracts/data_layout/*.schema.json` | `candidate` · `assessment`（`CONFLICTING` 需两侧、非 UNKNOWN 需 evidence_refs、禁 `decision`/`score`）· `evidence_package`（禁 `direction`/`strength`/`grade`）· `run_manifest`（终态需 `completed_at`）· `decision`（GateSet 层枚举） |
| `src/contracts/data_layout/*.schema.yaml` | `instantiation`（禁 `candidate_id`/`assessments`/`evidence_refs`）· `gate_binding`（`oneOf`：gate_binding / gateset_binding 两分支） |
| `src/contracts/data_layout/csv_headers.yaml` | 所有 CSV 的规范表头（logical name → 有序列名，17 项）。**仓库不存 `.csv` 文件**，此 YAML 是 CSV 的规范来源，`scaffold` 脚本据此在外部写真实表头。 |
| `docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md` | 单文档 worked example：完整 `TGT-04 × CEACAM5` 树，每个文件路径为标题 + 内容以 fenced code block 呈现（json/yaml/csv/text）；顶部标注 `REFERENCE EXAMPLE — NOT REAL DATA`。不落地为文件（避免 `.csv` 触发边界检查）。 |
| `scripts/scaffold_data_layout.sh` | `scaffold_data_layout.sh <target_root> [instantiation_id]`：在**外部绝对路径**创建空的 `00_REGISTRY … 90_ARCHIVE` + 15 个 Level CSV 表头 + 可选 Instantiation 骨架；**拒绝在 repo 内运行**（exit 3）；表头从 `csv_headers.yaml` 生成（需 python3 + PyYAML）。 |

## 三、本 PR 不做什么

- **不在 repo 内创建任何 `DATA/` 目录、真实数据、`.csv` 文件、EP 正文或 run
  产物。** worked example 是单个 `.md`，CSV 内容全部在 fenced block 内。
- 不改 `core_objects.yaml` / `gate_system.yaml` / CURRENT_SYSTEM v5 / `contract.zh-CN.md`
  / 任何现有 `src/` 代码或合同。
- 不启动 runtime migration PR A–E（本 spec 是其物理层依据，但本身只是文档+schema）。
- 不解除 `EVGAP-01`/`EVGAP-02`；不动 CRC 41/369 pool；不动用户自有 untracked 文件。

## 四、与设计文档的差异（有意）

- 设计文档给了一个真实文件树样例；本 PR 因 `verify_repository_boundary.sh`
  **禁止任何 `.csv` 文件**，改为：(a) `csv_headers.yaml` 承载 CSV 规范表头；
  (b) worked example 为单文档、CSV 以 fenced block 呈现。语义完全一致。
- 其余（顶层目录、四原则、五类文件、Gate folder 三层、ID 规范、Decision 边界）
  与设计文档一一对应。

## 五、验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 555 tests — OK

命令：bash tests/test_git_sync.sh
结果：passed (A-D)

命令：git diff --check
结果：clean

命令：（在干净 tracked 树的临时 worktree 上）bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.（exit 0；本地工作树因 pre-existing 用户
      自有 untracked `pipelines/` 等仍报违规，与 PR #94/#95 相同，CI 不受影响）

命令：所有 *.schema.json / *.schema.yaml 结构合法性（json.load / yaml.safe_load）
结果：7 schema + csv_headers.yaml 全部 OK

命令：worked example 内嵌 JSON/YAML 手写不变量检查（id pattern、EP 无 grade、
      assessment 无 decision/score、CONFLICTING 需两侧、matrix cell 非数字、
      candidate 无 context_id）
结果：all data-layout invariant checks passed

命令：bash scripts/scaffold_data_layout.sh <repo 内路径>
结果：Refusing ... inside the repository（exit 3）

命令：bash scripts/scaffold_data_layout.sh <外部临时路径> INST-DEMO-ADC-TARGET-v1
结果：创建 24 个文件（目录 + CSV 表头行），无数据行
```

## 六、下一步

1. ~~本 PR `APPROVE` 并合并 → `v1.0-draft` → `v1.0`。~~ **已完成**：PR #96 @
   `dc8684e` 获 ChatGPT `APPROVE`（见 §十），随冻结提交把 §0 版本区块与
   `csv_headers.yaml` `spec_version` 改为 `v1.0` / `APPROVED`。
2. 用 `scripts/scaffold_data_layout.sh` 在 `/Volumes/Stelligen_SSD/Stelligen/DATA/StelligenOS/`
   （或操作者选定路径）生成真实外部骨架（外部运行，产物不入仓）。
3. runtime migration **PR A**（CURRENT_SYSTEM v5 §16 B 组问题 23）以本 spec 为
   物理层依据推进——需 Owner 单独授权。审核方指示"不再继续优化目录结构，
   正式进入 PR A"。
4. 负责人（有 `workflow` scope）把 `bash tests/test_scaffold_data_layout.sh`
   加进 `.github/workflows/ci.yml`（`git_sync` 步骤后一行）。

## 七、REQUEST_CHANGES 第一轮修订（2026-08-28，同一 PR #96）

ChatGPT 在 `Biotech ideas → AI审核方案` 对话对 `fad39ac` 返回
`REQUEST_CHANGES`（方向正确、目录主体不动，只修 contract/provenance/state-safety
问题）。已按 6 点修改，仍 docs+schema+脚本、未启动 runtime migration：

1. **Context 有了 canonical 物理落点。** 新增顶层 `15_CONTEXTS/`（`context_index.csv`
   + `CTX-*/vNNN.yaml` canonical + `latest.yaml` 副本），新增 §2b。Instantiation
   与 Assessment 增加 `context_version`（pin 到具体 `vNNN.yaml`）。新增
   `src/contracts/data_layout/context.schema.yaml`。`csv_headers.yaml` 增
   `context_index`，`registry_instantiation` 增 `context_version`。"5 类
   canonical 文件" 改称 "5 类 primary product outputs"，并列出 Context /
   Instantiation / gate_binding / gateset_binding / run_manifest 也是 canonical
   record（配置/绑定/施工层）。
2. **版本引用链闭合。** EvidencePackage 定为 **immutable-by-ID**（被引用后
   内容永不原地改，纠错→新 EP + `superseded_by`），`evidence.json` 的 `version`
   → `schema_version`（仅结构版本）。Decision 的 `assessment_snapshot` 从
   `{gate: "cell"}` 改为 `{gate: {assessment_id, assessment_version, cell}}`
   或字符串 `"NOT_EVALUATED"`；`triggered_by` 增 `assessment_version`。新增
   §10.1 / §17 规则，列为冻结项。
3. **Assessment schema 真正 enforce 状态铁律。** §8.2 新增 direction×strength
   组合表：`POSITIVE`/`NEGATIVE` 禁 `UNKNOWN` 且需 ≥1 evidence_ref；
   `CONFLICTING` 用 `contains`/`minContains` 强制 ≥1 `SUPPORTING` + ≥1
   `CONTRADICTING`，两个 `key_*` 数组非空；`INCONCLUSIVE` 有证据则带 strength
   （`INCONCLUSIVE/DIRECT` 等，不丢信息），无证据 = `UNKNOWN` 固定
   serialization；`NOT_APPLICABLE` 单列。canonical Assessment / Decision JSON
   的 `review.status` 固定 `HUMAN_APPROVED`（`const`），proposal 只在 `RUNS/`。
4. **Candidate schema 机器禁止评估字段。** `candidate.schema.json` 的 `not.anyOf`
   现禁止 `context_id` / `context_version` / `direction` / `strength` /
   `decision` / `score` / `assessment_id` / `evidence_refs` / `gate_id` /
   `gateset_id`（Level-specific 生物字段仍允许）。`csv_headers.yaml` 增
   `gate_current_assessments`（列同 `assessments_long`，作用域为单 Gate），
   §5/§7 注明二者列相同。
5. **scaffold 脚本 boundary 检查顺序修复。** 现先用 python 走到最近存在的祖先
   并 `realpath`（跟随 symlink）解析目标 → 判断是否在 repo 内 → **通过后才
   `mkdir`**。repo 内目标（含不存在的路径、含 external symlink 指回 repo）一律
   拒绝且不创建任何目录。新增回归测试 `tests/test_scaffold_data_layout.sh`
   （A 拒绝 repo 内不存在路径且不创建 / B 拒绝 symlink 逃逸 / C 外部只写表头行
   / D 拒绝坏 instantiation_id / E 幂等 / F 只写到外部）。**未能接入
   `.github/workflows/ci.yml`**：本会话的 gh OAuth token 缺 `workflow` scope，
   push 含 workflow 改动的 commit 被 GitHub 拒绝。已回退 `ci.yml`；负责人（有
   `workflow` scope）加一行 `bash tests/test_scaffold_data_layout.sh` 即可。
   本地与本轮验证均已运行该测试。
6. **worked example 修正两处科学语义。** (a) 删除 "没有定量密度数据" 的
   `CONTRADICTING` EP（`EP-00000131` / `SRC-00000902`），该缺口只进
   `critical_unknowns: EXPERIMENT_REQUIRED`；TGT-04 assessment 现只有 1 条
   `SUPPORTING` EP，`evidence_count=1`；新增 §10.2 "absence of evidence ≠
   contradicting evidence"。(b) Matrix 未评估 Gate 与 Decision `assessment_snapshot`
   一致使用显式机器值 `NOT_EVALUATED`，不再用 em dash。

治理措辞：PR body 的 `NO_ARCHITECTURE_CHANGE` → `NO_CORE_ARCHITECTURE_CHANGE /
NEW_DATA_LAYOUT_CONTRACT`（v5 决策架构未变，但新增并冻结一套 physical data
architecture）。

**改动文件（本轮）：** `docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md`、
`docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md`、
`src/contracts/data_layout/`（+`context.schema.yaml`）、
`scripts/scaffold_data_layout.sh`、`tests/test_scaffold_data_layout.sh`（新）、
本 handoff、worklog。（`ci.yml` 因 token 缺 `workflow` scope 未改，见上。）

**验证（本轮）：** unittest 555 OK；`test_git_sync` A-D；
`test_scaffold_data_layout` A-F；`git diff --check` clean；干净 tracked-tree
worktree 上 `verify_repository_boundary` passed + scaffold test + unittest 全过；
7 schema + `context.schema.yaml` + `csv_headers.yaml` 结构合法；worked example
+ csv_headers 手写不变量检查全过（em dash 不在 csv/json block、snapshot pin
`assessment_version`、EP 用 `schema_version` 且无 grade、canonical `HUMAN_APPROVED`、
candidate header 无评估列、matrix 非数字且 decision=MORE_EVIDENCE、7 个
`NOT_EVALUATED`）。

**GitHub connector：** 审核方再次尝试写 PR #96 的 `APPROVE` review，仍
`403 Resource not accessible by integration`，未写回 GitHub。

## 八、数据边界声明

本仓库只保存本 spec、`src/contracts/data_layout/` 下的 schema 与 `csv_headers.yaml`、
单文档 worked example、以及 scaffold 脚本，均为治理文本 / 参考文档 / 脚本。
没有新增任何数据、缓存、结果文件或 `.csv` 文件。所有真实数据在 `$STELLIGENOS_DATA`
（仓库外部）。

## 九、PR #96 REQUEST_CHANGES 第 2 轮（仅 immutable-record supersession）

审核结论：**REQUEST_CHANGES，仅剩 1 个 blocker。** 第 1 轮 6 点全部确认关闭，
目录主体 / Candidate/Gate 结构 / 状态机 / Context 设计 / scaffold 设计均无需再动。
唯一问题：**immutable / append-only canonical record 与 forward `superseded_by`
自相矛盾**——record 声明"写入后永不原地改"，却又要求旧 record 自己写指向未来
新 record 的 `superseded_by`。

本轮统一冻结规则（新增 spec §0.4）：

> **Immutable canonical records never contain forward pointers that become
> known only in the future.**

- 旧 record 永不修改；
- 新 record 可选携带 **backward** pointer `supersedes_*`；
- **forward** `superseded_by` / `status` / "哪版最新" 只住在 mutable/derived
  index（`evidence_index.csv`）或 `latest.*` 副本 / `(id, version)` 推导；
- **Assessment** 天然 `v001 → v002 → v003` + `latest.json`，不需要任何
  supersession pointer，schema 已删除 `superseded_by`；
- **Context** 由 `(context_id, context_version)` + `latest.yaml` 推导，
  `vNNN.yaml` 仅可选 `supersedes_version`；
- **EvidencePackage** `evidence.json` 不含 forward `superseded_by`/`status`，
  可选 backward `supersedes_evidence_id`；forward 关系写 `evidence_index.csv`；
- **Decision** `DEC-*.json` 不含 forward `superseded_by`，可选 backward
  `supersedes_decision_id`；`decisions.csv` 反映最新状态。

**改动文件（本轮）：**

| 文件 | 改动 |
|---|---|
| `STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md` | 新增 §0.4 冻结规则表；§8.1 删除 Assessment `superseded_by` 行并加不含说明；§10.1 重写（旧 EP 文件不动，forward 关系入 `evidence_index.csv`）；§10.3 `superseded_by` → backward `supersedes_evidence_id` 并禁 forward；§14 措辞对齐；§17 Decision 加 backward `supersedes_decision_id`、禁 forward |
| `evidence_package.schema.json` | `superseded_by` 属性 → `supersedes_evidence_id`；`not.anyOf` 增禁 `superseded_by` / `status`；description 对齐 |
| `assessment.schema.json` | 删除 `superseded_by` 属性；`not.anyOf` 增禁 `superseded_by`；description 对齐 |
| `decision.schema.json` | `superseded_by` 属性 → `supersedes_decision_id`；新增 `not.anyOf` 禁 forward `superseded_by`；description 对齐 |
| `context.schema.yaml` | forward `superseded_by` → backward `supersedes_version`；`not.anyOf` 增禁 `superseded_by` |
| `csv_headers.yaml` | `library_evidence_index` 加注释：这是 forward `superseded_by`/`status` 的**唯一**存放处 |
| worked example | EP 说明段：纠错 = 新建 `EP-00000124`（可带 backward `supersedes_evidence_id`）+ `evidence_index.csv` 标 `status=SUPERSEDED, superseded_by=...`；本文件永不编辑 |

`evidence_index.csv`（`library_evidence_index` header）保留现有 `status` +
`superseded_by` 列不变——它是 mutable/derived index，是唯一允许放 forward
pointer 的地方。

**非 blocker（未处理，需负责人）：** `tests/test_scaffold_data_layout.sh` 仍未
接入 `.github/workflows/ci.yml`（本会话 gh token 缺 `workflow` scope）。GitHub
上显示的 CI success 不含 A–F 这组新测试。负责人在 `git_sync` 步骤后加一行
`bash tests/test_scaffold_data_layout.sh` 即可。

**验证（本轮）：** `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest` 555 OK
（无 `-B`/env 时本地会因残留 `__pycache__` 误报 1 项，与本改动无关，CI 设该 env）；
`test_git_sync` A-D；`test_scaffold_data_layout` A-F；`git diff --check` clean；
干净 tracked-tree worktree 上 `verify_repository_boundary` passed；9 schema/yaml
结构合法；worked example + schema supersession 手写不变量检查全过（三类 immutable
record 无 forward `superseded_by`；EP 无 `status`/grade；`supersedes_evidence_id`
/ `supersedes_decision_id` / `supersedes_version` 就位；spec 含 §0.4 冻结句；
snapshot 仍 pin `assessment_version`；7 个 `NOT_EVALUATED`；em dash 不在 csv/json
block）。

**GitHub connector：** 审核方再次尝试写 PR #96 `REQUEST_CHANGES` review，仍
`403 Resource not accessible by integration`，未写回 GitHub。

## 十、PR #96 `APPROVE` 与 `v1.0` 冻结（2026-08-28，同一 PR #96）

- **Review input：** ChatGPT 在 `Biotech ideas → AI审核方案` 对话对 PR #96 @
  `dc8684e` 返回 **`APPROVE`**。上一轮唯一剩余 blocker（immutable record 不得含
  forward `superseded_by`）已关闭；`EvidencePackage / Context / Assessment /
  Decision` 的 supersession 现在统一遵循"immutable record 不存未来才知道的
  forward pointer；新 record 可存 backward `supersedes_*`；forward lifecycle
  状态只在 mutable/derived index"。审核方确认 Decision 历史复现链已闭合
  （每 Gate pin `assessment_id + assessment_version + cell`，未评估用
  `NOT_EVALUATED`），满足其 provenance requirement。
- **随本次冻结的收口文字修正（审核方点名，非 blocker，不需第 4 轮）：**
  §0.4 原文把 `run_manifest.json` 一并说成"一经写入永不修改"；实际其状态机是
  `RUNNING → COMPLETED / FAILED / ABORTED`，到 terminal 后才 immutable
  （`run_manifest.schema.json` 已正确表达）。§0.4 该句已改。
- **冻结动作：** `docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md` §0 版本
  区块 `v1.0-draft` / `PENDING_EXPERT_REVIEW` → `v1.0` / `APPROVED`（附三轮审核
  与 403 说明）；附录 D 补三轮审核记录；`src/contracts/data_layout/csv_headers.yaml`
  `spec_version: "1.0-draft"` → `"1.0"`。spec 主体（目录树、schema、状态机、
  worked example）不再改动。
- **遗留（非 blocker）：** `tests/test_scaffold_data_layout.sh` 仍未接入
  `.github/workflows/ci.yml`（本会话 gh token 缺 `workflow` scope）。负责人补一行。
- **GitHub connector：** 审核方尝试向 PR #96 写 `APPROVE` review，仍
  `403 Resource not accessible by integration`，正式 review 状态未写回 GitHub；
  APPROVE 全文由 leezx 在对话中转述。
- **审核方结论：** 冻结 `STELLIGENOS_DATA_LAYOUT_SPEC v1.0`，生成外部真实
  workspace，**不再继续优化目录结构，正式进入 runtime migration PR A**。
