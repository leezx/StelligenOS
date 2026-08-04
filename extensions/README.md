# StelligenOS Extensions

## 这个目录是什么

`extensions/` 保存**尚未进入架构内核**的扩展提案。每个扩展是一个独立的插件包，有自己的身份、版本、状态和契约壳。

这些扩展来自 `prompts/GPT-Feedback.md` 的外部专家反馈。反馈本身不是架构变更授权，因此这些内容不写进内核，只在本目录中固化，防止遗忘，并为将来的独立治理任务留下可引用的起点。

## 内核不变式（Kernel Invariants）

以下四条是本目录存在的前提。任何扩展都不得违反：

1. **单向依赖。** 扩展可以引用内核的对象、Gate 身份和合同；内核不得引用、导入或依赖任何扩展。`src/` 下不允许出现 `import extensions` 或 `from extensions`。此不变式由 `tests/test_extension_boundary.py` 校验。
2. **内核冻结边界不动。** 本目录不修改 `docs/architecture/contract.zh-CN.md`、四阶段生命周期、八类核心对象、45-Gate 拓扑与身份、`genmodules/assetgenos_catalog/` 下的 gate/model/profile 定义，也不修改 `GateInputEnvelope@2.0.0` 或 `GateModelOutput@2.0.0`。核心对象的权威清单是 `src/contracts/core_objects.yaml`；本条只声明「不修改」，不复述清单内容。
3. **扩展不产生决策。** 扩展的输出只能是建议、约束描述或结构化判据，不得自动改写 Gate 分数、状态、阈值、Profile 绑定或生命周期状态。晋级仍然只能来自显式的人类决策。
4. **仓库仍然 data-free。** 扩展只保存合同、身份和说明；证据、结果、模型权重、临床结局数据全部留在外部工作区，只以 `external:` 引用出现。

## 扩展状态语义

| 状态 | 含义 |
|---|---|
| `shell_only` | 只固化目的、边界和契约骨架，没有可执行逻辑。目的是防止遗忘。 |
| `active_design` | 契约已可执行并有测试，但尚未接入任何真实运行。 |
| `partially_absorbed` | 核心概念已由内核以自己的方式实现，本扩展只剩下未被覆盖的部分。历史论证保留在扩展目录内供追溯，不删。 |
| `governed` | 已通过独立治理任务进入内核或被内核正式引用。当前没有任何扩展处于此状态。 |

从 `shell_only`、`active_design` 或 `partially_absorbed` 进入 `governed` 必须另立任务分支、独立 PR 和 ChatGPT `APPROVE`，不得在扩展目录内部自行提升。

`partially_absorbed` 与 `governed` 不同：`governed` 表示**这个扩展**被内核正式引用；`partially_absorbed` 表示内核自行实现了同一个想法，扩展本身从未被引用，因此剩余范围仍未受治理。扩展进入该状态时必须在 `extension.yaml` 写明 `absorbed_by_kernel` 与 `remaining_scope`。

## 扩展注册表

| ID | 名称 | 来源 | 优先级 | 状态 |
|---|---|---|---|---|
| `EXT-01` | [`ground_truth_learning_loop`](./ground_truth_learning_loop/) | GPT-Feedback v4 一级风险一 | 低（等真实药物实验数据） | `shell_only` |
| `EXT-02` | [`dynamic_gate_context`](./dynamic_gate_context/) | GPT-Feedback v4 一级风险二 | 中 | `partially_absorbed`（v5 已实现核心概念，剩余 `RS-01`..`RS-05`） |
| `EXT-03` | [`asset_search_engine`](./asset_search_engine/) | GPT-Feedback v4 一级风险三 | 中 | `shell_only` |
| `EXT-04` | [`stop_rule`](./stop_rule/) | GPT-Feedback v4 一级风险四 | **最高** | `active_design` |

七个二级风险见 [`BACKLOG.zh-CN.md`](./BACKLOG.zh-CN.md)，当前全部不做，只登记。

## 目录约定

每个扩展目录包含：

- `extension.yaml`：身份、版本、状态、来源、内核接触面和禁止行为。
- `README.md`：目的、设计逻辑、边界、以及激活前必须回答的问题。
- `contracts.py`：frozen dataclass 契约与 Protocol 端口。`shell_only` 扩展的端口方法体为 `...`。

文件名只允许 `A-Z`、`a-z`、`0-9`、`_`、`.`、`-`，禁止空格。
