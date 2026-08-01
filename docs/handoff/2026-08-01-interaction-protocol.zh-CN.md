# 任务交接备忘：PR 协作规范

## 任务信息

- 任务编号：`task_20260801_pr-workflow`
- 分支：当前改动待在 `task_20260801_pr-workflow` 分支交付
- PR：待创建
- Commit：待提交
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

- `./scripts/verify_repository_boundary.sh`：待本次修改完成后运行。
- Markdown 链接检查：待本次修改完成后运行。
- `bash -n scripts/git_sync.sh`：待本次修改完成后运行。
- Git staged diff：提交前必须人工确认仅包含本任务文件。

## 未决问题与风险

- 当前工作仍在 `main` 的未提交状态；交付前必须切换到任务分支。
- PR 链接和最终 commit 尚未生成。

## 下一步

1. 在确认工作区文件范围后创建任务分支。
2. 显式暂存本任务文件并检查 staged diff。
3. 提交、推送并创建 PR 到 `main`。
4. 将 PR 链接交给外部模型审核。

## 数据边界声明

本仓库只保存架构系统文档、代码和小型治理文本；本任务没有新增任何数据、缓存或结果文件。所有数据和处理仍位于外部工作区。
