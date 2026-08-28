# Handoff：Runtime Migration PR B —— canonical Gate / GateSet / EvidenceLadder / Decision

## 任务信息

- 任务编号：`task_20260828_runtime-migration-pr-b`
- 分支：`task_20260828_runtime-migration-pr-b`
- 基线：`origin/main` @ `7555f8e`（PR #99 merge，PR A 收口后）
- PR：待创建
- 时间：`2026-08-28`
- 授权：用户"Runtime Migration PR A–D，逐一来做"；PR A APPROVE 后审核方
  "Merge 后可以正式进入 PR B"
- 变更定位：`RUNTIME_CONTRACT_ADD`（第二层运行时对象合同：Gate 系统两层规则 +
  第六个对象 Decision + legacy 45-Gate 迁移参考。不删 legacy、不改冻结文档、
  不加依赖、不引入 decision engine）

## 一、依据（冻结文档，本 PR 不修改，只按其顺序施工）

- CURRENT_SYSTEM v5 §6.1（两层规则显式分离）、§6.2（Evidence Ladder /
  Direction ⊥ Strength / ceiling）、§6.3（LEGACY_GATE_SYSTEM 冻结 → semantic
  migration → Canonical GateSet Registry）、§6.4（一 Gate 一主 Module）、
  §16 B 组问题 19。
- contract.zh-CN.md §3.4.1（Gate / GateSet 两层规则、第六个对象 Decision）。
- Data Layout Spec v1.0 §6（Gate folder / gate_binding）、§17（Decision）；
  `src/contracts/data_layout/decision.schema.json` /
  `gate_binding.schema.yaml`（`v1.0` / `APPROVED`，本 PR 与之 parity）。

## 二、三个决策（用户已拍板，均取推荐项）

1. **Decision policy = 只定义对象与 policy 声明形状，不做 engine。** PR B 定义
   `Decision` 对象（与 `decision.schema.json` exact parity）+ `decision_rule` /
   `fatal_gate_policy` / `required_gate_policy` / `unknown_policy` 的声明形状
   （以 `external:` ref 引用，与冻结的 `gate_binding.schema.yaml` 一致）。
   仓库内**无** `evaluate_decision()`。
2. **Evidence Ladder = 只定义形状，不放具体 ladder。** `EvidenceLadder` 定义
   rung 结构（`{grade, admissible_evidence_classes, ceiling_rule}` 有序、
   恰好 `DIRECT / INDIRECT_STRONG / WEAK` 各一次、最高在前）+ `evidence_ceiling`；
   TGT-01…TGT-08 的具体 rung 属 PR D。
3. **不新增 Gate 输出 envelope。** Gate 的 Direction ⊥ Strength 输出就是 PR A
   的 `CandidateGateAssessment`；legacy `GateModelOutput.score/status` 保持
   `FROZEN_LEGACY`，新 lineage 不引用它。

## 三、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/gate_contracts.yaml`（新） | 声明式 registry：`Gate@0.1.0` / `GateSet@0.1.0` / `EvidenceLadder@0.1.0` / `Decision@0.1.0` 的 required/optional/forbidden 字段、`field_kinds`、`allowed_values`、`id_patterns`；`two_rule_layers` 说明；`vocabularies`（`decision_values` 7 值、`dominant_evidence_regimes` 4 值、`ladder_grades` 3 值、`assessment_snapshot_cell_regex`、15 个 `canonical_gateset_ids`）；`legacy_gatechain_crosswalk`（3 条 legacy chain → canonical GateSets，逐字 v5 §6.3）；`legacy_gate_system`（`FROZEN_LEGACY`）；`migration.parity`（Decision=exact vs decision.schema.json；Gate/GateSet=consistency vs gate_binding.schema.yaml）；`migration.deferred`（concrete ladders / CRC-ADC-TARGET-GATESET-v1 → PR D，Matrix → PR C，逐 Gate Module → PR E+，decision engine = not in repo）。 |
| `src/objects/gate_model.py`（新） | frozen `@dataclass` + `__post_init__`，**复用 PR A `decision_model.py` 的 `_deep_freeze` / `_check_block` / `_require_*` / ID 正则**（两层合同校验方式不分叉）。词表 `DECISION_VALUES` / `DOMINANT_EVIDENCE_REGIMES` / `LADDER_GRADES` / `CANONICAL_GATESET_IDS`（`MappingProxyType`，import 期自检覆盖 L00–L14 且 id 合法）。对象：`LadderRung` / `EvidenceLadder`（rung 顺序强制）、`Gate`（`gateset_id` `^[A-Z0-9_]+_GATESET$`、`primary_module_id` `^MOD-[A-Z0-9]+$`、`dominant_evidence_regime` enum、`fatal_conditions` 可空、无 `score` 字段）、`GateSetMember` / `GateSet`（≥1 gate、4 个 `*_ref` 均 `external:`、无 inline policy body）、`TriggeredBy` / `Decision`（与 `decision.schema.json` exact parity：`decision` enum、`assessment_snapshot` 值 = 字符串 `"NOT_EVALUATED"` 或 closed `{assessment_id, assessment_version, cell}`、`cell` 正则、`review` closed 且 `HUMAN_APPROVED`、`not.anyOf` forbid `superseded_by`、`supersedes_decision_id` 可选、deep-frozen）。 |
| `src/objects/legacy_gate_map.py`（新） | `LegacyGateSystem` + `LEGACY_GATE_SYSTEM`（`gate_system` / `0.1.0` / topology `0.2.0` / 45 / `FROZEN_LEGACY`）；`LegacyGatechainCrosswalk` + `LEGACY_GATECHAIN_CROSSWALK`（`MappingProxyType`，3 条 chain）。import 期 `_check_agrees_with_kernel_topology()`：keys == `src.capabilities.gates.GATE_GROUPS`；`gate_count == len(GATE_IDS)`；每 chain legacy 计数 == `GATE_CATALOG` 分组计数（13/16/16）；canonical 目标 ⊆ `CANONICAL_GATESET_IDS.values()`。**不 import/不改** `gate_system.yaml` 或 `gates.py`。 |
| `src/objects/__init__.py`（改） | 追加 export；PR A / legacy 符号不变。 |
| `tests/test_gate_model.py`（新，37 tests） | 见 §四。 |
| `manifests/runtime_migration_pr_b_manifest.yaml`（新） | `chatgpt_review: PENDING`、boundary 声明、test 命令、artifact 清单。 |
| `src/objects/README.md` / `src/contracts/README.md`（改） | 说明 PR B 的对象与 `gate_model.py` / `legacy_gate_map.py`。 |

## 四、测试（`tests/test_gate_model.py`，37 tests）

1. **contract YAML shape** —— version、合同集合 `{EvidenceLadder, Gate, GateSet,
   Decision}`、`migration.deferred`（含 `decision_engine`）、
   `legacy_gate_system` `FROZEN_LEGACY` / `gate_count 45`。
2. **registry ↔ Python parity** —— `required_fields` == 无默认值字段集；
   `vocabularies` == 词表元组；`canonical_gateset_ids` == `CANONICAL_GATESET_IDS`；
   Decision `forbidden_fields` == `DECISION_FORBIDDEN_FIELDS`。
3. **Decision exact parity vs `decision.schema.json`** —— `required` 数组、
   `decision` enum、`triggered_by` items（closed，keys == `TriggeredBy` 字段）、
   `assessment_snapshot` oneOf（`const NOT_EVALUATED` + closed
   `{assessment_id, assessment_version, cell}`，`cell` pattern）、`review`
   closed + `status` const `HUMAN_APPROVED`、`not.anyOf` == forbidden、
   `additionalProperties: false`、ID pattern —— 全部逐一对齐。
4. **Gate / GateSet consistency vs `gate_binding.schema.yaml`** ——
   `dominant_evidence_regime` enum、`gateset_id` / `primary_module_id` pattern、
   `candidate_level` enum 一致；disk `gateset_binding` 必填的 3 个 policy ref
   ⊆ `GateSet` 必填字段，且 `GateSet` 另加 `unknown_policy_ref`（v5 §6.1）。
5. **逐对象 accept / reject** —— ladder rung 必须恰好三级且顺序正确；rung 坏
   grade / 空 class / 空 ceiling raise；Gate 坏 `gateset_id` / 坏 regime / 坏
   `MOD-` id / 空 `evidence_required` / 非 `external:` ref raise；GateSet 零 gate
   / 坏 id / 非 `external:` policy ref raise；Decision 坏 `DEC-` id / 坏
   `decision` / 非 `HUMAN_APPROVED` / 坏 `supersedes_decision_id` raise。
6. **deep immutability** —— 外部 dict 构造后 mutation 不污染 Decision；穿过对象
   改 `review` / `assessment_snapshot[...]` raise `TypeError`；
   `CANONICAL_GATESET_IDS` / `LEGACY_GATECHAIN_CROSSWALK` 不可写。
7. **legacy 45-Gate 拓扑未动** —— `len(GATE_IDS) == 45`、三组 13/16/16；
   `gate_system.yaml` 仍 `gate_count 45` / `architecture_version 0.2.0` /
   `topology_change_policy frozen_until_explicit_unfreeze`；`GateModelOutput`
   仍有 `score` / `status` 字段；`LEGACY_GATE_SYSTEM` 与 kernel 一致；crosswalk
   与 `gate_contracts.yaml` 一致。
8. **canonical gateset ids** —— 15 个、每 level 一个、均匹配
   `^[A-Z0-9_]+_GATESET$`、levels == `CANDIDATE_LEVELS`。

## 五、明确未改 / 未做

- `src/contracts/gate_system.yaml`、`src/capabilities/gates.py`（45-Gate 拓扑、
  `GateModelOutput.score/confidence/status`）—— `FROZEN_LEGACY`，未动。
- `src/contracts/decision_objects.yaml` / `src/objects/decision_model.py` /
  `legacy_adapters.py`（PR A）—— 未改（`gate_model.py` 只**import** PR A 的
  helper，不修改）。
- `src/contracts/data_layout/*.schema.*` —— Data Layout Spec v1.0 冻结，未改。
- `docs/architecture/*` —— migration PR 不改冻结文档。
- 无 decision engine（`evaluate_decision()` 不进仓库）；无具体 GateSet / ladder
  内容（PR D）；无 Matrix 机制（PR C）。
- 无新依赖（无 `jsonschema`）。无 persistence / 无执行 / 无数据 / 无 `.csv`；
  `src/` 未 import `genmodules/`。
- `MIGRATION_PENDING` 未解除（到 PR E 前不声称 Blueprint v1.3 conformance）。
- 用户自有 untracked 文件未暂存。

## 六、验证命令与结果

```
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
→ Ran 646 tests ... OK   (609 baseline + 37 new)

PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gate_model -v
→ Ran 37 tests ... OK

git diff --check → clean
# 干净 tracked-tree worktree（排除用户 untracked 文件）
verify_repository_boundary.sh → Repository boundary check passed. (exit 0)
python3 -c 'yaml.safe_load(gate_contracts.yaml)' → ok
```

## 七、审核

提交 PR 后在网页版 ChatGPT `Biotech ideas → AI审核方案` 提交审核。connector
写 review 若仍 `403`（前 5 个 PR 均如此），审核意见由 leezx 转述，落
`logs/chatgpt-review-2026-08-28-runtime-migration-pr-b.md`（APPROVE 记录按
PR #95/#97/#99 先例用独立 docs-only PR 补登）。

## 八、后续（PR C–D，未启动）

- **PR C** —— Matrix / provenance / 可复用 EP 引用机制（`evidence_package_ids`
  引用）。
- **PR D** —— `CRC-ADC-TARGET-GATESET-v1`：冻结 `TGT-01`–`TGT-08` 的
  context-specific Gate 合同与 Evidence Ladder（需科学审核）。
- 每个 PR 独立走 ChatGPT 审核，合并前不推进下一个。
