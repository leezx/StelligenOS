# StelligenOS `gen_indication_endpoint_target` 开发总纲 v1.0

> 状态：架构冻结候选  
> 模块：`gen_indication_endpoint_target`  
> 所属生命周期：`Opportunity Generation`  
> 核心输出：`Opportunity` / `TargetOpportunityHypothesis`  
> Gate基线：`ADC Gate / Model / I/O Contracts v0.2`  
> Gate数量：固定为45个原生Gate；任何新增Gate必须走`Gate Extension`治理流程  
> 操作系统语言：中文  
> 核心代码、Schema、配置键、机器可读数据与科学报告正文：英文

---

# 0. 当前执行指令

你正在为StelligenOS开发核心机会生成模块：

`gen_indication_endpoint_target`

当前必须严格按Phase执行。每个Phase完成后必须停止，等待用户和架构审核者明确批准。未经批准不得进入下一Phase。

本总纲是本模块的最高执行规范。若仓库中的旧Prompt、README、实现计划或局部文档与本总纲冲突，以本总纲为准；但不得因此擅自修改既有45个Gate的合同、身份、版本或语义。

当前仅执行本总纲末尾指定的当前Phase。

---

# 1. 模块使命

本模块回答：

> 在已经锁定的临床未满足需求范围内，哪些`indication × patient population × clinical endpoint × ADC target`组合值得形成正式Opportunity，并进入StelligenOS的Target Opportunity Chain审核？

本模块不是：

- 无约束、全癌种、全靶点枚举器；
- 通用膜蛋白数据库；
- 单次大模型推荐器；
- ADC分子设计器；
- Binder生成器；
- 产品实现链；
- 商业尽调系统；
- 自动立项系统；
- 自动融资判断系统。

本模块必须以已有Gate合同为约束边界，在有限临床空间中逐步生成、收缩、补证、复核和排序候选。

---

# 2. 核心输出定义

本模块核心输出对象为：

`Opportunity`

其机器对象应与既有`TargetOpportunityHypothesis`保持兼容或建立明确适配层。

Opportunity的不可缺失临床身份为：

```text
indication
+ patient_population
+ clinical_endpoint
+ adc_target
```

同一target在以下任一上下文变化时，必须视为不同Opportunity：

- indication不同；
- patient population不同；
- disease setting不同；
- line of therapy不同；
- treatment context不同；
- comparator不同；
- endpoint不同；
- endpoint time horizon不同。

不得仅以`indication + target`作为唯一身份。

---

# 3. 固定Gate体系：不得临时发明新Gate

## 3.1 Gate权威来源

本模块只承认以下原生Gate体系：

- Gate Group T：Target Opportunity Chain；
- Gate Group P：ADC Product Realization Chain；
- Gate Group C：Commercial Executability Chain。

Gate身份、名称、版本、输入输出合同、依赖、Hard Gate属性和Model绑定，以仓库中的正式Gate合同与Registry为唯一事实来源。

不得在Prompt、代码、报告或配置中临时创造新的“Gate”。

以下内容不是Gate，除非已按`Gate Extension`流程正式注册：

- filter；
- heuristic；
- evidence requirement；
- ranking factor；
- review question；
- search constraint；
- source-quality policy；
- validation task；
- adversarial objection；
- precondition；
- data completeness check。

这些内容必须使用其真实类型命名，不得伪装为Gate。

---

## 3.2 固定45个原生Gate

### Gate Group T: Target Opportunity Chain

1. `T0 clinical_context_endpoint` — Clinical Context and Endpoint Lock  
2. `T1 endpoint_driving_population` — Endpoint-Driving Cell Population  
3. `T2 target_population_mapping` — Target-to-Population Mapping  
4. `T3 intervention_causality` — Intervention Causality  
5. `T4 baseline_coverage_and_escape` — Coverage, Residual Disease and Escape  
6. `T5 treatment_induced_state_response` — Treatment-Induced State Transition and Ecological Response  
7. `T6 net_endpoint_benefit` — Net Endpoint Benefit  
8. `T7 tumor_cell_surface_availability` — Tumor-Cell Surface Availability  
9. `T8 intratumoral_antigen_accessibility` — In-Tumor Antigen Accessibility  
10. `T9 antibody_dependent_internalization` — Antibody-Dependent Internalization Potential  
11. `T10 antibody_epitope_realizability` — Antibody and Epitope Realizability  
12. `T11 on_target_therapeutic_index` — On-Target Therapeutic Index  
13. `T12 target_opportunity_decision` — Target Opportunity Decision  

### Gate Group P: ADC Product Realization Chain

14. `P0 product_design_objective` — Product Design Objective Lock  
15. `P1 epitope_landscape` — Epitope Landscape Definition  
16. `P2 epitope_function` — Epitope Functional Behavior  
17. `P3 binding_geometry_kinetics` — Antibody Binding Geometry and Kinetics  
18. `P4 antibody_format_fc_design` — Antibody Format and Fc Design  
19. `P5 antibody_sequence_developability` — Antibody Sequence and Developability  
20. `P6 productive_internalization_trafficking` — Productive Internalization and Trafficking  
21. `P7 conjugation_platform_site` — Conjugation Platform and Site Selection  
22. `P8 dar_molecular_property_balance` — DAR and Molecular Property Balance  
23. `P9 payload_cell_state_match` — Payload Mechanism–Cell-State Match  
24. `P10 linker_release_match` — Linker Release Mechanism Match  
25. `P11 bystander_tumor_coverage` — Bystander and Tumor-Coverage Design  
26. `P12 integrated_pk_stability_exposure` — Integrated PK, Stability and Exposure  
27. `P13 construct_therapeutic_index` — Construct-Level Therapeutic Index  
28. `P14 biomarker_clinical_assay_codesign` — Biomarker and Clinical Assay Co-Design  
29. `P15 integrated_adc_product_decision` — Integrated ADC Product Decision  

### Gate Group C: Commercial Executability Chain

30. `C0 commercial_opportunity_threshold` — Commercial Opportunity Threshold  
31. `C1 regulatory_development_path` — Regulatory and Development Path Attractiveness  
32. `C2 competitive_position_entry_window` — Competitive Position and Entry Window  
33. `C3 product_claim_decomposition` — Product Claim Decomposition  
34. `C4 patent_landscape` — Patent Landscape  
35. `C5 preliminary_technical_fto` — Preliminary Technical FTO  
36. `C6 blocking_claim_severity` — Blocking Claim Severity  
37. `C7 design_around_opportunity` — Design-Around Opportunity  
38. `C8 access_strategy` — License, Acquire, Partner or Abandon  
39. `C9 fto_product_configuration` — FTO-Cleared Product Configuration  
40. `C10 own_ip_inventive_concept` — Own-IP Inventive Concept  
41. `C11 patentability_enablement` — Patentability and Enablement  
42. `C12 claim_architecture_patent_estate` — Claim Architecture and Patent Estate Design  
43. `C13 disclosure_filing_strategy` — Disclosure Timing and Filing Strategy  
44. `C14 lifecycle_exclusivity_strategy` — Regulatory–IP–Commercial Lifecycle Strategy  
45. `C15 transaction_readiness` — Transaction Readiness and Asset Saleability  

---

# 4. 本模块与45个Gate的责任边界

## 4.1 原生决策链：T0–T12

`gen_indication_endpoint_target`的原生Gate链只能是：

`T0 → T1 → T2–T11 → T12`

本模块的正式成功条件不是“排名第一”，而是生成少量满足以下条件的Opportunity：

- 已形成完整临床身份；
- 关键正向证据非空；
- 没有被高置信度Hard Gate明确淘汰；
- 关键未知已显式记录；
- T0–T11结果可审计；
- T12能够基于同一Candidate、同一版本上下文做出正式决策；
- 输出可交接给后续资产生成阶段。

不得创建“T13”“Target Quality Gate”“Evidence Gate”“Membrane Gate”等临时Gate。

如果需要额外检查，必须建模为：

- `SearchConstraint`；
- `EvidencePolicy`；
- `Filter`；
- `ReviewCheck`；
- `RankingFeature`；
- `ValidationTask`；
- 或正式`Gate Extension Proposal`。

---

## 4.2 P链不得提前运行

P0–P15评估的是具体ADC产品假设与Construct。

在本模块尚未生成以下内容前，不得正式运行P链：

- concrete binder；
- defined epitope；
- antibody format；
- sequence；
- conjugation platform；
- DAR；
- payload；
- linker；
- construct-level PK/TI assumptions。

本模块可以收集与未来P链相关的先验证据，但必须标记为：

- `forward_evidence`；
- `preliminary_product_constraint`；
- `handoff_note`；
- 或`not_evaluated`。

不得把T9的target-level internalization potential等同于P6的construct-level productive internalization and trafficking。

不得把T10的target-level antibody/epitope realizability等同于P1–P5已经通过。

---

## 4.3 C链按输入成熟度运行

C链不得被整体提前塞入Opportunity生成流程。

在本模块阶段：

- C0–C2可在其正式输入合同满足时作为附加约束或排序参考；
- C4–C8只有在已有足够专利、竞争与技术定义时才可运行；
- C3、C9–C15通常依赖更成熟的产品构型、权利要求或交易材料，默认不在本模块正式运行。

若输入不足，必须输出：

- `NOT_EVALUATED`；
- `UNRESOLVED`；
- 或合同允许的空值语义。

不得为了得到完整表格而虚构输入。

C链结果不能替代T12的Target Opportunity Decision。

---

# 5. Gate Extension治理

## 5.1 何时允许提出Gate Extension

只有当发现一个真实决策问题同时满足以下全部条件时，才允许提出Gate Extension：

1. 该问题无法被现有T、P、C Gate中的任何一个合理表达；
2. 该问题不是数据缺失、证据标准、排序权重、搜索约束或验证任务；
3. 该问题具有独立的Go/Hold/Stop决策意义；
4. 已在至少两个真实Candidate中重复出现；
5. 不增加该Gate会导致系统性错误决策；
6. 无法通过扩展现有Gate的Model、Rule、Profile或Evidence Adapter解决。

不得因为“更方便”“更清楚”或“当前Prompt需要”而新增Gate。

---

## 5.2 Gate Extension必须交付

任何Gate Extension必须先建立独立提案，至少包含：

```yaml
extension_id:
title:
status: proposed
problem_statement:
affected_candidates:
why_existing_gates_are_insufficient:
nearest_existing_gate_ids:
alternatives_considered:
proposed_gate_group:
proposed_dependencies:
proposed_input_contract:
proposed_output_contract:
hard_gate_rationale:
migration_impact:
backward_compatibility:
testing_plan:
approval_record:
```

建议路径：

```text
governance/gate_extensions/<extension_id>/proposal.zh-CN.md
governance/gate_extensions/<extension_id>/contract.yaml
```

在用户明确批准前：

- 不得加入Gate Registry；
- 不得分配正式T/P/C编号；
- 不得修改任何既有Gate依赖图；
- 不得修改现有Profile；
- 不得将其用于淘汰Candidate；
- 只能作为`experimental_review_check`运行。

---

## 5.3 优先扩展顺序

发现新需求时，必须按以下顺序尝试解决：

1. 新Evidence Adapter；
2. 新Data Source；
3. 新Rule；
4. 新Model实现；
5. 新Profile；
6. 新Filter或RankingFeature；
7. 扩展现有Gate合同的兼容字段；
8. 最后才是Gate Extension。

---

# 6. 不可变架构

本模块固定为以下六层：

```text
1. Scope Definition
2. Constrained Clinical Frame Generation
3. Constrained Target Candidate Generation
4. Iterative T-Gate / Rule / Model Evaluation
5. Evidence Sufficiency and Adversarial Review
6. Opportunity Ranking and T12 Handoff
```

不得新增新的顶层阶段。

未来可增加：

- 数据源；
- Evidence Adapter；
- Rule；
- Model；
- Profile；
- Filter；
- RankingFeature；
- 评估轮次配置；
- 公共数据处理脚本；
- 新适应症Scope；
- 新Endpoint Scope。

但不得改变：

- Opportunity临床身份；
- T0–T12作为原生决策链；
- P链后置；
- Gate Extension治理；
- Evidence可追溯要求；
- Generation与Evaluation隔离；
- 多轮候选收缩机制；
- Phase审核机制。

---

# 7. 核心运行逻辑

## 7.1 总体流程

```text
Clinical unmet need scope
        ↓
T0 clinical context and endpoint lock
        ↓
T1 endpoint-driving population definition
        ↓
Limited target candidate generation
        ↓
High-information early evaluation using existing T Gates
        ↓
Evidence acquisition and candidate reduction
        ↓
Remaining T2–T11 evaluation
        ↓
Historical ADC Rule and Model integration
        ↓
Evidence sufficiency and adversarial review
        ↓
T12 target opportunity decision
        ↓
Ranked Opportunity handoff
```

“高信息早期评价”不是新Gate层，而是对现有T Gate的配置化调度。

---

## 7.2 Scope Definition

Scope必须来自已有clinical unmet need定义和T0合同。

输入至少包括：

- indication；
- disease setting；
- line of therapy；
- treatment context；
- comparator；
- patient segment boundary；
- clinical endpoint；
- endpoint time horizon；
- minimum clinically meaningful success condition；
- evidence cutoff date；
- modality constraint：ADC。

输出对象：

`OpportunitySearchScope`

核心字段使用英文：

```yaml
scope_id:
version:
indication:
disease_setting:
line_of_therapy:
treatment_context:
comparator:
patient_segment_constraints:
endpoint_definition:
endpoint_time_horizon:
clinical_success_condition:
modality: ADC
evidence_cutoff_date:
candidate_budget:
source_policy_id:
evaluation_plan_id:
```

不得在未锁定T0上下文时生成target。

---

## 7.3 Clinical Frame生成

`ClinicalFrame`必须由T0和T1共同约束。

最小字段：

```yaml
clinical_frame_id:
indication:
disease_setting:
line_of_therapy:
treatment_context:
comparator:
patient_population:
endpoint:
endpoint_time_horizon:
unmet_need:
endpoint_driving_population:
clinical_rationale:
source_evidence_ids:
t0_result_id:
t1_result_id:
```

只有当T0已完成上下文锁定，且T1至少形成可审核的endpoint-driving population定义时，才能进入target generation。

若T1证据不足，可保留为探索性ClinicalFrame，但不得宣称已锁定目标细胞群。

---

## 7.4 有限Target Candidate生成

Target生成必须在单一ClinicalFrame内进行。

候选来源可以包括：

- peer-reviewed literature；
- public transcriptomics；
- public proteomics；
- single-cell data；
- spatial data；
- pathology data；
- normal tissue resources；
- surfaceome resources；
- receptor trafficking evidence；
- internalization evidence；
- genetic or perturbation evidence；
- historical ADC programmes；
- user-provided internal evidence。

但数据源不是Gate。

每个TargetCandidate必须至少包含：

```yaml
candidate_id:
clinical_frame_id:
target_gene:
target_protein:
target_identity:
biological_hypothesis:
adc_hypothesis:
candidate_generation_reasons:
positive_evidence_ids:
negative_evidence_ids:
unknown_claims:
generation_method:
generation_run_id:
```

必须通过配置限制候选规模：

```yaml
candidate_generation_policy:
  maximum_candidates_per_clinical_frame:
  minimum_distinct_positive_evidence_groups:
  require_target_identity_resolution: true
  require_relevant_tumor_context_evidence: true
  permit_model_only_generation: false
  permit_rule_only_generation: false
```

候选数量不得通过硬编码固定，应由Scope配置。

---

# 8. 现有T Gate的分轮调度

以下是本模块推荐的默认调度，不改变Gate依赖与合同。真实执行顺序仍必须满足Gate Registry中的正式依赖图。

## Round 0：Clinical Lock

使用：

- T0 `clinical_context_endpoint`
- T1 `endpoint_driving_population`

目的：

- 锁定临床问题；
- 限定Endpoint；
- 限定真正驱动Endpoint的细胞群；
- 决定是否允许生成target。

---

## Round 1：Target Mapping and Surface Eligibility

优先使用：

- T2 `target_population_mapping`
- T7 `tumor_cell_surface_availability`

目的：

- 快速排除无法映射到endpoint-driving population的target；
- 快速排除缺乏真实肿瘤细胞表面可用性的target。

注意：

这只是调度优先级，不改变T2、T7的正式依赖。

---

## Round 2：Delivery and Safety Plausibility

使用：

- T8 `intratumoral_antigen_accessibility`
- T9 `antibody_dependent_internalization`
- T10 `antibody_epitope_realizability`
- T11 `on_target_therapeutic_index`

目的：

- 检查抗体能否到达；
- 检查target-level internalization potential；
- 检查是否存在可实现的抗体/表位空间；
- 检查on-target therapeutic index plausibility。

---

## Round 3：Endpoint Biology

使用：

- T3 `intervention_causality`
- T4 `baseline_coverage_and_escape`
- T5 `treatment_induced_state_response`
- T6 `net_endpoint_benefit`

目的：

- 判断清除target-positive population是否真正改变Endpoint；
- 判断覆盖不足、逃逸、状态转换和反弹；
- 综合形成净Endpoint收益判断。

---

## Round 4：Integrated Decision

使用：

- T12 `target_opportunity_decision`

T12必须只消费：

- 同一Candidate；
- 同一运行上下文；
- 版本绑定的T0–T11结果；
- 正式Evidence ID；
- 正式Rule/Model版本。

T12不得引入新的经验事实。

---

# 9. Early Filtering的严格定义

本模块允许Early Filtering，但Early Filter不得伪装成Gate。

Early Filter只能执行以下行为：

- 检查是否满足运行某个既有Gate的最低输入；
- 根据既有Hard Gate的高置信结果淘汰；
- 根据身份冲突或Scope不匹配排除；
- 根据Evidence Policy将候选标记为`EVIDENCE_INSUFFICIENT`；
- 根据候选预算限制暂缓低优先级候选；
- 将候选送入补证队列。

Early Filter不得：

- 创造新Gate语义；
- 把“无数据”改写为FAIL；
- 把Rule直接当成Hard Gate；
- 跳过既有Gate依赖；
- 修改Gate结果；
- 用排名分数覆盖Hard Gate结果。

推荐对象名称：

`CandidateFilterResult`

```yaml
filter_result_id:
candidate_id:
filter_id:
filter_type:
status:
reason:
evidence_ids:
related_gate_ids:
reversible:
required_resolution:
```

---

# 10. Evidence Ledger

所有关键判断必须引用Evidence Ledger。

既有Gate合同规定：

- `null`或`[]`表示unknown；
- 不表示测量零；
- 不表示阳性；
- 不表示阴性。

本模块必须保留该语义，不得转换。

Evidence最小结构：

```yaml
evidence_id:
claim_id:
candidate_id:
clinical_frame_id:
gate_id:
rule_id:
model_id:
evidence_type:
direction:
source_type:
source_reference:
source_date:
access_date:
extraction_method:
raw_observation:
normalized_claim:
confidence:
limitations:
independence_group:
review_status:
```

`direction`至少支持：

- `POSITIVE`
- `NEGATIVE`
- `MIXED`
- `NEUTRAL`
- `UNKNOWN`

必须区分：

- peer-reviewed evidence；
- public dataset observation；
- database annotation；
- model inference；
- historical ADC analogy；
- expert judgment；
- user-provided evidence；
- internal experimental evidence。

LLM总结不能替代原始来源。

---

# 11. Positive Evidence Policy

“没有被淘汰”不等于“可以进入ADC研发”。

进入`READY_FOR_T12_DECISION`或同等状态前，必须满足配置化Positive Evidence Policy。

默认至少要求以下既有Gate域有非空、可追溯的正向或支持性证据：

- T0：clinical context and endpoint；
- T1：endpoint-driving population；
- T2：target-to-population mapping；
- T7：tumor-cell surface availability；
- T9：antibody-dependent internalization potential；
- T11：on-target therapeutic index plausibility。

T3、T4、T5、T6、T8、T10必须至少达到：

- 有可审核结果；
- 或明确UNRESOLVED；
- 或有可执行的验证任务；
- 不能被静默跳过。

这是Evidence Policy，不是新增Gate。

示例：

```yaml
positive_evidence_policy:
  policy_id:
  required_gate_evidence:
    - gate_id: clinical_context_endpoint
      minimum_direction: supported
    - gate_id: endpoint_driving_population
      minimum_direction: supported
    - gate_id: target_population_mapping
      minimum_direction: supported
    - gate_id: tumor_cell_surface_availability
      minimum_direction: supported
    - gate_id: antibody_dependent_internalization
      minimum_direction: supported
    - gate_id: on_target_therapeutic_index
      minimum_direction: supported
  minimum_independent_source_groups:
  maximum_critical_unknowns:
  allow_model_only_support: false
  allow_rule_only_support: false
```

具体阈值必须配置化，不得在核心代码中写死。

---

# 12. Gate、Rule、Model、Filter的边界

## Gate

Gate是既有45个正式决策合同之一，或经批准的Gate Extension。

Gate负责回答一个正式开发决策问题。

## Rule

Rule是从历史ADC或其他证据中归纳出的方向性判断。

Rule必须绑定：

- `rule_id`
- `rule_version`
- `applicable_gate_ids`
- `applicable_context`
- `conditions`
- `expected_direction`
- `supporting_adc_examples`
- `contradicting_examples`
- `evidence_ids`
- `confidence`
- `limitations`

Rule默认不得直接淘汰Candidate。

只有当既有Rule治理明确批准其为Hard Rule，且绑定到现有Gate合同后，才可影响Hard Gate决策。

## Model

Model是某个Gate的可版本化实现。

Model输出必须遵守既有`GateModelOutput`合同。

Model不得创建新Gate。

Model不得把预测值伪装成实验事实。

## Filter

Filter负责候选流量控制、输入完整性检查和运行调度。

Filter不得改变Gate语义。

## RankingFeature

RankingFeature只用于通过基本资格检查后的候选排序。

RankingFeature不得覆盖Hard Gate FAIL。

---

# 13. Generation与Evaluation隔离

必须逻辑隔离：

1. `Generator`
2. `Evidence Collector`
3. `Gate Evaluator`
4. `Rule Evaluator`
5. `Adversarial Reviewer`
6. `T12 Decision Integrator`

最低约束：

- Generator不得修改Gate Registry；
- Generator不得修改Rule Registry；
- Generator输出的理由不能直接成为Gate事实；
- Evaluator必须读取Evidence ID，不得只读取Generator摘要；
- Adversarial Reviewer不得删除原始证据；
- T12只能整合正式T0–T11结果；
- 同一运行必须保留完整trace。

无需建立复杂多Agent平台。可以通过独立函数、Prompt、文件和运行记录实现隔离。

---

# 14. Candidate生命周期

本模块内部状态固定为：

- `SCOPE_DEFINED`
- `CLINICAL_FRAME_GENERATED`
- `CLINICAL_FRAME_RETAINED`
- `TARGET_CANDIDATE_GENERATED`
- `UNDER_T_GATE_EVALUATION`
- `EVIDENCE_INSUFFICIENT`
- `CONDITIONALLY_RETAINED`
- `REJECTED`
- `READY_FOR_ADVERSARIAL_REVIEW`
- `READY_FOR_T12_DECISION`
- `OPPORTUNITY_RETAINED`
- `OPPORTUNITY_ON_HOLD`
- `OPPORTUNITY_REJECTED`
- `ARCHIVED`

不得把模块内部状态描述为：

- validated asset；
- investable asset；
- lead；
- development candidate。

---

# 15. Adversarial Review

Adversarial Review不是新Gate。

它是T12前的独立审核步骤，输出`AdversarialReviewRecord`。

至少检查：

- T1定义的endpoint-driving population是否真实；
- T2映射是否由bulk或非肿瘤细胞混淆；
- T3因果链是否只是相关；
- T4是否存在大比例target-negative residual disease；
- T5是否存在治疗诱导状态转换；
- T6净Endpoint收益是否被短期debulking夸大；
- T7表面证据是否为真实蛋白和抗体可及形式；
- T8是否存在血管、间质、空间或shed-antigen限制；
- T9内吞证据是否依赖不相关细胞系、抗体或表位；
- T10可实现性是否只是注释完整性；
- T11正常组织风险是否被低估；
- 历史ADC Rule是否被选择性引用；
- Evidence是否来自同一数据源的重复分析；
- 数据缺失是否被错误解释为安全。

输出：

```yaml
review_id:
candidate_id:
reviewed_gate_result_ids:
objections:
counter_evidence_ids:
alternative_explanations:
critical_unresolved:
required_validation_tasks:
review_status:
reviewer:
reviewed_at:
```

Adversarial Review不得直接覆盖Gate结果，只能触发：

- 补证；
- 重跑现有Gate；
- HOLD；
- 或提交T12时附带异议。

---

# 16. Opportunity排序

只有以下候选可进入正式排序：

- 无高置信Hard Gate FAIL；
- 满足最低Positive Evidence Policy；
- 完成Adversarial Review；
- 已形成或即将形成T12结果。

排序不是Gate。

排序维度可以包括：

- clinical value；
- endpoint clarity；
- T1 population confidence；
- T2 mapping strength；
- T3 causal support；
- T4/T5 escape burden；
- T6 net endpoint benefit；
- T7 surface availability；
- T8 accessibility；
- T9 internalization potential；
- T10 realizability；
- T11 therapeutic index；
- evidence strength；
- evidence independence；
- historical ADC Rule alignment；
- unresolved risk burden；
- cheapest decisive experiment；
- time to first experiment；
- C0–C2 results when formally available。

不得强制压缩为单一总分。

建议输出：

- `priority_tier`
- `rank`
- `confidence`
- `dominant_strengths`
- `dominant_risks`
- `bottleneck_gate_ids`
- `cheapest_decisive_experiment`
- `next_action`

---

# 17. Opportunity输出Schema

建议最小结构：

```yaml
opportunity_id:
version:
status:

clinical_frame:
  indication:
  disease_setting:
  line_of_therapy:
  treatment_context:
  comparator:
  patient_population:
  unmet_need:
  clinical_endpoint:
  endpoint_time_horizon:
  clinical_success_condition:
  endpoint_driving_population:

target_hypothesis:
  target_gene:
  target_protein:
  target_identity:
  biological_hypothesis:
  adc_modality_hypothesis:
  biomarker_hypothesis:

evidence_summary:
  positive_evidence_ids:
  negative_evidence_ids:
  mixed_evidence_ids:
  unknown_claim_ids:
  evidence_independence_groups:
  source_quality_summary:

target_opportunity_chain:
  t0_result_id:
  t1_result_id:
  t2_result_id:
  t3_result_id:
  t4_result_id:
  t5_result_id:
  t6_result_id:
  t7_result_id:
  t8_result_id:
  t9_result_id:
  t10_result_id:
  t11_result_id:
  t12_result_id:
  hard_failures:
  hard_unknowns:
  bottleneck_gate_ids:

rule_evaluation:
  applied_rule_ids:
  supporting_rule_ids:
  contradicting_rule_ids:
  non_applicable_rule_ids:

model_evaluation:
  model_run_ids:
  model_versions:
  model_limitations:

adversarial_review:
  review_id:
  status:
  objections:
  required_validation_tasks:

ranking:
  priority_tier:
  rank:
  confidence:
  dominant_strengths:
  dominant_risks:

handoff:
  recommendation:
  rationale:
  required_next_evidence:
  cheapest_decisive_experiment:
  eligible_for_asset_generation: false

provenance:
  search_scope_id:
  generation_run_id:
  evaluation_plan_id:
  gate_registry_version:
  rule_registry_version:
  model_registry_version:
  evidence_policy_version:
  evidence_cutoff_date:
  generated_at:
```

只有后续正式审核批准后，`eligible_for_asset_generation`才可变为`true`。

---

# 18. Registry与配置

至少支持：

- `gate_registry`：只读取正式Gate；
- `rule_registry`；
- `model_registry`；
- `data_source_registry`；
- `filter_registry`；
- `evidence_policy_registry`；
- `search_scope_registry`；
- `evaluation_plan_registry`；
- `ranking_policy_registry`。

核心代码不得写死45个Gate的详细合同，但可以验证：

- Gate ID属于正式Registry；
- Profile选择合法；
- 依赖满足；
- 版本锁定；
- 输出符合Schema。

推荐目录遵循现有StelligenOS仓库边界，不得为本模块重复创建第二套Gate合同。

模块内部建议：

```text
gen_indication_endpoint_target/
├── README.md
├── configs/
├── schemas/
├── registries/
├── src/
├── prompts/
├── tests/
├── examples/
├── reports/
└── logs/
```

若仓库已有统一目录规范，应复用现有规范，不得复制一套平行基础设施。

---

# 19. 语言规范

使用中文：

- Prompt；
- README；
- 操作指南；
- Phase报告；
- 审核清单；
- 工作日志；
- Migration Log；
- Decision Log；
- 错误解释；
- Codex执行说明。

使用英文：

- Python/TypeScript/Shell代码；
- 类名、函数名、变量名；
- JSON/YAML键；
- Schema；
- Gate、Rule、Model ID；
- 机器状态；
- 测试名称；
- 科学报告正文；
- Opportunity报告正文；
- Investor/partner-facing报告；
- 核心数据文件。

代码注释优先英文。

---

# 20. 简化原则

禁止：

- 新建第二套Gate系统；
- 复制45个Gate合同到模块内部并形成漂移；
- 无约束枚举全癌种和全膜蛋白；
- 一次接入所有公共数据库；
- 第一版建立知识图谱；
- 第一版建立复杂数据库；
- 第一版建立Web UI；
- 第一版建立多Agent编排框架；
- 把每个过滤条件升级成Gate；
- 把每个数据源升级成Engine；
- 把Rule、Model、Evidence混成一个对象；
- 把空值解释为阴性或零；
- 把模型推测写成事实；
- 用总分覆盖Hard Gate FAIL；
- 自动启动Binder或ADC开发；
- 自动改变Gate依赖；
- 自动提交Gate Extension；
- 自动进入下一Phase。

优先实现：

1. Markdown；
2. YAML/JSON；
3. JSON Schema；
4. Python；
5. 简单CLI；
6. 最小测试。

---

# 21. 分Phase开发计划

每次只执行一个Phase。

## Phase 0：Gate Contract and Existing Asset Audit

目标：

- 读取正式45个Gate合同；
- 读取现有Gate Registry、Profile、Model、Rule和Evidence结构；
- 识别T0–T12可直接复用内容；
- 识别现有clinical unmet need输入；
- 识别当前target generation相关内容；
- 识别所有旧Prompt中伪造或暗含的新Gate；
- 建立迁移矩阵；
- 不实现业务代码。

必须明确：

- 哪些是正式Gate；
- 哪些只是Filter；
- 哪些只是Evidence Policy；
- 哪些只是Review Question；
- 哪些需要Rule/Model扩展；
- 是否存在真正Gate Extension候选。

本Phase不得提出正式新Gate，除非仅作为未批准提案记录。

---

## Phase 1：Module Contract and Schemas

目标：

- 固定模块输入输出；
- 建立`OpportunitySearchScope`；
- 建立`ClinicalFrame`；
- 建立`TargetCandidate`；
- 建立`CandidateFilterResult`；
- 建立`AdversarialReviewRecord`；
- 建立`Opportunity`；
- 建立candidate lifecycle；
- 建立与现有`TargetOpportunityHypothesis`和Gate envelope的适配；
- 不修改任何Gate合同。

---

## Phase 2：T0–T1 Clinical Frame Pipeline

目标：

- 从现有clinical unmet need范围生成有限ClinicalFrame；
- 运行或调用T0；
- 运行或调用T1；
- 保留Evidence；
- 只输出可用于target generation的ClinicalFrame；
- 不大规模生成target。

---

## Phase 3：Target Candidate Generation

目标：

- 在单一ClinicalFrame内有限生成TargetCandidate；
- 接入最少必要公共证据来源；
- 建立Evidence Adapter；
- 建立候选预算；
- 不执行P链；
- 不发明新Gate。

---

## Phase 4：Early T-Gate Candidate Reduction

目标：

- 使用现有T2和T7优先收缩候选；
- 在依赖满足时逐步使用T8–T11；
- 实现Filter与Gate的严格区分；
- 保存所有淘汰和HOLD原因；
- 不将无证据视为FAIL；
- 不运行T12。

---

## Phase 5：Endpoint Biology Completion

目标：

- 补齐T3–T6；
- 接入历史ADC Rule；
- 接入现有Gate Model；
- 生成完整T0–T11 trace；
- 不修改Gate合同；
- 不运行P链。

---

## Phase 6：Evidence Sufficiency and Adversarial Review

目标：

- 实现Positive Evidence Policy；
- 实现Evidence independence检查；
- 实现Adversarial Review；
- 将关键未知转化为ValidationTask；
- 形成`READY_FOR_T12_DECISION`候选。

---

## Phase 7：T12 Decision and Ranking

目标：

- 运行正式T12；
- 保留T12的全部输入版本；
- 区分`provisional_advance`、exploration、HOLD和FAIL；
- 只对合格候选排序；
- 输出Opportunity handoff package；
- 不进入Binder开发。

---

## Phase 8：End-to-End Pilot

使用一个受限CRC ClinicalFrame运行完整闭环。

可以将TWEAKR作为候选之一，但不得预设其胜出。

必须允许：

- TWEAKR被保留；
- TWEAKR被HOLD；
- TWEAKR被淘汰；
- 其他target优先级更高；
- 所有候选均不满足推进标准。

---

## Phase 9：Freeze and Release

目标：

- 修复阻断问题；
- 固定模块合同；
- 固定Gate Extension流程；
- 固定T/P/C边界；
- 发布模块v1.0；
- 归档旧Prompt；
- 明确未来可扩展项和不可变项。

---

# 22. 每个Phase固定交付物

每个Phase必须生成：

1. 中文Phase报告；
2. 中文审核清单；
3. 中文Migration Log更新；
4. 中文Decision Log更新；
5. 英文机器可读Manifest；
6. 测试结果；
7. 实际修改文件；
8. 未解决问题；
9. Gate变更声明；
10. 是否建议进入下一Phase。

Gate变更声明必须明确输出以下之一：

- `NO_GATE_CHANGE`
- `GATE_EXTENSION_PROPOSED_NOT_APPLIED`
- `APPROVED_GATE_EXTENSION_APPLIED`

默认必须是：

`NO_GATE_CHANGE`

---

# 23. Phase报告的Gate合规检查

每个Phase报告必须回答：

1. 是否修改任何现有Gate ID？
2. 是否修改任何现有Gate名称？
3. 是否修改任何现有Gate版本？
4. 是否修改任何Gate输入输出字段？
5. 是否修改任何Gate依赖？
6. 是否修改任何Hard Gate属性？
7. 是否新增任何Gate？
8. 是否把Filter、Rule、Model或Review误称为Gate？
9. 是否提前运行P链？
10. 是否在输入不足时强行运行C链？
11. 是否保留`null`和`[]`的unknown语义？
12. 是否存在未批准Gate Extension？

只要1–7任一为“是”且没有明确批准记录，本Phase必须判定为：

`DO_NOT_PROCEED`

---

# 24. 当前Phase：Phase 0

当前只执行：

`Phase 0：Gate Contract and Existing Asset Audit`

不得执行Phase 1或后续Phase。

## Phase 0必须读取

- 正式Gate合同；
- Gate Registry；
- T/P/C Profile；
- Gate依赖图；
- Model Registry；
- Rule Registry；
- Evidence结构；
- clinical unmet need相关文件；
- 旧`gen_indication_endpoint_target` Prompt；
- target generation相关脚本或Prompt；
- ADC calibration Rule；
- 当前测试和日志。

## Phase 0必须输出

建议路径：

```text
docs/phases/GEN_IET_PHASE_0_REPORT.zh-CN.md
docs/phases/GEN_IET_PHASE_0_REVIEW_CHECKLIST.zh-CN.md
manifests/gen_iet_phase_0_manifest.yaml
logs/migration_log.zh-CN.md
```

报告至少包含：

1. Executive Summary；
2. Official Gate Baseline；
3. T0–T12 Reuse Map；
4. P-chain Boundary；
5. C-chain Boundary；
6. Existing Clinical Scope Assets；
7. Existing Target Generation Assets；
8. Existing Rule and Model Assets；
9. Evidence and Provenance Gaps；
10. Items Incorrectly Described as Gates；
11. Migration Matrix；
12. Gate Extension Candidates；
13. Phase 1 Minimum Scope；
14. Explicit Out-of-Scope；
15. Recommendation。

## Phase 0禁止

- 修改45个Gate；
- 新增正式Gate；
- 迁移大量业务代码；
- 实现target generation；
- 运行真实候选筛选；
- 自动进入Phase 1。

## Phase 0结束输出

完成后在终端或最终回复中明确列出：

- 实际读取的关键文件；
- 新增或修改的文件；
- 可直接复用的T0–T12资产；
- 发现的伪Gate或职责混淆；
- 是否存在真正Gate Extension候选；
- 五个最严重缺口；
- Phase 1建议；
- Gate变更声明；
- 是否建议进入Phase 1。

然后停止。

---

# 25. 最终成功标准

本模块成功不是因为生成了很多靶点，也不是因为给每个靶点打了分。

成功标准是：

> 在T0和T1限定的临床问题中，有限生成target candidates，使用既有T2–T11进行多轮、可审计的证据约束和候选收缩，再由T12作出正式Target Opportunity Decision，最终只保留少量具有非空正向证据、无未解决高置信Hard Gate失败、关键未知可验证、且值得投入第一笔实验资金的Opportunity。

任何新决策问题优先通过Evidence、Rule、Model、Profile、Filter或ValidationTask扩展解决。

只有在现有45个Gate无法表达真实且重复出现的独立决策问题时，才允许提出Gate Extension，并且在人工批准前不得进入正式Gate体系。
