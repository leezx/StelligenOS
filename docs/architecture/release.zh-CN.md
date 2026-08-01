# 架构冻结与发布规范

## 冻结范围

- 顶层生命周期固定为 Opportunity Generation、Opportunity Validation、Asset Generation、Asset Development。
- 七类核心对象、45 Gate 拓扑、两条 Binder/ADC 路线和三类跨阶段服务合同是稳定边界。
- 本仓库只保存架构、合同、Prompt、代码、脚本、测试和必要说明，不保存任何数据。

## 开发规则

- 新能力必须归入既有生命周期或 capability/cross-cutting 层，不得新增顶层生命周期。
- 数据、证据、模型权重、运行结果、缓存和数据库必须位于外部工作区。
- 任何阶段任务必须从最新 `main` 创建 `task_<编号>_<简短名>` 分支，经 PR 和 ChatGPT `APPROVE` 后才可合并。
- 每次阶段交接必须更新 `docs/handoff/` 和 `logs/worklog.md`。
- 显式暂存相关文件，提交前检查 `git status`；禁止 `git add .`。

## 发布门禁

- 单元测试、repository boundary、aggregate diff 和 `git diff --check` 必须通过。
- Manifest、report、checklist、handoff、worklog 和 PR 描述必须一致。
- 任何数据残留、内部持久化、未审核阶段变更或自动晋级均阻断发布。
- 发布只标记软件合同和代码版本，不打包外部数据。
