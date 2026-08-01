# 任务交接备忘：Phase 3 AssetGenOS Gate 合同迁移

## 任务信息

- 任务编号：`task_20260801_phase3-assetgenos-gates`
- 分支：`task_20260801_phase3-assetgenos-gates`
- Base：Phase 2 合并后的 `main`
- PR：[#4](https://github.com/leezx/StelligenOS/pull/4)
- 状态：草稿 PR 已创建，等待 ChatGPT 审核

## 总纲与范围

本阶段只迁移 AssetGenOS Gate 体系的架构合同。45 Gate 的身份、分组和顺序被
视为冻结拓扑；Gate 的输入、输出和生命周期治理通过外部引用和 Protocol 接口
表达。StelligenOS 不执行 Gate，也不保存 Gate 结果。

## 改动

- `src/capabilities/gates.py`：Gate catalog、输入/输出 envelope 和外部 runtime port。
- `src/capabilities/__init__.py`：导出 Gate 合同。
- `src/contracts/gate_system.yaml`：拓扑、迁移和治理边界。
- `tests/test_phase3_gate_contracts.py`：45 Gate、顺序和外部引用边界测试。
- Phase 3 report、checklist、manifest 和 worklog。

## 明确未改动

- 未复制 AssetGenOS 的 Gate 文件、规则 JSON、数据库、模型记录、案例或证据。
- 未实现评分、调度、数据读取、结果写入或自动生命周期晋级。
- 未修改用户工作树中的 `prompts/GPT-Feedback.md`。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
- `./scripts/verify_repository_boundary.sh`
- `git diff origin/main...HEAD --check`
- `git diff --check`

## 下一步

创建 PR 后，将 PR 链接提交到网页版 ChatGPT 的“GitHub PR 信息”聊天，并使用
Phase Gate 审核指令。只有明确 `APPROVE` 才能标记本阶段完成并进入 Phase 4。
