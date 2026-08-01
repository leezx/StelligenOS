# Phase 0.5 审核清单

- 确认 `AssetGenOS` 已被重新定义为历史来源，而不是整个 StelligenOS 系统。
- 确认遗留盘点覆盖主仓库、GenModules、备份归档和知识库证据来源。
- 确认迁移矩阵包含 `MIGRATE_AS_IS`、`MIGRATE_WITH_ADAPTATION`、`ARCHIVE`、`REFERENCE_ONLY` 和 `MOVE_OUT_OF_REPO` 决策。
- 确认仓库边界仍禁止大型数据集、原始输入、中间文件、缓存、输出和临时产物。
- 确认 `AssetGenOS/data/adc_factory.sqlite3` 被视为数据残留，不作为仓库内容。
- 确认 Phase 0 和 Phase 0.5 产物均存在，并一致写明 `PROCEED_TO_PHASE_1`。
- 确认移除 macOS 元数据允许项后，仓库边界脚本仍然通过。
