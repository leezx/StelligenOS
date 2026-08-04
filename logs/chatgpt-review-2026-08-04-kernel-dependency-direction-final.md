# ChatGPT Review Record: Kernel dependency direction Final

- Review date: 2026-08-04 EDT
- Pull request: #47 (PR A)
- Approved head: `50a3e26`
- Base branch: `main`
- Merge commit: `8d5d808`
- Reviewer: ChatGPT
- Decision: `APPROVE` (Round 1, no blockers)
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.**

## What was reviewed

The `src/` → `genmodules/` dependency inversion introduced by PR #45. A
module-level `from genmodules.gen_indication_endpoint_target.contracts import
ClinicalLockState` in `src/capabilities/gates.py` made the Capabilities layer
depend on a module implementation, so importing `src.repository.boot`
transitively loaded that GenModule and the OS boot path could not load without
it.

Fixed by moving `ClinicalLockState`, `LOCK_ORDER` and
`can_transition_clinical_lock` into `src/lifecycle/clinical_lock.py`, mirroring
`src/lifecycle/state_machine.py`, with the GenModule re-exporting them so all
four import paths still yield the identical type object.

Root cause recorded: this was Round 2 blocker 3 of PR #45 ("two incompatible
`ClinicalLockState` enums must become one canonical enum") fixed on the wrong
side of the layer boundary, and no test guarded that direction —
`tests/test_extension_boundary.py` banned `src/` → `extensions/` but there was no
symmetric `src/` → `genmodules/` guard.

## Final conclusion

> PR #47 — PR A，内核依赖方向修复
>
> APPROVE
>
> 这项修复是正确的。
>
> ClinicalLockState、顺序和转换逻辑被移动到 src/lifecycle/clinical_lock.py；Gate 层和
> GenModule 都依赖内核定义，因此依赖方向恢复为：
>
> genmodules → src
>
> src/capabilities/gates.py 不再导入 genmodules，而是从 src.lifecycle.clinical_lock
> 导入 canonical enum。
>
> 设计选择合理：
>
> * enum、lock order、transition function 放在同一个 lifecycle 内核模块；
> * GenModule 继续 re-export，保持既有公开导入路径；
> * 新增 AST 级依赖守卫，能发现模块级和函数内部延迟 import；
> * 新增行为测试，验证加载 kernel 不会把 genmodules 放入 sys.modules；
> * 既有跨模块 assertIs 保持成立；
> * 45-Gate 拓扑和 lock semantics 未变化。
>
> 这是结构修复，不是功能重写，范围控制合格。
>
> 唯一残余风险是仓库没有 CI，189 tests 是本地证据，不是独立 Actions 结果；这不构成阻断。

## Mutation evidence accepted at review time

| Injected defect | Result |
|---|---|
| `gates.py` imports the genmodule again | `FAILED (failures=2)` |
| GenModule redefines `ClinicalLockState` | `FAILED (failures=2)` |
| GenModule restates `LOCK_ORDER` | `FAILED (failures=1)` |
| All restored | `OK` |

Restored from file backups, not `git checkout --`.

## Verification at the approved head

- 189 tests passing (183 + 6 new).
- `scripts/verify_repository_boundary.sh`: passed.
- `git diff --check`: clean.
- `genmodules` imports under `src/`: 0.
- `genmodules` packages in `sys.modules` after importing the kernel: none.

## Merge note

The merge-base advanced because PR #46 landed first. The only conflict was the
append-only `logs/worklog.md`, resolved in timestamp order. The non-worklog diff
was verified identical to the approved state before merging: 5 files, +207/-32.

## Residual risk carried forward, not blocking

The repository still has no GitHub Actions or commit status, so the 189-test
figure is local evidence corroborated by audit records, not independent CI. The
reviewer stated explicitly that this is not a blocker.

## Scope of this approval

Approved:

- `src/lifecycle/clinical_lock.py` as the single canonical definition of
  `ClinicalLockState`, `LOCK_ORDER` and `can_transition_clinical_lock`.
- The GenModule re-export, preserving the public API.
- `tests/test_kernel_dependency_direction.py` as the standing guard against
  `src/` → `genmodules/`.
- Merging PR #47 into `main`.

Not authorized by this approval:

- Any change to `ClinicalLockState` members, values, order or transition rule.
  Semantics were preserved verbatim and remain frozen.
- Any change to the 45-Gate topology, gate IDs, `GATE_GROUPS`, or any
  gate/model/profile definition.
- Promoting the reverse edge in `genmodules/gate_model_rule/core/contracts.py`
  from a function-local import to a module-level one.
- Guarding lateral dependencies between GenModules, which remains unguarded.
