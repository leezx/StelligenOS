# ChatGPT 审核记录：Runtime Migration PR E1 —— TGT-01 / MOD-TGT01 Construction Contract

- 日期：`2026-08-29`
- PR：#106 `task_20260829_runtime-migration-pr-e1`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`2596c96`（第三轮修订，drawing wording residual）
- Merge 提交：`b20c021`（`Merge pull request #106 from leezx/task_20260829_runtime-migration-pr-e1`）
- 结论：**APPROVE @ `2596c96`**。E1 construction contract 冻结。下一步 PR E2 =
  MOD-TGT01 implementation，严格按本施工合同实现，不重新定义 Gate science 或
  proposal / canonical semantics。

本记录在**独立 docs-only PR**（`task_20260829_runtime-migration-pr-e1-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 / #105 先例——审核记录不落在被批准的
PR branch 上。本 PR 同时把 `manifests/runtime_migration_pr_e1_manifest.yaml`
补成 approved。不改 PR E1 的施工合同、drawing 或测试内容。

## 四个 scoping 决策（建代码前，审核方拍板）

- **E-1：起手 Gate = TGT-01**（ADC Modality Precedent）。顺序确认 fatal-first +
  cheap-first：`TGT-01 → TGT-05 → TGT-08 → TGT-02 → TGT-03 → TGT-04 → TGT-06 →
  TGT-07`。TGT-01 不是最 fatal，而是最好的 **Module architecture calibration
  case**：`PUBLIC_PRIMARY`、不依赖 CRC 多组学下载、不依赖实验、evidence class
  最简单、能最快验证完整链条。
- **E-2：选 E2a 并冻结**。PR E1 只交付 frozen Module construction contract +
  human-readable drawing + validation/tests + 17 项 acceptance checklist。
  **不出现** provider / adapter / extractor / normalizer / runner / dry-run
  executor / EvidencePackage runtime output / Assessment proposer
  implementation，甚至 no-op runner 也不要。`PR E1 = DESIGN_FREEZE`，
  `PR E2 = MOD-TGT01 implementation`。E1 merge 后 `MIGRATION_PENDING` 仍不解除。
- **E-3：Module 代码不放 `genmodules/`**（那是 Asset Generation lifecycle，明文
  `not Gate implementations`）。物理布局冻结为
  `src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml` +
  `docs/gate_modules/TGT-01_ADC_Modality_Precedent.md` + `tests/`。未来 PR E2
  才新建顶层 `gate_modules/`，单向依赖（`kernel defines contract; Gate Module
  implements contract`；`src/` 不 import `gate_modules/`，与 `extensions/`
  同治理）。
- **E-4：17 项 template 原文拿不到**。Blueprint v1.3 §H2.8（Gate Module
  Acceptance Template）被 CURRENT_SYSTEM v5 引用，但仓库和 File Library 都没有
  正文。合同 `template_provenance.status: RECONSTRUCTED` +
  `claim.not_claimed_verbatim_from_blueprint: true`，17 项由冻结 v5 §6.4 +
  PR A–D 合同重建。

TGT-01 专属锁死：**MOD-TGT01 回答"这个 target 是否已经被 ADC modality 现实检验
过？"**，不回答 target-在-CRC-好不好 / ADC-有没有效 / 治疗窗-安不安全 /
density·internalization 是否充分。source plan 可命名 ADCdb / trial / regulatory /
company / publication / patent source classes，但 **PR E1 不接任何 provider**。

## 四轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `6543174`（首版：施工合同 + drawing + 18 tests + 17 项 checklist） | `REQUEST_CHANGES`。外层 scope PASS（E-1～E-4 落实、17 项数量与顺序完整、测试直接读 PR D `crc_adc_target_gateset.yaml` 做 normalized equality、顶层 `gate_modules/` 不存在、provider / implementation / numeric scoring 均 `forbidden`）。剩 **3 个 E1 construction-contract blocker**。 |
| 2 | `84de608`（第一轮修订，21 tests） | `REQUEST_CHANGES`。3 个 blocker 全部关闭且被 regression test 锁住。剩 **1 个新的窄口**：item 12 proposal-envelope identity completeness。 |
| 3 | `c6cb838`（第二轮修订，22 tests） | `REQUEST_CHANGES`。item 12 machine contract 正确、regression test 锁住。剩 **同一 blocker 在 human drawing 的两处旧措辞**（docs-only）。 |
| 4 | `2596c96`（第三轮修订，23 tests / 774 全量） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 3 个 blocker（`6543174` → `84de608`）

都在同一 PR 内做最小契约修订，不写任何实现，scoping E-1～E-4 不变。

1. **item 12 proposal / canonical 边界。** 首版写 Module "proposes a
   CandidateGateAssessment"，与 PR A 冻结合同直接矛盾：`CandidateGateAssessment`
   是 canonical matrix cell，`CANONICAL_REVIEW_STATUS = HUMAN_APPROVED`，构造该
   对象时 `review.status != HUMAN_APPROVED` 即被 reject。改名
   `12_assessment_proposal_envelope_contract`：Module 产出 **non-canonical、
   module-local proposal envelope**，只 MIRROR `assessment.schema.json` 的
   field 形状、不带 `review` block；canonical 对象由 review surface 在
   HUMAN_APPROVED 之后（item 14）构造，Module 永不构造。item 13/14/15/17
   同步改词。
2. **item 16 fatal-safe stop rule。** 首版 "when any of" 成立就停，第一条即
   "TGT-01 evidence ceiling reached" —— 找到一个足够强的 same-target clinical
   ADC precedent 就停，会漏掉 item 08 的 discontinued / failed 同靶点项目扫查
   （与 fatal-first 自相矛盾）。新增 `mandatory_completion_before_any_stop`
   （同靶点 ADC 项目清单含 active / approved **及** discontinued / failed +
   已披露 failure / discontinuation-reason 扫查必须先完成）+
   `rationale_for_the_mandatory_sweep`；原 4 条 stop 条件降为
   `then_stop_searching_public_evidence_when_any_of`。item 13 machine 验收增一条
   "item-16 mandatory completion conditions are satisfied"。不改 PR D fatal
   semantics。
3. **item 09 ADCdb source authority。** 首版把 "an ADC-target database (e.g. an
   ADCdb-class asset) resolved to its primary disclosures" 放在 `strong` source
   class，易被 E2 实现成 `ADCdb row → strong EP → DIRECT`（secondary-index
   evidence laundering）。移出 `strong`，新增 `discovery_and_index_layer` +
   `discovery_index_authority_rule`：ADCdb-class 库只做 discovery /
   entity-resolution / program inventory，**不独立确立 Evidence Ladder rung**；
   行解析后 EvidencePackage 的 provenance / evidence authority 归底层 primary
   disclosure；未解析的 database-only 行是 retrieval lead。不改 PR D Evidence
   Ladder。

## 第二轮 REQUEST_CHANGES 的 1 个 blocker（`84de608` → `c6cb838`）

**item 12 proposal-envelope identity completeness。** 首版
`the_proposal_envelope_carries` 只有 scientific fields + machine record，不带
canonical `CandidateGateAssessment` 的 identity pins。proposal artifact 因此
无法被独立审计地回答"这是哪个 candidate / instantiation / context / gate 的
proposal"，只能靠 review surface 从 item 10 外部 input 补回来 —— 对一个要落成
E2 runtime handoff artifact 的施工合同不够稳。

修订（只动 item 12）：`the_proposal_envelope_carries` 拆成
`identity_pins_for_deterministic_canonicalisation`（`candidate_id` /
`instantiation_id` / `context_id` / `context_version` / `gateset_id` /
`gateset_version` / `gate_id` / `gate_version`，对齐
`src/contracts/data_layout/assessment.schema.json` 的 `required` 字段）、
`scientific_fields`、`machine_record`；新增
`the_proposal_envelope_never_carries`（`assessment_id`、`assessment_version`、
`review.status` / `reviewer` / `reviewed_at` —— 属 human canonicalisation）。
`rules` / `shape_ref` 改词：proposal envelope 不对 `assessment.schema.json`
做校验，只承载它的 identity pins + scientific fields 以便 deterministic
field-map canonicalisation。新增
`test_item12_proposal_envelope_carries_all_identity_pins`。

## 第三轮 REQUEST_CHANGES 的 docs-only 残留（`c6cb838` → `2596c96`）

同一 proposal / canonical boundary blocker 在
`docs/gate_modules/TGT-01_ADC_Modality_Precedent.md` 的两处旧措辞（不动 machine
contract）：

1. **Gate ordering 段链条**：`proposed CandidateGateAssessment` →
   `assessment proposal envelope`，链条终点补
   `→ human-review surface → HUMAN_APPROVED CandidateGateAssessment`，加一句
   Module 永不产 canonical `CandidateGateAssessment`（review surface 在 approval
   时才产）。
2. **item 17 行**：重写为 Module 交付 `EvidencePackage`s + assessment proposal
   envelope 给 human review surface；只有 HUMAN_APPROVED 之后 review surface 才
   构造 canonical `CandidateGateAssessment`，*那条记录*才被 `MatrixView` /
   GateSet decision layer 消费；Module 自身输出不直接进入 `MatrixView` 或
   decision layer；不构造 `CandidateGateAssessment`、不发 `HUMAN_APPROVED`
   记录。

新增 `test_drawing_has_no_stale_proposed_candidategateassessment_wording`。

## APPROVE 时的确认（`2596c96`）

- 两处 docs residual 已与 machine contract 对齐；drawing regression test 禁止旧
  `proposed CandidateGateAssessment` wording 与 direct-to-Matrix / decision
  语义回归。
- PR HEAD `2596c96`，open、mergeable，CI `verify (3.11 / 3.12)` success。
- E-1～E-4、items 03/05/07/08、item 09、item 12 machine contract、item 16、
  PR D parity、repository boundary 全程未改。
- 全程无实现 / provider / runner / numeric scoring / 新依赖 / 新 core object；
  PR A/B/C/D 合同与冻结文档未动；`MIGRATION_PENDING` 未解除。
- 全量测试 774 OK（751 baseline + 23 E1）。

GitHub connector 写 review（APPROVE / REQUEST_CHANGES）四轮都返回
`403 Resource not accessible by integration`，故 GitHub review state 未写回；
审核结论全文在 `AI审核方案` 对话中转述，并由本记录补登。

## 后续

- **PR E2** —— MOD-TGT01 implementation：新建顶层
  `gate_modules/tgt01_adc_modality_precedent/`（providers / adapters /
  extractor / normalizer / runner / dry-run executor / EvidencePackage writer /
  Assessment proposer），单向依赖 `src/`。**需用户单独 go-ahead 后才开工。**
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
