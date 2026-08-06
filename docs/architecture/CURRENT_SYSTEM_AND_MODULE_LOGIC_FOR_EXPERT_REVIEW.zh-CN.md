# StelligenOS 当前设计架构与模块逻辑（专家审核版）

## 0. 版本与审核基线

- 文档 ID：`CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW`
- 当前文档版本：`v3-draft`
- 架构审核基线：`STELLIGENOS-ARCH-2026.08.06-v3-draft`
- 仓库基线：`main@8aa7e87`
- 基线日期：`2026-08-06`
- 版本状态：`PENDING_EXPERT_REVIEW`
- 规范路径：本文件固定为最新版本，不在文件名中写版本号。
- 已冻结快照：`docs/architecture/versions/`；当前只有经 PR #42 批准的 `v1`。

StelligenOS 当前没有一个覆盖全部模块的单一软件 SemVer。核心合同、Gate
拓扑和 GenModule 各自独立版本化。因此，本节的 `v3-draft` 是**架构说明文档
版本**，不是新的运行时发布标签，也不改变任何现有合同版本。

本版相对旧 `v2-draft` 的主要变化：

1. 纳入已经合并的 CRC ADC Pool Level 01、输入绑定、EVGAP-01/02 契约和 Preview 状态。
2. 纳入 Public-Evidence Target Safety Pre-screen `0.4.0`。
3. 纳入 Biotech 基础设施目录和 Cancer Patient-Anchored Data Infrastructure。
4. 明确区分已实现逻辑、合同壳、外部运行和仅登记扩展。
5. 记录截至 2026-08-06 的开放 PR 与真实阻断，不把活动分支当成 `main`。

## 1. 一句话定义

StelligenOS 是一个面向 biotechnology asset generation 的**软件操作系统实现**：
它把临床问题、靶点机会、证据、Gate、抗体/ADC 设计、尽调和人类决策组织成
版本化、可审计、可逐步推进的流程。

它不是数据库，也不是一个可以自行宣布资产成功的自治代理。真实数据、证据、
模型权重、运行结果、法律意见、投资结论和生命周期状态全部由外部工作区持有；
仓库只保存对象、合同、端口、规则、代码、测试和文档。

## 2. 系统最终目标与核心研发单元

系统目标是把未满足临床需求逐步转化为可验证、可工程化、可开发和可交易的
生物技术资产。当前核心链路是：

```text
Clinical unmet need
  -> ClinicalHypothesis
  -> Target opportunity
  -> Binder / ADC product hypothesis
  -> BinderCandidate
  -> ADCConstruct
  -> LeadSeries
  -> DevelopmentCandidate
  -> Asset
```

早期研发单元不再是一次性永久锁死的 `indication-endpoint-target` 三元组，而是：

```text
Target
x Anchor Clinical Context
x Intended Benefit / Product Hypothesis
```

精确 endpoint、最终 biomarker cutoff、CDx 和注册标签按开发成熟度递进锁定。
系统支持三种入口：

- `mature-target-first`：成熟 target 先进入，再补临床上下文和产品假设。
- `target-context-co-selection`：target 与临床上下文协同形成，属于默认入口。
- `clinical-problem-first`：临床问题和 intended benefit 先形成，target 后补。

## 3. 不可破坏的设计原则

1. **临床与产品假设协同。** Target 不能脱离人群、治疗场景和 intended benefit 被孤立排序。
2. **递进锁定。** 早期 endpoint class、protocol endpoint 和 observed outcome 是三种不同对象。
3. **证据与判断分离。** Retrieval、assertion、expert review、Gate output 和 human decision 不得互相冒充。
4. **未知不是失败。** `unknown`、`null`、`NOT_EVALUATED` 和 `UNRESOLVED` 不得自动转换为 0、FAIL 或安全。
5. **支持与反对证据并存。** Supporting、opposing、conflicting、missing 和 provenance 都必须保留。
6. **规则和模型不直接改写决策。** Rule/Model 只能产生受限输出，不能自行改 Gate 分数、状态或 Profile。
7. **状态不自动晋级。** 脚本成功、模型高分、单个 Gate 通过或模块完成都不构成生命周期晋级。
8. **Fatal-first 先于加权平均。** 明确致命风险不能被其他高分抵消。
9. **外部引用优先。** 跨边界对象使用版本化 `external:` reference，不把业务记录复制进仓库。
10. **全过程可审计。** 输入版本、合同、代码提交、来源、缺失、审核和人类决定均须可追溯。

## 4. 总体软件架构

### 4.1 六个软件层

| 层 | 当前职责 | 当前实现位置 |
|---|---|---|
| Operating System | 统一架构、对象、合同、治理和 boot 边界 | `docs/architecture/`、`src/repository/boot.py` |
| Lifecycle | 约束合法阶段和递进 lock，不持久化状态 | `src/lifecycle/` |
| Capabilities | 定义机会生成、证据、Gate、排序、路线等端口 | `src/capabilities/` |
| Cross-cutting | Knowledge Ledger、Model governance、IP/FTO、DD、Portfolio | `src/cross_cutting/` |
| Objects | 定义核心对象身份，不保存对象记录 | `src/objects/`、`src/contracts/core_objects.yaml` |
| Repository implementation | 连接外部运行时和外部工作区 | `src/repository/` |

依赖方向必须从模块实现指向内核合同，内核 `src/` 不得反向依赖
`genmodules/` 或 `extensions/`。这条边界已有测试保护。

### 4.2 四阶段生命周期

```text
Opportunity Generation
        -> Opportunity Validation
        -> Asset Generation
        -> Asset Development
```

- `Opportunity Generation`：形成 ClinicalHypothesis、候选 target 和初始证据需求。
- `Opportunity Validation`：执行 target opportunity Gate、证据充分性和 T12 决策。
- `Asset Generation`：选择 existing-binder 或 de novo 路线，形成 binder/ADC asset package。
- `Asset Development`：推进 lead series、development candidate、DD、IP/FTO 和交易准备。

状态机只验证相邻合法转移，不保存状态，也不自动晋级。

### 4.3 八个核心对象

`core_objects@1.1` 当前登记：

1. `Opportunity`
2. `ClinicalHypothesis`
3. `TargetHypothesis`
4. `BinderCandidate`
5. `ADCConstruct`
6. `LeadSeries`
7. `DevelopmentCandidate`
8. `Asset`

每个对象至少具有 `object_type`、`object_id` 和 `schema_version`。对象实例仍在
外部系统中，仓库内只有类型和身份合同。

### 4.4 ClinicalHypothesis 递进锁定

锁定顺序是：

```text
exploratory
  -> provisional
  -> anchored
  -> product-locked
  -> protocol-locked
  -> regulatory-locked
```

每次只允许单步前进；lock state 表示假设成熟度，不表示 Gate 已通过。正式路径
需要 `clinical_hypothesis_ref`，旧精确 tuple 路径只能显式声明
`legacy_compatibility=True`。

## 5. Capability 与运行边界

内核登记 9 类 OS capability：Opportunity Discovery、Knowledge Mining、Rule
Learning、Evidence Extraction、ADC Design、Binder Engineering、Patent Analysis、
Due Diligence、Portfolio Management。

当前代码进一步提供以下数据无关端口：

- Opportunity generation
- Clinical-frame pipeline
- Target-candidate generation
- Early T-Gate reduction
- Endpoint-biology completion
- Evidence independence / adversarial review / readiness
- T12 decision and opportunity ranking
- Binder/ADC route selection
- End-to-end pilot and closure
- Architecture freeze/release
- External runtime

这些端口的含义是“外部实现必须遵守什么”，不是“仓库已经内置全部数据和科学
执行器”。`boot()` 只返回静态架构计划和外部引用，状态是
`ready_for_external_runtime`；它不会加载数据、运行模型或写结果。

## 6. Gate 系统

### 6.1 冻结拓扑

Gate 系统合同为 `gate_system@0.1.0`，拓扑架构版本为 `0.2.0`，共 45 个 Gate：

| Gate chain | 数量 | 逻辑范围 |
|---|---:|---|
| Target Opportunity | 13 | T0 临床上下文到 T12 target opportunity decision |
| Product Realization | 16 | 产品目标、epitope、binder、internalization、payload、PK/TI 到整合产品决策 |
| Commercial Executability | 16 | 商业阈值、监管、竞争、FTO、专利、access、交易准备 |

Target chain 的逻辑顺序是：临床上下文与 endpoint class、endpoint-driving
population、target-population mapping、干预因果、覆盖与逃逸、治疗诱导状态、
净 endpoint benefit、肿瘤表面可得性、肿瘤内可及性、抗体依赖内吞、epitope
可实现性、on-target therapeutic index，最后由 T12 综合决定。

### 6.2 Gate 输入输出语义

Gate 通过外部 envelope 接收 candidate、ClinicalHypothesis、证据、上游结果、
graph context 和 run context。输出包括 score、confidence、status、rationale、
evidence、missing information 和 validation recommendation。

重要约束：

- `score=None` 是未知，不是 0。
- Gate output 不自动写入仓库。
- Historical Rule 不能自动更改 score、status 或 Profile。
- T12 结果不自动创建 Asset，也不自动切换生命周期。
- Gate 仍需要外部运行时和显式审核。

当前存在一个需专家注意的版本一致性问题：`src/contracts/gate_system.yaml` 仍把
source envelope 写为 `2.0.0`，而 `src/capabilities/gates.py` 的当前默认合同版本
是 `2.1.0`。现有测试通过，但两处声明需要在独立治理任务中统一，本文不擅自
修改合同。

## 7. GenModule 与目录模块

当前有 7 个模块区域，其中 6 个具有 `module.yaml`；
`gen_indication_endpoint_target` 是当前被登记为 active 的纯合同包，但尚无模块
manifest。这一差异应由专家确认是否需要统一注册方式。

### 7.1 `gen_indication_endpoint_target@0.1.0`

用途：定义受约束的 ADC clinical context、endpoint class 和 target opportunity
生成合同。

它包含 ClinicalFrame、TargetCandidate、EvidenceRecord、AdversarialReview、
TargetOpportunityHandoff 和 ClinicalHypothesis 相关结构，但**不包含 generator、
evidence collector、ranking engine、Gate evaluator、runner 或数据库**。

逻辑：外部实现先形成 anchor clinical context 和 intended benefit，再生成 target
候选，保留 missing/unknown，经过证据和对抗审核后交给 T-chain。

### 7.2 `assetgenos_catalog@0.1.0`

状态：`migrated_contracts_only`。从 AssetGenOS 迁入：

- 7 个共享合同
- 45 个 Gate 定义
- 59 个 Model 定义
- 53 个 Profile 定义

它是软件目录，不是 Gate runtime。模型权重、runner、数据、结果、治理记录和
work package 均未迁入仓库。

### 7.3 `gate_model_rule@0.1.0`

用途：保存历史 Rule 的身份、引用和审计合同，不执行自然语言规则。

规则实例、case、数据库和生成结果保持外部；Rule 不能自动改分、改状态或绑定
Profile。它的存在是为了迁移可追溯性，不是第二套 Gate 系统。

### 7.4 `target_safety_therapeutic_window_prescreen@0.4.0`

用途：用已经标准化的公共证据 claim 做 ADC target-level 安全预筛，不宣称
product-specific therapeutic window。

六个 evidence axis：正常组织表达、表面可达性、抗原密度、soluble antigen /
shedding / sink、既有 modality 毒性、组织后果与可恢复性。

逻辑为 fatal-first：

- `KILL`：同一 hazard context 内满足明确致命条件。
- `HOLD`：关键证据未知、冲突、未覆盖或非致命 material risk 未解决。
- `CONDITIONAL_GO`：所有 material risk 都被相关 differential 明确覆盖。
- `GO`：六轴完整、无 material risk、无冲突；仍不等于临床安全。

合同强制 claim/evidence reference 唯一且集合一致，mitigation 只能指向同请求中
的 `SUPPORTS_RISK` claim，避免集合压缩造成错误放行。

### 7.5 `antibody_binder_asset_engineering@0.4.0`

用途：把已有 binder 工程化成 ADC carrier/asset package。

它有 16 个内部步骤，映射到冻结的 14-stage 外部路线。核心不是一个总分，而是
两条不可互相补偿的轴：

- Track A：序列/结构、humanization、liability 和 developability。
- Track B：结合、内吞、运输和 payload delivery 的版本化实验 phenotype。

两轴只通过 Pareto dominance 选择。序列干净不能补偿“不内吞”，高内吞也不能
掩盖严重分子 liability。模块还提供 evidence graph、failure mode、信息增益实验
排序和 cross-asset retrieval。外部结构预测默认关闭，需要显式授权。

### 7.6 `epitope_conditioned_de_novo_antibody_discovery@0.1.0`

用途：从 antigen 和人为定义的 epitope 约束出发，形成 de novo antibody
discovery package。

15 步覆盖 target biology、antigen/epitope engineering、IP/FTO 引导、结构准备、
negative design、de novo design、计算排序、多样性、实验设计、结构验证、亲和力
成熟、ADC readiness、专利包和 asset report。

外部科学工具默认不自动调用；工具不可用时只能输出约束和实验计划，不能虚构
真实抗体序列、结合或 ADC readiness。

### 7.7 `biotech_asset_due_diligence@0.1.0`

用途：对外部资产 artifact 建立可审计、modality-neutral 的尽调链。

```text
Asset -> AssetVariant -> AssessmentRun -> ArtifactRef
  -> EvidenceSource/Claim -> Observation -> Hypothesis
  -> FailureMode -> DecisionUncertainty -> ExperimentBranch
  -> SystemRecommendation -> HumanDecision
```

`SystemRecommendation` 与 `HumanDecision` 严格分离。模块不能声称法律 FTO、
临床安全、临床有效、portfolio 排名或最终资本配置。

## 8. Cross-cutting 逻辑

- **Knowledge Ledger**：以外部引用组织 evidence、rule、hypothesis、experiment、failure、decision、calibration 和 lesson。
- **Model lifecycle**：使用 `model_id@SemVer`；注册、权重、验证、晋级和退役由外部治理系统承担。
- **IP/FTO**：返回外部 decision package，不在仓库保存法律结论。
- **Stage-aware DD**：同一资产在不同生命周期阶段使用不同问题和证据标准。
- **Portfolio**：只定义端口，不保存估值、资本分配或组合决策。
- **Audit/versioning**：每次运行记录 input、contract、model/Gate、evidence、review 和时间戳。

## 9. Biotech 与患者数据基础设施

仓库已经登记可复用的外部 provider 方向，但尚未接通完整 provider runtime：

- 文献：Europe PMC、PMC OA/BioC
- 临床试验：ClinicalTrials.gov API、AACT
- Target-disease：Open Targets
- 单细胞：CELLxGENE Census
- 正常组织：GTEx、Human Protein Atlas
- 癌症组学：GDC/TCGA、cBioPortal、DepMap
- 蛋白结构：UniProt、PDB、AlphaFold DB、InterPro
- 化学：ChEMBL、PubChem、BindingDB
- 专利：EPO OPS、PATENTSCOPE、Lens
- 监管：FDA、EMA 和公司披露

Cancer Patient-Anchored Data Infrastructure 采用四层证据空间：

```text
P1 Direct Patient Observation
  -> P2 Patient-Derived Living Models
  -> P3 Model Perturbation
  -> P4 Clinical Intervention and Outcome
```

TCGA、HTAN、CPTAC、GENIE 和 ICGC/ARGO 属于直接患者观测；HCMI、PDO、
PDX 和低传代 culture 属于患者来源模型；DepMap、GDSC、PRISM 等主要属于模型
扰动；真实 clinical intervention/outcome 单独作为 P4。数据库名不能决定证据
强度，患者距离和因果强度必须分开记录。

当前这部分是基础设施目录和未来 provider 设计，不是已下载数据，也不是已经
完成的患者数据分析。

## 10. CRC ADC Pool Level 01 当前状态

### 10.1 已进入 `main` 的正式内容

- Level 01 定义与三把 eligibility lock 已冻结。
- 输入绑定固定为 9 个 clinical contexts、41 个 targets、369 个原始 pair。
- EVGAP-01 surface-localization extraction contract 已合并。
- EVGAP-02 CRC linkage extraction contract `0.1.0` 已合并。
- Level 01 Preview revision 2 已合并，但状态是
  `PROVISIONAL_NOT_AUTHORIZED_FOR_ADVANCEMENT`。

Preview 当前结果：

| 指标 | 当前值 |
|---|---:|
| raw clinical contexts | 9 |
| raw targets | 41 |
| raw matrix | 369 pairs |
| eligible context | 1 |
| provisional surface-eligible targets | 22 |
| provisional eligible universe | 22 pairs |
| active for Level 02 | 0 |
| excluded candidates | 0 |

`active=0` 不表示没有候选，而表示没有 pair 同时通过三把锁。HOLD 是缺证据，
不是负面结论。当前不得生成 `ADC_POOL_LEVEL_01_ACCEPTED`。

### 10.2 截至 2026-08-06 的开放工作

- PR #62：把 EVGAP-02 契约修订为 `0.2.0`，将已有运行降级为 retrieval
  candidates；979 条 retrieval candidates、0 条 linkage assertions，369 pairs
  全部保持 DEFER/HOLD。该 PR 未合并，因此不是当前 `main` 合同。
- PR #63：执行 SRCADM-01 surfaceome source admission audit，结论为
  `admissible_with_conditions`，但 PR 明确没有自行授予 admission，也没有解除
  EVGAP-01。
- PR #55：旧 target-safety PR 仍开放且 merge state 为 DIRTY；其修订版本已由
  PR #56 合并，属于应关闭的历史重复 PR，不代表当前模块缺失。

### 10.3 已知 CRC 阻断

1. Surfaceome snapshot 尚未完成正式 admission 引用绑定，EVGAP-01 未解除。
2. EVGAP-02 当前只有 retrieval，没有可支撑 LOCK-03 的结构化 assertions。
3. 41-target 轴含至少四个不可直接消歧实体：`Undisclosed`、`EDBN`、`AG7`、`CA19-9`。
4. Accepted Level 01 pool 尚未形成，不能进入 Level 02、T-Gate scoring 或资产生成。
5. 尚无被批准的 CRC pair 进入 binder/ADC generation。

## 11. Extensions：已登记但未进入内核

扩展只能依赖内核，内核不能依赖扩展；扩展不能改 Gate 或生命周期状态。

| ID | 扩展 | 状态 | 当前含义 |
|---|---|---|---|
| EXT-01 | ground-truth learning loop | `shell_only` | 等真实项目结局后再治理 |
| EXT-02 | dynamic gate context | `partially_absorbed` | v5 已吸收核心概念，剩余范围未治理 |
| EXT-03 | asset search engine | `shell_only` | 仅登记搜索能力方向 |
| EXT-04 | stop rule | `active_design` | 有合同和测试，尚未接真实运行 |

Backlog 还包括 evidence independence、动态剪枝、早期 DD、commercial refresh、
success probability、resource-aware planning 和 portfolio learning。登记不等于批准。

## 12. 系统实际运行逻辑

```text
Human strategy + external evidence providers
  -> BootRequest（只验证外部引用）
  -> Clinical unmet need / entry mode
  -> ClinicalHypothesis（递进 lock）
  -> target/context enumeration
  -> evidence retrieval
  -> structured assertion + provenance
  -> expert/adversarial review
  -> T0-T11 Gate evaluation
  -> evidence readiness
  -> T12 decision/ranking
  -> explicit human handoff
  -> route selection
       -> existing-binder engineering
       -> epitope-conditioned de novo discovery
  -> ADC product / lead / candidate
  -> stage-aware DD + IP/FTO + portfolio package
  -> explicit HumanDecision
```

每个箭头传递版本化对象或外部 artifact reference。任何单个模块只能完成自己的
合同职责，不能因为“运行成功”就跳过证据、Gate、审核或人类决定。

## 13. 现在能运行什么，不能运行什么

### 可以运行或验证

- data-free OS boot 和架构 smoke test。
- 8 类对象、4 阶段生命周期、ClinicalHypothesis lock、45 Gate 拓扑和 envelope 校验。
- 各 capability 的输入输出合同与外部引用边界。
- Existing-binder pipeline 的大部分软件逻辑和受控外部工具调用。
- De novo route 的流程骨架与外部 package 生成。
- Target-safety `0.4.0` 的纯内存、确定性预筛，只要外部提供合格 claims。
- CRC Level 01/EVGAP 合同、Preview 和机器可读验证。
- 当前 `main` 的 338 项单元测试和 repository boundary check。

### 不能声称已经完成

- 没有一个仓库内数据库或统一 data lake。
- 公共 provider 目录不等于 provider 已全部接通。
- `gen_indication_endpoint_target` 不会自行生成 pair。
- AssetGenOS 目录不执行 45 个 Gate。
- Model YAML 不等于模型已经加载、校准或运行。
- Level 01 Preview 不等于 Accepted pool。
- Retrieval hit 不等于 evidence assertion。
- Target safety GO 不等于产品 therapeutic window。
- Binder/de novo package 不等于实验验证或 development candidate。
- SystemRecommendation 不等于 HumanDecision。

## 14. 当前实现成熟度

| 范围 | 成熟度 | 说明 |
|---|---|---|
| 架构内核 | 已实现并测试 | 对象、生命周期、端口、边界和 boot 可运行 |
| Gate/Model/Profile 目录 | 合同已迁移 | 45/59/53；真实运行在外部 |
| ClinicalHypothesis v5 | 已进入内核 | 递进锁定和三入口已实现 |
| Opportunity generation | 合同完整度较高 | 真实 generator/provider 尚在外部 |
| Existing-binder route | 可运行软件逻辑较多 | 依赖外部输入和科学工具 |
| De novo route | 流程骨架可运行 | 真实序列设计和验证依赖外部工具/实验 |
| Target safety pre-screen | 确定性引擎已实现 | 依赖外部标准化 evidence claims |
| Due diligence | 合同和实体链已实现 | 不产生最终人类决策 |
| Biotech/patient infrastructure | 已登记 | 尚未形成完整 provider adapter 层 |
| CRC Level 01 | Preview 已形成 | Accepted pool 尚未形成 |
| 端到端真实资产生成 | 未完成 | 尚无批准 pair 贯通全部 Gate 与生成路线 |

## 15. 当前需要专家审核的问题

1. `ClinicalHypothesis` 的三种入口和递进 lock 是否足以覆盖真实 ADC 开发路径。
2. T0-T12 的顺序、Hard Gate、fatal-first、HOLD 和 T12 handoff 是否合理。
3. Gate envelope `2.0.0`/`2.1.0` 版本漂移应如何统一。
4. `gen_indication_endpoint_target` 是否应补正式 `module.yaml`，还是继续作为内核共享合同包。
5. 患者直接观测、患者来源模型、模型扰动和临床干预的 P1-P4 分层是否足够。
6. Evidence independence 应按 primary source、dataset lineage 还是实验批次定义。
7. Retrieval -> assertion -> disposition 三层是否足以阻止检索命中被误当成证据。
8. CRC target 轴中非标准实体应在何处消歧，是否需要重开 41/369 冻结计数。
9. EVGAP-01/02 解除后，Level 01 Accepted 的最低人工审核门槛是什么。
10. Existing-binder 双轴 Pareto 和 de novo 15-stage 路线是否符合实际实验决策。
11. 哪些判断必须专家签字，哪些可由模型辅助，哪些才允许确定性自动化。
12. 何时应把 stop rule、evidence independence 和 resource-aware planning 纳入内核。

## 16. 版本维护规则

1. 规范路径保持不变，下一次实质更新升为 `v4-draft`。
2. 每个版本必须记录 repository baseline、日期和审核状态。
3. 只有获得明确批准的版本才复制到 `docs/architecture/versions/` 形成只读快照。
4. 未批准 draft 被新 draft 取代时不补造“已批准快照”。
5. 架构文档必须分别标记 `implemented`、`contract-only`、`external runtime`、
   `planned` 和 `pending review`，不得用一个“已完成”概括所有层。
6. 架构更新不得顺带改变 Gate、合同或科学决策；发现不一致只登记为审核问题，
   另立治理任务修复。
