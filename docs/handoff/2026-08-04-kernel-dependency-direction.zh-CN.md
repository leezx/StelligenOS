# 任务交接备忘：内核依赖方向修复

- 任务编号：`task_20260804_kernel-dependency-direction`
- 分支：`task_20260804_kernel-dependency-direction`（从 `main` `a5bf77f` 创建）
- PR：**PR A**，base 为 `main`
- 当前状态：`PENDING_CHATGPT_REVIEW`
- 变更性质：依赖方向修复 + 新增边界测试，**无行为变更**
- Gate 变更：`NO_GATE_CHANGE`

## 问题

PR #45 在 `src/capabilities/gates.py` 加了一行模块级导入：

```python
from genmodules.gen_indication_endpoint_target.contracts import ClinicalLockState
```

这违反六层架构的依赖方向。架构一直是 `genmodules -> src`（模块依赖内核），这一行把它变成
`src/capabilities -> genmodules`（内核依赖模块实现）。

实测后果：

```text
import src.repository.boot
→ 连带加载 genmodules.gen_indication_endpoint_target.contracts
```

也就是 **OS 启动路径离开这个 GenModule 就加载不了**。反向边也已存在：
`genmodules/gate_model_rule/core/contracts.py` 在函数体内 `from src.capabilities.gates import
gate_definition`，写在函数里所以没有形成硬循环导入，但逻辑上环已闭合。

根因不是疏忽取舍，而是 Round 2 阻断 3 的修复落点错了。该阻断要求「两个不兼容的
`ClinicalLockState` 必须统一成一份」——要求本身正确，但唯一那份被放在了层边界的模块侧。

**并且这个方向当时没有任何测试守着。** `tests/test_extension_boundary.py` 明确禁止
`src/ -> extensions/`，但没有对称的 `src/ -> genmodules/` 守卫，所以这条边悄悄进来了。

## 变更

| 文件 | 变更 |
|---|---|
| `src/lifecycle/clinical_lock.py` | 新增。`ClinicalLockState`、`LOCK_ORDER`、`can_transition_clinical_lock` 的唯一权威定义。 |
| `src/lifecycle/__init__.py` | 导出上述三者。 |
| `src/capabilities/gates.py` | 导入改为 `from src.lifecycle.clinical_lock import ClinicalLockState`。 |
| `genmodules/gen_indication_endpoint_target/contracts.py` | 删除本地定义，改为从内核导入并再导出；注明不得重述。 |
| `tests/test_kernel_dependency_direction.py` | 新增 6 项，禁止 `src/ -> genmodules/`。 |

落点选 `src/lifecycle/` 而不是 `src/objects/`，因为 `src/lifecycle/state_machine.py` 已经是同一
形态的先例：枚举 + 顺序 + `can_transition` 三者同处内核一个模块。`LOCK_ORDER` 与
`can_transition_clinical_lock` 一并迁入，是为了避免「内核拥有枚举、模块拥有其语义」这种更弱的
拆分。

`_LOCK_ORDER` 迁入后改名为 `LOCK_ORDER`（去掉下划线），因为它跨模块可见了。

## 公开 API 保持不变

GenModule 侧继续再导出，因此以下四条路径拿到的是**同一个类型对象**，实测 `is` 全部为真：

```text
src.lifecycle.clinical_lock.ClinicalLockState
src.capabilities.gates.ClinicalLockState
genmodules.gen_indication_endpoint_target.ClinicalLockState
genmodules.gen_indication_endpoint_target.contracts.ClinicalLockState
```

`tests/test_phase3_gate_contracts.py:78` 的 `assertIs(ClinicalLockState,
GenModuleClinicalLockState)`（Round 2 阻断 3 要求的跨模块集成断言）继续成立，未改动该测试。

## 新增测试为什么这样写

`test_the_guard_also_catches_deferred_imports` 是这组测试的自检。守卫用 AST 遍历而不是匹配行首，
因为**函数体内的延迟导入同样是依赖**——反向边就正是那个形态。该项断言已知的函数内
`genmodules -> src` 导入必须被 AST 扫描看见；如果扫描漏掉函数体，这一项会失败，从而证明上面那条
禁令不是空转。

`test_the_kernel_imports_without_genmodules_on_the_path` 在子进程里实测内核导入后
`sys.modules` 中不含任何 `genmodules` 顶级包，这是对「启动不依赖模块」的行为断言，而非源码断言。

## 变异测试证据

逐个注入缺陷确认失败，随后从文件备份还原（不用 `git checkout --`，该做法曾在 PR #16 造成未提交
修改丢失）：

| 注入的缺陷 | 结果 |
|---|---|
| `gates.py` 改回导入 genmodule | `FAILED (failures=2)` |
| GenModule 重新定义 `ClinicalLockState` | `FAILED (failures=2)` |
| GenModule 重述 `LOCK_ORDER` | `FAILED (failures=1)` |
| 全部还原 | `OK` |

## 明确未改动

- 未改动 45-Gate 拓扑、`gate_id`、顺序、`GATE_GROUPS` 或任何 gate/model/profile 定义。
- 未改动 `ClinicalLockState` 的成员、取值、顺序或迁移规则；语义逐字保留。
- 未改动四阶段生命周期、`LifecycleStage`、`ALLOWED_TRANSITIONS`。
- 未改动核心对象、`ClinicalHypothesis` 及其锁定门槛、`legacy_compatibility` 路径。
- 未改动任何既有测试。
- 未改动 `extensions/`（EXT-02 的状态漂移属 PR B）。
- 未新增数据、缓存、结果或运行产物。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 189 tests —— OK（183 + 新增 6）

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.

命令：git diff --check
结果：通过

src/ 下 genmodules 导入：0 处
内核导入后 sys.modules 中的 genmodules 包：无
__pycache__：0
```

## 未决问题与风险

- 仓库仍无 GitHub Actions 或 commit status，上述数字只能由仓库审计记录佐证，无法由 CI 独立复核。
- 反向边 `genmodules/gate_model_rule/core/contracts.py` 的函数内 `src` 导入方向正确，本 PR 保留
  不动。它写在函数里是为了避开导入期循环；现在环已解开，理论上可以提到模块级，但那属于与本
  PR 目标无关的整理，未做。
- 新守卫只覆盖 `src/ -> genmodules/`。`src/ -> extensions/` 由既有测试覆盖。`genmodules/` 之间
  的横向依赖仍无守卫，如需可另立任务。

## 下一步

- 提交 ChatGPT 审核本 PR。获 `APPROVE` 后由人类负责人决定合并。
- 本 PR 与 PR C（审计闭环）、PR B（文档同步）互相独立，均从 `main` `a5bf77f` 创建。三者都会追加
  `logs/worklog.md`，因此合并时会出现追加式冲突，按时间戳顺序保留两侧即可。
