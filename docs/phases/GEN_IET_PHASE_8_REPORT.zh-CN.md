# `gen_indication_endpoint_target` Phase 8 报告

- 阶段：Phase 8，End-to-End Pilot
- 分支：`task_20260801_gen-iet-phase8-external-pilot`
- 父阶段：Phase 7，已获 ChatGPT `APPROVE`
- 状态：`APPROVED_PHASE_8`
- Gate 变更：`NO_GATE_CHANGE`

## 本阶段实现

新增 `src/capabilities/end_to_end_pilot.py`，定义受限 CRC ClinicalFrame
pilot 的 external-only 编排合同：

- `EndToEndPilotRequest`：接收外部 CRC data bundle、ClinicalFrame、候选生成、生命周期合同、Phase 0-7 trace 和候选引用。
- `PilotCandidateOutcome`：为每个候选保留外部 disposition 和 decision trace，不预设 TWEAKR 胜出。
- `EndToEndPilotResult`：允许候选保留、HOLD、淘汰或全部不推进，资产生成资格固定为 false。
- `EndToEndPilotPort`：仅定义外部实现的 `run` 方法。

## 明确未执行

本阶段没有复制或读取 CRC 数据，没有运行完整闭环，没有执行 T0-T12、Gate、
Rule、Model 或 P-chain，没有生成资产，没有创建本地 pilot/candidate 结果，
没有持久化结果，也没有调用数据库、cache、模型权重、runner 或新 Gate。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：75 passed
- `./scripts/verify_repository_boundary.sh`：passed
- `git diff --check`：passed

## 停止点

ChatGPT 已批准 Phase 8 external pilot contract-only PR，可以进入 Phase 9。
该批准不包括真实 CRC pilot；Phase 9 必须从本阶段批准 tip 创建新分支并单独提交审核。
