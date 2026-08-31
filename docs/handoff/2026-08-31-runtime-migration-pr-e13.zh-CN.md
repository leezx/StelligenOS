# Handoff：Runtime Migration PR E13 —— TGT-06 / MOD-TGT06 construction contract

## 任务信息

- 任务编号：`task_20260831_runtime-migration-pr-e13`
- 分支：`task_20260831_runtime-migration-pr-e13`
- 基线：`origin/main` @ `6ef1892`（PR #128 merge `f09ab3d` = PR E12
  MOD-TGT04@1.0.0 三轮 APPROVE 收口 + PR #129 approval record `6ef1892` 之后）
- PR：待创建
- 时间：`2026-08-31`
- 授权：用户在 PR E12 收口后 "go on"；开工前审核方（ChatGPT `AI审核方案`）给出
  **APPROVE-to-proceed**，把 E13 冻结为 **TGT-06 / MOD-TGT06 Construction
  Contract, design-only**，并给了 **7 个关键 freeze point** + 逐条 E13-1…E13-8
  修正 + 3 条 headline conclusion。
- 变更定位：`CONTRACT_ADD`（设计冻结，与 E1 / E3 / E5 / E7 / E9 / E11 同型）。只交
  17 项施工合同 + human-readable drawing + parity / validation tests + 17 项验收
  清单 + manifest + handoff + worklog append；**不含任何实现**。Module 在 PR E14
  才开工，且必须在本合同 APPROVE 之后。`primary_module_version` 保持 `0.0.0`；
  binding / registry / README / built-roster test 一律不动（唯一既有文件改动是
  append `logs/worklog.md`）；`MIGRATION_PENDING` 保持。

## 一、7 个关键 freeze point（审核方 closing summary，逐字冻结在合同）

1. **Option A** —— qualifying `INDIRECT_STRONG` addressability landscape 传播成
   `POSITIVE / INDIRECT_STRONG`；TGT-06 **不是** TGT-04 那种 single-tier gate
   （frozen PR D 把 constitutive endocytosis / non-CRC antibody-induced
   internalization / successful same-target ADC 定义为 "strong support"，
   `unknown_behavior` 只锁在 "No internalization data for any configuration"）。
2. **Legal Direction × Strength pair 恰好 6 个**（不是我提的 8 个）：
   `POSITIVE/DIRECT`、`POSITIVE/INDIRECT_STRONG`、`NEGATIVE/DIRECT`、
   `CONFLICTING/DIRECT`、`INCONCLUSIVE/DIRECT`、`INCONCLUSIVE/UNKNOWN`。无
   `NEGATIVE/INDIRECT_STRONG`、`CONFLICTING/INDIRECT_STRONG`、
   `INCONCLUSIVE/INDIRECT_STRONG`、`INCONCLUSIVE/WEAK`。
3. **一个** independent DIRECT-quality failure configuration + 无 productive
   DIRECT → `INCONCLUSIVE / DIRECT`，**不是** `NEGATIVE`（PR D
   forbidden_inference：a single non-internalizing configuration → target is
   non-internalizing 是 FORBIDDEN）。
4. `NEGATIVE / DIRECT` 与 potential fatal 都需要 **multiple independent
   antibody / epitope configurations**。
5. **Route A 本身**必须是 declared multi-configuration analysis（`>= 2` unique
   configuration id）—— 单个 configuration 的 reproducibility 不能绕过 frozen
   PR D 的 "multiple independent configurations"。
6. **`WELL_MATCHED_CRC_MODEL` 可以进 fatal contributor**（与 TGT-04 相反）——
   frozen PR D TGT-06 fatal 句没限定 "on CRC malignant cells"，DIRECT authority
   本身就是 "in a disease-relevant context"。**但**任何 qualifying productive
   DIRECT existence proof 都取消 target-wide surface-static machine fatal trigger。
7. Completion **不建立** `qualifying_indirect_configuration_ids`；DIRECT
   integrated evidence 永远不能靠不同 observations / configurations 拼接产生。

## 二、E13-1…E13-8 scoping 决策（逐字见 manifest `scoping_decisions`）

- **E13-1 Scope / files（批准）**：文件名
  `tgt06_internalization_trafficking_addressability.yaml` /
  `TGT-06_Internalization_Trafficking_Addressability.md` /
  `test_tgt06_module_construction_contract.py`。canonical Gate 名
  "Internalization / Trafficking Addressability"。`MIGRATION_PENDING` 保持
  （八个 Module 全建完才解除；余下 TGT-06 → TGT-07）。main 当前 built 6 个
  （TGT-01/02/03/04/05/08）。
- **E13-2 Template / parity（批准）**：items 03/05/07/08 normalized-equality
  parity vs 冻结 PR D TGT-06；item 04 EXACT set-equality。**确认：frozen PR D
  TGT-06 无 `inference_guard` 字段** —— EVGAP-01 是 TGT-04 专属，TGT-06 无等价
  external guard，Module 不得自造。
- **E13-3 Direction × Strength（Option A + truth table）**：见 freeze point
  1/2/3 与合同 item 06 `tgt06_specific_aggregation_truth_table`。
  **Existence-proof dominance** —— Config A productive+lysosomal、B fails、
  C fails → 仍 `POSITIVE / DIRECT`（不是 NEGATIVE、不 auto-CONFLICTING）。
  **Different configurations 表现不同 ≠ CONFLICTING**（HARD lock）。
  **No cross-observation synthesis of DIRECT** —— EP-A "config A internalizes" +
  EP-B "config B reaches lysosome" 不合成 DIRECT，即使同一 target；DIRECT 必须
  来自 ONE upstream-qualified INTEGRATED configuration observation。
  `internalization_direction_mapping`：`PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY`
  → SUPPORTS；`FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING` → OPPOSES；
  `MIXED_OR_UNRESOLVED / NOT_ESTABLISHED` → CONTEXTUAL；
  `INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED` → 只在 INDIRECT_STRONG
  ceiling 上的 positive support，never DIRECT，never OPPOSES。
- **E13-4 Fatal review（Route A / Route B，Route A 收窄）**：见 freeze point
  4/5/6。GLOBAL PRECONDITION —— 无 qualifying productive DIRECT configuration
  （任一 productive DIRECT 取消 trigger）。fatal contributor：DIRECT-class
  antibody-induced internalization observation（`observation_kind` ∈
  {`ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING`,
  `ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY`}）+ QUALIFIED disease-relevant
  context（`CRC_MALIGNANT_CELLS` **或** `WELL_MATCHED_CRC_MODEL`）+ QUALIFIED
  assay validation + 非空 `assay_method` + `internalization_outcome ==
  FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING` + 各自 auditable basis。
  Route B `>= 2` unique `internalization_configuration_id`，**不是** `> 2` /
  `>= 3`。non-internalizing-payload strategies 在 fatal call 之外（逐字 pin 进
  item 08）。status 单值 `POTENTIAL_FATAL_PATTERN`；仅 accepted run actionable；
  机器永不 `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / fatal flag / KILL / HOLD /
  Decision；不在 proposal envelope 上。
- **E13-5 InternalizationEvidenceCompletion（名称批准，4 轴改名）**：
  `antibody_configuration_internalization_search_complete` /
  `productive_trafficking_search_complete` /
  `same_target_adc_functional_delivery_search_complete` /
  `receptor_endocytosis_and_inference_search_complete`。umbrella
  `public_internalization_search_complete == all(four)`；矛盾 → HARD。
  **只有一个** qualifying configuration set —— `qualifying_direct_configuration_ids`
  （见 freeze point 7；**没有** `qualifying_indirect_configuration_ids`）。
  completion ↔ `SEARCH_COMPLETION_AUDIT` snapshot parity（E6/E8/E10 gene）。
- **E13-6 Source-plan hard locks（批准 + 3 extra）**：surface localization alone
  → WEAK；receptor-family membership → WEAK；constitutive endocytosis /
  internalizing-receptor biology → INDIRECT_STRONG ceiling；non-CRC
  antibody-induced internalization → INDIRECT_STRONG（never DIRECT；DOES grant
  `POSITIVE / INDIRECT_STRONG`）；functional ADC delivery precedent 必须是
  GENUINELY SUCCESSFUL same-target ADC；disease-relevant productive
  antibody-induced internalization + lysosomal delivery → DIRECT（只在
  `context_class` ∈ {`CRC_MALIGNANT_CELLS`, `WELL_MATCHED_CRC_MODEL`} +
  QUALIFIED context + auditable basis，永不凭 crc_specific alone）。
  **Extra hard lock 1** —— internalization observed 但 lysosomal delivery 未确认
  → ≤ INDIRECT_STRONG。**Extra hard lock 2** —— no cross-observation synthesis of
  DIRECT。**Extra hard lock 3** —— "a same-target ADC exists / had a program"
  （TGT-01 territory）≠ TGT-06 functional delivery precedent。cross-gate —— TGT-04
  / TGT-02 / TGT-03 各 ≠ TGT-06；internalization ≠ efficacy / payload release。
- **E13-7 Stop rule + EXPERIMENT_REQUIRED（方向批准，后半随 Option A 修改）**：
  precedence 0(HARD)→1(incomplete → INCONCLUSIVE/UNKNOWN, zero refs)→2(complete
  但 audit invalid → HARD)→3(complete+audited → 按 item-06 truth table)。
  WEAK-only completed landscape → `INCONCLUSIVE / UNKNOWN`；public source space
  exhausted → `EXPERIMENT_REQUIRED` "test additional independent antibody /
  epitope configurations ..."（措辞必须强调 ADDITIONAL INDEPENDENT
  CONFIGURATIONS）。unresolved item kind —— `KNOWN_PUBLIC_NOT_YET_RESOLVED` →
  `PUBLIC_RESOLVABLE`；`ACCESS_OR_ANNOTATION_BLOCKED` → `CURRENTLY_UNRESOLVABLE`。
- **E13-8 Items 10–17 runtime genes + E14 conceptual shape**：8 observation
  kinds（见下）；`internalization_outcome` CLOSED enum（保留 `_OR_TRAFFICKING`）；
  `declared_multi_configuration_analysis` single-vs-multi identity pattern +
  `configuration_identity_basis` + `antibody_identity` /
  `epitope_identity_or_region` / `affinity_context` / `conjugation_context`
  （OPEN strings，非全需）；WHO 需要 configuration id（DIRECT-quality 总要；
  non-CRC internalization 在 source 标明 configuration 时要；constitutive
  endocytosis / same-target-ADC precedent 不要，也不因缺失被拒）；typed context
  qualification（`context_class` / `context_adequacy_status` + basis，DIRECT 不凭
  crc_specific alone）；`assay_validation_status` closed + DIRECT 需非空
  `assay_method`（vocab open）；**无 raw-value 分支**（source-reported number 进
  neutral claim string，由 ordinary parity 覆盖；禁止 Module 拿它比 threshold）。

## 三、三条 headline conclusion（写在合同顶部，审核方原话）

1. Internalization is configuration-specific, not a target-intrinsic constant.
   One qualifying disease-relevant antibody / epitope configuration with
   productive antibody-induced internalization and lysosomal delivery is
   sufficient DIRECT existence proof for addressability; failure of one
   configuration is only configuration-level opposing evidence and can never
   establish target-wide non-internalization.
2. DIRECT productive-addressability authority requires an auditable integrated
   observation tying antibody-induced internalization and lysosomal delivery to
   the same antibody / epitope configuration in a disease-relevant context.
   Surface localization, receptor-family inference, constitutive endocytosis,
   internalization without confirmed lysosomal delivery, non-CRC internalization
   and successful same-target ADC precedent remain lower-ceiling evidence and may
   not be combined across unrelated observations or configurations to synthesize
   DIRECT.
3. A target-wide surface-static potential fatal pattern requires
   productive-internalization / trafficking failure across multiple independent
   qualified antibody / epitope configurations and no qualifying productive
   DIRECT existence proof in the completed landscape. The machine may surface
   only POTENTIAL_FATAL_PATTERN; it never decides fatality, ADC efficacy, KILL,
   HOLD or a Candidate-level Decision.

## 四、交付物

- `src/contracts/gate_modules/tgt06_internalization_trafficking_addressability.yaml`
  —— 17 项施工合同。
- `docs/gate_modules/TGT-06_Internalization_Trafficking_Addressability.md`
  —— 17 行表 + 3 条 headline blockquote + normalized-observation /
  `InternalizationEvidenceCompletion` conceptual shape。8 observation kinds：
  `ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING` /
  `ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY` / `TRAFFICKING_OR_RECYCLING_ONLY`
  / `SAME_TARGET_ADC_DELIVERY_PRECEDENT` /
  `CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY` /
  `RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE` / `SURFACE_LOCALIZATION_ONLY_INFERENCE` /
  `SEARCH_COMPLETION_AUDIT`。
- `tests/test_tgt06_module_construction_contract.py` —— **73 tests**（10 类；
  checklist completeness + E1-template reuse；items 03/05/07/08
  normalized-equality parity + item 04 **exact set equality** derived parity +
  no-inference_guard confirmation；existence-proof / highest-qualifying-rung
  grading authority + 六个 legal pair + aggregation truth table +
  existence-proof dominance + no-cross-observation-synthesis-of-DIRECT；7 个
  freeze point 冻结；fatal Route A / Route B（都 multi-configuration，
  `WELL_MATCHED_CRC_MODEL` eligible，productive DIRECT 取消 trigger）；source
  hard locks；E2/E4/E6/E8/E10/E12 gene inheritance；no-implementation
  reconciliation —— 包 dir 不存在、binding 仍 0.0.0、binding / registry / 既有
  test 未动、只 append worklog；drawing 覆盖 17 项）。
- `manifests/runtime_migration_pr_e13_manifest.yaml`、本 handoff。

## 五、验证

- `tests/test_tgt06_module_construction_contract.py` **73 OK**；全量
  **1611 OK**（PR E12 收口 1538）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项
  （`AI_RESULT_ACCEPTANCE.md`、`CRC Patient Territory Map.png`、
  `STELLIGEN_CONSTRAINTS.md`、`pipelines/`、`.claude/scheduled_tasks.lock`）。
- `git diff --check` clean；contract + manifest YAML 合法且无
  list-element-parsed-as-dict。
- `src/` 不 import `gate_modules/`。

## 六、状态与下一步

- 8 个 primary Module 施工合同已 APPROVE 7 个（TGT-01/05/08/02/03/04 + 本 PR 待审）；
  已实现 6 个（TGT-01/02/03/04/05/08 @ 1.0.0）。MOD-TGT06 `primary_module_version`
  仍 `0.0.0`。`MIGRATION_PENDING` 保持。
- Next：开 PR、CI 绿后回 `AI审核方案` 贴 E13 review。APPROVE 后 PR E14 =
  MOD-TGT06@1.0.0 实现，需各自 go-ahead。fatal-first 余下 TGT-07。
