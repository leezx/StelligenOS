# TGT-05 决策模型 canonical 迁移 RFC 交接

- 时间：2026-10-22 15:31 EDT
- 任务分支：`task_20261022_tgt05_decision_model_rfc`
- Base：`main` @ `1c8ba22`
- PR：[StelligenOS #142](https://github.com/leezx/StelligenOS/pull/142)，`OPEN`；当前 tip `7d40496`（审计元数据提交）
- 初版 code commit：`19475d897eefdf51661dbb48aa05817c2f5aa109`；PR base：`1c8ba2274cbdbdd0c7193e2f5a5b3a440952730c`
- 目标：将 webReport Gate 设计中的 TGT-05 决策模型 v1.0 纳入 StelligenOS canonical 迁移计划，先审定科学与对象边界。

## 本阶段交付

新增 `docs/architecture/TGT05_DECISION_MODEL_V1_MIGRATION_RFC.zh-CN.md`，提出 v2 lineage、E1/E2/E3 与现行 ladder 的隔离、Gate-neutral EP、reviewer-facing Decision Record、人工审议、GateSet 决策权、覆盖质控和逐 PR 验收。`logs/worklog.md` 记录读取、判断、修改和验证。

## 范围与状态

这是**设计审阅 PR**，不是已生效 canonical 规则。现行 GateSet、module YAML/Python、schema、测试和策略引用未改；未进行 DATA 下载或真实 250 靶点评估。来源 `PR/webReport_Stelligen` 的 design 尚无 Git remote，因此实施 PR 需锁定其 Git 提交。现行外部 `fatal_gate_policy`/`decision_rule` 实体位置尚未确认，实施前必须解决。

## 验证

- `git status --short`：仅本 RFC、handoff 和 `logs/worklog.md` 属本任务；旧主工作区改动留在原工作区。
- `git diff --check`：通过。
- `bash scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- 数据边界：只有小型文档；无数据、缓存、运行结果。

## 审阅要点与下一步

请审核：版本迁移是否应为 `TGT-05@2.0` / `ADC_TARGET_GATESET@2.0`；单个归因充分的 ADC 临床事件何时可触发 KILL 审议；Decision Record 的对象归属；外部决策策略的 canonical 所有者及版本。GPT/ChatGPT 对本 PR 明确 `APPROVE` 前，不修改运行契约、不做依赖运行；`APPROVE` 后仍由人类决定 merge 和下一 Phase。

2026-10-22 15:32 EDT：已将 PR #142 @ `7d40496` 提交至固定的 `Biotech ideas → AI审核方案` ChatGPT 对话，要求基于 GitHub current PR 输出 `APPROVE / REQUEST_CHANGES / REJECT_PHASE`。审核回复待收。
