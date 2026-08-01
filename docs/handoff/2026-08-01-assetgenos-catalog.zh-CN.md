# 任务交接备忘：AssetGenOS Catalog 迁移

- 任务编号：`task_20260801_assetgenos-contracts`
- 目标：将 AssetGenOS 中可复用的纯软件定义迁移到 StelligenOS，不迁移数据或运行态。
- 当前状态：迁移分支已完成本地验证，待创建 PR 并提交 ChatGPT 审核。

## 已迁移

- `genmodules/assetgenos_catalog/contracts/`：7 个共享契约。
- `genmodules/assetgenos_catalog/gates/`：45 个 ADC Gate 定义。
- `genmodules/assetgenos_catalog/models/`：59 个 Model 定义。
- `genmodules/assetgenos_catalog/profiles/`：53 个 Profile 定义。
- `genmodules/assetgenos_catalog/module.yaml`：数量、身份和外部执行边界。

原始目录结构和版本路径保持不变，方便后续对照和审计。

## 明确未迁移

- `model_governance/`、`model_work_packages/` 和审计、校准、review 记录。
- 数据集、历史标签、数据库、缓存、生成结果、模型权重和 runner。
- 任何会在 StelligenOS 内保存输入或结果的执行逻辑。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 40 passed
- `./scripts/verify_repository_boundary.sh`: passed
- `git diff --check`: passed

## 下一步

1. 创建 PR 到 `main`。
2. 通过网页版 ChatGPT 的 GitHub 来源审核迁移边界、数量和引用。
3. 只有收到 `APPROVE` 后合并。
