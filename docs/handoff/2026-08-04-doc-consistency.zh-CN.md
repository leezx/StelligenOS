# 任务交接备忘：架构与文档一致性同步

- 任务编号：`task_20260804_doc-consistency`
- 分支：`task_20260804_doc-consistency`（从 `main` `a5bf77f` 创建）
- PR：**PR B**，base 为 `main`
- 当前状态：`ROUND_1_REQUEST_CHANGES_ADDRESSED_PENDING_REVIEW`
- 变更性质：文档与扩展元数据同步 + 三项新守卫测试 + EXT-02 升版 `0.1.0` → `0.2.0`，**无内核变更、无行为变更**
- Gate 变更：`NO_GATE_CHANGE`

## 三个不一致

### 1. EXT-02 的状态描述已经不是事实

EXT-02 `dynamic_gate_context` 的立论是「真正的评分对象不是 `Target` 而是
`Target × Clinical Context`，**用适配器解决，不改内核**」。

v5 clinical hypothesis 架构（PR #45，合并为 `a5bf77f`）实现的正是这件事，而且是改在内核里：
`ClinicalHypothesis` = Target × Anchor Clinical Context × Intended Benefit/Product Hypothesis，
Gate 输入携带 `clinical_hypothesis_ref` 与递进 lock state。

但 `extension.yaml` 仍写着 `status: shell_only` 和 `design_constraint: 不改内核`。

### 2. 两份规范性文档仍声明「七类核心对象是稳定边界」

`src/contracts/core_objects.yaml`（version 1.1）已列八类，v5 插入了 `ClinicalHypothesis`。

命中的文件分两类，本 PR 只改前者：

| 类别 | 文件 | 处理 |
|---|---|---|
| 规范条文 | `docs/architecture/release.zh-CN.md`（冻结范围）、`extensions/README.md`（内核不变式 2） | 已改 |
| 历史审计记录 | `logs/worklog.md`、`logs/chatgpt-review-*.md`、`docs/handoff/*`、`docs/phases/*`、`docs/architecture/versions/*` | **不动** |

历史记录记的是当时的事实，按追加式审计的不可变原则不得改写。

### 3. 架构文档完全没有提到 `extensions/`

`docs/architecture/` 下零处提及。只读架构契约的专家不会知道 `EXT-01`..`EXT-04` 与
`BL-01`..`BL-07` 存在。

## 变更

| 文件 | 变更 |
|---|---|
| `extensions/dynamic_gate_context/extension.yaml` | `status` → `partially_absorbed`；`extension_version` `0.1.0` → `0.2.0`；新增 `absorbed_by_kernel` 与 `remaining_scope`（`RS-01`..`RS-05`）；`design_constraint` 改为只约束剩余范围；`future_direction` 与 `activation_requirements` 按 v5 后的现实更新。 |
| `extensions/dynamic_gate_context/contracts.py` | `EXTENSION_VERSION` 同步为 `0.2.0`；模块 docstring 首行由 `shell only` 改为 `partially absorbed into the v5 kernel` 并指向 `remaining_scope`。合同本身未改。 |
| `extensions/dynamic_gate_context/README.md` | 顶部新增「状态变更说明」，列出内核已覆盖与仍属本扩展的部分。**原有论证与五轴设计原样保留**，作为这次内核变更的来源记录。 |
| `extensions/README.md` | 状态语义表新增 `partially_absorbed` 并说明其与 `governed` 的区别；注册表 EXT-02 行更新；内核不变式 2 的对象计数改为引用权威清单。 |
| `docs/architecture/release.zh-CN.md` | 冻结范围不再复述对象计数，改为指向 `src/contracts/core_objects.yaml`。 |
| `docs/architecture/contract.zh-CN.md` | §6 新增核心对象清单指针；新增 §7「尚未进入内核的扩展」，指向 `extensions/README.md` 与 `extensions/BACKLOG.zh-CN.md`。 |
| `tests/test_extension_boundary.py` | 期望状态更新；新增 3 项守卫。 |

## 为什么不删 EXT-02

`partially_absorbed` 是新引入的状态，不是把它当作 `governed` 处理，两者含义不同：

- `governed` = **这个扩展**被内核正式引用。
- `partially_absorbed` = 内核自行实现了同一个想法，扩展本身从未被引用，剩余范围仍未受治理。

因此 EXT-02 既不能标 `governed`（会谎称它被治理过），也不该删（会丢掉这次内核变更的来源论证）。

## 剩余范围不是空的

v5 覆盖了「context 应当是身份的一部分」这个概念，但五项具体工作一项都没做：

| ID | 项 | v5 为何没覆盖 |
|---|---|---|
| `RS-01` | 五个 context 轴的取值域 | v5 给了容器 `AnchorClinicalContext`，没定义各轴是自由文本、受控词表还是外部本体 |
| `RS-02` | 逐 Gate 的跨 context 复用策略 | v5 完全没触及；`GateContextBinding` 默认 `undecided`，45 个 Gate 需专家逐个标注 |
| `RS-03` | context 变化时既有 Gate 结果的失效规则 | v5 的 lock state 表达承诺程度，不是 context 失效 |
| `RS-04` | context 粒度 | 「三线 CRC」与「三线 MSS CRC」是一个还是两个，仍未定 |
| `RS-05` | 既有 CRC 试运行结果的映射 | 9 indication / 36 endpoint / 41 target 如何映射到 `ClinicalHypothesis`，仍未定 |

README 的「激活前必须回答」四问在 v5 之后全部仍然成立。

## 新增测试与一次自我修正

- `test_every_status_is_defined_in_the_status_semantics_table`：扩展声明的每个 status 必须在
  `extensions/README.md` 的状态语义表里有定义。
- `test_partially_absorbed_extensions_declare_what_is_left`：状态为 `partially_absorbed` 时必须同时
  声明 `absorbed_by_kernel` 与非空 `remaining_scope`，防止「核心已被吸收」变成静默退役。

第一项的初版是在整个 README 里搜 status 字面量。变异测试发现该写法**无效**：注册表那一行也含同一
字面量，删掉语义表定义仍然通过。已改为只在 `## 扩展状态语义` 小节的表格行内匹配，重跑变异后失败。

## 变异测试证据

还原用文件备份，不用 `git checkout --`：

| 注入的缺陷 | 结果 |
|---|---|
| 语义表定义行改名（初版测试） | `OK` ← **测试无效，已修正** |
| 语义表定义行改名（修正后测试） | `FAILED (failures=1)` |
| 删除语义表定义行、保留注册表行 | `FAILED (failures=1)` |
| `remaining_scope` 置空 | `FAILED (failures=1)` |
| 删除 `absorbed_by_kernel` | `FAILED (failures=1)` |
| 全部还原 | `OK` |

## 明确未改动

- 未改动任何内核代码。`src/` 下只改了两份文档，未改任何 `.py`。
- 未改动 45-Gate 拓扑、`gate_id`、顺序、任何 gate/model/profile 定义。
- 未改动四阶段生命周期、核心对象定义、`ClinicalHypothesis` 及其锁定门槛。
- 未改动 EXT-01／EXT-03／EXT-04 的任何文件。（EXT-02 的 `contracts.py` **已改动**，见下方 Round 1 修订；本条初版写「未改动 EXT-02 的 `contracts.py`」，在 Round 1 修订后已不成立，故更正。）
- 未改动 `extensions/BACKLOG.zh-CN.md`。
- 未改写任何历史审计记录（`logs/`、`docs/handoff/` 既有内容、`docs/phases/`、
  `docs/architecture/versions/`）。
- 未改动 `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`。该文件
  当前是 `v2-draft` / `PENDING_CHATGPT_APPROVAL`，正在自己的审核流程里；在别的 PR 里改动它会让那次
  审核的对象发生漂移。扩展指针因此放在稳定的 `contract.zh-CN.md`。
- 未新增数据、缓存、结果或运行产物。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 186 tests —— OK（183 + 新增 3）

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.

命令：git diff --check
结果：通过

规范性文档中残留的「七类核心对象」声明：0 处
（历史审计记录中的同类表述按设计保留，未计入）
```

## Round 1 `REQUEST_CHANGES` 与修订

ChatGPT 对本 PR 返回 `REQUEST_CHANGES`，一条阻断，经核实成立。

### 阻断：EXT-02 的 `extension_version` 必须升版

成立。本 PR 对 manifest 的改动不是 prose 级别：`status` 语义变了、新增 `absorbed_by_kernel`、
新增结构化 `remaining_scope`、`design_constraint` 与 `activation_requirements` 改写、全局状态语义表
新增一个状态。这是 manifest 语义与结构的实质变化，继续声明 `0.1.0` 不成立。初版 handoff 用「只改
元数据与说明」作为不升版的理由，该理由错误——**status 语义本身就是 manifest 的实质内容**。

修订：`extension_version` 升为 `0.2.0`。

### 版本引用的同步核查（审核要求的第二步）

按要求逐处核查版本引用，结果如下：

| 位置 | 是否含版本 | 处理 |
|---|---|---|
| `extensions/dynamic_gate_context/extension.yaml` | 是，`extension_version` | 升为 `0.2.0` |
| `extensions/dynamic_gate_context/contracts.py` | 是，`EXTENSION_VERSION` | 升为 `0.2.0` |
| `extensions/README.md` 注册表 | 无版本列 | 无需改 |
| `extensions/dynamic_gate_context/README.md` | 无版本 | 无需改 |
| `tests/test_extension_boundary.py` | 只断言 `extension_version` 键存在，不断言取值 | 见下 |

### 核查中发现的两个额外问题

**其一：两处版本号此前无任何测试约束其一致。** 既有测试只检查 `extension_version` 键存在。
也就是说这次的漂移能发生，正是因为缺少这条守卫；只把数字改对而不加守卫，下次会重复。已新增
`test_manifest_and_contracts_declare_the_same_version`，对每个扩展断言
`extension.yaml` 的 `extension_version` 与 `contracts.py` 的 `EXTENSION_VERSION` 相等。

**其二：`contracts.py` 的模块 docstring 首行仍写 `shell only`。** 与本 PR 把 status 改为
`partially_absorbed` 直接矛盾，属同一次漂移的第二处。已改写首段，说明核心概念已由 v5 在内核实现、
本文件剩下的是 v5 未做的部分，并指向 `remaining_scope` 与 `RS-02`。

因此本 PR 确实改动了 EXT-02 的 `contracts.py`（版本 + docstring），上文「明确未改动」一节相应更正。

### 变异测试证据

| 注入的缺陷 | 结果 |
|---|---|
| 两处版本号不一致（`contracts.py` 退回 `0.1.0`） | `FAILED (failures=1)` |
| 还原 | `OK` |

## 未决问题与风险

- 仓库仍无 GitHub Actions 或 commit status，上述数字只能由仓库审计记录佐证。
- `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md` 是专家实际阅读的文档，但本 PR 没在
  其中加扩展指针，理由见上。该文件的 `v2` 审核完成后，建议在同一次或紧随的任务中补一行指针。
- EXT-01 与 EXT-03 未复核是否也被 v5 部分吸收。初步看不像：EXT-01 依赖真实结局数据，EXT-03 关于
  资产搜索轴，v5 都没触及。如需正式复核可另立任务。

## 下一步

- 提交 ChatGPT 审核本 PR。获 `APPROVE` 后由人类负责人决定合并。
- 本 PR 与 PR C（#46 审计闭环）、PR A（#47 内核依赖修复）互相独立，均从 `main` `a5bf77f` 创建。
  三者都追加 `logs/worklog.md`，合并时会出现追加式冲突，按时间戳顺序保留两侧即可。
  PR A 与本 PR 都改 `tests/test_extension_boundary.py` 之外的不同文件，无重叠。
