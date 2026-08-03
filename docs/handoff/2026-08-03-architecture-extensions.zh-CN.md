# 任务交接备忘：架构文档版本规则与扩展插件包

## 任务信息

- 任务编号：`task_20260803_architecture-extensions`
- 分支：`task_20260803_architecture-extensions`
- 分支基点：`94dc6c8`（PR #42 已批准 tip，非 `main`；`main` 当前落后，尚未包含架构说明文档）
- PR：#43（base 为 PR #42 已批准 head `task_20260802_current-architecture-expert-review-doc`，非 `main`）
- Aggregate diff：1 commit、26 files、`+2465/-0`
- 当前状态：`PENDING_CHATGPT_REVIEW`
- 时间：`2026-08-03 10:25 EDT`
- 任务性质：documentation + extension shells + repository hygiene
- Gate 变更：`NO_GATE_CHANGE`
- 内核代码变更：`NO_KERNEL_CODE_CHANGE`

## 本次改动

### 1. 架构文档版本规则（修复重命名导致的引用断裂）

工作区此前把已批准的架构说明文档重命名为 `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN v1.md`（含空格），导致 `docs/handoff/`、`logs/worklog.md` 和 `prompts/GPT-Feedback.md` 中的路径引用全部失效。已确认该重命名为纯改名，正文无改动。

采用「稳定规范路径 + 文档内版本区块 + 只读快照」替代「文件名带版本号」：

- 恢复规范路径 `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`，删除含空格的文件。
- 在该文档新增第 0 节「文档版本」，记录文档 ID、当前版本 `v1`、审核状态和快照位置。
- 新增 `docs/architecture/versions/`，写入版本规则 `README.md` 和只读快照 `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.v1.zh-CN.md`。

选择理由：`logs/worklog.md` 和 `logs/chatgpt-review-*.md` 是带时间戳的追加式审计记录，`docs/handoff/` 记录每个 PR 的交接事实。若把版本号写进规范路径文件名，每次升版都必须回头改写已被 ChatGPT 批准的历史记录，破坏审计轨迹不可变性。

### 2. 扩展插件包 `extensions/`

按 `prompts/GPT-Feedback.md` `# v4` 的四个一级风险建立扩展包。**不改动内核**。

| ID | 名称 | 状态 | 说明 |
|---|---|---|---|
| `EXT-01` | `ground_truth_learning_loop` | `shell_only` | 结局回写 Rule/Model/Gate 的改动分类与治理级别。 |
| `EXT-02` | `dynamic_gate_context` | `shell_only` | `Target x Clinical Context` 复合身份，适配器方式，不改 45-Gate 拓扑。 |
| `EXT-03` | `asset_search_engine` | `shell_only` | 十条搜索轴登记；显式记录「标准 ADC 平台垫着」为推迟而非默认。 |
| `EXT-04` | `stop_rule` | `active_design` | 可执行的 `EvidenceSufficiencyContract` 与三值裁决，带单元测试。 |

`extensions/README.md` 固化四条内核不变式：单向依赖（内核不得导入扩展）、内核冻结边界不动、扩展不产生决策、仓库仍 data-free。

`EXT-04` 的设计要点：把「证据是否充分」和「是否还允许继续搜索」分成两个独立维度，裁决为三值。搜索预算耗尽产出 `INSUFFICIENT_EXHAUSTED` 并强制升级为人类决策，**不得转为 FAIL**——否则等于把「没找到足够证据」伪装成「target 不好」，违反内核设计原则第 3 条。

`DEFAULT_SUFFICIENCY_BASELINES` 的阈值来自外部专家建议值，标记为 `proposed_baseline_requires_expert_calibration`，不是经过校准的科学阈值。

### 3. 二级风险登记

`extensions/BACKLOG.zh-CN.md` 登记七个二级风险 `BL-01` 到 `BL-07`，全部不做，只登记。其中 `BL-01`（evidence independence 定义不严）已在 `EXT-04` 的 `known_limitations` 中标记为其正确性前置条件。

### 4. 仓库卫生

- `.gitignore`：新增 `__pycache__/`、`*.py[cod]`、`.claude/settings.local.json`、`.venv/`、`venv/`、`.pytest_cache/`。此前只有 `.DS_Store`，导致跑完测试后 `tests/test_assetgenos_modules.py` 与 `tests/test_gen_indication_endpoint_target.py` 会把自己产生的 `__pycache__` 判定为 data-bearing runtime artifact 而失败。
- `scripts/verify_repository_boundary.sh`：allowlist 新增 `extensions` 和 `.claude`。此前该脚本因顶层存在 `.claude/` 而失败（`.claude/settings.local.json` 被用户全局 gitignore 忽略，故 `git status` 干净但 `find` 仍可见），而 AGENTS.md 要求新增顶层目录前必须运行此脚本。

### 5. 导航更新

`README.md` 与 `LINKS.md` 增加 `extensions/` 与版本目录入口。

## 明确未改动

- 未修改 `docs/architecture/contract.zh-CN.md`、`capabilities.zh-CN.md`、`lifecycle.zh-CN.md`、`release.zh-CN.md`。
- 未修改四阶段生命周期、七类核心对象、45-Gate 拓扑与身份。
- 未修改 `genmodules/` 下任何 gate/model/profile 定义或 module.yaml。
- 未修改 `src/` 下任何内核代码。
- 未修改 `docs/tasks/CRC_GATE_SCORING_CONTRACT.zh-CN.md`（该契约已获 ChatGPT `APPROVE`，改动它等于重开已关闭的审核门）。
- 未修改任何 `logs/chatgpt-review-*.md` 历史审核记录。
- 未执行 CRC Gate scoring、T12、pair ranking/recommendation 或 asset generation。
- 未新增数据、缓存、结果或临时产物。
- `docs/.DS_Store` 为既有已跟踪文件，不在本次范围内，未处理。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1，逐模块运行 tests/test_*.py（23 个模块）
结果：ALL 23 TEST MODULES OK（新增 tests/test_stop_rule_extension.py 17 项、
      tests/test_extension_boundary.py 11 项，共 28 项新测试全部通过）

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.（修复前为 exit=1，违规项 .claude）

命令：bash tests/test_git_sync.sh
结果：git_sync behavior tests passed (A-D).

命令：git diff --check
结果：通过，无空白错误
```

## 未决问题与风险

- `EXT-04` 的三组 baseline 阈值未经科学校准，激活前必须逐 Gate 由领域专家复核。
- `EXT-04` 依赖「独立证据数」，而 `BL-01` 未解决，该判据可能被重复来源虚增，偏向过早判定充分。
- 规范路径文档当前版本 `v1` 与快照 `v1` 之间存在且仅存在第 0 节版本元数据这一处差异，已在 `docs/architecture/versions/README.md` 中显式说明。
- 扩展目录未加 `__init__.py`，依赖 Python 3 命名空间包，与 `src/` 现状一致（`src/` 亦无顶层 `__init__.py`）。

## 下一步

- 推送分支并创建 PR，提交 ChatGPT 审核。
- 在获得 `APPROVE` 前，不得把任何扩展从 `shell_only`/`active_design` 提升为 `governed`，不得开始 `EXT-04` 的逐 Gate 阈值实例化，也不得继续 CRC 批次审核以外的工作。

## 数据边界声明

本仓库只保存架构系统文档、代码和小型治理文本；本任务没有新增任何数据、缓存或结果文件。所有数据和处理仍位于外部工作区。
