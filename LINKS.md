# LINKS

## 规范来源

- [Architecture](./architecture.md)
- [Architecture Contract](./docs/architecture/contract.zh-CN.md)
- [Capabilities](./docs/architecture/capabilities.zh-CN.md)
- [Lifecycle](./docs/architecture/lifecycle.zh-CN.md)
- [Legacy Inventory](./docs/architecture/legacy_inventory.zh-CN.md)
- [Current System And Module Logic](./docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md)
- [Architecture Doc Versioning](./docs/architecture/versions/README.md)
- [Phase 0 Prompt](./prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md)
- [Phase 0 Report](./docs/phases/PHASE_0_REPORT.zh-CN.md)
- [Phase 0.5 Report](./docs/phases/PHASE_0_5_REPORT.zh-CN.md)
- [ChatGPT-Codex Talk](./ChatGPT-Codex-talk.md)
- [ChatGPT-Codex Phase Gate Protocol](./docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md)
- [ADCdb–Atlas–ADC AIDD Design Pipeline](./docs/protocols/ADCdb_Atlas_ADC_AIDD_design.md)
- [Worklog](./logs/worklog.md)
- [Git Sync Script](./scripts/git_sync.sh)
- [Handoff Template](./docs/handoff/TEMPLATE.zh-CN.md)

## 扩展提案

- [Extensions Registry](./extensions/README.md)
- [Extensions Backlog](./extensions/BACKLOG.zh-CN.md)

扩展是尚未进入架构内核的提案。内核不得依赖扩展；扩展不得改写 Gate 结果或推动生命周期。

## 存储策略

- 数据和处理产物都必须留在仓库外部。
- 数据集、分析输出、证据包都应放在外部工作区。
- reference examples、toy examples、report templates、demo assets、golden test cases 只允许保持小而受控。
- `logs/worklog.md` 是详细执行轨迹。
- `scripts/git_sync.sh` 用于显式文件清单的 fetch / rebase / commit / push；禁止用全量暂存替代范围检查。

## 说明

- 当前仓库已完成 Phase 0 和 Phase 0.5。
- 后续任何数据相关路径都只能在仓库外部定义，再以引用形式挂回这里。
