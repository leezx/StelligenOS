# Handoff：ADC Pool 漏斗 Level 01 定义与执行契约

- 日期：`2026-08-04`
- 任务分支：`task_20260804_adc-pool-level-01`
- 基线：`main` @ `e7092d5`
- 来源：`Zhixins-KB/2.Biotech/Asset-Generation-OS-architecture.md` 的 `# ADC pool漏斗gating`（第 2–602 行，只读取，未修改）
- 交付物类型：**contract-only**
- 外部运行：**无。本次没有执行任何外部运行，没有产生任何候选、pair、disposition、排序或推荐。**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（依据是 diff 范围，可由 `git diff --stat` 核验；见第六节）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次范围

人类负责人的指示是：读取来源文档的 ADC pool 漏斗 gating 一节，开始构建 ADC Pool，**先做 Level 01，审核完了再做下一个**；核心原理是先用一些 gate 锁定漏斗的最大可能性集合，再逐级加层、加入新 gate 逐级下筛；**每一个 Level 用了什么 gate 都要记录下来**，且先用最低成本的高可信 gate，较难的 gate 放到后面。

本次交付 Level 01 的**定义与执行契约**，不执行 Level 01。这个先后顺序是 2026-08-04 对 PR #53 与 #54 的审核裁决所要求的：先用 contract-only PR 预先冻结范围、语义、证据标准与输出验证，获 `APPROVE` 后再运行，重跑产物才是被接受的产物。本 PR 就是 Level 01 的那个前置契约。

候选池本身是数据，按仓库硬边界必须留在外部工作区；本仓库只冻结判据身份、顺序与语义。

## 二、仓库内交付了什么

三个文件，全部数据自由（data-free）：

| 文件 | 作用 |
|---|---|
| `docs/pools/ADC_POOL_FUNNEL_LEVEL_01.zh-CN.md` | Level 01 的完整定义与执行契约（面向操作者，中文） |
| `docs/pools/adc_pool_gate_usage.yaml` | **每层用了什么判据的权威机器可读记录**，即人类负责人要求「记录下来」的那份记录。每新增一层在 `levels` 下追加一个条目 |
| `tests/test_adc_pool_gate_usage.py` | 14 项校验，把上面那份记录钉在冻结的 45-Gate 拓扑与 `CandidateFilterResult` 语义上 |

## 三、Level 01 的核心结论

**Level 01 运行的 Gate 数量是零。** 它只运行三把 eligibility lock，产出 `CandidateFilterResult`——按契约明确不是 Gate 结果。三把锁各自借用一个 Gate 的**职责**，但都不构成该 Gate 的 PASS。

| 顺序 | Lock | 粒度 | 借用职责 |
|---|---|---|---|
| 1 | `LOCK-02` crc_clinical_context_eligibility | clinical context 级 | `clinical_context_endpoint`（T0，`low`） |
| 2 | `LOCK-01` target_identity_eligibility | target 级 | `tumor_cell_surface_availability`（T7，`medium`） |
| 3 | `LOCK-03` target_context_linkage_existence | pair 级 | `target_population_mapping`（T2，`medium`） |

`Universe Index`（完整笛卡尔积，用于证明覆盖范围）与 `Pool Level 01 active`（只有至少一项 linkage 证据的 pair）分成两层；未录入的 pair 不删除，状态为 `reactivation-eligible`。

## 四、关键设计决策

**1. 把「成本」定义为每淘汰一个候选的边际成本，而不是 catalogue 的 `cost_tier`。**
边际成本由判据的作用粒度决定：淘汰一个 clinical context 一次性移除候选矩阵的一整列，淘汰一个 target 移除一整行，pair 级判据每次只处理一格。因此顺序必然是 context 级 → target 级 → pair 级。这与来源文档第四节给出的 Level 01 顺序独立地一致，并解释了它为什么对。该约束由 `test_locks_run_cheapest_granularity_first` 机械保证，顺序退化即失败。

**2. 明确「便宜本身不够，必须同时具备否决力」。**
这条来自实测反例而非推理：45 个 Gate 中 `cost_tier = low` 的只有 7 个——T0 与 C40–C45。`competitive_position_entry_window`、`patent_landscape`、`preliminary_technical_fto` 全是 `low`，**比 T2／T7／T11 的 `medium` 更便宜**；但来源文档第二节明确竞争拥挤不得单独 KILL（已有成功竞争者同时也是靶点与 modality 可行的证据）。所以它们尽管最便宜也不能排在最前。完整表述是：**在阴性结果具有否决力的判据里，先跑边际成本最低的那个。**

**3. 每个锁输出必须同时记录 `pool_state`。**
`CandidateDisposition` 只有三值，来源文档的锁输出是四值，且第七节要求「无 linkage 的 pair 留在 Universe Index 不删除」——这是「未录入但仍存活」，既不是 EXCLUDE（已淘汰）也不是 DEFER（等证据）。只写 disposition 会丢信息，所以 12 个 outcome 全部同时写 `disposition` 与 `pool_state`，并登记为 `GAP-P04`。

**4. 每个 EXCLUDE 都必须写明排除依据，且只有定义性依据才允许排除。**
Level 01 的错误偏好是召回优先。因此只有 `not_surface_target`（纯胞内蛋白不可能是 ADC 靶点）与 `redundant_context`（可判定的集合包含关系）允许排除；`no_known_linkage` 虽记为 EXCLUDE，但 `pool_state` 强制为 `reactivation-eligible`，因为无关联证据不等于已证伪。由 `test_every_exclusion_declares_its_basis` 强制。

**5. `DEVIATION-01`（唯一的实质偏离，明示待审核方裁决）。**
来源文档把 weak 与 redundant 合成一个 `weak_or_redundant_context` 输出，本契约拆成 `redundant_context`（EXCLUDE）与 `weak_context`（DEFER）。理由：`redundant` 可判定，`weak` 是价值判断；若合并并映射为 EXCLUDE，本层就会因价值判断丢候选，直接违反它自己声明的错误偏好。明示以便审核方接受或否决，而不是静默改写来源文档。

## 五、对照仓库实测得到的发现

**发现 1（高）：在不运行 T1 的前提下，Level 01 在结构上不可能产生一个合法的 T7 结果。**
实测依赖链为 `tumor_cell_surface_availability → target_population_mapping → {clinical_context_endpoint, endpoint_driving_population}`。来源文档第五节明确 T1 不适合作 Level 01–03 的普遍筛选器，而冻结拓扑要求按依赖顺序执行、不得跳过前置 Gate。所以把三把锁写成 `CandidateFilterResult` 不是图省事，而是唯一与冻结拓扑相容的表达方式。这给来源文档「Level 01 不要跑完整 Gate」的设计取舍补上了一个硬理由。

**发现 2（高，属 Level 02，登记为 `GAP-P05`）：既有内核与来源文档在 Level 02 的 Gate 顺序上直接冲突。**
`src/capabilities/early_t_gate_reduction.py` 的 `EarlyReductionSchedule.__post_init__` 硬性要求 `gate_ids[:2] == (target_population_mapping, tumor_cell_surface_availability)`，即 **T2 必须先于 T7**；而来源文档第四节要求 Level 02 **先跑 T7**。二者不能同时成立，必须在定义 Level 02 时解决。现在登记，避免下一层重新发现。

**发现 3（中，属 Level 02，登记为 `GAP-P06`）：`EARLY_REDUCTION_GATE_IDS` 只含 T2/T7/T8/T9/T10/T11，不含任何 C Gate**，故来源文档 Level 02 的 C2/C4/C5 quick scan 无法通过既有能力调度。

**发现 4（中）：Level 01 的三把锁不需要任何新契约。**
对照实际文件得到的对应关系：锁结果 → `CandidateFilterResult`（`filter_id` 承载 lock id）；三值 → `CandidateDisposition`；未评估／未解决 → `EvaluationStatus`；clinical context → v5 `AnchorClinicalContext` + `IntendedBenefitHypothesis`；「至少一项 linkage 证据」→ `TargetCandidateGenerationPolicy.minimum_distinct_positive_evidence_groups`；笛卡尔积上限 → `maximum_candidates_per_clinical_frame` 与 `candidate_budget`；证据出处 → `EvidenceRecord`。

**发现 5（中）：契约层已经禁止「模型单独生成候选」。**
`TargetCandidateGenerationPolicy.__post_init__` 对 `permit_model_only_generation` 与 `permit_rule_only_generation` 一律抛错。这正是 PR #53 被阻断的那一点，已经是契约级强制，不只是 policy 约定。本契约据此把「模型领域知识单独不足以录入一个 pair」写入证据标准。

**发现 6（低）：`filter_policy_ref` 必须是 `external:`**，因此锁的具体数值门槛按契约设计属于外部 policy。本仓库只冻结判据身份、顺序与语义，这是设计使然而非让步。

## 六、架构影响

本 PR 改动五个文件：上述三个 + 本 handoff + 一条 `logs/worklog.md`。

未触碰：`src/`、`src/contracts/`、`genmodules/`、`genmodules/assetgenos_catalog/`、`extensions/`、`docs/architecture/`、`AGENTS.md`、`prompts/`。未新增 Gate、未改 45-Gate 拓扑与身份、未改四阶段生命周期、未改八类核心对象、未改 `GateInputEnvelope@2.0.0` 与 `GateModelOutput@2.0.0`、未改任何 Model 或 Profile。可由 `git diff --stat main...HEAD` 核验。

据此本 PR 不构成架构变更，不消耗 2026 年 8 月的月度架构修复额度。第七节的六条缺口确实是架构问题，**它们仍未解决**，需要独立任务与额度；执行者不代为裁决。

## 七、已记录但未解决的缺口

| ID | 缺口 | 影响层 |
|---|---|---|
| `GAP-P01` | 内核没有 pool level 身份或层级快照对象 | 01 |
| `GAP-P02` | 内核没有 `active`／`hold`／`killed`／`superseded`／`reactivation-eligible` 这组 pool 生命周期状态 | 01 |
| `GAP-P03` | 内核没有与 Pool Level 01 相区分的 Universe Index 对象 | 01 |
| `GAP-P04` | `CandidateDisposition` 三值不足以表达四值 lock 输出、Level 02 五值输出，以及「未录入但可复活」 | 01 |
| `GAP-P05` | `EarlyReductionSchedule` 强制 T2 先于 T7，与来源文档 Level 02 冲突 | 02 |
| `GAP-P06` | `EARLY_REDUCTION_GATE_IDS` 不含任何 C Gate | 02 |

## 八、明确没有做什么

- **没有执行 Level 01。** 没有枚举 clinical context、没有枚举 target、没有生成任何 pair、没有给出任何 disposition、没有排序、没有推荐。
- **没有定义 Level 02 与 Level 03。** `defined_levels` 只有 `"01"`，由测试断言与 `levels` 条目一致。来源文档第八节的 Level 02／03 Gate 清单只作为 `GAP-P05`／`GAP-P06` 的上下文被引用，未被冻结为定义。
- **没有实现第七节的六条缺口**，也没有为了让 Level 01「看起来完整」而私自扩展 `CandidateDisposition` 或新增 pool 生命周期枚举。
- **没有使用被隔离运行的任何产物。** PR #53 与 #54 的两次外部运行仍是 `UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`，其 20 个 unmet-need 场景、45 个靶点、Tier A 选择、payload 结论、Seed Admission Standard 与靶点 disposition **一条都没有被引用为输入或依据**。
- **没有修正一处已发现的无关缺陷。** `requirements.txt` 的注释写「the full suite (207 tests)」，实测为 228。这属于本次范围之外的改动，按第 25 条不在本 PR 内顺手改；此处记录，留待相关 PR 处理。
- 没有创建仍然欠着的两个 contract-only PR（#53 上游 CRC clinical frame 的、Playbook 六模块的），也没有补 #53／#54 的批准记录。二者都是独立范围。

## 九、验证结果

- `Ran 242 tests` 全部通过（`main` 基线 228 + 本次新增 14）。
- `scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- `git diff --check`：通过。
- 零 `__pycache__`（全程 `PYTHONDONTWRITEBYTECODE=1`）。
- **新增测试做过变异检验**，不是只看绿灯。5 个变异各自被捕获、随后精确回滚：把 `LOCK-02` 的 `borrowed_gate_cost_tier` 由 `low` 改成 `medium`（`FAILED`）；允许 RNA 满足 `LOCK-01`（`FAILED`）；从 `gates_not_run` 删掉 `transaction_readiness`（`FAILED`）；把 pair 级锁的 `run_order` 提到第一（`FAILED`）；删掉一个 EXCLUDE 的 `exclusion_basis`（`FAILED`）。回滚后与备份 `diff -q` 一致、测试恢复 `OK`。
- 数值对账：`snapshot_columns` 25 列、`gates_not_run` 45 项、3 把锁 12 个 outcome、6 条缺口、catalogue 中 `cost_tier = low` 的 Gate 7 个——全部由脚本实测，不是估计。

## 十、当前阻断

- `BLOCK-01`：本契约获 ChatGPT `APPROVE` 前，**不得执行 Level 01**。
- `BLOCK-02`：`LOCK-02` 需要一份 CRC clinical context 清单，而目前唯一的枚举来自被隔离的 PR #53 运行，按裁决不得作为任何后续工作的输入。**因此即使本契约获批，Level 01 仍不能执行**，必须先按裁决重跑 CRC clinical frame 并被接受。这是隔离裁决的直接后果，此处明示而非绕过。

## 十一、请审核方重点看的三点

1. `DEVIATION-01` 是否接受：把来源文档的 `weak_or_redundant_context` 拆成 `redundant_context`（EXCLUDE）与 `weak_context`（DEFER）。
2. 第六节的 `NO_ARCHITECTURE_CHANGE` 判断是否成立。这一次的依据是 diff 范围而非推导结论，与 PR #54 被降级的那个断言性质不同；若仍认为它只能是待审假设，请指出。
3. `BLOCK-02` 的处理是否正确：Level 01 的定义可以先冻结，但执行必须等 CRC clinical frame 重跑被接受。
