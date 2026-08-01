# `gen_indication_endpoint_target` Phase 0 架构审计报告

- 模块：`gen_indication_endpoint_target`
- 审计日期：2026-08-01
- 审计范围：只审计架构、合同、Registry、规则、模型和迁移边界；不执行业务生成
- 状态：`COMPLETED_PENDING_REVIEW`
- Gate 变更声明：`NO_GATE_CHANGE`

## 1. 执行摘要

Phase 0 已完成。结论是：该模块可以建立在现有 Opportunity Generation 能力和 AssetGenOS 的纯定义资产之上，但不能把 AssetGenOS 的数据库、数据索引、缓存、结果、模型权重、运行器或历史实例迁入 StelligenOS。

AssetGenOS 已有正式冻结的 ADC Gate 拓扑：45 个 Gate，分为 T=13、P=16、C=16。`gen_indication_endpoint_target` 应使用 T0-T12 作为既有 Target Opportunity 决策链的报告别名，不应新增 Gate。候选生成、早期筛选、证据充分性、对抗性审查和排序都不是 Gate。

本阶段没有新增业务代码、没有生成候选、没有读取或复制数据、没有运行真实模型。建议审核通过后进入 Phase 1，只实现无数据的 schema、contract、policy 和外部引用适配边界；Phase 1 仍不执行真实生成。

## 2. 官方 Gate 基线

来源：AssetGenOS `configs/gate_topology_freeze.yaml`、`configs/v0.2_gate_groups.yaml`、`configs/v0.2_graph.yaml` 以及 `components/gates/adc/v0.2/`。

| 项目 | 基线 |
|---|---|
| 拓扑冻结版本 | `adc_gate_topology@0.3.0` |
| 架构版本 | `0.2.0` |
| 正式 Gate 总数 | 45 |
| T-chain | 13 |
| P-chain | 16 |
| C-chain | 16 |
| 本模块 Gate 变更 | `NO_GATE_CHANGE` |

### 2.1 T-chain（13）

`clinical_context_endpoint`、`endpoint_driving_population`、`target_population_mapping`、`intervention_causality`、`baseline_coverage_and_escape`、`treatment_induced_state_response`、`net_endpoint_benefit`、`tumor_cell_surface_availability`、`intratumoral_antigen_accessibility`、`antibody_dependent_internalization`、`antibody_epitope_realizability`、`on_target_therapeutic_index`、`target_opportunity_decision`。

### 2.2 P-chain（16）

`product_design_objective`、`epitope_landscape`、`epitope_function`、`binding_geometry_kinetics`、`antibody_format_fc_design`、`antibody_sequence_developability`、`productive_internalization_trafficking`、`conjugation_platform_site`、`dar_molecular_property_balance`、`payload_cell_state_match`、`linker_release_match`、`bystander_tumor_coverage`、`integrated_pk_stability_exposure`、`construct_therapeutic_index`、`biomarker_clinical_assay_codesign`、`integrated_adc_product_decision`。

### 2.3 C-chain（16）

`commercial_opportunity_threshold`、`regulatory_development_path`、`competitive_position_entry_window`、`product_claim_decomposition`、`patent_landscape`、`preliminary_technical_fto`、`blocking_claim_severity`、`design_around_opportunity`、`access_strategy`、`fto_product_configuration`、`own_ip_inventive_concept`、`patentability_enablement`、`claim_architecture_patent_estate`、`disclosure_filing_strategy`、`lifecycle_exclusivity_strategy`、`transaction_readiness`。

## 3. T0-T12 复用地图

T0-T12 是本模块面向人类和 ChatGPT 的决策链编号，不是新增的第二套 Gate ID。每一行均绑定到上述正式 Gate。

| 决策阶段 | 正式 Gate | 可复用资产 | Phase 0 结论 |
|---|---|---|---|
| T0 | `clinical_context_endpoint` | `clinical_context_endpoint_lock_v1`、T0 context lock | 复用定义和模型插件；输入必须外部化 |
| T1 | `endpoint_driving_population` | `target_population_mapping_evidence_v1` | 复用证据模型；输出 ClinicalFrame，不新增 Gate |
| T2 | `target_population_mapping` | target population evidence/challenger 模型 | 复用规则/模型语义，暂不迁运行时 |
| T3 | `intervention_causality` | intervention causality evidence 模型 | 复用模型契约，保留未知状态 |
| T4 | `baseline_coverage_and_escape` | baseline coverage/escape evidence 模型 | 复用字段语义，禁止缺数据判 FAIL |
| T5 | `treatment_induced_state_response` | treatment state response evidence 模型 | 复用模型身份和证据方向 |
| T6 | `net_endpoint_benefit` | deterministic net-benefit integrator | 复用确定性集成逻辑，但改为外部引用输入 |
| T7 | `tumor_cell_surface_availability` | T7 consensus、direct-surface evidence contract | 复用正式证据合同；需补 provenance 端口 |
| T8 | `intratumoral_antigen_accessibility` | 现有 Gate/LLM baseline 定义 | 只复用定义和模型身份，不复制数据 |
| T9 | `antibody_dependent_internalization` | trafficking reference model | 复用方向性模型；不可把 reference 变成 Gate 结果 |
| T10 | `antibody_epitope_realizability` | annotation precedent model | 复用模型语义；保留 UNRESOLVED |
| T11 | `on_target_therapeutic_index` | TI evidence model | 复用证据结构和模型身份 |
| T12 | `target_opportunity_decision` | deterministic decision integrator | 复用最终决策语义；不得用总分覆盖 hard fail |

AssetGenOS 的 `v2 evaluate` 和 pipeline 可以作为历史行为参考，但不作为 StelligenOS 的可直接运行实现，因为它们初始化数据库并管理本地运行状态。

## 4. P-chain 边界

P-chain 只有在具体产品假设成熟后才可启动，最低需要 binder、epitope、format、sequence、conjugation、DAR、payload、linker、construct 等明确输入。当前 `gen_indication_endpoint_target` 只负责临床问题、endpoint、患者群体和 target opportunity 假设，不负责产品构型设计。

因此 P0-P15 全部不在本模块 Phase 0/Phase 1 最小范围内。任何“候选已通过 P-chain”的描述都必须被拒绝，除非外部产品设计运行已经提供可审计的输入和引用。

## 5. C-chain 边界

C0 unmet need 和 C2 competitive landscape 可以作为补充证据或优先级输入，但不能替代 T-chain，也不能把临床 scope 分数描述为商业预测。C3 及 C9-C15 通常不属于本模块默认范围；C-chain 不能在 T12 之前改变 target opportunity 的正式 Gate 语义。

所有不足输入必须记录为 `NOT_EVALUATED`、`UNRESOLVED` 或 validation task，不能静默降级为 PASS，也不能把未知当作零风险。

## 6. 现有临床范围资产

AssetGenOS 已有 `ClinicalUnmetNeedEvidenceAdapter` 和 `configs/c0_unmet_need_sources.yaml`：

- 外部数据集身份：`ADC_clinical_unmet_need_reference@0.1.0`
- 外部相对根：`DATA/1.Databases/ADC_clinical_unmet_need_reference`
- 场景表：`processed/v0.1.0/clinical_unmet_need_scenarios.tsv`
- 证据截止日期：`2026-07-29`
- 匹配维度：indication、patient segment、molecular subtype、disease setting、line、treatment context
- 评分语义：prognosis severity、option scarcity、durability gap 的临床 unmet need 参考分数
- 约束：confidence cap 0.45；不是商业预测、不是患者计数、不是 target recommendation

这些是外部数据接口和语义的迁移依据，不是允许复制到 StelligenOS 的数据。StelligenOS 已有 `OpportunityGenerationRequest` 外部端口，可承接 knowledge scope、clinical context、generation policy 和 run context 的逻辑引用。

当前缺少无数据的 `OpportunitySearchScope`、`ClinicalFrame`、evidence policy 和 search scope registry 合同，需要在 Phase 1 补齐。

## 7. 现有 Target Generation 资产

AssetGenOS 的 `src/adc_factory/seed.py` 提供 `create_candidate` 和 deterministic mock candidate 生成，字段覆盖 target gene/protein、indication、cancer type、subtype、cell state、hypothesis、generation method、source run。`src/adc_factory/cli.py` 的 `generate` 和 `v2 evaluate` 提供历史入口。

迁移结论：只迁移字段语义、生成策略配置的概念和来源追踪要求，不迁移 mock seed、CSV、evidence JSON、SQLite、pipeline runner 或 output。候选生成策略必须 config-driven，不能硬编码在业务代码中。

当前 StelligenOS 尚无 `gen_indication_endpoint_target` 模块目录；这是有意保留的 Phase 0 边界，不代表遗漏。

## 8. 现有 Rule 和 Model 资产

可复用软件定义包括：

- `docs/gate_rules/ADC_naive_rules_batch1_T0-T12_v0.1.json`
- `docs/gate_rules/ADC_naive_rules_batch2_P0-P15_v0.1.json`
- `docs/gate_rules/ADC_naive_rules_batch3_C0-C15_v0.1.json`
- `docs/gate_rules/RULE_MODEL_INDEX.md`
- `configs/naive_rule_guardrails.yaml`
- `components/contracts/historical_adc_rule_reference.v1.0.yaml`
- AssetGenOS 的 45 个 baseline model 定义及 T0/T2/T3/T4/T5/T6/T7/T9/T10/T11/T12 专用模型定义

历史 Rule 只能作为方向性弱监督或证据提示，不能把历史终态直接映射为 Gate FAIL，不能自动覆盖 Gate 结果。Model、Rule、Evidence Collector、Gate Evaluator、Adversarial Reviewer 和 T12 Integrator 必须保持逻辑分离。

## 9. Evidence / provenance 缺口

Phase 0 发现以下必须在 Phase 1 通过合同显式解决的缺口：

1. StelligenOS 尚无满足最小字段集的 data-free evidence ledger record。
2. 尚无 `OpportunitySearchScope`、`ClinicalFrame`、`TargetCandidate`、`CandidateFilterResult`、`AdversarialReview` 的模块合同。
3. 尚无独立性分组、source date/access date、extraction method 和 review status 的统一外部证据引用合同。
4. AssetGenOS 模型插件依赖 DB-backed `Evidence` 和运行上下文，不能原样导入。
5. 尚无 search scope、evaluation plan、evidence policy、filter、ranking policy 的模块 Registry 合同。
6. 尚无明确的 adversarial review 记录来承载反例、替代解释、关键未知和验证任务。
7. 尚无把 T0/T1 结果安全映射到现有 `OpportunityGenerationRequest` / `TargetOpportunityHypothesis` 外部端口的适配合同。

## 10. 不应被描述为 Gate 的项目

以下项目必须保持非 Gate 身份：

- candidate budget、candidate filter、去重、数据完整性检查和早期淘汰；
- C0 unmet need score、临床 scope 保留分数和商业预筛；
- historical Rule、naive Rule、model challenger 和 evidence adapter；
- T0-T12 的 round schedule、Evidence Sufficiency、Adversarial Review、Validation Task；
- opportunity ranking、ranking score、handoff readiness；
- “没有数据”到 `FAIL` 的转换；
- P/C 链未运行时对完整 ADC 产品或商业可执行性的断言。

## 11. 迁移矩阵

| 资产 | 来源 | 迁移决定 | 目标阶段 |
|---|---|---|---|
| 45 Gate 定义/拓扑 | AssetGenOS gate YAML/config | 使用现有 `assetgenos_catalog`，不复制为新 Gate | 已完成 |
| T0-T12 Rule/Model 身份 | AssetGenOS registry/docs | 建立引用和 profile 映射 | Phase 1 |
| Clinical unmet need adapter | `src/adc_factory/unmet_need.py` | 只抽象外部引用合同 | Phase 1 |
| Scope / ClinicalFrame | Master Prompt | 新增 data-free schema | Phase 1 |
| TargetCandidate | `seed.py` 字段语义 + Prompt | 新增 data-free schema，config-driven generation policy | Phase 1 |
| CandidateFilterResult | Prompt | 新增非 Gate 合同 | Phase 1 |
| Evidence ledger record | Prompt + existing external ports | 新增 provenance 合同 | Phase 1 |
| AdversarialReview | Prompt | 新增非 Gate 合同 | Phase 1 |
| Opportunity / T12 handoff | StelligenOS capability port + Prompt | 建立适配合同，不复制实例 | Phase 1 |
| DB、CSV、TSV、JSON evidence instances | AssetGenOS runtime/data | 禁止迁移 | 永不进入本仓库 |
| cache、output、weights、runner | AssetGenOS runtime | 禁止迁移 | 外部 runtime |
| P-chain execution | AssetGenOS product profile | 本模块不执行 | 后续独立阶段 |
| C-chain execution | AssetGenOS commercial profile | 仅按外部引用补充 | 后续独立阶段 |

## 12. Gate Extension 候选

没有发现必须新增 Gate 的问题。临床 scope 定义、候选生成策略、证据充分性、对抗性审查和排序均可由现有 Gate + Rule + Model + Filter + ValidationTask 组合表达。

**Gate 变更声明：`NO_GATE_CHANGE`。**

## 13. Phase 1 最小范围

Phase 1 仅建议实现以下无数据软件合同：

1. `OpportunitySearchScope`：indication、disease setting、line、treatment context、comparator、endpoint、time horizon、success condition、candidate budget、source/evaluation policy 引用。
2. `ClinicalFrame`：临床上下文、endpoint-driving population、T0/T1 结果引用和外部证据 ID。
3. `TargetCandidate`：target 身份、biological/ADC hypothesis、正负证据引用、未知声明、生成方法和 run 引用。
4. `CandidateFilterResult`：保留/排除理由和未知状态；明确不是 Gate。
5. `EvidenceRecord`：claim、candidate、frame、gate/rule/model、source、日期、提取、观察、归一化主张、置信度、局限、独立性和审查状态。
6. `AdversarialReview` 和 T12 handoff：反例、替代解释、关键未知、验证任务和外部 Opportunity 引用。
7. 生命周期枚举和 config-driven policy Registry；不实现真实生成和真实评估。

## 14. 明确不在范围内

本模块当前不复制或实现：任何数据文件、数据库、SQLite、cache、result、model weight、运行器、真实候选生成、真实证据采集、真实 Gate 执行、完整 P-chain、完整 C-chain、商业预测、患者计数、自动网页检索、外部数据落盘以及新的 Gate。

## 15. 建议与停止点

建议架构审核批准 Phase 0，并批准进入 Phase 1 的“纯合同/边界”工作。Phase 1 只有在本报告和审核清单获得明确批准后才能开始；本次任务在此停止，不进入业务代码或真实资产生成。

