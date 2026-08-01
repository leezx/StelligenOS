# `gen_indication_endpoint_target` Phase 4 报告

- 阶段：Phase 4，Early T-Gate Candidate Reduction
- 分支：`task_20260801_gen-iet-phase4-early-t-gate`
- 父阶段：Phase 3，已获 ChatGPT `APPROVE`
- 状态：`COMPLETED_PENDING_REVIEW`
- Gate 变更：`NO_GATE_CHANGE`

## 本阶段实现

新增 `src/capabilities/early_t_gate_reduction.py`，定义早期 T-Gate 收缩的
external-only 调度和结果合同：

- `EarlyReductionSchedule`：只允许既有 T2、T7 及 T8-T11，强制 T2/T7 优先，并禁止 T12。
- `CandidateReductionDecision`：保留每个候选的 `PROVISIONAL_ADVANCE`、`HOLD` 或 `EXCLUDE`、原因、Gate 结果、证据和缺口引用。
- `EarlyTGateReductionRequest/Result`：只传递 external 候选、ClinicalFrame、Gate 输入范围、运行和 trace 引用。
- `EarlyTGateReductionPort`：仅定义外部实现的 `reduce` 方法，不执行本地 Gate。

无证据只能进入 `HOLD` 并附带缺口或证据引用，不定义或使用 `FAIL` 状态。

## 明确未执行

本阶段没有读取证据或临床数据，没有运行 T2-T11，没有创建本地候选、Gate
结果或 Evidence 记录，没有运行 T12/P-chain，没有持久化结果，没有调用数据库、
cache、模型权重、runner 或新 Gate。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：64 passed
- `./scripts/verify_repository_boundary.sh`：passed
- `git diff --check`：passed

## 停止点

等待 ChatGPT 审核 Phase 4 contract-only PR。批准前不进入 Phase 5 endpoint
biology completion。
