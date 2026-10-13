# Cancer Vaccine Indication–Neoantigen Portfolio Design Pipeline

- 文档版本：`Cancer_Vaccine_Indication_Neoantigen_Portfolio_Design@0.1.0-draft`
- 状态：`DESIGN_REVIEW_REQUIRED_EXECUTION_NOT_AUTHORIZED`
- 搜索范围：`pan-cancer patient territories`；CRC 仅作首个 calibration case
- 策略：Small Biotech、territory-first、truth-set-first、公开工具复用、实验反馈优先、平台合作优先
- 固定审核上下文：ChatGPT `Biotech ideas / moderna癌症疫苗三期`

本文件与 `ADCdb_Atlas_ADC_AIDD_design.md` 同级，但二者科学 authority 独立。ADC pipeline 选择 ADC patient territory 与 target；本 pipeline 选择对 vaccination 存在可干预因果脆弱性的 patient territory，并在 territory commit 后验证 patient-specific antigen portfolio selection。不得把 ADC 的 target、Gate、precedent 或 status 直接映射成 vaccine 结论。

## 1. 目标、非目标与 100% 定义

本 pipeline 回答两个连续但不可混淆的问题：

1. **Indication discovery**：哪个 `disease × setting × biomarker × burden/MRD × prior treatment × metastatic site × intended benefit` territory 的主要免疫失败，确实可被 vaccination 推过有效免疫阈值？
2. **Portfolio technology validation**：在已承诺 territory 中，能否比公开 baseline 更可靠地选择产生功能性、持久、肿瘤相关 T-cell response 的 antigen portfolio？

100% 终点是一次版本化、可复现、可审计的外部运行，从 pan-cancer territory universe 收敛到一个 human-approved `PRIMARY_VACCINE_TERRITORY`，建立合格 human truth set，完成盲法 shadow trial、prospective presentation/T-cell/tumor-recognition 验证与固定 delivery platform 的 portfolio POC，并形成 `VACCINE_PORTFOLIO_HIT` 的 `GO`、`ITERATE` 或 `STOP` 决策包。

该终点**不等于** Development Candidate、GMP product、IND-ready、临床候选物、临床疗效、预防获批或 Moderna/V940 end-to-end parity。

```text
TerritoryUniverse
  -> VaccineMechanismProfile
  -> VaccineTerritoryCommit
  -> ClinicalNeoantigenTruthSet
  -> BlindedShadowTrial
  -> ProspectiveImmuneValidation
  -> FixedPlatformPortfolioPOC
  -> VaccinePortfolioHitDecision
```

本设计不以重新实现 WES/RNA pipeline、HLA binder predictor、mRNA chemistry、LNP、batch-of-one CMC 或临床运营为起点。可复用的公开能力先作为 pinned baseline；有限资源集中在 territory causal fit、human response labels、portfolio optimization 和高信息量实验反馈。

## 2. 唯一 critical path

```text
0 GOVERNANCE + UNIVERSE LOCK
  -> 1 TERRITORY ENUMERATION
  -> 2 VACCINE-MECHANISM MUST-PASS
  -> 3 CLINICAL + EXECUTION MUST-PASS
  -> 4 VACCINE_TERRITORY_COMMIT
  =============== indication selection done ===============
  -> 5 TRUTH-SET ADMISSION + LEAKAGE FIREWALL
  -> 6 BLINDED SHADOW TRIAL
  -> 7 PROSPECTIVE IMMUNE VALIDATION
  -> 8 FIXED-PLATFORM PORTFOLIO POC
  -> 9 VACCINE_PORTFOLIO_HIT DECISION
```

Stage 4 是“找到适应症”的完成边界；Stage 5–9 是 selection technology 的独立验证链。任何 downstream 成功不得倒推未通过的 territory 为合格，任何 territory commit 也不得被表述为 vaccine efficacy 或模型 superiority。

## 3. 全局边界

### 3.1 仓库与外部运行

StelligenOS 只保存设计、合同、代码和小型审计材料。患者数据、测序、候选 peptide、免疫测定、模型训练材料、cache、数据库、权重和结果必须位于仓库外部。每次外部运行只有一个根：

```text
${BIOWORKSPACE_ROOT}/DATA/2.PROJECTS/Stelligen-CancerVaccine-OS/result/<pipeline_run_id>/
├── 00_governance/
├── 01_territory_universe/
├── 02_vaccine_mechanism/
├── 03_clinical_execution/
├── 04_territory_commit/
├── 05_truth_set/
├── 06_shadow_trial/
├── 07_prospective_validation/
├── 08_fixed_platform_poc/
├── 09_vaccine_hit_decision/
└── report/
```

### 3.2 Source admission 与 provenance

临床试验、publication/source data、dbGaP/EGA/GEO、IEDB、immunopeptidomics、HLA/APM、TCR、ctDNA、专利、竞争和公共算法来源，在消费前必须具备 admission record：

```text
source_id, source_version_or_cutoff, access_date, checksum,
licence_and_access_note, allowed_fields, identity_policy,
patient_privacy_class, extraction_method, exclusion_reason, review_status
```

每个运行 artifact 必须携带：

```text
pipeline_run_id, pipeline_version, stage_id, artifact_schema_version,
record_id, source_snapshot_refs, source_record_refs, code_commit,
software_or_model_versions, config_checksum, artifact_checksum,
created_at, created_by, evidence_refs, review_status
```

受限访问不等于可自由再分发；公开论文不等于 underlying patient-level data 可用；聊天中的 URL 与总结只可作为 discovery lead，不是 source admission 或 scientific evidence。

### 3.3 Claim boundary

- predicted HLA binding 不等于 processing、presentation 或 immunogenicity；
- peptide-loaded APC response 不等于 endogenous tumor-cell recognition；
- after-expansion response 不等于 direct-ex-vivo response；
- peripheral expansion 不等于 tumor infiltration、killing、durability 或 clinical benefit；
- vaccine-selected 但未测定的 epitope 是 `NOT_MEASURED`，不是 negative；
- 未被 vaccine 选择的 candidate 通常没有 response label，不能静默编码为 non-immunogenic；
- ctDNA clearance、RFS、ORR、PFS 和 OS 是不同终点，不能互换；
- single-arm、小样本或机制性研究可支持 feasibility/mechanism claim，不能建立 comparative efficacy；
- CRC calibration hypothesis 不等于 pan-cancer ranking result。

### 3.4 Pipeline-local check，不新增全局 Gate

本文件的 `VAX-*` 是本 pipeline 的 must-pass check，不是 StelligenOS frozen Gate、RuleBook disposition 或 lifecycle state。它们不得修改已有 `OpportunityTerritory`、`SearchSpaceAdmission`、`SponsorFitAssessment` 或 `ProgramCommitmentReview` 的 authority。

### 3.5 Unknown taxonomy

每个 unknown 必须落入恰好一类：

- `PRECOMMIT_BLOCKER`：没有该信息就不能作 Stage 4 territory commit，例如 intended population 的 antigen opportunity 或 HLA/APM competence 是否存在；
- `ONE_SHOT_UNKNOWN`：允许一次预先定义的补证任务；仍 unresolved 则退出 active territory funnel；
- `DEFERRED_PRODUCT_RISK`：territory commit 后才可经济地验证，例如具体 concatemer junction、平台 innate sensing 或 portfolio-specific immunodominance。

每条 unknown 必须记录 `affected_decision`、`resolution_task`、`owner`、`deadline_or_stage`、`stop_if_unresolved` 和 `evidence_refs`。Unknown 不是正证据，也不得用零分参与补偿性总分。

## 4. Stage 0 — GOVERNANCE + UNIVERSE LOCK

锁定以下运行条件：

- pan-cancer 搜索边界与 evidence cutoff；
- vaccine 类型范围：personalized neoantigen、shared driver/shared antigen、preventive 等是否纳入；
- disease setting、burden/MRD、prior treatment、metastatic site 与 combination context 的允许词汇；
- intended benefit 与 endpoint class；
- source admission、identity、patient privacy 与 licence policy；
- Small-Biotech capital/capability boundary；
- Stage 1–4 的固定 policy 与人工 review owner。

输出：

- `vaccine_search_scope.yaml`
- `source_admission_policy.yaml`
- `territory_evaluation_policy.yaml`
- `review_and_cost_gate_policy.yaml`

人群边界不清、comparators 不清、vaccine role 混合、endpoint class 不可审计或来源未准入时，输出 `UNIVERSE_LOCK_BLOCK`，不得开始枚举。

## 5. Stage 1 — TERRITORY ENUMERATION

Stage 1 只枚举临床 territory，不选 peptide、不训练模型、不生成 mRNA。

### 5.1 VaccineTerritorySeed minimum contract

```text
disease
× disease setting / line / prior therapy
× molecular or etiologic subgroup
× tumor burden / MRD state
× metastatic site or prevention context
× vaccine role
× antigen strategy hypothesis
× intended benefit / endpoint class
× comparator / combination context
```

`vaccine role` 至少区分：

- `PREVENTIVE`
- `ADJUVANT_OR_MRD`
- `POST_RESECTION_HIGH_RISK`
- `METASTATIC_COMBINATION`
- `THERAPEUTIC_MONOTHERAPY_HYPOTHESIS`

`antigen strategy hypothesis` 只描述 personalized neoantigen、shared driver、shared tumor antigen 或其他 route 的初始假设，不证明任何 antigen 可用。

输出：`vaccine_territory_universe.tsv`、`territory_identity_map.tsv`、`territory_source_manifest.json`。每个 seed 记录正反证、缺失字段、来源和 unknown class。Stage 1 不使用综合分数，也不输出 primary/backup。

### 5.2 CRC calibration，不是预设赢家

首轮 policy calibration 应保留至少四个 CRC territory hypothesis：

1. resected ctDNA-positive MSS CRC / MRD；
2. Lynch 或 premalignant MSI-prone prevention；
3. resected oligometastatic CRC / CRLM NED；
4. bulky refractory MSS mCRC combination setting。

这些只是 calibration candidates。前三者不得因聊天判断自动 PASS，第四者也不得因困难自动全局 KILL。

## 6. Stage 2 — VACCINE-MECHANISM MUST-PASS

Stage 2 判断 failure state 是否存在可被 vaccination 直接改变的承重环节。

| Check | 必答问题 | Active funnel 退出条件 |
|---|---|---|
| `VAX-M1 antigen opportunity` | intended population 是否存在可表达、可加工、可覆盖的 antigen opportunity | 可靠证据显示 antigen opportunity 不足 |
| `VAX-M2 clonality/coverage` | truncal/clonal 或 portfolio coverage 是否足以限制 escape | coverage 明显不足且无可行 portfolio route |
| `VAX-M3 HLA/APM competence` | HLA、B2M、processing/presentation 在 intended population 是否保留 | intended population 中不可解决的呈递缺陷占主导 |
| `VAX-M4 priming vulnerability` | 主要缺陷是否包含 tumor-reactive repertoire/priming 不足 | 主要失败完全位于 vaccination 下游且无可行组合路线 |
| `VAX-M5 trafficking/exclusion` | induced T cells 能否进入目标组织 | exclusion 风险不可管理且无 evidence-backed modifier hypothesis |
| `VAX-M6 suppression/escape` | exhaustion、TGFβ/VEGF、髓系、Treg、liver tolerance、antigen/HLA escape 是否可管理 | 多重 suppressive/escape burden 使 intended benefit 不可信 |

输出：

- `vaccine_mechanism_profiles.tsv`
- `antigen_opportunity_evidence.tsv`
- `hla_apm_integrity_evidence.tsv`
- `immune_failure_state_map.tsv`
- `mechanism_must_pass_decisions.json`

每个 territory 必须给出 `dominant_failure_state`、`vaccine_addressable_link`、`required_combination`、`counterfactual_failure_if_vaccine_works` 和 evidence refs。若 vaccine 只能制造 T cells、但下游 trafficking/suppression 仍足以解释必然失败，则不得用“cold-to-hot”自然语言放行。

## 7. Stage 3 — CLINICAL + EXECUTION MUST-PASS

本阶段只消费 Stage 2 survivors，评估能否以有限成本建立可读、可验证、可合作的 program。

| Check | 必答问题 |
|---|---|
| `VAX-C1 burden/window` | tumor burden、MRD/prevention window 与 turnaround time 是否匹配 vaccine kinetics |
| `VAX-C2 patient identification` | biomarker、组织、血液、ctDNA、HLA 与 longitudinal sample 是否可获得 |
| `VAX-C3 endpoint observability` | immune、molecular 与 clinical endpoint 是否有预先定义的层级与时间窗 |
| `VAX-C4 truth-label availability` | 是否存在可用于独立 retrospective benchmark 的 human response cohorts |
| `VAX-C5 competition/differentiation` | 当前 trial/asset occupancy 是否仍允许 preclinical 可见差异 |
| `VAX-C6 platform/partnerability` | 标准化 vaccine platform、assay、CRO、CMC/clinical partner 是否可获得 |
| `VAX-C7 ethics/regulatory` | prevention、germline-risk、tissue use 和 patient privacy 是否有可行边界 |

高竞争不是 scientific KILL；能力缺口不否定 territory。Sponsor fit、partner route 与资本边界作为 metadata，不能补偿 `VAX-M1`–`VAX-M4` 的科学失败。

输出：`clinical_execution_must_pass.tsv`、`specimen_and_biomarker_feasibility.tsv`、`truth_label_availability.tsv`、`competition_and_partnerability.tsv`、`opposing_evidence.tsv`。

## 8. Stage 4 — VACCINE_TERRITORY_COMMIT

Stage 4 的主干输出严格为：

```text
PRIMARY_VACCINE_TERRITORY
BACKUP_VACCINE_TERRITORY (最多一个)
NO_GO
```

不得用 `ACTIVE_SEARCH`、`WATCHLIST`、`PARTNER_ONLY`、model rank 或 narrative recommendation 替代上述 commit。

所有 hard fail 先退出 active funnel。剩余 territory 不训练黑盒综合分数，按固定 lexicographic priority 决策：

1. vaccine-addressable causal link；
2. antigen opportunity、clonality 与 patient coverage；
3. HLA/APM competence；
4. burden/window 与 endpoint observability；
5. patient/specimen 与 human truth-label availability；
6. trafficking/suppression/escape manageability；
7. clinical differentiation；
8. Small-Biotech execution与 partnerability。

输出 `vaccine_territory_commit.json` 与 `vaccine_territory_commit_table.tsv`，至少包含：

```yaml
primary_vaccine_territory: ...
backup_vaccine_territory: ...
no_go: false
vaccine_role: ...
antigen_strategy_hypothesis: ...
intended_benefit: ...
endpoint_class: ...
dominant_failure_state: ...
vaccine_addressable_link: ...
required_combination: ...
hard_check_results: ...
selection_order: ...
precommit_unknowns: ...
deferred_product_risks: ...
first_value_inflection: ...
human_decision_ref: ...
review_status: ...
```

放行要求：恰好一个 primary、最多一个 backup，或显式 `NO_GO`；所有承重输入可追溯；没有 unresolved `PRECOMMIT_BLOCKER`；下一笔成本和 stop rule 明确；人类与 ChatGPT 审核记录齐全。

## 9. Stage 5 — TRUTH-SET ADMISSION + LEAKAGE FIREWALL

目标不是先训练模型，而是建立 `patient × candidate antigen × vaccine × immune response × tumor recognition × clinical outcome` 的可审计 truth set。

### 9.1 TruthSetCohortRecord

每个 cohort 至少记录：

```text
trial/cohort/patient IDs, cancer and setting, vaccine platform,
pre-vaccination tumor/normal DNA, tumor RNA, HLA and clonality refs,
candidate universe ref, published selection ref, administered portfolio,
assay type/timepoint, direct-ex-vivo versus expanded response,
CD4/CD8, magnitude, persistence, TCR expansion, tumor infiltration,
tumor-cell recognition/killing, ctDNA, recurrence and clinical outcome,
NOT_MEASURED/NEGATIVE/POSITIVE/INDETERMINATE status,
source/access/licence/privacy refs
```

一个 cohort 只有 selected peptides、没有可重建 candidate universe 时，可进入 `LABEL_ONLY` 层，但不得声称支持 universe-level top-k recall。只有 post-vaccination assay、缺失 pre-vaccination inputs 时，不得进入 blinded shadow trial。

### 9.2 Leakage firewall

- split 单位至少为 patient，并优先按 trial/cohort family 隔离；
- 同一 patient、sample、derived peptide、replicate 或 longitudinal aliquot 不得跨 split；
- post-vaccination immune、TCR、ctDNA、clinical outcome 和 published responder status 在 scoring freeze 前保持 masked；
- feature engineering 只能消费预先批准的 pre-vaccination fields；
- imputation、normalization、threshold 与 feature selection 在 holdout unblind 前冻结；
- public selector 的已发表选择结果可以作为 comparator，不得作为待评模型的隐藏输入；
- missing label 与 negative label 分开；selection-biased assay 不能伪装成全 universe negative set；
- cohort exclusion、failed assay、missing file 与 identity ambiguity 必须显式记录。

输出：`truth_set_registry.tsv`、`truth_set_data_dictionary.yaml`、`label_hierarchy.yaml`、`split_manifest.json`、`leakage_audit.json`、`truth_set_admission_decision.json`。

## 10. Stage 6 — BLINDED SHADOW TRIAL

本 design 的 Stage 5–6 首版合同只授权 personalized/shared **neoantigen** route。若 Stage 4 commit 到 non-neoantigen、viral antigen 或其他 vaccine route，必须先创建并审核 route-specific truth-set/label contract；不得把 mutation/clonality/HLA 字段强塞给不适用的 route，也不得绕过 Stage 5 admission。

Shadow trial 只允许查看 vaccination 前信息。运行前必须冻结并哈希：

- candidate universe 与 eligibility policy；
- public baseline 名称、版本、参数和容器/环境；
- 待评 ranking/portfolio policy；
- cohort split、label mask 与 unblind owner；
- primary/secondary metrics、missing-label handling 与 failure threshold；
- compute budget 与 stop rule。

### 10.1 评价层级

不能用一个指标混合所有 truth：

1. **candidate level**：在实际 assayed candidates 中的 response enrichment、rank/AUC 类指标；
2. **portfolio level**：top-5/10/20/34 recall、HLA-I/II coverage、truncal/subclone coverage、driver/essential clone coverage、WT dissimilarity、redundancy；
3. **patient level**：是否产生任何 direct-ex-vivo functional response、breadth、magnitude、persistence；
4. **tumor relevance**：tumor infiltration 与 endogenous tumor recognition/killing；
5. **clinical exploratory**：ctDNA、recurrence、RFS 等只作分层探索，不从小样本建立 efficacy claim。

若非 selected candidates 没有被 assayed，primary analysis 必须明确 selection bias；不得把未测 candidates 当 negative 计算虚假 specificity。

### 10.2 放行门

Pipeline-local evidence checkpoint `VAX-P1_RETROSPECTIVE_COMPUTATIONAL_SUPERIORITY` 至少要求：

- 在预注册的独立 holdout cohort families 中相对 pinned public baselines 有一致、可解释的 improvement；
- improvement 不由一个 trial、共享 patient、label leakage 或 post-vaccine feature 驱动；
- sensitivity analysis、negative controls、ablation 和 uncertainty 已报告；
- 失败 cohort 与 opposing evidence 不被删除；
- reviewer 能从 frozen artifacts 重跑主要比较。

具体数值阈值必须由后续 contract PR 在看见 holdout label 前冻结，本 design 不用事后阈值授权成功。

输出：`shadow_trial_preregistration.yaml`、`frozen_rankings/`、`baseline_comparison.tsv`、`portfolio_coverage.tsv`、`unblinding_record.json`、`shadow_trial_report.md`、`retrospective_gate_decision.json`。

## 11. Stage 7 — PROSPECTIVE IMMUNE VALIDATION

只有 Stage 6 获批且存在独立 human cost authorization 才进入。按信息价值逐层停止：

| 子阶段 | 关键问题 | 不可替代的 readout |
|---|---|---|
| 7A presentation | candidate 是否真实产生并被相应 HLA 呈递 | immunopeptidomics / orthogonal presentation evidence |
| 7B immune priming | human PBMC/T-cell 是否产生特异功能反应 | direct ex vivo 或预定义 expansion 后 ELISpot/ICS/tetramer/TCR |
| 7C tumor recognition | T cells 是否识别 endogenous antigen 的 tumor cell | matched tumor-cell recognition/killing 与 blocking controls |
| 7D breadth/durability | portfolio 是否形成广度、持续性与 HLA/clone diversification | longitudinal functional/TCR readout |

peptide-loaded APC 的阳性不能单独通过 7C。Presentation fail、assay fail、PBMC quality fail 和 biological non-response 必须分开。输出 `prospective_validation_plan.yaml`、`presentation_validation.tsv`、`t_cell_response.tsv`、`tumor_recognition.tsv`、`durability_and_breadth.tsv`、`prospective_gate_decision.json`。

Pipeline-local evidence checkpoint `VAX-P2_PROSPECTIVE_IMMUNOLOGICAL_SUPERIORITY` 不是 clinical efficacy。

## 12. Stage 8 — FIXED-PLATFORM PORTFOLIO POC

本阶段固定 delivery/platform、剂量和 assay，只比较 antigen portfolio selection；不得同时更换 ranking、RNA chemistry、LNP、dose 与 schedule 后把差异归因给 selection engine。

需要记录：

- antigen count、ordering、junction/flank、MHC-I/II balance；
- codon/translation、RNA structure、UTR/cap/poly(A)/nucleoside policy；
- platform/LNP 或替代 delivery 的 partner与 batch refs；
- identity、purity、integrity、encapsulation、particle、potency 与 release QC；
- innate sensing、APC uptake、antigen expression 和 cross-presentation；
- matched public/published-selection control portfolio。

输出：`fixed_platform_protocol.yaml`、`portfolio_construct_specs.yaml`、`manufactured_lot_manifest.json`、`release_qc.tsv`、`matched_portfolio_comparison.tsv`、`fixed_platform_poc_decision.json`。

预测 sequence、已下单材料或 release-QC 合格但无 functional comparison 的 lot 都不是 vaccine portfolio hit。

## 13. Stage 9 — VACCINE_PORTFOLIO_HIT DECISION

`VACCINE_PORTFOLIO_HIT` 只允许在以下证据链闭合后使用：

```text
approved VaccineTerritoryCommit
AND admitted human truth set
AND blinded shadow-trial gate PASS
AND prospective presentation/T-cell/tumor-recognition evidence
AND fixed-platform matched portfolio POC
AND human review
```

输出 `vaccine_portfolio_hit_decision_package/`，最终 disposition 为 `GO`、`ITERATE` 或 `STOP`。必须说明：

- 哪个 territory 与 patient-selection hypothesis 被验证到何种层级；
- selection engine 相对哪些 baseline、在哪些 cohort/assay 上改善；
- 哪些链路仍只有 proxy；
- platform、CMC、clinical、regulatory 与 partner 风险；
- 下一次 value inflection、成本、stop condition 和 decision owner。

## 14. 最小 I/O contract

| From | To | 唯一允许的承重输入 |
|---|---|---|
| Stage 0 | Stage 1 | approved scope/source/policy refs |
| Stage 1 | Stage 2 | auditable `VaccineTerritorySeed`，不含预填 mechanism PASS |
| Stage 2 | Stage 3 | vaccine-mechanism survivors + opposing/conflicting/unknown refs |
| Stage 3 | Stage 4 | clinical/execution survivors + route metadata |
| Stage 4 | Stage 5 | approved `VaccineTerritoryCommit` + truth-set build authorization |
| Stage 5 | Stage 6 | admitted, masked truth-set refs + leakage audit + frozen benchmark plan |
| Stage 6 | Stage 7 | approved retrospective gate + prospective experiment authorization |
| Stage 7 | Stage 8 | prospective immune evidence + fixed-platform authorization |
| Stage 8 | Stage 9 | physical lot/release QC + matched functional POC evidence |
| Stage 9 | final | human-reviewed `GO/ITERATE/STOP` package |

任何 Stage 不得通过复制下游字段、预填 PASS、把未测量当 negative、把 post-vaccine feature 放入 prediction 或用自然语言暗示绕过上游审核。

## 15. Failure、blocker 与 error taxonomy

至少区分：

- governance/source：`SOURCE_ADMISSION_BLOCK`、`PRIVACY_OR_LICENCE_BLOCK`、`IDENTITY_RESOLUTION_BLOCK`、`UNIVERSE_LOCK_BLOCK`；
- territory science：`ANTIGEN_OPPORTUNITY_FAIL`、`CLONAL_COVERAGE_FAIL`、`HLA_APM_FAIL`、`VACCINE_CAUSAL_MISMATCH`、`TRAFFICKING_BLOCK`、`SUPPRESSION_ESCAPE_BLOCK`；
- clinical/execution：`PATIENT_IDENTIFICATION_BLOCK`、`ENDPOINT_OBSERVABILITY_BLOCK`、`TRUTH_LABEL_AVAILABILITY_BLOCK`、`PLATFORM_ACCESS_BLOCK`、`ETHICS_REGULATORY_BLOCK`；
- truth set/benchmark：`CANDIDATE_UNIVERSE_MISSING`、`LABEL_NOT_MEASURED`、`LEAKAGE_AUDIT_FAIL`、`BASELINE_REPRODUCIBILITY_FAIL`、`SHADOW_TRIAL_FAIL`；
- experiment/platform：`PRESENTATION_FAIL`、`T_CELL_RESPONSE_FAIL`、`TUMOR_RECOGNITION_FAIL`、`DURABILITY_FAIL`、`LOT_RELEASE_FAIL`、`FIXED_PLATFORM_POC_FAIL`；
- process：`EVIDENCE_INSUFFICIENT`、`ASSAY_ERROR`、`PIPELINE_ERROR`。

每条必须记录 `failure_class`、`failed_stage`、`affected_claims`、`evidence_refs`、`recoverable`、`unknown_class`（适用时）和 `recommended_next_action`。`BLOCK` 不等于 scientific KILL；`ASSAY_ERROR`/`PIPELINE_ERROR` 不得转成 biological non-response；`EVIDENCE_INSUFFICIENT` 不得转 PASS。

## 16. 人工成本跃迁与 PR 放行

| 成本跃迁 | 必需 artifact | 未获批时 |
|---|---|---|
| Stage 4 -> 5 truth-set build | `vaccine_territory_commit` + `truth_set_build_authorization.json` | 不收集/抽取 patient-level truth data |
| Stage 5 -> 6 benchmark compute | `truth_set_admission_decision` + `shadow_trial_execution_authorization.json` | 不解封 scoring inputs |
| Stage 6 -> 7 prospective assays | `retrospective_gate_decision` + `prospective_validation_authorization.json` | 不采购、不运行 PBMC/immunopeptidomics |
| Stage 7 -> 8 platform POC | `prospective_gate_decision` + `fixed_platform_poc_authorization.json` | 不设计/制造 mRNA/LNP lot |
| Stage 8 -> 9 hit decision | fixed-platform result review + human decision | 不称为 hit |

每个阶段遵循：

```text
design/contract PR -> ChatGPT APPROVE -> authorized external run
-> result PR -> ChatGPT APPROVE -> next cost decision
```

建议 PR 序列：

```text
PR-0  本 design/governance
PR-A  Stage 0-4 contracts + source policy + territory evaluation policy
PR-B  territory universe result record（不含 patient-level data）
PR-C  mechanism/clinical screens + VaccineTerritoryCommit result record
PR-D  truth-set admission + leakage firewall contract
PR-E  admitted registry/result record + shadow-trial preregistration
PR-F  shadow-trial result record
PR-G  prospective validation contract/result（按成本可再拆分）
PR-H  fixed-platform POC contract/result（按成本可再拆分）
```

所有 PR 复用 ChatGPT `Biotech ideas / moderna癌症疫苗三期` 对话。`APPROVE_WITH_NONBLOCKING_COMMENTS` 不等于进入下一成本阶段的授权。

## 17. 当前进度与不授权项

100% endpoint：从 pan-cancer territory universe 产生一个经人类批准、经 human truth set、盲法 shadow trial、prospective immune validation 和固定平台 POC 支持的 `VACCINE_PORTFOLIO_HIT` 决策包。

| Workstream | 权重 | 当前状态 | blocker | 下一里程碑 |
|---|---:|---|---|---|
| Design/governance | 10% | 8/10，Phase 0 draft | ChatGPT PR review pending | PR-0 APPROVE |
| Source admission + truth-set structure | 15% | 0/15 | sources/labels 未准入 | PR-A/PR-D contracts |
| Territory discovery + commit | 25% | 0/25 | pan-cancer universe 未运行 | PR-B/PR-C |
| Blinded shadow trial | 20% | 0/20 | truth set 与 preregistration 缺失 | PR-E/PR-F |
| Prospective immune validation | 20% | 0/20 | retrospective gate 未通过、实验资源未授权 | PR-G |
| Fixed-platform POC + hit decision | 10% | 0/10 | prospective gate/platform/CMC 未就绪 | PR-H/Stage 9 |

当前总体进度：`0% -> 8% (+8%)`。工程/设计治理 readiness 为 `8%`；scientific readiness、truth-set readiness、experimental/operational readiness 均为 `0%`。

本设计不授权：修改既有 contracts/Gates/lifecycle/core objects；下载、抽取或处理 patient data；建立 truth-set 实例；执行 pan-cancer ranking；运行 neoantigen predictor；训练/校准模型；解盲 outcome；设计 peptide/mRNA/LNP；采购、合成、制造、CRO、PBMC、immunopeptidomics、animal 或临床工作；生成 disease/vaccine recommendation；或把聊天内容升级为生物学/临床事实。
