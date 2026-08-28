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

1. 本 PR `APPROVE` 并合并 → `v1.0-draft` → `v1.0`。
2. 用 `scripts/scaffold_data_layout.sh` 在 `/Volumes/Stelligen_SSD/Stelligen/DATA/StelligenOS/`
   （或操作者选定路径）生成真实外部骨架（外部运行，产物不入仓）。
3. runtime migration PR A–E（CURRENT_SYSTEM v5 §16 B 组问题 23）以本 spec 为
   物理层依据推进——需 Owner 单独授权。

## 七、数据边界声明

本仓库只保存本 spec、`src/contracts/data_layout/` 下的 schema 与 `csv_headers.yaml`、
单文档 worked example、以及 scaffold 脚本，均为治理文本 / 参考文档 / 脚本。
没有新增任何数据、缓存、结果文件或 `.csv` 文件。所有真实数据在 `$STELLIGENOS_DATA`
（仓库外部）。
