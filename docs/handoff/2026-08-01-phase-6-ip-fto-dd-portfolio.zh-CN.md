# 任务交接备忘：Phase 6 IP/FTO、Due Diligence 和 Portfolio

## 任务信息

- 任务编号：`task_20260801_phase6-ip-fto-dd-portfolio`
- 分支：`task_20260801_phase6-ip-fto-dd-portfolio`
- Base：Phase 5 合并后的 `main` at `10fe06b`
- PR：[#7](https://github.com/leezx/StelligenOS/pull/7)
- 状态：草稿 PR 已创建，等待 ChatGPT 审核

## 范围

本阶段只建立三类跨阶段外部服务合同：IP/FTO、stage-aware Due Diligence 和
Portfolio。法律材料、尽调证据、资产组合、资本上下文和决策包全部由外部工作区管理。

## 改动

- `src/cross_cutting/ip_fto_due_diligence_portfolio.py`：请求、结果和三个外部 port。
- `src/cross_cutting/__init__.py`：导出跨阶段合同。
- `src/contracts/ip_fto_due_diligence_portfolio.yaml`：服务边界和禁止事项。
- `tests/test_phase6_cross_cutting.py`：阶段和外部引用测试。
- Phase 6 report、checklist、manifest 和 handoff。
- 同步 Phase 5 合并状态和 worklog。

## 明确未改动

- 未迁移专利、claim、FTO、尽调、Portfolio、资本、财务或任何结果记录。
- 未实现法律分析、风险评分、尽调执行、组合优化、资本分配或持久化。
- 未修改用户工作树中的 `prompts/GPT-Feedback.md`。

## 下一步

本地验证完成后创建 PR，提交到网页版 ChatGPT 的“GitHub PR 信息”聊天审核。
只有明确 `APPROVE` 才能合并并进入 Phase 7。
