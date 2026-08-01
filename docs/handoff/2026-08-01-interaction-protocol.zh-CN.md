# 任务交接备忘：PR 协作规范

## 任务信息

- 任务编号：`task_20260801_pr-workflow`
- 分支：`task_20260801_pr-workflow`
- PR：https://github.com/leezx/StelligenOS/pull/1
- Commit：`0fc4bbb`
- 时间：`2026-08-01 America/New_York`

## 本次改动

- 将 ChatGPT/Codex 协作固化为 `main -> task branch -> commit -> push -> PR -> external review -> merge/reject`。
- 固定任务分支格式为 `task_<编号>_<简短名>`。
- 要求每个任务 PR 在 `docs/handoff/` 留下交接备忘。
- 增加显式暂存和提交前状态检查要求，禁止全量暂存命令。
- 更新同步脚本，使其必须接收明确的文件路径清单。

## 明确未改动

- 未修改架构契约、Phase 0/0.5 结论或任何数据处理逻辑。
- 未新增数据、缓存、结果、视频或临时产物。
- 未修改 `Zhixins-KB` 或其他外部数据目录。

## 验证

- `./scripts/verify_repository_boundary.sh`：通过。
- `bash -n scripts/git_sync.sh`：通过。
- `git diff HEAD^ --check`：通过。
- Git staged diff：提交前必须人工确认仅包含本任务文件。

## 未决问题与风险

- 任务分支已推送，draft PR 已创建，等待外部模型审核。
- PR 链接和最终 commit 尚未生成。

## 下一步

1. 将 PR 链接交给外部模型审核。
2. 只按当前 PR 的审核意见修订。
3. 由负责人决定 merge 或打回。

## 数据边界声明

本仓库只保存架构系统文档、代码和小型治理文本；本任务没有新增任何数据、缓存或结果文件。所有数据和处理仍位于外部工作区。
