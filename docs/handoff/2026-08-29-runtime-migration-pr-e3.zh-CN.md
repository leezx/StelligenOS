# Handoff：Runtime Migration PR E3 —— TGT-05 / MOD-TGT05 Construction Contract

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e3`
- 分支：`task_20260829_runtime-migration-pr-e3`
- 基线：`origin/main`（PR #108 merge + PR #109 approval record 之后，PR E2 收口）
- PR：待创建
- 时间：`2026-08-29`
- 授权：用户 PR E2 APPROVE 后追加 "go ahead"；开工前审核方（ChatGPT
  `AI审核方案`）在 APPROVE 里说下一步是「真实 provider / external calibration，或
  按既定顺序开 TGT-05 的 construction drawing」。真实 provider / calibration 属外部
  workspace，不是 in-repo PR，故 in-repo 下一个 PR 由审核方拍板为 **PR E3 =
  TGT-05 / MOD-TGT05 Construction Contract**，并给了 8 个 scoping 决策
  E3-1…E3-8。
- 变更定位：`RUNTIME_CONTRACT_ADD`（第五层：TGT-05 primary Evidence Production
  Module 的**施工合同 + 施工图 + 验收清单 + parity 测试**。不写实现、不接
  provider、不产 EvidencePackage / Assessment、不改冻结文档、不新增依赖、不改
  MOD-TGT01、不改 TGT-05 `primary_module_version`、不解除 `MIGRATION_PENDING`）。

## 一、8 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

| # | 决策 |
|---|---|
| E3-1 | 下一 Gate = TGT-05，顺序不变（TGT-01→05→08→02→03→04→06→07）。machine identity：`TGT-05@1.0` / `ADC_TARGET_GATESET@1.0` / L04 / `INST-CRC-REFRACTORY-ADC-TARGET-v1` / `MOD-TGT05` / `module_version 0.0.0`（E3 未实现）。PR D 的 TGT-05 scientific contract 一字不改。 |
| E3-2 | E3 严格 design-only：contract + drawing + 17 项 checklist + validation/parity tests + manifest/handoff/worklog。**禁止** implementation / provider / adapter / runner / network / external data / runtime EvidencePackage 或 proposal / numeric scoring / new ladder semantics。**不建** generic GateModule framework / abstract base class，**不重构** MOD-TGT01。 |
| E3-3 | 17 项模板沿用**已批准的 E1 模板**（已被 PR E2 实际验证），不再重新发明。provenance 写明 `not_claimed_verbatim_from_blueprint`。item **03 / 05 / 07 / 08** 与冻结 PR D `crc_adc_target_gateset.yaml:TGT-05` 做 **normalized-equality parity test**，不是手工近似复制。 |
| E3-4 | **TGT-05 冻结成"单向 liability detector"，绝不能变成 safety predictor。** Direction 描述的是**证据相对 Gate 问题**、不是 candidate desirability —— TGT-05 `POSITIVE`/`DIRECT` 是很坏的 candidate signal，但 Module 不翻转 Direction；`HOLD`/`KILL` 是 GateSet Decision policy（PR B）的事。`NEGATIVE` 在当前 public path 上**基本不可达**：HPA/RNA/IHC negative、或一个没报毒的临床项目，都不能产生 `NEGATIVE = safe`。 |
| E3-5 | fatal semantics 把「单产品毒性」与「target-intrinsic convergence」彻底分开：1 个同靶点 ADC + explicit target-mediated toxicity → **DIRECT liability，非 target-wide fatal**；human protein 表达 / 同靶点 non-ADC 毒性 / translationally relevant NHP 毒性 → **INDIRECT_STRONG，非 fatal**；**≥2 个 materially distinct 同靶点 ADC construct + convergent target-mediated normal-tissue toxicity** → potential fatal signal。每条 clinical ADC toxicity observation 必须可审计 construct fingerprint（antibody/binder、linker、payload、format）+ **observed severity FOR THIS PRODUCT**（永不升成 target-wide severity）+ target-attribution basis + primary source。「materially distinct」与「是否真 target-mediated」保留 **human-review judgement**。无 numeric severity score，无 Candidate-level KILL。 |
| E3-6 | source plan 显式区分「liability evidence」与「vital-organ coverage completeness」。DIRECT/INDIRECT_STRONG/WEAK source class 按 PR D，硬锁：RNA-only ✗→ protein；whole-tissue protein ✗→ cell-surface accessibility；non-ADC severity ✗→ ADC；negative atlas ✗→ safety。coverage map 覆盖 CNS / cardiac / hepatic / pulmonary / hematopoietic / GI。**无 universal threshold**（organ count / TPM / IHC score / severity grade）。当前 Instantiation 是 `PUBLIC_ONLY`，E3 只设计 public path。 |
| E3-7 | **asymmetric fatal-sweep-mandatory stop rule**：Path A（发现 potential fatal pattern → `PUBLIC_FATAL_SIGNAL_ESTABLISHED`，停止追更弱 atlas/RNA，handoff human review）；Path B（只有一个 DIRECT ADC toxicity → **不能立刻停**，必须完成同靶点 ADC construct inventory + toxicity/discontinuation/attribution sweep）；Path C（无 DIRECT clinical liability → 系统性做 human-protein vital-organ coverage sweep + non-ADC 同靶点毒性 sweep + relevant NHP sweep + RNA-only sweep；无法解决 → `critical_unknown` = `EXPERIMENT_REQUIRED`）。核心：**absence of public risk evidence is not a stop condition for safety.** |
| E3-8 | items 10–17 直接**冻结**（不再复制 E2 代码）PR E2 已验证的 runtime genes：single authoritative canonical target identity、canonical SourceIndex provenance authority、Gate-neutral atomic EvidencePackage、exact canonical EP reuse（never recreate by old id）、classification-driving semantic parity on reuse、non-canonical proposal envelope、human approval → canonical CandidateGateAssessment、hard identity/provenance failure → machine reject、`UNKNOWN` ≠ integrity failure、no Decision / KILL / persistence / numeric score。 |

一句话（审核方原话）：**MOD-TGT05 的任务不是证明一个 target"安全"，而是尽可能
可靠地发现 target-level normal-tissue liability；public evidence 可以强力证实
风险，却通常不能证实风险不存在。** 这是 TGT-05 与 TGT-01 最大的科学结构差异。

## 二、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml`（新） | 机器施工合同：`migration`（pr `runtime_migration_pr_e3`、`next` PR E4、`order`）；`template_provenance`（`RECONSTRUCTED` + `template_basis` = approved E1 17-item template + `seventeen_item_template_reused_from_e1`）；`kernel_invariant`（单向依赖 + "one-way liability detector, never a safety predictor"）；`acceptance_checklist` **17 项**（键名与 E1 完全一致），其中 03 `gate_question` / 05 ladder+ceiling / 07 allowed·forbidden inference / 08 fatal_conditions（含 `potential_fatal_signal`）逐字继承 PR D TGT-05；06 Direction（liability detector 语义）；09 source plan（PUBLIC_ONLY、coverage map、硬锁、`no_universal_threshold`、`connect_provider_in_this_pr: false`）；13 machine acceptance（含 hard integrity → run rejected、no product-specific therapeutic-window conclusion）；16 asymmetric stop rule（Path A/B/C）；17 downstream（Module 不做 product-specific therapeutic-window conclusion、不 flip Direction）。`deferred_to_pr_e4_plus`；`repository_policy`（implementation / provider / numeric_scoring / biological_thresholds / product_specific_therapeutic_window_logic / generic_gatemodule_framework / modifies_mod_tgt01 全部 `forbidden`，`migration_pending: remains`）。 |
| `docs/gate_modules/TGT-05_Normal_Tissue_Fatal_Liability.md`（新） | 人读施工图：本文件是什么、MOD-TGT05 做什么·不做什么（liability detector）、template provenance（复用 E1 + parity）、gate ordering、17 项验收清单（表格）、PR E4+ deferred。 |
| `tests/test_tgt05_module_construction_contract.py`（新，32 tests） | 见 §三。 |
| `manifests/runtime_migration_pr_e3_manifest.yaml`（新） | `chatgpt_review: PENDING`、8 个 scoping_decisions、boundary 声明、artifact 清单。 |

## 三、测试（`tests/test_tgt05_module_construction_contract.py`，32 tests）

- `ContractShapeTests`：version `0.1.0`、`migration.pr == runtime_migration_pr_e3`、
  boundary 含 "no implementation"、`next` 指 PR E4、`order` 正确；
  `template_provenance.status == RECONSTRUCTED` +
  `seventeen_item_template_reused_from_e1`；`kernel_invariant` 含 "src/ must
  never import gate_modules/" + "one-way normal-tissue liability detector" +
  "never a safety predictor"；`acceptance_checklist` 恰好 17 项且键名顺序
  == E1 模板。
- `VerbatimFromPrDTests`：item 01 identity；item 02 `MOD-TGT05` + `0.0.0`；
  **item 03 `text` normalized-equality == PR D TGT-05 `gate_question`**；item 04
  `not_admissible_into_this_gate` 含 TGT-01…08（除 05）；**item 05 三个 rung 的
  `admissible_evidence_classes` + `ceiling_rule` + `evidence_ceiling` 逐字 ==
  PR D**；**item 07 allowed / forbidden 逐字 == PR D**；**item 08
  `potential_fatal_signal` 逐字 == PR D `fatal_conditions`**，rule 含 "never
  performs a candidate-level kill" + "no numeric severity score"，
  `single_product_vs_target_intrinsic_convergence` 与 `convergence_audit_requirements`
  （construct fingerprint / linker / payload / observed severity for this
  product / target-attribution basis / primary source）+ `human_review_reserved`
  （materially distinct / truly target-mediated）。
- `LiabilityDetectorSemanticsTests`：item 06 "not candidate desirability" +
  "does not flip direction" + `NEGATIVE` "essentially unreachable" + "no risk
  seen" + HPA/RNA/IHC-negative "do not produce negative = safe" + `CONFLICTING`
  "not contradictory"；item 09 硬锁四条 + coverage map 六器官 +
  `no_universal_threshold` + `connect_provider_in_this_pr == false` +
  `current_instantiation_regime == PUBLIC_ONLY`；item 15 "never auto-PASS" +
  "not an integrity failure" + "absence of public risk evidence is not a
  safety-negative"；item 16 三条 path（`PUBLIC_FATAL_SIGNAL_ESTABLISHED` /
  construct inventory / vital-organ coverage sweep / `EXPERIMENT_REQUIRED`）；
  item 13 + 17 "no product-specific therapeutic-window conclusion" + "flip
  direction based on candidate desirability" 禁止。
- `InheritsPrE2GenesTests`：item 10 "single authoritative target" + "no
  separate drift-prone target argument"；item 11 "reuses the exact canonical
  package, never copies or re-creates" + "present and equal" + "hard identity
  integrity failure"；item 12 non-canonical envelope、`never_carries`
  assessment_id / review.status / therapeutic-window conclusion、identity pins；
  item 13 on_failure "rejects the whole run" + "unknown from genuinely
  incomplete coverage is not an integrity failure"。
- `NoImplementationInPrE3Tests`：`repository_policy` 8 项 `forbidden` +
  `migration_pending: remains`；`deferred_to_pr_e4_plus` 提及
  `gate_modules/tgt05_normal_tissue_fatal_liability/` / `1.0.0` / runner；
  顶层 `gate_modules/tgt05_normal_tissue_fatal_liability/` **不存在**；
  **TGT-05 gate_binding `primary_module_version` 仍 == `0.0.0`**；
  **MOD-TGT01 binding 仍 == `1.0.0`**（未动）；`gate_modules/` 下只有
  `tgt01_adc_modality_precedent` 的 `.py`（无 generic framework）；
  合同正文正则扫无 numeric cutoff / TPM / FPKM。
- `DrawingTests`：drawing 存在、含 "MOD-TGT05's job is not to prove a target" +
  "one-way liability detector" + "construction contract + drawing only" +
  "normalized-equality parity test"；1–17 每项作为表格行出现；含 "pr e3 does
  not touch it" + "pr e4 also bumps the tgt-05"。

## 四、明确未改 / 未做

- **未写** 任何 Module 实现代码；**未建** `gate_modules/tgt05_*/` 目录；**未接**
  任何 retrieval provider / dataset；**未产** EvidencePackage / Assessment 运行
  输出；**无** numeric scoring / biological threshold / product-specific
  therapeutic-window logic / 新 scientific ladder semantics / generic
  GateModule framework / abstract base class。
- **未改** PR A / B / C 合同；**未改** PR D 的 TGT-05 Gate science（parity 测试
  只读不写）；**未改** MOD-TGT01（binding 仍 `1.0.0`，`gate_modules/tgt01_*/`
  代码未动）；**未改** TGT-05 `primary_module_version`（仍 `0.0.0`，PR E4 才 bump）。
- **未解除** `MIGRATION_PENDING`。无新依赖（仍只 PyYAML）。
- 其余 6 个 TGT primary Module（TGT-08 → 02 → 03 → 04 → 06 → 07）属 PR E4+。

## 五、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 853 tests ... OK   (821 baseline + 32 new)
git diff --check                       # clean
bash scripts/verify_repository_boundary.sh   # 干净 tracked-tree worktree 上 pass
python3 -c "import yaml; yaml.safe_load(open('src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml'))"  # 结构合法
```

## 六、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入；GitHub connector 写 review 仍 `403`）。审核重点：8 个 scoping 决策
  是否落实、item 03/05/07/08 是否真的 normalized-equality parity 冻结 PR D
  TGT-05、liability-detector 语义（Direction / NEGATIVE 不可达 / 负 atlas ≠
  safety / incomplete coverage → UNKNOWN）、fatal 的单产品 vs convergence 分离与
  convergence-audit 字段、asymmetric stop rule、E2 genes 冻结、是否确实无实现 /
  provider / framework、MOD-TGT01 与 TGT-05 binding version 未动。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一对话
  复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #95/#97/#99/#101/#103/#105/#107/#109 先例）。

## 七、后续（PR E4+，未启动）

- **PR E4** —— MOD-TGT05 实现：新建顶层
  `gate_modules/tgt05_normal_tissue_fatal_liability/`（providers / adapters /
  extractor / normalizer / runner / dry-run executor / EvidencePackage writer /
  assessment proposer），单向依赖 `src/`；并把 TGT-05 gate_binding
  `primary_module_version` `0.0.0 → 1.0.0`。仅在本合同 APPROVE 后开工。
- **PR E5+** —— 逐 Gate 施工图 + 实现，按 `TGT-08 → 02 → 03 → 04 → 06 → 07`
  顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
