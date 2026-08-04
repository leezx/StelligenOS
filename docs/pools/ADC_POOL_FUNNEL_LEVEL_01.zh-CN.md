# ADC Pool 漏斗 Level 01 定义与执行契约

- 任务分支：`task_20260804_adc-pool-level-01`
- 来源：`Zhixins-KB/2.Biotech/Asset-Generation-OS-architecture.md` 的 `# ADC pool漏斗gating` 一节（第 2–602 行，只读取未修改）
- 机器可读记录：[`adc_pool_gate_usage.yaml`](./adc_pool_gate_usage.yaml)，由 `tests/test_adc_pool_gate_usage.py` 校验
- 当前状态：**contract-only，未执行，等待 ChatGPT 审核**

## 目的

冻结 ADC Pool 漏斗 Level 01 的**定义、判据、顺序、语义、证据标准和输出验证**，并把本层使用了哪些判据写成可复核的机器可读记录。

本文件**不执行 Level 01**，不生成候选、不生成 pair、不生成 disposition、不排序、不推荐靶点。获得 `APPROVE` 后才可执行；执行产物全部留在外部工作区。

这一顺序是 2026-08-04 对 PR #53 与 #54 的审核裁决所要求的：先用 contract-only PR 预先冻结范围与语义，获批后再运行，**重跑产物才是被接受的产物**。本 PR 就是 Level 01 的那个前置契约。

## 一、Level 01 是什么

> **CRC ADC Candidate Universe v0.1：由公开可枚举膜蛋白 × 明确 CRC clinical contexts 构成的高召回候选池。**

必须按来源文档收紧口径：**Level 01 只能宣称是「当前公开知识下、按既定定义构建的高覆盖候选宇宙」，不得宣称是理论上所有 CRC indication–target pair。** 至少以下六类未来仍可能出现且不可由 gene-level surfaceome 枚举：新发现的膜蛋白或蛋白异构体、非经典膜相关抗原、肿瘤特异糖基化／剪切／构象表位、治疗诱导后才暴露的 target、正常组织存在但肿瘤中可达性异常的 target、复合物或非蛋白抗原。

Level 01 的目标不是准确，而是：尽量不漏、每个 pair 可追溯、可增量更新、后续由低成本判据快速压缩。因此本层的错误偏好明确是 **recall 优先于 precision**：宁可保留可疑候选，不要过早漏掉。

### 最小单元是 Clinical context × Target，不是 indication × target

Level 01 的一个候选是一个 pair，其 clinical context 至少包含 disease setting、line of therapy、molecular subgroup、treatment history、metastatic site 或 resistant context。

此时 **endpoint 不锁定**，只记录 intended clinical benefit、endpoint class、endpoint maturity、unresolved endpoint assumptions。若在 Level 01 就要求 protocol endpoint，本层会退化成临床方案设计，而不是候选枚举。这与 v5 的六级递进锁一致：Level 01 对应 `exploratory`／`provisional`，不对应 `protocol-locked`。

### Level 01 有三个对象，不是两个

来源文档区分了 Universe Index 与 Pool Level 01。但只分两层会让计数失去唯一的 denominator：被 `LOCK-01` 判为 `not_surface_target` 的靶点按定义就不属于「合格 surface targets」，被 `LOCK-02` 判为 `redundant_context` 的情境是否还算「合格 clinical contexts」也没有答案。**context 级资格结论、target 级资格结论与 pair 级池状态是三种不同粒度的对象，混进一个总和里就无法对账。** 因此本契约拆成三个：

| 对象 | 内容 | 用途 |
|---|---|---|
| **A. Raw Enumeration Matrix** | 所有被枚举、准备评估的 raw contexts × raw targets。**可以**包含 `undefined_context`、`redundant_context`、`not_surface_target`、`identity_unresolved` | 记录评估范围本身 |
| **B. Eligible Universe Index** | 只有通过两把身份资格锁的 eligible contexts × eligible surface targets | 证明覆盖范围 |
| **C. Pool Level 01** | Eligible Universe Index 经 `LOCK-03` 后的 pair 级状态：`active`／`hold`／`reactivation-eligible` | 真正进入后续层的候选 |

不做 B 与 C 的区分，就会把算力花在成千上万个毫无生物学关联的组合上，并让 `unknown` 淹没有意义的候选。**未进入 active pool 的 pair 不删除**，留在 Eligible Universe Index，状态为 `reactivation-eligible`。

### 状态词表按粒度分开

| 粒度 | 状态 | 由哪把锁赋值 |
|---|---|---|
| clinical context 级 | `eligible`／`hold`／`superseded` | `LOCK-02` |
| target 级 | `eligible`／`hold`／`killed` | `LOCK-01` |
| pair 级 | `active`／`hold`／`reactivation-eligible` | `LOCK-03` |

**`killed` 与 `superseded` 属资格审计历史，从不产生 pair 行，因此不参与 pair 级对账。** 一个 context 被 `superseded`，Eligible Universe Index 减少 `|eligible_targets|` 个 pair；一个 target 被 `killed`，减少 `|eligible_contexts|` 个 pair；两种情况下 Raw Enumeration Matrix 都不变——排除是审计记录，不是删除。

## 二、Level 01 运行的判据：三把锁，零个 Gate

**Level 01 运行的 Gate 数量是零。** 这不是省略，是本层的定义。本层只运行三把 eligibility lock，产出 `CandidateFilterResult`，按契约（`genmodules/gen_indication_endpoint_target/contracts.py`）**明确不是 Gate 结果**。本层不写任何 Gate 分数、不写任何 Gate 状态、不推进任何 Gate。

三把锁各自借用一个 Gate 的**职责**，但都不是该 Gate 的简化执行，也**不构成该 Gate 的 PASS**——来源文档第二节对 T7 亦明确「不能把它当成完整 T7 PASS」。

| 顺序 | Lock | 粒度 | 借用职责 | 该 Gate 的 catalogue cost_tier | 问的问题 |
|---|---|---|---|---|---|
| 1 | `LOCK-02` crc_clinical_context_eligibility | clinical context 级 | `clinical_context_endpoint`（T0） | `low` | 这个 CRC 临床情境是否真实存在、当前疗效或人群覆盖是否有明确不足、人群是否可界定、是否有大致 intended benefit |
| 2 | `LOCK-01` target_identity_eligibility | target 级 | `tumor_cell_surface_availability`（T7） | `medium` | 这个靶点是否存在有合理依据的细胞外可及蛋白形式，身份是否能映射到统一 gene/protein identifier |
| 3 | `LOCK-03` target_context_linkage_existence | pair 级 | `target_population_mapping`（T2） | `medium` | 是否至少存在一项公开证据表明该靶点与该 CRC 情境有关（不要求证明有效） |

### 为什么必须是锁而不是 Gate：一个可验证的依赖链理由

除了「Level 01 不该跑重 Gate」这个设计取舍之外，还有一个由仓库实测得到的硬理由：

```
tumor_cell_surface_availability (T7)
  └─ 依赖 target_population_mapping (T2)
       └─ 依赖 clinical_context_endpoint (T0), endpoint_driving_population (T1)
```

来源文档第五节明确要求 **T1 不适合作为 Level 01–03 的普遍筛选器**（代价高、定义困难，且会把系统拖回 cell-state-first）。而冻结拓扑要求按依赖顺序执行、不得跳过前置 Gate。因此**在不运行 T1 的前提下，Level 01 在结构上就不可能产生一个合法的 T7 结果**。把三把锁写成 `CandidateFilterResult` 不是为了图省事，而是唯一与冻结拓扑相容的表达方式。

### 每把锁的输出与 disposition 映射

`CandidateDisposition` 只有 `RETAIN`／`EXCLUDE`／`DEFER` 三值，无法区分两种性质完全不同的 EXCLUDE，因此每一行都必须同时记录 `disposition_semantics` 与 `resulting_state`，否则会丢信息（见 `GAP-P04`）：

- **`EXCLUDE_DEFINITIONALLY_INELIGIBLE`**：定义性不合格，落到 `killed` 或 `superseded`，**不可复活**。
- **`EXCLUDE_FROM_ACTIVE_POOL`**：只是移出 active pool，落到 `reactivation-eligible`，**不构成科学证伪**。

**LOCK-02 clinical context 级**

| 输出 | disposition | resulting_state | evidence_state | 排除依据 |
|---|---|---|---|---|
| `validated_unmet_context` | RETAIN | `eligible` | `present` | — |
| `plausible_unmet_context` | DEFER | `hold` | `absent_incomplete_search` | — |
| `redundant_context` | EXCLUDE（定义性） | `superseded` | `present` | 可判定的集合包含关系，必须写出取代它的 context 引用 |
| `weak_context` | DEFER | `hold` | `present` | — |
| `undefined_context` | DEFER | `hold` | `not_assessed` | — |

> **DEVIATION-01（需审核确认）**：来源文档把 weak 与 redundant 合成一个 `weak_or_redundant_context` 输出。本契约把它拆成两个。理由是二者的排除依据强度不同：`redundant` 是可判定的集合包含关系；`weak` 是价值判断，在一个以召回为先的层里不足以据此排除。若合并保留并映射为 EXCLUDE，本层就会因为价值判断而丢候选，直接违反它自己声明的错误偏好。这是本契约对来源文档唯一的实质偏离，明示以便审核方接受或否决。

**LOCK-01 target 级**

| 输出 | disposition | resulting_state | evidence_state | 排除依据 |
|---|---|---|---|---|
| `eligible_surface_target` | RETAIN | `eligible` | `present` | — |
| `possible_surface_target` | DEFER | `hold` | `absent_incomplete_search` | — |
| `not_surface_target` | EXCLUDE（定义性） | `killed` | `present` | 纯胞内蛋白不可能是 ADC 靶点 |
| `identity_unresolved` | DEFER | `hold` | `not_assessed` | — |

**LOCK-03 pair 级**

「没有发现 linkage」包含两种性质完全不同的情况，必须严格区分，否则执行者可以把普通的证据缺失编码成排除，直接改变 Pool Level 01 的规模。

| 输出 | disposition | resulting_state | evidence_state | 说明 |
|---|---|---|---|---|
| `linkage_evidence_exists` | RETAIN | `active` | `present` | — |
| `linkage_unassessed` | DEFER | `hold` | `not_assessed` | **尚未评估**，属证据缺失 |
| `linkage_evidence_missing` | DEFER | `hold` | `absent_incomplete_search` | **检索未达规定范围**，属证据缺失 |
| `no_known_linkage_after_complete_search` | EXCLUDE（仅 `EXCLUDE_FROM_ACTIVE_POOL`） | `reactivation-eligible` | `absent_after_complete_search` | **已按规定范围检索完毕仍无 linkage**，这是阳性检索结论，不是证据缺失 |

`no_known_linkage_after_complete_search` 的约束是硬性的：

- 它**只**表示移出 active pool，**不表示科学证伪**，`is_scientific_disproof: false`，`is_killed: false`。
- pair **留在 Eligible Universe Index**，状态恒为 `reactivation-eligible`，不得解读为 `killed`。
- 必须同时具备六项检索完整性记录：`search_complete`、`search_policy_ref`、`source_coverage_ref`、`search_scope`、`searched_at`、`search_policy_version`。**缺任何一项即不得输出本 outcome，必须退回 `linkage_evidence_missing`（DEFER）。**

### 录入规则

- pair 进入 active pool 的条件是**三把锁全部 RETAIN**。
- 任一锁 DEFER → `hold`。
- 任一锁定义性排除 → 该 context 或 target 不进入 Eligible Universe Index（`superseded` 或 `killed`）。
- `LOCK-03` 完整检索后无 linkage → pair 留在 Eligible Universe Index，状态 `reactivation-eligible`。

## 三、顺序原则

人类负责人的原则是「先用最低成本的高可信 gate 去筛，比较难的 gate 放到后面」。本契约把它落成两条可执行的判据。

**第一条：成本按「每淘汰一个候选的边际成本」衡量，而边际成本由作用粒度决定。**

淘汰一个 clinical context 会一次性移除候选矩阵的一整列，淘汰一个 target 移除一整行，pair 级判据每次只处理一格。因此顺序必然是 `clinical_context_level → target_level → pair_level`。这与来源文档第四节给出的 Level 01 顺序（clinical context eligibility → surface-target identity → minimal linkage）独立地一致，也解释了它为什么是对的。该约束由测试 `test_locks_run_cheapest_granularity_first` 机械保证，顺序退化会直接失败。

**第二条：便宜本身不够，必须同时具备否决力。**

这一条来自实测的反例，不是推理：45 个 Gate 中 cost_tier 为 `low` 的只有 T0 与 C40–C45 共 7 个，`competitive_position_entry_window`、`patent_landscape`、`preliminary_technical_fto` 全部是 `low`，**比 T2／T7／T11 的 `medium` 更便宜**。但来源文档第二节明确指出竞争拥挤不得单独 KILL——已有成功竞争者同时也是靶点与 modality 可行的证据。所以它们尽管最便宜，也不应排在最前，只能作 `deprioritize`／`conditional retain`／`differentiation required`。

因此「便宜优先」的完整表述是：**在阴性结果具有否决力的判据里，先跑边际成本最低的那个。**

## 四、Level 01 明确不做什么

`adc_pool_gate_usage.yaml` 的 `gates_not_run` 逐一列出全部 45 个 Gate，测试断言该清单与冻结拓扑完全相等。按来源文档第五节，其中以下几类**即使到 Level 02–03 也不适合作普遍筛选器**，此处一并记录，避免下一层重新讨论：

- `endpoint_driving_population`（T1）：代价高、定义困难，会把系统拖回 cell-state-first；只对进入 Level 03 的优先候选运行。
- `treatment_induced_state_response`（T5）：高度依赖具体 treatment context 与 longitudinal data，早期公开数据通常不足。
- `net_endpoint_benefit`（T6）：多个前置 Gate 的综合结果，不能作早期独立过滤器。
- `target_opportunity_decision`（T12）：阶段性聚合决策，不是 evidence Gate。既有内核的 `EarlyReductionSchedule` 也已硬性禁止调度 T12。
- **全部 16 个 P Gate**：需要具体 antibody／ADC construct。Level 01–03 还没有产品对象，不得提前假装运行；最多只能记录 anticipated product risk、design hypothesis、unresolved product requirement。
- **C46–C55（`blocking_claim_severity` 起共 10 个）**：进入真实资产开发后的商业／IP 深化，不属 universe filtering 阶段。

同时，Level 01 也不做：T1 的 cell population 精细建模、T3 intervention causality、T5 treatment-induced state、任何 P 系列、任何深度 IP／FTO。

## 五、证据标准

- **只用公开证据。**
- **RNA 证据不得满足 `LOCK-01`。** 这是仓库硬规则，无例外：RNA 不得当作蛋白层面验证。RNA 可以支持 `LOCK-03`——该锁只问「是否存在关联」，不问蛋白是否在表面——但必须标注 `rna_only`，且不得据此给出 `eligible_surface_target`。
- **模型领域知识单独不足以录入一个 pair。** 这与 `src/capabilities/target_candidate_generation.py` 的 `TargetCandidateGenerationPolicy` 一致，该契约已把 `permit_model_only_generation` 与 `permit_rule_only_generation` 硬编码为禁止。这也正是 PR #53 被阻断的那一点：未经原始来源验证的模型领域知识只能形成待验证假设，不支撑正式筛选排序。
- **证据缺失一律 DEFER，永不 EXCLUDE。** 「证据缺失」在本契约中严格限于两种 `evidence_state`：`not_assessed`（尚未评估）与 `absent_incomplete_search`（检索未达规定范围）。二者一律 DEFER，落到 `hold`。`null` 不得转为 0，缺失信息必须显式，`NOT_EVALUATED` 与 `UNRESOLVED` 全程保留、不得静默转成 PASS。
- **「已按规定范围检索完毕仍无 linkage」不属于证据缺失。** 它是一项阳性的检索结论（`evidence_state = absent_after_complete_search`），可以把 pair 移出 active pool，但**仅限于此**：语义只能是 `EXCLUDE_FROM_ACTIVE_POOL`，不构成科学证伪，不置为 `killed`，pair 留在 Eligible Universe Index 且恒为 `reactivation-eligible`，并必须附六项检索完整性记录。这条与上一条的界线是执行者唯一可以缩小 Pool Level 01 规模的地方，因此它由测试机械把守。

## 六、输出与验证

Level 01 必须产出**五份**外部产物，不得合并成一张表：Raw Enumeration Matrix、Context Eligibility Audit、Target Eligibility Audit、Eligible Universe Index、Pool Level 01 Snapshot。快照字段见 `adc_pool_gate_usage.yaml` 的 `snapshot_columns`（31 列），涵盖来源文档第六节要求的全部状态历史字段，外加 `LOCK-03` 的六项检索完整性记录。**候选即使被排除也不删除**，只改状态，取值限于对应粒度的词表。

执行后必须逐条验证，任一条不通过即不得提交结果 PR：

1. 每个 pair 都有三把锁各自的 outcome、disposition 与 `evaluation_status`；未评估的必须显式写 `NOT_EVALUATED`，不得留空。
2. `decision = RETAIN` 的行，三把锁必须全部 RETAIN。
3. 任何 EXCLUDE 行都必须有非空 `decision_reason_refs`，且其 `disposition_semantics` 与 `resulting_state` 与本契约第二节的映射表一致。
4. 所有证据引用都是可追溯的外部引用；仓库内不出现任何证据数据。
5. **凡 `evidence_state ∈ {not_assessed, absent_incomplete_search}` 的行，disposition 必须是 DEFER。** 出现任何一行以证据缺失为由 EXCLUDE，即为验证失败。
6. **凡输出 `no_known_linkage_after_complete_search` 的行，六项检索完整性字段必须齐备且 `search_complete = true`。** 缺任何一项即必须改回 `linkage_evidence_missing`。
7. 计数对账，五条恒等式全部成立：
   - `CNT-01`：`|raw_matrix| = |raw_contexts| × |raw_targets|`
   - `CNT-02`：`|eligible_universe_index| = |eligible_contexts| × |eligible_targets|`
   - `CNT-03`：`|eligible_universe_index| = |active| + |hold_pairs| + |reactivation_eligible_pairs|`
   - `CNT-04`：`|raw_contexts| = |eligible_contexts| + |hold_contexts| + |superseded_contexts|`
   - `CNT-05`：`|raw_targets| = |eligible_targets| + |hold_targets| + |killed_targets|`

   `killed` 与 `superseded` **不得**出现在 `CNT-03` 的求和里——它们是 context 级与 target 级的资格审计历史，从不产生 pair 行。
8. 输出中不出现任何 Gate 分数、Gate 状态或 Gate PASS/FAIL 字样。
9. 每个产物文件的 **SHA-256 逐文件记录**并写入结果 PR 的 handoff。这是 PR #53／#54 审核的第 3／4 条要求，此后为常规要求。
10. 结果 PR 在获得 ChatGPT `APPROVE` 前，不得发布任何排序、推荐或资产决策。

## 七、已记录但本次不解决的契约缺口

以下六条都是真实缺口。它们**没有在本 PR 中被实现**，因为架构已于 2026-08-04 冻结、每月最多一次积累修复，顺手实现正是前两轮被阻断的越界行为。

| ID | 缺口 | 影响层 |
|---|---|---|
| `GAP-P01` | 内核没有 pool level 身份或层级快照对象，来源文档第六节的状态历史目前只能以外部 TSV 表达 | 01 |
| `GAP-P02` | 内核没有 `active`／`hold`／`killed`／`superseded`／`reactivation-eligible` 这组 pool 生命周期状态 | 01 |
| `GAP-P03` | 内核没有 Raw Enumeration Matrix／Eligible Universe Index／Pool Level 01 这三个对象，也没有把 context 级与 target 级资格审计与 pair 级池状态分开的结构，故三对象与 `CNT-01`..`CNT-05` 只能靠外部产物加本注册表约束表达 | 01 |
| `GAP-P04` | `CandidateDisposition` 只有三值，无法表达来源文档四值 lock 输出与 Level 02 五值输出；尤其无法区分 `EXCLUDE_DEFINITIONALLY_INELIGIBLE`（`killed`／`superseded`）与 `EXCLUDE_FROM_ACTIVE_POOL`（`reactivation-eligible`，非科学证伪）。本契约靠 `disposition_semantics` 与 `resulting_state` 两个字段补足，属外部编码约定而非契约支持 | 01 |
| `GAP-P05` | `src/capabilities/early_t_gate_reduction.py` 的 `EarlyReductionSchedule` **强制 T2 先于 T7**，而来源文档第四节要求 Level 02 先跑 T7。既有内核与来源文档直接冲突 | 02 |
| `GAP-P06` | `EARLY_REDUCTION_GATE_IDS` 只含 T2/T7/T8/T9/T10/T11，不含任何 C Gate，故来源文档 Level 02 的 C2/C4/C5 quick scan 无法通过既有能力调度 | 02 |

`GAP-P05` 与 `GAP-P06` 属 Level 02，现在记录是因为它们在读取 Level 01 依赖时被发现，提前登记可避免下一层重新发现。

## 八、与既有仓库对象的对应关系

Level 01 的三把锁不需要任何新契约，可完全由既有对象表达。以下对应关系对照实际文件得出，可独立复核：

| Level 01 概念 | 既有仓库对象 |
|---|---|
| 锁的判定结果 | `CandidateFilterResult`（`filter_id` 承载 lock id；`filter_policy_ref` 必须是 `external:`） |
| 三值 disposition | `CandidateDisposition` |
| 未评估／未解决 | `EvaluationStatus` |
| clinical context | v5 `AnchorClinicalContext` + `IntendedBenefitHypothesis`，锁状态 `exploratory`／`provisional` |
| 「至少一项 linkage 证据」 | `TargetCandidateGenerationPolicy.minimum_distinct_positive_evidence_groups` |
| 笛卡尔积上限 | `TargetCandidateGenerationPolicy.maximum_candidates_per_clinical_frame`、`TargetCandidateGenerationRequest.candidate_budget` |
| 禁止模型单独生成 | `TargetCandidateGenerationPolicy.permit_model_only_generation = False`（契约层强制） |
| 证据出处 | `EvidenceRecord` |

按契约设计，`filter_policy_ref` 必须是 `external:`，因此**锁的具体数值门槛属于外部 policy，本仓库只冻结判据身份、顺序与语义**。本文件与 `adc_pool_gate_usage.yaml` 冻结的正是后者。

## 九、架构影响

本 PR 的改动只有五个文件：本文件、`adc_pool_gate_usage.yaml`、`tests/test_adc_pool_gate_usage.py`、一份 `docs/handoff/`、一条 `logs/worklog.md`。

未触碰：`src/`、`src/contracts/`、`genmodules/`、`genmodules/assetgenos_catalog/`、`extensions/`、`docs/architecture/`、`AGENTS.md`。未新增 Gate、未改 45-Gate 拓扑与身份、未改四阶段生命周期、未改八类核心对象、未改 `GateInputEnvelope@2.0.0` 与 `GateModelOutput@2.0.0`、未改任何 Model 或 Profile。可由 `git diff --stat main...HEAD` 直接核验。

据此，本 PR 不构成架构变更、不消耗 2026 年 8 月的月度架构修复额度。第七节六条缺口则确实是架构问题，**它们仍未解决**，需要独立任务与额度；本 PR 不代为裁决。

## 十、当前阻断

- `BLOCK-01`：本契约获得 ChatGPT `APPROVE` 前，**不得执行 Level 01**。
- `BLOCK-02`：`LOCK-02` 需要一份 CRC clinical context 清单，而目前唯一的枚举来自 2026-08-04 被隔离的运行（PR #53，`UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`），**按裁决不得作为任何后续工作的输入**。因此即使本契约获批，Level 01 仍不能执行，必须先按裁决重跑 CRC clinical frame 并被接受。这是隔离裁决的直接后果，此处明示而非绕过。
- 本仓库不得写入候选池、快照、证据、cache、result 或 weights。

## 十一、Level 02 与 Level 03 不在本 PR 范围内

人类负责人的指示是「先做 Level 01，审核完了再做下一个」。因此本 PR **不定义 Level 02 与 Level 03**，`adc_pool_gate_usage.yaml` 的 `defined_levels` 只有 `"01"`，并由测试断言 `defined_levels` 与 `levels` 条目一致。来源文档第八节给出的 Level 02／03 Gate 清单在本 PR 中**只作为 `GAP-P05`／`GAP-P06` 的上下文被引用，未被冻结为定义**。
