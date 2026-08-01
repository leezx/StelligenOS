# AGENTS.md for StelligenOS

## Mission

本仓库定义 StelligenOS 的实现。它是一个 biotechnology asset operating system implementation repository，
不是数据库，也不是结果仓库。

## 硬性边界

1. 仓库允许放：架构文档、Prompt、Schema、脚本、代码、参考文档，以及少量受控示例。
2. 仓库禁止放：large datasets、raw sequencing、intermediate files、caches、outputs、temporary artifacts、data-bearing working files。
3. 允许的示例材料必须小、可追溯、非敏感，并明确标注为参考或测试用途。
4. 所有数据采集、处理、分析和存储必须发生在仓库外部的工作区。
5. 如果任务需要数据，不要把数据暂存进这个仓库。
6. 任何会让仓库偏离“实现仓库”边界的改动，都要先回到架构契约。

## 工作规则

- 保持 Phase 0 / Phase 0.5 的审计优先心态。
- 现有遗留文本默认只作为参考材料，除非已被正式提升到架构契约。
- Phase 0 = 仓库审计；Phase 0.5 = 旧系统盘点与迁移映射。
- 每次完成较大的任务后，都要追加一条时间戳记录到 `logs/worklog.md`。
- 机器可读 ID、路径和 Schema 名保持英文。
- 面向操作者的说明优先使用中文。

## 遗留文件

- `prompts/GPT-Feedback.md` 是用户反馈，不是 canonical architecture。
- `architecture.md` 是入口页；正式契约在 `docs/architecture/` 下。
- `ChatGPT-Codex-talk.md` 是 ChatGPT/Codex 的固定交互规范；以后需要“只负责执行、由外部模型审核”时，优先遵守这份文件。
- 默认审核单位是 PR，不是本地未推送工作区；需要复审时，优先提供 PR diff、commits、report、checklist、manifest 和验证结果。
- 默认任务分支格式是 `task_<编号>_<简短名>`；每个 PR 都要在 `docs/handoff/` 留下交接备忘。
- 提交前必须先运行 `git status --short`，只用 `git add -- <相关文件>`，禁止 `git add .`、`git add -A` 和 `git add --all`。

## 校验

- 在增加新的顶层文件或目录之前，先运行 `scripts/verify_repository_boundary.sh`。
- 不要把数据类文件或数据类目录加进这个仓库。
- 例行 GitHub 同步优先使用 `scripts/git_sync.sh <branch> <commit-message> <相关文件...>`，保证 fetch/rebase/显式暂存/commit/push 流程一致。
- 同步脚本在暂存区非空时必须拒绝执行；脚本行为由 `tests/test_git_sync.sh` 的 A-D 场景验证。
