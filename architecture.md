# StelligenOS 架构入口

这是 StelligenOS 架构导航入口页。

## 规范文档

- [Architecture Contract](./docs/architecture/contract.zh-CN.md)
- [Capabilities](./docs/architecture/capabilities.zh-CN.md)
- [Lifecycle](./docs/architecture/lifecycle.zh-CN.md)
- [Current Design Architecture and Module Logic](./docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md)
- [Biotech Infrastructure Catalog](./docs/architecture/BIOTECH_INFRASTRUCTURE_CATALOG.zh-CN.md)
- [Sponsor Strategy Contracts](./docs/architecture/sponsor-strategy.zh-CN.md)
- [Early Search-Space Admission](./docs/architecture/search-space-admission.zh-CN.md)
- [Program Commitment Review](./docs/architecture/program-commitment-review.zh-CN.md)
- [Value Inflection Plan](./docs/architecture/value-inflection-plan.zh-CN.md)
- [Sponsor Fit Assessment](./docs/architecture/sponsor-fit-assessment.zh-CN.md)
- [Opportunity Territory Map](./docs/architecture/opportunity-territory.zh-CN.md)
- [Legacy Inventory](./docs/architecture/legacy_inventory.zh-CN.md)
- [Migration Prompt](./prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md)

## 当前状态

StelligenOS 已定义为 biotechnology asset operating system 的实现仓库。
正式架构契约与运行 Prompt 分离。

当前专家审核基线为 `STELLIGENOS-ARCH-2026.08.27-v5`（PR #94 `APPROVE`，merge
`ea9dc04`；快照 `docs/architecture/versions/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.v5.zh-CN.md`），
以规范路径上的 Current Design Architecture 文档为准。`v5` 依据 Blueprint v1.3
把 Candidate × Gate × Evidence 六对象决策模型、Candidate Levels L0–L14 与
canonical GateSet registry 提升为架构主干。这是 **architecture-specification**
批准：`core_objects.yaml`、`gate_system.yaml` 仍为 legacy 快照，但按 v5 文档
第 16 节 B 组的 PR A–E16 顺序施工的 **runtime conformance 已 COMPLETE** —— PR
A–E16 的 Candidate × Gate × Evidence runtime migration 与八个 primary Evidence
Production Module（TGT-01…TGT-08 @ `1.0.0`）migration 已收口（PR E16 建成
MOD-TGT07 并解除 `MIGRATION_PENDING`）。此收口只覆盖 PR A–E16 runtime
conformance 与八 primary Module migration；其它 deferred work（quantitative
ladder calibration、epitope-layer 分析、external evaluators、下游 Candidate
level、FTO 任务）仍在后续。
