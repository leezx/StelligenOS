# 任务交接备忘：AssetGenOS Catalog 迁移

- 任务编号：`task_20260801_assetgenos-contracts`
- 分支：`task_20260801_assetgenos-contracts`
- PR：**#15**（base 为 `main`，是整条 28 层 PR 链的链底）
- 当前状态：`ROUND_1_REQUEST_CHANGES_ADDRESSED_PENDING_REVIEW`
- 目标：将 AssetGenOS 中可复用的纯软件定义迁移到 StelligenOS，不迁移数据或运行态。
- **HEAD 与 aggregate diff 的权威来源是 GitHub PR #15 的实时值**；本文件中的数字均为撰写时快照。

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

## Round 1 `REQUEST_CHANGES` 与修订

ChatGPT 对 HEAD `4b8d029` 返回 `REQUEST_CHANGES`，两条阻断经核实均成立。

### 阻断 1：handoff 与实际流程状态不一致

本文件此前写「待创建 PR」，而 PR #15 已存在且为 OPEN。已更新为记录 PR 编号、base、状态与验证结果。

### 阻断 2：测试只验证文件数量，无法证明迁移内容完整正确

核实成立。原 `tests/test_assetgenos_modules.py` 只断言 45/59/53/7 这几个计数以及禁止目录名不存在；错误的 Gate ID、漂移的版本或损坏的 YAML 都能通过。

已新增 `MigratedYamlIntegrityTests`，共 10 项：

| 测试 | 作用 |
|---|---|
| `test_every_migrated_yaml_document_parses` | `genmodules/` 下全部 200 个 YAML 逐个 `yaml.safe_load`，失败时报出文件与错误 |
| `test_migrated_yaml_count_is_not_silently_reduced` | 防止上一条在被清空的目录树上「空转通过」 |
| `test_catalog_gate_ids_match_the_frozen_registry_exactly` | 45 个 gate_id 与 `src/capabilities/gates.py` 的 `GATE_IDS` 集合完全相等 |
| `test_catalog_gate_groups_match_the_frozen_registry` | 每个 Gate 的 `gate_group` 与冻结 Registry 的分组逐一相等 |
| `test_catalog_gate_order_matches_the_frozen_registry` | 按 `sequence` 排序后的 gate_id 序列与 `GATE_IDS` 顺序完全一致 |
| `test_catalog_gate_sequences_are_unique` | sequence 无重复 |
| `test_catalog_gate_versions_are_semver` | `gate_version` 必须是 `x.y.z` |
| `test_catalog_gate_identity_is_consistent_with_its_path` | gate_id 与 gate_group 必须出现在其文件路径中，捕捉被挪错目录的 Gate |
| `test_every_model_binds_a_gate_in_the_frozen_registry` | 59 个 Model 的 `gate_id` 必须指向冻结 Registry 中真实存在的 Gate |
| `test_every_model_version_is_semver` | `model_version` 必须是 `x.y.z` |

#### 一处必须说明的设计取舍：比较顺序，不比较 sequence 数值

目录使用**稀疏编号**（target 0-12、product 20-35、commercial 40-55，在 13-19 与 36-39 处留空），而 `src/capabilities/gates.py` 的 `GATE_CATALOG` 使用**连续编号** 0-44。两个来源的 sequence 数值本就不同，真正需要成立的不变式是**相对顺序**。

因此测试断言「按 sequence 排序后的序列 == `GATE_IDS`」，而不是逐个比对数值。若照字面比数值，测试会失败，而修复方向可能变成去改其中一侧——那会破坏冻结拓扑。这一编号差异是既有状态，本 PR 未改动任何一侧，但记录在此以免将来被误判为 bug。

#### 变异测试证据

为验证新测试确实能捕捉审核指出的缺陷类型，逐个注入缺陷确认失败，随后还原：

| 注入的缺陷 | 结果 |
|---|---|
| 在 gate.yaml 末尾追加损坏 YAML | `FAILED (failures=1, errors=6)` |
| `gate_id` 拼错一个字母 | `FAILED (failures=3, errors=1)` |
| `gate_group` 从 target 改为 product | `FAILED (failures=2)` |
| `sequence` 由 7 改为 33（打乱顺序） | `FAILED (failures=2)` |
| `gate_version` 由 `0.2.0` 改为 `0.2` | `FAILED (failures=1)` |
| model 的 `gate_id` 指向不存在的 Gate | `FAILED (failures=1)` |
| 全部还原 | `OK` |

## 明确未改动

- 未改动任何 gate/model/profile/contract YAML 内容。
- 未改动 `src/` 与 `genmodules/` 下任何代码或契约。
- 未改动 `module.yaml` 的数量声明与外部执行边界。
- 未改动 `.gitignore` 与 `scripts/verify_repository_boundary.sh`（见下方说明）。
- 未新增数据、缓存、结果或临时产物。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1，逐模块运行 tests/test_*.py
结果：ALL OK —— 10 modules / 50 tests
      （修订前 40 项，新增 MigratedYamlIntegrityTests 10 项）

命令：bash scripts/verify_repository_boundary.sh
结果：本地工作区 exit=1，违规项 `.claude`
      临时移开 `.claude` 后 exit=0，Repository boundary check passed.

命令：git diff --check
结果：通过
```

### 关于 boundary script 的 `.claude` 违规

`.claude/settings.local.json` 是本地 Claude Code 工具配置，被用户全局 gitignore 忽略，因此 `git status` 干净但脚本用 `find` 仍可见。该目录在本分支创建之后才出现，不是本 PR 引入的内容。

对应修复（精确豁免 `.claude/settings.local.json` 单条路径，该目录下其他内容仍判违规）位于链顶 PR #43，已获 `APPROVE`。本 PR **不重复该修复**，以避免与 PR #43 在同一文件上产生合并冲突。在干净 clone 上本分支的边界检查是通过的。

## 未决问题与风险

- 本 PR 是 28 层 PR 链的链底。`main` 自 2026-08-01 `f8206e9` 起未移动，链上共 87 个 commit。本 PR 获批并合并是后续 27 个 PR 进入 `main` 的前提。
- 新增测试依赖 `pyyaml`，而仓库没有任何依赖声明文件（无 `requirements.txt`／`pyproject.toml`）。这是既有状态，建议另立任务处理。
- GitHub 上没有 commit status 或 Actions workflow，因此上述验证数字目前只能由仓库记录佐证，无法由 CI 独立复核。建议另立任务引入 CI，不在本 PR 范围内。
- 合并本 PR 后 `logs/worklog.md` 会与链上后续分支产生追加式冲突（各分支各自追加过条目）。解决方式是按时间顺序保留两侧，不是取舍其一。

## 下一步

1. 提交 ChatGPT 复审本 PR。
2. 只有收到 `APPROVE` 后，由人类负责人决定合并。
3. 依赖顺序为 #15 → #16 → #17；本 PR 获批后才推进 #16。
