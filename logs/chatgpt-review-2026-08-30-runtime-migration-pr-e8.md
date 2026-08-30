# ChatGPT 审核记录：Runtime Migration PR E8 —— MOD-TGT02@1.0.0 实现

- 日期：`2026-08-30`
- PR：#120 `task_20260829_runtime-migration-pr-e8`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`3e48626`（第二轮修订）
- Merge 提交：`ca0b4ad`（`Merge pull request #120 from leezx/task_20260829_runtime-migration-pr-e8`）
- 结论：**APPROVE @ `3e48626`**。「APPROVE —— MOD-TGT02@1.0.0 deterministic
  implementation 可以 merge。下一步按既定顺序就是 TGT-03 construction contract /
  PR E9。」GitHub connector 每轮均 `403 Resource not accessible by integration`，
  REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
  为 authoritative。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e8-approval-record`）
中补登，按 PR #95 … #119 先例。本 PR 同时把
`manifests/runtime_migration_pr_e8_manifest.yaml` 补成 approved。不改 PR E8 的
实现、测试或 handoff 内容。

## 9 个 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板，E8-1…E8-8 + (a)(b)(c)）

见 `manifests/runtime_migration_pr_e8_manifest.yaml` 的 `scoping_decisions` 与
`three_headline_invariants`，以及
`docs/handoff/2026-08-30-runtime-migration-pr-e8.zh-CN.md` §一。要点：

- **E8-1** 完整确定性 Gate-specific core（同 E2 / E4 / E6），11 文件；
  `completion.py` 与 `fatal_review.py` 各自独立小文件；`CrcCohortCoverageCompletion`
  是 module-local run record，**非**第七个 core object；最小 binding 更新
  （TGT-02 `0.0.0 → 1.0.0`）；冻结 E7 合同正文一字不改；`run()` 纯 Python 只调
  injected port。
- **E8-2** 一个 `Tgt02CoverageProviderPort`（本包自己声明其它三个 port）；
  `assay_method` 是 typed classification-driving fact，DIRECT 只能经
  `VALIDATED_IHC` / `QUANTITATIVE_PROTEOMICS` / `VALIDATED_MULTIPLEX_IF`；
  `cohort_n` 只是 raw fact；`SEARCH_COMPLETION_AUDIT` 带 11 字段结构化 snapshot。
- **E8-3** 确定性 rung 分类 + hard locks（transcript / generic protein assay /
  protein-without-attribution 永不 DIRECT；`cohort_n` 永不改 rung；matched
  normal-tumor 只 contextualise；stroma/immune CONTEXTUAL 非 HARD）；单个
  observation 永不是 Direction。
- **E8-4** 显式 precedence（HARD → 无 proposal；未 landscape-complete →
  `INCONCLUSIVE/UNKNOWN` 零 refs 合法非错误态；complete 但 audit 坏 → HARD；
  complete + audited → 评估）；overall Strength = **最强 qualifying class**（无
  two-axis rule）；audited multi-cohort `RARE_HIGHLY_HETEROGENEOUS`（>= 2 cohorts）
  → `NEGATIVE` 不 `CONFLICTING`；WEAK-only completed → `INCONCLUSIVE/UNKNOWN`。
- **E8-5** typed `CrcCohortCoverageCompletion` + 3 个 HARD invariant
  （completeness consistency、mandatory audit presence + 11 字段 snapshot
  parity、qualifying cohort-set parity）；`CoverageUnresolvedItem(description,
  kind)` internal type。
- **E8-6** machine-local `fatal_review` review TRIGGER；`required` iff completed
  audited landscape + DIRECT-class protein cohorts 跨 **AT LEAST TWO**
  independent cohort identities（>= 2，明确不是 "> 2" / ">= 3" —— E8-6 草稿正文
  的「> 2」经追问确认是笔误）；`status` 单值 `POTENTIAL_FATAL_PATTERN`；raw
  detector 内部算，actionable 只在 accepted run；machine 永不
  `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / KILL / HOLD / Decision；不在 proposal
  envelope 上。
- **E8-7** Gate-neutral PR A EP + exact canonical reuse（parity keys 含
  `assay_method` + `crc_specific`）；machine acceptance = E7 item-13 可执行检查；
  HARD identity / provenance / completion-consistency / qualification 失败 → 拒
  整个 run，绝不降级 accepted UNKNOWN；`critical_unknowns` 窄确定性映射
  （incomplete → `PUBLIC_RESOLVABLE`；access/annotation blocked →
  `CURRENTLY_UNRESOLVABLE`；IS-only directional 无 qualifying DIRECT →
  `EXPERIMENT_REQUIRED` protein confirmation；WEAK-only complete →
  `INCONCLUSIVE/UNKNOWN` + `EXPERIMENT_REQUIRED`）；Module 绝不构造
  `CandidateGateAssessment` / `HUMAN_APPROVED` / `Decision`。
- **E8-8** CI 只跑 synthetic / in-memory；`TARGET_A` / `CRC_COHORT_A` / `_B` /
  `_C` / `STROMA` / `IMMUNE`；无 HER2 / TROP2 / 真实靶点名。
- **(a)** `completion.py` / `fatal_review.py` 各自独立小文件。
- **(b)** `module.yaml` 必须有，同 E2/E4/E6 型。
- **(c)** E8 允许触碰的既有文件完整清单：`crc_adc_target_gateset.yaml` / `.py`、
  `gate_modules/README.md`、`test_crc_adc_target_gateset.py`、
  `test_gate_modules_boundary.py`、`test_tgt02_module_construction_contract.py`
  （E7 test 迁成 post-E8 reconciliation），以及 `test_tgt05_module*.py` /
  `test_tgt08_module*.py` 里 hard-coded「只三个 built package」的最窄同步。

3 条 headline invariant（审核方原话）：

1. **A single observation is never a Direction.** 只有 `aggregate`，在一个
   completed audited CRC coverage landscape 上，才产 proposed Direction ×
   Strength。
2. **TGT-02 NEGATIVE is a Gate-relative SCIENTIFIC coverage judgement** —— 绝不
   是 fatal flag，绝不是 KILL。cross-cohort protein-level negative-coverage
   pattern 至多 surface 成 machine-local `fatal_review = POTENTIAL_FATAL_PATTERN`。
3. **The typed `CrcCohortCoverageCompletion` grants the Module its authority to
   grade a population-level Direction** —— 一个自相矛盾、无法被审计、或与
   qualifying evidence 不符的 completion 一文不值，拒整个 run。

## 三轮历史（初次提交 + 2 轮修订）

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `86ded60`（首版：11-file 实现包 + binding + 75 tests，全量 1185） | `REQUEST_CHANGES`。**主体架构接受**（11-file standalone、typed assay、highest-qualifying-class aggregation、`>= 2` cross-cohort、binding、`MIGRATION_PENDING`、冻结 E7 truth table、NEGATIVE ≠ fatal ≠ KILL、ladder、TMA never DIRECT）。**7 个 runtime correctness / integrity blocker**。 |
| 2 | `bab4d4a`（第一轮修订，90 tests / 全量 1200） | `REQUEST_CHANGES`。第一轮 7 个 blocker 全部确认关闭。**4 个 narrow integrity / factual-output blocker**。 |
| 3 | `3e48626`（第二轮修订，98 tests / 全量 1208） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 7 个 blocker（`86ded60` → `bab4d4a`）

不改架构、frozen E7 truth table / science、`>= 2` 规则、ladder、
highest-qualifying-class Strength、TMA never DIRECT、binding scope、
`MIGRATION_PENDING`、MOD-TGT01 / 05 / 08。

1. **固定 Instantiation 的 context / scope 没真正绑定。** `Tgt02ModuleInput`
   只查 `CTX-...` 前缀 + `> 0`，没跟冻结 Instantiation（`context_id
   CTX-CRC-REFRACTORY-MCRC` / `context_version 1`）比；observation
   `context_key` / completion `search_scope` 也没跟 input 比。修：input pin
   canonical `context_id` + `context_version`；`module.run()` HARD-check 每条
   observation 的 `context_key` vs run，和（attempted 时）
   `completion.search_scope` vs run 的 `crc_coverage_search_scope`；test
   fixture `CTX_ID` 改成 canonical。+4 regression。
2. **incomplete landscape + 两个 negative cohorts 会被 raw fatal trigger 反向
   变成 rejected run。** 修：`fatal_review.detect()` 接 `completion`，`not
   completion.landscape_complete` → `FatalReviewRecord.none()`。+1 regression。
3. **Gate-neutral EP 对 CONTEXTUAL evidence 写错事实**（对任何
   `PROTEIN_COHORT` 都写「annotated CRC malignant cells」，于是 `NON_MALIGNANT`
   contextual observation 的 EP 反而声称它在 malignant cells）。修：
   `_directly_supports()` 按实际字段陈述；incomplete `SEARCH_COMPLETION_AUDIT`
   EP 报 snapshot factual state；`_NEUTRAL_CEILING` 改中性。+2 regression。
4. **mandatory audit presence 没按冻结 E8-5 invariant 2 实现，且 exact-one 可被
   `(source_id, claim)` dedup 绕过。** 修：`CrcCohortCoverageCompletion` 只要
   `attempted`（complete 与否）就 require `audit_observation_id`；
   `audit_presence_failure` gate 在 `attempted`；`module.run()` 从 normalized
   admissible identity 层（dedup 前）统计 `SEARCH_COMPLETION_AUDIT`。+4 regression。
5. **`cohort_ids` 在没有 `declared_multi_cohort_analysis=True` 时被当成
   cross-cohort**（`cohort_identities` 不查 declared flag）。修：cross-field
   validation（`cohort_ids` non-empty ↔ declared flag，declared 需 `>= 2`
   distinct ids 且无 single `cohort_id`）；`cohort_identities` 只在 declared
   flag true 时读 `cohort_ids`。+3 regression。
6. **EXPERIMENT_REQUIRED 在仍有 public unresolved source 时过早出现**
   （`CURRENTLY_UNRESOLVABLE` 与 `EXPERIMENT_REQUIRED` 可共存）。修：aggregate
   只在 `completion.unresolved_items` 为空时才 auto-add `EXPERIMENT_REQUIRED`。
   +2 regression。
7. **`one_evidence_package_per_observation` acceptance check 查错字段**（只查
   `evidence_id` 不重复）。修：acceptance 加 `observation_id` 唯一性检查；
   `module.run()` 在 normalized-input 层对 duplicate `observation_id` 拒整个
   run。+1 regression。

顺手同步：`src/objects/crc_adc_target_gateset.py` 注释「other five TGT gates」→
「other four」。第一轮修订后 `tests/test_tgt02_module.py` 90 tests，全量 1200。

## 第二轮 REQUEST_CHANGES 的 4 个 blocker（`bab4d4a` → `3e48626`）

第一轮 7 个 blocker 全部确认关闭。4 个 narrow integrity / factual-output 修复。

1. **provenance-bearing audit EP 仍可被 dedup 吃掉。** normalized 层 audit
   exact-one 关闭了「两条 audit dedup 成一条」，但 `build_evidence_packages`
   对所有 kind 共用一个 `(source_id, claim)` dedup，于是一条
   `SEARCH_COMPLETION_AUDIT` 若与 non-audit observation 撞可被 drop —— completion
   仍会 grade 却没有 provenance-bearing audit EP。修：`module.run()` 额外验证
   attempted completion 有**恰好一条** emitted / reused
   `SEARCH_COMPLETION_AUDIT` EvidencePackage 匹配 `audit_observation_id`；被
   dedup drop → HARD reject。+1 regression。
2. **exact canonical reuse 没验证完整 canonical identity / provenance。**
   `_reused_package_is_compatible()` 现在 (a) 把 `observation_id` 加进
   exact-reuse identity parity（reused EP 的 `study_context.observation_id`
   指向别的 observation → HARD），(b) 验证 reused EP 自己的 provenance
   `source_type` / `source_identifier` / `locator` 仍等于 resolved canonical
   SourceIndex（E7 item 13，不只是 `source_id` resolve）；`retrieved_at` 保留
   reused EP 自己的 timestamp。+2 regression。
3. **EXPERIMENT_REQUIRED 的 structured resolution 第一轮已 gate，但 WEAK-only
   分支的 `aggregation_rationale` free text 仍固定写「a new ... measurement is
   required」。** 修：rationale 尾句按 `public_space_exhausted` 分支 —— 仍有
   unresolved public path 时写「the remaining unresolved public evidence path
   must be resolved before determining whether a new measurement is required」。
   +2 regression（查 rationale text）。
4. **Gate-neutral EP 的 `study_context` 对所有 observation 硬编码 CRC tumor
   context**（`indication: refractory_metastatic_colorectal_cancer` /
   `sample_type: crc_tumor_tissue`），对 `SEARCH_COMPLETION_AUDIT` /
   `PAN_CANCER_UNRESOLVED` / `MATCHED_NORMAL_TUMOR` / non-CRC contextual
   observation 是事实错误。修：新 `_study_context_facts(o)` 按 kind / fact 给
   non-inflated `(indication, sample_type)`；Module 绝不把 source study 提升成
   「refractory metastatic CRC」（run context 已由 `context_key` / Instantiation
   单独 pin）；普通 CRC observation 只写到 `colorectal_cancer`。+3 regression。

顺手同步 PR #120 body 的 test 数（75 / 1185 → 98 / 1208）。第二轮修订后
`tests/test_tgt02_module.py` 98 tests，全量 1208。

## 第三轮 APPROVE（`3e48626`）

审核方逐条复核（exact-HEAD `3e48626e…` CI `verify (3.11)` / `verify (3.12)` 均
`completed / success`，含 unit tests / repository boundary / no-bytecode /
working-tree-clean）：

- 第二轮 4 个 blocker 均已实质关闭：
  - **provenance-bearing audit EP dedup bypass 已关闭** —— 现在同时要求
    normalized 层 exactly one matching audit 和 emitted / reused surface 上
    exactly one matching `SEARCH_COMPLETION_AUDIT` EP；唯一 audit 被 dedup 吃掉
    → HARD integrity failure，不能再凭 completion booleans 获得 grading
    authority。
  - **canonical EP reuse identity / provenance parity 已关闭** ——
    `observation_id` 已加入 exact-reuse parity；reused EP 自身的 `source_type` /
    `source_identifier` / `locator` 也必须重新匹配 resolved canonical
    SourceIndex；`retrieved_at` 保留 canonical EP 自己的历史时间。
  - **EXPERIMENT_REQUIRED free-text premature assertion 已关闭** —— 仍有 public
    resolution path 时 rationale 只说先 resolve remaining public evidence，再判
    是否需要新 measurement；只有 source space 真正耗尽时才说 new measurement
    required。
  - **Gate-neutral EP study_context inflation 已关闭** —— 新
    `_study_context_facts()` 不再把所有 observation 强行标成 refractory mCRC
    tumor tissue；普通 CRC evidence 也只写到 `colorectal_cancer`。
- 本轮修订非常窄：相对 `bab4d4a` 只改了 `aggregate.py` / `evidence.py` /
  `module.py`、tests 和 governance 记录，没动 E7 contract / drawing / binding
  science 或其他 Module。**没有 scope creep**。

**APPROVE —— MOD-TGT02@1.0.0 deterministic implementation 可以 merge。** 下一步
按既定顺序是 TGT-03 construction contract / PR E9（需各自 go-ahead）。

CI（GitHub Actions `verify`，python 3.11 + 3.12）对 `86ded60` / `bab4d4a` /
`3e48626` 均 `success`。全量 `unittest discover`：首版 1185 → 第一轮修订后 1200
（+15 `Round1RegressionTests`）→ 第二轮修订后 1208（+8 `Round2RegressionTests`）。

GitHub connector 每轮都返回 `403 Resource not accessible by integration`，
REQUEST_CHANGES / APPROVE 的 GitHub review state 未写回；`AI审核方案` 对话结论
为 authoritative。

## 状态

8 个 primary Module 已实现 4 个：MOD-TGT01@1.0.0（E2）、MOD-TGT05@1.0.0（E4）、
MOD-TGT08@1.0.0（E6）、MOD-TGT02@1.0.0（E8）。其余四个 gate（TGT-03 → TGT-04 →
TGT-06 → TGT-07）属后续 PR，`primary_module_version` 仍 `0.0.0`。
`MIGRATION_PENDING` 保持。真实 retrieval provider / adapter / dataset 与外部
workspace calibration 各自需 go-ahead。下一步 PR E9 = MOD-TGT03 施工合同
（design-only，需各自 go-ahead）。
