# `gen_indication_endpoint_target` Phase 2 报告

- 阶段：Phase 2，T0-T1 Clinical Frame Pipeline
- 分支：`task_20260801_gen-iet-phase2-clinical-frame`
- 状态：`APPROVED_PHASE_2`
- Gate 变更：`NO_GATE_CHANGE`

## 本阶段实现

新增 `src/capabilities/clinical_frame_pipeline.py`，定义外部-only 的 T0-T1 pipeline port：

- `ClinicalFramePipelineRequest`：search scope、clinical unmet need、T0/T1 input、policy 和 run context 均为 `external:` 引用，并限制 candidate budget。
- `ClinicalFramePipelineResult`：ClinicalFrame、T0、T1、Evidence、missing information 和 run 结果均为 `external:` 引用。
- `ClinicalFramePipelinePort`：只定义外部实现应提供的 `run` 方法。

## 明确未执行

本阶段没有读取 clinical unmet need 数据，没有运行 T0/T1，没有创建 ClinicalFrame 记录，没有采集 Evidence，没有生成 target，没有写入结果，也没有调用数据库、缓存、模型或 runner。

该 port 只为外部 runtime 提供安全边界；真实运行必须在外部 workspace 中完成，并通过现有 External Runtime Adapter 接入。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：58 passed
- `./scripts/verify_repository_boundary.sh`：passed
- `git diff --check`：passed

## 停止点

ChatGPT 已批准 Phase 2 contract-only PR，可以进入 Phase 3。该批准不包括 Phase 3 实现或真实资产生成；Phase 3 必须从本阶段批准 tip 创建新分支并单独提交审核。
