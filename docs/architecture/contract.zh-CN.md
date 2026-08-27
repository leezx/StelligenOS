# StelligenOS 架构契约

## 1. System Definition

StelligenOS 是一个 biotechnology asset operating system。

本仓库只承载该操作系统的一种实现，包括架构契约、Prompt、Schema、脚本、代码和必要的说明文档。

本仓库不是数据库，也不是数据仓库。

## 2. Repository Boundary

允许：

- 架构文档
- Prompt
- Schema
- 脚本
- 代码
- 参考文档
- reference examples
- toy examples
- report templates
- demo assets
- golden test cases

禁止：

- large datasets
- raw sequencing
- intermediate files
- caches
- outputs
- temporary artifacts
- data-bearing working files

所有数据、数据处理和数据产物必须放在仓库外部的独立工作区。

## 3. Architecture Layers

StelligenOS 采用以下分层：

1. Operating System
2. Lifecycle
3. Capabilities
4. Cross-cutting
5. Objects
6. Repository Implementation

分层是**软件结构**。决策层模型（Candidate × Gate × Evidence 六对象 +
Instantiation 绑定层）见 3.4.1，它是所有生命周期阶段与所有 Candidate 类型
共用的骨架，冻结后不随实例化改变。

### 3.1 Lifecycle

四个主生命周期阶段：

1. Opportunity Generation
2. Opportunity Validation
   - `AssetGenOS` 只作为该阶段下的子系统
3. Asset Generation
4. Asset Development

`Asset Development` 是对外更自然的行业语言，优于 `Asset Advancement`。

### 3.2 Capabilities

Capabilities 是操作系统提供的能力集合，不是生命周期，也不是核心对象。

初始能力包括：

- Opportunity Discovery
- Knowledge Mining
- Rule Learning
- Evidence Extraction
- ADC Design
- Binder Engineering
- Patent Analysis
- Due Diligence
- Portfolio Management

### 3.3 Cross-cutting

横向能力贯穿所有阶段，包括：

- Knowledge Ledger
- IP/FTO
- stage-aware Due Diligence
- Audit
- Versioning

`Knowledge Ledger` 是首选名称，可覆盖 evidence、rules、hypotheses、experiments、failures、decisions、calibrations 和 lessons。

### 3.4 Objects

#### 3.4.1 决策层模型（Blueprint v1.3，规范）

StelligenOS 的决策层是一个 **Candidate × Gate × Evidence** 系统。六个核心对象
被冻结，不随 Candidate 类型或开发阶段改变：

1. `Candidate` —— 与 Context 解耦（context-independent），不持有 `context_id`
2. `Context`
3. `Gate`（及其 `GateSet`）—— Gate 层 `assessment_rule` 产生 `Direction + Strength`；GateSet 层 `decision_rule` / `fatal_gate_policy` / `required_gate_policy` 产生 `Decision`
4. `EvidencePackage` —— 原子、full provenance、**无固有 Strength grade**、引用而非复制
5. `CandidateGateAssessment` —— 矩阵最小 cell，Candidate 与 Context 在此首次关联
6. `Decision` —— `GO / CONDITIONAL_GO / HOLD / MORE_EVIDENCE / KILL / NOMINATE / COMMIT`

`Instantiation` **不是第七个对象**：它是 configuration/binding 对象，只把
`candidate_type + context_id + modality` 绑定到某个版本化的 `gateset_id`，
本身不产生科学结论。它是唯一的跨项目/跨阶段扩展机制。

正交性铁律：`Direction ⊥ Strength`，且在 `CONFLICTING` 状态下同样成立
（不因冲突自动降级 Strength）；`evidence type ceiling > evidence quantity`；
禁止通用数值分数；`UNKNOWN` 与 `CONFLICTING` 是一等状态。

#### 3.4.2 Candidate Level Registry（L0–L14，规范）

Candidate 生命周期是一系列逐层收敛的搜索空间；上一级 Candidate 被选定后冻结
为下一级的 Context。canonical Candidate Level 与对应 GateSet：

`L0` Indication · `L1` Patient Territory · `L2` Endpoint · `L3` Modality ·
`L4` ADC Target · `L5` ADC Epitope · `L6` Antibody/Binder · `L7` Linker ·
`L8` Payload · `L9` ADC Design · `L10` ADC Hit · `L11` ADC Lead ·
`L12` Biomarker · `L13` Development Candidate · `L14` Clinical Regimen。

完整定义（每级 GateSet、Gate ID → Candidate Level 归属、evidence regime）以
外部 Blueprint `StelligenOS_Candidate_Levels_and_GateSets_Blueprint.v0.1` 与
`StelligenOS-产品形态-Blueprint v1.3` 为规范来源，并由
`docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`
（`v5-draft`）在仓库侧维护。

#### 3.4.3 Runtime Conformance 与 legacy → target migration crosswalk

**本契约的 3.4.1 / 3.4.2 是 architecture specification 的规范目标；它已变，
但 runtime implementation 未变。** 两者关系：

```text
Target architecture:
  Blueprint v1.3 six-object model + Instantiation binding layer

Current runtime contracts:
  core_objects@1.1                          （8 legacy object types）
  gate_system@0.1.0 / topology@0.2.0        （45 legacy gates, FROZEN_LEGACY）
  GateInputEnvelope / GateModelOutput@2.1.0  （score/confidence/status）

Runtime conformance:
  MIGRATION_PENDING

Rule:
  在后续 runtime migration PR（顺序见 CURRENT_SYSTEM v5-draft §16 B 组问题 23，
  PR A–E）合并之前，repository runtime 不得声称已实现 Blueprint v1.3 conformance。
```

`src/contracts/core_objects.yaml` 当前仍登记 8 个 **legacy object type**。它们到
目标 ontology 的映射是**迁移拆分，不是一一等价**（多数是 composite）：

1. `Opportunity` —— legacy search/orchestration wrapper → `Instantiation` intent + `Context` seed + Candidate-generation request（不属于任何 Candidate Level）
2. `ClinicalHypothesis` —— legacy composite（当前组合 target、anchor clinical context、intended benefit、biomarker hypothesis、product hypothesis）→ `Context` + `Candidate`/reference + biomarker/product hypothesis reference；lock state → `Context` maturity
3. `TargetHypothesis` —— `Candidate`，`candidate_type = ADC Target`（L4）
4. `BinderCandidate` —— `Candidate`（L6）
5. `ADCConstruct` —— legacy composite，跨 L9 ADC Design / L10 ADC Hit（未来需 stage/type discriminator 或 distinct Candidate objects）
6. `LeadSeries` —— legacy series/container around L11 ADC Lead candidates（decomposition pending）
7. `DevelopmentCandidate` —— `Candidate`（L13）
8. `Asset` —— `NOMINATE` / `COMMIT` 后的对外商业/交易表述，非新 Candidate Level

`Biomarker`（L12）、`Endpoint`（L2）及 `Epitope` / `Linker` / `Payload` /
`ADC Lead` / `Clinical Regimen` 是 `core_objects@1.1` **尚缺、migration 时须新增**
的 Candidate Type，不是上表 8 对象的 crosswalk。

架构方向（8 对象折叠为泛化 `Candidate` + `candidate_type` + `level`；旧 45-Gate
冻结为 legacy、新建 canonical GateSet lineage）已由 Blueprint v1.3 决定，登记在
`CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md` 第 16 节 **A 组**；
尚待实现设计的 blocker 在同节 **B 组**。本契约的决策层模型（3.4.1 / 3.4.2）
是规范目标，其代码落地属独立实现任务。

#### 3.4.4 ClinicalHypothesis 递进锁定

`ClinicalHypothesis` 是 v5 的早期研发单元，组合 target、anchor clinical
context、intended benefit、biomarker hypothesis 和 product hypothesis。
它支持 `mature-target-first`、`target-context-co-selection` 和
`clinical-problem-first` 三种入口；探索态允许 seed 不完整，正式锁定状态
按最低必填条件校验。
v5 Candidate/T12 路径必须传递 `ClinicalHypothesis` 身份；旧的精确
indication-endpoint-target 路径只能通过显式 `legacy_compatibility` 标记
使用，不能继续作为默认不变量。
它采用 `exploratory -> provisional -> anchored -> product-locked ->
protocol-locked -> regulatory-locked` 递进锁定；未知不等于失败。

`Asset` 必须能够进入商业讨论，能被 partner、investor、BD 或 licensing 语境使用。

## 4. Phase Structure

Phase 0:

- Repository Audit

Phase 0.5:

- Legacy Inventory
- Migration Matrix

Phase 1:

- Freeze the architecture contract
- Create the minimal directory skeleton
- Keep the prompt separate from the contract

后续 Phase 只在契约冻结后推进。

## 5. Naming Rules

- 面向操作者的说明使用中文
- 机器可读 ID、Schema 名、路径和脚本名使用英文
- `Asset Advancement` 改用 `Asset Development`
- 架构契约和运行 Prompt 必须分离

## 6. Source of Truth

- 架构契约：`docs/architecture/contract.zh-CN.md`
- 决策层模型与当前实现说明（`v5-draft`）：`docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`
- 决策层规范来源（外部 Blueprint）：`StelligenOS-产品形态-Blueprint v1.3`、`StelligenOS_Candidate_Levels_and_GateSets_Blueprint.v0.1`
- 能力说明：`docs/architecture/capabilities.zh-CN.md`
- 生命周期说明：`docs/architecture/lifecycle.zh-CN.md`
- 核心对象清单（当前实现登记，待 crosswalk）：`src/contracts/core_objects.yaml`
- 运行 Prompt：`prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md`

## 7. 尚未进入内核的扩展

外部专家反馈产生的改进提案登记在 `extensions/`，**不属于本契约**，也不构成架构变更授权。注册表见 `extensions/README.md`，二级风险清单见 `extensions/BACKLOG.zh-CN.md`。

只读本契约不会看到这些提案，因此此处留指针。扩展进入内核必须另立治理任务、独立 PR 和 ChatGPT `APPROVE`；内核不得引用或导入任何扩展。
