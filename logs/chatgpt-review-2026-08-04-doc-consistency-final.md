# ChatGPT Review Record: Architecture and documentation consistency Final

- Review date: 2026-08-04 EDT
- Pull request: #48 (PR B)
- Approved head: `a1ec4bd`
- Base branch: `main`
- Merge commit: `8298bdf`
- Reviewer: ChatGPT
- Decision: `APPROVE` (Round 2)
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.**

## Review history

- Round 1: `REQUEST_CHANGES`, one blocker.
  - EXT-02's `extension_version` had to be bumped. The manifest change was not
    prose: `status` semantics changed, `absorbed_by_kernel` and a structured
    `remaining_scope` were added, `design_constraint` and
    `activation_requirements` were rewritten, and the global status vocabulary
    gained a member. The earlier "metadata and prose only" rationale for holding
    at `0.1.0` was wrong, because status semantics are substantive manifest
    content. The reviewer also required checking whether README, registry or
    tests carried version references needing synchronisation.
  - Correction: bumped to `0.2.0` in `extension.yaml` and in `contracts.py`.
    Auditing every version reference surfaced two further problems in the same
    drift: (a) nothing asserted the two version numbers agreed, which is *why*
    the drift was possible, so `test_manifest_and_contracts_declare_the_same_version`
    was added; (b) the `contracts.py` module docstring still opened with
    `shell only`, contradicting the new `partially_absorbed` status, and was
    rewritten. The handoff's "explicitly unchanged" list had claimed EXT-02's
    `contracts.py` was untouched; that claim was corrected rather than left
    standing.
- Round 2: `APPROVE`.

## Final conclusion

> PR #48 — 文档同步
>
> APPROVE
>
> 上轮版本治理问题已关闭：
>
> * EXT-02 manifest 的 extension_version 已从 0.1.0 升到 0.2.0。
> * contracts.py 中的 EXTENSION_VERSION 同步到 0.2.0。
> * 新增测试保证 manifest 与 contracts 版本一致，避免未来再次漂移。
>
> 其他变更也合理：
>
> * partially_absorbed 准确表达"核心概念已被 v5 内核独立吸收，但扩展剩余范围仍未治理"的
>   状态。
> * remaining_scope 明确保留五项未完成工作，而不是把 EXT-02 静默退役。
> * contracts.py 的旧 shell only 描述已同步修正，但 contract definitions 本身未改变。
> * 两份规范文档不再硬编码"七类对象"，改为引用 authoritative YAML。
> * architecture contract 增加 extensions registry 和 backlog 指针。
> * 历史 handoff、phase、review 和旧架构快照未被改写。
> * 新增状态语义、remaining scope 和版本一致性测试，且 mutation evidence 显示这些测试
>   不是空转。
> * 45-Gate 拓扑、核心对象、生命周期和运行行为未改变。

## The new `partially_absorbed` status

Introduced because neither existing status describes the situation:

- `governed` means **the extension itself** is formally referenced by the kernel.
- `partially_absorbed` means the kernel implemented the same idea independently;
  the extension was never referenced, so its remaining scope is still ungoverned.

Marking EXT-02 `governed` would have claimed governance it never passed; deleting
it would have discarded the provenance of a kernel change. Its original argument
and five-axis design are kept verbatim in `extensions/dynamic_gate_context/README.md`.

## Remaining scope registered, not retired

| ID | Item |
|---|---|
| `RS-01` | Value domains of the five context axes |
| `RS-02` | Per-Gate cross-context reuse policy — largest and least automatable |
| `RS-03` | Invalidation rule when clinical context changes |
| `RS-04` | Context granularity |
| `RS-05` | Mapping the existing CRC pilot output onto `ClinicalHypothesis` |

## Mutation evidence accepted at review time

| Injected defect | Result |
|---|---|
| Rename the semantics-table definition row (first version of the test) | `OK` ← test was vacuous, fixed |
| Rename the semantics-table definition row (corrected test) | `FAILED (failures=1)` |
| Delete the semantics row, keep the registry row | `FAILED (failures=1)` |
| Empty `remaining_scope` | `FAILED (failures=1)` |
| Remove `absorbed_by_kernel` | `FAILED (failures=1)` |
| Desync `extension.yaml` and `contracts.py` versions | `FAILED (failures=1)` |
| All restored | `OK` |

The first row is recorded deliberately: one guard was written, proven vacuous by
mutation, and rewritten. The reviewer's note that "mutation evidence 显示这些测试
不是空转" refers to the corrected versions.

## Verification at the approved head

- 186 tests passing (183 + 3 new).
- `scripts/verify_repository_boundary.sh`: passed.
- `git diff --check`: clean.
- Residual "seven core objects" claims in normative documents: 0. The same
  phrasing inside historical audit records is preserved by design.

## Merge note

The merge-base advanced because PRs #46 and #47 landed first. The only conflict
was the append-only `logs/worklog.md`, resolved in timestamp order. The
non-worklog diff was verified identical to the approved state before merging:
7 files. Test count on `main` after all three merges is 192 (183 + 6 + 3).

## Scope of this approval

Approved:

- EXT-02 at `partially_absorbed`, version `0.2.0`, with `absorbed_by_kernel` and
  `remaining_scope` `RS-01`..`RS-05`.
- The `partially_absorbed` status entering the registry vocabulary.
- Normative documents referencing `src/contracts/core_objects.yaml` instead of
  restating an object count.
- The extension-registry pointer added to `docs/architecture/contract.zh-CN.md`.
- The three new registry guards.
- Merging PR #48 into `main`.

Not authorized by this approval:

- Promoting any extension to `governed`. EXT-02 is `partially_absorbed`; EXT-01
  and EXT-03 remain `shell_only`; EXT-04 remains `active_design`.
- Starting any of `RS-01`..`RS-05`.
- Any change to EXT-02's contract definitions. Only its version constant and
  module docstring changed.
- Any kernel, Gate topology, Model, Profile or lifecycle change.
- Adding the extension pointer to
  `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`, which is
  `v2-draft` / `PENDING_CHATGPT_APPROVAL` and inside its own review.
