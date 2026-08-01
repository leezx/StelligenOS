# 任务交接备忘：`gen_indication_endpoint_target` Phase 3

- 任务编号：`task_20260801_gen-iet-phase3-target-candidates`
- 父阶段：Phase 2，已获 ChatGPT `APPROVE`
- 当前状态：Phase 3 contract-only 完成，等待 ChatGPT PR 审核
- Gate 变更：`NO_GATE_CHANGE`

## 已实现

- 新增 external-only `TargetCandidateGenerationPolicy`、`TargetCandidateGenerationRequest`、`TargetCandidateGenerationResult` 和 `TargetCandidateGenerationPort`。
- 以单一 ClinicalFrame 为边界，使用配置化 candidate budget 和 minimum distinct positive evidence groups 限制候选规模。
- 强制 ClinicalFrame、证据范围、policy、run、TargetCandidate、Evidence 和 missing information 引用使用 `external:`。
- 明确禁止 model-only/rule-only generation，不把候选生成 port 变成 Gate 或 evaluator。

## 未执行

- 未读取公共证据或临床数据。
- 未创建本地 TargetCandidate 或 Evidence 记录。
- 未执行 P-chain、T-gate、数据库、cache、result、weights、runner 或新 Gate。

## 验证

- 61 tests passed
- repository boundary passed
- `git diff --check` passed
- Phase 0/1/2/3 manifest YAML parse passed

## 下一步

等待 ChatGPT 审核并批准 Phase 3 PR；批准前不得进入 Phase 4 early T-Gate candidate reduction。
