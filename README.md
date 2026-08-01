# StelligenOS

StelligenOS 是一个 biotechnology asset operating system 的实现仓库。

这个仓库只保存操作系统的一种实现、架构契约、运行 Prompt、脚本、代码和少量必要说明。
它不是操作系统本体，也不是数据库。

## 仓库边界

- 允许放入：架构文档、Prompt、Schema、脚本、代码、参考文档，以及少量受控示例材料。
- 允许的示例材料包括：reference examples、toy examples、report templates、demo assets、golden test cases。
- 禁止放入：large datasets、raw sequencing、intermediate files、caches、outputs、temporary artifacts、data-bearing working files。
- 所有数据和数据处理必须放在仓库外部的工作区。

## 当前阶段

- Phase 0 已完成
- Phase 0.5 已完成
- 当前可进入 Phase 1 的前置条件已满足，等待下一步执行

## 关键入口

- `architecture.md`
- `docs/architecture/contract.zh-CN.md`
- `docs/architecture/capabilities.zh-CN.md`
- `docs/architecture/lifecycle.zh-CN.md`
- `docs/architecture/legacy_inventory.zh-CN.md`
- `prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md`
- `docs/phases/PHASE_0_REPORT.zh-CN.md`
- `docs/phases/PHASE_0_5_REPORT.zh-CN.md`
- `logs/worklog.md`
- `ChatGPT-Codex-talk.md`
- `AGENTS.md`
- `LINKS.md`
- `scripts/verify_repository_boundary.sh`
- `scripts/git_sync.sh`
