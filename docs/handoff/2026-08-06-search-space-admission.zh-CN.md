# Handoff：小微 Biotech 架构调整第 2 步

## 任务

- 任务：Early Search-Space Admission sponsor-relative 路由合同
- 分支：`task_20260807_search-space-admission`
- 基线：`origin/main@12055f5`
- 版本：`SearchSpaceAdmission@0.1.0`
- PR：https://github.com/leezx/StelligenOS/pull/68
- 状态：`APPROVED_WAITING_HUMAN_MERGE`

## 总体四步路线

1. Sponsor Profile 和 Program Thesis 合同（已合并 PR #67）。
2. Early Search-Space Admission 路由（本 PR）。
3. T12 后 Program Commitment Review。
4. ValueInflectionPlan 与风险转移计划。

只有本 PR 获得 ChatGPT 明确 `APPROVE` 并合并后，才允许开始第 3 步。

## 本 PR 已完成

- 新增 `SearchSpaceAdmission@0.1.0` 合同及四个路由：`ACTIVE_SEARCH`、`WATCHLIST`、`PARTNER_ONLY`、`OUT_OF_MANDATE`。
- 冻结八个低成本条件及三态状态：`SATISFIED`、`UNKNOWN`、`UNSATISFIED`。
- 新增纯内存校验类型；路由策略、证据、理由和实例均要求外部引用。
- 明确 `UNKNOWN` 不等于 KILL，路由不是科学 Gate 结果，不删除或变更候选，不放行 Gate 或 Asset Generation。
- 新增架构说明、导航和 5 个回归测试。

## 明确未做

- 未实现证据抽取、数据采集、Gate、EVGAP、评分模型或自动路由策略。
- 未修改现有 45 个 Gate、Gate 拓扑、生命周期、核心对象、ClinicalHypothesis、TargetHypothesis 或 Asset Generation 路由。
- 未创建任何 sponsor、program、candidate 或 admission 实例。
- 未下载数据，未产生 cache、result、数据库、模型权重或外部运行产物。
- 未实现 T12 后 Program Commitment Review 或 ValueInflectionPlan。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`：`381 tests`，全部通过。
- 定向测试：Search-Space Admission 与 Sponsor Strategy 共 `9 tests`，全部通过。
- `bash scripts/verify_repository_boundary.sh`：通过。
- `git diff --check`：通过。
- 未生成 `__pycache__` 或其他运行产物。

## 审核后动作

- ChatGPT review：`APPROVE`，审核记录见 `logs/chatgpt-review-2026-08-06-search-space-admission-phase2.md`。
- 当前动作：按既定协作授权合并 PR #68；合并前不创建第 3 步实现分支。
- 合并后：再单独创建第 3 步 PR，只实现 T12 后 Program Commitment Review。
- `REQUEST_CHANGES`：只在本 PR 按反馈最小修订并重新验证。
- `REJECT_PHASE`：停止执行，等待重新定义总纲或阶段边界。
