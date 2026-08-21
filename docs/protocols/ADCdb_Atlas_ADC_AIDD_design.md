# ADCdb–Atlas–ADC AIDD Design Pipeline

- 文档版本：`ADCdb_Atlas_ADC_AIDD_Design@0.2.0-draft`
- 状态：`DESIGN_REVISION_PENDING_CHATGPT_REVIEW_EXECUTION_NOT_AUTHORIZED`
- 首个疾病试点：`MSS/pMMR refractory metastatic colorectal cancer`
- 适用策略：Small Biotech、repurposing-first、计算优先、外部平台协作
- 当前授权：只设计，不执行 ADCdb 抽取、Atlas 分析、Gate 评分、AIDD、ADC 组装或实验
- 修订基线：`0.1.0` 已由 PR #84/#85 审核收口；`0.2.0-draft` 只补 artifact contract、成本门控和 pre-assembly antibody-hit 接口

## 1. 最终目标与 100% 定义

这条 pipeline 的目标不是从全部膜蛋白中寻找“最新奇”的 ADC 靶点，而是：

> 从已经被真实 ADC 开发部分去风险的 target universe 出发，在明确的 refractory patient territory 中寻找 indication-transfer opportunity；通过 Atlas 和 StelligenOS Gate 缩小不确定性，寻找可形成独立知识产权的新 epitope/binder，再借助成熟 ADC 平台形成并逐步验证 ADC hit。

本项目的 `100%` 终点定义为：完成一次版本化、可复现、可审计的外部运行，从 patient territory lock 到至少一个组装后的 ADC hit，形成经人类批准的 `GO`、`ITERATE` 或 `STOP` 验证决策包。该终点不等于 DevelopmentCandidate、IND-ready asset、临床候选物或临床成功。

对象链固定为：

```text
OpportunityTerritory
  -> ClinicalHypothesis
  -> TargetHypothesis
  -> BinderCandidate
  -> ADCConstruct
  -> LeadSeries / validated hit package
```

所有科学数据、证据、候选、模型产物和实验结果都保存在仓库外部；StelligenOS 只保存设计、合同、代码和小型审计文档。

## 2. 核心收敛逻辑

### 2.1 疾病空间先收敛，靶点搜索后开始

CRC 首个试点的硬约束是：

```text
MSS/pMMR refractory mCRC
post-standard-of-care, operationally 3L+ unless a reviewed clinical definition supersedes it
```

靶点搜索开始前还必须固定：既往治疗、耐药/难治状态、关键转移背景、未满足需求、intended benefit、endpoint class 和 biomarker hypothesis。早期只锁 endpoint class，不假装已经锁定最终注册性 endpoint。

“其他癌种也必然收敛到这个空间”的可迁移含义不是所有癌种都变成 mCRC，而是：

> 每个癌种都必须先收敛到一个由疾病阶段、治疗线次、既往治疗、耐药状态和预期临床获益共同定义的 refractory patient territory；不得以一个 target 名称代替 patient territory。

### 2.2 ADCdb 提供现实世界 prior，Atlas 判断适应症迁移

- `ADCdb` 回答：哪些 target、antibody、ADC、indication、临床阶段和构型已经被真实资金与开发活动探索过。
- `Atlas` 回答：这些已部分去风险的 target 是否在 refractory mCRC 中保留、覆盖足够患者、覆盖恶性细胞、在治疗后和转移灶中保持，并具有可管理的正常组织风险。
- `Gate` 回答：证据是否足以支持 Target Opportunity、Product Realization 和 Commercial Executability 的下一步判断。
- `AIDD` 回答：能否在 target 已去风险的前提下，围绕新的可及 epitope 形成差异化、可实验验证的 binder candidate。
- `ADC platform` 回答：能否用成熟 conjugation/linker/payload 能力把 binder 转成可质控、可测量的 ADC hit。

### 2.3 创新只集中在少数维度

首选资产形态为：

```text
已部分去风险的 ADC target
× 新的 refractory mCRC patient selection
× 新 epitope / 新 binder
× 成熟或平台已验证的 linker-payload / conjugation
```

不得在同一个首轮项目里同时押注全新 target、全新 internalization mechanism、全新 binder、全新 linker、全新 payload 和全新 conjugation chemistry。

## 3. 三个不能混为一谈的“避让”决策

### 3.1 Target crowding

“去掉最热门靶点”必须由版本化 `crowding_policy_ref` 求值，至少记录：同适应症批准资产、临床阶段分布、活跃项目数、独立 sponsor 数、近期 readout、项目终止历史和同类产品差异化空间。

高拥挤不等于科学 KILL，只能路由为 `WATCHLIST`、`PARTNER_ONLY` 或 `OUT_OF_MANDATE`。不得仅用项目数量或新闻热度自动删除 target。

### 3.2 Target / antibody / epitope IP whitespace

Target 已被开发不代表所有 epitope 都被占据。需要分别核对 target-level claims、已知 antibody sequence claims、epitope/competition-bin claims、功能性 claims、用途和 indication claims。输出只能是 `FTO_PLAUSIBILITY_TRIAGE`，不能声称法律意义上的 `FTO_CLEARED`。

### 3.3 Linker-payload / conjugation FTO

Linker-payload 在 target 初筛时只作为平台可行性背景，不作为过早淘汰 target 的默认理由。正式 linker-payload FTO 在 binder 已有实验支持、进入 ADC assembly 前执行，覆盖 chemistry、cleavability/release mechanism、payload class、conjugation site、DAR range、组合 claims 和平台许可边界。

三类避让结果必须分别存储，不得合成一个不可解释的“专利分数”。最终法律意见必须由 patent counsel 给出。

## 4. 执行和审核状态机

每个 Stage 使用以下状态：

```text
NOT_AUTHORIZED
  -> CONTRACT_APPROVED
  -> RUNNING
  -> RESULT_PENDING_REVIEW
  -> RESULT_APPROVED
```

任何阻断进入 `BLOCKED`；修复后仍回到同一个 Stage。每个 Stage 必须按顺序经过：

1. contract/design PR：冻结输入、输出、来源、方法、校验和停止条件；
2. ChatGPT 在本项目指定的同一 GitHub 审核对话中给出明确 `APPROVE`；
3. 外部运行：只写外部 DATA 目录；
4. result PR：仓库只记录 manifest 引用、状态和 handoff，不提交结果数据；
5. ChatGPT 明确 `APPROVE` 后，下一 Stage 才可开始。

`APPROVE_WITH_NONBLOCKING_COMMENTS` 不放行下一 Stage。脚本成功、产物存在或 AI 没发现 bug 也不构成放行。

### 4.1 全局工程控制

- **Fatal-first**：source、identity、patient territory、normal-tissue、surface accessibility、platform access 和明显 IP blocker 必须先于昂贵生成或实验工作求值。
- **Unknown is not safe**：`UNKNOWN`、`UNRESOLVED`、`CONFLICTING` 和缺失证据都不能转成正结论，也不能静默丢弃。
- **No silent fallback**：parser 失败、alias 无法消歧、structure 缺失、模型失败、平台不可用或实验批次失败必须形成显式 blocker/error artifact；不得用空表或 mock 输出继续。
- **Immutable outputs**：任何被下游消费的 Stage 输出必须由 immutable run ID、pipeline version、source snapshot、code commit 和 checksum 唯一定位；修订必须产生新版本，不能原位覆盖。
- **Stage-local claims**：target prior、Atlas context、binder prediction、实测 binder 和 ADC construct 是不同证据层，不得向下游升级宣称。
- **Cost-escalation approval**：启动 AIDD、下单 binder synthesis、开始 ADC conjugation 和进入 focused in-vivo 前，分别需要独立 human decision artifact。

## 5. 单一外部运行根目录

每次完整运行只有一个根目录：

```text
${BIOWORKSPACE_ROOT}/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/<pipeline_run_id>/
├── 00_governance/
├── 01_patient_territory/
├── 02_adcdb_target_prior/
├── 03_crowding_ip_triage/
├── 04_atlas_transfer_validation/
├── 05_target_gate_review/
├── 06_program_commitment/
├── 07_epitope_aidd/
├── 08_adc_assembly/
├── 09_progressive_validation/
└── report/
```

不得为同一次运行建立多个 sibling result root。每个 Stage 都必须保存 `input_manifest`、`output_manifest`、source/version/checksum、代码 commit、环境信息、方法配置、日志、异常、未解决项和 reviewer decision。

## 6. Stage 0 — Governance、source admission 与快照冻结

目的：确保 ADCdb、Atlas、专利、临床和蛋白来源可被审计，不能把“本地已有数据”误写成“已准入数据”。

| 项目 | 定义 |
|---|---|
| 输入 | ADCdb/ADC Drug Index 位置与版本证据；Atlas dataset registry；专利与临床来源清单；source licence/access notes；Sponsor Profile；route policy |
| 必需检查 | ADCdb `SRCADM-02` 独立准入；snapshot/cutoff/checksum；字段白名单；identity normalization；去重规则；更新策略；licence 与只读边界 |
| 输出 | `source_admission_bundle.json`、`source_snapshot_manifest.json`、`field_dictionary.yaml`、`identity_resolution_policy.yaml`、`run_governance.yaml` |
| 放行条件 | 所有承重来源均有可验证 admission record；没有悬空 ref；ADCdb snapshot 被固定；人类批准本次运行范围 |
| STOP/BLOCK | `SRCADM-02` 未准入；无法固定 ADCdb 快照；来源许可/访问不清；关键字段无法追溯；Sponsor Profile 或 route policy 缺失 |
| 不得声称 | 数据集已证明任何靶点有效；source admission 等于生物学/临床结论 |

当前已知 blocker：仓库既有记录仍把 `ADCdb` 标为 `SRCADM-02` 待准入。设计 PR 不解除该 blocker。

## 7. Stage 1 — Refractory Patient Territory Lock

目的：先冻结“为谁解决什么临床失败”，再允许 target 进入搜索。

| 项目 | 定义 |
|---|---|
| 输入 | 已批准 Opportunity Territory Map；公开临床证据；SOC/既往治疗；Sponsor Thesis；人类给定的 MSS/pMMR refractory mCRC 约束 |
| CRC 必填字段 | MSS/pMMR；metastatic；refractory/post-SOC；治疗线次；prior-treatment classes；关键转移背景；current failure mode；intended benefit；endpoint class；biomarker hypothesis |
| 输出 | `clinical_hypothesis.json`、`patient_territory_definition.md`、`endpoint_strategy.yaml`、`exclusion_boundary.yaml` |
| 放行条件 | ClinicalHypothesis 至少达到 `anchored`；patient territory、intended benefit 与 endpoint class 可审计；不由 target 名称定义 territory |
| STOP/BLOCK | patient population 仍过宽；“refractory”未操作化；endpoint 与 intended benefit 不一致；biomarker 与患者选择无法连接 |
| 不得声称 | 早期 endpoint class 是最终注册 endpoint；MSS/pMMR 本身预测 ADC 获益 |

其他癌种复用时，只替换 disease-specific territory 内容，不改变“territory-first”的顺序。

## 8. Stage 2 — ADCdb Target Prior Universe

目的：从已被 ADC 世界探索过的 target 开始，而不是从全部 human surfaceome 开始。

| 项目 | 定义 |
|---|---|
| 输入 | Stage 0 已准入 ADCdb snapshot；ADC/antigen/antibody/linker/payload/indication records；identity policy |
| 最小纳入逻辑 | target 在其他癌种或适应症中至少有可追溯 ADC precedent；优先临床阶段 precedent；必须记录证据层级，不能把 preclinical 与 clinical 混写 |
| 输出 | `adcdb_target_universe.tsv`、`adc_program_precedent.tsv`、`target_identity_map.tsv`、`cross_indication_precedent.tsv`、`source_manifest.json` |
| 每 target 必填 | canonical target；synonyms；ADC programme refs；indications；最高可信阶段；active/terminated status；antibody refs；已知 internalization/delivery refs；source locator；unknowns |
| 放行条件 | 全部 target 可追溯到 ADCdb source record；阶段和适应症文本经过审计；重复 target/alias 已解析；没有 ranking 或推荐 |
| STOP/BLOCK | 不能区分 ADC programme 与 target；阶段来源不明；同一记录重复计数；只因 RNA 表达而纳入；无法区分临床与 preclinical precedent |
| 不得声称 | ADC precedent 自动证明 CRC efficacy、CRC expression、安全窗或可用 epitope |

Stage 2 只产生 target prior universe，不运行 Gate，不决定 shortlist。

进入后续 active search 的 precedent floor 必须分别有可追溯记录：抗体可接近的 extracellular target、internalization/trafficking 或 payload-delivery 先例、以及真实 ADC construct 先例。缺少任一轴时保留在 universe，但默认不能作为 `ACTIVE_SEARCH` 放行；临床阶段 ADC 先例权重最高，但不能替代 target territory-specific 证据。

## 9. Stage 3 — Sponsor-relative Crowding 与 IP Triage

目的：保留“跟车”带来的去风险价值，同时避开 Small Biotech 无法承受的正面拥挤和明显 IP 封锁。

| 项目 | 定义 |
|---|---|
| 输入 | Stage 2 target universe；最新竞争管线；批准/临床/终止信息；公开专利；Sponsor Profile；route policy |
| 分析轴 | same-territory occupancy；跨癌种 precedent；sponsor concentration；临床成熟度；近期 readout；target/antibody/epitope claims；design-around plausibility；partnerability |
| 输出 | `target_crowding_matrix.tsv`、`target_ip_triage.tsv`、`target_route_decisions.tsv`、`opposing_evidence.tsv`、`missing_information.tsv` |
| 路由 | `ACTIVE_SEARCH`、`WATCHLIST`、`PARTNER_ONLY`、`OUT_OF_MANDATE` |
| 放行条件 | 路由依据逐字段可追溯；高拥挤与 IP 风险分开；至少存在一个有 ADC precedent 但在目标 territory 仍有白区的候选，或明确输出 empty result |
| STOP/BLOCK | 用一个任意项目数阈值定义“最热门”；把高拥挤写成科学 KILL；把 AI patent search 写成 FTO clearance；提前用 linker-payload 专利删除 target |
| 不得声称 | `OUT_OF_MANDATE` 否定 target 科学价值；专利检索等于法律意见 |

## 10. Stage 4 — Atlas Indication-transfer Validation

目的：判断其他癌种已部分去风险的 ADC target 能否迁移到 MSS/pMMR refractory mCRC。

| 项目 | 定义 |
|---|---|
| 输入 | Stage 1 ClinicalHypothesis；Stage 3 active/watch candidate refs；准入的 bulk/scRNA/spatial/proteomic/IHC/normal-tissue/clinical datasets；analysis plan |
| 必答问题 | 恶性细胞表达；患者 prevalence；malignant-cell coverage；antigen density proxy；治疗后保留；原发-转移保留；肝/腹膜等关键转移灶；患者内/间异质性；正常组织与关键细胞；shedding/sink；与 intended benefit 的关联 |
| 输出 | `target_atlas_evidence.tsv`、`patient_coverage.tsv`、`treatment_state_retention.tsv`、`metastasis_retention.tsv`、`normal_tissue_risk.tsv`、`heterogeneity_escape.tsv`、`analysis_report.md` |
| 放行条件 | patient-level unit 正确；RNA、protein、surface density 分层；source/analysis version 完整；支持、反对、冲突、未知证据同时保留 |
| STOP/BLOCK | 把 RNA 当 surface protein；把平均表达当 patient coverage；忽略治疗史/转移灶；公开 atlas 与真实 refractory population 不匹配；关键证据只能来自未准入数据 |
| 不得声称 | association 等于 causality；公开数据直接证明 internalization、payload delivery、疗效或安全窗 |

Atlas 的角色是验证 indication transfer，不是重新做一个无边界的 CRC encyclopedia。

## 11. Stage 5 — Target Opportunity Gate Review

目的：把 Stage 1–4 的证据送入冻结的 T-chain，而不是用一个自造综合分数替代 Gate。

| 项目 | 定义 |
|---|---|
| 输入 | ClinicalHypothesis；TargetHypothesis candidates；ADCdb precedent；Atlas evidence；normal-tissue prescreen；competition/IP evidence；opposing/conflict/unknown refs |
| Gate 范围 | T0–T12：clinical context、endpoint-driving population、target-population mapping、causality、coverage/escape、treatment-state response、net endpoint benefit、surface availability、intratumoral accessibility、internalization、epitope realizability、target-level TI、integrated target decision |
| 输出 | `gate_input_manifest.json`、`gate_results.tsv`、`gate_evidence_map.tsv`、`opposing_evidence.tsv`、`unresolved_gaps.tsv`、`target_shortlist_decision.json` |
| 每 Gate 必填 | model/rule version；score（可为空）；confidence（可为空）；status；supporting/opposing refs；missing information；recommended validation；human reviewer |
| 放行条件 | 所有依赖顺序合法；UNKNOWN 保持 UNKNOWN/HOLD；T12 只综合已实际求值的 Gate；候选必须使用冻结的 `PROVISIONAL_ADVANCE`、`EXPLORATION`、`HOLD` 或 `FAIL` disposition |
| STOP/BLOCK | ADCdb precedent 自动 PASS T7/T9/T11；Atlas expression 自动 PASS internalization；缺失证据被写成反对证据；自造总分覆盖 Gate；跳过 hard unknown |
| 不得声称 | 高分等于生物学真值；target-level TI 等于构型特异 therapeutic window |

Stage 5 的 shortlist 是 Target Opportunity shortlist，不是 ADC hit shortlist。

## 12. Stage 6 — Program Commitment 与 Value-Inflection Plan

目的：在开始 expensive binder/AIDD 工作前，再问一次“当前 Small Biotech 是否值得投入”。

| 项目 | 定义 |
|---|---|
| 输入 | T12 decision；`SponsorFitAssessment@0.1.0` external ref；Sponsor Profile；资本边界；能力缺口；IP/FTO triage；buyer/partner map；竞争窗口 |
| 输出 | `program_commitment_review.json`、`value_inflection_plan.json`、`capability_sourcing_plan.yaml`、`partner_platform_brief.md` |
| 允许结果 | `SELF_DEVELOP`、`CO_DEVELOP`、`DATA_PACKAGE_ONLY`、`PARTNER_NOW`、`MONITOR`、`STOP_FOR_SPONSOR` |
| 冻结绑定 | `ProgramCommitmentReview@0.2.0` 必须消费无默认值的 `sponsor_fit_assessment_ref`；缺少该 external ref 时不得构造 commitment review |
| 下游状态 | `SELF_DEVELOP`、`CO_DEVELOP`、`PARTNER_NOW` -> `EXTERNAL_HANDOFF_REQUIRED`；`MONITOR`、`DATA_PACKAGE_ONLY`、`STOP_FOR_SPONSOR` -> `BLOCKED_NO_COMMITMENT` |
| 必填计划 | target transaction stage；minimum evidence package；success criteria；stop conditions；cost/duration band refs；required capabilities；capability sources；buyer requirements；fallback route |
| 放行条件 | 只有 `SELF_DEVELOP`、`CO_DEVELOP` 或 `PARTNER_NOW`，且 `downstream_status = EXTERNAL_HANDOFF_REQUIRED`、human decision/authorization 已存在、ValueInflectionPlan 完整、stop conditions 非空、AIDD/平台能力来源明确，才允许进入 Stage 7 |
| STOP/BLOCK | `MONITOR`、`DATA_PACKAGE_ONLY` 或 `STOP_FOR_SPONSOR` 必须停在 `BLOCKED_NO_COMMITMENT`，不得进入 epitope/AIDD；没有 SponsorFitAssessment ref；没有 ValueInflectionPlan；没有 external platform/CRO 路径；关键未知只能用大规模新实验才能判断基本价值；资本与时间窗不匹配 |
| 不得声称 | `STOP_FOR_SPONSOR` 是科学 KILL；commitment 自动启动 Asset Generation |

Stage 6 的正式承重链是：`SponsorFitAssessment@0.1.0` -> `ProgramCommitmentReview@0.2.0` -> `ValueInflectionPlan@0.1.0` -> human authorization -> asset-directed route。具有人类批准不等于获得 asset-directed commitment；non-asset-directed outcome 不得绕过 `BLOCKED_NO_COMMITMENT`。

## 13. Stage 7 — Epitope White-space、AIDD 与 Experimental Antibody Hit

目的：在 target biology 已部分去风险后，把创新集中到新的、可及的 epitope 和 binder，并在 ADC assembly 前补齐真实 antibody-hit 证据。

### 13.1 Stage 7A — Epitope hypothesis 与 AIDD design candidate

| 项目 | 定义 |
|---|---|
| 输入 | approved TargetHypothesis；asset-directed `ProgramCommitmentReview@0.2.0` ref；`SponsorFitAssessment@0.1.0` ref；完整 ValueInflectionPlan ref；human authorization ref；`aidd_execution_decision.json`；extracellular-domain/topology/isoform/PTM evidence；known antibody/epitope map；target/antibody/epitope patent triage；species orthology；negative-design constraints；AIDD tool manifest |
| 顺序 | target biology → antigen engineering → epitope engineering → IP-guided epitope selection → structural preparation → negative design → de novo design → multi-objective ranking → diversity → focused wet-lab plan |
| 输出 | `epitope_opportunities.tsv`、`epitope_packets/`、`aidd_input.yaml`、`binder_candidates.fasta`（仅真实工具输出时）、`predicted_structures/`、`binder_ranking.tsv`、`synthesis_panel.tsv`、`focused_validation_plan.yaml`、`patent_triage.md` |
| 放行条件 | epitope 在结构/拓扑上可及；避开明显已知 footprint/claims；候选保持 sequence/structure diversity；developability、specificity、cross-reactivity 和 ADC carrier constraints 已进入目标函数；human synthesis decision 已存在 |
| STOP/BLOCK | 没有可用 extracellular epitope；只有受阻断 claims 覆盖的 epitope；外部 AIDD 工具不可用却生成虚构序列；只按 affinity prediction 排序；没有 negative controls；没有 reproducible model/version/seed/input manifest |
| 不得声称 | prediction 证明结合、epitope、internalization、可制造性、专利性或 ADC readiness |

新 epitope 在律师和实验确认前只能称为 `epitope whitespace hypothesis`，不能称为已验证 novel epitope。AIDD 输出只能称为 `design candidate`，不能称为 binder。

### 13.2 Stage 7B — Experimental antibody-hit validation

| 项目 | 定义 |
|---|---|
| 输入 | human-approved synthesis panel；真实 expressed binder lots；recombinant target；target-positive/negative cells；relevant refractory CRC models；benchmark/known-binder controls |
| 最小实验 | identity/purity/aggregation/expression；biochemical binding；cell-surface binding；specificity；epitope verification/binning；internalization kinetics；trafficking/lysosomal delivery；cross-reactivity；developability |
| 输出 | `antibody_hit_validation.tsv`、`binding_kinetics.tsv`、`epitope_validation.tsv`、`internalization_trafficking.tsv`、`developability_qc.tsv`、external experimental refs、`adc_grade_binder_decision.json` |
| 允许状态 | `ADC_GRADE_HIT`、`NEEDS_OPTIMIZATION`、`BINDER_NOT_ADC_GRADE`、`FAIL` |
| 放行条件 | 只有实验确认的 `ADC_GRADE_HIT`，且 identity/QC、specific binding、cell binding、epitope status、internalization/delivery 和 developability 可追溯，才允许进入 Stage 8 |
| STOP/BLOCK | 未表达或错误 identity；无 target-specific binding；错误/未解析 epitope；只结合不内吞/不递送；严重 cross-reactivity 或 developability defect；实验数据只有转述无 source refs |
| 不得声称 | 单一 affinity、单一 internalization readout 或计算预测等于 ADC-grade antibody；binder-level evidence 等于 ADC therapeutic window |

Stage 7A 与 7B 是同一顶层 Stage 内的两个独立成本门。两者各自执行 contract approval、外部运行、result review 和 immutable output manifest；产物分别位于单一运行根下的 `07_epitope_aidd/7A_design/` 与 `07_epitope_aidd/7B_antibody_validation/`。7A result 获批后才能下单 synthesis；7B result 获批后才能开始 conjugation。这样避免 Stage 8 依赖尚未被任何上游 Stage 产生的实测 binder evidence。

## 14. Stage 8 — ADC Platform Assembly 与 Construct Design

目的：用可获得的成熟平台把已验证到足够程度的 binder 转为可制造、可质控、可测试的 ADC construct。

| 项目 | 定义 |
|---|---|
| 输入 | Stage 7B `ADC_GRADE_HIT` ref；BinderCandidate sequences；实测 binding/epitope/internalization/trafficking/developability evidence；target density 与 heterogeneity；payload-cell-state hypothesis；platform capability/quality agreement；linker-payload/conjugation patent triage；human conjugation authorization |
| 设计轴 | antibody format/Fc；conjugation site；linker release；payload class；DAR；hydrophobicity；stability；bystander requirement；cross-resistance；manufacturability；platform licence/FTO |
| 输出 | `adc_design_matrix.tsv`、`platform_selection.md`、`construct_specifications.yaml`、`linker_payload_fto_triage.tsv`、`manufacturing_qc_plan.yaml`、`manufactured_lot_manifest.json`、batch-release QC refs、`ADCConstruct` refs |
| 放行条件 | 至少一个平台已实际承接并返回可追溯 lot；每个 construct 的 binder/linker/payload/site/DAR/spec 可追溯；基础 identity/purity/DAR/free-payload/aggregation release QC 合格；成熟组件优先；专利和许可边界已审查；构型有明确 failure hypothesis |
| STOP/BLOCK | binder 没有 Stage 7B `ADC_GRADE_HIT` 就组装；payload 与 disease state/既往治疗明显不匹配；平台不能提供所需 chemistry；组合 claims 无 plausible design-around；同时引入多个未验证高风险组件 |
| 不得声称 | 计算组合等于已制造 ADC；平台可用等于 construct 已满足质量标准；AI triage 等于 FTO clearance |

Linker-payload 的正式选择和专利避让发生在这里，而不是 Stage 2 的 target universe 生成阶段。

## 15. Stage 9 — Progressive Validation 与 ADC Hit Decision

目的：用最少但高信息量的实验逐层消除关键 residual uncertainty；每层都允许停止。

| 子阶段 | 输入 | 最小输出 | 通过/停止重点 |
|---|---|---|---|
| 9A Construct identity + binding retention | Stage 8 release-qualified construct、matched unconjugated binder、target/negative controls | construct identity/QC trace、binding retention、cell-surface binding、specificity | 偶联后 binding/specificity 丢失即 STOP/ITERATE；不得用 Stage 7B binder 结果替代 construct 测量 |
| 9B Delivery retention | release-qualified construct + target-positive/negative cells | ADC internalization kinetics、trafficking/lysosomal delivery、antigen-density response、与 unconjugated binder 的差异 | 偶联后只结合不递送，或 delivery 明显丢失，不得进入 ADC hit |
| 9C Extended conjugate QC | Stage 8 release-qualified constructs | 加速/血浆稳定性、payload release、批间一致性 | 质量或稳定性不达标先修构型，不用 efficacy 掩盖 CMC 缺陷 |
| 9D In-vitro ADC activity | qualified constructs + state-matched models | target-dependent killing、density threshold、bystander、payload sensitivity、resistance controls | killing 必须依赖 target/construct；游离 payload 对照不可缺 |
| 9E Translational models | refractory mCRC cell/PDO/organoid/co-culture models | patient-state coverage、heterogeneity、normal-cell selectivity、combination hypothesis | 模型必须与 Stage 1 territory 匹配 |
| 9F Focused in-vivo POC | selected hit(s) + `in_vivo_cost_escalation_decision.json` | exposure、efficacy、tolerability、PD/biomarker、failure analysis | 只做 ValueInflectionPlan 要求且经人类批准的最小 POC，不惯性扩张 |

Stage 9 最终输出：

```text
adc_hit_decision_package/
├── construct_identity_and_qc
├── evidence_graph
├── gate_results
├── supporting_opposing_conflicting_unknown
├── failure_mode_analysis
├── ip_fto_triage
├── biomarker_and_patient_selection
├── reproducibility_manifest
└── human_decision_GO_ITERATE_STOP
```

只有具有版本化实验证据的 construct 才能称为 `ADC hit`。预测候选、设计 spec 或已下单 construct 都不是 ADC hit。

## 16. Stage 间最小 I/O 接口

| From | To | 唯一允许的承重输入 |
|---|---|---|
| Stage 0 | Stage 1–4 | approved source/snapshot/policy refs |
| Stage 1 | Stage 2–5 | anchored ClinicalHypothesis 与 patient territory ref |
| Stage 2 | Stage 3 | provenance-complete ADCdb target prior universe |
| Stage 3 | Stage 4 | sponsor-relative routed target refs，不是科学 PASS |
| Stage 4 | Stage 5 | Atlas evidence refs，不是 Gate result |
| Stage 5 | Stage 6 | reviewed T12 Target Opportunity decision |
| Stage 6 | Stage 7A | `ProgramCommitmentReview@0.2.0` 的 `SELF_DEVELOP`/`CO_DEVELOP`/`PARTNER_NOW` + `EXTERNAL_HANDOFF_REQUIRED` + `SponsorFitAssessment@0.1.0` ref + 完整 ValueInflectionPlan + human authorization + `aidd_execution_decision.json`；其余结果必须为 `BLOCKED_NO_COMMITMENT` |
| Stage 7A | Stage 7B | human-approved diverse synthesis panel + epitope/IP refs + reproducible AIDD manifest；prediction 不是 binder |
| Stage 7B | Stage 8 | experimental `ADC_GRADE_HIT` ref + binding/epitope/internalization/trafficking/developability refs + human conjugation authorization |
| Stage 8 | Stage 9 | physically realized construct refs + QC plan |
| Stage 9 | final | evidence-backed human `GO/ITERATE/STOP` decision |

任何 Stage 不得通过复制下游字段、预填 PASS 或自然语言暗示绕过上游结果审核。

### 16.1 最小机器可读 artifact contract

下表定义的是每个输出投影的最低字段，不复制或取代现有 authoritative contract、Gate RuleBook 或外部 evidence store。后续 Stage contract PR 可以增加字段，但不能删除这些 provenance 和 decision-boundary 字段。

| Stage artifact | 最低字段 |
|---|---|
| `source_admission_bundle.json` | source_id；admission_record_ref；snapshot_id；cutoff；checksum；licence/access；field whitelist；identity policy ref；review status |
| `clinical_hypothesis.json` | clinical_hypothesis_id；disease/stage/biomarker；refractory definition；line/prior therapies；metastatic context；unmet need；intended benefit；endpoint class；patient-selection hypothesis；source refs；review status |
| `adcdb_target_universe.tsv` | target_id；canonical gene/protein；aliases；n assets/clinical assets/sponsors/indications；highest credible stage；active/terminated counts；antibody/internalization/delivery refs；unknowns；source record refs |
| `target_crowding_matrix.tsv` | target_id；global/CRC crowding evidence；active/late-stage/approved programme counts；sponsor concentration；same-territory occupancy；epitope crowding；termination/readout refs；unknowns |
| `target_ip_triage.tsv` | target_id；target/antibody/epitope claim refs；design-around plausibility；preliminary risk；counsel-required flag；unknowns；evidence refs；不得写 `FTO_CLEARED` |
| `target_route_decisions.tsv` | target_id；crowding ref；IP triage ref；early platform feasibility；differentiation hypothesis；sponsor route；fatal blocker；human reviewer；decision rationale |
| `target_atlas_evidence.tsv` | target_id；malignant expression/specificity；patient/tumor-cell prevalence；heterogeneity/spatial coverage；refractory-state evidence；normal-tissue risk；protein/surface support；conflicts；unknowns；evidence refs |
| `gate_results.tsv` | target_id；gate_id/version；status；score/confidence when defined；fatal flag；supporting/opposing refs；missing information；recommended validation；human reviewer；T12 disposition ref |
| `program_commitment_review.json` | target decision ref；sponsor fit ref；commitment outcome；downstream status；ValueInflectionPlan ref；stop conditions；capability sources；human authorization ref |
| `epitope_opportunities.tsv` | target_id；epitope_id；residue/structural patch；structure ref；surface accessibility；glycosylation/PTM risk；membrane proximity；known-binder/patent overlap；internalization hypothesis；uncertainty；decision |
| `binder_ranking.tsv` | target_id；epitope_id；candidate_id；sequence refs；model/version/seed；predicted epitope engagement；structure confidence；developability/specificity/cross-reactivity proxies；family cluster；uncertainty；decision |
| `antibody_hit_validation.tsv` | target/epitope/candidate/lot IDs；identity/QC；binding and cell-binding status；specificity；epitope status；internalization/trafficking；cross-reactivity；developability；experimental refs；overall status |
| `adc_design_matrix.tsv` | target/binder/design IDs；conjugation method/site；linker/payload classes；DAR target；bystander hypothesis；platform/source/access；preliminary IP risk；rationale；design decision |
| `manufactured_lot_manifest.json` | design/construct/lot IDs；platform/manufacturer refs；binder/linker/payload/site/DAR identity；manufacturing date；chain of custody；release-QC refs；artifact checksum；release status |
| `adc_hit_decision_package` | construct refs；release/extended QC；binding/delivery retention；target-dependent activity；controls；reproducibility；translational evidence；failure analysis；human `GO/ITERATE/STOP` |

每一行或 evidence object 还必须携带适用的通用 envelope：

```text
pipeline_run_id
pipeline_version
stage_id
artifact_schema_version
record_id
source_snapshot_refs
source_record_refs
code_commit
software_or_model_versions
config_checksum
artifact_checksum
created_at
created_by
evidence_refs
review_status
```

### 16.2 Failure、blocker 与 pipeline error 分类

失败必须可学习、可路由，不能只留一个 `FAIL`。至少使用以下分类：

```text
SOURCE_ADMISSION_BLOCK
IDENTITY_RESOLUTION_BLOCK
CLINICAL_TERRITORY_BLOCK
ADC_PRECEDENT_INSUFFICIENT
CRC_CONTEXT_FAIL
NORMAL_TISSUE_FAIL
SURFACE_ACCESS_FAIL
INTERNALIZATION_FAIL
TRAFFICKING_FAIL
COMPETITION_ROUTE_BLOCK
IP_RISK_BLOCK
PLATFORM_ACCESS_BLOCK
EPITOPE_FAIL
AIDD_PIPELINE_ERROR
BINDER_BINDING_FAIL
BINDER_DEVELOPABILITY_FAIL
ADC_CONJUGATION_FAIL
ADC_MECHANISM_FAIL
PAYLOAD_MISMATCH
TRANSLATIONAL_FAIL
EVIDENCE_INSUFFICIENT
PIPELINE_ERROR
```

`BLOCK` 表示当前不能继续，不等于科学 KILL；`PIPELINE_ERROR` 表示流程/工具失败，不得转成资产结论；`EVIDENCE_INSUFFICIENT` 保持未知并进入补证或 HOLD。每条记录必须有 `failure_class`、`failed_stage`、`affected_claims`、`evidence_refs`、`recoverable`、`recommended_next_action`。

### 16.3 成本跃迁的人类审批点

| 成本跃迁 | 必须的人类 decision artifact | 未获批时 |
|---|---|---|
| Stage 6 -> 7A AIDD execution | asset-directed commitment + `aidd_execution_decision.json` | `BLOCKED_NO_COMMITMENT` |
| Stage 7A -> 7B synthesis/experimental validation | `synthesis_panel_decision.json` | 不下单、不生成虚构实验结果 |
| Stage 7B -> 8 conjugation/manufacturing | `conjugation_authorization.json` + `ADC_GRADE_HIT` ref | 不组装 ADC |
| Stage 9E -> 9F focused in-vivo | `in_vivo_cost_escalation_decision.json` + ValueInflectionPlan criterion | 不惯性扩张到动物实验 |

这些 decision artifact 只授权指定的一次成本跃迁，不授权后续 Stage，也不替代 result review。

## 17. 全局验收规则

每个 Stage 的结果 PR 必须同时回答：

1. Execution correctness：输入、代码、输出、checksum、异常与复现是否正确；
2. Method validity：方法是否适合当前问题，统计单位和 proxy 是否合理；
3. Scientific validity：结论是否越过 RNA→protein→surface density→internalization→delivery→efficacy 的证据边界；
4. Project alignment：是否减少 indication-transfer 的关键 residual uncertainty；
5. Operational usefulness：是否真的能决定下一实验、合作、停止或资产动作；
6. Human acceptance：领域专家、平台/CRO、专利律师或人类负责人是否在相应边界签字。

所有 target/epitope/construct 必须显式保留 supporting、opposing、conflicting、unknown 和 missing-information refs。未检索到证据不能写成反对证据；`UNKNOWN` 不能静默转换为 PASS、FAIL 或零分。

## 18. 当前进度与阻断

### 18.1 权重定义

| Workstream | 权重 | 100% 完成标准 | 当前状态 | 当前 blocker | 下一里程碑 |
|---|---:|---|---|---|---|
| Pipeline 设计与治理 | 10% | 本设计通过 PR/ChatGPT 审核并合并 | approved baseline 0.1.0；0.2.0 draft pending review，10/10 | 0.2.0 尚未 `APPROVE` | 设计修订 PR |
| Source admission 与快照 | 10% | ADCdb/Atlas/专利/临床来源可审计并冻结 | not started | `SRCADM-02` ADCdb 未准入 | Stage 0 contract PR |
| Refractory territory lock | 10% | ClinicalHypothesis anchored | not started | 需把人类约束固化为版本化输出 | Stage 1 contract/run |
| Target prior 与 crowding/IP triage | 15% | ADCdb universe 和 sponsor-relative route 结果获批 | not started | 依赖 Stage 0/1 | Stage 2/3 |
| Atlas transfer + T-chain | 20% | Atlas 包和 T0–T12 target decision 获批 | not started | 依赖 dataset admission 与 analysis plan | Stage 4/5 |
| Epitope + AIDD binder | 15% | 有真实工具输出和实验可验证 binder package | not started | 依赖 Program Commitment 与工具/平台 | Stage 6/7 |
| ADC assembly | 10% | 至少一个 construct 被实际制造并 QC | not started | 依赖 binder 实验证据与平台协议 | Stage 8 |
| Progressive validation | 10% | 至少一个 ADC hit 有 `GO/ITERATE/STOP` 决策包 | not started | 依赖 wet-lab/CRO 资源 | Stage 9 |

当前总体进度：`10% → 10% (+0%)`。获批的 0.1.0 已完成设计与治理里程碑；0.2.0-draft 只关闭接口和 schema 缺口，不增加科学或运行完成度。它获批前以 0.1.0 为有效基线。

- 工程/设计治理完成度：`10%`
- 科学就绪度：`0%`（尚未运行 ADCdb、Atlas 或 Gate）
- 实验/运营就绪度：`0%`（尚未落实 AIDD 工具执行、ADC 平台或 CRO）

### 18.2 当前最小下一步

1. 审核并合并本 design-only PR；
2. 单独建立 Stage 0 contract PR，完成 `SRCADM-02` ADCdb source admission 与 snapshot freeze；
3. Stage 0 结果获批前，不运行 target universe，不选择靶点。

## 19. 本设计明确不授权

- 不运行或读取 ADCdb 内容来产生新结果；
- 不执行 Atlas 分析、Gate 评分、target ranking 或资产推荐；
- 不生成 epitope、抗体序列、结构或 linker-payload 组合；
- 不联系或委托 ADC 平台/CRO；
- 不下载数据或把数据、cache、result、数据库、模型权重写入 StelligenOS；
- 不修改 45-Gate 拓扑、生命周期、核心对象或既有合同；
- 不以本设计文件替代后续每个 Stage 的 contract PR、result PR 和人类决策。
