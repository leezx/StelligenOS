# 任务交接备忘：AssetGenOS GenModule 迁移

- 任务编号：`task_20260801_assetgenos-migration`
- Base：架构冻结后的 `main` at `acd2f2c`
- 目标：将 AssetGenOS 的两个生成模块迁移到 StelligenOS 的 Asset Generation 生命周期
- 当前状态：开发中，等待 PR 和 ChatGPT 审核

## 已迁移

- `genmodules/antibody_binder_asset_engineering/`，版本 `0.4.0`
  - 保留 16 阶段、输入/输出契约、SHA-256 产物校验和外部执行默认关闭策略。
- `genmodules/epitope_conditioned_de_novo_antibody_discovery/`，版本 `0.1.0`
  - 保留 15 阶段、输入验证、外部工具探测和“不凭空生成抗体序列”边界。
- `tests/test_assetgenos_modules.py`
  - 只验证模块身份、阶段目录、契约版本和仓库边界。

## 明确排除

- `AssetGenOS/data/adc_factory.sqlite3`
- `AssetGenOS/.venv/`、缓存和 `__pycache__`
- 历史归档、真实/示例输入、运行结果、报告、模型权重和数据构建脚本
- SQLite、数据库服务、内部结果持久化和自动生命周期晋级

## 外部边界

模块输入、证据、工具环境、模型权重、观察结果、候选资产、报告和运行目录
必须由外部工作区提供。`--output-root` 不得指向本仓库；外部科学执行保持
`disabled_by_default`，只有显式允许时才可调用。

## 后续建议

1. ChatGPT 审查本 PR 的迁移完整性、模块版本和零数据边界。
2. 审核通过后，再迁移 Gate/Model 运行时中的纯契约适配层；不得迁移旧数据库层。
3. 最后再单独评估持续学习和历史标签服务是否能改造成外部存储端口。
