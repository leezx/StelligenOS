# `src/contracts/data_layout/`

`StelligenOS Data Layout Spec v1.0` 的机器可读 schema。

- 规范文档：`docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md`
- worked example（单文档）：`docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md`
- 外部骨架生成：`scripts/scaffold_data_layout.sh`

## 内容

| 文件 | 校验对象 |
|---|---|
| `candidate.schema.json` | `10_CANDIDATES/Lnn_*.csv` 的一行（identity 字段；机器禁止 `context_id` / `direction` / `strength` / `decision` / `score` / …） |
| `context.schema.yaml` | `15_CONTEXTS/CTX-*/vNNN.yaml`（Context，可复用、版本化、无 verdict） |
| `assessment.schema.json` | `TGT-NN/ASSESSMENTS/<cand>/vNNN.json`（canonical = `HUMAN_APPROVED` only；direction×strength 组合与 `CONFLICTING` 两侧 machine-enforced） |
| `evidence_package.schema.json` | `30_EVIDENCE_LIBRARY/PACKAGES/EP-*/evidence.json`（immutable-by-ID；`schema_version` 非内容版本） |
| `run_manifest.schema.json` | `TGT-NN/RUNS/RUN-*/run_manifest.json` |
| `decision.schema.json` | `20_INSTANTIATIONS/<inst>/DECISIONS/DEC-*.json`（canonical = `HUMAN_APPROVED` only；`assessment_snapshot` pin `{assessment_id, assessment_version, cell}`） |
| `instantiation.schema.yaml` | `20_INSTANTIATIONS/<inst>/instantiation.yaml`（含 `context_version`） |
| `gate_binding.schema.yaml` | `TGT-NN/gate_binding.yaml` 与 `gateset_binding.yaml`（`oneOf` 两分支） |
| `csv_headers.yaml` | 所有 CSV 的规范表头（logical name → 有序列名）。`gate_current_assessments` 与 `assessments_long` 列相同（作用域不同）。 |

回归测试：`tests/test_scaffold_data_layout.sh`（`scaffold_data_layout.sh` 的
repo-boundary 拒绝、symlink 逃逸拒绝、外部只写表头行、幂等）。

## 边界

- 本仓库**不存放 `.csv` 文件**（`scripts/verify_repository_boundary.sh` 禁止
  data-like 文件）。CSV 的规范定义在 `csv_headers.yaml`；真实 `.csv` 表头由
  `scaffold_data_layout.sh` 在**外部** data root 写出。
- 这些 schema 是**声明**，本仓库不运行本布局下的任何真实数据。
- schema 版本随 `STELLIGENOS_DATA_LAYOUT_SPEC` 演进（`v1.x` 兼容增改；`v2.0`
  破坏性变更需专家审核）。`$schema` 使用 draft 2020-12。
