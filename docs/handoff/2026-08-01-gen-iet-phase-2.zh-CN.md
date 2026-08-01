# 任务交接备忘：`gen_indication_endpoint_target` Phase 2

- 任务编号：`task_20260801_gen-iet-phase2-clinical-frame`
- 父阶段：Phase 1，已获 ChatGPT `APPROVE`
- 当前状态：Phase 2 contract-only 完成，ChatGPT 已 APPROVE，可进入 Phase 3
- Gate 变更：`NO_GATE_CHANGE`

## 已实现

- 新增外部-only `ClinicalFramePipelineRequest`、`ClinicalFramePipelineResult` 和 `ClinicalFramePipelinePort`。
- 强制 search scope、clinical unmet need、T0/T1 input、policy、run、ClinicalFrame、Evidence 和 missing information 引用使用 `external:`。
- 限制 candidate budget 为正整数，禁止本地执行和持久化。
- 新增 Phase 2 报告、manifest 和边界测试。

## 未执行

- 未读取 clinical unmet need 数据。
- 未运行 T0/T1。
- 未生成 ClinicalFrame、TargetCandidate 或 Evidence 记录。
- 未调用数据库、cache、result、weights、runner 或新 Gate。

## 验证

- 58 tests passed
- repository boundary passed
- `git diff --check` passed

## 下一步

ChatGPT 已通过 Phase 2 审核，记录见 `logs/chatgpt-review-2026-08-01-gen-iet-phase2.md`。下一步已从本阶段批准 tip 建立 `task_20260801_gen-iet-phase3-target-candidates`，完成 Phase 3 target candidate generation contract-only port；该阶段需单独提交 PR 并再次经 ChatGPT 审核。
