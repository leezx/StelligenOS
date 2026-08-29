# Handoff：Runtime Migration PR E1 —— TGT-01 / MOD-TGT01 Construction Contract

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e1`
- 分支：`task_20260829_runtime-migration-pr-e1`
- 基线：`origin/main`（PR #105 merge，PR D 收口后）
- PR：待创建
- 时间：`2026-08-29`
- 授权：用户"继续直到完成所有 PR A-D"后追加"开始 PR E"，并让审核方（ChatGPT
  `AI审核方案`）拍 scoping 决策。
- 变更定位：`RUNTIME_CONTRACT_ADD`（第五层：TGT-01 primary Evidence Production
  Module 的**施工合同 + 施工图 + 验收清单**。不写实现、不接 provider、不产
  EvidencePackage / Assessment、不改冻结文档、不新增依赖、不解除
  `MIGRATION_PENDING`）。

## 一、依据（冻结文档，本 PR 不修改，只按其顺序施工）

- CURRENT_SYSTEM v5 §6.4（一 Gate 一主 Evidence Production Module；Module 不得改
  Gate id / name / candidate ownership / gate_question / Evidence Ladder /
  evidence ceiling / fatal / unknown / conflict / inference semantics；不得跨
  Gate 推理；不得降低 measurement requirement；不得把 UNKNOWN 自动变 PASS /
  HOLD / KILL；"逐 Gate 绘制施工图，审核通过后 Module 才可开工"）、§6.5（shared
  infrastructure：retrieval / entity resolution / provenance ledger /
  serialization 可多 Gate 共用，不含 Gate-specific scientific authority）、
  §16 B 组问题 23（PR E+ = 逐 Gate primary Module，TGT-01 … TGT-08）。
- `src/contracts/crc_adc_target_gateset.yaml`（PR D，`ADC_TARGET_GATESET@1.0`）：
  TGT-01 的 `gate_question` / Evidence Ladder / `allowed_inference` /
  `forbidden_inference` / `fatal_conditions` —— **逐字继承**。
- `src/contracts/data_layout/evidence_package.schema.json` /
  `assessment.schema.json`（PR A 形状）；`src/contracts/evidence_reference.yaml`
  （PR C 可复用 EP 引用层 + provenance walk）；`src/contracts/gate_contracts.yaml`
  （PR B：`assessment_rule` / `fatal_gate_policy` 是 GateSet 级 ref，不是 Module
  逻辑）。
- `extensions/README.md`（单向依赖治理：外围可引用内核，内核不引用外围）；
  `genmodules/README.md`（GenModules 属 Asset Generation lifecycle，**不是** Gate
  implementations）。

## 二、四个 scoping 决策（审核方在 `AI审核方案` 拍板）

1. **E-1：起手 Gate = TGT-01。** 顺序确认 fatal-first + cheap-first：
   `TGT-01 → 05 → 08 → 02 → 03 → 04 → 06 → 07`。TGT-01 是最合适的第一个，理由是
   它是最好的 **Module architecture calibration case**：`PUBLIC_PRIMARY`、不依赖
   CRC 多组学下载、不依赖实验、evidence class 最简单、能最快验证完整链条。
2. **E-2：选 E2a，且冻结这一点。** PR E1 只交付
   `TGT-01 frozen Module construction contract + human-readable construction
   drawing + contract validation/tests + acceptance checklist`。**不出现**
   provider / adapter / extractor / normalizer / runner / dry-run executor /
   EvidencePackage runtime output / Assessment proposer implementation。同一个
   PR 一边 review 施工图一边出 runner，就违反 design-before-execution。
3. **E-3：Module 代码不放 `genmodules/`。** 物理布局冻结为
   `src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml`（机器施工合同）
   + `docs/gate_modules/TGT-01_ADC_Modality_Precedent.md`（人读施工图）+
   `tests/`。未来 **PR E2** 真正实现时才新建顶层 `gate_modules/` 目录
   （`gate_modules/tgt01_adc_modality_precedent/`），单向依赖（kernel defines
   contract；Gate Module implements contract；`src/` 不 import `gate_modules/`）。
4. **E-4：17 项 template 目前拿不到原文。** Blueprint v1.3 §H2.8（Gate Module
   Acceptance Template 17 项）被 v5 引用，但**不在仓库或 File Library**。因此
   合同里 `template_provenance.status: RECONSTRUCTED`，`claim.not_claimed_verbatim_from_blueprint:
   true`，17 项由冻结 v5 §6.4 + PR A–D 合同重建，功能上完整且与过去讨论一致。

TGT-01 专属锁死：**MOD-TGT01 回答的是"这个 target 是否已经被 ADC modality
现实检验过？"**，不是"target 在 CRC 是否好 / 我们的 ADC 是否有效 /
therapeutic window 是否安全 / density·internalization 是否充分"。source plan
可命名 ADCdb / trial / regulatory / company / publication / patent source
classes，但 **PR E1 不接任何 provider**。

## 三、交付物

| 文件 | 说明 |
|---|---|
| `src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml`（新） | 机器施工合同：`migration`（pr `runtime_migration_pr_e1`、`boundary` design-before-execution、`next` PR E2、`order`）；`template_provenance`（`RECONSTRUCTED` + source 4 条 + `not_claimed_verbatim_from_blueprint`）；`kernel_invariant`（单向依赖 + Module 权责边界）；`acceptance_checklist` **17 项**（`01_gate_identity_and_version` … `17_downstream_consumer_and_handoff`），其中 03 `gate_question` / 05 Evidence Ladder + ceiling / 07 allowed·forbidden inference / 08 fatal_conditions 逐字继承 PR D TGT-01；04 列出 7 个 not-admissible-into-this-gate（TGT-02…08）；09 evidence_source_plan（`PUBLIC_PRIMARY`、strong/supporting/weak_only source classes、`connect_provider_in_this_pr: false`、shared-infra note）；`deferred_to_pr_e2_plus`；`repository_policy`（implementation / provider / numeric_scoring `forbidden`，`migration_pending: remains`）。 |
| `docs/gate_modules/TGT-01_ADC_Modality_Precedent.md`（新） | 人读施工图：本文件是什么、MOD-TGT01 只回答什么、template provenance、gate ordering、17 项验收清单（表格）、PR E2+ deferred。 |
| `tests/test_tgt01_module_construction_contract.py`（新，18 tests） | 见 §四。 |
| `manifests/runtime_migration_pr_e1_manifest.yaml`（新） | `chatgpt_review: PENDING`、4 个 scoping_decisions、boundary 声明、artifact 清单。 |

## 四、测试（`tests/test_tgt01_module_construction_contract.py`，18 tests）

- `ContractShapeTests`：version `0.1.0`、`migration.pr == runtime_migration_pr_e1`、
  boundary 含 "no implementation"、`next` 指 PR E2、`order` 正确；
  `template_provenance.status == RECONSTRUCTED` 且 `not_claimed_verbatim_from_blueprint`、
  source 提及 "Blueprint v1.3 section H2.8" + "not present in this repository"；
  `kernel_invariant` 含 "src/ must never import gate_modules/"；
  `acceptance_checklist` 恰好 17 项且键名顺序 == `01_…17_`。
- `VerbatimFromPrDTests`：item 01 identity（TGT-01 / `1.0` / ADC_TARGET_GATESET /
  L04 / INST-CRC-REFRACTORY-ADC-TARGET-v1）；item 02 `MOD-TGT01` +
  `module_implementation_version == "0.0.0"`；item 03 `text`（空白归一化）==
  PR D TGT-01 `gate_question` 且 framing "already been reality-tested"；item 04
  `not_admissible_into_this_gate` 含 TGT-02…08；item 05 三个 rung 的
  `admissible_evidence_classes` + `ceiling_rule` + `evidence_ceiling` 逐字 ==
  PR D；item 07 allowed / forbidden 逐字 == PR D；item 08 `potential_fatal_signal`
  逐字 == PR D `fatal_conditions` 且 rule 含 "never performs a candidate-level
  kill"；item 15 "not KILL" + "never silently converted"。
- `NoImplementationInPrE1Tests`：`repository_policy` 4 项（implementation /
  provider / numeric_scoring `forbidden`，`migration_pending: remains`）；
  `deferred_to_pr_e2_plus` 提及 `gate_modules/` / implementation / runner；
  顶层 `gate_modules/` 目录**不存在**；
  `09_evidence_source_plan.connect_provider_in_this_pr == false`；合同正文正则
  扫无 numeric cutoff（`>N` / `<N` / `N%` / `N/cell` / `N molecules`）。
- `DrawingTests`：drawing 存在，含 framing question、`RECONSTRUCTED`、
  "construction contract + drawing only"；1–17 每项都作为表格行出现。

## 五、明确未改 / 未做

- **未写** 任何 Module 实现代码；**未建** 顶层 `gate_modules/` 目录；**未接**
  任何 retrieval provider / dataset；**未产** EvidencePackage / Assessment 运行
  输出；**无** numeric scoring；**无** 新 scientific ladder semantics。
- **未改** PR A / B / C / D 的合同或对象；`src/objects/*` 未动；`data_layout/*`
  未动；任何冻结文档未动。
- **未解除** `MIGRATION_PENDING`（整个 PR E 系列完成前，repository runtime 不得
  声称已实现 Blueprint v1.3 conformance）。无新依赖（仍只 PyYAML）。
- 其余 7 个 TGT primary Module（TGT-05 → 08 → 02 → 03 → 04 → 06 → 07）属 PR E2+。

## 六、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 769 tests ... OK   (751 baseline + 18 new)
git diff --check                       # clean
bash scripts/verify_repository_boundary.sh   # 干净 tracked-tree worktree 上 pass
python3 -c "import yaml; yaml.safe_load(open('src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml'))"  # 结构合法
```

## 六之二、第一轮修订（PR #106 @ `6543174` REQUEST_CHANGES）

审核方（ChatGPT `AI审核方案`）在 PR #106 首版给 **REQUEST_CHANGES**，只列 3 个
E1 construction-contract blocker，并声明修完这 3 点下一轮直接 **APPROVE E1 → 开
PR E2 implementation**，不重开 E-1～E-4 scoping。3 处修订都在同一 PR 内做最小
改动，**不写任何实现**。

1. **item 12 —— proposal / canonical 边界。** 首版"proposed
   CandidateGateAssessment"与 PR A 冲突：`CandidateGateAssessment` 是 canonical
   matrix cell，`CANONICAL_REVIEW_STATUS = HUMAN_APPROVED`，`review.status !=
   HUMAN_APPROVED` 构造即被拒。改名 `12_assessment_proposal_envelope_contract`：
   Module 产出 **non-canonical、module-local proposal envelope**，不是
   `CandidateGateAssessment`；envelope 只 MIRROR `assessment.schema.json` 的
   field 形状、不带 `review` block；canonical 对象由 review surface 在
   HUMAN_APPROVED 之后（item 14）构造，Module 永不构造。item 13/14/15/17
   同步改词。
2. **item 16 —— fatal-safe stop rule。** 首版 stop 条件命中 positive ceiling
   即可停，会跳过 item 08 的 discontinued / failed 同靶点 ADC 项目扫查。新增
   `mandatory_completion_before_any_stop`（同靶点 ADC 项目清单含 active /
   approved **及** discontinued / failed + 已披露停止 / 失败原因扫查必须完成）
   + `rationale_for_the_mandatory_sweep`（positive ceiling 不 license 停；违反
   fatal-first）；原 4 条 stop 条件降为
   `then_stop_searching_public_evidence_when_any_of`。item 13 machine 验收增
   "item-16 mandatory completion conditions are satisfied"。
3. **item 09 —— ADCdb source-authority 边界。** 首版把 "an ADCdb-class database
   resolved to its primary disclosures" 放进 `strong` source class，等于让
   secondary index 直接确立 ladder rung。移出 `strong`，新增
   `discovery_and_index_layer` + `discovery_index_authority_rule`：ADCdb-class
   库只做 discovery / entity-resolution / program inventory，**不独立确立
   Evidence Ladder rung**；行解析后 EvidencePackage 的 provenance 与 evidence
   authority 归底层 primary disclosure；未解析的 database-only 行是 retrieval
   lead。明确不改 PR D Evidence Ladder。

三处同步落到 `docs/gate_modules/TGT-01_ADC_Modality_Precedent.md` 的第
9 / 12 / 16 行表格；`tests/test_tgt01_module_construction_contract.py` item 12
键名改为 `12_assessment_proposal_envelope_contract`，新增
`test_item12_is_a_non_canonical_proposal_envelope` /
`test_item16_has_a_mandatory_adverse_sweep_before_any_stop` /
`test_item09_adcdb_is_a_discovery_index_not_an_evidence_authority`（共 21 tests）。

**仍未改：** 无实现、无 provider、无 runner、无 numeric scoring、无新依赖、
未动 PR A/B/C/D 合同与冻结文档、`MIGRATION_PENDING` 未解除，scoping 决策
E-1～E-4 不变。

验证：`test_tgt01_module_construction_contract` 21 OK / 全量 `unittest
discover` **772 OK**（751 baseline + 21 E1）/ `git diff --check` clean / 干净
tracked-tree worktree boundary passed / YAML 结构合法。

## 七、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入；GitHub connector 写 review 仍 `403`）。审核重点：4 个 scoping 决策
  是否落实、17 项验收清单是否功能完整、item 03/05/07/08 是否真的逐字继承 PR D、
  是否确实**没有**任何实现 / provider / runner / 数据。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一对话
  复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #95/#97/#99/#101/#103/#105 先例）。

## 八、后续（PR E2+，未启动）

- **PR E2** —— MOD-TGT01 实现：新建顶层 `gate_modules/tgt01_adc_modality_precedent/`
  （providers / adapters / extractor / normalizer / runner / dry-run executor /
  EvidencePackage writer / Assessment proposer），单向依赖 `src/`。仅在本合同
  APPROVE 后开工。
- **PR E3+** —— 逐 Gate 施工图 + 实现，按 `TGT-05 → 08 → 02 → 03 → 04 → 06 →
  07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
