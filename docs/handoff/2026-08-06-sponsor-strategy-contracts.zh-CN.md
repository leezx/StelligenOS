# Handoff：小微 Biotech 架构调整第 1 步

## 任务

- 任务：建立 Sponsor Profile 与 Program Thesis 合同
- 分支：`task_20260806_sponsor-contracts`
- 基线：`main@b497246`
- Code commit：`e558181`
- 版本：`DevelopmentSponsorProfile@0.1.0`、`ProgramThesis@0.1.0`
- PR：https://github.com/leezx/StelligenOS/pull/67
- 状态：`APPROVED_WAITING_HUMAN_MERGE`

## 总体四步路线

1. Sponsor Profile 和 Program Thesis 合同（本 PR）。
2. Early Search-Space Admission 路由。
3. T12 后 Program Commitment Review。
4. ValueInflectionPlan 与风险转移计划。

只有本 PR 获得 ChatGPT 明确 `APPROVE` 并合并后，才允许开始第 2 步。

## 本 PR 已完成

- 新增 `src/contracts/sponsor_strategy.yaml`，冻结两个 0.1.0 合同的字段、引用和边界。
- 新增 `src/contracts/sponsor_strategy.py`，提供不持久化的内存校验类型。
- 新增 `docs/architecture/sponsor-strategy.zh-CN.md`，说明当前边界和后续四步的非授权关系。
- 更新架构入口、README 和 contracts README 的导航。
- 新增 4 个合同回归测试。

## 明确未做

- 未修改现有 45 个 Gate、Gate 拓扑、生命周期、ClinicalHypothesis 或核心对象注册表。
- 未实现 Search-Space Admission、Program Commitment Review、SponsorFitAssessment 或 ValueInflectionPlan。
- 未建立当前 Stelligen 的 Profile 实例、预算记录、样本/模型数据或项目 Thesis 实例。
- 未下载数据、未运行 provider、Gate、模型、EVGAP 或资产生成。
- 未把任何数据、cache、result、数据库或临时产物写入仓库。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`：`376 tests`，全部通过。
- `bash scripts/verify_repository_boundary.sh`：通过。
- `git diff --check`：通过。
- 未生成 `__pycache__` 或其他运行产物。

## 审核后动作

- ChatGPT review：`APPROVE`，审核记录见 `logs/chatgpt-review-2026-08-06-sponsor-strategy-phase1.md`。
- 当前动作：等待人类负责人合并 PR #67；合并前不创建第 2 步分支、不执行第 2 步。
- 合并后：再单独创建第 2 步 PR，只实现 Early Search-Space Admission。
- `REQUEST_CHANGES`：只在本 PR 按反馈最小修订并重新验证。
- `REJECT_PHASE`：停止执行，等待重新定义总纲或阶段边界。
