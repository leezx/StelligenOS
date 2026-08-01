# 任务交接备忘：Phase 5 Binder/ADC 生成路线

## 任务信息

- 任务编号：`task_20260801_phase5-binder-adc-routes`
- 分支：`task_20260801_phase5-binder-adc-routes`
- Base：Phase 4 合并后的 `main` at `d2f8c09`
- PR：[#6](https://github.com/leezx/StelligenOS/pull/6)
- 状态：ChatGPT 已批准，等待 PR 合并

## 范围

本阶段只建立 AssetGenOS 两条 Binder/ADC GenModule 路线的架构合同：Existing-Binder
Asset Engineering 和 Epitope-Conditioned de novo Antibody Discovery。路线运行时、
科学工具、模型、观察、候选、证据和报告全部由外部工作区管理。

## 改动

- `src/capabilities/binder_adc_routes.py`：两条路线、阶段目录、request/result 和外部 port。
- `src/contracts/binder_adc_routes.yaml`：路线版本、阶段数量和禁止事项。
- `tests/test_phase5_binder_adc_routes.py`：路线数量、阶段和引用边界测试。
- Phase 5 report、checklist、manifest 和 handoff。
- 同步 Phase 4 合并状态和 worklog。

## 明确未改动

- 未复制 AssetGenOS GenModule 代码、示例输入、模型权重、科学工具、数据或输出。
- 未实现序列工程、de novo 设计、排序、实验设计、报告生成或 Gate 写入。
- 未修改用户工作树中的 `prompts/GPT-Feedback.md`。

## 下一步

PR #6 已提交到网页版 ChatGPT 的“GitHub PR 信息”聊天并获得明确 `APPROVE`，
可以进入 Phase 6。合并后从最新 `main` 创建 Phase 6 分支。
