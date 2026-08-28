# `src/contracts/data_layout/`

`StelligenOS Data Layout Spec v1.0` 的机器可读 schema。

- 规范文档：`docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md`
- worked example（单文档）：`docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md`
- 外部骨架生成：`scripts/scaffold_data_layout.sh`

## 内容

| 文件 | 校验对象 |
|---|---|
| `candidate.schema.json` | `10_CANDIDATES/Lnn_*.csv` 的一行（统一 identity 字段） |
| `assessment.schema.json` | `TGT-NN/ASSESSMENTS/<cand>/vNNN.json`（CandidateGateAssessment） |
| `evidence_package.schema.json` | `30_EVIDENCE_LIBRARY/PACKAGES/EP-*/evidence.json` |
| `run_manifest.schema.json` | `TGT-NN/RUNS/RUN-*/run_manifest.json` |
| `decision.schema.json` | `20_INSTANTIATIONS/<inst>/DECISIONS/DEC-*.json` |
| `instantiation.schema.yaml` | `20_INSTANTIATIONS/<inst>/instantiation.yaml` |
| `gate_binding.schema.yaml` | `TGT-NN/gate_binding.yaml` 与 `gateset_binding.yaml`（`oneOf` 两分支） |
| `csv_headers.yaml` | 所有 CSV 的规范表头（logical name → 有序列名） |

## 边界

- 本仓库**不存放 `.csv` 文件**（`scripts/verify_repository_boundary.sh` 禁止
  data-like 文件）。CSV 的规范定义在 `csv_headers.yaml`；真实 `.csv` 表头由
  `scaffold_data_layout.sh` 在**外部** data root 写出。
- 这些 schema 是**声明**，本仓库不运行本布局下的任何真实数据。
- schema 版本随 `STELLIGENOS_DATA_LAYOUT_SPEC` 演进（`v1.x` 兼容增改；`v2.0`
  破坏性变更需专家审核）。`$schema` 使用 draft 2020-12。
