# Handoff：Runtime Migration PR D —— CRC-ADC-TARGET-GATESET-v1

## 任务信息

- 任务编号：`task_20260828_runtime-migration-pr-d`
- 分支：`task_20260828_runtime-migration-pr-d`
- 基线：`origin/main`（PR #103 merge，PR C 收口后）
- PR：待创建（#104）
- 时间：`2026-08-28`
- 授权：用户"Runtime Migration PR A–D，逐一来做" + "继续直到完成所有 PR A-D"；
  PR C APPROVE 后审核方"下一步可以进入 PR D — ADC_TARGET_GATESET 的 CRC-specific
  binding + TGT-01…TGT-08 concrete Evidence Ladders/contracts"。
- 变更定位：`RUNTIME_CONTRACT_ADD`（第四层：canonical ADC_TARGET_GATESET 的
  context-specific 首次施工实例。不删 legacy、不改冻结文档、不加依赖、不做
  evaluator、不建 Evidence Production Module、不新增 canonical gateset_id）。

## 一、依据（冻结文档，本 PR 不修改，只按其顺序施工）

- CURRENT_SYSTEM v5 §6.4（第一施工实例固定：candidate_type=ADC Target /
  context=refractory mCRC / modality=ADC / gateset=CRC-ADC-TARGET-GATESET-v1 /
  public evidence only；TGT-01–TGT-08 的科学名称与 L04 归属；Module 不得改名 /
  合并 / 拆分 / 重新归属；一 Gate 一主 Module）、§11.2（EVGAP-01 → 贡献 TGT-04
  surface-localization，不 discharge density；EVGAP-02 → primarily TGT-02，不
  自动支持 TGT-03；"科学审核确认后才写入 Context-specific Evidence Ladder"）、
  §16 B 组问题 21 / 23（PR D = 冻结 TGT-01…TGT-08 context-specific contract 与
  Evidence Ladder）。
- contract.zh-CN.md §3.4。
- Data Layout Spec v1.0 §6（gate_binding）、§7.3（gateset_binding）、附录 A
  （`Module = MOD-<GATE 无连字符>`）。
- `src/contracts/data_layout/gate_binding.schema.yaml`（`v1.0` / `APPROVED`）：
  本 PR 的 binding 记录与其 `oneOf`（gate_binding / gateset_binding）做 parity。

## 二、两个决策（审核方在 `AI审核方案` 拍板）

1. **Decision A = A2′：骨架 + 8 个 concrete three-rung Evidence Ladders 作为
   PR draft，科学审核在 PR #104 内完成。** A1（只冻结结构骨架）会让 PR D 变成
   空壳，把科学合同偷偷 defer 到 PR E；A3（写满 production science rules，含
   quantitative cutoff / patient-fraction / molecules-per-cell 等）是无来源发明。
   PR D 只冻结 **evidence-class semantics / ceilings / inference boundaries**，
   不发明 numeric biological thresholds。REQUEST_CHANGES until scientifically
   acceptable → APPROVE → merge == v1.0 frozen ladders（与 PR A/B/C 同款：代码
   先做 proposal，PR review 本身就是冻结机制）。
2. **Decision B = B1：PR D 建立第一份 machine-readable TGT-01…TGT-08 roster。**
   CURRENT_SYSTEM v5 §6.4 是 ID / name / L04 ownership 的 frozen normative
   basis，但 v5 把完整 Gate 骨架指向外部 Blueprint v0.1 §H2.4（不在仓库），且
   没有任何冻结仓库文档给出 per-Gate machine `gate_version`。因此 PR D 初始化
   `gate_version = "1.0"`，并在合同里明确"NOT claimed to be copied from a
   pre-existing per-Gate version in Blueprint prose"。
   - 顺带锁死：`CRC-ADC-TARGET-GATESET-v1` 只能是 program label，绝不进
     `gateset_id`；PR D 不建 primary Module —— 只冻结 `MOD-TGT0n` binding slot，
     `primary_module_version = "0.0.0"`（declared, not built）。

## 三、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/crc_adc_target_gateset.yaml`（新） | 声明式 registry：`program_label`（never a gateset_id）；`normative_basis` / `gate_version_provenance` / `scientific_review` / `boundary`；`roster`（8 行：gate_id + name + dominant_evidence_regime）+ `roster_constants`（level L04 / gateset_id ADC_TARGET_GATESET / gate_version "1.0"）+ `roster_invariants`；`gateset`（ADC_TARGET_GATESET@1.0，8-gate members，4 policy refs）；`instantiation`（INST-CRC-REFRACTORY-ADC-TARGET-v1，PUBLIC_ONLY）；`gate_contracts`（每 gate：`gate_question` / `evidence_required` / `evidence_ladder`（DIRECT / INDIRECT_STRONG / WEAK 各 `admissible_evidence_classes` + `ceiling_rule`）/ `evidence_ceiling` / `allowed_inference` / `forbidden_inference` / `unknown_behavior` / `fatal_conditions`；TGT-02/03/04 带 `inference_guard` 引用 v5 §11.2 的 EVGAP 映射）；`context_specific_bindings`（1 个 gateset_binding + 8 个 gate_binding，parity vs 冻结 gate_binding.schema.yaml；`primary_module_id = MOD-TGT0n`、`primary_module_version = "0.0.0"`）；`primary_module_binding`（slot 规则）；`migration.deferred`（primary Modules / quantitative calibration → PR E+；evaluators = not in repo）。 |
| `src/objects/crc_adc_target_gateset.py`（新） | frozen `@dataclass`：`TgtGateSpec`（gate_id ∈ TGT-01..08、name == `TGT_GATE_NAMES[gate_id]`、level L04、gateset_id ADC_TARGET_GATESET、gate_version "1.0"、regime == `TGT_GATE_REGIMES[gate_id]`）；`TgtGateContract`（compose PR B `EvidenceLadder`；`allowed/forbidden_inference` / `fatal_conditions` 非空 tuple；`primary_module_id == MOD-<gate 无连字符>`、`primary_module_version == "0.0.0"`；**共享字段校验 delegate 给 PR B `Gate.__post_init__`**——构造一个 `Gate` 触发 canonical-gateset / regime / external-ref / MOD-id-pattern 校验）；`CrcAdcTargetGateSetV1`（roster / gateset / instantiation / gate_contracts 必须 == 恰好 TGT-01..08 且顺序一致、全部 L04、全部 "1.0"、gateset_id 永远 ADC_TARGET_GATESET、每 contract.gate_spec == roster 行）。import 期：`PROGRAM_LABEL` 不匹配 `_GATESET_ID`；`CANONICAL_GATESET_IDS["L04"] == ADC_TARGET_GATESET`；name / regime map 覆盖恰好 8 个。**只从 PR A/B/C import，不修改。** |
| `src/objects/__init__.py`（改） | 追加 PR D export；PR A/B/C / legacy 符号不变。 |
| `tests/test_crc_adc_target_gateset.py`（新，27 tests） | 见 §四。 |
| `manifests/runtime_migration_pr_d_manifest.yaml`（新） | `chatgpt_review: PENDING`、`scientific_review` 说明、boundary 声明、test 命令、artifact 清单。 |
| `src/objects/README.md` / `src/contracts/README.md`（改） | 追加 PR D 段落。 |

## 四、测试（`tests/test_crc_adc_target_gateset.py`，27 tests）

- `ContractBuildsTests`：YAML → runtime 对象（`_build()`）成功；`migration.pr ==
  runtime_migration_pr_d`、`deferred` 含 primary Modules、有 `scientific_review`
  / `gate_version_provenance`；`program_label.never_a_gateset_id` 为真，且
  `gateset` / `instantiation` / 8 个 gate_binding / gateset_binding 的
  `gateset_id` 全部 == `ADC_TARGET_GATESET`。
- `RosterParityTests`：YAML roster == `TGT_GATE_IDS`；每行 name == `TGT_GATE_NAMES`；
  `roster_constants` = L04 / ADC_TARGET_GATESET / "1.0"；8 个 gate 科学名称
  （空白归一化后）在冻结 CURRENT_SYSTEM v5 §6.4 正文中出现。
- `BindingParityTests`：8 个 gate_binding 的 key 集 == 冻结
  `gate_binding.schema.yaml` `$defs.gate_binding.properties`，required ⊆ key 集；
  gateset_binding 同理；`primary_module_id` / `gateset_id` 匹配 schema pattern，
  `dominant_evidence_regime` / `candidate_level` ∈ schema enum，3 个 `*_ref` 走
  `external:`。
- `NoModuleInPrDTests`：每个 gate_binding `primary_module_version == "0.0.0"`
  且 `primary_module_id == MOD-<gate 无连字符>`；`primary_module_binding.unbuilt_version
  == "0.0.0"`；`src/objects/` 下没有 `mod_tgt0n.py`。
- `TgtGateSpecTests`：valid；gate_id `TGT-09` / 错 name / level L05 /
  gateset_id `ADC_EPITOPE_GATESET` / gate_version `2.0` / TGT-04 regime 写成
  `PUBLIC_PRIMARY` → 各自 raise。
- `TgtGateContractTests`：valid；`primary_module_version="1.0.0"` → raise；
  `primary_module_id="MOD-TGT99"` → raise；非 `external:` ref → raise；空
  `allowed_inference` / `fatal_conditions` / `forbidden_inference=("",)` → raise；
  ladder 的 gate_id 与 gate_spec 不符 → raise。
- `CrcAdcTargetGateSetV1Tests`：`_build()` 有效；把 gateset_id 换成
  `CRC_ADC_TARGET_GATESET` → raise（program label 不能进 gateset_id）；roster
  乱序 → raise；gateset_version `2.0` → raise。
- `ImmutabilityAndBoundaryTests`：`TGT_GATE_NAMES` 只读；`TgtGateSpec` frozen；
  `evidence_required` 是只读 tuple；import PR A/B/C 模块正常、
  `CANONICAL_GATESET_IDS["L04"] == "ADC_TARGET_GATESET"`；`field_names` helper。

## 五、明确未改 / 未做

- **未新增** canonical `gateset_id`；`gateset_id` 永远是 `ADC_TARGET_GATESET`。
  `CRC-ADC-TARGET-GATESET-v1` 只是 program label。
- **未新增** `src/contracts/data_layout/` 下任何 schema（binding 记录与冻结
  `gate_binding.schema.yaml` 做 parity）。
- **未改** PR A（`decision_model` / `legacy_adapters` / `decision_objects.yaml`）、
  PR B（`gate_model` / `legacy_gate_map` / `gate_contracts.yaml`）、PR C
  （`evidence_reference_model` / `evidence_reference.yaml`）——只 import。
- **未改** 任何冻结文档、`gate_system.yaml`、`src/capabilities/*`、既有测试。
- **未做** evaluator（assessment / decision）、Evidence Production Module（8 个
  `MOD-TGT0n` 只是 declared slot，`0.0.0`）、quantitative ladder calibration、
  epitope 层——均 PR E+。
- **未解除** `MIGRATION_PENDING`（到 PR E）。无新依赖（仍只 PyYAML）。

## 六、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 743 tests ... OK   (716 baseline + 27 new)
git diff --check                       # clean
bash scripts/verify_repository_boundary.sh   # 干净 tracked-tree worktree 上 pass
python3 -c "import yaml; yaml.safe_load(open('src/contracts/crc_adc_target_gateset.yaml'))"  # 结构合法
```

## 七、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入；GitHub connector 写 review 仍 `403`）。**本 PR 的审核包含科学审核**：
  8 个 Evidence Ladder 的 evidence-class 划分 / ceiling / inference guard 是否
  科学可接受。REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与
  worklog、回同一对话复审。APPROVE → merge（= v1.0 frozen ladders）+ 独立
  docs-only approval-record PR（按 PR #95/#97/#99/#101/#103 先例）。

## 八、后续（PR E+，未启动）

- **PR E+** —— 逐 Gate primary Evidence Production Module（TGT-01…TGT-08）：每个
  Module 按 Blueprint v1.3 §H2.8 的 Gate Module Acceptance Template（17 项）绘
  施工图，审核通过后开工。Module 把 PR D 冻结的 evidence-class ladder 落成
  可执行证据生产，并可提出 quantitative calibration，但不得改 Gate id / name /
  question / ladder / ceiling / fatal / unknown 语义（v5 §6.4）。
- PR E 合并后方可解除 `MIGRATION_PENDING`。
