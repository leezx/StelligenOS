# Handoff：Runtime Migration PR E14 —— MOD-TGT06@1.0.0 实现

## 任务信息

- 任务编号 / 分支：`task_20260831_runtime-migration-pr-e14`
- 基线：`origin/main` @ `aa80865`（PR #130 merge `aa57640` = PR E13 TGT-06 施工
  合同四轮 APPROVE 收口 + PR #131 approval record `aa80865` 之后）
- PR：待创建
- 时间：`2026-08-31`
- 授权：用户在 PR E13 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E14 冻结为 **MOD-TGT06@1.0.0 deterministic
  implementation**：「E14-1…E14-8 总体可以开工。它与已冻结 E13 contract 一致：
  TGT-06 是 configuration-specific existence-proof Gate；Option A / 6 legal
  pairs；ordered aggregation；Route A/B fatal；single IDENTIFIED_MULTI 不得绕过
  Route A；无 machine conflict resolver；无 numeric threshold。要求在写代码前再
  冻结 6 个 implementation tightenings，只消除 runtime discretion。」
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-06 primary Evidence Production
  Module 的确定性科学核心实现，严格实现冻结的 PR E13 施工合同）。`run()` 纯
  Python，只调 injected port，不上网 / 不开 subprocess / 不写仓库 / 不自增 ID /
  不接 live-cell-imaging·pH-sensitive-dye·surface-decay-flow·
  lysosomal-co-localization·recycling-vs-degradation·same-target-ADC retrieval /
  **包内不建 normalizer** / **不对 source-reported internalization number 做
  numeric coercion** / 不做 ontology·embedding·LLM 推理 / 不产 canonical
  Assessment 或 Decision / 不产 numeric·ranking score / 不产 internalization-rate·
  half-life·percent-internalized·colocalization-coefficient cutoff / 不发明
  ADC-effective internalization range / 不解析 `reproducibility_basis` 自由文本 /
  不把 UNKNOWN 变 PASS·HOLD·KILL / 不产 PUBLIC_FATAL_SIGNAL_ESTABLISHED。窄修
  binding：TGT-06 `primary_module_version` `0.0.0 → 1.0.0`。不改冻结的 E13 合同
  正文，不重构 MOD-TGT01 / MOD-TGT02 / MOD-TGT03 / MOD-TGT04 / MOD-TGT05 /
  MOD-TGT08，不解除 `MIGRATION_PENDING`（8 个 primary Module 建成 7 个，余 TGT-07）。

## 一、8 个 scoping 决策 + 6 个 required tightening

见 `manifests/runtime_migration_pr_e14_manifest.yaml` 的 `scoping_decisions`
（E14-1…E14-8）、`six_required_implementation_tightenings`（逐字）与
`frozen_proposal_evidence_role_mapping`。要点：

- **E14-1 包结构**：11 文件（`__init__` / `module.yaml` / `contracts` / `ports`
  / `classify` / `evidence` / `aggregate` / `completion` / `fatal_review` /
  `acceptance` / `module`）。`InternalizationEvidenceCompletion` 是 module-local
  run record，**不是**第七个 core object。`acceptance.py` 执行 E13 item
  13/10/11/12/16 的可执行检查，不是 17-item YAML parser。
- **T1 outcome-aware INDIRECT_STRONG**：`FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING`
  永不成为 positive INDIRECT_STRONG；`ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY`
  + `PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY` 是 HARD typed-fact
  incoherence（contract-constructor `ValueError`）。
- **T2 single classifier authority**：三种 DIRECT-quality failure kind 统一映射
  `evidence_rung=DIRECT` + `addressability_implication=OPPOSES_ADDRESSABILITY`；
  `aggregate.py` / `fatal_review.py` 只消费 classified result，不再判定科学资格。
- **T3 configuration identity canonicalise**：`internalization_configuration_ids`
  → `tuple(sorted(set(...)))`；三态在 constructor 强制；local id 撞
  `CTX-CRC-REFRACTORY-MCRC` 为 HARD；所有 identity 逻辑只走
  `configuration_identity_projection`。
- **T4 exact audit identity**：`attempted` completion = 恰好一个 normalized
  `SEARCH_COMPLETION_AUDIT`（`observation_id == audit_observation_id`）+ 恰好一个
  provenance-bearing 匹配 EP；逐字段 snapshot parity；completed landscape 上
  `qualifying_direct_configuration_ids` == 全部 qualifying DIRECT-rung
  observation（productive 或 failure）的 projection 并集。**无**
  `qualifying_indirect_configuration_ids`。
- **T5 reuse / dedup parity**：`claim` + `antibody_identity` +
  `epitope_identity_or_region` + `affinity_context` + `conjugation_context`
  加入 exact reuse / true-dedup parity（连同 `internalization_outcome` 等 typed
  fields）；任一漂移 = HARD。
- **T6 neutral-claim number 不是 threshold**：`acceptance.py` 的 no-numeric-
  threshold 只扫 Module-owned text（`aggregation_rationale` + critical unknowns +
  `directly_supports`），不扫 `package.claim`；无 `float()` / `Decimal()`，无
  Module-authored numeric internalization 比较 / 归一 / 打分。
- **frozen evidence-role mapping**：clean productive existence proof 下的
  different-configuration failure 是 **CONTEXTUAL, not CONTRADICTING**。

## 二、frozen_evaluation_order（`aggregate.py` 直接硬编码，stop-at-first-match）

0. 未 completed / audit 无效 → item-16 stop rule（`module.py`）。
1. 按 `configuration_identity_projection` 分组所有 DIRECT-quality observation。
2. ≥1 CLEAN / uncontested productive DIRECT configuration → **POSITIVE / DIRECT**
   （existence-proof dominance：压过 heterogeneous failure，也压过别处的
   conflicted configuration）。
3. 否则 同一 configuration identity 同时带 productive DIRECT 与 DIRECT-quality
   failure → **CONFLICTING / DIRECT**（v1 无 machine conflict resolver）。
4. 否则 ≥2 独立 DIRECT-quality failure configuration，无 productive DIRECT →
   **NEGATIVE / DIRECT**。
5. 否则 恰好 1 个 DIRECT-quality failure configuration，无 productive DIRECT →
   **INCONCLUSIVE / DIRECT**（单一 configuration 失败永不成为 target-wide
   non-internalization）。
6. 否则 无 DIRECT-rung observation 但有 qualifying positive INDIRECT_STRONG →
   **POSITIVE / INDIRECT_STRONG**（highest-qualifying-rung authority）。
7. 否则 WEAK-only / 无 qualifying evidence → **INCONCLUSIVE / UNKNOWN**，零 refs。

6 个 legal Direction × Strength pair：`POSITIVE/DIRECT`、
`POSITIVE/INDIRECT_STRONG`、`NEGATIVE/DIRECT`、`CONFLICTING/DIRECT`、
`INCONCLUSIVE/DIRECT`、`INCONCLUSIVE/UNKNOWN`。

## 三、fatal_review（`fatal_review.py`）

- completed + audited landscape 才可能触发。
- **global precondition（HARD lock）**：landscape 上存在任一 qualifying
  productive DIRECT configuration → `required=False`、`status=""`。
- 合格 contributor：classified `qualifying_direct_failure`，kind ∈
  {`ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING`,
  `ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY`, `TRAFFICKING_OR_RECYCLING_ONLY`}
  （由 classifier 保证 disease-relevant QUALIFIED context —— 含 QUALIFIED
  WELL_MATCHED_CRC_MODEL —— + QUALIFIED assay + FAILS outcome + 已披露
  configuration identity；detector 不再复判）。
- **Route A**：某一个 `IDENTIFIED_MULTI` contributor，projection size ≥ 2，
  `reproducibility_status == QUALIFIED` + 非空 basis（basis 文本不解析）。
- **Route B**：≥2 个 **DISTINCT** eligible failure **observation** 且其
  projection 并集 size ≥ 2。单个 `IDENTIFIED_MULTI` observation 无论 projection
  cardinality 都不满足 Route B。`>= 2`，非 `> 2` 非 `>= 3`。
- ordinary Gate NEGATIVE ≠ machine `POTENTIAL_FATAL_PATTERN`：单个
  `IDENTIFIED_MULTI {A,B}` failure 仍投影出 2 个 failure config、仍可支撑
  NEGATIVE / DIRECT，但无 `reproducibility_status == QUALIFIED` 时不触发 fatal。
- machine 只出 `POTENTIAL_FATAL_PATTERN`，且仅在 accepted run 上 actionable；
  不是 proposal envelope 字段。

## 四、binding / registry 窄修（E14-8）

- `src/contracts/crc_adc_target_gateset.yaml`：TGT-06 `primary_module_version`
  `0.0.0 → 1.0.0` + 注释；`primary_module_binding.rule` 文案；
  `built_module_versions` 增 `TGT-06: "1.0.0"`。
- `src/objects/crc_adc_target_gateset.py`：`BUILT_MODULE_VERSIONS` 增 `TGT-06` +
  注释；剩余未建 = 仅 `TGT-07`。
- `gate_modules/README.md`：MOD-TGT06 注册表行 + 「其余一个 TGT primary
  Module（TGT-07）」。
- `tests/test_gate_modules_boundary.py`：新增 `Tgt06ModuleManifestTests`。
- 窄改 built-roster 断言：`test_crc_adc_target_gateset.py`（sample gate
  `TGT-06 → TGT-07`；`_BUILT_MODULE_VERSIONS` 增 TGT-06）、`test_tgt02/03/05/08
  module.py` 与 `test_tgt02/03/04/05/08 module_construction_contract.py`
  （TGT-06 → built；allowed-package tuple 增 `tgt06_internalization_trafficking_addressability`）。
- `tests/test_tgt06_module_construction_contract.py`：`NoImplementationInPrE13Tests`
  → `ContractIsFrozenAndImplementedInPrE14Tests`，指向 E14 后仓库状态。
- 未触碰 PR A/B/C 合同、PR D TGT-06 science、其它 Module。

## 五、测试

- `tests/test_tgt06_module.py`：67 条 synthetic in-memory 测试（无网络 / 无真实
  数据 / 无持久化）。覆盖 binding + boundary、rung classification + T1/T2、
  frozen_evaluation_order + evidence-role mapping、configuration identity + T3、
  completion invariants + T4、fatal_review + T2/T6、exact reuse / improved dedup
  + T5、duplicate `observation_id` preflight（proposal None、`allocator.calls
  == 0`、source resolver 未调用、EP 构造跳过）、no-numeric-threshold + T6、
  typed-fact coherence + T1、输出面、study_context `treatment_state`。
- 本地全量 `python -B -m unittest discover -s tests -p 'test_*.py'`：**1702 OK**
  （E13 收口 1629 → +67 新实现测试 + 少量 reconciliation / rename 断言）。

## 六、状态 / Next

- 8 个 primary Module 施工合同已 APPROVE 7 个；**已实现 7 个**（TGT-01/02/03/04/
  05/06/08 @ 1.0.0）。`MIGRATION_PENDING` 保持。
- 提交 PR → 轮询 CI（python 3.11 + 3.12 matrix）→ 把 E14 实现级审核请求提交
  ChatGPT `AI审核方案`。APPROVE 后 merge + 独立 approval-record PR（review log +
  manifest → approved）。
- fatal-first 余下 **TGT-07**：PR E15 = 施工合同（需独立 go-ahead），PR E16 =
  实现。8 个 primary Module 全部建成后才解除 `MIGRATION_PENDING`。
