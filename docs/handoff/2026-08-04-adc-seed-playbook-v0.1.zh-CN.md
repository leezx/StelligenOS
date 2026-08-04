# 任务交接备忘：Target-centered ADC Seed Playbook v0.1 实施与压力测试（外部 run 留痕）

- 任务编号：`task_20260804_adc-seed-playbook-v0.1`
- 分支：`task_20260804_adc-seed-playbook-v0.1`（从 `main` `dcc94a7` 创建）
- 当前状态：`PENDING_CHATGPT_REVIEW`
- 任务性质：外部运行留痕（audit record for an external run）
- 代码变更：`NO_CODE_CHANGE`
- Gate 变更：`NO_GATE_CHANGE`
- 测试变更：`NO_TEST_CHANGE`
- 契约变更：`NO_CONTRACT_CHANGE`
- 架构变更：`NO_ARCHITECTURE_CHANGE`（结论，非假设，见第 3 节）

**本 PR 不适用 `AGENTS.md`「审核豁免」。** 该豁免只覆盖 `prompts/GPT-Feedback.md`；本 PR 提交的是
handoff 与 worklog，落在允许集合之外，须经 ChatGPT `APPROVE` 后方可合并。

## 1. 来源与指示

人类负责人指示：读取 `5.Archive/ChatGPT/2026-GPT-Biotech#Target-centered ADC Seed Playbook v0.1`，
**分步骤分模块做完后再一起审核**（不逐模块送审）。

引用中的 `#` 是 Obsidian 标题链接，故实际目标为
`Zhixins-KB/5.Archive/ChatGPT/2026-GPT-Biotech.md` 的 `Target-centered ADC Seed Playbook v0.1` 一节，
即该 45,830 行文件的第 1-382 行。已全文读取。

## 2. 授权状态（须裁决）

**该外部 run 在执行时没有授权 PR。如实记录，不作辩解。**

与前一个 run 相同的两条冲突仍然成立：`AGENTS.md` 第 23 行把「外部数据运行」列入必须通过 PR 交付并送审
的范围；第 24 行禁止在当前 PR 获 `APPROVE` 前开始下一项工作，而 **PR #52 与 PR #53 均处于 `OPEN` 且
未批准**。两条均已向人类负责人提出，人类负责人指示继续并在完成后统一审核。

后果写入产物本身而非隐去：run `status` = `draft_pending_repo_review`，`authorising_pr` = `null`，
`source_manifest.json` 的 `authorisation_status` 与 `run_report.md`「Governance status」一节记录同一
事实。**执行者不主张既成事实**；若裁决为不可追认，产物应作废重跑。

## 3. 最重要的结论：本 playbook 不需要改架构

**M1 将 playbook 完整映射到冻结拓扑，34 行中需要新契约的为 0 行**（32 行 full coverage，2 行 partial）。

这一点关键，因为架构今日刚冻结、每月只有一次修复额度；而 playbook 自己的第七节也明确说「框架已经足够」、
当前更高价值的动作是跑通一个真实闭环而不是继续扩框架。两个约束方向一致，M1 是**独立验证**这一致性而非
假设它。**本次不消耗月度架构修复额度。**

映射要点：

- 左链 10 步 → T0-T7 加 P34；右链 17 步 → T7-T11 再 P20-P35，FTO 落在 C45/C46/C49。
- 第六节五个停顿点 → T12、P20、P27、P32/P33、P35，均不隐含新 Gate。
- **Seed 就是 v5 `ClinicalHypothesis` + `entry_mode = mature-target-first`。** playbook 从
  「indication → target → ADC」转向 target 为中心的重构，已于 2026-08-03 被 v5 吸收。
- **Seed Admission Standard 就是 `CandidateFilterResult`**，契约明确写了它不是 Gate；其
  `filter_policy_ref` 必须是 `external:`，因此该 policy **按设计**属于仓库之外，不是让步。
- 第八节把 Gate 重新表述为资本分配而非评分，是对既有 `output_semantics`（`null_is_not_zero`、
  `nullable_domain_values_mean_unknown`、`missing_information_is_explicit`、禁止总分覆盖 hard fail）
  的重述，不是改动。

两行 partial，记录而未解决：R-05 shedding／soluble antigen 无专属 Gate；S-02 playbook 把
ADC-grade antibody 放进 Seed，而 `BinderCandidate` 位于 `TargetHypothesis` 下游，`ProductHypothesis`
以约束形式表达抗体要求。

## 4. 数据边界

**本 PR 不引入任何数据、结果或运行产物。** 全部产物位于仓库之外：

```
/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/
  gen_iet_adc_seed_playbook_v0.1_20260804T201605Z/
```

已验证仓库工作树未被该 run 触碰。**未运行任何 Gate，未赋任何 Gate score**；
`RETAIN`/`DEFER`/`EXCLUDE` 属 `CandidateFilterResult` 语义，按契约明确不是 Gate 结果；
`NOT_EVALUATED` 与 `UNRESOLVED` 全程保留未降级为 PASS；T0-T12 未执行，45-Gate 拓扑未触碰。

## 5. 六个模块产出

| 模块 | 产物 | 规模 |
|---|---|---|
| M1 映射到冻结拓扑 | `m1_playbook_to_gate_map.tsv` | 34 行，需新契约 **0** |
| M2 Seed Admission Standard | `m2_seed_admission_standard.tsv` | 36 行：5 决策规则／21 类别准则／8 致命否决／2 排序规则 |
| M3 Seed Discovery Sprint | `m3_seed_discovery_sprint.tsv` | 17 靶点：8 RETAIN／7 DEFER／2 EXCLUDE |
| M4 抗体开发进入门槛 | `m4_antibody_entry_threshold.tsv` | 10 条件 + 1 指针行 |
| M5 三靶点压力测试 | `m5_three_target_stress_test.tsv` | 30 条件行 + 3 决策 |
| M6 Gate 决策价值 | `m6_gate_decision_value.tsv` | 14 条发现（6 high） |

M2 补了三条 playbook 隐含但未写明的决策规则：RNA 永不满足任一类别（外部工作区规则 3 无例外）；
证据缺失记为未满足且永不构成否决；disposition 三值化，2/4 且无否决时 DEFER 而非淘汰。

M4 的 AE-06 内吞**故意设为非阻断**，因为 playbook 明确说只有抗体实验能回答它，设为阻断会制造第五节
自己警告的无限研究。AE-10（最大剩余不确定性必须只能由抗体／ADC 实验回答）是决定性条件。M4
**未复述**第五节的排序规则，改为指向 M2 的 SEQ-01／SEQ-02，理由是 EXT-02 曾因同一值存在两处而漂移。

## 6. 压力测试结果：无一进入 PROVISIONAL_ADVANCE

| 靶点 | 类别 | 达标 | 阻断条件 | 决策 |
|---|---|---|---|---|
| GUCY2C | A 已部分 derisk | 7/10 | AE-02、AE-03、AE-10 | `EXPLORATION` |
| CDH17 | B 证据强但 ADC 开发不足 | 5/10 | AE-02、AE-03、AE-07、AE-10 | `EXPLORATION` |
| TNFRSF12A | C 来自 cell-state／atlas | 2/10 | AE-02..05、07、08、AE-10 | `HOLD` |

**GUCY2C 是最有信息量的一例。** 它完全 derisk、无竞争否决、且是既有 consensus 首选，仍然不够资格投入
抗体开发——因为其主要不确定性（indusatumab vedotin 为何败在疗效、转移灶表达是否均一）可由 IHC 与既有
试验读出回答。这个结论**只由 AE-10 产生**；没有 AE-10，就会花钱去学一件更便宜的事能回答的问题。

**CDH17 的阻断问题异常便宜**：连接部定位可能把表位埋在相邻细胞之间，而这可用现有研究抗体染**完整**
组织（而非解离细胞）来判定，不需要任何构建体。

**TNFRSF12A 被正确地 HOLD 而非 FAIL**，因为其阻断证据是缺失而非阴性；其中若干问题是免费的公开查询。

## 7. M6 主要发现

- **组合受限于数据集而非 Gate。** 已测量：三个靶点阻断集合的交集恰为 AE-02、AE-03、AE-10。**一次**
  跨靶点的配对原发／转移 MSS CRC 组织 IHC panel 可同时解锁全部已录入 seed。在该 panel 存在之前，
  继续设计规则不会推动任何事。这是两次 run 中识别出的最高杠杆动作。
- **AE-10 是唯一改变了结论的条件。**
- **结构性缺陷：全部 4 个 class C 靶点均未获录入。** playbook 给 novel／atlas／cell-state 靶点分配
  20-30% 额度，而录入标准要求 3/4 类别由蛋白级或临床 modality 证据满足；新靶点按定义缺少此类已发表
  证据，因此 **class C 无法走同一道门**，该额度按现写法是装饰性的。修法不是放宽标准，而是给 class C
  一条基于**内部** atlas 证据的独立录入路径——这正是 Cancer Atlas 的用途；否则应删掉该额度，不要再把
  novel 靶点描述为「在探索」。
- **两个淘汰都是竞争性而非生物学性的**（MET、ERBB2 各满足 4/4 类别，仅因 FV-06 出局）。seed 阶段
  C-chain 杀掉的比 T-chain 生物学 Gate 更多。
- **决策价值 ≠ 信息可得性。** T7／T11／T2／C42／T12 改变了 disposition；T3 与 T10 没有且结构上不能
  ——playbook 自己说 ADC 靶点不必是 driver，故 T3 阴性不杀 seed；而几乎任何表面蛋白都能找到抗体，故
  T10 几乎总是通过。填充它们很便宜，但不可误认为进展，这正是第四节警告的「退化成数据库工程」。
- **五类证据永远无法由公开数据关闭**：治疗后／耐药灶保留、分布而非均值、内吞通量、单细胞表面拷贝数、
  原位表位可及性。其中拷贝数与原位可及性对每个保留靶点都是决定性的。把它们当作「待查文献」会无限期
  拖住整个组合。
- **系统过松之处只有一处**：shedding／soluble antigen 无专属决策点，而它是 CEACAM5、MUC1、MSLN 的既
  载失败模式，占 17 个 sprint 靶点的约 18%。**建议不加 Gate**——拓扑已冻结，冻结的价值高于整齐；改为
  在 T7 下定义显式 shedding 证据 claim class，属 policy 变更，无需契约变更。

## 8. 建议

1. **跑一次共用 IHC panel**（GUCY2C／CDH17／GPA33／LY6G6D，配对原发与转移 MSS/pMMR CRC 组织，按强度、
   阳性细胞百分比、均一性评分）。
2. **取得 indusatumab vedotin 试验的靶点表达与响应数据**，它决定 GUCY2C 的失败是载荷受限还是靶点受限，
   而该答案会传导到整个组合的载荷选择。
3. **染完整 CDH17 阳性组织**，判定原位表位可及性。
4. **先跑 TNFRSF12A 的免费公开检查**（正常组织图谱、膜定位、ectodomain 大小）再谈其他投入。
5. **在下一轮 sprint 前决定 class C 的录入路径**，或删掉该额度。
6. **不要改架构**；以上全部作为外部 policy 与 run 记录实施。

随后用同一模板重跑 M5 并对比。**模板才是实验，跑一遍不是。**

## 9. 本次产出明确不支持什么

- **M1 的映射是对照实际契约文件与 Gate 目录做出的，可复核；M3 与 M5 的靶点判断不是**，属模型领域知识，
  标注为 `derived_not_calibrated` 或 `unverified_domain_prior`。两者不可等同置信。
- **DPEP1 与 TSPAN8 是为填满 class C 额度而纳入的**，非既有实证，且两者均 DEFER。此举诚实但薄弱，其
  本身即为 F-03 的证据。
- 未执行 skeptic review pass，故 8 个已录入 seed 是待审候选而非推荐。
- 三靶点选择遵循第七节的处方，但每类 n=1，类别层面的结论各只有一个例子支撑。

## 10. 明确未改动

- 无任何代码、契约、Gate 拓扑、Model、Profile、生命周期、核心对象或测试变更。
- 未改动 `AGENTS.md`、`ChatGPT-Codex-talk.md`、Phase Gate 协议、`prompts/GPT-Feedback.md`。
- 未改写任何历史 worklog 条目或既有 handoff 内容。
- 未把数据、缓存、结果或运行产物加入仓库。
- 未改动来源 KB 文件；仅读取。
- 未改动 08-02 与 08-04 早先两次 run 的既有产物。

## 11. 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 207 tests —— OK（与 `main` 相同，本 PR 不含代码或测试变更）

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.

命令：git diff --check
结果：通过

零 `__pycache__`；仓库工作树是否被外部 run 触碰：未被触碰（已验证）
```

外部产物一致性（在外部工作区执行，不写入本仓库）：六份模块 TSV 列数分别为 9／9／14／7／8／7，各自内部
一致；`source_manifest.json` 为合法 JSON。M5 中两个决策行原写 met-count 为 6 与 1，与实测 5 与 2 不符，
已按实测值更正而非保留原文。

## 12. 未决问题与风险

- **授权状态未决**，见第 2 节，为本 PR 首要待裁决事项。
- **class C 录入路径未定**（F-03），影响下一轮 sprint 是否名实相符。
- **S-02 顺序差异待确认**（F-13）：playbook 是否要求 Seed 录入前必须已存在真实 binder。若是，则与其
  自身 class B 定义（有 binder 但无成熟 ADC）冲突。当前按「约束」解读推进，请人类负责人确认。
- shedding 证据 claim class 尚未定义（F-09）。
- 架构冻结后的月度修复窗口仍无机制记录「本月是否已用」；本次未使用，但该事实只靠本文件记录。
- PR #52、#53 仍 `OPEN` 未批准。
- `AGENTS.md` 无测试守卫；豁免三路径无机制强制；CI 不覆盖 macOS；54 个已合并分支待清理（破坏性操作，
  须明确授权）。

## 13. 下一步

- 提交 ChatGPT 审核本 PR，重点为第 2 节授权裁决与第 3 节「不需要改架构」的结论是否成立。
- 获 `APPROVE` 后由人类负责人决定合并。
