# ChatGPT 审核记录：Runtime Migration PR E9 —— TGT-03 / MOD-TGT03 construction contract

- 日期：`2026-08-30`
- PR：#122 `task_20260830_runtime-migration-pr-e9`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`8ba624c`（第二轮修订后）
- Merge 提交：`a2d585d`（`Merge pull request #122 from leezx/task_20260830_runtime-migration-pr-e9`）
- 结论：**APPROVE @ `8ba624c`**。「PR #122 @ `8ba624c` 可以 merge，E9 construction
  contract 可以正式冻结……E9 Construction Contract 已冻结，可以进入 PR E10 =
  MOD-TGT03@1.0.0 deterministic implementation。」GitHub connector 每轮均
  `403 Resource not accessible by integration`，REQUEST_CHANGES / APPROVE 的
  GitHub review state 未写回；`AI审核方案` 对话结论为 authoritative。

本记录在**独立 docs-only PR**（`task_20260830_runtime-migration-pr-e9-approval-record`）
中补登，按 PR #95 … #121 先例。本 PR 同时把
`manifests/runtime_migration_pr_e9_manifest.yaml` 补成 approved。不改 PR E9 的
合同正文、drawing 或 tests 内容。

## 开工前的 scoping 决策（写代码前，审核方在 `AI审核方案` 拍板）

见 `manifests/runtime_migration_pr_e9_manifest.yaml` 的 `scoping_decisions`
（E9-1…E9-8）、`four_mandatory_scoping_corrections` 与 `three_headline_conclusions`，
以及 `docs/handoff/2026-08-30-runtime-migration-pr-e9.zh-CN.md`。要点：

- E9 是**设计冻结**，与 E1 / E3 / E5 / E7 同型：只交 17 项施工合同 +
  human-readable drawing + parity / validation tests + 17 项验收清单；**不含任何
  实现**。Module 在 PR E10 才开工，且必须在本合同 APPROVE 之后。
  `primary_module_version` 保持 `0.0.0`；binding / registry / 既有 test 一律不动
  （唯一既有文件改动是 append `logs/worklog.md`）；`MIGRATION_PENDING` 保持。
- 三条 headline conclusion：baseline expression ≠ persistence（TGT-02 证据除非
  source 本身显式测量 qualified treatment / metastasis context，否则不 discharge
  TGT-03）；TGT-03 是 **bidirectional** scientific persistence gate（qualified
  clinical-context retention → `POSITIVE`，qualified near / marked loss →
  `NEGATIVE`；`NEGATIVE` 不 fatal 不 `KILL`）；reproducible protein-level near /
  marked loss 至多触发 `POTENTIAL_FATAL_PATTERN`，reproducibility 需 auditable
  evidence 且不由 numeric context count 单独定义，Module 永不裁决 fatality。
- 四条 mandatory correction（全部冻进合同）：(1)
  `TRANSIENT_OR_MINOR_DOWNREGULATION` 不固定为 `CONTEXTUAL` —— 仍显示 retained
  expression 时 SUPPORTS persistence（可贡献 `POSITIVE`），永不贡献 `NEGATIVE`
  或 `fatal_review`；(2)「reproducible」= Route A（auditable explicit
  reproducibility qualification）OR Route B（convergent `NEAR_LOSS_OR_MARKED_LOSS`
  across **at least two** independent qualified clinical context identities），
  不是 numeric context count，不是 `"> 2"`；(3) DIRECT protein measurement 是
  **OPEN set**（protein-level clinical-context measurement + factual
  `assay_method` type + `protein_measurement_validation_status` / basis），
  validated IHC / quantitative proteomics / validated multiplex IF 只是范例，非
  closed three-assay whitelist；(4) EvidencePackage **可以**陈述 empirical
  persistence / loss 事实，只有 Gate-relative 结论被禁，且即使 literal
  Gate-relative wording 是 source 自己的 claim，Module 也永不升级。
- items 03 / 05 / 07 / 08 对冻结 PR D TGT-03 合同做 normalized-equality parity；
  item 04 做 **exact** set-equality derived parity；`inference_guard` 逐字 pin。
  items 10–17 继承 E2 / E4 / E6 / E8 runtime genes（fixed-Instantiation
  `context_id` / version + `observation.context_key` / `completion.search_scope`
  HARD binding；exact canonical EP reuse 含 `observation_id` + reused-EP
  canonical-provenance 复核；kind / fact-specific `study_context`；不可被 dedup
  吃掉的 `SEARCH_COMPLETION_AUDIT` EP；HARD integrity 失败 → 拒整个 run）。
  `fatal_review` record 增 `reproducibility_basis_refs`。

## 审核往返（3 轮）

### Round 1 —— REQUEST_CHANGES @ `23e1b7e`

整体架构全部接受（PR D parity、17-item template、item-04 exact-union parity、
inference guard、design-only boundary、Route A / B、open DIRECT assay set、
`ClinicalPersistenceCompletion`、E8 runtime genes、binding 仍 `0.0.0`、
`MIGRATION_PENDING` 均无问题）。**3 个窄 contract-shape blocker**，都不是重开
science，而是把自然语言语义压成 E10 可无歧义消费的 typed fact：

1. **`TRANSIENT_OR_MINOR_DOWNREGULATION` 的 SUPPORTING / CONTEXTUAL 分支缺机器可读
   事实。** 修复：新增 typed upstream classification-driving field
   `residual_target_presence_status ∈ {PRESENT, UNRESOLVED}` +
   `residual_target_presence_basis`。冻结映射：`TRANSIENT_OR_MINOR_DOWNREGULATION`
   + `PRESENT` + auditable basis → `SUPPORTS_PERSISTENCE`；+ `UNRESOLVED` →
   `NONDIRECTIONAL / CONTEXTUAL`。分支只由该字段决定，永不 free-text parsing；
   provider 仍只出事实；字段进入 E10 exact canonical EP reuse identity parity；
   不引入 numeric threshold。合同 items 06 / 11 / 13 / 15；drawing 行 6 / 11 / 13
   + normalized-observation conceptual shape；+5 tests。
2. **裸 `context_id` / `context_ids` 与 canonical Instantiation `context_id`
   撞命名空间。** 修复：只重命名 LOCAL evidence-context namespace ——
   `context_id` / `context_ids` → `persistence_context_id` /
   `persistence_context_ids`；`qualifying_{direct,indirect}_context_ids` →
   `qualifying_{direct,indirect}_persistence_context_ids`；
   `fatal_review.context_ids` → `persistence_context_ids`。canonical
   `context_id`（`CTX-CRC-REFRACTORY-MCRC`，items 10 / 12 identity pins）不动。
   新增 item-09 `persistence_context_id_namespace` 说明 + item-13 HARD
   identity-namespace check。合同 items 09 / 11 / 12 / 13 / 14；drawing 行 9 / 11
   / 12 / 13 + conceptual shape + `ClinicalPersistenceCompletion` 字段表；+2
   tests（+1 canonical-pin regression）。
3. **`protein_measurement_validation_status` 是 DIRECT-driving 但 enum / predicate
   未冻结。** 修复：冻结为 CLOSED enum `{QUALIFIED, NOT_ESTABLISHED}`（新 item-05
   `protein_measurement_validation_predicate` 块），`assay_method` 仍是 OPEN
   factual type。规则：`QUALIFIED` 需非空 auditable
   `protein_measurement_validation_basis`；DIRECT 需
   `protein_measurement_validation_status == QUALIFIED`；`NOT_ESTABLISHED` 永不
   到 DIRECT。仍非 closed assay whitelist。合同 items 05 / 09 / 11 / 13；drawing
   行 5 / 11 / 13 + conceptual shape；+2 tests。

顺带修一个既有 YAML colon-space bug：`migration.spec_refs[5]`（"… for
MOD-TGT03: canonical target identity …"）本被 `yaml.safe_load` 误解析成单键
mapping —— 改写为 " — "。

### Round 2 —— REQUEST_CHANGES @ `1239a2d`

round 1 的 3 个实质 blocker 全部判定关闭。**唯一遗留 blocker（blocker-2 rename
漏改，不涉 science / architecture）**：合同 item 11 的 `SEARCH_COMPLETION_AUDIT`
structured snapshot 仍写旧字段名 `qualifying_direct_context_ids` /
`qualifying_indirect_context_ids`。非文案问题 —— E10 要实现 completion ↔
`SEARCH_COMPLETION_AUDIT` **exact snapshot parity**，冻结旧名会留下两个互相冲突的
machine contract。修复：item 11 该处改为
`qualifying_{direct,indirect}_persistence_context_ids`，并加一句说明 snapshot
字段名与 typed completion 字段名完全一致（同 namespace），E10 parity 无冲突合同。
新增 regression `test_audit_snapshot_uses_the_new_persistence_context_id_namespace`
—— 断言 item-11 `each_package` 合同含两个新 identifier，且合同全文不含任一旧
identifier。审核方明确「不要再动」：Direction、fatal semantics、Route A / Route B、
completion design、EXPERIMENT_REQUIRED、EvidencePackage wording、其他 runtime genes。

### Round 3 —— APPROVE @ `8ba624c`

无新 blocker。审核方确认：HEAD 正确、open、mergeable；exact-head CI run
`33345828221` 两个 matrix legs（3.11 / 3.12）unit tests + repository boundary +
working-tree-unchanged checks 全过；round-2 blocker 完全关闭，exact-head 搜索旧
`qualifying_direct_context_ids` = 0 matches，新 identifiers 在 completion /
namespace declaration / audit snapshot / acceptance criteria 中一致；新增
regression 同时断言两个新 identifier 存在并读取整个 contract 断言两个旧 identifier
均不存在。3 轮收口：Round 1 三个 deterministic contract-shape blocker → CLOSED；
Round 2 一个 audit-snapshot rename residue → CLOSED；Round 3 无新 blocker。

审核方备注（不再为此加一轮）：PR body 初始测试数字仍是旧的 66 / 1274，当前是
75 / 1283，属非阻断 metadata housekeeping —— 已在 merge 前把 PR body 更新为
75 / 1283 + 3 轮审核小结。

## 验证（被审核 HEAD `8ba624c`）

- `tests/test_tgt03_module_construction_contract.py` **75 OK**（round-1 前 66；
  round 1 +8；round 2 +1）。
- 全量 `python3 -B -m unittest discover -s tests -p 'test_*.py'` **1283 OK**
  （PR E8 收口 1208；round-1 提交时 1274）。
- `bash scripts/verify_repository_boundary.sh` 只报既有 untracked 杂项
  （`AI_RESULT_ACCEPTANCE.md`、`CRC Patient Territory Map.png`、
  `STELLIGEN_CONSTRAINTS.md`、`docs/worklogs/`、`pipelines/`）。
- `git diff --check` clean。合同 + manifest YAML 合法且无 list-element-parsed-as-dict。
- exact-head CI（`33345320984` → `33345828221`）两个 matrix leg 全 success。

## 冻结事实

- `chatgpt_review: APPROVE`，`approved_tip: 8ba624c8b17f5fe0cb2c2584739d7ba630ba3745`，
  `merge_commit: a2d585d752142a581cc904a1229692eaa94a0fe7`，`review_rounds: 3`，
  `test_count_at_approval: 1283`。
- MOD-TGT03 `primary_module_version` 仍 `0.0.0`；binding / registry / 既有 test
  未动；`MIGRATION_PENDING` 保持。
- 下一步：PR E10 = MOD-TGT03@1.0.0 deterministic implementation（需各自 go-ahead）。
  fatal-first 顺序余下 TGT-04 → TGT-06 → TGT-07。
