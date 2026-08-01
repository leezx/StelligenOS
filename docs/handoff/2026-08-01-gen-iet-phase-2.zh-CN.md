# 任务交接备忘：`gen_indication_endpoint_target` Phase 2

- 任务编号：`task_20260801_gen-iet-phase2-clinical-frame`
- 父阶段：Phase 1，已获 ChatGPT `APPROVE`
- 当前状态：Phase 2 contract-only 完成，等待 ChatGPT PR 审核
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

先通过 ChatGPT 审核 Phase 2 PR；批准后才进入 Phase 3 target candidate generation contract/adapter 设计。

