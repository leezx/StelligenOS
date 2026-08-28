# ChatGPT 审核记录：Runtime Migration PR A —— Core decision objects

- 日期：`2026-08-28`
- PR：#98 `task_20260828_runtime-migration-pr-a`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`
- 被审核 HEAD：`f225e9f`（REQUEST_CHANGES 第一轮修订）
- Merge 提交：`cbab012`（`Merge pull request #98 from leezx/task_20260828_runtime-migration-pr-a`）
- 结论：**APPROVE @ `f225e9f`**

本记录在**独立 docs-only PR**（`task_20260828_runtime-migration-pr-a-approval-record`）
中补登，按 PR #95 / #97 先例——审核记录不落在被批准的 PR branch 上。本 PR
同时把 `docs/handoff/2026-08-28-runtime-migration-pr-a.zh-CN.md` 里首版遗留的
`38 tests / 593` 数字改成最终的 `54 / 609`（审核方点名的唯一非 blocker），并把
`manifests/runtime_migration_pr_a_manifest.yaml` 的 `status` / `chatgpt_review`
/ `approved_tip` 补成 approved。不改 PR A 的 runtime 合同或测试逻辑。

## 两轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `323641d`（PR A 首版：`decision_objects.yaml` + `decision_model.py` + `legacy_adapters.py` + 38 tests） | `REQUEST_CHANGES`，方向/scope 正确、无架构越界；3 个 runtime-contract correctness 问题 |
| 2 | `f225e9f`（同一 PR 一轮修订，54 tests） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 3 点及关闭方式

### 1. deep immutability（blocker）

`@dataclass(frozen=True)` 只浅冻结：`Context.dimensions`、EvidencePackage 的
`measurement / study_context / provenance / interpretation_boundary /
derivation`、Assessment 的 `review / critical_unknowns / key_*` 接受普通
`Mapping`，构造后调用方仍可通过原 dict 改值绕过 `__post_init__`；
`LEGACY_CROSSWALK: Final[dict]` 的 `Final` 只是 type hint，runtime 可改。

→ `decision_model.py` 新增 `_deep_freeze()`：Mapping → `MappingProxyType`
over fresh copy，list/tuple → tuple，递归（str/bytes 视为 scalar）。每个
dataclass `__post_init__` **先 `_freeze_attr(...)` 再 validate**，validate 跑在
不可变快照上。`legacy_adapters.py`：内部 `_LEGACY_CROSSWALK` dict →
`LEGACY_CROSSWALK = MappingProxyType(...)`（`LegacyCrosswalkEntry` 本就是 frozen
dataclass）；新增 `MISSING_CANDIDATE_TYPES` 同样 `MappingProxyType`。
新增测试：外部 dict 构造后 mutation 不污染对象；穿过对象改 `review` /
`critical_unknowns[0]` / `dimensions` / EP 各 block raise `TypeError`；nested
list → tuple；`LEGACY_CROSSWALK` / `MISSING_CANDIDATE_TYPES` 不可写不可删。

### 2. nested schema parity（blocker）

之前只比较 required keys / 顶层 enum / forbidden fields；runtime 会接受 frozen
Data Layout schema 明确拒绝的 nested 数据（`additionalProperties: false` 下的
extra key、nested scalar 型别、`minLength`、array-item 型别、日期 pattern）。

→ `decision_model.py` 新增 `_check_block(required, allowed, closed=)`
（`closed=True` 对应 `additionalProperties: false` → 精确 key 集）+ 逐 block
scalar / 型别 / pattern 校验：

- `measurement`（closed）：精确 key ⊆ `{type, analyte, readout, result, unit}`；
  前 4 非空 string；`unit` string。
- `provenance`（closed）：精确 5 key；`source_id` 匹配 `^SRC-[0-9]{8}$`；
  `source_type` ∈ 10 值；`source_identifier` 非空 string；`locator` string；
  `retrieved_at` 日期前缀。
- `interpretation_boundary`（closed）：精确 4 key；前 3 个 = string tuple；
  `evidence_ceiling` 非空 string。
- `derivation`（closed）：精确 2 key，均 string。
- `study_context`（open，`additionalProperties: true`）：允许 extra key；3 个
  必填为 string；`n` ∈ int|str；`model` / `assay` string。
- `review`（closed）：精确 3 key；`status == HUMAN_APPROVED`；`reviewer` 非空
  string；`reviewed_at` 日期前缀。
- `critical_unknowns[i]`（closed）：精确 `{unknown, resolution}`；`unknown`
  非空 string；`resolution` ∈ 3 值。
- `key_supporting_evidence` / `key_contradicting_evidence`：tuple of mapping。

meta-parity 测试：Python 侧 closed-block allowed-key 常量（`_MEASUREMENT_KEYS`
/ `_PROVENANCE_KEYS` / `_INTERPRETATION_KEYS` / `_DERIVATION_KEYS` /
`_REVIEW_KEYS` / `_CRITICAL_UNKNOWN_KEYS`）== 对应 schema `properties` key 集；
`context` / `instantiation` schema `additionalProperties` == false。
加代表性 reject 测试（extra key、`source_identifier=123`、`locator=["x"]`、
`n=[1]`、`reviewed_at="27-08-2026"`、空 `unknown` 等）。

冻结的边界（写进 `decision_model.py` docstring 精神）：**PR A runtime object
表示的每个字段，Python 构造不得接受一个 nested value —— 若该 value 仅因其
intrinsic shape/type/enum 约束会被对应 frozen Data Layout schema 拒绝。**
仍是 "Python executable mirror + parity test"，未引入 `jsonschema`。

### 3. `missing_candidate_types` 清单不完整（小 blocker）

原来只列 7 个，漏 `INDICATION L00` / `PATIENT_TERRITORY L01` / `MODALITY L03`
/ `ADC_DESIGN L09` / `ADC_HIT L10`（后两个正是 `ADCConstruct` composite 明确
spanning 的 L09/L10）。

→ `decision_objects.yaml` `missing_candidate_types` 补成完整 **12 个**非
clean-1:1 Candidate Type（`L00 L01 L02 L03 L05 L07 L08 L09 L10 L11 L12 L14`）；
note 改为明确"完整集合 = 无 clean 1:1 legacy 映射的 12 个 Level；加上 legacy
clean mapping `L04 ADC_TARGET` / `L06 ANTIBODY_BINDER` / `L13
DEVELOPMENT_CANDIDATE` 即完整 L00–L14 ontology"。`legacy_adapters.py` 新增
`MISSING_CANDIDATE_TYPES`（level → type，`MappingProxyType`）+ import 期
`_check_missing_candidate_types_are_complete()`（与 one-to-one levels 并集 ==
`CANDIDATE_LEVELS` 且不相交）。新增测试：YAML ↔ Python 一致；并集完整且互斥；
L09/L10 存在且 `ADCConstruct` 非 1:1。

## 批准范围（审核方原话要点）

- **APPROVE PR #98 @ `f225e9f`。可以 merge。** 3 个 blocker 实质关闭且未引入新
  runtime/architecture blocker。
- deep immutability：`_deep_freeze()` 对 Mapping 先 fresh-copy 再
  `MappingProxyType`、list/tuple 递归转 tuple；Assessment / EvidencePackage /
  Context 都在 validation 前 freeze，外部原始 dict 后续 mutation 不污染已
  validated 的 runtime object。
- nested schema parity：closed nested block 的 allowed keys 与 frozen schema
  properties 做 meta-parity，并测 extra key / 错误 scalar type / 日期格式等
  reject 路径 —— 已达到"Python 是 frozen Data Layout schema 的 executable
  mirror，而不是第二套自由发挥的 specification"这条边界。
- missing candidate types：registry 完整列出 12 个无 clean 1:1 legacy mapping
  的 level，与 legacy clean mapping `L04/L06/L13` 合并正好覆盖 L00–L14；测试锁住
  完整覆盖、互斥，以及 `ADCConstruct → L09/L10 composite` 语义。
- legacy 兼容边界仍正确：只有 `TargetHypothesis / BinderCandidate /
  DevelopmentCandidate` 三个无歧义对象自动适配；5 个 composite/wrapper 没有被
  偷偷 decomposition。
- 无要求修改 `core_objects.yaml` / 旧 45-Gate / Data Layout schemas / 冻结
  architecture docs 的理由。PR A scope 已干净完成，不需继续优化。
- **非 blocker（本 PR 已修文档，不再开 runtime 轮）：** PR body / handoff 前半段
  首版遗留 `38 tests / 593`，实际 `54 new / 609`。
- Merge 后可正式进入 **Runtime Migration PR B —— canonical Gate / GateSet +
  Evidence Ladder + Decision**。

## 操作层说明

审核方两轮均尝试通过 GitHub connector 直接给 PR #98 写入 review 状态
（`REQUEST_CHANGES`、`APPROVE` anchor 到 `f225e9f`），GitHub 每次返回
`403 Resource not accessible by integration`，未能写回 GitHub。GitHub 上 PR #98
因此没有 formal review 记录，实际两轮意见与最终 `APPROVE` 以本文件与
`AI审核方案` 对话为准。

## 边界

本次批准的是 **runtime 决策层对象合同**（`src/contracts/decision_objects.yaml`
+ `src/objects/decision_model.py` + `src/objects/legacy_adapters.py` + 54
tests）。它是四个 runtime-migration PR 的第一个。合并后 `core_objects.yaml` 的
8 个 legacy object type 仍保留，`gate_system.yaml` 的 45-Gate 拓扑 +
`GateModelOutput.score` 仍 `FROZEN_LEGACY`（属 PR B），CURRENT_SYSTEM v5 的
`MIGRATION_PENDING` 未解除——到 PR E 合并前 repository runtime 不得声称已实现
Blueprint v1.3 conformance。仓库内不保存运行数据或 `.csv`。

冻结与进度状态：

> Blueprint v1.3：冻结
> CURRENT_SYSTEM v5：冻结
> Data Layout Spec v1.0：冻结
> Runtime Migration PR A（core decision objects）：**已合并**（PR #98 @ `f225e9f`，`cbab012`）
> 下一步：Runtime Migration PR B —— canonical Gate / GateSet + Evidence Ladder + Decision
