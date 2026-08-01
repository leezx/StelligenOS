# `gen_indication_endpoint_target` Phase 3 报告

- 阶段：Phase 3，Target Candidate Generation
- 分支：`task_20260801_gen-iet-phase3-target-candidates`
- 父阶段：Phase 2，已获 ChatGPT `APPROVE`
- 状态：`COMPLETED_PENDING_REVIEW`
- Gate 变更：`NO_GATE_CHANGE`

## 本阶段实现

新增 `src/capabilities/target_candidate_generation.py`，定义单一
ClinicalFrame 内有限候选生成的 external-only port：

- `TargetCandidateGenerationPolicy`：配置化候选预算、最少独立正证据组和目标身份解析要求；禁止 model-only/rule-only generation。
- `TargetCandidateGenerationRequest`：只接受 external ClinicalFrame、证据范围、policy 和 run context 引用，并要求正的候选预算。
- `TargetCandidateGenerationResult`：只返回 external TargetCandidate、Evidence、missing information 和 run 引用；允许空候选组以表达暂时没有可保留候选。
- `TargetCandidateGenerationPort`：仅定义外部实现的 `generate` 方法。

## 明确未执行

本阶段没有读取公共证据或临床数据，没有生成 TargetCandidate/Evidence
记录，没有执行 P-chain，没有运行 T-gate，没有持久化结果，没有调用数据库、
cache、模型权重、runner 或新 Gate。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：61 passed
- `./scripts/verify_repository_boundary.sh`：passed
- `git diff --check`：passed

## 停止点

等待 ChatGPT 审核 Phase 3 contract-only PR。批准前不进入 Phase 4 early
T-Gate candidate reduction。
