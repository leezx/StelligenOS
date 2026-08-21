# PR-A：ADCdb → Atlas Target-selection Execution Contract

- 合同版本：`ADCdb_Atlas_ADC_AIDD_PR_A_Contract@0.1.0`
- 状态：`CONTRACT_REVIEW_REQUIRED_EXECUTION_NOT_AUTHORIZED`
- 对应 frozen pipeline：`ADCdb_Atlas_ADC_AIDD_Design@0.3.0`
- 疾病范围：`MSS/pMMR refractory metastatic CRC, operationally >=3L`
- 本 PR：只定义输入、输出、计算单位、阈值、状态和验收；不下载、不解析、不运行。

## 1. 操作者先看这里

这份 PR-A 解决一个很具体的问题：把 v0.3 的文字规则变成下一步可以机械执行的合同。

它不会告诉我们哪个靶点最好，也不会提前运行 Atlas。PR-A 获批后，才允许建立 PR-B，实际生成 20–50 个左右的 `TargetSeed`，并对每个 seed 做 Atlas G1–G4。

```text
锁定 MSS/pMMR refractory mCRC >=3L
  -> 固定 ADCdb 来源和快照
  -> 生成约 20-50 个 TargetSeed
  -> 用 G1-G4 杀掉明显不适合的 seed
  -> 输出 Atlas MUST-PASS survivors
```

20–50 是第一批生产容量目标，不是为了凑数的通过条件；真实可审计 seed 数不足时必须如实输出较少数量或空结果。

## 2. PR-A 的输入与输出

### 2.1 输入

| 输入 | 作用 | PR-A 要冻结的内容 |
|---|---|---|
| `clinical_territory.yaml` | 锁定为谁解决什么问题 | 唯一权威的 territory lock：字段、schema version、枚举、空值规则、review status |
| `clinical_hypothesis.json` | 记录初始开发假设 | 只能引用同一 `territory_id/schema_version`，不得扩大 clinical territory；其假设内容和引用必须在运行前冻结 |
| ADCdb source record | 证明来源是什么 | source id、版本、locator、license/access、field whitelist |
| ADCdb snapshot manifest | 证明本次读的是哪一份 | snapshot id、cutoff、文件清单、逐文件 SHA-256、整体 manifest checksum |
| identity policy | 统一 target/ADC/antibody/indication 别名 | canonicalization、collision、unresolved 处理 |
| run policy | 固定 G1–G7 的规则版本 | policy id/version、阈值、证据层级、decision precedence |

`clinical_territory.yaml` 是唯一 authoritative clinical territory object。`clinical_hypothesis.json` 是受其约束的 derived hypothesis object；二者必须在 LOCK 中引用同一 `territory_id` 和 `schema_version`，且 hypothesis 不能扩大 disease、biomarker、metastatic status、line、refractory definition、intended benefit 或 endpoint scope。`review_status` 只有 `APPROVED` 可以进入 PR-B；枚举值、空值处理和 cross-field invariant 必须在 source admission 前冻结。

LOCK 的最低字段是：

```yaml
territory_id: <required>
schema_version: TargetSelectionLock@0.1.0
disease: colorectal_cancer
biomarker_state: MSS/pMMR
metastatic_status: metastatic
operational_line: ">=3L"
refractory_definition: <required>
prior_treatment_classes: [<required controlled values>]
current_failure_mode: <required>
intended_benefit: <required>
endpoint_class: <required controlled value>
patient_selection_hypothesis: <required>
source_refs: [<non-empty stable refs>]
human_review_ref: <required when APPROVED>
review_status: APPROVED
```

### 2.2 输出

PR-A 只冻结输出形状，实际结果由 PR-B/PR-C 写入外部 DATA：

```text
00_governance/
├── source_admission_bundle.json
├── source_snapshot_manifest.json
├── field_dictionary.yaml
├── identity_resolution_policy.yaml
├── target_selection_run_policy.yaml
└── run_governance.yaml

02_adcdb_seed/target_seed_candidates.tsv
03_atlas_kill_screen/
├── atlas_must_pass.tsv
├── endpoint_population_map.tsv
├── population_causality_evidence.tsv
├── coverage_summary.tsv
└── atlas_kill_decision.json
04_developability_kill_screen/
├── developability_must_pass.tsv
├── normal_tissue_fatal_risk.tsv
├── competition_feasibility.tsv
├── epitope_whitespace_triage.tsv
└── opposing_evidence.tsv
05_target_commit/
├── target_commit.json
└── target_commit_table.tsv
```

PR-A 自身在仓库内只提交合同和测试，不提交上述运行产物。

## 3. Source admission contract

### 3.1 `source_admission_bundle.json`

每个承重来源必须有 admission record，最低字段：

```yaml
source_id: adcdb
source_name: ADCdb
source_type: derived_database
source_version: <required, not current_at_download only>
source_locator: <stable external locator>
retrieved_at_utc: <timestamp>
snapshot_id: <immutable snapshot id>
license_access_note: <required>
read_only_boundary: true
field_whitelist_ref: <required>
identity_policy_ref: <required>
admission_basis_refs: [<source evidence refs>]
admission_status: PENDING | APPROVED | BLOCKED
human_review_ref: <required when APPROVED>
```

`APPROVED` 的必要条件是：版本可核验、快照可定位、license/access 可追溯、字段白名单和 identity policy 已冻结、人工审核引用存在。自述版本号或单独 checksum 不能替代 admission record。

### 3.2 `source_snapshot_manifest.json`

```yaml
snapshot_id: <immutable id>
source_id: adcdb
source_version: <release or commit>
cutoff_utc: <timestamp>
files:
  - relative_path: <path outside repository>
    size_bytes: <integer>
    sha256: <64 hex chars>
manifest_sha256: <sha256 of canonical manifest>
normalization_status: NOT_STARTED | VERIFIED | FAILED
checksum_status: NOT_CHECKED | PASS | FAIL
```

任一文件 checksum 不匹配、文件清单不完整或 source version 无法核验时，整个运行是 `SOURCE_ADMISSION_BLOCK`，不能用剩余文件继续。

## 4. `TargetSeed` schema

### 4.1 核心定义

```text
Patient Territory × Intended Benefit / Endpoint Class
× ADC Target × ADC Precedent × Initial Development Hypothesis
```

以下字段在 Stage 1 合法且必须显式写出：

```yaml
endpoint_driving_population: UNRESOLVED
population_causality: UNRESOLVED
```

它们只有在 Atlas G2/G3 通过后才能 materialize 为 audited fields。

### 4.2 `target_seed_candidates.tsv` 最低列

```text
seed_id
territory_ref
disease
biomarker_state
refractory_definition_ref
intended_benefit
endpoint_class
canonical_target_id
canonical_target_name
target_aliases
extracellular_access_status
adc_construct_precedent_status
internalization_delivery_precedent_status
clinical_precedent_status
initial_development_hypothesis
endpoint_driving_population
population_causality
adcdb_record_refs
antibody_record_refs
delivery_record_refs
source_snapshot_refs
identity_resolution_status
unknown_class
supporting_evidence_refs
opposing_evidence_refs
created_at
pipeline_version
artifact_schema_version
review_status
```

### 4.3 Active seed 条件

`ACTIVE_SEED` 必须同时满足：target identity 已解析且无 collision；有 extracellular antibody-accessible 先例；有真实 ADC construct precedent；有 internalization/delivery precedent；每项 precedent 有 source record ref；population 和 causality 仍明确为 `UNRESOLVED`。

缺任一项可以留在 audit universe，但必须是 `DEFERRED_SEED`，不得进入 Atlas active screen。

## 5. Atlas G1–G4 operational definition

### 5.1 共同统计单位

- `patient-level unit` 是患者；同一患者多个样本先在 patient ID 内聚合。
- `malignant-cell unit` 是预先冻结的 malignant-cell annotation。
- `independent_cohort` 是不同 study/cohort accession；同一数据集的不同 batch 不算独立 cohort。
- RNA 是 proxy；protein/surface 结果必须单独列出。

统一的 `PR-A-PATIENT-AGGREGATION-v0.1.0` 规定：有效样本必须同时有 `patient_id`、预先冻结的 malignant-cell annotation 和 assay-native target measurement；同一患者的所有有效样本先合并 malignant cells，不做 sample weighting；分子是 target-positive malignant cells，分母是该患者全部有效 malignant cells。患者只有在 `target-positive malignant cells / all valid malignant cells >= 10%` 时才算 `patient_positive`。缺失 patient ID 或恶性细胞分母不可计算直接为 `UNKNOWN`，不能用样本数替代患者数。

### 5.2 G1：expression / prevalence

默认 `target_positive_cell` 是 assay-native normalized expression 高于预先声明 detection threshold 且 malignant-cell annotation 有效的细胞。运行 manifest 必须锁定 threshold。G1 的 patient prevalence 必须引用统一的 `PR-A-PATIENT-AGGREGATION-v0.1.0` patient-positive definition。

| 状态 | 默认 operational criterion |
|---|---|
| `PASS` | 至少 2 个独立、与 refractory mCRC 相容 cohort；patient prevalence >=20%，每 cohort malignant-cell detection >=10% |
| `KILL` | 至少 2 个独立 cohort 均显示 patient prevalence <5%，且 malignant-cell detection <5% |
| `UNKNOWN` | 只有 1 cohort、patient unit 缺失、cohort 冲突或 assay threshold 无法核对 |

`PASS` 只表示进入下一项，不表示 surface density PASS。`RNA clearly absent/low` 必须绑定 `g1_policy_ref` 和实际计数。

### 5.3 G2：endpoint-driving population mapping

mapping 必须在运行前声明 population classifier、marker/state definition 和 target-positive 分组方法。默认且唯一的 mapping effect 是同一 cohort 内 population-state prevalence ratio：`prevalence(state | target_positive) / max(prevalence(state | target_negative), 0.01)`；PASS 要求该 ratio `>=2.0`、方向在至少 2 个独立 cohort 一致。classifier、分组方法、denominator floor 和 effect metric 必须在运行前冻结，不能在 PR-B 边跑边选。

| 状态 | 默认 operational criterion |
|---|---|
| `PASS` | 至少 2 个独立 cohort；同一 predeclared classifier 稳定映射到一个 population/state；方向一致，默认 population-state prevalence ratio >=2.0 |
| `KILL` | 至少 2 个独立 cohort 稳定落入与 intended benefit 无关或明确相反的 malignant population，且一次补证不能解决 |
| `UNKNOWN` | 只有 association、classifier 未冻结、只有 1 cohort、effect 不稳定或 population identity 冲突 |

### 5.4 G3：endpoint population causality

证据层级：`Tier A` 为 longitudinal/recurrence、perturbation/dependency、lineage 或直接功能干预；`Tier B` 为 treatment enrichment、空间进展、转移/复发富集或多 cohort 重复；`Tier C` 为横断面相关或单队列表达关联。

| 状态 | 默认 operational criterion |
|---|---|
| `PASS` | 至少 1 条 Tier A，或至少 2 个独立且方向一致的 Tier B，并直接连接 intended benefit |
| `KILL` | 反向 Tier A/B，或一次针对性补证后仍只有不能连接 intended benefit 的 Tier C |
| `UNKNOWN` | 只有 Tier C、Tier A/B 冲突、population 因果单位不清或补证尚未完成 |

G3 评估 population causality，不要求 target gene/protein 本身 causal。

### 5.5 G4：patient and malignant-burden coverage

`patient_positive` 以 patient ID 聚合：同一患者所有有效样本的 malignant cells pooled；分子是 target-positive malignant cells，分母是全部有效 malignant cells；比例达到 `>=10%` 才算阳性。没有 sample weighting，也不能把样本数当患者数。这个定义同时用于 G1 patient prevalence 和 G4 coverage。

| 状态 | 默认 operational criterion |
|---|---|
| `PASS` | 至少 2 个独立 cohort；patient_positive prevalence >=20%，且 target-positive malignant-cell burden 的 cohort-level median >=10% |
| `KILL` | 至少 2 个独立 cohort 的 patient_positive prevalence <10%，且 burden median <5% |
| `UNKNOWN` | patient ID 缺失、malignant denominator 不可核对、只有 1 cohort 或方向冲突 |

默认阈值是第一版 policy floor，不是生物学真理；修改必须先提交 PR-A amendment，不能在 PR-B 运行时临时改变。

## 6. G5–G7 operational criteria

PR-A 只冻结 developability 的分类，不在这里运行专利或安全数据。

| Gate | `PASS` | `KILL` / route block | `UNKNOWN` |
|---|---|---|---|
| G5 normal-tissue fatal risk | 没有 fatal normal-surface、essential-organ 或 target-mediated ADC toxicity blocker | 高正常 surface + essential-organ concern，或已知 toxicity 与下一成本不相容 | 只有 RNA/非 surface 组织证据，或证据冲突 |
| G6 competition feasibility | 有可审计 CRC whitespace、epitope differentiation 或可行 partner route | crowded target + crowded CRC + late-stage occupancy + 无可执行 differentiation，路由 `OUT_OF_MANDATE` | crowding/IP/platform 证据不足，路由 `WATCHLIST`/`PARTNER_ONLY` |
| G7 epitope whitespace | 至少一个 extracellular accessible patch，且没有明显全覆盖 claim blocker | 所有可及 patch 均 `EPITOPE_BLOCKED`，或结构明确不可达 | structure/topology/claim map 不足，进入一次性补证 |

G6 的高拥挤不是科学 KILL；G7 的 UNKNOWN 不能无限循环。G5–G7 结果必须保留 supporting、opposing、conflicting 和 unknown refs。

## 7. `TargetCommit` schema

PR-C 必须把 Atlas survivors 的 G1–G4 和 developability G5–G7 汇总为唯一主干决定：

```yaml
target_commit_schema: TargetCommit@0.1.0
territory_ref: <required>
candidate_input_refs: [<required>]
primary_target: <exactly one unless no_go=true>
backup_target: <zero or one>
no_go: <boolean>
g1_g7_results_ref: <required>
lexicographic_selection_trace:
  - adc_precedent_strength
  - patient_coverage
  - endpoint_population_evidence
  - normal_tissue_margin
  - crc_competitive_whitespace
  - epitope_whitespace
  - antibody_aidd_execution_ease
hard_gate_results: <required>
endpoint_driving_population: <audited Atlas field>
population_causality: <audited Atlas field>
development_hypothesis: <required>
primary_unresolved_product_risk: new_epitope_internalization_and_construct_specific_window
residual_risks: <required, may be non-empty>
next_cost_step: AIDD | NONE
human_decision_ref: <required>
review_status: PENDING | APPROVED | BLOCKED
```

不变量：`no_go=false` 时必须恰好一个 primary、最多一个 backup；`no_go=true` 时 primary/backup 必须为空；不能以多个并列 primary 绕过决策。

## 8. 结果状态与 PR-A 放行条件

每条 G1–G7 记录必须有：`status`、`policy_ref`、`score_or_measurement`（适用时）、`supporting_refs`、`opposing_refs`、`conflicting_refs`、`unknown_class`、`missing_information`、`recommended_next_action`。

缺 source/checksum/identity 的结果是 `SOURCE_ADMISSION_BLOCK` 或 `IDENTITY_RESOLUTION_BLOCK`，不是 KILL。工具失败是 `PIPELINE_ERROR`，不是科学失败。没有证据是 `EVIDENCE_INSUFFICIENT`，不是 opposing evidence。

PR-A 必须满足：source/snapshot/checksum/identity/字段白名单有机器可读字段；TargetSeed 不依赖 Atlas 结论；G1–G7 有统计单位、默认阈值、PASS/KILL/UNKNOWN 规则和 policy version；G4 以 patient ID 聚合；TargetCommit 只能输出一个 primary、最多一个 backup 或 NO_GO；运行结果全部在外部 DATA；不修改 v0.3、不执行 ADCdb/Atlas/Gate/AIDD。

## 9. 期待的下一步输出

PR-A 获批后，PR-B 才会锁定并验证 ADCdb snapshot，生成真实 `target_seed_candidates.tsv`，计算 G1–G4，并提交 Atlas survivor 数量和失败原因分布。PR-B 不执行 G5–G7，也不生成 TargetCommit。
