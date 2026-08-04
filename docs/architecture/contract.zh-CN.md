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

核心对象：

1. Opportunity
2. ClinicalHypothesis
3. TargetHypothesis
4. BinderCandidate
5. ADCConstruct
6. LeadSeries
7. DevelopmentCandidate
8. Asset

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
- 能力说明：`docs/architecture/capabilities.zh-CN.md`
- 生命周期说明：`docs/architecture/lifecycle.zh-CN.md`
- 核心对象清单：`src/contracts/core_objects.yaml`
- 运行 Prompt：`prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md`

## 7. 尚未进入内核的扩展

外部专家反馈产生的改进提案登记在 `extensions/`，**不属于本契约**，也不构成架构变更授权。注册表见 `extensions/README.md`，二级风险清单见 `extensions/BACKLOG.zh-CN.md`。

只读本契约不会看到这些提案，因此此处留指针。扩展进入内核必须另立治理任务、独立 PR 和 ChatGPT `APPROVE`；内核不得引用或导入任何扩展。
