# 任务交接备忘：PR 协作规范

## 任务信息

- 任务编号：`task_20260801_pr-workflow`
- 分支：`task_20260801_pr-workflow`
- PR：https://github.com/leezx/StelligenOS/pull/1
- Base：`56c2e16`
- Code head：`190e24a`
- PR latest head at prior handoff revision：`025d815`
- Audit evidence commit：`ada438e`
- PR current tip：以 PR 页面实时状态为准
- Commits：
  - Code commits through code head:
    - `0fc4bbb` `task_20260801_pr-workflow: formalize PR handoff collaboration`
    - `959d124` `task_20260801_pr-workflow: record handoff verification`
    - `54c0126` `task_20260801_pr-workflow: link handoff to pull request`
    - `88e1b46` `task_20260801_pr-workflow: fix sync safety and add tests`
  - PR metadata commits after code head:
    - `190e24a` `task_20260801_pr-workflow: update v4 audit handoff`
    - `7bf3eac` `task_20260801_pr-workflow: align handoff head`
    - `025d815` `task_20260801_pr-workflow: clarify audited code head`
    - `ada438e` `task_20260801_pr-workflow: record ChatGPT review evidence`
    - `13b1737` `task_20260801_pr-workflow: clarify PR audit tip` (current PR tip at the time of this handoff revision)
- PR 状态：`OPEN / DRAFT`
- 时间：`2026-08-01 America/New_York`

## 本次改动

- 将 ChatGPT/Codex 协作固化为 `main -> task branch -> commit -> push -> PR -> external review -> merge/reject`。
- 固定任务分支格式为 `task_<编号>_<简短名>`。
- 要求每个任务 PR 在 `docs/handoff/` 留下交接备忘。
- 增加显式暂存和提交前状态检查要求，禁止全量暂存命令。
- 更新同步脚本，使其必须接收明确的文件路径清单。
- 修复同步脚本对未跟踪文件无效的问题，并在暂存区非空时拒绝执行。
- 新增 `tests/test_git_sync.sh`，覆盖未跟踪文件、已跟踪修改、非空暂存区和缺少文件清单四个场景。
- 将 Phase 0.5 审核清单改为中文，保留机器状态值为英文。

## 明确未改动

- 未修改架构契约、Phase 0/0.5 结论或任何数据处理逻辑。
- 未新增数据、缓存、结果、视频或临时产物。
- 未修改 `Zhixins-KB` 或其他外部数据目录。

## 验证

- `./scripts/verify_repository_boundary.sh`：通过。
- `bash -n scripts/git_sync.sh`：通过。
- `bash -n tests/test_git_sync.sh`：通过。
- `tests/test_git_sync.sh`：通过，A-D 四个场景均通过。
- `git diff main...190e24a --check`：通过，覆盖代码审计范围。
- `git diff main...025d815 --check`：通过，覆盖完整 PR aggregate diff。

## 未决问题与风险

- 任务分支已推送，draft PR 已创建，等待外部模型审核。
- PR 已创建并已补充最终 handoff。
- ChatGPT 最终复审结论：`APPROVE`；可以进入 Phase 1。脚本、测试、aggregate diff、数据边界和 commit 分类追溯均已完成。

## 下一步

1. 由负责人决定是否合并 PR #1。
2. Phase 1 从 `main` 拉取最新代码，创建新的 `task_<编号>_<简短名>` 分支和 PR。
3. 继续使用 `docs/handoff/`、worklog、显式暂存和 GitHub 插件复审闭环。

说明：本 handoff 文件自身的最新 metadata commit 不在自身列表中自引用；PR 页面是当前 branch tip 的权威来源。

## 数据边界声明

本仓库只保存架构系统文档、代码和小型治理文本；本任务没有新增任何数据、缓存或结果文件。所有数据和处理仍位于外部工作区。
