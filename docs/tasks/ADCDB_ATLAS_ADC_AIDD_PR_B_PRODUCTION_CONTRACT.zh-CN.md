# PR-B：ADCdb SEED + Atlas MUST-PASS 生产契约

**合同版本：** `ADCdb_Atlas_ADC_AIDD_PR_B_Production@0.2.0`
**前置批准：** PR-A `APPROVE`，基线 `2a2e21b`  
**当前状态：** `PR_B_CROSS_INDICATION_SEED_SCOPE_REVIEW_REQUIRED`
**范围：** `MSS/pMMR refractory metastatic CRC, operationally >=3L`

## 1. 通俗说明

PR-B 是第一次把系统从“规则”推进到“真实候选筛选”。ADCdb seed 阶段不要求 ADC 先例已经发生在 CRC：只要靶点在已批准的 ADCdb 快照中有其他癌种或疾病的 ADC modality precedent，就可以作为初始 seed；随后统一拿到 MSS/pMMR refractory mCRC 的公开数据中做 Atlas 验证。

PR-B 先做四件事：锁定 ADCdb 来源和快照；不按 ADCdb 的 disease/indication 过滤，生成约 20–50 个真实 TargetSeed；运行 G1；运行 G2–G4 并输出 survivors 和失败分布。数量不足时如实输出，不补假候选。

这里的逻辑是：ADCdb 的其他癌种/疾病只提供 target-level ADC modality prior，不提供 CRC efficacy 结论。CRC 的临床 territory 仍由 LOCK 固定，CRC transfer 由 Atlas G1–G4 决定。

PR-B 不做 G5–G7、不选 `PRIMARY_TARGET`/`BACKUP_TARGET`、不生成 `NO_GO`、不做 epitope/AIDD、不做抗体或 ADC 设计。

## 2. 执行前置条件

PR-B 只有在以下条件全部满足并写入 run lock 后才可执行：PR-A 已明确 `APPROVE`；clinical territory lock 为 `APPROVED`；ADCdb source admission 为 `APPROVED`；snapshot 逐文件 SHA-256 和整体 manifest 校验通过；identity policy、field whitelist、G1–G4 policy ref 已冻结；外部运行目录不在 Git 仓库内；run id、输入引用和输出引用已生成。

任一条件不满足，必须输出 `RUN_BLOCKED`，不得生成候选或 Gate 结果。

## 3. 输入契约

| 输入 | 必须包含 | 用途 |
|---|---|---|
| approved territory lock | `territory_id`、schema version、refractory definition、intended benefit、endpoint class、review ref | 固定临床问题 |
| ADCdb admission bundle | source id、版本、locator、license/access、field whitelist、identity policy、human review ref | 证明来源已准入 |
| ADCdb snapshot manifest | snapshot id、cutoff、文件清单、size、逐文件 SHA-256、manifest checksum | 保证输入可复现 |
| identity policy | canonical target/ADC/antibody/indication mapping、collision 和 unresolved 路由 | 生成唯一 target identity |
| PR-A run policy | TargetSeed、G1–G4 policy id、阈值和统计单位 | 禁止运行时改规则 |
| Atlas evidence inputs | cohort/accession、patient id、malignant annotation、assay measurement、证据来源 | 执行 G1–G4 |

ADCdb、Atlas matrix、文献全文和运行结果只通过外部路径与 provenance ref 进入运行，不复制进仓库。

## 4. 输出契约

所有输出位于外部 DATA 的单一 run root：

```text
${BIOWORKSPACE_ROOT}/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/<pipeline_run_id>/
├── 00_governance/{run_lock.json,source_admission_bundle.json,source_snapshot_manifest.json,input_provenance.json,execution_log.json}
├── 02_adcdb_seed/{target_seed_candidates.tsv,seed_generation_summary.json,deferred_seed_candidates.tsv}
└── 03_atlas_kill_screen/{atlas_gate_results.tsv,atlas_must_pass.tsv,endpoint_population_map.tsv,population_causality_evidence.tsv,coverage_summary.tsv,atlas_failure_distribution.json,atlas_kill_decision.json}
```

`run_id` 只是兼容字段，必须满足 `run_id == pipeline_run_id`，不得创建第二个运行标识或第二套结果根目录。

仓库只提交契约、代码、测试和 handoff，不提交上述运行产物。

`target_seed_candidates.tsv` 至少包含 `seed_id`、`territory_ref`、`canonical_target_id`、`adcdb_record_refs`、`precedent_disease_or_indication_refs`、`adc_precedent_status`、`extracellular_access_status`、`internalization_delivery_precedent_status`、`intended_benefit`、`endpoint_class`、`initial_development_hypothesis`、`endpoint_driving_population`、`population_causality`、`identity_resolution_status`、`source_snapshot_refs`、证据 refs、`unknown_class` 和 `review_status`。其中 population 和 causality 必须仍为 `UNRESOLVED`；`precedent_disease_or_indication_refs` 可以是 CRC 之外的癌种或疾病，且不得被写成 CRC efficacy evidence。

`atlas_gate_results.tsv` 每个 seed 每个 gate 一行，至少包含 `seed_id`、`canonical_target_id`、`gate_id`、`policy_ref`、`status`、`measurement_unit`、`cohort_refs`、patient/cell counts、effect metric/value、threshold ref、supporting/opposing/conflicting refs、`unknown_class`、missing information 和 next action。`status` 只能是 `PASS`、`KILL` 或 `UNKNOWN`。

`atlas_must_pass.tsv` 只包含 G1–G4 全部 `PASS` 的 seed；没有 survivor 时输出空表加完整 failure distribution，`NO_SURVIVOR` 是合法生产结果。

## 5. 固定运行顺序

```text
RUN_LOCK_VERIFY -> SOURCE_ADMISSION_VERIFY -> ADCDB_SEED_MATERIALIZE
-> TARGET_IDENTITY_RESOLVE -> G1 -> G2 -> G3 -> G4 -> ATLAS_MUST_PASS_EXPORT
```

source admission 或 snapshot 失败就停止；identity unresolved 进入 `DEFERRED_SEED`，不得进入 active Atlas；G1/G4 共用 `PR-A-PATIENT-AGGREGATION-v0.1.0`；G2 使用固定 `population_state_prevalence_ratio`，不得临时换指标。

每个 `UNKNOWN` 必须标注 `FATAL_UNKNOWN`、`RESOLVABLE_CRITICAL_UNKNOWN` 或 `CARRIED_RISK`。

## 6. 审核边界

本 PR 审核“PR-B 生产运行是否可以开始”。在 PR-B 明确 `APPROVE` 之前，不得读取 ADCdb、下载或解析 Atlas 输入、生成真实 TargetSeed 或写入运行结果。PR-B 获批后，结果仍必须作为可审计 PR 提交；即使 survivors 为零，也应交付 `NO_SURVIVOR`，不能先改架构。
