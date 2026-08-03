<!-- FROZEN SNAPSHOT: v1, approved in PR #42 (ChatGPT APPROVE, Round 2). Read-only. Do not edit. -->
<!-- Canonical latest version: ../CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md -->

# StelligenOS 当前总架构与模块逻辑（专家审核版）

## 1. 系统目标

StelligenOS 的目标是把未满足临床需求逐步转化为可验证、可工程化、可开发、可交易的生物技术资产。

系统的核心产出链是：

`Clinical unmet need -> Indication -> Endpoint -> Target -> Binder -> ADC construct -> Lead series -> Development candidate -> Asset`

系统负责定义对象、流程、证据要求、决策门、模块接口和审计规则；真实数据、证据、模型权重、运行结果和决策记录全部位于外部工作区。StelligenOS 是软件，不是数据库。

## 2. 总体设计原则

1. **临床问题先行**：先固定 indication 和需要改善的 endpoint，再寻找能够改变该 endpoint 的 target，避免从热门靶点反推适应症。
2. **证据与判断分离**：原始证据、机器提取、专家复核、Gate 评分和最终决策分别记录，不允许相互冒充。
3. **未知不是失败**：`unknown/null` 表示证据不足，不得自动转换为 0、FAIL 或负面证据。
4. **支持与反对证据并存**：相关合同分别保留 supporting/opposing/mixed、conflict、unknown 和 missing information（如存在）的引用；缺失不代表阴性。
5. **规则和模型不能直接改写决策**：历史 Rule、Model 或自然语言 if/then 只能提供参考；只有受治理的 Gate 执行才能产生 Gate 结果。
6. **状态不能自动晋级**：脚本成功、模型高分或单个 Gate 通过都不能自动推动生命周期；晋级需要显式决策及其证据和审计记录。
7. **全过程可追溯**：对象、合同、模型、Gate、输入、输出、证据和审核均使用版本化身份和外部引用。

## 3. 总架构

### 3.1 六个软件层

| 层 | 核心职责 |
|---|---|
| Operating System | 统一对象、生命周期、能力、合同和治理边界。 |
| Lifecycle | 规定资产从机会生成到开发的合法状态变化。 |
| Capabilities | 提供机会发现、证据提取、Gate、抗体/ADC 设计等可插拔能力接口。 |
| Cross-cutting | 提供 Knowledge Ledger、模型治理、IP/FTO、尽调、审计和版本控制。 |
| Objects | 定义系统中七类核心对象的稳定身份。 |
| Repository implementation | 连接外部工作区和外部运行时，不在仓库内保存业务数据。 |

### 3.2 四阶段生命周期

1. **Opportunity Generation**：从临床需求生成 indication-endpoint-target 机会假设。
2. **Opportunity Validation**：用证据、Rule、Model 和 Gate 判断机会是否值得推进；AssetGenOS 属于本阶段。
3. **Asset Generation**：选择现有 binder 工程化或表位条件化 de novo 发现路线，形成可验证的抗体/ADC 资产包。
4. **Asset Development**：围绕候选物开展后续实验、转化、临床、监管和交易准备。

合法状态只允许按上述顺序前进；当前代码只验证“是否允许转换”，不自动保存或执行转换。

### 3.3 七类核心对象

`Opportunity -> TargetHypothesis -> BinderCandidate -> ADCConstruct -> LeadSeries -> DevelopmentCandidate -> Asset`

每个对象当前只定义 `object_type`、`object_id` 和 `schema_version` 等身份合同，不承担数据库功能。`Asset` 是最终可进入 BD、合作、许可、融资或商业讨论的对象。

### 3.4 45 Gate 决策系统

45 个 Gate 分为三个连续决策域：

| 决策域 | Gate 数 | 核心问题 |
|---|---:|---|
| Target Opportunity（T-chain） | 13 | 临床问题是否明确；target 是否影响 endpoint；是否具备肿瘤表面可及性、内吞、表位可实现性和治疗指数。 |
| Product Realization（P-chain） | 16 | 能否把 target 变成具备合理抗体、表位、连接子、payload、DAR、PK、旁观者效应和生物标志物方案的 ADC 产品。 |
| Commercial Executability（C-chain） | 16 | 市场、竞争、监管、专利、FTO、可绕开性、权利要求、独占期和交易准备是否支持开发。 |

每个 Gate 接收候选对象、上游 Gate 结果和外部证据引用，输出 `score`、`confidence`、`status`、rationale、证据、缺失信息和建议验证。`null` 不等于 0。45 Gate 的身份和顺序已经冻结，新增或修改 Gate 必须走独立治理流程。

## 4. 模块设计逻辑

### 4.1 `gen_indication_endpoint_target`

目的：生成并验证 `indication + endpoint + target` 机会组合。

逻辑：下列内容是分阶段外部合同规定的目标运行顺序。当前仓库中的 `gen_indication_endpoint_target` 只提供 contract/port，不在仓库内执行候选生成、证据读取、Gate、T12、排序或持久化。

1. 从临床 unmet need 建立 `ClinicalFrame`，固定患者亚群、疾病状态、现有治疗缺口和目标 endpoint。
2. 从 ADC 临床先例、公共数据和文献中枚举 target；候选必须有明确身份，并达到外部策略规定的独立正向证据组数量，禁止仅凭 Model 或 Rule 生成。
3. 先运行早期关键 Target Gates：人群映射、肿瘤细胞表面可用性、组织内可及性、抗体依赖内吞、表位可实现性和治疗指数；证据不足进入 `HOLD`，不是自动淘汰。
4. 完成 endpoint biology：干预因果性、基线覆盖与逃逸、治疗诱导状态和净 endpoint 获益，形成 T0-T11 完整证据轨迹。
5. 检查证据独立性并执行对抗性审核；模型支持、重复来源或相互依赖证据不能虚增可信度。
6. 只有证据充分且重大冲突得到解决，才允许进入 T12 综合决策；T12 后的排序不能覆盖 Hard Gate 或 T12 结论。
7. 输出 Opportunity handoff：indication、endpoint、target、各 Gate 状态、支持/反对证据、关键未知、下一步最具判别力的验证任务。

当前 CRC 外部试运行已固定 9 个 indication、36 个 endpoint、41 个 target，并提取 292 条 target-level evidence；这些证据仍在分批 provisional review，尚未执行 Gate 评分、排序或最终 pair 推荐。

### 4.2 `assetgenos_catalog`

目的：保存 Opportunity Validation 所需的稳定软件目录。

逻辑：目录包含 45 个 Gate 定义、59 个 Model 定义和 53 个 Profile 定义。Gate 定义问题和输出语义，Model 绑定计算方法，Profile 定义不同 Gate/Model 组合及依赖图。目录只保存合同和身份，不保存训练数据、历史案例、校准结果或运行结果。

### 4.3 `gate_model_rule`

目的：把历史 ADC 经验转化为可审计的 Rule/Model 元数据，同时阻止经验规则直接控制 Gate。

逻辑：每条历史规则必须绑定既有 Gate、版本和外部适用性证据；自然语言 if/then 默认是描述性知识。未经单独治理和验证，不得自动改变 Gate 分数、状态、阈值或 Profile 绑定。

### 4.4 `antibody_binder_asset_engineering`

目的：把已有、版本化的 binder 工程化为 ADC carrier/asset package。

核心逻辑是两条不可相互补偿的评价轴：

- Track A：从序列和结构计算 binder 分子质量、humanization、化学 liability 和 developability。
- Track B：从有完整实验元数据的观察值评估 ADC carrier 的结合、内吞、运输和 payload delivery phenotype。

两条轴不加总，只用 Pareto dominance 选择；干净序列不能补偿不内吞的 carrier。模块还构建 Observation -> Hypothesis -> Failure mode -> Decision -> Experiment 推理图，用信息增益排序验证实验，并用临床 ADC 对照检索判断是否存在真正可比先例。16 个内部步骤映射到冻结的 14-stage 外部路线。

### 4.5 `epitope_conditioned_de_novo_antibody_discovery`

目的：从治疗性 antigen 和人为定义的 epitope 出发，生成 de novo antibody discovery package。

逻辑：依次完成 target biology、antigen/epitope engineering、IP/FTO 引导的表位选择、结构准备、negative design、表位条件化设计、计算排序、多样性优化、实验设计、结构验证、亲和力成熟、ADC readiness、专利包和资产报告，共 15 步。外部 AI/结构工具不会自动调用；工具不可用时只固化约束和实验包，不虚构抗体序列。

### 4.6 `biotech_asset_due_diligence`

目的：对任意 modality 的资产形成可审计尽调链，而不是直接给出投资结论。

逻辑链为：

`Asset -> AssetVariant -> AssessmentRun -> ArtifactRef -> EvidenceSource/Claim -> Observation -> Hypothesis -> FailureMode -> DecisionUncertainty -> ExperimentBranch -> SystemRecommendation`

系统建议与 `HumanDecision` 严格分离。尽调问题随生命周期阶段变化；系统不声称法律 FTO、临床安全性、临床有效性或最终资本配置结论。

### 4.7 横向能力

- **Knowledge Ledger**：统一记录 evidence、rule、hypothesis、experiment、failure、decision、calibration 和 lesson 的外部引用。
- **Model lifecycle**：模型以 `model_id@SemVer` 管理；模型注册、权重、验证和晋级决定留在外部治理系统。
- **IP/FTO、Due Diligence、Portfolio**：均通过外部服务接口返回 decision package，不在仓库内保存法律意见、尽调档案或资本配置记录。
- **Audit/versioning**：所有运行必须记录输入版本、合同版本、模型/Gate 版本、证据引用、缺失信息、审核者和时间戳。

## 5. 模块如何共同运作

```text
Human strategy + external evidence
        |
        v
Clinical unmet need -> ClinicalFrame -> indication + endpoint
        |
        v
Target enumeration -> evidence extraction -> expert/adversarial review
        |
        v
T0-T11 Target Gates -> evidence readiness -> T12 decision/ranking
        |
        v
Opportunity handoff -> explicit route selection
        |
        +-> Existing-binder engineering
        |
        +-> Epitope-conditioned de novo discovery
        |
        v
BinderCandidate -> ADCConstruct -> LeadSeries -> DevelopmentCandidate -> Asset
        |
        v
Stage-aware DD + IP/FTO + portfolio review + explicit human decision
```

模块之间只传递版本化对象和外部 artifact references。任何模块都不能因为自身运行成功而越过 Gate、替代专家审核或自动推动生命周期。

## 6. 当前版本的真实完成度

- 已完成：顶层架构、四阶段生命周期、七类对象、45 Gate 拓扑、Model/Profile 软件目录、两条抗体/ADC 生成路线、尽调合同、外部运行和审计边界。
- 已具备真实运行实现：existing-binder engineering 和 epitope-conditioned discovery 的外部输出流水线；前者功能更完整，后者仍依赖外部科学工具补足真实序列设计。
- 已完成 CRC 外部试运行的一部分：indication/endpoint/target 枚举和 target-level evidence extraction。
- 正在进行：292 条 CRC target evidence 的分批 ChatGPT provisional review，真实专家复核尚未完成。
- 尚未执行：CRC Gate scoring、T12 决策、最终 pair 排序/推荐、CRC binder/ADC asset generation、正式开发晋级。

## 7. 建议专家重点审核

1. indication 和 endpoint 的定义粒度是否足以对应真实临床开发人群和可测量获益。
2. T0-T12 的问题、依赖顺序、Hard Gate 和 HOLD 语义是否符合 ADC 开发规律。
3. target evidence 的九类维度、来源独立性和 supporting/opposing/unknown 判定是否合理。
4. 肿瘤表面可及性、内吞、异质性、脱落和正常组织风险是否需要更严格的必需证据。
5. binder 分子质量与 ADC carrier phenotype 采用双轴 Pareto、禁止加总的设计是否合理。
6. T12 到 Asset Generation 的准入条件是否充分，是否需要增加人工委员会或实验最低门槛。
7. IP/FTO、尽调和商业 Gate 的介入时间是否合理，是否存在过早或过晚的问题。
8. 哪些判断必须由人类专家签字，哪些可以由模型辅助，哪些可以自动执行。
