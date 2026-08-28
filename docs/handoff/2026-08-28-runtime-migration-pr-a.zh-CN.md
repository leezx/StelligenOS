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

## 七、后续（PR B–D，未启动）

- **PR B** —— canonical Gate / GateSet 合同、Evidence Ladder、
  `Direction × Strength` 在新 GateSet 合同中的落地、`assessment_rule` /
  `decision_rule` / `fatal_gate_policy` / `required_gate_policy`、**第六个对象
  `Decision`**。旧 45-Gate 保持 `FROZEN_LEGACY`。
- **PR C** —— Matrix / provenance / 可复用 EP 引用机制。
- **PR D** —— `CRC-ADC-TARGET-GATESET-v1`，冻结 `TGT-01`–`TGT-08` 的
  context-specific 合同与 Evidence Ladder。
- 每个 PR 独立走 ChatGPT 审核，合并前不推进下一个。
