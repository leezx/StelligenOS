# 任务交接备忘：Target-centered ADC Seed Playbook v0.1 实施与压力测试（外部 run 留痕）

> ## 审核裁决与隔离声明（2026-08-04 插入，下方原文一字未删）
>
> ChatGPT 于 2026-08-04 对本 PR 返回 **`REQUEST_CHANGES`**，并指出阻断比 #53 更明确。五条全部接受：
>
> 1. 六模块外部运行无 authorizing PR，且在 **#52、#53 均未批准**时继续执行，**违反依赖工作顺序门禁**。
> 2. 本次不仅记录结果，还新增了 Seed Admission 决策规则、抗体进入条件、17-target disposition、压力测试
>    与实验建议，属**实质性外部 policy／analysis 运行**，不能按「审计记录」事后放行。
> 3. **部分结论依赖未获批准的 #53 运行，单独批准 #54 无法洗净其上游来源。**
> 4. 外部产物缺少逐文件 SHA-256，无法从 GitHub 锁定确切审核对象。
> 5. **「不需要架构变化」只能作为待审核假设，不能依据未授权运行直接成为已确认结论。**
>
> ### 本次运行状态已改为 `UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`
>
> **不得作为任何后续工作的输入。** 明确不被接受的内容：
>
> - M2 Seed Admission Standard 的决策规则、类别准则与致命否决；
> - M4 抗体开发进入的 10 条条件；
> - M3 的 17 靶点 disposition；
> - M5 的压力测试判定与 `EXPLORATION`／`HOLD` 决策；
> - M6 的 14 条发现与**全部**实验建议；
> - **M1「不需要架构变化」的结论，已降级为未经验证的假设。**
>
> ### 第 5 条如何处理：降级而非撤回
>
> 原文把它写成已确认结论，且据此声称「本次不消耗月度架构修复额度」。两处均已更正：结论降为**待审核假设**，
> 并明确写出**月度额度是否被消耗同样未定**，不得以本 run 为据记为未使用。
>
> 保留而非撤回的理由：该映射是对照真实契约文件与 Gate 目录做出的，可独立复核。但**不得用它作为跳过架构
> 问题的依据，也不得引用它作为冻结已被论证的证据**。这正是审核第 5 条的要点——推导质量不能替代授权。
>
> ### 第 3 条：上游污染已具体标出
>
> 本运行**消费了** #53 运行的 anchor clinical context（MSS/pMMR mCRC 3L+ 与持久缩瘤收益）。M5 的
> AE-01 正是据此对三个靶点全部标为 `MET`。因此**即使本运行日后单独获得授权，AE-01 也不能视为 MET**；
> 必须先重跑并接受上游运行。已在两份外部 manifest 与两份 handoff 中互相记录。
>
> ### 解决路径（不走事后追认）
>
> 1. 本 run 隔离为审计证据；
> 2. **先**完成 #52 审计闭环（已于 2026-08-04 合并为 `985edf8`）；
> 3. **再**通过 #53 自己的 contract-only PR 与重跑解决上游运行；
> 4. **然后**为 Playbook 六模块另建独立 contract-only PR，预先冻结范围、规则语义、证据标准与输出验证；
> 5. 获 `APPROVE` 后重新执行。
>
> 下方为原始交接文本，保留不改，用于对照裁决前后的差异。

---

- 任务编号：`task_20260804_adc-seed-playbook-v0.1`
- 分支：`task_20260804_adc-seed-playbook-v0.1`（从 `main` `dcc94a7` 创建）
- 当前状态：`REQUEST_CHANGES_ADDRESSED_PENDING_RE_REVIEW`
- 外部 run 状态：`UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`（原记为 `draft_pending_repo_review`）
- 任务性质：外部运行留痕（audit record for an external run）
- 代码变更：`NO_CODE_CHANGE`
- Gate 变更：`NO_GATE_CHANGE`
- 测试变更：`NO_TEST_CHANGE`
- 契约变更：`NO_CONTRACT_CHANGE`
- 架构变更：`NO_ARCHITECTURE_CHANGE`（~~结论，非假设~~ → **已按审核第 5 条降级为待审核假设**，见顶部裁决声明）

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

> **本节标题与结论已被 2026-08-04 审核裁决第 5 条降级**（见本文件顶部裁决声明）。它现在是**待审核假设**，
> 不是已确认结论；**月度架构修复额度是否被消耗同样未定**，不得以本 run 为据记为未使用。原文保留以对照。

这一点关键，因为架构今日刚冻结、每月只有一次修复额度；而 playbook 自己的第七节也明确说「框架已经足够」、
当前更高价值的动作是跑通一个真实闭环而不是继续扩框架。两个约束方向一致。~~本次不消耗月度架构修复额度。~~
**更正：额度是否被消耗未定**，须待授权重跑后判定。

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

---

## 附录 A：外部产物 SHA-256（2026-08-04 补充，回应审核第 4 条）

在**全部隔离标记写入之后**计算，因此锁定的是被裁决为不接受的这一确切版本，可防静默替换。

外部目录：
`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_adc_seed_playbook_v0.1_20260804T201605Z/`

| 文件 | SHA-256 |
|---|---|
| `external_run_worklog.md` | `f550be77ece7537064ae2513667189c1eecf68b6a35dfdf6290cee8d622f7f23` |
| `m1_playbook_to_gate_map.tsv` | `e4e149cbb7a491b4e5fea8b55c8008b9fd05d286bda602d89573cc8bbe747613` |
| `m2_seed_admission_standard.tsv` | `c73029db10ba5c333aacf38c20fcdc92c0cacfe8052f5cd64213fcab66ef654d` |
| `m3_seed_discovery_sprint.tsv` | `bf170cb64f142afbcb913ef6c296e280e5383ce77921523d2251952601b63d72` |
| `m4_antibody_entry_threshold.tsv` | `e0cb309ddf667776c5971ab6047d0924e54f28ff22379e9bd353af55d92dab82` |
| `m5_three_target_stress_test.tsv` | `99d6a837c88cac76e821ec8501f80c9784c1b5d42ebfb289404678d47df6ebc7` |
| `m6_gate_decision_value.tsv` | `ccc1b3d058387d0f06965c23971a001220a62060a6ad556d2da8940472254d3f` |
| `run_report.md` | `15307f3fa46af521d9c297a3fec3da74870ebae3f6199caac3b1e5b2d8339cdf` |
| `source_manifest.json` | `29b0637b0bad928129927c81301ce8d0db49bdd22410d82731c0045ee33a458f` |

复核命令（在上述目录下执行）：`shasum -a 256 *`

## 附录 B：本次修订做了什么、没做什么

**做了：**

1. 外部 run `status` 与 `authorisation_status` 改为 `UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`，新增
   `quarantine` 块，逐条记录五项裁决、不被接受清单、上游污染与解决路径。
2. `source_manifest.json` 的 `headline_result.status` 改为 `UNVERIFIED_HYPOTHESIS_NOT_CONFIRMED`。
3. `run_report.md` 头部加入 QUARANTINE NOTICE；标题「The headline result」改为明示其为待审核假设；
   删去「不消耗月度修复额度」的断言；改写 Governance 一节。
4. 外部 `external_run_worklog.md` 追加 6 条时间戳记录。
5. 本 handoff 顶部**插入**裁决声明（原文一字未删），正文第 3 节与元数据行加入降级标注，补附录 A 校验和。
6. `logs/worklog.md` 追加一条记录本次裁决与修订。

**没做：**

- **没有事后追认该 run。**
- **没有撤回 M1 的映射内容**，只降级其效力。映射对照真实文件做出、可独立复核，销毁它会丢失可复核证据；
  但已明确禁止用它作为跳过架构问题或论证冻结的依据。
- 没有删除任何科学内容。隔离是标注不接受，不是销毁审计材料。
- **没有创建那两个 contract-only PR**（#53 上游的、以及本 Playbook 六模块的）。它们需要预先冻结范围与
  语义，属新范围，须另立任务授权；在本 PR 内顺手做掉正是本次被阻断的那类越界。
- 没有任何代码、契约、Gate 拓扑、Model、Profile、生命周期、核心对象或测试变更。

## 附录 C：分支事故与更正（2026-08-04）

本 PR 送审后、修订期间发生一次分支错置，如实记录：

- 人类负责人于 16:57 的提交 `108931b`（`target_safety_therapeutic_window_prescreen` GenModule，684 行）
  落在了 **#53 的分支**上，而其自身 worklog 记明本意是「从最新 `origin/main` 创建
  `task_20260804_target-safety-prescreen`」。随后 PR #55 在第二个指向同一提交的分支上创建，导致
  **#53 与 #55 内容完全相同**。
- 执行者的隔离修订提交也因共享工作树的 HEAD 在 `checkout` 与 `commit` 之间被移动而落在错误分支。
  **未推送到任何远端**（已核验），已先移至保留分支再复位，人类负责人的提交未受损。
- 经人类负责人授权后拆分：#53 分支重置为 `3a4462d` + 隔离修订（仅审计，2 文件）；#55 分支将
  `108931b` 变基到 `origin/main` 并去掉审计提交（仅模块，9 文件）。两次 `--force-with-lease`。
  恢复点已留存。
- 已采纳的预防措施：此后每次 `git add`／`commit` 前断言分支名，不匹配即中止。
- **另需人类负责人注意**：#55 新增了一个带自有 `contracts.py` 的 GenModule。在今日生效的架构冻结下，
  这属于需要显式提出的架构问题，不宜作为模块新增顺带通过。执行者不代为裁决。
