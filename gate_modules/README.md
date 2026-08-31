# StelligenOS Gate Modules

## 这个目录是什么

`gate_modules/` 保存**逐 Gate 的 primary Evidence Production Module 实现**。一个
Gate 一个主 Module（CURRENT_SYSTEM v5 §6.4）。每个 Module 是一个独立的
Python 包，把「一个 Gate 的施工合同」翻译成确定性可执行代码。

施工合同（施工图 + 17 项验收清单）是 `src/contracts/gate_modules/<name>.yaml`
（Runtime Migration PR E1 起冻结）；本目录是那份合同的实现（PR E2 起）。

## 内核不变式（Kernel Invariants）

以下五条是本目录存在的前提。任何 Module 都不得违反：

1. **单向依赖。** Module 可以引用内核的对象、Gate 身份和合同；内核不得引用、
   导入或依赖任何 Module。`src/` 下不允许出现 `import gate_modules` 或
   `from gate_modules`。此不变式由 `tests/test_gate_modules_boundary.py` 校验。
2. **内核定义合同，Module 实现合同。** Module 不得修改 Gate id / name /
   candidate ownership / `gate_question` / Evidence Ladder / evidence ceiling /
   fatal / unknown / conflict / inference 语义（v5 §6.4）。它不得跨 Gate 推理，
   不得降低 measurement requirement，不得把 `UNKNOWN` 变成 `PASS` / `HOLD` /
   `KILL`。
3. **Module 不产生 canonical 记录，也不产生决策。** Module 的输出只能是
   `EvidencePackage` 集合 + 一个 **non-canonical assessment proposal envelope**
   + machine acceptance record + sweep completion record。它**不构造**
   `CandidateGateAssessment`（PR A：`CANONICAL_REVIEW_STATUS = HUMAN_APPROVED`，
   由 human review surface 在批准后构造），不产生 `Decision` / `KILL`，不写
   `MatrixView`。
4. **仓库仍然 data-free、零 persistence。** Module 只保存代码、合同、身份和
   说明。真实 retrieval / entity resolution / source registry / EvidenceIndex
   更新 / `RUNS` / `ASSESSMENTS` 文件写入全部在外部工作区，通过 injected port
   进入。Module 不上网、不开 subprocess、不写仓库、不自增 ID。
5. **Module 只做 Gate-specific 科学判读。** 共享的 retrieval / entity
   resolution / provenance ledger / serialization（v5 §6.5）不按 Gate 重写；
   Module 只定义它需要的 normalized port。

## 目录约定

每个 Module 目录包含：

- `module.yaml`：身份、版本、Gate binding、port 清单、边界与禁止行为。
- `contracts.py`：frozen dataclass 输入 / 输出契约。
- `ports.py`：Protocol 端口（provider / id allocator / source registry）。
- `classify.py` / `evidence.py` / `aggregate.py` / `acceptance.py`：确定性科学核心。
- `module.py`：纯 Python `run(...)` orchestration，只调用 injected port。

文件名只允许 `A-Z`、`a-z`、`0-9`、`_`、`.`、`-`，禁止空格。

## Module 注册表

| Module | Gate | GateSet | 版本 | 状态 |
|---|---|---|---|---|
| [`MOD-TGT01`](./tgt01_adc_modality_precedent/) | TGT-01 ADC Modality Precedent | `ADC_TARGET_GATESET@1.0` | `1.0.0` | built (PR E2) |
| [`MOD-TGT02`](./tgt02_indication_specific_malignant_cell_coverage/) | TGT-02 Indication-Specific Malignant-Cell Coverage | `ADC_TARGET_GATESET@1.0` | `1.0.0` | built (PR E8) |
| [`MOD-TGT03`](./tgt03_treatment_metastatic_persistence/) | TGT-03 Treatment / Metastatic Persistence | `ADC_TARGET_GATESET@1.0` | `1.0.0` | built (PR E10) |
| [`MOD-TGT04`](./tgt04_tumor_surface_availability_density_plausibility/) | TGT-04 Tumor Surface Availability / Density Plausibility | `ADC_TARGET_GATESET@1.0` | `1.0.0` | built (PR E12) |
| [`MOD-TGT05`](./tgt05_normal_tissue_fatal_liability/) | TGT-05 Normal-Tissue Fatal Liability | `ADC_TARGET_GATESET@1.0` | `1.0.0` | built (PR E4) |
| [`MOD-TGT08`](./tgt08_target_opportunity_competition_ip_whitespace/) | TGT-08 Target Opportunity / Competition / IP Whitespace | `ADC_TARGET_GATESET@1.0` | `1.0.0` | built (PR E6) |

其余两个 TGT primary Module（TGT-06 → TGT-07）属后续
PR E-series，`primary_module_version` 仍为 `0.0.0`。

## MIGRATION_PENDING

一个 TGT-01 Module 做完远不能宣称 8-Gate runtime migration 完成。全部 8 个
primary Module 完成前，`MIGRATION_PENDING` 保持。
