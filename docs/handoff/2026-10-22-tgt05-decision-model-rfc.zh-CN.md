# TGT-05 决策模型 canonical 迁移 RFC 交接

- 时间：2026-10-22 15:31 EDT
- 任务分支：`task_20261022_tgt05_decision_model_rfc`
- Base：`main` @ `1c8ba22`
- PR：[StelligenOS #142](https://github.com/leezx/StelligenOS/pull/142)，`OPEN`；审核前应核对 GitHub 实时 tip
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

## Round 1 审核与同 PR 修订（2026-10-22 18:58 EDT）

固定审核会话对 PR #142 @ `e712adfa771f359fa85413334d209ec200fdcf8a` 给出 `REQUEST_CHANGES`，六项 blocker 的逐项记录见 `logs/chatgpt-review-2026-10-22-tgt05-decision-model-rfc.md`。GitHub review integration 返回 403；会话文本是本轮审核反馈。未获 `APPROVE`，没有进入下一 Phase。

用户明确选择 v2 GateSet policy bodies 放在 StelligenOS 版本化契约目录，并授权把 TGT-05 决策模型章节的逐字快照提交公开 PR。RFC 同 PR 修订：冻结 v2 Gate/Module/GateSet/Instantiation lineage 和八成员版本；E1/E2/E3 与 canonical Direction/Strength 的映射及上限；`Tgt05DecisionRecord` 的非 canonical 人审地位；临床和功能 KILL route 的 program/context 限制；四个 policy ref、Git registry 路径、binding 一致性与审批权。新增 `docs/architecture/TGT05_DECISION_MODEL_V1_SOURCE_SNAPSHOT.md`，10,410 bytes，SHA256 `2e41525f65c6f7e4e9ec909bd8f110623f6ce62f54d5c82448c37aa80224674c`；与本地 design 从唯一章节标题起至 EOF 的字节完全相同，完整 design SHA256 `e4e5198a0021256fdb1cee3f516cd1e941d8c72c3c3fcb90b7c5e3dd9c4a2603`。本 PR 仍是 RFC，不创建 policy body、Module 或真实靶点结果；policy body 属 Phase A 契约 PR，须本轮审核明确 `APPROVE` 后才启动。

验证：`python3` 字节比对和 SHA256 通过；`git diff --check` 通过；`bash scripts/verify_repository_boundary.sh` 输出 `Repository boundary check passed.`。推送后须以 GitHub exact HEAD 更新本交接和审核记录，并把同一 PR 送回固定会话复审。
