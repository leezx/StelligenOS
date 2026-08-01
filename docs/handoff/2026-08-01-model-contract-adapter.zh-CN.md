# 任务交接备忘：AssetGenOS 模型契约适配层

- 任务编号：`task_20260801_model-contract-adapter`
- Base：架构冻结后的 `main` at `a0ad160`
- 目标：迁移 AssetGenOS 中可复用的模型身份与生命周期契约边界
- 当前状态：PR #12 已通过 ChatGPT 两轮审核，待 squash merge

## 本批迁移

- `src/cross_cutting/model_contracts.py`
  - 复用 `model_id@SemVer` 的纯解析规则。
  - 固定绑定 `ModelLifecycleStandard@1.0.0`。
  - 提供生命周期描述对象和外部治理请求端口。
- `src/contracts/model_lifecycle.yaml`
  - 声明模型身份、生命周期阶段和外部治理边界。
- `tests/test_model_contracts.py`
  - 验证有效/无效模型引用、标准绑定和外部请求边界。
- `logs/chatgpt-review-2026-08-01-model-contract-adapter.md`
  - 保存 ChatGPT 对代码批次和 metadata-only 更新的批准记录。

## 明确排除

- AssetGenOS 的旧 Pydantic 领域 schemas。
- `components/model_governance/` 下的治理记录和模型 registry。
- 模型文件、权重、校准结果、历史标签、缓存、数据库和运行结果。
- 本仓库内的模型读取、持久化、自动晋级和评分决策。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
- `./scripts/verify_repository_boundary.sh`
- `git diff --check`

## 审核状态

- 初次审核：`APPROVE`，可以合并 PR #12，并进入下一批迁移。
- metadata-only 复核：`APPROVE`，可以合并 PR #12。
