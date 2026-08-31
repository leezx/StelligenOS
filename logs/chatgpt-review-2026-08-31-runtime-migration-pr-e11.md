# ChatGPT 审核记录：Runtime Migration PR E11 —— MOD-TGT04 施工合同（design-only）

- 日期：`2026-08-31`
- PR：#126 `task_20260831_runtime-migration-pr-e11`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`1ad620d`（第二轮修订后）
- Merge 提交：`499cf3a`（`Merge pull request #126 from leezx/task_20260831_runtime-migration-pr-e11`）
- 结论：**APPROVE @ `1ad620d`**。「PR #126 @ `1ad620d` 可以 merge，E11
  construction contract 可以正式冻结。下一步进入 PR E12 = MOD-TGT04@1.0.0
  deterministic implementation。」GitHub connector 每轮均 `403 Resource not
  accessible by integration`，REQUEST_CHANGES / APPROVE 的 GitHub review state
  未回写；`AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260831_runtime-migration-pr-e11-approval-record`）
中补登，按 PR #95 … #125 先例。本 PR 同时把
`manifests/runtime_migration_pr_e11_manifest.yaml` 补成 approved。不改 PR E11 的
合同、drawing、测试或 handoff 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e11_manifest.yaml` 的 `scoping_decisions`
（E11-1…E11-8）、`four_key_scoping_corrections` 与 `three_headline_conclusions`，
以及 `docs/handoff/2026-08-31-runtime-migration-pr-e11.zh-CN.md`。要点：

- E11 是 **CONSTRUCTION_CONTRACT_ADD**，与 E1 / E3 / E5 / E7 / E9 同型：只交付
  `src/contracts/gate_modules/tgt04_tumor_surface_availability_density_plausibility.yaml`
  的 17 项施工合同 + 人类可读 drawing + parity / validation 测试 + manifest /
  handoff / worklog append。**不交付任何实现**：无 `gate_modules/tgt04.../`
  runtime、无 provider / adapter / retrieval / runner、无 EvidencePackage /
  proposal / fatal-detector runtime、无 numeric / ranking score、无 antigen-density
  cutoff / molecules-per-cell / ABC / percent-positive / H-score threshold、无
  invented "clinically effective antigen-density range"、无 generic GateModule
  框架 / ABC。`MOD-TGT04` `primary_module_version` 仍 `0.0.0`（PR E12 才 bump 到
  `1.0.0`）；binding / registry / README / built-roster test 一律不动；唯一既有
  文件改动是 `logs/worklog.md` append。`MIGRATION_PENDING` 保持（八个 primary
  Module 全部建成前不解除；剩余顺序 TGT-04 → TGT-06 → TGT-07）。
- 3 条 headline conclusion（逐字冻结在合同）：surface localization is not antigen
  density（只有 quantitative DIRECT 证据能回答 TGT-04 density-plausibility 问题）；
  quantitative values are evidence, not thresholds（可保留测得的 antigen-density
  数值 / 单位，但永不推导 universal ADC-effective density cutoff；density
  plausibility 必须以 auditable upstream qualification 到达）；reproducible
  quantitative `NEGLIGIBLE_OR_UNDETECTABLE` surface antigen 至多 surface
  `POTENTIAL_FATAL_PATTERN`（low-but-present 永不自动 negative / fatal，Module
  永不裁决 fatality 或 ADC efficacy）。
- 4 个 key scoping correction（审核方逐字，前两条最重要）：
  1. **localization-only → `INCONCLUSIVE / UNKNOWN`，不是 `INCONCLUSIVE /
     INDIRECT_STRONG`** —— TGT-04 是 TWO-TIER evidence architecture（LOCALIZATION
     tier：INDIRECT_STRONG membranous IHC / surfaceomics；DENSITY tier：DIRECT
     quantitative antigen density）+ SINGLE-TIER grading authority。只有
     qualifying DIRECT quantitative antigen-density 观察（在 completed audited
     landscape 上）才授予 graded Direction；INDIRECT_STRONG 永不传播成 Gate-level
     proposed Strength。E12 不得复制 E10 式「highest qualifying rung == overall
     Strength」。legal Direction × Strength pair 恰好 5 个：`POSITIVE/DIRECT`、
     `NEGATIVE/DIRECT`、`CONFLICTING/DIRECT`、`INCONCLUSIVE/DIRECT`、
     `INCONCLUSIVE/UNKNOWN`。
  2. **不 overload 单个 status 同时承载 measurement validity 与 density
     direction** —— 三个分离 typed field：`measurement_validation_status`
     `{QUALIFIED, NOT_ESTABLISHED}`（这个 quantitative measurement 是否有资格进
     DIRECT —— QUALIFIED 不是 positive density conclusion）；
     `density_plausibility_status` `{PLAUSIBLY_ADEQUATE, NOT_PLAUSIBLY_ADEQUATE,
     MIXED_OR_UNRESOLVED, NOT_ESTABLISHED}`（upstream-qualified 科学解释，basis
     `{SOURCE_REPORTED, HUMAN_REVIEWED_NORMALIZATION}`，永不由 Module 从数字算）；
     `surface_antigen_level` `{QUANTITATIVELY_PRESENT, LOW_BUT_PRESENT,
     NEGLIGIBLE_OR_UNDETECTABLE, MIXED_OR_UNRESOLVED, NOT_ESTABLISHED}`（为 fatal
     path 单独冻结，`LOW_BUT_PRESENT` 永不被静默等同于 `NOT_PLAUSIBLY_ADEQUATE`）。
  3. **raw quantitative density value / unit 是 admissible factual evidence**
     （`reported_density_value` / `reported_density_unit` /
     `reported_density_summary`）—— 禁止的是 Module 拿它与任何 threshold / cutoff /
     invented "clinically effective range" 比较。
  4. **fatal Route A / Route B 镜像 TGT-03**；local identity 名
     `surface_context_id(s)`；Route B = convergent `NEGLIGIBLE_OR_UNDETECTABLE`
     跨 `>= 2` independent qualified surface-context identity —— deterministic
     SUFFICIENT convergence pattern，非 "reproducible" 词义，非 `> 2`。
- items 03/05/07/08 对冻结的 PR D TGT-04 合同做 normalized-equality parity；item
  04 做 EXACT set-equality derived parity（`evidence_required` ∪ ladder
  admissible classes）；EVGAP-01 `inference_guard` 逐字 pin。items 10-17 继承
  E2/E4/E6/E8/E10 runtime gene，含五个 E10-review correction。improved TGT-03
  dedup。

## 审核往返（3 轮）

### Round 1 —— REQUEST_CHANGES @ `41be84a`

审核方确认主体合同成立（design-only boundary；PR D items 03/05/07/08 parity +
item 04 exact-set parity；localization-only → INCONCLUSIVE/UNKNOWN；5 个 legal
Direction×Strength pair；三套 density typed fact；raw-value/no-threshold；Route
A/B；four-component completion；narrow EXPERIMENT_REQUIRED）。**4 个窄
construction-contract blocker**：

1. **INDIRECT_STRONG 的 context authority 被错误扩到 `WELL_MATCHED_CRC_MODEL`**。
   Frozen PR D：DIRECT = quantitative density on CRC malignant cells **OR**
   well-matched CRC models；INDIRECT_STRONG = membranous IHC / surface proteomics
   on CRC malignant cells **only** —— model 许可只在 DIRECT。修复：拆开 item-13
   predicate —— DIRECT 允许 `{CRC_MALIGNANT_CELLS, WELL_MATCHED_CRC_MODEL}`；
   INDIRECT_STRONG rung 要求 `surface_context_class == CRC_MALIGNANT_CELLS`（+
   `malignant_cell_attribution` + auditable basis）；well-matched model
   localization 观察是 CONTEXTUAL reading，永不成 INDIRECT_STRONG rung。新增
   item-06 `rung_context_authority`。
2. **fatal machine criteria 也把 well-matched CRC model 错误扩进去了**（审核方
   同时修正了自己开工前 E11-4/E11-6 ruling 里一处过宽表述）。Frozen PR D fatal
   句更窄：*"negligible or undetectable cell-surface antigen on CRC malignant
   cells"*。修复：fatal_review contributor 只能是 **CRC-malignant-cell**
   quantitative 观察（`surface_context_class == CRC_MALIGNANT_CELLS`）；
   well-matched CRC model NEGLIGIBLE 观察可贡献普通 DIRECT OPPOSES Direction 但
   永不是 fatal contributor；Route B convergence 要求跨 `>= 2` independent
   qualified CRC **malignant-cell** surface-context identity。（items
   08/12/13/on_failure）
3. **qualifying INDIRECT_STRONG localization 的 local-context / completion
   authority 被漏掉**。E11 scoping 已冻结：任何 qualifying DIRECT **或**
   INDIRECT_STRONG 观察都要带 auditable local `surface_context_id`。修复：item 13
   对两者都要求 local id；`SurfaceAvailabilityCompletion` 恢复
   `qualifying_indirect_surface_context_ids`（与 `qualifying_direct_...` 并列）；
   SEARCH_COMPLETION_AUDIT snapshot parity 同时锁两组；新增 item-06
   `qualifying_local_surface_context_identity`。该 indirect set 只是 evidence /
   audit-integrity，**不是 grading axis**：localization-only + valid indirect set
   仍然 INCONCLUSIVE/UNKNOWN（item 15）。
4. **raw quantitative density 是 canonical empirical fact，但 exact canonical EP
   reuse parity 未覆盖它**。修复：对 `QUANTITATIVE_SURFACE_DENSITY` 观察，raw
   `reported_density_value` / `reported_density_unit` /
   `reported_density_summary` 是 present 时的 FACTUAL EXACT-REUSE PARITY 字段 ——
   reuse 时 drift 即 HARD identity integrity failure（empirical-identity parity，
   非 classification authority；raw 值仍永不驱动 Direction / fatal signal /
   threshold 比较）。（items 11/13/on_failure）

审核方明确「不要改」：5 个 legal pair；localization-only → INCONCLUSIVE/UNKNOWN；
INDIRECT_STRONG 永不传播 Strength；DIRECT assay vocabulary OPEN；
`measurement_validation_status` CLOSED；raw 值允许 / threshold 禁止；
`LOW_BUT_PRESENT` ≠ 自动 NEGATIVE/fatal；Route A OR Route B；Route B `>= 2` 非
`> 2`；NEGATIVE ≠ fatal ≠ KILL；four search component = completeness only；
EXPERIMENT_REQUIRED precedence；design-only；MOD-TGT04 仍 0.0.0；MIGRATION_PENDING
保持。

修订：合同 items 06/08/09/11/13/15；drawing rows 6/8/9/11/12/13/15 + conceptual
shape；`tests/test_tgt04_module_construction_contract.py` 58 → 67（新增
`ReviewRound1RegressionTests` + 6 处断言随合同措辞更新）；manifest
`review_rounds: 1` + `review_round_1` block；worklog append。全量 1437 → 1446。
提交 `e510833`。

### Round 2 —— REQUEST_CHANGES @ `e510833`

审核方判定 round-1 的 4 个 blocker **全部 CLOSED**，仅剩 2 个非常窄的 residual
contract inconsistency（只改 contract/drawing/test/manifest/worklog，无新
scientific decision，不动架构；审核方预期修完下一轮 APPROVE）：

1. **item-06 `direction_definitions` 对 well-matched CRC model 前后不一致**：
   `POSITIVE` 写 "CRC malignant cells (or a qualified well-matched CRC
   malignant-cell model)"，但 `NEGATIVE` 只写 "CRC malignant cells"，而
   `density_direction_mapping` 把 model + NEGLIGIBLE 映射为 OPPOSES。给 E12 两套
   冲突 contract。修复：`NEGATIVE` 同样加 "(or a qualified well-matched CRC
   malignant-cell model)"；新增
   `well_matched_model_ordinary_direction_boundary` —— ordinary graded Direction
   （POSITIVE/NEGATIVE/CONFLICTING/INCONCLUSIVE，均 Strength DIRECT）可由
   `CRC_MALIGNANT_CELLS` **或** `WELL_MATCHED_CRC_MODEL` 上的 qualifying DIRECT
   观察支撑（镜像 frozen DIRECT ladder，POSITIVE/NEGATIVE 对称）；well-matched
   model 支撑的 `NEGATIVE / DIRECT` 只是 ordinary density assessment，model
   evidence **永不**进 fatal_review —— fatal authority 仍 CRC malignant-cell
   only。不扩 fatal 权。
2. **raw `reported_density_*` exact-reuse parity 仍是单向**（"no drift WHEN
   PRESENT on the canonical package"），没挡反方向的 presence asymmetry
   （canonical absent / current present，或 canonical unit absent / current unit
   present）。修复：冻结为 **对称 presence-and-value parity** —— present on one
   side only（任一方向），或 value / unit 不同，即 HARD identity integrity
   failure；两侧都有且相等、或两侧都无，才 compatible。仍：raw 值 ≠
   classification authority ≠ threshold ≠ score。（items 11/13/on_failure +
   drawing rows 11/13 + conceptual shape）

非阻断 housekeeping：PR #126 body 测试数从 58/1437 同步到 71/1450，并加 ChatGPT
review round 1 / round 2 状态。

修订：合同 item 06 `direction_definitions` + items 11/13 raw-density parity +
`on_failure`；drawing rows 6/11/13 + conceptual shape；测试 67 → 71（新增
`ReviewRound2RegressionTests` + 2 处 round-1 断言随对称化更新）；manifest
`review_rounds: 2` + `review_round_2` block；worklog append。全量 1446 → 1450。
提交 `1ad620d`。

### Round 3 —— APPROVE @ `1ad620d`

审核方确认 PR 仍 open / mergeable、HEAD 与请求一致、PR body 已同步到 71 个 TGT-04
construction-contract test / 1450 full-suite test、exact-head CI run
`33400505274` 为 success。round-2 的 2 个 residual blocker 均已关闭：
`POSITIVE / NEGATIVE` 对 `WELL_MATCHED_CRC_MODEL` 的 ordinary DIRECT authority
现在对称，且 model-supported `NEGATIVE / DIRECT` 只是 ordinary density
assessment、永不进 fatal_review、fatal authority 仍严格限定 CRC malignant-cell
evidence；`reported_density_value / unit / summary` 的 canonical reuse 已冻结为
真正的 symmetric presence-and-value parity（任一侧单独存在、值不同或 unit 不同
均 HARD；两侧相同或两侧都缺失才 compatible），它仍只是 empirical identity，不
参与 Direction / fatal / threshold / scoring。对应 regression 也锁住了 ordinary
model Direction / fatal boundary 与 raw-density presence / value 双向 parity。

三轮状态：Round 1 —— 4 blockers → CLOSED；Round 2 —— 2 residual consistency
blockers → CLOSED；Round 3 —— 无新 blocker。5 个 legal Direction×Strength pair
不变；MOD-TGT04 仍 0.0.0；`MIGRATION_PENDING` 保持。

**结论：APPROVE —— PR E11 可以 merge。下一步进入 PR E12 = MOD-TGT04@1.0.0
deterministic implementation。**

## Merge

- PR #126 于 `2026-08-31` 以 `--merge` 合入 `main`，merge 提交 `499cf3a`。
- 8 个 primary Module 施工合同已 APPROVE 6 个（TGT-01/02/03/04/05/08）；已实现
  5 个（TGT-01/02/03/05/08 @ 1.0.0）。MOD-TGT04 `primary_module_version` 仍
  `0.0.0`，PR E12 才 bump。`MIGRATION_PENDING` 保持。TGT-06 → TGT-07 属后续 PR。
