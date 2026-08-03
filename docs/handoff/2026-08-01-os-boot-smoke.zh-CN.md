# 任务交接备忘：OS Boot Smoke

- 任务编号：`task_20260801_os-boot-smoke`
- 分支：`task_20260801_os-boot-smoke`
- PR：**#16**（base 为 `task_20260801_assetgenos-contracts`，即 PR #15 的 head）
- 当前状态：`ROUND_1_REQUEST_CHANGES_ADDRESSED_PENDING_REVIEW`
- 目标：根据冻结 architecture 建立无数据 OS 启动入口，证明架构可以被加载并准备接入外部 runtime。
- **HEAD 与 aggregate diff 的权威来源是 GitHub PR #16 的实时值**；本文件中的数字均为撰写时快照。

## 依赖与阻断关系

依赖顺序为 **#15 → #16 → #17**。

- 本 PR 的 base 是 PR #15 的 head，因此 **PR #15 获批并合并是本 PR 的前提**。
- **PR #17（external runtime adapter）在本 PR 获批前仍被阻断。** 该 adapter 已在分支 `task_20260801_external-runtime-adapter` 上实现并开有 PR #17，不再是「本 PR 获批后才开始做」的未来步骤。本文件此前的描述与实际流程状态不符，已更正。

## 已实现

- `src/repository/boot.py`
  - 从权威定义加载四个生命周期阶段、9 个能力、3 个 Gate Group 和 2 条 Binder/ADC 路由。
  - 强制 workspace、run context、policy 使用 `external:` 引用。
  - 只返回静态 BootReport，不执行模型、不写入仓库、不生成结果。
- `scripts/boot_os.py`
  - 提供命令行启动入口并打印 JSON 架构计划。
- `tests/test_os_boot.py`
  - 覆盖精确身份与顺序、单一权威来源不变式、三个引用字段各自的本地值拒绝，以及 CLI 启动。

## Round 1 `REQUEST_CHANGES` 与修订

ChatGPT 对 HEAD `df8c851` 返回 `REQUEST_CHANGES`，三条阻断经核实均成立。

### 阻断 1：`boot.py` 重新硬编码生命周期与能力清单

核实成立。原 `boot.py` 在本模块内重新声明了 `LIFECYCLE_STAGES` 与 `CAPABILITY_IDS`；测试只断言数量 4/9/3/2，因此名称或顺序漂移仍能通过。

进一步核查发现两件事：

- 生命周期在 `src/lifecycle/state_machine.py` 已有权威定义 `LifecycleStage`，但其值是面向操作者的展示名（`"Opportunity Generation"`），与 `boot.py` 需要的机器可读 ID（`opportunity_generation`）是两种表示，因此当时被重新写了一份。
- **9 个能力在整个 `src/` 下没有任何权威定义**，`boot.py` 是唯一出处。架构契约 `docs/architecture/capabilities.zh-CN.md` 以英文列出这 9 项，是真正的契约权威。

修订建立单一权威来源：

| 位置 | 作用 |
|---|---|
| `src/lifecycle/state_machine.py` 新增 `LIFECYCLE_STAGE_IDS` | 由 `LifecycleStage` 枚举派生（`stage.name.lower()`），不再另写一份 |
| 新增 `src/capabilities/registry.py` | `CAPABILITY_NAMES` 为契约名，`CAPABILITY_IDS` 由其派生；这是能力的唯一机器可读来源 |
| `boot.py` | 改为导入上述两者，删除本地副本；`LIFECYCLE_STAGES` 仅作再导出并注明「不是第二份定义」 |
| `src/lifecycle/__init__.py`、`src/capabilities/__init__.py` | 导出新常量 |

测试从「数数量」改为精确断言：

- `test_boot_reports_exact_lifecycle_stages_in_order` 等四项，逐一比对完整 ID 元组与顺序，而非长度。
- `SingleSourceOfTruthTests` 六项，断言 boot 的输出来自权威定义、ID 由枚举／契约名派生，并且 **`boot.py` 源码中不得再出现任何生命周期或能力 ID 字面量**——这一条会在有人重新引入硬编码副本时直接失败。
- `test_capability_registry_matches_the_architecture_contract` 解析 `docs/architecture/capabilities.zh-CN.md` 的能力列表，与注册表逐项比对，使架构文档成为最终权威。

### 阻断 2：handoff 未反映真实流程状态

核实成立。本文件此前写「待创建 PR」，并把 external runtime adapter 写成「本 PR 获批后再新增」，而 PR #16、#17 都已存在。已更正，并在上方「依赖与阻断关系」明确 PR #17 在本 PR 获批前仍被阻断。

### 阻断 3：外部引用测试只覆盖 `workspace_ref`

核实成立。原测试只用 `/tmp/workspace` 试探 `workspace_ref`。已改为 `test_each_reference_field_rejects_a_local_path`，对 `workspace_ref`、`run_context_ref`、`policy_ref` 三个字段各自用 `/tmp/workspace`、`logs/worklog.md`、`./local` 三种本地形式交叉验证，共 9 组 subTest。

### 变异测试证据

为验证新测试确实能捕捉漂移，逐个注入缺陷确认失败，随后从备份还原：

| 注入的缺陷 | 结果 |
|---|---|
| 生命周期阶段重命名（`ASSET_DEVELOPMENT` → `ASSET_ADVANCEMENT`） | `FAILED (failures=2)` |
| 调换两个 capability 的顺序 | `FAILED (failures=2)` |
| 架构文档删掉一项能力（与注册表不一致） | `FAILED (failures=1)` |
| `boot.py` 重新硬编码生命周期清单 | `FAILED (failures=1)` |
| 全部还原 | `OK` |

## 明确未改动

- 未改动 `ALLOWED_TRANSITIONS`、`can_transition` 或任何生命周期转换规则。
- 未改动 `LifecycleStage` 的成员、取值或顺序。
- 未改动 45-Gate 拓扑、`GATE_GROUPS`、`ROUTE_IDS` 或任何 Gate/Model/Profile 定义。
- 未改动 `docs/architecture/capabilities.zh-CN.md`（仅作为测试读取的权威来源）。
- 未改动 `scripts/boot_os.py`。
- 未改动 `.gitignore` 与 `scripts/verify_repository_boundary.sh`。
- 未新增数据、缓存、结果或临时产物。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1，逐模块运行 tests/test_*.py
结果：ALL OK —— 11 modules / 65 tests
      本 PR 自身新增：tests/test_os_boot.py 由 3 项增至 15 项
      合并 base（PR #15 的 Round 1 修订）后又并入其 10 项完整性测试

历史数字（仅供追溯）：修订前 43 项；本 PR 修订后、合并 base 前为 55 项。
验证数字的权威来源是当前 HEAD 上实际运行的结果。

命令：bash scripts/verify_repository_boundary.sh
结果：本地工作区 exit=1，违规项 `.claude`
      该目录在本分支创建之后才出现，修复位于已获批的链顶 PR #43，
      本 PR 不重复修复以避免同文件合并冲突。

命令：git diff --check
结果：通过
```

## 未决问题与风险

- `src/capabilities/registry.py` 是新增文件，链上后续 27 个分支都没有它。这不会产生冲突（纯新增），但合并顺序仍须自底向上。
- GitHub 上没有 commit status 或 Actions workflow，因此上述验证数字目前只能由仓库记录佐证，无法由 CI 独立复核。建议另立任务引入 CI。
- 合并后 `logs/worklog.md` 会与链上后续分支产生追加式冲突，解决方式是按时间顺序保留两侧。

## 下一步

1. 提交 ChatGPT 复审本 PR。
2. 只有收到 `APPROVE` 后，由人类负责人决定合并，且须在 PR #15 合并之后。
3. 本 PR 获批后才推进 PR #17。
