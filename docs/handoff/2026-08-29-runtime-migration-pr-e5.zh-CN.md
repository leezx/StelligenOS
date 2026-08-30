# Handoff：Runtime Migration PR E5 —— TGT-08 / MOD-TGT08 Construction Contract

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e5`
- 分支：`task_20260829_runtime-migration-pr-e5`
- 基线：`origin/main`（PR #112 merge + PR #113 approval record 之后，PR E4 收口）
- PR：待创建
- 时间：`2026-08-29`
- 授权：用户在 PR E4 APPROVE + approval record merge 之后说 "go on"。开工前审核方
  （ChatGPT `AI审核方案`）拍板 **PR E5 = TGT-08 / MOD-TGT08 Construction Contract
  （design-only）**，E5 审核通过后才是 **PR E6 = MOD-TGT08@1.0.0 deterministic
  implementation**，并给了 8 个 scoping 决策 E5-1…E5-8 + 一个 24 条测试清单 + 边界
  一句话。
- 变更定位：`RUNTIME_CONTRACT_ADD`（第五层：TGT-08 primary Evidence Production
  Module 的**施工合同 + 施工图 + 17 项验收清单 + parity/validation 测试**。不写
  实现、不接 provider、不做 trial/patent retrieval、不产 EvidencePackage /
  Assessment、不做 FTO / sponsor decision runtime、不改冻结文档、不新增依赖、不改
  已建的 MOD-TGT01 / MOD-TGT05、不改 TGT-08 `primary_module_version`、不解除
  `MIGRATION_PENDING`）。

## 一、8 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

| # | 决策 |
|---|---|
| E5-1 | 完整施工合同，不写实现。文件 `src/contracts/gate_modules/tgt08_target_opportunity_competition_ip_whitespace.yaml` + `docs/gate_modules/TGT-08_Target_Opportunity_Competition_IP_Whitespace.md` + `tests/test_tgt08_module_construction_contract.py` + manifest/handoff/worklog。禁止 `gate_modules/tgt08.../` / provider / adapter / trial·patent retrieval / runtime classifier / EvidencePackage generation / proposal runtime / sponsor decision runtime / FTO engine / numeric·ranking score / 新依赖 / 外部数据。MOD-TGT08 `primary_module_version` 仍 `0.0.0`；MOD-TGT01 = `1.0.0`；MOD-TGT05 = `1.0.0`；`MIGRATION_PENDING` 保持。 |
| E5-2 | **最关键边界：TGT-08 ≠ scientific de-risking，也 ≠ sponsor decision。** 三层分离：Scientific Gates TGT-01…07（target biology / ADC feasibility / liability）→ TGT-08（external opportunity landscape —— competition / target-specific differentiation / IP-whitespace **SIGNALS**）→ Sponsor axis（v5 §7 —— `OUT_OF_MANDATE` / `STOP_FOR_SPONSOR` 都不是 `KILL`）。TGT-08 **可以**输出 canonical `NEGATIVE` Assessment；该 `NEGATIVE` 只表示「current public opportunity evidence weighs against a differentiated entry for this target in refractory mCRC」——**不是** scientifically bad target / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE / FTO blocked / no viable molecule。TGT-08 `POSITIVE` ≠ TGT-01…07 de-risked。Sponsor capability / cash runway / risk appetite / company mandate 不允许进入 Module Direction。 |
| E5-3 | 17 项模板原样继承 E1（已被 E2 / E4 实际验证）；items **03 / 05 / 07 / 08** 与冻结 PR D `crc_adc_target_gateset.yaml:TGT-08` 做 **normalized-equality parity**；item **04** 对 `evidence_required` + ladder `admissible_evidence_classes` 做 derived parity，防止偷增 commercial evidence class。 |
| E5-4 | **Direction × Strength：TGT-08 的 `NEGATIVE` 必须真正可达**（与 TGT-05 相反）。Module 把 atomic fact 归入 `SUPPORTS_OPPORTUNITY` / `OPPOSES_OPPORTUNITY` / `CONTEXTUAL`；provider 只给事实。frozen truth table（completed axis 上）：只有 material supporting → `POSITIVE`；只有 material opposing → `NEGATIVE`；两者都有 → `CONFLICTING`；两轴都完成 → `DIRECT`，否则 `INDIRECT_STRONG`。indication-level unmet-need-only → `INCONCLUSIVE / WEAK`（永不「grim indication → good opportunity」），且不参与 target-specific `CONFLICTING`。materially incomplete landscape → `INCONCLUSIVE / UNKNOWN`；永不 `UNKNOWN` → attractive / uncrowded / whitespace；永不 favorable commercial picture → TGT-01…07 de-risked。 |
| E5-5 | **DIRECT 是「两轴完成的 evidence bundle」，不是单条 EvidencePackage。** A. Competitive / clinical landscape 轴 COMPLETE（PUBLIC_PRIMARY authority —— trial registries / regulatory filings / company primary disclosures / primary clinical publications；必须覆盖 approved / registrational / active / discontinued-failed programs、same-target ADC 与 non-ADC targeted programs、refractory-mCRC relevance；pipeline DB 是 index → 至多 `INDIRECT_STRONG`）**AND** B. Composition-level patent 轴 COMPLETE（真实 patent publications / families / legal-status records；relevant composition claim families / assignees / status / declared jurisdiction / claim-category mapping / congestion-whitespace signals；target-level（非 composition-level）patent search 至多 `INDIRECT_STRONG`；Lens / PATENTSCOPE / Google Patents / EPO 是 discovery / metadata 工具，claim fact 的 canonical provenance 是 actual patent publication / official status source —— index 不是 evidence authority，与 TGT-01 的 ADCdb 规则相同；composition-level patent landscape **不是** FTO judgement）。**新 invariant：absence inference 需要 completion provenance** —— 「no competitor / no patent → whitespace」只有在 complete audited search 返回 no qualifying competitor 时才成立，永不 `records == []`；未来 E6 携带 module-local typed `CompetitiveLandscapeCompletion` / `PatentLandscapeCompletion`，pin `as_of` date / search scope / sources searched / context / unresolved items / completion status —— run-level machine records，**不是第七个 core object**。 |
| E5-6 | **fatal 不是 scientific fatal：冻结独立的 module-local `sponsor_review` 记录**（与 TGT-05 的 `fatal_review` 不同名、不同路由）。`status` 单值 `POTENTIAL_SPONSOR_FATAL_PATTERN`；字段 `required` / `status` / `evidence_ids` / `competitor_program_ids` / `patent_family_ids` / `landscape_as_of` / `patent_scope`；**不是** EvidencePackage / CandidateGateAssessment / Decision / Gate fatal flag / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE。machine 至多检测 candidate pattern（same target + ADC + same mCRC context + approved OR registrational + primary-source verified + composition-level patent congestion present）→ `required = true`。machine 永不断言 "dominant" / "well protected" / "no differentiation path" / "this sponsor should stop" —— 全部 human / sponsor-governance reserved；「no differentiation path」不能由 MOD-TGT08 推出（未来差异化可能来自 novel epitope / different antibody / conditional binding / linker-payload / DAR / bystander / patient selection / combination / regimen）。`sponsor_review` 记录路由到 external sponsor governance（`SearchSpaceAdmission` / `ProgramCommitmentReview`）on the sponsor-relative axis，绝不走 scientific `fatal_gate_policy`。 |
| E5-7 | **stop rule：两轴 completeness + freshness；不是「搜到一个 competitor 就停」。** item 10 pin `landscape_as_of` / `retrieval_window` / mCRC context / canonical target identity / patent search scope-jurisdictions，无 implicit default。competitive-landscape 轴与 composition-level patent 轴都必须达到 coverage completeness；coverage complete ≠ DIRECT quality（complete pipeline-DB inventory + complete target-level patent search 是 coverage-complete 但只有 `INDIRECT_STRONG` authority → 仍可产 `POSITIVE` / `NEGATIVE` / `CONFLICTING`，不是 `UNKNOWN`）；某一轴没搜 → `INCONCLUSIVE / UNKNOWN`。DIRECT 要求两轴都完成。sponsor-review provisional stop：发现 approved / registrational same-target mCRC ADC + strong composition-level congestion pattern → 置 `sponsor_review`、暂停追更弱证据、handoff —— **但**两个 core 轴的 completeness 仍必须满足。normal stop：evidence ceiling reached / additional public evidence 不能改 Direction-Strength / enumerated public source space exhausted / `sponsor_review` handoff triggered after core completion。TGT-08 **不用** `EXPERIMENT_REQUIRED` —— FTO 不是实验问题；gap 是 `PUBLIC_RESOLVABLE` / `CURRENTLY_UNRESOLVABLE` / external legal-sponsor review required。 |
| E5-8 | items 10–17 直接继承 E2 / E4 runtime genes —— Item 10 canonical target identity（single authoritative、no separate drift-prone arg）+ Instantiation identity / refractory mCRC context / PUBLIC_ONLY / run_id / `landscape_as_of` / retrieval-search scope / existing evidence refs，无 implicit context；Item 11 atomic Gate-neutral immutable-by-ID EvidencePackage + full provenance + exact canonical reuse（competition EP 陈述 program fact，patent EP 陈述 claim / status fact，永不 Gate-relative conclusion）；Item 12 non-canonical proposal envelope（无 assessment_id / assessment_version / review），`sponsor_review` 独立；Item 13 machine acceptance（source / EP refs 可解析、无 duplicate source-claim、frozen ladder classes only、Strength ≤ ceiling、two-axis completeness、absence-based whitespace claim 有 completion provenance、无 FTO wording / conclusion、无 TGT-01…07 scientific inference、无 sponsor Decision / KILL；hard identity-provenance inconsistency → machine reject / proposal = None；real landscape incomplete → `INCONCLUSIVE / UNKNOWN`，不是 integrity failure）；Item 14 human review（competitor context matching / registrational-status interpretation / strategic materiality / patent-family relevance / aggregation reasonableness，sponsor-only dominant / well-protected / differentiation-path / proceed）；Item 15（incomplete → UNKNOWN、WEAK unmet need → INCONCLUSIVE / WEAK、target-specific pos+neg → CONFLICTING、dense claims may support NEGATIVE、NEGATIVE ≠ KILL）；Item 16 = E5-7 two-axis stop rule；Item 17 两路（human-approved CandidateGateAssessment → MatrixView / ADC_TARGET_GATESET ordinary consumption；module-local `sponsor_review` → external sponsor governance）；禁止 `sponsor_review` → canonical scientific fatal → KILL。 |

一句话（审核方原话，放在施工图醒目位置）：
- **TGT-08 evaluates the external opportunity landscape; it does not evaluate the
  target's scientific validity and it does not decide whether this sponsor
  should proceed.**
- **IP whitespace is an evidence-backed landscape signal. It is not freedom to
  operate.**

## 二、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/gate_modules/tgt08_target_opportunity_competition_ip_whitespace.yaml`（新） | 机器施工合同：`version 0.1.0`；`migration`（pr `runtime_migration_pr_e5`、`next` PR E6、`order` `TGT-01 -> TGT-05 -> TGT-08 -> TGT-02 -> ...`）；`template_provenance`（`RECONSTRUCTED` + E1 模板复用 + `not_claimed_verbatim_from_blueprint`）；`kernel_invariant`（单向依赖 + "does not evaluate the target's scientific validity" + "does not decide whether this sponsor should proceed" + "IP whitespace ... is not freedom to operate"）；`acceptance_checklist` **17 项**（键名顺序与 E1 完全一致），其中 03/05/07/08 逐字继承 PR D TGT-08，04 derived parity；06 frozen truth table（`NEGATIVE / DIRECT`、`NEGATIVE / INDIRECT_STRONG` 明确可达）；09 two_axes（competitive + composition-level patent）+ `absence_inference_needs_completion_provenance` + `not_fto` + `no_universal_threshold`；12 `sponsor_review` sub-block（`POTENTIAL_SPONSOR_FATAL_PATTERN`、`machine_never_emits` KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE）；13 machine acceptance（two-axis completeness、absence claim completion provenance、no FTO wording、no TGT-01…07 inference、no sponsor Decision）；15 `negative_is_not_a_kill` + `resolution_kinds`（不含 EXPERIMENT_REQUIRED）；16 two-axis stop rule；17 两路 handoff。`deferred_to_pr_e6_plus`；`repository_policy`（implementation / provider / trial_or_patent_retrieval / numeric_or_ranking_scoring / freedom_to_operate_or_legal_logic / sponsor_decision_runtime / generic_gatemodule_framework / modifies_mod_tgt01 / modifies_mod_tgt05 全部 `forbidden`，`migration_pending: remains`）。 |
| `docs/gate_modules/TGT-08_Target_Opportunity_Competition_IP_Whitespace.md`（新） | 人读施工图：本文件是什么、三层分离表、`NEGATIVE` 可达且 bounded、template provenance（复用 E1 + parity）、gate ordering、17 项验收清单（表格）、PR E6+ deferred。 |
| `tests/test_tgt08_module_construction_contract.py`（新，45 tests） | 见 §三。 |
| `manifests/runtime_migration_pr_e5_manifest.yaml`（新） | `chatgpt_review: PENDING`、8 个 `scoping_decisions`、boundary 声明、artifact 清单。 |

## 三、测试（`tests/test_tgt08_module_construction_contract.py`，45 tests）

- `ContractShapeTests`：version `0.1.0`、`migration.pr == runtime_migration_pr_e5`、
  boundary 含 "no implementation"、`next` 指 PR E6、`order` 正确；
  `template_provenance` 复用 E1；`kernel_invariant` 含三层边界 + "IP whitespace
  ... is not freedom to operate"；`acceptance_checklist` 恰好 17 项且键名顺序
  == E1 模板。
- `IdentityTests`：item 01 `TGT-08@1.0` / `ADC_TARGET_GATESET@1.0` / L04 /
  `INST-CRC-REFRACTORY-ADC-TARGET-v1`；item 02 `MOD-TGT08` + `0.0.0`。
- `VerbatimFromPrDTests`：**item 03 `text` normalized-equality == PR D
  `gate_question`**；**item 05 三个 rung 的 `admissible_evidence_classes` +
  `ceiling_rule` + `evidence_ceiling` 逐字 == PR D**；**item 07 allowed /
  forbidden 逐字 == PR D**；**item 08 `potential_fatal_signal` 逐字 == PR D
  `fatal_conditions`**；**item 04 `evidence_required_from_pr_d` == PR D
  `evidence_required`，`admissible` == ladder 三 rung 的 union**；item 04
  `not_admissible` 含 TGT-01…07；PR D `unknown_behavior` ==
  "Incomplete landscape -> UNKNOWN."。
- `CommercialStrategicBoundaryTests`：`NEGATIVE` reachable & bounded（framing +
  truth table `NEGATIVE / DIRECT`、`NEGATIVE / INDIRECT_STRONG`）；`NEGATIVE` 不是
  KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE 且不 de-risk / re-risk TGT-01…07；
  favorable commercial picture 不能 de-risk 科学（forbidden inference +
  truth table `never`）；FTO / "no design-around" / "no differentiation path"
  显式 forbidden（item 07 + item 09 `not_fto`）；sponsor 变量排除在 Direction
  之外（item 06 + item 04 `not_admissible`）。
- `TwoAxisEvidenceBundleTests`：DIRECT 要求 competitive + composition-level
  patent 两轴（item 16 + item 13）；pipeline-DB alone / target-level patent
  search alone 至多 `INDIRECT_STRONG`；unmet need alone = `INCONCLUSIVE / WEAK`；
  incomplete landscape = `UNKNOWN`（half landscape 不能出判断）；
  absence inference 需 completion provenance（`records == []` 不行、"no patent
  found" ≠ "patent whitespace"、not a seventh core object、item 13 强制、
  on_failure 含 "an absence claim with no completion provenance"）；
  index 不是 evidence authority（same rule as ADCdb in TGT-01）。
- `SponsorReviewTests`：`sponsor_review` machine-local only 且与 `fatal_review`
  不同（`what_it_is` + `machine_may_emit == POTENTIAL_SPONSOR_FATAL_PATTERN` +
  `machine_never_emits` 含 kill / stop_for_sponsor / out_of_mandate / canonical
  fatal flag）；machine 不能断言 dominant / well-protected / no differentiation
  path / this sponsor should stop（item 08 `machine_never_asserts`）；
  `sponsor_review` 不变成 canonical KILL（item 17 `this_module_does_not` +
  routed to external sponsor governance / sponsor-relative axis）；
  `sponsor_review` 不进 proposal envelope。
- `InheritsRuntimeGenesTests`：item 10 single authoritative target + no
  separate drift-prone arg + `landscape_as_of` +「a landscape with no as_of
  date is not admissible」；item 11 Gate-neutral + exact canonical reuse +
  present and equal + hard identity integrity failure + "no TGT-08 opportunity
  conclusion stamped onto it"；item 12 non-canonical envelope 省
  assessment_id / assessment_version / review、identity pins 齐；item 13
  on_failure "rejects the whole run" + "never degraded to an accepted UNKNOWN"
  + "UNKNOWN from a genuinely incomplete landscape is not an integrity failure"；
  no `EXPERIMENT_REQUIRED` for FTO（item 15 + item 16）。
- `NoImplementationInPrE5Tests`：`repository_policy` 全 `forbidden` +
  `migration_pending: remains`；`deferred_to_pr_e6_plus` 提及
  `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/` / `1.0.0` /
  `sponsor_review detector`；顶层 `gate_modules/tgt08.../` 若存在则 `module.yaml`
  必须 `built_in: runtime_migration_pr_e6`（同 E1→E2 / E3→E4 先例）；TGT-08
  gate_binding `primary_module_version` 跟随 built manifest（当前 `0.0.0`）；
  **MOD-TGT01 / MOD-TGT05 binding 仍 `1.0.0`**（未动）；`gate_modules/` 下只有
  `tgt01_*` / `tgt05_*` / `tgt08_*` 的 `.py`（无 generic framework）；合同正文
  正则扫无 numeric / ranking cutoff；`MIGRATION_PENDING` 保持。
- `DrawingTests`：drawing 存在、含两句醒目标语（blockquote）、1–17 每项作为
  表格行出现、含 "PR E5 does not touch it" + "PR E6"；含 "the first gate whose
  canonical assessment can be `negative`" + "it is **not** a scientifically bad
  target"。

## 四、明确未改 / 未做

- **未写** 任何 Module 实现代码；**未建** `gate_modules/tgt08_*/` 目录；**未接**
  任何 retrieval provider / patent database / dataset；**未产** EvidencePackage /
  Assessment 运行输出；**无** numeric·ranking scoring / FTO·legal logic /
  sponsor decision runtime / 新 scientific·strategic ladder semantics / generic
  GateModule framework / abstract base class。
- **未改** PR A / B / C 合同；**未改** PR D 的 TGT-08 Gate science（parity 测试
  只读不写）；**未改** MOD-TGT01 / MOD-TGT05（binding 仍 `1.0.0`，
  `gate_modules/tgt01_*/` / `tgt05_*/` 代码未动）；**未改** TGT-08
  `primary_module_version`（仍 `0.0.0`，PR E6 才 bump）。
- **未解除** `MIGRATION_PENDING`。无新依赖（仍只 PyYAML）。
- 其余 5 个 TGT primary Module（TGT-02 → 03 → 04 → 06 → 07）属 PR E6+。

## 五、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> 全量 963（918 baseline + 45 E5）；唯一本地 FAIL 是既有 __pycache__ 物理扫描
#    噪音（test_assetgenos_modules），CI 干净 checkout 上 GREEN
git diff --check                       # clean
bash scripts/verify_repository_boundary.sh   # 干净 tracked-tree worktree 上 pass
python3 -c "import yaml; yaml.safe_load(open('src/contracts/gate_modules/tgt08_target_opportunity_competition_ip_whitespace.yaml'))"  # 结构合法
```

## 六、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入）。审核重点：8 个 scoping 决策 E5-1…E5-8 是否逐条落实、03/05/07/08
  是否 normalized-equality parity + 04 derived parity 冻结 PR D TGT-08、
  commercial/strategic 三层边界（`NEGATIVE` reachable but not KILL / sponsor
  stop、favorable commercial picture 不 de-risk 科学、FTO / no-design-around /
  no-differentiation-path forbidden）、two-axis DIRECT bundle + completion
  provenance for absence inference、`sponsor_review` 是 machine-local review
  trigger 且不同于 `fatal_review`、E2/E4 genes 冻结、是否确实无实现 / provider /
  framework、MOD-TGT01 / MOD-TGT05 与 TGT-08 binding version 未动。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一对话
  复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #95/#97/#99/#101/#103/#105/#107/#109/#111/#113 先例）。

## 七、后续（PR E6+，未启动）

- **PR E6** —— MOD-TGT08 实现：新建顶层
  `gate_modules/tgt08_target_opportunity_competition_ip_whitespace/`（providers /
  adapters / trial·patent retrieval / extractor / normalizer / runner /
  dry-run executor / EvidencePackage writer / assessment proposer /
  `sponsor_review` detector），单向依赖 `src/`；并把 TGT-08 gate_binding
  `primary_module_version` `0.0.0 → 1.0.0`。仅在本合同 APPROVE 后开工。
- **PR E7+** —— 逐 Gate 施工图 + 实现，按 `TGT-02 → 03 → 04 → 06 → 07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
