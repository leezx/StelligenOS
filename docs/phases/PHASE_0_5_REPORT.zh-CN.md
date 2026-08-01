# Phase 0.5 Report

## 1. 执行摘要

Phase 0.5 已完成。这个阶段的目标不是实现新功能，而是把旧系统、外部证据和迁移边界彻底盘点清楚，避免把数据层、历史缓存或旧包裹直接拖进 StelligenOS。

本次盘点确认：

- `AssetGenOS` 是历史实现和旧资产系统的主要来源；
- `BACKUPS` 保存了多个旧版本归档，只能作为只读参考；
- `Zhixins-KB` 保存了提示词、证据摘录和历史决策记录，是知识来源，不是代码仓库；
- `AssetGenOS/data/adc_factory.sqlite3` 属于数据残留，不能留在实现仓库里。

Phase 0.5 的结论是：迁移对象已经分清，仓库边界已经写死，Phase 1 可以在不引入数据层的前提下继续。

## 2. 盘点对象

### 2.1 `AssetGenOS`

`AssetGenOS` 仍然是最重要的历史系统，但它已经不再被视为整个 StelligenOS 本体，而是被重新定位为 Opportunity Validation 阶段下的历史子系统来源。

盘点到的主要内容：

- 45 个 Gates 和 59 个 Models 的门控/模型契约；
- existing-binder、de novo antibody discovery、biotech asset due diligence 三个 GenModule；
- `MODEL_PROGRESS_VERSION.md` 中的阶段完成记录；
- `data/adc_factory.sqlite3` 这类数据残留。

### 2.2 `BACKUPS`

`BACKUPS` 中的归档文件只承担历史快照角色，不能被视为可执行工作区：

- `AssetGenOS-pre-packet-refactor-20260729-152514.tar.gz`
- `AssetGenOS-20260731.zip`
- `AssetGenOS-pre-standard-v1.1-20260729-151352.tar.gz`
- `AssetGenOS/archive/AssetGenOS-v0.1.0.tar.gz`

### 2.3 `Zhixins-KB`

`Zhixins-KB` 中的提示词和证据摘录构成了迁移的认知来源，尤其包括：

- Gate evidence extraction prompt 的历史版本；
- TWEAKR / partner gate template 类文档；
- 和资产验证、证据抽取、合作方 gate 相关的中文笔记。

## 3. 迁移矩阵

| Source | Disposition | Reason |
| --- | --- | --- |
| `AssetGenOS` 主仓 | `MIGRATE_WITH_ADAPTATION` | 历史系统来源，但不能原样并入 |
| Gate / Model contract | `MIGRATE_AS_IS` | 作为阶段契约参考保留 |
| existing-binder GenModule | `MIGRATE_AS_IS` | 历史能力原型可保留 |
| de novo antibody discovery GenModule | `MIGRATE_AS_IS` | 历史能力原型可保留 |
| biotech asset due diligence GenModule | `MIGRATE_AS_IS` | 已完成阶段性验证，可作为参考 |
| `BACKUPS` 归档 | `ARCHIVE` | 只读快照，不参与实现 |
| `Zhixins-KB` 证据与提示词 | `REFERENCE_ONLY` | 知识来源，不是实现仓库内容 |
| `AssetGenOS/data/adc_factory.sqlite3` | `MOVE_OUT_OF_REPO` | 数据残留，必须外置 |

## 4. 边界确认

- StelligenOS 是软件实现仓库，不是数据库。
- 允许少量受控示例、模板、golden test cases。
- 不允许大规模数据、原始输入、处理中间产物、缓存、输出、临时工件。
- 不允许把历史 SQLite、结果包或数据工作副本留在仓库里。

## 5. Phase 1 进入条件

Phase 1 可以开始，但前提是继续保持以下约束：

1. 只补最小目录骨架，不引入数据层。
2. 架构契约与运行 Prompt 分离。
3. 继续保留 Legacy Inventory 作为只读历史映射。
4. 如需样例，只允许小而受控的非数据化示例。

## 6. 结论

Phase 0.5 已完成，迁移矩阵已写清，系统边界已冻结。接下来进入 Phase 1 时，只做实现骨架，不做历史数据搬迁。

## 7. Recommendation

`PROCEED_TO_PHASE_1`
