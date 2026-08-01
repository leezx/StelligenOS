# 任务交接备忘：biotech_asset_due_diligence 迁移

- 任务编号：`task_20260801_biotech-dd`
- 目标：将 AssetGenOS Due Diligence Phase 1A 的纯软件合同边界迁移到 StelligenOS。
- 当前状态：已完成实现，等待 PR 审核；未合并。

## 本次已迁移

- `genmodules/biotech_asset_due_diligence/core/`
  - 不可变核心记录、稳定内容寻址 ID、外部 ArtifactRef 校验、严格合同验证。
- `genmodules/biotech_asset_due_diligence/adapters/antibody_engineering.py`
  - 只读消费外部 Binder `0.4.0` 制品，拒绝旧版或未通过合同验证的制品。
- `genmodules/biotech_asset_due_diligence/contracts/`
  - Phase 1A 输入、输出和证据链对象合同。
- `genmodules/biotech_asset_due_diligence/module.yaml`
  - 模块身份、外部输入/输出、持久化禁止和声明性禁止项。

## 明确未迁移

- `examples/` 中的真实/示例输入。
- `archive/` 历史压缩包。
- `run_pipeline.py`、报告生成、运行目录和任何结果写入逻辑。
- 数据库、缓存、模型权重、虚拟环境和外部运行产物。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 29 passed
- `./scripts/verify_repository_boundary.sh`: passed
- `git diff --check`: passed
- 迁移目录未发现数据后缀、样例目录、归档或 runner。

## 审核重点

1. 是否保持 StelligenOS 的“软件仓库、外部数据和运行结果”边界。
2. Binder `0.4.0` 兼容校验是否明确且未错误放宽版本。
3. SystemRecommendation 与 HumanDecision 是否仍然分离。
4. 是否需要在下一 PR 再引入外部运行时端口；本 PR 不包含该扩展。
