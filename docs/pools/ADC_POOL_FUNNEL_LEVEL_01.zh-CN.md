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

### Universe Index 与 Pool Level 01 是两层，不是一层

| | 内容 | 用途 |
|---|---|---|
| **Universe Index** | 所有可枚举 CRC clinical contexts × 所有合格 surface targets 的完整笛卡尔积 | 证明覆盖范围 |
| **Pool Level 01（active）** | 只有**至少存在一项 target–context linkage 证据**的 pair | 真正进入后续层的候选 |

不做这个区分，就会把算力花在成千上万个毫无生物学关联的组合上，并让 `unknown` 淹没有意义的候选。**未进入 active pool 的 pair 不删除**，留在 Universe Index，状态为 `reactivation-eligible`。

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

`CandidateDisposition` 只有 `RETAIN`／`EXCLUDE`／`DEFER` 三值，来源文档的锁输出是四值，因此每一行都必须同时记录 `pool_state`，否则会丢信息（见 `GAP-P04`）。

**LOCK-02 clinical context 级**

| 输出 | disposition | pool_state | 排除依据 |
|---|---|---|---|
| `validated_unmet_context` | RETAIN | `active` | — |
| `plausible_unmet_context` | DEFER | `hold` | — |
| `redundant_context` | EXCLUDE | `superseded` | 定义性（集合包含关系），必须写出取代它的 context 引用 |
| `weak_context` | DEFER | `hold` | — |
| `undefined_context` | DEFER | `hold` | — |

> **DEVIATION-01（需审核确认）**：来源文档把 weak 与 redundant 合成一个 `weak_or_redundant_context` 输出。本契约把它拆成两个。理由是二者的排除依据强度不同：`redundant` 是可判定的集合包含关系；`weak` 是价值判断，在一个以召回为先的层里不足以据此排除。若合并保留并映射为 EXCLUDE，本层就会因为价值判断而丢候选，直接违反它自己声明的错误偏好。这是本契约对来源文档唯一的实质偏离，明示以便审核方接受或否决。

**LOCK-01 target 级**

| 输出 | disposition | pool_state | 排除依据 |
|---|---|---|---|
| `eligible_surface_target` | RETAIN | `active` | — |
| `possible_surface_target` | DEFER | `hold` | — |
| `not_surface_target` | EXCLUDE | `killed` | 定义性（纯胞内蛋白不可能是 ADC 靶点） |
| `identity_unresolved` | DEFER | `hold` | — |

**LOCK-03 pair 级**

| 输出 | disposition | pool_state | 排除依据 |
|---|---|---|---|
| `linkage_evidence_exists` | RETAIN | `active` | — |
| `no_known_linkage` | EXCLUDE | `reactivation-eligible` | 无关联证据不等于已证伪；**留在 Universe Index，不删除** |
| `linkage_unassessed` | DEFER | `hold` | — |

### 录入规则

- pair 进入 active pool 的条件是**三把锁全部 RETAIN**。
- 任一锁 DEFER → `hold`。
- 任一锁 EXCLUDE → 未录入 active pool；按上表决定是 `killed`、`superseded` 还是 `reactivation-eligible`。

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
- **证据缺失一律 DEFER，永不 EXCLUDE。** `null` 不得转为 0，缺失信息必须显式，`NOT_EVALUATED` 与 `UNRESOLVED` 全程保留、不得静默转成 PASS。

## 六、输出与验证

Level 01 的输出是外部工作区的一份层级快照，字段见 `adc_pool_gate_usage.yaml` 的 `snapshot_columns`（25 列），涵盖来源文档第六节要求的全部状态历史字段。**候选即使被淘汰也不删除**，只改 `pool_state`，取值限于 `active`／`hold`／`killed`／`superseded`／`reactivation-eligible`。

执行后必须逐条验证，任一条不通过即不得提交结果 PR：

1. 每个 pair 都有三把锁各自的 outcome、disposition 与 `evaluation_status`；未评估的必须显式写 `NOT_EVALUATED`，不得留空。
2. `decision = RETAIN` 的行，三把锁必须全部 RETAIN。
3. 任何 EXCLUDE 行都必须有非空 `decision_reason_refs`，且其 `pool_state` 与本契约第二节的映射表一致。
4. 所有证据引用都是可追溯的外部引用；仓库内不出现任何证据数据。
5. 计数对账：`|Universe Index| = |active| + |hold| + |killed| + |superseded| + |reactivation-eligible|`，且 Universe Index 的 pair 数等于合格 context 数 × 合格 target 数。
6. 输出中不出现任何 Gate 分数、Gate 状态或 Gate PASS/FAIL 字样。
7. 每个产物文件的 **SHA-256 逐文件记录**并写入结果 PR 的 handoff。这是 PR #53／#54 审核的第 3／4 条要求，此后为常规要求。
8. 结果 PR 在获得 ChatGPT `APPROVE` 前，不得发布任何排序、推荐或资产决策。

## 七、已记录但本次不解决的契约缺口

以下六条都是真实缺口。它们**没有在本 PR 中被实现**，因为架构已于 2026-08-04 冻结、每月最多一次积累修复，顺手实现正是前两轮被阻断的越界行为。

| ID | 缺口 | 影响层 |
|---|---|---|
| `GAP-P01` | 内核没有 pool level 身份或层级快照对象，来源文档第六节的状态历史目前只能以外部 TSV 表达 | 01 |
| `GAP-P02` | 内核没有 `active`／`hold`／`killed`／`superseded`／`reactivation-eligible` 这组 pool 生命周期状态 | 01 |
| `GAP-P03` | 内核没有与 Pool Level 01 相区分的 Universe Index 对象，「未录入但仍存活」只能靠 `pool_state` 字段承载 | 01 |
| `GAP-P04` | `CandidateDisposition` 只有三值，无法表达来源文档四值 lock 输出与 Level 02 五值输出，也无法区分「淘汰」与「未录入但可复活」 | 01 |
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
