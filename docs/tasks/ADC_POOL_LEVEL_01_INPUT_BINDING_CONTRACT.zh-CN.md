# ADC Pool Level 01 输入绑定与执行契约

- 任务分支：`task_20260804_adc-pool-level-01-input-binding`
- 前置工作包：PR #57（Level 01 判据定义），ChatGPT `APPROVE`
- 机器可读绑定：[`../pools/adc_pool_level_01_input_binding.yaml`](../pools/adc_pool_level_01_input_binding.yaml)，由 `tests/test_adc_pool_level_01_input_binding.py` 校验
- 当前状态：**contract-only，未执行，等待 ChatGPT 审核**
- **授权范围：仅绑定 raw 轴。本契约不授权执行 Level 01**——被 `EVGAP-01`／`EVGAP-02` 两个证据缺口阻断，见第十节。

## 目的

解除 PR #57 的 `BLOCK-02`，把 Level 01 的两条原始轴与 linkage 证据绑定到**已获独立批准**的外部产物上，并冻结「来源状态 → LOCK 输出上限」的映射。

本文件**不执行 Level 01**，也**不授权任何新的枚举运行**。

**并且，经第二轮审核核实，本契约也不授权执行 Level 01。** 已批准证据包既不含 plasma-membrane 定位证据，也不含源级 CRC-specific linkage 证据，`LOCK-01` 与 `LOCK-03` 都无法产出任何 RETAIN。执行只会得到一份空的 Eligible Universe Index 与空的 pool 快照。缺口与所需的后续受控抽取见第十节。

## 一、关键发现：不需要重跑枚举

PR #57 的 `BLOCK-02` 写的是「唯一的 context 枚举来自被隔离的 2026-08-04 运行」。**这句话不准确，本契约予以更正。**

核实结果：2026-08-02 的枚举运行早已通过 **PR #29 `APPROVE`**，其批准记录明确写着

> Authorized: use external enumeration output as input to a new target-level evidence extraction task.

而 target 级证据抽取又通过 **PR #31 `APPROVE`**。因此存在一条完整的、未被隔离的输入链。`BLOCK-02` 的正确表述应是「不得使用 2026-08-04 那次运行的产物」，而不是「没有可用的 context」。

**后果：Level 01 不需要任何新的外部枚举运行，只需要一次 Level 01 自身的执行。** 原先估计的「两个契约 + 两次运行」缩减为「一个契约 + 一次运行」。

## 二、允许的输入

| 来源 | 授权 PR | 提供 | 规模 |
|---|---|---|---|
| `gen_iet_crc_target_enumeration_20260802` | #29 `APPROVE` | raw clinical contexts、raw targets | 9 indications（36 endpoint 行）、41 targets |
| `gen_iet_crc_target_evidence_20260801T2235EDT` | #31 `APPROVE` | linkage 证据 | 292 evidence units、41 genes |

7 + 3 个输入文件的 SHA-256 已逐一记录在绑定 YAML 中。**执行前必须逐个校验，任一不一致即中止。**

`indication_endpoint_target_pairs.tsv`（1,476 行）**不作为输入**：它按旧的 `indication + endpoint + target` 单元构建，而 Level 01 的单元是 `clinical context × target` 且 endpoint 不锁定。Level 01 自己生成 pair。

## 三、明确禁止的输入

| 来源 | 状态 | 禁止内容 |
|---|---|---|
| `gen_iet_crc_clinical_frame_and_membrane_target_screen_20260804T191053Z`（PR #53） | `UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED` | 20 个场景（11 个为新增）、45 个靶点（4 个为新增：GPA33、LY6G6D、TNFRSF12A、CEACAM6）、全部 disposition 与 Tier A、benefit ranking、endpoint 定量门槛、payload 类别结论 |
| `gen_iet_adc_seed_playbook_v0.1_20260804T201605Z`（PR #54） | `UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED` | Seed Admission Standard、17 靶点 disposition、抗体进入条件、压力测试判定、全部实验建议与架构结论 |

输出验证规则 `VAL-B06` 明确禁止上述四个仅存在于被隔离运行的靶点出现在结果中。

## 四、范围收缩，写明而不回避

| | 被隔离运行 | 本契约 |
|---|---|---|
| clinical contexts | 20 | **9** |
| targets | 45 | **41** |
| Raw Enumeration Matrix | — | **369 pairs**（9 × 41） |

Level 01 首次执行的范围因此小于那次被隔离的运行。**这是正确结果，不是退步**——差额正是未经授权扩大的那部分。

## 五、LOCK-02：来源状态决定 outcome 上限

实测 9 个 context 的来源状态：1 个 `canonical_c0`（confidence 0.93）、7 个 `derived_strategy`（`not_calibrated`）、1 个 `benchmark_subgroup`（`benchmark_only`）。

| 来源状态 | 校准 | outcome 上限 | disposition | 数量 |
|---|---|---|---|---|
| `canonical_c0` | calibrated | `validated_unmet_context` | RETAIN 可用 | 1 |
| `derived_strategy` | `not_calibrated` | `plausible_unmet_context` | **强制 DEFER** | 7 |
| `benchmark_subgroup` | `benchmark_only` | `weak_context` | **强制 DEFER** | 1 |

依据是 PR #28 契约自身的禁令：「不得将 derived strategy 自动升级为 canonical clinical fact」。此处继承，并由测试机械保证未校准来源不可能得到 RETAIN。

**直接后果：只有 1 个 context 可以 `eligible`。** 但 LOCK-01 给出 0 个 eligible target，故 Eligible Universe Index 为 1 × 0 = **0**，见第六节与第十节。

## 六、LOCK-01：既有 disposition 列不可继承

`target_evidence_catalog.tsv` 已有 `disposition` 列，取值为 `benchmark`（19）／`candidate`（16）／`hold`（6）。

**这些不是 `CandidateFilterResult`，不得当作 LOCK-01 输出。** 它们由 PR #28 契约的五条最小筛选层产生，判据与 LOCK-01 不同；且全部 41 行的 `gate_score_status = not_scored_in_enumeration_run`、`gate_pass_status = not_assessed`。测试断言这三个标签与 `CandidateDisposition` 的取值无交集，避免混读。

### LOCK-01 的确定性推导

**第二轮审核裁决：跨膜段证据不足以判定 `eligible_surface_target`，本契约已据此更正。** `transmembrane_segment_count` 只证明蛋白具有跨膜拓扑，不能单独证明位于质膜、存在细胞外结构域、表位可被抗体接近，也不能排除内质网／高尔基／线粒体等细胞器膜蛋白。而 PR #57 冻结的 LOCK-01 问题是「是否存在有合理依据的**细胞外可及蛋白形式**」。原映射把 32 个靶点判为 eligible，超过输入证据能支持的强度。

`eligible_surface_target` 现在要求**同时**满足三项，缺一不可，且全部要求蛋白层面来源：

| 要求 | 内容 |
|---|---|
| `RQ-01` | plasma-membrane localization |
| `RQ-02` | extracellular domain / topology |
| `RQ-03` | protein-level provenance |

| ID | 条件 | outcome | disposition | 数量 |
|---|---|---|---|---|
| `L1-01` | 同时满足 `RQ-01`＋`RQ-02`＋`RQ-03` | `eligible_surface_target` | RETAIN | **0**（本次空规则） |
| `L1-02` | 只有 `transmembrane_segment_count` supporting，无质膜定位与细胞外结构域证据 | `possible_surface_target` | DEFER | **32** |
| `L1-03` | `evidence_locator = not_available` | `possible_surface_target` | DEFER | **9** |
| `L1-04` | 注释指向细胞器膜，或定位证据冲突 | `possible_surface_target` | DEFER | 0（本次空规则） |
| `L1-05` | 同 gene 同时 supporting 与 opposing | `possible_surface_target` | DEFER | 0（本次空规则） |
| `L1-06` | 证据来源为 RNA 层面 | `possible_surface_target` | DEFER | 0（本次空规则） |

- 来源固定为 `target_evidence_units.tsv`／`dimension = surface_reachability`／按 `gene_symbol` 连接
- **禁止参与推导的字段**：`disposition`、`gate_score_status`、`gate_pass_status`、`evidence_class`、`clinical_stage_max`、`internalization_status`、`normal_tissue_risk_status`
- `retain_requirements_satisfiable_by_approved_inputs: false`。实测依据：`target_evidence_units.tsv` 中 `plasma membrane`／`extracellular`／`localization`／`signal peptide`／`GPI` 关键词命中数**均为 0**；`surface_reachability` 只有 `transmembrane_segment_count`(32) 与 `not_available`(9)。
- 原始 statement 自述「supports a membrane-associated target hypothesis but **does not prove tumor-cell surface exposure**」——这句话本身就说明它不足以 RETAIN。

**两个 outcome 仍然不可用**：`not_surface_target` 要求阳性的 negative protein/topology 证据，已批准层没有任何一条断言某靶点不是表面蛋白；`identity_unresolved` 要求身份解析结论字段，已批准层没有。

**完备性：41 = 32 (`L1-02`) + 9 (`L1-03`)，eligible = 0，killed = 0。** 零自由裁量、零排除，但也**零录入**。

## 六之二、36 行 → 9 个 clinical context 的确定性投影

PR #57 规定 Level 01 的单元是 `clinical context × target` 且 endpoint 不锁定，而输入是每 indication 4 行 endpoint。若不冻结投影规则，不同执行者都能产出「9 个 context」但 identity 与字段内容不同。以下规则消除该自由度。

- **身份**：`indication_id`，仅此一项。`clinical_context_ref = external:clinical-context/crc/{indication_id}`，只依赖 `indication_id`，故 endpoint 变化不改身份。
- **必须组内一致的 context 级字段**：`label`、`status`、`source`、`clinical_need`、`confidence`、`priority`。实测 9 个分组全部一致，无冲突行。
- **endpoint 折叠为 metadata，绝不锁定**：4 个 `endpoint_role`（`regulatory_ultimate`／`pivotal_supporting`／`early_adc_proof`／`supportive_exploratory`）折叠成 `endpoint_candidates`，保留 `endpoint_class`、`endpoint_maturity = not_locked_at_level_01`、`unresolved_endpoint_assumptions`；`endpoint`、`endpoint_role`、`rationale` 不进入 context 身份。
- **确定性**：按 `(indication_id, endpoint_role)` 排序，按 `(indication_id, endpoint_role, endpoint)` 去重。实测重复 role 对为 0。行序变化不改结果。
- **冲突与残缺**：`CTX-01` 组内字段取值不唯一、`CTX-02` `endpoint_role` 不足 4 种，两者都 → `undefined_context` DEFER `hold`。**不排除。**
- **provenance**：每个 context 记录其全部 `source_row_keys`，36 行必须全部被引用、无遗漏无重复（`VAL-B09`）。

测试用一份与真实 schema 同构的合成 fixture 实现上述规则并验证：36 行必得 9 个 context；正序、逆序、旋转输入结果完全相同；追加重复行不改结果；改一个 context 级字段值即走 `undefined_context`；删一个 endpoint 行同样走该路径且不影响其他 context；36 行与引用集合一一对应；改 endpoint 值不改任何 `clinical_context_ref`。

## 七、LOCK-03：证据只有 target 级，这是硬上限

实测：292 个 evidence unit = 41 genes × 7 dimensions + 5 opposing。**没有 indication／context 列**，证据是 target 级、疾病级，不是 pair 级、亚群级。方向分布为 supporting 88／opposing 32／unknown 172，且 **292 个单元全部为 `machine_extracted_requires_human_review`**；20 个专家复核批次只完成 2 个，覆盖 4 个靶点。

### 两类可接受的 linkage 依据

**实测发现，并据此更正了本契约初稿：41 条 `crc_prevalence` 单元全部 `direction = unknown`、`locator = not_available`**，原始 statement 自述「Target-specific CRC prevalence and malignant-cell/state prevalence were not harmonized in this run」。初稿把 LOCK-03 只绑到 `crc_prevalence` 一个 dimension，那会**保证 active pool 为空**。这是执行者的错误，由实测自查发现。

来源文档 Lock 3 列出的合格 linkage 形式本就包含「**已有 CRC preclinical 或 clinical targeting evidence**」，因此只绑表达类证据本身就是漏读来源文档。冻结两类依据：

| 依据 | dimension | 判据 | 实测 supporting | 实测**合格** |
|---|---|---|---|---|
| `LB-expression` | `crc_prevalence` | `direction = supporting` | 0 | **0** |
| `LB-precedent` | `adc_precedent` | `supporting` 且 `locator = clinical_adc_names;clinical_stage_max` **且源证据本身写明 CRC/colorectal indication** | 33 | **0** |

**第二轮审核裁决：泛癌 ADC precedent 不能直接证明 CRC linkage，本契约已据此收紧。** 「某靶点已有临床 ADC」可能发生在任何癌种，它最多证明该 target 具有 ADC modality precedent。`LB-precedent` 现在要求源证据本身包含 CRC/colorectal indication，或 CRC 细胞系／PDO／PDX／动物模型的 ADC/preclinical targeting 证据，并记录 `precedent_indication` 与 `source_locator`。仅在其他癌种中的 precedent 保留为 target/modality metadata（`LNK-02b`），**不满足 LOCK-03**。

`indication_fit` **不得替代**源级 CRC 证据（`LNK-02c`）：它只有两种 CRC-scoped 标签、对 41 行全部成立、不区分任何靶点，且属 catalog 派生判断；PR #57 已明确模型领域知识单独不足以录入 pair。

**实测结果：`measured_source_level_crc_units = 0`。** `adc_precedent` 的 33 条 supporting 单元实质主张都是「Local ADC Index contains ADC precedent for〈药名〉」，**不附任何 indication**。

> **一个必须记录的实测陷阱**：这 33 条 statement 全部含 "CRC" 字样，但只出现在免责句「precedent does not establish CRC efficacy or a safe therapeutic window」里。按「statement 是否包含 CRC」计数会得到 33/33，是假阳性。契约已写入 `measurement_trap`，禁止用该判据。

| ID | 条件 | outcome | disposition |
|---|---|---|---|
| `LNK-01` | 命中任一合格依据，且 context 为 `canonical_c0` | `linkage_evidence_exists` | RETAIN |
| `LNK-02` | 命中任一合格依据，但 context 为 derived／benchmark 亚群 | `linkage_unassessed` | DEFER |
| `LNK-02b` | 仅有其他癌种 ADC precedent，无源级 CRC indication | `linkage_unassessed` | DEFER |
| `LNK-02c` | 仅有 catalog 派生的 `indication_fit`，无源级 CRC 证据 | `linkage_unassessed` | DEFER |
| `LNK-03` | 未命中任何依据 | `linkage_unassessed` | DEFER |
| `LNK-04` | 未按规定范围完成检索 | `linkage_evidence_missing` | DEFER |

**两类依据本次都为空。** 测试据此断言：每个依据的 `vacuous_this_run` 必须与其**合格**计数一致（不是 supporting 计数——泛癌 precedent 是 supporting 但不合格）；且当没有任何依据合格时，`authorises_level_01_execution` **必须为 `false`**。这样全空的绑定会明确阻断执行，而不是静默产出空池。

**`no_known_linkage_after_complete_search` 本次不可用。** 该 outcome 要求 `search_complete = true` 与完整检索记录；既有证据包为 machine-extracted、专家复核只完成 2/20，检索范围未闭合。`VAL-B03` 禁止其出现在输出中。

### `DECISION-02`（请裁决）

**未经专家复核的 machine-extracted 证据，是否满足 LOCK-03 的「存在性」？** 本契约冻结为**满足**，但附两个硬约束：

1. 每个 pair 行必须携带 `linkage_evidence_review_status`；
2. linkage 证据仅为 `machine_extracted_requires_human_review` 的 pair 可进入 Level 01 active pool，但**不得晋级 Level 02**，直到该证据通过专家复核。

理由：LOCK-03 问的是「是否存在一项公开证据表明相关」，不问有效性，且每个单元都有 `source_id`、`source_path_or_url` 与 `evidence_locator` 可回溯；Level 01 的错误偏好是召回优先。被否决的替代方案是「只有专家复核通过的证据才满足」——那会让 41 个靶点里只剩 4 个可用，Level 01 报出接近空池，而每个靶点其实都有可回溯来源，反而失真。真正的质量判断留给 Level 02，届时 review status 就在表里。

若审核方认为应采用严格方案，改动只是把 `machine_extracted_evidence_satisfies_existence` 置为 `false`，规则与测试都已就位。

## 八、本契约授权与不授权

**授权：** 把 raw clinical context 轴与 raw target 轴绑定到 PR #29／#31 已批准的产物并固定 SHA-256；冻结 LOCK-01 推导、LOCK-02 状态上限、LOCK-03 linkage 依据与 clinical context 投影；记录 `EVGAP-01`／`EVGAP-02` 及其所需的后续受控抽取。

**不授权：** **执行 Level 01**（被 `EVGAP-01`／`EVGAP-02` 阻断）；任何证据抽取或检索运行；任何新的 context 或 target 枚举；任何靶点筛选排序、Tier 划分、资产推荐或实验建议；任何 Gate 执行或评分；endpoint 锁定或定量门槛；Level 02 与 Level 03；把被隔离运行的任何产物重新引入。

## 九、输出验证

继承 PR #57 契约的 10 条验证规则，另加 6 条：

| ID | 规则 |
|---|---|
| `VAL-B01` | 每个 context 行必须携带 `source_status` 与 `calibration`，LOCK-02 outcome 不得超过第五节上限 |
| `VAL-B02` | 每个 pair 行必须携带 `linkage_evidence_review_status`；仅 machine-extracted 的行必须标记不得晋级 Level 02 |
| `VAL-B03` | 输出中不得出现 `no_known_linkage_after_complete_search` |
| `VAL-B04` | Raw Enumeration Matrix 必须恰好 369 行 |
| `VAL-B05` | 每个输入文件的 SHA-256 必须与绑定记录一致，不一致即中止 |
| `VAL-B06` | 输出中不得出现 GPA33、LY6G6D、TNFRSF12A、CEACAM6 |

执行后每个产物文件仍须逐文件记录 SHA-256，并通过独立结果 PR 审核；`APPROVE` 前不得发布任何排序、推荐或资产决策。

## 十、按本绑定推算的结果，以及为什么不授权执行

| 量 | 值 |
|---|---|
| Raw Enumeration Matrix | **369** |
| context 资格 | eligible **1**／hold **8**／superseded **0** |
| target 资格 | eligible **0**／hold **41**／killed **0** |
| Eligible Universe Index | **0**（1 × 0） |
| Pool Level 01 | active **0**／hold **0**／reactivation-eligible **0** |

`CNT-02` 对账 1 × 0 = 0；`CNT-03` 对账 0 = 0 + 0 + 0。

LOCK-02 给出 1 个 eligible context，但 LOCK-01 给出 **0** 个 eligible target，故 Eligible Universe Index 为空，Level 01 不产生任何 pair 行。LOCK-03 的两类依据也都为空，即使 LOCK-01 通过也不会有 active。

**结论：已批准证据包无法支撑 Level 01 执行。** 执行只会产出一份空的 Eligible Universe Index 与空的 pool 快照，既无候选价值，又有被误读为「已筛完」的风险。因此本契约**只授权绑定 raw 轴**。

### 阻断执行的两个证据缺口

| ID | 阻断 | 缺什么 | 实测依据 | 所需后续运行 |
|---|---|---|---|---|
| `EVGAP-01` | `LOCK-01` | plasma-membrane 定位与 extracellular domain/topology 证据（蛋白层面） | `plasma membrane`／`extracellular`／`localization`／`signal peptide`／`GPI` 关键词命中数均为 0 | 受控的 target-surface localization evidence extraction |
| `EVGAP-02` | `LOCK-03` | 源级 CRC-specific linkage 证据 | `crc_prevalence` 41 条全 `not_available`；33 条 `adc_precedent` 均不附 indication；`indication_fit` 为 catalog 派生且对 41 行全部成立 | 受控的 CRC-specific target-context linkage evidence extraction |

两条缺口各自需要一次受控证据抽取运行，**各自走 contract-only PR 与 `APPROVE`**，都不在本 PR 的授权范围内。

## 十一、当前阻断

- **本契约获 `APPROVE` 后仍不得执行 Level 01**，直到 `EVGAP-01` 与 `EVGAP-02` 各自通过受控抽取补齐并被接受。
- 本仓库不得写入候选池、快照、证据、cache、result 或 weights。
- `DECISION-02` 未获裁决前，执行者不得自行改用严格方案。
