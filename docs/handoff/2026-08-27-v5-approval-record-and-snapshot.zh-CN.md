# Handoff：v5 审核记录补登 + 只读快照

## 任务信息

- 任务编号：`task_20260827_v5-approval-record-and-snapshot`
- 分支：`task_20260827_v5-approval-record-and-snapshot`
- 基线：`origin/main` @ `ea9dc04`（PR #94 merge）
- PR：待创建
- 时间：`2026-08-27 16:40 EDT`
- 交付物类型：**审核记录补登 + 版本快照 + 基线字符串收尾**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（不改代码、契约、测试、Gate、科学决策；
  快照是既有正文的只读复制）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用「审核豁免」。**

## 一、为什么单独一个 PR

PR #94 的 `APPROVE` 在其内容冻结（`37fa6c2`）之后才到。按
`docs/architecture/versions/README.md` 与
`docs/handoff/2026-08-06-architecture-v4-refresh.zh-CN.md` 先例，审核记录与快照
**不能加到被批准的 branch 上**，否则改掉那个 HEAD。因此另立本 PR。

## 二、改了什么

1. **`logs/chatgpt-review-2026-08-27-architecture-v5-blueprint-alignment.md`（新增）**
   补登 PR #94 的 `APPROVE`：两轮历史（`98fc29f` → `37fa6c2`）、第一轮
   `REQUEST_CHANGES` 的 6 点及关闭方式、批准范围原话要点、PR A–E migration
   顺序、GitHub connector 写 review 失败（`403 Resource not accessible by
   integration`）的操作层说明、以及「这是 architecture-spec 批准、不是 runtime
   批准，`MIGRATION_PENDING` 未解除」的边界。

2. **`docs/architecture/versions/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.v5.zh-CN.md`（新增，只读快照）**
   `git show 37fa6c2:...` 逐字节复制，与被审核正文完全一致（已 `diff` 验证
   `IDENTICAL`）。其 §0 版本区块仍写 `v5-draft` / `PENDING_EXPERT_REVIEW`，
   符合「快照保存被审核时的正文」。

3. **`docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`（规范路径 §0）**
   仅更新 §0 版本区块（这是 `versions/README.md` 允许且仅允许的一处元数据
   差异，正文不动）：`v5-draft` → `v5`；`PENDING_EXPERT_REVIEW` → `APPROVED`
   （附 PR #94 / `37fa6c2` / `ea9dc04` / 审核记录路径）；快照清单加入 `v5`；
   补一句「`v5` 之后的 runtime migration（PR A–E）不修改本文档」。

4. **`docs/architecture/versions/README.md`**
   「当前快照」表加入 `v5` 行；说明段更新为「`v2/v3/v4-draft` 无快照；`v5`
   快照是 `37fa6c2` 逐字节复制，规范路径 §0 已更新为 `v5`/`APPROVED`，是允许
   的唯一元数据差异」。

5. **`architecture.md` / `README.md`**
   审核基线字符串 `STELLIGENOS-ARCH-2026.08.27-v5-draft` →
   `STELLIGENOS-ARCH-2026.08.27-v5`；补 `APPROVE` / merge / 快照指针，并写明
   runtime conformance = `MIGRATION_PENDING`，须按 v5 文档 §16 B 组 PR A–E
   施工。

## 三、本 PR 不做什么

- 不修改 v5 文档正文（只改规范路径 §0 元数据区块）。
- 不修改 `src/`、`genmodules/`、`extensions/`、`core_objects.yaml`、
  `gate_system.yaml`、任何测试或合同。
- 不开始任何 runtime migration（PR A–E）——那是独立授权的施工阶段。
- 不解除 `EVGAP-01`/`EVGAP-02`；不改 CRC 41/369 pool。
- 不动用户自有 untracked 文件。

## 四、验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 555 tests — OK

命令：bash tests/test_git_sync.sh
结果：passed (A-D)

命令：git diff --check
结果：clean

命令：diff <(git show 37fa6c2:docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md) docs/architecture/versions/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.v5.zh-CN.md
结果：IDENTICAL

命令：bash scripts/verify_repository_boundary.sh
结果：仅报 pre-existing 用户自有 untracked（`pipelines/`、`STELLIGEN_CONSTRAINTS.md`、
      `CRC Patient Territory Map.png`、`AI_RESULT_ACCEPTANCE.md`），未修改、未暂存

命令：git status --short
结果：仅本 PR 的 5 个文件（新增 chatgpt-review log、新增 v5 快照、
      CURRENT_SYSTEM §0、versions/README、architecture.md/README.md、本 handoff）
```

## 五、下一步

1. 本 PR `APPROVE` 并合并。
2. `v5` 至此为正式治理基线。**runtime migration（PR A → B → C → D → E+）需
   Owner 单独授权后才启动**，执行前重读 v5 文档 §16 B 组问题 23 的顺序与边界。
3. 无关事项：`task_20260822_crc-atlas-cohort-binding` 分支的未提交 worklog
   仍在 `git stash@{0}`，回到该分支后 `git stash pop` 取回。

## 六、数据边界声明

本仓库只保存架构系统文档、代码和小型治理文本；本任务没有新增任何数据、缓存
或结果文件。新增的 v5 快照是既有架构文档的只读复制，属治理文本。所有数据和
处理仍位于外部工作区。
