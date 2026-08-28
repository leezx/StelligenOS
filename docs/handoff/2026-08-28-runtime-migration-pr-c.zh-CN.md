# Handoff：Runtime Migration PR C —— Matrix view / reusable EvidencePackage references / provenance walk

## 任务信息

- 任务编号：`task_20260828_runtime-migration-pr-c`
- 分支：`task_20260828_runtime-migration-pr-c`
- 基线：`origin/main` @ `9aafc57`（PR #101 merge，PR B 收口后）
- PR：待创建
- 时间：`2026-08-28`
- 授权：用户"Runtime Migration PR A–D，逐一来做"；PR B APPROVE 后审核方
  "Merge 后可以进入 PR C — Matrix / provenance / reusable EvidencePackage
  references"
- 变更定位：`RUNTIME_CONTRACT_ADD`（第三层运行时对象合同：Matrix 派生视图 +
  可复用证据引用层 + provenance walk。不删 legacy、不改冻结文档、不加依赖、
  不引入 engine、不新增 `data_layout/` schema）

## 一、依据（冻结文档，本 PR 不修改，只按其顺序施工）

- CURRENT_SYSTEM v5 §2.1（Candidate × Gate 矩阵、cell = CandidateGateAssessment、
  逐层 drill-down 到 Evidence Package → Source）、§9（可引用复用的 EvidencePackage
  库、`evidence_package_ids` 引用而非复制）、§13（runtime flow：引用而非复制）、
  §16 B 组问题 23（PR C = Matrix / provenance / reusable EP references）。
- contract.zh-CN.md §3.4。
- Data Layout Spec v1.0 §4（Matrix 宽表 = derived view，从 `latest.json` +
  `DEC-*.json` 无损重建，不手工编辑）、§4.1（冻结 cell 词表，禁数字分数）、
  §11–§13（Evidence ↔ Assessment 通过 `evidence_refs` 引用、EP 全局单份存储、
  Gate folder 只放 evidence index）、§14（`source_index.csv` 一源多 EP、
  `evidence_index.csv` 是 mutable/derived、forward `status`/`superseded_by`
  只住这里）、§0.4（immutable record 不含 forward pointer）、附录 B（Matrix
  **无** JSON Schema，只有 `csv_headers.yaml`）。
- `src/contracts/data_layout/csv_headers.yaml`（`v1.0`）：本 PR 的 header parity 依据。

## 二、三个决策（用户已拍板，均取推荐项；审核方在 `AI审核方案` 已独立同意同款）

1. **Matrix = 只做 view contract，不加 JSON Schema。** `MatrixView` frozen
   dataclass 承载宽/长视图形状，对 `csv_headers.yaml` 的 `matrix_adc_target` /
   `assessments_long` / `decisions` 做 header parity；编码"派生、可重建、从不
   手工编辑、无 id"这条不变量。`data_layout/` 目录不新增任何 schema 文件
   （Data Layout Spec 附录 B 明确 Matrix 无 schema）。
2. **可复用证据引用层 = 加性交付三种 index，PR A 不动。** 新
   `EvidenceIndexEntry` / `SourceIndexEntry` / `GateEvidenceIndexEntry`（外加各自
   容器），加"forward `status`/`superseded_by` 只住 index、canonical EP 只带
   backward `supersedes_evidence_id`"的不可变边界。PR A 的
   `CandidateGateAssessment.evidence_refs`（`[{evidence_id, role}]`）即 Blueprint
   v1.3 `evidence_package_ids` 的可执行形态 —— **不改名、不动
   `decision_objects.yaml` / `decision_model.py`**。
3. **Provenance = index 表 + walk 不变量。** 冻结 index dataclasses，加声明式
   provenance walk（cell → Assessment → `evidence_refs` → EP.provenance.source_id
   → `source_index` → `external_ref`）+ 跨记录引用完整性校验函数。**不引入
   ProvenanceChain / LineageGraph 这类被持久化的图对象**。

## 三、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/evidence_reference.yaml`（新） | 声明式 registry：`MatrixView@0.1.0` / `EvidenceIndexEntry@0.1.0` / `SourceIndexEntry@0.1.0` / `GateEvidenceIndexEntry@0.1.0` 的 required/optional 字段、`field_kinds`、`allowed_values`、`id_patterns`、`invariants`、容器说明；`vocabularies`（`evidence_index_status` 3 值、`evidence_ref_roles` 3 值、`source_type_values` 10 值、`matrix_cell_regex`、宽表固定列/尾列、`matrix_long_columns`、`decisions_view_columns`）；`migration.parity`（4 个合同 = header parity vs `csv_headers.yaml`，MatrixView 说明"rebuildable projection, no id, no JSON Schema"）；`migration.reusable_evidence_reference`（`mechanism: evidence_refs`、`pr_a_contract_untouched: true`、正文点名 `evidence_package_ids`）；`migration.provenance_walk`（chain + supersession lineage + 不变量）；`migration.immutable_record_boundary`（forward pointer 只住 `EvidenceIndexEntry`）；`migration.deferred`（CRC → PR D、逐 Gate Module → PR E+、decision engine / matrix rebuild engine = not in repo）；`migration.open_questions`（evidence independence 定义 → 科学审核，不阻塞结构）。 |
| `src/objects/evidence_reference_model.py`（新） | frozen `@dataclass` + `__post_init__`，**复用 PR A `decision_model.py` 的 `_deep_freeze` / `_freeze_attr` / `_require_*` / ID 正则**，并复用 PR B `gate_model.py` 的 `_require_canonical_gateset` / `DECISION_VALUES`（三层合同校验不分叉）。对象：`MatrixRow` / `MatrixView`（`gateset_id` 必须是该 level 的 canonical GateSet、`member_gate_ids` 唯一非空、每行每 member gate 恰一 cell、cell ∈ 冻结宽表词表、`decision` ∈ `DECISION_VALUES` ∪ `{"NOT_EVALUATED"}`、`traced_cells()` 列出需追溯的 cell、`wide_columns()` 重建宽表 header）；`EvidenceIndexEntry` / `EvidenceLibraryIndex`（字段顺序 == 冻结 `library_evidence_index` header；`status`/`superseded_by` 一致性：`SUPERSEDED` ⇔ 有 pointer、`ACTIVE` 要求空 pointer、禁自指；容器强制 `evidence_id` 唯一、`superseded_by` 在索引内可解析且无环）；`SourceIndexEntry` / `SourceIndex`（`source_id` 唯一；`year` = 4 位 int 或 4 位串或空；`external_ref` 走 `external:`）；`GateEvidenceIndexEntry` / `GateEvidenceIndex`（行 4 字段 == 冻结 `gate_evidence_index` header；容器带 folder-implicit `gate_id`）。函数：`check_evidence_library_against_sources` / `check_gate_index_against_library` / `check_matrix_cells_are_backed` —— 纯引用完整性，不算 direction/strength/decision。 |
| `src/objects/__init__.py`（改） | 追加 PR C export；PR A / PR B / legacy 符号不变。 |
| `tests/test_evidence_reference.py`（新，48 tests） | 见 §四。 |
| `manifests/runtime_migration_pr_c_manifest.yaml`（新） | `chatgpt_review: PENDING`、boundary 声明、`open_questions`、test 命令、artifact 清单。 |
| `src/objects/README.md` / `src/contracts/README.md`（改） | 追加 PR C 段落；顺带把 PR B 段落里遗留的"exact parity"表述改为"persistence shape mirrors … runtime stricter（runtime-valid ⊂ schema-valid）"，与已合并的 PR B 合同一致。 |

## 四、测试（`tests/test_evidence_reference.py`，48 tests）

- `ContractRegistryTests`：version / 合同集 / `migration.pr == runtime_migration_pr_c` /
  deferred 含 engine + CRC / `open_questions` 含 evidence independence /
  `repository_policy` 禁 persistence + engine / `reusable_evidence_reference.mechanism == "evidence_refs"` 且正文含 `evidence_package_ids` /
  `immutable_record_boundary.forward_pointer_home` / MatrixView 声明为 derived 无 id。
- `RegistryPythonParityTests`：4 合同 `required_fields` == dataclass 无默认字段；
  词表（status / cell regex / 宽表列 / 长表列 / decisions 列）== 模块常量；
  `MATRIX_CELL_STATES` 逐个匹配 regex 且计数 = 4×3+3。
- `CsvHeaderParityTests`：`data_layout/` 无 `matrix.schema.json` /
  `evidence_index.schema.json` / `source_index.schema.json`；
  `library_evidence_index` / `library_source_index` / `gate_evidence_index`
  header == 对应 dataclass `field_names`（含顺序）；YAML `csv_columns` 与
  `required ∪ optional` 自洽；`make_matrix().wide_columns()` 逐字重建
  `matrix_adc_target`；长表 / decisions header == 模块常量。
- `MatrixViewTests`：valid；非 canonical gateset/level → raise，canonical 配对通过；
  坏 id；`member_gate_ids` 空 / 重复 → raise；行缺 member gate cell / 出现非 member
  gate cell → raise；重复 candidate 行 → raise；cell 词表 / `decision` 词表
  reject（`"POSITIVE"` / `"+3"` / `"PROCEED"`）；`NOT_EVALUATED` decision 允许；
  `traced_cells()` 跳过 UNKNOWN / NOT_APPLICABLE / NOT_EVALUATED。
- `EvidenceIndexEntryTests` / `EvidenceLibraryIndexTests`：ACTIVE valid；
  `SUPERSEDED` 无 pointer → raise、pointer 无 `SUPERSEDED` → raise、`ACTIVE` +
  pointer → raise、自指 → raise、`RETRACTED` 可无 pointer；坏 `primary_source_id`
  / `candidate_refs` / `created_at`；`candidate_refs` 可空；容器 `evidence_id`
  唯一；`superseded_by` 必须在索引内可解析；supersession 环 → raise。
- `SourceIndexTests`：valid；坏 `source_id` / `source_type` / `external_ref` /
  `year`；`year` int 或空可接受；`source_id` 唯一。
- `GateEvidenceIndexTests`：valid；行 4 字段各自 reject；容器空 `gate_id` → raise。
- `ProvenanceWalkTests`：`check_evidence_library_against_sources` 悬空
  `primary_source_id` → raise、全解析 → pass；`check_gate_index_against_library`
  悬空 `evidence_id` → raise；`check_matrix_cells_are_backed` —— `POSITIVE/DIRECT`
  cell 无对应 gate-index 条目 → raise、UNKNOWN/NOT_APPLICABLE/NOT_EVALUATED cell
  无需 backing、正确 backing → pass、candidate 不匹配 → raise。
- `ImmutableBoundaryTests`：PR A `EVIDENCE_PACKAGE_FORBIDDEN_FIELDS` 仍含
  `superseded_by` + `status`（forward pointer 只在 PR C 的 index）；
  `decision_objects.yaml` 的 `matrix_and_reusable_evidence_references: PR C`
  未被本 PR 改动。
- `DeepImmutabilityTests`：外部 dict/list 构造后 mutation 不污染
  `MatrixRow.cells` / `EvidenceIndexEntry.candidate_refs`；穿对象改 `cells` →
  `TypeError`；改 `MatrixView.member_gate_ids` → `AttributeError`（frozen）。

## 五、明确未改 / 未做

- **未新增** `src/contracts/data_layout/` 下任何 schema 文件（Matrix / evidence
  index / source index 仍只由冻结的 `csv_headers.yaml` 定义）。
- **未改** PR A：`decision_objects.yaml` / `decision_model.py` /
  `legacy_adapters.py`（只 import 其 helper 与 `EVIDENCE_PACKAGE_FORBIDDEN_FIELDS`）。
  `evidence_refs` 机制不改名、`evidence_package_ids` 不"落实为字段"。
- **未改** PR B：`gate_contracts.yaml` / `gate_model.py` / `legacy_gate_map.py`
  （只 import `_require_canonical_gateset` / `DECISION_VALUES`）。
- **未改** 任何冻结文档、`gate_system.yaml`、`src/capabilities/*`、既有测试。
- **未做** decision engine、matrix rebuild engine、ProvenanceChain/LineageGraph
  持久图对象、CRC / TGT-01–TGT-08 具体内容（PR D）、逐 Gate Module（PR E+）。
- **未解除** `MIGRATION_PENDING`（到 PR E）。无新依赖（仍只 PyYAML）。
- evidence independence 的定义（v5 §16 B-Q6）标为 `open_questions`，交科学审核。

## 六、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 705 tests ... OK   (658 baseline + 47 new -- 见 §四；48 计数含 1 个 subTest)
git diff --check                       # clean
bash scripts/verify_repository_boundary.sh   # 干净 tracked-tree worktree 上 pass
python3 -c "import yaml,sys; yaml.safe_load(open('src/contracts/evidence_reference.yaml'))"  # 结构合法
```

## 七、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（GitHub connector 写
  review 仍 `403`，verdict 以对话与 `logs/chatgpt-review-*.md` 为准）。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一对话复审。
- APPROVE → merge + 独立 docs-only approval-record PR（按 PR #95/#97/#99/#101 先例）。

## 八、后续（PR D，未启动）

- **PR D** —— CRC-ADC-TARGET-GATESET-v1：在 canonical `ADC_TARGET_GATESET` 上，
  用 `Instantiation` + context-specific `gateset_binding` / `gate_binding` refs
  冻结 TGT-01…TGT-08 的 context-specific Gate 合同与 Evidence Ladder（需科学审核）。
  不 mint 第二个 `gateset_id`。审核方 PR B 复审时点名：PR D 实例化时必须锁死
  TGT-01–TGT-08 的 membership / level / 版本，不能让 Module 自由造 Gate ID。
