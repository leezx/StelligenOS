# ADC Pool Level 01 输入绑定与执行契约

- 任务分支：`task_20260804_adc-pool-level-01-input-binding`
- 前置工作包：PR #57（Level 01 判据定义），ChatGPT `APPROVE`
- 机器可读绑定：[`../pools/adc_pool_level_01_input_binding.yaml`](../pools/adc_pool_level_01_input_binding.yaml)，由 `tests/test_adc_pool_level_01_input_binding.py` 校验
- 当前状态：**contract-only，未执行，等待 ChatGPT 审核**

## 目的

解除 PR #57 的 `BLOCK-02`，把 Level 01 的两条原始轴与 linkage 证据绑定到**已获独立批准**的外部产物上，并冻结「来源状态 → LOCK 输出上限」的映射。

本文件**不执行 Level 01**，也**不授权任何新的枚举运行**。

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

**直接后果：本次执行只有 1 个 context 可以 `eligible`。** Eligible Universe Index 因此恰为 1 × 32 = 32 pairs（32 见第六节 LOCK-01 推导）。这个数字小，但它是「只用已批准证据」的真实结果。

## 六、LOCK-01：既有 disposition 列不可继承

`target_evidence_catalog.tsv` 已有 `disposition` 列，取值为 `benchmark`（19）／`candidate`（16）／`hold`（6）。

**这些不是 `CandidateFilterResult`，不得当作 LOCK-01 输出。** 它们由 PR #28 契约的五条最小筛选层产生，判据与 LOCK-01 不同；且全部 41 行的 `gate_score_status = not_scored_in_enumeration_run`、`gate_pass_status = not_assessed`。测试断言这三个标签与 `CandidateDisposition` 的取值无交集，避免混读。

### LOCK-01 的确定性推导

只允许一个来源、一个 dimension、一个判决字段。不是为了简洁，而是因为已批准层里只有这一个可判别字段。

- 来源：`target_evidence_units.tsv`，`dimension = surface_reachability`，按 `gene_symbol` 连接
- 判决字段：`evidence_locator`，实测取值只有两种——`transmembrane_segment_count`（32）与 `not_available`（9）
- **禁止参与推导的字段**：`disposition`、`gate_score_status`、`gate_pass_status`、`evidence_class`、`clinical_stage_max`、`internalization_status`、`normal_tissue_risk_status`

| ID | 条件 | outcome | disposition | 数量 |
|---|---|---|---|---|
| `L1-01` | `evidence_locator = transmembrane_segment_count` 且 `direction = supporting` | `eligible_surface_target` | RETAIN | **32** |
| `L1-02` | `evidence_locator = not_available` | `possible_surface_target` | DEFER | **9** |
| `L1-03` | 同一 gene 同时存在 supporting 与 opposing | `possible_surface_target` | DEFER | 0（本次空规则） |
| `L1-04` | 证据来源为 RNA 层面 | `possible_surface_target` | DEFER | 0（本次空规则） |

RETAIN 的证据基础只能是 `protein_topology_annotation`，白名单只有 `transmembrane_segment_count` 一个 locator，`rna_derived_locators_may_retain: false`。原始 statement 自述「supports a membrane-associated target hypothesis but does not prove tumor-cell surface exposure」——这正合 LOCK-01 的职责（身份与拓扑），证明肿瘤细胞表面可得是 Level 02 的 T7，不在本层。

**两个 outcome 本次不可用：**

- `not_surface_target`：要求阳性的 negative protein/topology 证据（注释为纯胞内、零跨膜段且无信号肽或 GPI 锚）。已批准层只有上述两种 locator，**没有任何一条断言某靶点不是表面蛋白**。因此本次执行不得排除任何靶点。
- `identity_unresolved`：要求一个身份解析结论字段，已批准层没有，无法区分「身份未解析」与「注释不可得」，故一律落 `possible_surface_target`。

完备性：32 + 9 = 41，全部靶点得到确定状态，**零自由裁量、零排除**。`VAL-B07`／`VAL-B08` 强制记录命中规则 ID 与 provenance，并禁止结果与旧 `disposition` 列存在函数依赖。

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

| 依据 | dimension | 判据 | 实测 supporting |
|---|---|---|---|
| `LB-expression` | `crc_prevalence` | `direction = supporting` | **0**（本次为空） |
| `LB-precedent` | `adc_precedent` | `direction = supporting` 且 `locator = clinical_adc_names;clinical_stage_max` | **33** |

`indication_fit` 在 41 行中全部为 CRC 范围（19 个 `CRC clinical benchmark in local ADC Index`、22 个 `CRC public literature/landscape candidate`），故该字段用于确认 CRC 归属，不用于区分。

| ID | 条件 | outcome | disposition |
|---|---|---|---|
| `LNK-01` | 命中任一依据，且该 context 为 `canonical_c0` | `linkage_evidence_exists` | RETAIN |
| `LNK-02` | 命中任一依据，但 context 为 derived 或 benchmark 亚群 | `linkage_unassessed` | DEFER |
| `LNK-03` | 未命中任何依据 | `linkage_unassessed` | DEFER |
| `LNK-04` | 未按规定范围完成检索 | `linkage_evidence_missing` | DEFER |

`LNK-02` 的理由是：疾病级证据不能建立亚群特异 linkage。这与第五节的 LOCK-02 上限相互独立，但结论一致——目前只有 canonical context 能走到 RETAIN。

测试断言**至少存在一个非空依据**，且每个依据的 `vacuous_this_run` 必须与其实测计数一致——若将来所有依据都变空，测试会直接失败，而不是静默产出空池。

**`no_known_linkage_after_complete_search` 本次不可用。** 该 outcome 要求 `search_complete = true` 与完整检索记录；既有证据包为 machine-extracted、专家复核只完成 2/20，检索范围未闭合。`VAL-B03` 禁止其出现在输出中。

### `DECISION-02`（请裁决）

**未经专家复核的 machine-extracted 证据，是否满足 LOCK-03 的「存在性」？** 本契约冻结为**满足**，但附两个硬约束：

1. 每个 pair 行必须携带 `linkage_evidence_review_status`；
2. linkage 证据仅为 `machine_extracted_requires_human_review` 的 pair 可进入 Level 01 active pool，但**不得晋级 Level 02**，直到该证据通过专家复核。

理由：LOCK-03 问的是「是否存在一项公开证据表明相关」，不问有效性，且每个单元都有 `source_id`、`source_path_or_url` 与 `evidence_locator` 可回溯；Level 01 的错误偏好是召回优先。被否决的替代方案是「只有专家复核通过的证据才满足」——那会让 41 个靶点里只剩 4 个可用，Level 01 报出接近空池，而每个靶点其实都有可回溯来源，反而失真。真正的质量判断留给 Level 02，届时 review status 就在表里。

若审核方认为应采用严格方案，改动只是把 `machine_extracted_evidence_satisfies_existence` 置为 `false`，规则与测试都已就位。

## 八、本契约授权与不授权

**授权：** 按本绑定执行 Level 01 一次，产出 PR #57 契约规定的五份产物。

**不授权：** 任何新的 context 或 target 枚举；任何靶点筛选排序、Tier 划分、资产推荐或实验建议；任何 Gate 执行或评分；endpoint 锁定或定量门槛；Level 02 与 Level 03；把被隔离运行的任何产物重新引入。

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

## 十、可以预见的结果形状（逐项可核对）

按第五至七节的规则算出，不是估计：

| 量 | 值 |
|---|---|
| Raw Enumeration Matrix | **369** |
| context 资格 | eligible **1**／hold **8**／superseded **0** |
| target 资格 | eligible **32**／hold **9**／killed **0** |
| Eligible Universe Index | **32**（1 × 32） |
| Pool Level 01 | active **27**／hold **5**／reactivation-eligible **0** |

`CNT-03` 对账：32 = 27 + 5 + 0。推导：1 个 canonical context × 32 个 LOCK-01 eligible target = 32 pair；其中 27 个命中 `LB-precedent`，走 `LNK-01` 得 active；其余 5 个未命中任何 linkage 依据，走 `LNK-03` 得 hold。

**执行结果必须逐项等于上表。任一项不符即视为执行偏离本契约。**

### 必须写进结果报告的结构性限制

**27 个 active pair 的 linkage 全部只有「已有临床 ADC 针对该靶点」这一类，没有任何一条 CRC 表达证据**——因为已批准层里 41 条 `crc_prevalence` 全是 `not_available`。`adc_precedent` 的原始 statement 也自述「precedent does not establish CRC efficacy or a safe therapeutic window for a new asset」。

因此 `active` 在本次执行中的含义仅是「存在一条可回溯的 CRC-scoped ADC precedent」，**不代表该靶点在 CRC 上有表达支持**。这一句必须原样出现在结果报告里，否则 active 会被误读。

真正的瓶颈是 CRC 表达证据缺口与**剩余 18 个专家复核批次**，不是漏斗设计——与 PR #54 M6「portfolio 受数据集限制而非 Gate 限制」一致，只是这次建立在已批准证据上。

## 十一、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行 Level 01。
- 本仓库不得写入候选池、快照、证据、cache、result 或 weights。
- `DECISION-02` 未获裁决前，执行者不得自行改用严格方案。
