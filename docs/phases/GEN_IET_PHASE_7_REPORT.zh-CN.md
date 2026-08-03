# `gen_indication_endpoint_target` Phase 7 报告

- 阶段：Phase 7，T12 Decision and Ranking
- 分支：`task_20260801_gen-iet-phase7-t12-ranking`
- 父阶段：Phase 6，已获 ChatGPT `APPROVE`
- 状态：`APPROVED_PHASE_7`
- Gate 变更：`NO_GATE_CHANGE`

## 本阶段实现

新增 `src/capabilities/t12_decision_ranking.py`，定义正式 T12 和非 Gate
Opportunity ranking 的 external-only ports：

- `T12DecisionRequest/Result`：要求 readiness 和完整 T0-T11 trace 引用，区分 `PROVISIONAL_ADVANCE`、`EXPLORATION`、`HOLD`、`FAIL`。
- `OpportunityHandoffPackage`：保留外部 rationale、下一步证据和最便宜决定性实验引用，`eligible_for_asset_generation` 永远保持 false。
- `OpportunityRankingRequest/Result`：只接收 eligible T12 decision 引用，排序不能覆盖 Hard Gate 或 T12 语义。
- `T12DecisionPort/OpportunityRankingPort`：仅定义外部实现接口，不在仓库内执行。

## 明确未执行

本阶段没有运行 T12 或 ranking，没有读取证据或临床数据，没有创建本地
Opportunity/handoff 记录，没有进入 Binder 开发，没有执行 P-chain，没有
持久化结果，没有调用数据库、cache、模型权重、runner 或新 Gate。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：73 passed
- `./scripts/verify_repository_boundary.sh`：passed
- `git diff --check`：passed

## 停止点

ChatGPT 已批准 Phase 7 contract-only PR，可以进入 Phase 8。该批准不包括
Phase 8 实现或真实 T12；Phase 8 必须从本阶段批准 tip 创建新分支并单独提交审核。
