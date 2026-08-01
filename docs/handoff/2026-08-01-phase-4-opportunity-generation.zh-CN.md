# 任务交接备忘：Phase 4 Opportunity Generation

## 任务信息

- 任务编号：`task_20260801_phase4-opportunity-generation`
- 分支：`task_20260801_phase4-opportunity-generation`
- Base：Phase 3 合并后的 `main` at `505ddd1`
- PR：[#5](https://github.com/leezx/StelligenOS/pull/5)
- 状态：草稿 PR 已创建，等待 ChatGPT 审核

## 范围

本阶段只建立 Opportunity Generation 的最小软件接口。知识、靶点、临床上下文、
生成策略、运行上下文以及返回的 Opportunity、TargetHypothesis、Evidence 和 run
均由外部工作区管理；StelligenOS 不生成、保存或推进任何机会记录。

## 改动

- `src/capabilities/opportunity_generation.py`：request/result 合同和外部 port。
- `src/contracts/opportunity_generation.yaml`：阶段、引用和晋级边界。
- `tests/test_phase4_opportunity_generation.py`：外部引用边界测试。
- Phase 4 report、checklist、manifest 和 handoff。
- 同步 Phase 3 合并状态和 worklog。

## 明确未改动

- 未创建对象记录、数据集、数据库、缓存、输出或临时文件。
- 未实现候选生成、证据处理、模型调用、排序或自动生命周期晋级。
- 未修改用户工作树中的 `prompts/GPT-Feedback.md`。

## 下一步

本地验证完成后创建 PR，提交到网页版 ChatGPT 的“GitHub PR 信息”聊天审核。
只有明确 `APPROVE` 才能合并并进入 Phase 5。
