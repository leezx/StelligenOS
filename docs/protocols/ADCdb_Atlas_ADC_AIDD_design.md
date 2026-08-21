# ADCdb-Atlas-ADC AIDD Design Pipeline

- 文档版本：`ADCdb_Atlas_ADC_AIDD_Design@0.3.0`
- 状态：`DESIGN_REVIEW_REQUIRED_EXECUTION_NOT_AUTHORIZED`
- 首个疾病试点：`MSS/pMMR refractory metastatic colorectal cancer, operationally >=3L`
- 策略：Small Biotech、repurposing-first、计算优先、外部平台协作
- 历史版本：[`ADCdb_Atlas_ADC_AIDD_design.v0.2.md`](./ADCdb_Atlas_ADC_AIDD_design.v0.2.md)

本文件是唯一的 v0.3 authoritative pipeline。v0.2 仅作为 immutable historical snapshot；不得从 v0.2 复制旧 Stage/I-O 顺序作为当前执行路线。

## 1. 最终目标与 100% 定义

目标不是评价所有膜蛋白或消除所有不确定性，而是在明确的 refractory patient territory 中，从已有 ADC precedent 的 target 出发，用有限的高信息量筛选收敛到 `PRIMARY_TARGET`、最多一个 `BACKUP_TARGET` 或 `NO_GO`，再进入 epitope/AIDD、抗体 hit、ADC hit 和渐进验证。

100% 的终点是一次版本化、可复现、可审计的外部运行，从 patient territory lock 到至少一个组装后的 ADC hit，并形成经人类批准的 `GO`、`ITERATE` 或 `STOP` 决策包。该终点不等于 DevelopmentCandidate、IND-ready asset、临床候选物或临床成功。

```text
PatientTerritory -> TargetSeed -> AtlasSurvivor -> TargetHypothesis
  -> TargetCommit -> EpitopeHypothesis -> BinderCandidate
  -> ADCConstruct -> ADC_HIT
```

所有科学数据、证据、候选、模型产物和实验结果保存在仓库外部；StelligenOS 只保存设计、合同、代码和小型审计文档。

## 2. 唯一 critical path

```text
0 LOCK
  -> 1 ADCdb SEED
  -> 2 ATLAS MUST-PASS KILL SCREEN
  -> 3 DEVELOPABILITY MUST-PASS KILL SCREEN
  -> 4 TARGET_COMMIT
  =============== target selection done ===============
  -> 5 EPITOPE + AIDD
  -> 6 ANTIBODY HIT
  -> 7 ADC HIT
  -> 8 PROGRESSIVE VALIDATION
```

此顺序是 v0.3 唯一有效顺序。SponsorFit、ProgramCommitment 和 ValueInflection 不属于 target-selection critical path，不得作为 Stage 4 -> 5 的承重输入或阻塞条件。

## 3. 全局边界与证据规则

### 3.1 Source admission、外部运行和 provenance

ADCdb、Atlas、临床、专利、蛋白结构和正常组织来源必须有 admission record、snapshot/cutoff、checksum、licence/access note、字段白名单和 identity policy。当前已知 `ADCdb SRCADM-02` 未准入时，不得执行本 pipeline。

每次运行只有一个外部根目录：

```text
${BIOWORKSPACE_ROOT}/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/<pipeline_run_id>/
├── 00_governance/
├── 01_patient_territory/
├── 02_adcdb_seed/
├── 03_atlas_kill_screen/
├── 04_developability_kill_screen/
├── 05_target_commit/
├── 06_epitope_aidd/
├── 07_antibody_hit/
├── 08_adc_hit/
├── 09_progressive_validation/
└── report/
```

每个 artifact 必须携带：

```text
pipeline_run_id, pipeline_version, stage_id, artifact_schema_version,
record_id, source_snapshot_refs, source_record_refs, code_commit,
software_or_model_versions, config_checksum, artifact_checksum,
created_at, created_by, evidence_refs, review_status
```

不得将数据、cache、result、数据库或模型权重写入 StelligenOS 仓库。parser 失败、alias 无法消歧、structure 缺失、模型失败、平台不可用或实验失败必须形成显式 blocker/error artifact；不得以空表、mock 或自然语言继续。

### 3.2 ADC 生物学三层拆分

ADC 不要求 target 本身必须是癌症 driver：

1. `endpoint_population_causality`：被杀的 malignant state/population 是否参与驱动 refractory disease、progression、metastasis、recurrence、survival 或 intended benefit；
2. `target_to_population_mapping`：target 是否稳定标记该 population，并覆盖足够患者和 malignant burden；
3. `target_biological_causality`：target 本身是否驱动疾病，这是 bonus，不是 ADC target 的默认 must-pass。

### 3.3 Proxy 与 claim boundary

- RNA 只能是 expression/antigen-density proxy，不能写成 surface protein 或 ADC delivery 证据。
- ADCdb precedent 是 target-level modality prior，不能自动证明 CRC efficacy、安全窗、当前 epitope 或当前 binder internalization。
- Atlas association 不能写成 causality；population causality 与 target causality 分开。
- target-level delivery precedent 不能替代 `new binder x epitope x CRC cell` 的实验 internalization。
- patent triage 只能写 `FTO_PLAUSIBILITY_TRIAGE`，不能写 `FTO_CLEARED`。

### 3.4 Unknown 分层

`UNKNOWN` 不是正证据，但也不自动等于无限期 HOLD：

- `FATAL_UNKNOWN`：没有该信息绝不能支付下一阶段成本，例如是否为 extracellular antibody-accessible target；必须先解决。
- `RESOLVABLE_CRITICAL_UNKNOWN`：允许一次针对性 evidence acquisition；一次补证仍 unresolved，则退出当前 active funnel。
- `CARRIED_RISK`：进入 risk register 并在后续解决，例如新 epitope 在 CRC 细胞中的最终 internalization。

每个 unknown 必须有 `unknown_class`、`affected_decision`、`one_shot_resolution_plan`（适用时）、`carry_forward_owner` 和 `stop_if_unresolved`。

## 4. 审核与成本门控

每个阶段遵循：

```text
contract/design PR -> ChatGPT APPROVE -> external run
-> result PR -> ChatGPT APPROVE
```

Target selection 分为三个审核 PR：

```text
PR-A  LOCK、ADCdb seed、Atlas kill、TargetCommit contract
PR-B  source admission、seed generation、Atlas MUST-PASS result
PR-C  Developability MUST-PASS、TARGET_COMMIT result
```

PR-C 获得指定 ChatGPT 审核对话明确 `APPROVE` 且人类批准后，才可建立 PR-D Epitope/AIDD。脚本成功、产物存在或没有明显代码错误均不构成科学放行。

## 5. Stage 0 — LOCK：Opportunity 与 patient territory

固定 territory：`MSS/pMMR refractory metastatic CRC, operationally >=3L`。

输入为人类给定约束、临床 unmet need、SOC/既往治疗和公开临床证据。输出：

- `clinical_territory.yaml`
- `clinical_hypothesis.json`

必填 refractory definition、prior-treatment classes、关键转移背景、current failure mode、intended benefit、endpoint class 和 patient-selection hypothesis。早期只锁 endpoint class，不假装锁定最终注册 endpoint。人群过宽、refractory 未操作化或 biomarker 无法连接患者选择时 STOP/BLOCK。

## 6. Stage 1 — ADCdb SEED：TargetSeed generation

目的：从已准入 ADCdb 直接生成可进入 Atlas screen 的 `TargetSeed`，不先建立无决策终点的 target universe，也不要求 Atlas 尚未产生的 population 结论。

### 6.1 TargetSeed minimum contract

```text
Patient Territory
× Intended Benefit / Endpoint Class
× ADC Target
× ADC Precedent
× Initial Development Hypothesis
```

以下两个字段在此阶段合法且必须显式写出：

```yaml
endpoint_driving_population: UNRESOLVED
population_causality: UNRESOLVED
```

`TargetSeed` 的 initial development hypothesis 只描述：target-level ADC delivery precedent 是否支持把该 target 作为 modality entry point，以及后续 Atlas 要验证的 population/coverage 假设；它不是已确认的 TargetHypothesis。

### 6.2 Precedent floor 与输出

每个 active seed 至少有可追溯记录：

- extracellular antibody-accessible target；
- real ADC construct precedent；
- internalization/delivery precedent；
- preferably clinical precedent。

输出：`target_seed_candidates.tsv`、`adc_program_precedent.tsv`、`target_identity_map.tsv`、`seed_source_manifest.json`。每个 seed 记录 canonical target、aliases、ADC programme refs、highest credible stage、antibody refs、delivery refs、source locators 和 unknowns。缺任一 precedent floor 的记录可留在 audit universe，但不得进入 active seed funnel。

此阶段只做 universe reduction，不做复杂 ranking。Stage 1 不 materialize `TargetHypothesis`，也不填写 population causality 结论。

## 7. Stage 2 — ATLAS MUST-PASS：Kill screen

Atlas 是 cheap, high-information kill engine。它消费 `TargetSeed`，并把 `endpoint_driving_population=UNRESOLVED` 的 seed 升级为 Atlas survivor 或退出 active funnel。

| Gate | 必答问题 | 直接 KILL 条件 |
|---|---|---|
| G1 expression/prevalence | target 在 MSS/pMMR refractory mCRC malignant cells 是否存在 | RNA clearly absent/low |
| G2 population mapping | target-positive malignant cells 属于哪个 endpoint-driving state/population | 无法形成可审计 mapping |
| G3 population causality | 该 population 是否参与驱动 refractory disease/intended benefit | 证据不足且一次补证仍无法解决 |
| G4 coverage | target-positive population 覆盖多少患者和 malignant burden | coverage 不足 |

允许证据包括 longitudinal、treatment enrichment、perturbation、lineage、spatial progression、recurrence/metastasis enrichment、dependency、organoid perturbation 和多 cohort replication。必须保留 patient-level prevalence、cell/burden coverage、heterogeneity、treatment-state、supporting/opposing/conflicting refs 和 unknown class。

输出：`atlas_must_pass.tsv`、`endpoint_population_map.tsv`、`population_causality_evidence.tsv`、`coverage_summary.tsv`、`atlas_kill_decision.json`。

Stage 2 通过后才 materialize：

```yaml
endpoint_driving_population: <audited population or state>
population_causality: <PASS/UNKNOWN with evidence refs>
atlas_survivor_status: PASS
```

这个输出投影为 `TargetHypothesis` 的 Atlas-backed fields；它不是 TargetCommit，也不等于 clinical efficacy。典型收敛 `100 -> 40 -> 18 -> 9 -> 5 -> 3` 只是说明，不是硬编码阈值。

## 8. Stage 3 — DEVELOPABILITY MUST-PASS：Atlas survivor screen

本阶段只消费 **Atlas MUST-PASS survivors**，理想规模约 3-5 个；数字是 descriptive，不是 hard-coded。不得写成“对 ADCdb SEED stage 的 3-5 个 target”。

### G5 Normal-tissue fatal risk

只问是否存在足以阻止下一笔 antibody/AIDD 成本的明显 fatal risk：高正常组织 surface expression、关键器官必要性、已有 target-mediated toxicity 或明确 ADC precedent toxicity 可直接 KILL；一般 uncertainty 进入 risk register。

### G6 Competition / Small-Biotech feasibility

高拥挤不等于科学 KILL。若同时存在 crowded target、crowded CRC indication、多个 late-stage ADC 且没有明显 epitope differentiation，可路由为 `OUT_OF_MANDATE`；否则保留 `ACTIVE_SEARCH`、`WATCHLIST` 或 `PARTNER_ONLY` metadata。不得用任意项目数阈值替代 sponsor-relative 判断。

### G7 Epitope whitespace / realizability

检查 extracellular structure/topology、accessibility、glycans、known antibody/ADC epitopes、patent bins、membrane geometry 和 internalization hypothesis。输出只能是 `EPITOPE_PLAUSIBLE`、`EPITOPE_BLOCKED` 或 `UNKNOWN`。没有可开发 whitespace 可 KILL 或 `OUT_OF_MANDATE`；未知不能无限循环。

输出：`developability_must_pass.tsv`、`normal_tissue_fatal_risk.tsv`、`competition_feasibility.tsv`、`epitope_whitespace_triage.tsv`、`opposing_evidence.tsv`。完整 safety、shedding、metastasis、product-level TI 和 linker-payload FTO 可在后续 evidence package 做，但除非触发 fatal blocker，不阻塞第一轮 target selection。

## 9. Stage 4 — TARGET_COMMIT

`TARGET_COMMIT` 是 Small Biotech 的资本承诺边界，不是科学真理。主干输出严格为：

```text
PRIMARY_TARGET
BACKUP_TARGET (最多一个)
NO_GO
```

旧的 `PROVISIONAL_ADVANCE`、`EXPLORATION`、`HOLD`、`FAIL`、`WATCHLIST`、`PARTNER_ONLY` 只能作为 metadata/audit detail，不能替代主干输出。

任何 G1-G7 hard fail 直接退出 active funnel。剩余 target 不训练综合模型、不构造黑盒总分，使用固定 lexicographic priority：

1. ADC precedent strength；
2. MSS/pMMR refractory mCRC patient coverage；
3. endpoint-driving population evidence；
4. normal-tissue margin；
5. CRC competitive whitespace；
6. epitope whitespace；
7. ease of antibody/AIDD execution。

输出 `target_commit.json` 与 `target_commit_table.tsv`，至少包括：

```yaml
primary_target: ...
backup_target: ...
no_go: false
territory_ref: ...
endpoint_driving_population: ...
population_causality: ...
selection_order: [adc_precedent, coverage, population_evidence, normal_tissue, competition, epitope, execution]
hard_gate_results: ...
development_hypothesis: ...
primary_unresolved_product_risk: new_epitope_internalization_and_construct_specific_window
residual_risks: ...
development_route: SELF_DEVELOP_TO_ADC_HIT
likely_exit: CO_DEVELOP_OR_LICENSE
human_decision_ref: ...
review_status: ...
```

放行必须恰好一个 primary、最多一个 backup，或明确 `NO_GO`；所有 selection input 可追溯；residual risks 和下一笔成本明确；人类批准已记录。

### 9.1 DevelopmentRoute（非 critical path）

原 v0.2 的 `SponsorFitAssessment`、`ProgramCommitmentReview`、`ValueInflectionPlan` 不删除，但在 v0.3 只作为 TargetCommit 后的 `DevelopmentRoute` metadata，用于合作、许可、外包和成本规划。它们不是 Stage 4 -> Stage 5 的承重输入，不得把 `PARTNER_NOW`、`MONITOR` 或 `DATA_PACKAGE_ONLY` 重新变成科学 target-selection gate。

## 10. Stage 5 — EPITOPE + AIDD

只有 TargetCommit 获批后进入。输入为 approved TargetCommit、target/antibody/epitope patent triage、extracellular topology/structure、glycan/PTM/isoform、species orthology、negative-design constraints 和 AIDD tool manifest。

顺序固定为：

```text
target biology -> epitope hypothesis -> IP-guided whitespace
-> structure preparation -> negative design -> de novo design
-> multi-objective ranking -> diversity -> focused synthesis panel
```

输出 `epitope_opportunities.tsv`、`epitope_packets/`、`aidd_input.yaml`、真实工具产生的 `binder_candidates.fasta`、`predicted_structures/`、`binder_ranking.tsv`、`synthesis_panel.tsv` 和 `focused_validation_plan.yaml`。预测只能叫 `design candidate`，不能叫 binder、novel epitope 或 ADC-ready。new-epitope internalization 是 `CARRIED_RISK`，不能由 target-level precedent 代替。

## 11. Stage 6 — ANTIBODY HIT

输入为 human-approved synthesis panel、真实 expressed binder lots、recombinant target、target-positive/negative cells、relevant refractory CRC models 和 controls。

最小实验：identity/purity/aggregation/expression、biochemical binding、cell-surface binding、specificity、epitope verification/binning、internalization kinetics、trafficking/lysosomal delivery、cross-reactivity 和 developability。

输出 `antibody_hit_validation.tsv`、`binding_kinetics.tsv`、`epitope_validation.tsv`、`internalization_trafficking.tsv`、`developability_qc.tsv`、`adc_grade_binder_decision.json`。只有实验确认的 `ADC_GRADE_HIT` 才能进入 ADC assembly。新 epitope/binder 失败不自动回溯为 target fail，除非 target-level hard evidence 被更新。

## 12. Stage 7 — ADC HIT

输入为 Stage 6 `ADC_GRADE_HIT`、实测 binding/epitope/internalization/trafficking/developability evidence、target density/heterogeneity、platform capability、linker-payload/conjugation triage 和 human conjugation authorization。

成熟 platform 优先，记录 antibody format/Fc、conjugation site、linker release、payload class、DAR、hydrophobicity、stability、bystander、cross-resistance、manufacturability 和许可边界。正式 linker-payload FTO 在此阶段执行，而不是在 target seed 阶段提前删除 target。

输出 `adc_design_matrix.tsv`、`platform_selection.md`、`construct_specifications.yaml`、`linker_payload_fto_triage.tsv`、`manufacturing_qc_plan.yaml`、`manufactured_lot_manifest.json`。只有 physically realized 且 release-QC 合格的 construct 才能进入 Stage 8。

## 13. Stage 8 — PROGRESSIVE VALIDATION

按最小高信息量顺序执行，每层允许停止：

| 子阶段 | 关键问题 |
|---|---|
| 8A identity/binding retention | 偶联后 identity、binding、specificity 是否保留 |
| 8B delivery retention | internalization、trafficking、lysosomal delivery 是否保留 |
| 8C conjugate QC | 稳定性、payload release、DAR、free payload、aggregation、批间一致性 |
| 8D in-vitro activity | target-dependent killing、density threshold、bystander、payload sensitivity、resistance controls |
| 8E translational models | refractory mCRC state coverage、heterogeneity、normal-cell selectivity |
| 8F focused in-vivo POC | 仅在独立 human cost decision 和 value-inflection criterion 存在时执行 |

最终输出 `adc_hit_decision_package/` 与 human `GO/ITERATE/STOP`。预测候选、设计 spec、已下单 construct 或单一 affinity/readout 都不是 ADC hit。

## 14. 最小 I/O contract

| From | To | 唯一允许的承重输入 |
|---|---|---|
| Stage 0 | Stage 1 | approved territory/source/snapshot/policy refs |
| Stage 1 | Stage 2 | `TargetSeed`；population 与 population causality 明确为 `UNRESOLVED`，不得预填 Atlas 结论 |
| Stage 2 | Stage 3 | Atlas MUST-PASS survivors / Atlas-backed `TargetHypothesis` refs |
| Stage 3 | Stage 4 | developability evidence、route metadata、opposing/conflicting/unknown refs |
| Stage 4 | Stage 5 | approved `TargetCommit` + AIDD execution decision；不需要 SponsorFit/ProgramCommitment 作为 science gate |
| Stage 5 | Stage 6 | human-approved diverse synthesis panel + reproducible AIDD manifest |
| Stage 6 | Stage 7 | experimental `ADC_GRADE_HIT` + binding/epitope/internalization/trafficking/developability refs + conjugation authorization |
| Stage 7 | Stage 8 | physically realized construct refs + release QC |
| Stage 8 | final | evidence-backed human `GO/ITERATE/STOP` package |

任何 Stage 不得通过复制下游字段、预填 PASS 或自然语言暗示绕过上游结果审核。

## 15. Failure、blocker 与成本跃迁

至少使用：`SOURCE_ADMISSION_BLOCK`、`IDENTITY_RESOLUTION_BLOCK`、`CLINICAL_TERRITORY_BLOCK`、`ADC_PRECEDENT_INSUFFICIENT`、`CRC_CONTEXT_FAIL`、`ENDPOINT_POPULATION_FAIL`、`COVERAGE_FAIL`、`NORMAL_TISSUE_FAIL`、`SURFACE_ACCESS_FAIL`、`COMPETITION_ROUTE_BLOCK`、`IP_RISK_BLOCK`、`EPITOPE_FAIL`、`AIDD_PIPELINE_ERROR`、`BINDER_BINDING_FAIL`、`BINDER_DEVELOPABILITY_FAIL`、`ADC_CONJUGATION_FAIL`、`ADC_MECHANISM_FAIL`、`PAYLOAD_MISMATCH`、`TRANSLATIONAL_FAIL`、`EVIDENCE_INSUFFICIENT`、`PIPELINE_ERROR`。

`BLOCK` 表示当前不能继续，不等于科学 KILL；`PIPELINE_ERROR` 不得转成资产结论；`EVIDENCE_INSUFFICIENT` 必须带 unknown class 和下一行动。每条失败必须包含 `failure_class`、`failed_stage`、`affected_claims`、`evidence_refs`、`recoverable` 和 `recommended_next_action`。

| 成本跃迁 | 必需 artifact | 未获批时 |
|---|---|---|
| Stage 4 -> 5 AIDD | `target_commit` + `aidd_execution_decision.json` | 不运行 AIDD |
| Stage 5 -> 6 synthesis | `synthesis_panel_decision.json` | 不下单，不生成实验结果 |
| Stage 6 -> 7 conjugation | `conjugation_authorization.json` + `ADC_GRADE_HIT` | 不组装 ADC |
| Stage 8E -> 8F in-vivo | `in_vivo_cost_escalation_decision.json` | 不惯性扩张动物实验 |

## 16. 当前进度与不授权项

100% endpoint：从 locked territory 产生至少一个经人类批准的 ADC hit decision package。

| Workstream | 权重 | 当前状态 | blocker | 下一里程碑 |
|---|---:|---|---|---|
| Funnel design/governance | 10% | v0.3 PR #88 revision pending | ChatGPT review pending | approve/merge v0.3 |
| Source admission/snapshots | 10% | not started | `SRCADM-02` ADCdb 未准入 | Stage 0 contract |
| Target selection | 35% | not started | 依赖 source + territory | PR-B/PR-C |
| Epitope/AIDD/binder | 15% | not started | 依赖 TargetCommit 和工具 | PR-D |
| ADC assembly | 10% | not started | 依赖 ADC_GRADE_HIT 和 platform | Stage 7 |
| Progressive validation | 20% | not started | 依赖 manufactured construct 和实验资源 | Stage 8 |

当前总体进度：`10% -> 10% (+0%)`；工程/设计治理为 `10%`，科学就绪度和实验/运营就绪度均为 `0%`。v0.3 不解除 `SRCADM-02`，不构成 target recommendation。

本设计不授权：运行 ADCdb、Atlas、Gate、TargetCommit、AIDD、synthesis、ADC assembly 或实验；下载数据；生成 epitope/抗体/结构/linker-payload；联系平台/CRO；将 result/cache/database/model weights 写入仓库；修改既有 authoritative contracts、Gate、lifecycle 或 core objects；或以本设计替代后续 contract PR、result PR、ChatGPT 审核和人类决策。
