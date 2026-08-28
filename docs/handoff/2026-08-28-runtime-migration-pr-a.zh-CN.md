# Handoff：Runtime Migration PR A —— Core decision objects

## 任务信息

- 任务编号：`task_20260828_runtime-migration-pr-a`
- 分支：`task_20260828_runtime-migration-pr-a`
- 基线：`origin/main` @ `6b8ef70`（PR #97 merge）
- PR：待创建
- 时间：`2026-08-28`
- 授权：用户明确指示"先做第一件：Runtime Migration PR A–D，逐一来做"
- 变更定位：`RUNTIME_CONTRACT_ADD`（新增运行时对象合同 + legacy adapter；
  不删 legacy、不改冻结文档、不加依赖、不引入 persistence / 执行）

## 一、依据（冻结文档，本 PR 不修改，只按其顺序施工）

- `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`
  §16 B 组问题 23：
  > PR A — Core decision objects：Candidate / Context / EvidencePackage /
  > CandidateGateAssessment / Instantiation config + legacy core-object
  > adapters（不删 legacy 8-object support）
- `docs/architecture/contract.zh-CN.md` §3.4.1 决策层模型、§3.4.2 Candidate
  Level Registry、§3.4.3 legacy → target crosswalk、§3.4.4 ClinicalHypothesis
  递进锁定
- `docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md` + `src/contracts/
  data_layout/*.schema.*`（`v1.0` / `APPROVED`）—— PR A 的运行时合同字段集与
  枚举与之逐字保持一致

## 二、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/decision_objects.yaml`（新） | 声明式 registry。5 个合同（`Candidate@0.1.0` / `Context@0.1.0` / `EvidencePackage@0.1.0` / `CandidateGateAssessment@0.1.0` / `Instantiation@0.1.0`）的 `required_fields` / `optional_fields` / `forbidden_fields` / `field_kinds` / `allowed_values` / `nested_required_keys` / `direction_strength_matrix`；`candidate_levels`（L00–L14）；`legacy_crosswalk`（8 个 legacy 对象）；`missing_candidate_types`（migration 时须新增）；`migration.deferred`（Decision + canonical GateSet 合同 → PR B，Matrix → PR C，CRC-ADC-TARGET-GATESET-v1 → PR D，逐 Gate Module → PR E+）。 |
| `src/objects/decision_model.py`（新） | frozen `@dataclass` + `__post_init__` 校验，遵循 repo 既有 `src/contracts/*.py` 风格（`Final` 词表元组、`external:` ref 校验、无 persistence / 无执行）。词表：`DIRECTION_VALUES` / `STRENGTH_VALUES` / `GRADED_STRENGTHS` / `EVIDENCE_ROLE_VALUES` / `CANDIDATE_LEVELS` / `CANDIDATE_STATUS_VALUES` / `CONTEXT_STATUS_VALUES` / `INSTANTIATION_STATUS_VALUES` / `EVIDENCE_REGIME_VALUES` / `CRITICAL_UNKNOWN_RESOLUTIONS` / `SOURCE_TYPE_VALUES` / `CANONICAL_REVIEW_STATUS`。ID 正则与 data_layout schema 逐字一致。`CANDIDATE_/CONTEXT_/EVIDENCE_PACKAGE_/ASSESSMENT_/INSTANTIATION_FORBIDDEN_FIELDS` 对应各 schema `not.anyOf`。 |
| `src/objects/legacy_adapters.py`（新） | `LegacyCrosswalkEntry` + `LEGACY_CROSSWALK`（覆盖全部 8 `CORE_OBJECT_TYPES`，import 期自检一致性）。`adapt_core_object_to_candidate(core_object, *, candidate_id, canonical_name, created_at, provenance_ref, ...)`：3 个 1:1 类型返回 `Candidate`；composite / wrapper / non_candidate raise `NotImplementedError` 并附 crosswalk target 与 §3.4.3 指引。 |
| `src/objects/__init__.py`（改） | 追加 export 新符号；legacy `CORE_OBJECT_TYPES` / `CoreObject` export 不变。 |
| `tests/test_decision_model.py`（新，38 tests） | 见 §三。 |
| `manifests/runtime_migration_pr_a_manifest.yaml`（新） | 按 `phase_2_manifest.yaml` 格式：scope、boundary 声明、`chatgpt_review: PENDING`、`approved_tip: null`、test 命令、artifact 清单。 |
| `src/objects/README.md` / `src/contracts/README.md`（改） | 说明 `core.py` = legacy registry、`decision_model.py` = PR A 六对象、`Decision` → PR B、`legacy_adapters.py` 的映射。 |

## 三、测试（`tests/test_decision_model.py`，38 tests）

1. **contract YAML shape** —— version、合同集合、`migration.deferred`、"不触碰
   legacy `core_objects.yaml`"。
2. **registry ↔ Python parity** —— `required_fields` == 无默认值的 dataclass
   字段集；`forbidden_fields` == 模块 `*_FORBIDDEN_FIELDS` 元组；`allowed_values`
   / `candidate_levels` == 词表元组。
3. **Python ↔ data_layout schema parity（防漂移）** —— 加载
   `candidate.schema.json` / `context.schema.yaml` / `evidence_package.schema.json`
   / `assessment.schema.json` / `instantiation.schema.yaml`：`required` 数组、
   各 enum（含嵌套 `evidence_refs.items.role` / `critical_unknowns.items.resolution`
   / `review.status` const / `provenance.source_type`）、`not.anyOf` forbidden
   字段、`nested_required_keys`、ID pattern —— 全部逐一对齐 Python 侧。
4. **逐对象 accept / reject** —— 合法实例构造成功；坏 ID / 坏 enum / 非
   `external:` provenance / 坏日期 / `version=0` 等 raise `ValueError`。
5. **direction × strength 矩阵** —— POSITIVE+UNKNOWN raise；POSITIVE 无证据
   raise；CONFLICTING 仅一侧 raise；CONFLICTING 缺 key 数组 raise；
   CONFLICTING+UNKNOWN raise；INCONCLUSIVE 两形态；NOT_APPLICABLE 严格；
   `review.status != HUMAN_APPROVED` raise；坏 `resolution` raise。
6. **守卫** —— `context_id` 不在 `Candidate` 字段；`candidate_id` 不在
   `Instantiation` 字段；`grade`/`direction`/`strength` 不在 `EvidencePackage`
   字段；`decision`/`score` 不在 `CandidateGateAssessment` 字段。
7. **legacy 路径保留** —— `CORE_OBJECT_TYPES` 仍为原 8 元组；`CoreObject` 照旧；
   `LEGACY_CROSSWALK` 覆盖且仅覆盖这 8 个；3 个 1:1 entry 的 `candidate_type` /
   `level` 正确；`adapt_core_object_to_candidate` 对 3 个 1:1 返回 `Candidate`、
   对 5 个 composite/wrapper raise `NotImplementedError`；disposition 与 contract
   prose 一致。

## 四、明确未改 / 未做

- `src/contracts/core_objects.yaml`、`src/objects/core.py`、`CoreObject`、
  `CORE_OBJECT_TYPES` —— legacy 8 对象支持完整保留。
- `src/contracts/gate_system.yaml`、`src/capabilities/*` —— 45-Gate 拓扑、
  `GateModelOutput.score/confidence/status` 保持 `FROZEN_LEGACY`（属 PR B）。
- `src/contracts/data_layout/*.schema.*` —— Data Layout Spec v1.0 冻结，未改。
- `docs/architecture/*` —— migration PR 不改冻结架构文档（v5 §17 rule 6）。
- 第六个对象 `Decision`（及 `GO/CONDITIONAL_GO/HOLD/MORE_EVIDENCE/KILL/
  NOMINATE/COMMIT` 词表）—— 归 PR B（与 GateSet decision policy 一起）。
- 无新依赖：`jsonschema` 未安装、未引入；词表在 Python 内重述并由 parity
  测试锁定。
- 无 persistence、无执行、无数据、无 `.csv`；`src/` 未 import `genmodules/`。
- `MIGRATION_PENDING` 未解除（到 PR E 前 repository runtime 不得声称 Blueprint
  v1.3 conformance）。
- 用户自有 untracked 文件（`pipelines/` 等）未暂存。

## 五、验证命令与结果

```
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
→ Ran 593 tests ... OK   (555 baseline + 38 new)

PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_decision_model -v
→ Ran 38 tests ... OK

git diff --check
→ clean

# 干净 tracked-tree worktree（排除用户 untracked 文件）
verify_repository_boundary.sh → Repository boundary check passed. (exit 0)

python3 -c 'json/yaml load 全部 src/contracts/data_layout/*.schema.* + decision_objects.yaml'
→ 结构合法
```

## 六、审核

提交 PR 后在网页版 ChatGPT `Biotech ideas → AI审核方案` 对话提交审核。
若 GitHub connector 写 review 返回 `403`（前 4 个 PR 均如此），审核意见由
leezx 在对话中转述，落 `logs/chatgpt-review-2026-08-28-runtime-migration-pr-a.md`
（按 PR #95 / #97 先例，APPROVE 记录可用独立 docs-only PR 补登）。

## 六之二、REQUEST_CHANGES 第一轮修订（2026-08-28，同一 PR #98）

审核结论：方向与 scope 正确、无架构越界；3 个 runtime-contract correctness
问题，同一 PR 一轮关闭，不碰冻结文档、不提前做 PR B。

1. **deep immutability（blocker）。** `@dataclass(frozen=True)` 只浅冻结；
   `Context.dimensions` / EvidencePackage 的 5 个 nested block / Assessment 的
   `review` / `critical_unknowns` / `key_*` 接受普通 `Mapping`，构造后调用方仍可
   通过原 dict 改值绕过 `__post_init__`。`LEGACY_CROSSWALK: Final[dict]` 的
   `Final` 只是 type hint，runtime 可改。
   → `decision_model.py` 新增 `_deep_freeze()`：mapping → `MappingProxyType`
   over fresh copy，sequence → `tuple`，递归；每个 dataclass 在
   `__post_init__` **先 freeze 再 validate**（`_freeze_attr`），validate 跑在
   不可变快照上。`legacy_adapters.py`：`_LEGACY_CROSSWALK`（内部 dict）→
   `LEGACY_CROSSWALK = MappingProxyType(...)`（`LegacyCrosswalkEntry` 本就是
   frozen dataclass）；`MISSING_CANDIDATE_TYPES` 同样 `MappingProxyType`。
   新增测试组：外部 dict 构造后 mutation 不影响对象；穿过对象改 nested 抛
   `TypeError`；`critical_unknowns` / `review` / EP 各 block / `dimensions`
   不可改；nested list → tuple；`LEGACY_CROSSWALK` / `MISSING_CANDIDATE_TYPES`
   不可写/不可删。
2. **nested schema parity 不完整（blocker）。** 之前只校验 required keys /
   顶层 enum / forbidden fields；runtime 会接受 frozen schema 明确拒绝的
   nested 数据（`additionalProperties: false` 下的 extra key、nested scalar
   类型、`minLength`、array-item 类型、日期 pattern）。
   → `decision_model.py` 新增 `_check_block(required, allowed, closed=)`
   （`closed` 对应 `additionalProperties: false` → 精确 key 集）+ 逐 block
   scalar/型别/pattern 校验：
   - `measurement`：精确 key ⊆ {type,analyte,readout,result,unit}；前 4 个
     非空 string；`unit` string。
   - `provenance`：精确 5 key；`source_id` 匹配 `^SRC-[0-9]{8}$`；`source_type`
     ∈ 10 值；`source_identifier` 非空 string；`locator` string；
     `retrieved_at` 日期前缀。
   - `interpretation_boundary`：精确 4 key；前 3 个是 string tuple；
     `evidence_ceiling` 非空 string。
   - `derivation`：精确 2 key，均 string。
   - `study_context`：`additionalProperties: true` → 允许 extra key；3 个必填
     为 string；`n` ∈ int|str；`model`/`assay` string。
   - `review`：精确 3 key；`status == HUMAN_APPROVED`；`reviewer` 非空 string；
     `reviewed_at` 日期前缀。
   - `critical_unknowns[i]`：精确 {unknown,resolution}；`unknown` 非空 string；
     `resolution` ∈ 3 值。
   - `key_supporting/contradicting_evidence`：tuple of mapping。
   新增 meta-parity 测试：Python 侧 closed-block allowed-key 常量
   （`_MEASUREMENT_KEYS` / `_PROVENANCE_KEYS` / `_INTERPRETATION_KEYS` /
   `_DERIVATION_KEYS` / `_REVIEW_KEYS` / `_CRITICAL_UNKNOWN_KEYS`）== schema
   `properties` key 集；`context` / `instantiation` schema `additionalProperties`
   == false。加代表性 reject 测试若干。
   验收（写进 `decision_model.py` docstring 精神）：PR A runtime object 表示的
   每个字段，Python 构造 **不得** 接受 nested value —— 若该 value 仅因其
   intrinsic shape/type/enum 约束会被对应 frozen Data Layout schema 拒绝。
   （仍是 "Python executable mirror + parity test"，未引入 `jsonschema`。）
3. **`missing_candidate_types` 清单不完整（小 blocker）。** 原来只列 7 个，漏
   `INDICATION L00` / `PATIENT_TERRITORY L01` / `MODALITY L03` /
   `ADC_DESIGN L09` / `ADC_HIT L10`（后两个正是 `ADCConstruct` composite 明确
   spanning 的 L09/L10）。
   → `decision_objects.yaml` `missing_candidate_types` 补成完整 **12 个**非
   clean-1:1 Candidate Type；note 改为明确"完整集合 = 无 clean 1:1 legacy
   映射的 12 个 Level，加上 L04/L06/L13 即完整 L00–L14 ontology"。
   `legacy_adapters.py` 新增 `MISSING_CANDIDATE_TYPES`（level→type，
   `MappingProxyType`）+ import 期 `_check_missing_candidate_types_are_complete()`
   （与 one-to-one levels 并集 == `CANDIDATE_LEVELS` 且不相交）。新增测试：
   YAML↔Python 一致；并集完整且互斥；L09/L10 存在且 `ADCConstruct` 非 1:1。

审核方明确不要求改：5 个 composite 继续 `NotImplementedError`（已明确拒绝
推测性 decomposition + 指向 crosswalk，足够）；不得借这轮碰 `core_objects.yaml`
/ `gate_system.yaml` / Data Layout schemas / 冻结架构文档。

**改动文件（本轮）：** `src/objects/decision_model.py`、
`src/objects/legacy_adapters.py`、`src/objects/__init__.py`、
`src/contracts/decision_objects.yaml`、`tests/test_decision_model.py`（54 tests，
+16）、本 handoff、worklog。**未改** manifest（artifact 清单不变）。

**验证（本轮）：** `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover`
609 OK（555 + 54）/ `git diff --check` clean / 干净 tracked-tree worktree
`verify_repository_boundary` passed / 9 data_layout schema + `decision_objects.yaml`
结构合法 / CI 待绿。

**GitHub connector：** 审核方尝试写 PR #98 `REQUEST_CHANGES` review，仍
`403 Resource not accessible by integration`。

## 七、后续（PR B–D，未启动）

- **PR B** —— canonical Gate / GateSet 合同、Evidence Ladder、
  `Direction × Strength` 在新 GateSet 合同中的落地、`assessment_rule` /
  `decision_rule` / `fatal_gate_policy` / `required_gate_policy`、**第六个对象
  `Decision`**。旧 45-Gate 保持 `FROZEN_LEGACY`。
- **PR C** —— Matrix / provenance / 可复用 EP 引用机制。
- **PR D** —— `CRC-ADC-TARGET-GATESET-v1`，冻结 `TGT-01`–`TGT-08` 的
  context-specific 合同与 Evidence Ladder。
- 每个 PR 独立走 ChatGPT 审核，合并前不推进下一个。
