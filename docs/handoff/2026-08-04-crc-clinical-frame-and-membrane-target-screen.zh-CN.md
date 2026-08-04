# 任务交接备忘：CRC 临床框架与膜蛋白靶点筛选（外部 run 留痕）

- 任务编号：`task_20260804_crc-clinical-frame-and-target-screen`
- 分支：`task_20260804_crc-clinical-frame-and-target-screen`（从 `main` `dcc94a7` 创建）
- 当前状态：`PENDING_CHATGPT_REVIEW`
- 任务性质：外部运行留痕（audit record for an external run）
- 代码变更：`NO_CODE_CHANGE`
- Gate 变更：`NO_GATE_CHANGE`
- 测试变更：`NO_TEST_CHANGE`
- 契约变更：`NO_CONTRACT_CHANGE`

**本 PR 不适用 `AGENTS.md`「审核豁免」。** 该豁免只覆盖 `prompts/GPT-Feedback.md`；本 PR 提交的是
handoff 与 worklog，落在允许集合之外，须经 ChatGPT `APPROVE` 后方可合并。

## 1. 触发与授权状态（本 PR 最需要审核的部分）

人类负责人于 2026-08-04 指示：架构冻结生效，此后一个月最多修复一次积累的架构问题；**现在开始做内容**。
第一项内容任务为四步：列出 CRC 所有 clinical unmet needs、列举最合适的临床收益、大致决定临床终点、
开始筛选潜在膜蛋白 ADC 靶点。

**该外部 run 在执行时没有授权 PR。这一点如实记录，不作辩解。**

已建立的模式是「PR 先授权外部 run」：`gen_iet_crc_target_enumeration_20260802` 的
`source_manifest.json` 记录 `approval_pr = PR #28`、`approval_status = ChatGPT APPROVE; external
enumeration authorized`，且该 run 自身的 worklog 写明
`result-review PR is required before treating this run as accepted`。

本次执行时存在两项冲突，均为实质冲突：

1. **`AGENTS.md` 第 24 行**：ChatGPT 未对当前 PR 明确 `APPROVE` 前，不得开始下一项工作。PR #52
   当时（现在仍）处于 `OPEN` 且未批准。
2. **`AGENTS.md` 第 23 行**：全局 PR 审核门禁明确把「外部数据运行、试运行」列入必须通过 PR 交付并
   送审的范围。本次 run 没有授权 PR。

执行者在动手前已就这两条向人类负责人明确提出，人类负责人以「现在开始做内容」直接指示继续。执行者据此
执行，并把后果写入产物本身而非隐去：

- run `status` = `draft_pending_repo_review`
- `source_manifest.json` 的 `authorising_pr` = `null`，`authorisation_status` 全文记录上述两条冲突
- `run_report.md` 设「Governance status」一节陈述同一事实
- 外部 `external_run_worklog.md` 末条记录同一事实

**须请审核方裁决的问题：**该 run 是否可被追认为已授权，或必须作废重跑。执行者不自行认定，也不因产物
已存在而主张既成事实。若裁决为不可追认，产物应作废重跑而非事后补授权。

## 2. 数据边界

**本 PR 不引入任何数据、结果或运行产物。** 全部内容产物位于仓库之外：

```
/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/
  gen_iet_crc_clinical_frame_and_membrane_target_screen_20260804T191053Z/
```

已验证仓库工作树未被该 run 触碰。本 PR 只提交本 handoff 与一条 worklog 记录，符合
`AGENTS.md` 第 27 行「PR 中只能提交可审计的代码/架构契约、manifest、摘要、校验信息和外部路径引用」。

## 3. 契约一致性

产出前先读取 `genmodules/gen_indication_endpoint_target/contracts.py` 与 `README.md`，使产物贴合 v5
`ClinicalHypothesis` 形状、`clinical-problem-first` entry mode 与六级 lock，而不是独立于架构的散文。

已核对：`dcc94a7`（本分支基点）与 `bfc04be`（run 执行时的仓库 tip）之间，`src`、`genmodules`、
`tests`、`extensions` 的差异为 **0 个文件**，因此 run 所依据的契约与本分支完全一致。

**未运行任何 Gate，未赋任何 Gate score。** `membrane_target_screen.tsv` 输出的是
`RETAIN`/`DEFER`/`EXCLUDE`，属 `CandidateFilterResult` 语义，按契约与 `README.md` 的明确规定**不是
Gate 结果**。`NOT_EVALUATED` 与 `UNRESOLVED` 全程保留，未被降级为 PASS。T0-T12 未执行；45-Gate 拓扑
未触碰。

## 4. 与既有工作的关系

**第 1-3 步此前已大体做过，第 4 步完全没做。**

`gen_iet_crc_target_enumeration_20260802`（PR #28 授权）已产出 9 个 CRC 场景、36 条 endpoint、
41 个靶点、1476 个 pair；`Zhixins-KB/2.Biotech/1.CEO/CRC unmet needs.md` 的三模型 consensus 已选定
MSS mCRC 3L+ 与 GUCY2C-first。

但该 catalog 全部 41 行均为 `gate_score_status = not_scored_in_enumeration_run`、
`gate_pass_status = not_assessed`——它是**枚举，不是筛选**。枚举与推荐之间缺少筛选这一步，推荐实际
依托 consensus 文档而非 catalog。本次 run 因此选择继承并扩展，把筛选作为实质内容，而不是重新生成
catalog。

继承 9 个场景与 41 个靶点，新增 11 个场景与 4 个靶点。

## 5. 产物清单

| 文件 | 内容 |
|---|---|
| `run_report.md` | 主分析文档，含 governance 与 counter-evidence 两节 |
| `clinical_unmet_needs.tsv` | 20 个场景（继承 9 + 新增 11），16 列 |
| `clinical_benefit_ranking.tsv` | 7 类临床收益排序，9 列 |
| `endpoint_decisions.tsv` | 12 条终点，带量化门槛，11 列 |
| `membrane_target_screen.tsv` | 45 个靶点、4 道硬门，19 列 |
| `coverage_gaps_vs_prior_run.tsv` | 15 条与 08-02 run 的对账 |
| `source_manifest.json` | 输入、授权状态、证据来源性质 |
| `external_run_worklog.md` | 外部时间戳记录 |

筛选结果：**4 RETAIN / 25 DEFER / 16 EXCLUDE**。Tier A 为 GUCY2C、CDH17、GPA33、LY6G6D。

## 6. 三项对既有产物的发现（建议审核方重点看）

1. **漏掉两个靶点。** GPA33 与 LY6G6D 均不在 41 个靶点内。LY6G6D 特异富集于 MSS，而 MSS 正是
   consensus 自己选定的人群——枚举漏掉了与自身所选战略最匹配的候选。
2. **一处内部矛盾。** 08-02 的 `indication_endpoint_universe.tsv` 在 CMS4 场景引用
   `TNFRSF12A_MSSmCRC_watch.json`，但 TNFRSF12A 从未进入 `target_evidence_catalog.tsv`。两张表未
   对账，属流水线缺陷而非科学判断。本次以 `NOT_EVALUATED` 补入使矛盾可见，未对其 ADC 资质作任何主张。
3. **catalog 含相当比例的泛 ADC benchmark 行。** CLDN18（胃）、PRLR（乳腺）、IL2RA（淋巴）、
   MELTF（黑色素瘤）、FOLR1（卵巢）、LAMP1（溶酶体）、RNF43（胞内）、SLC3A2（近乎普遍表达）、
   CA19-9（碳水化合物抗原，非蛋白）在 CRC 语境下失效。CRC 特异候选池从来小于 41。

## 7. 一条不由任何单步推出的结论

ABBV-400（c-MET）与 M9140（CEACAM5）是推进最快的两个 CRC ADC，**载荷均为拓扑异构酶 1 抑制剂**。
2026 年立项的项目将在 Top1i 暴露过的人群中读出数据，因此**载荷不应默认选 Top1i**——在这一特定竞争
格局下，通行的 deruxtecan 类默认会把一个本无关联的靶点变成交叉耐药负债，且发生在最难回头的决策点。
差异化决策在载荷，不在靶点。已作为 UN-20 与 GAP-14 记录。

同一条也重构了 GUCY2C：indusatumab vedotin **败在疗效而非毒性**。若原因是 MMAE 送不进足够细胞毒，
则正确反应既非「GUCY2C 已死」亦非「改用 deruxtecan 类」，而是先测该靶点的递送能力再据以选载荷。这与
KB consensus 把 GUCY2C 列为首选的结论存在张力，已在 `run_report.md` 明确写出而非抹平。

## 8. 本次产出明确不支持什么

- **本次 run 没有任何一条论断被原始来源验证过。** 所有百分比、ORR/OS 基准、复发风险在 TSV 中标注为
  `unverified_domain_prior` 或 `derived_not_calibrated`，属模型领域知识而非抽取证据。足以支撑排序与
  定框，**不足以作为决策记录**。
- **四个 Tier A 靶点的 `h2_mss_crc_protein_expression` 全为 `UNRESOLVED`**。筛选是在未测量的表达
  属性上排序。外部工作区规则禁止以 RNA 代替蛋白验证，本次未查阅任何蛋白数据。
- **unmet need 分数未校准。** `ADC_clinical_unmet_need_reference@0.1.0` 中 CRC 只有 **1 行**；
  继承的另外 8 个场景为 `not_calibrated`，新增 11 个更弱。分数仅支持相对排序。
- **继承而未关闭的缺口**：41 个靶点仅 6 行 opposing evidence；292 行证据中 172 行为 unknown；
  20 个 expert-review batch 仅审 2 个。
- **未执行 skeptic review pass**，而外部工作区规则要求任何 go/watch 推荐在被视为最终前必须经过该
  环节。因此 Tier A 全部四行是待审候选，不是推荐。

## 9. 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 207 tests —— OK（与 `main` 相同，本 PR 不含代码或测试变更）

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.

命令：git diff --check
结果：通过

零 `__pycache__`；仓库工作树是否被外部 run 触碰：未被触碰（已验证）
```

外部产物一致性检查（在外部工作区执行，不写入本仓库）：四份 TSV 列数分别为 16／9／11／19，各自内部
一致；`membrane_target_screen.tsv` 共 45 行 = 继承 41 + 新增 4；`source_manifest.json` 为合法 JSON。

## 10. 明确未改动

- 无任何代码、契约、Gate 拓扑、Model、Profile、生命周期、核心对象或测试变更。
- 未改动 `AGENTS.md`、`ChatGPT-Codex-talk.md`、Phase Gate 协议。
- 未改动 `prompts/GPT-Feedback.md`。
- 未改写任何历史 worklog 条目或既有 handoff 内容。
- 未新增数据、缓存、结果或运行产物到仓库。
- 未修改 08-02 run 的任何既有产物；本次对其的发现以新文件 `coverage_gaps_vs_prior_run.tsv` 记录在
  外部工作区，未回写覆盖。

## 11. 未决问题与风险

- **授权状态未决**，见第 1 节。这是本 PR 首要待裁决事项。
- 架构冻结后的月度修复窗口尚无机制记录「本月是否已用」，冻结承诺目前依赖执行者自觉。
- `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md` 仍为 `v2-draft` /
  `PENDING_CHATGPT_APPROVAL`。
- PR #52 仍 `OPEN` 未批准，2026-08-04 的审计闭环尚未完成。
- `AGENTS.md` 无测试守卫；豁免三路径上限无机制强制；CI 不覆盖 macOS；54 个已合并分支待清理（分支
  删除属破坏性操作，须明确授权）。
- EXT-01 与 EXT-03 尚未就 v5 吸收情况正式复核。

## 12. 下一步

- 提交 ChatGPT 审核本 PR，重点为第 1 节的授权裁决。
- 获 `APPROVE` 后由人类负责人决定合并。
- 若裁决为不可追认，作废该 run 并在获授权后重跑；执行者不主张既成事实。
