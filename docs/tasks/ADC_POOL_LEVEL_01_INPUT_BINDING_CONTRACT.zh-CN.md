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

**直接后果：本次执行最多只有 1 个 context 可以 `eligible`。** Eligible Universe Index 因此上限为 1 × |eligible_targets| ≤ 41 pairs。这个数字小，但它是「只用已批准证据」的真实结果。

## 六、LOCK-01：既有 disposition 列不可继承

`target_evidence_catalog.tsv` 已有 `disposition` 列，取值为 `benchmark`（19）／`candidate`（16）／`hold`（6）。

**这些不是 `CandidateFilterResult`，不得当作 LOCK-01 输出。** 它们由 PR #28 契约的五条最小筛选层产生，判据与 LOCK-01 不同；且全部 41 行的 `gate_score_status = not_scored_in_enumeration_run`、`gate_pass_status = not_assessed`。LOCK-01 必须独立推导。测试断言这三个标签与 `CandidateDisposition` 的取值无交集，避免混读。

## 七、LOCK-03：证据只有 target 级，这是硬上限

实测：292 个 evidence unit = 41 genes × 7 dimensions + 5 opposing。**没有 indication／context 列**，证据是 target 级、疾病级，不是 pair 级、亚群级。方向分布为 supporting 88／opposing 32／unknown 172，且 **292 个单元全部为 `machine_extracted_requires_human_review`**；20 个专家复核批次只完成 2 个，覆盖 4 个靶点。

据此冻结四条规则：

| ID | 条件 | outcome | disposition |
|---|---|---|---|
| `LNK-01` | `crc_prevalence` 单元存在且 `supporting`，且该 context 为 `canonical_c0` | `linkage_evidence_exists` | RETAIN |
| `LNK-02` | 同上但 context 为 derived 或 benchmark 亚群 | `linkage_unassessed` | DEFER |
| `LNK-03` | `crc_prevalence` 方向为 `unknown` 或不存在 | `linkage_unassessed` | DEFER |
| `LNK-04` | 未按规定范围完成检索 | `linkage_evidence_missing` | DEFER |

`LNK-02` 的理由是：疾病级证据不能建立亚群特异 linkage。这与第五节的 LOCK-02 上限相互独立，但结论一致——目前只有 canonical context 能走到 RETAIN。

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

## 十、可以预见的结果形状

按第五至七节的规则，本次执行的预期结果是：**1 个 `eligible` context，8 个 `hold`；active pool 上限 41 个 pair，全部集中在 canonical MSS/pMMR mCRC 3L+ 情境；其余 328 个 pair 落在 `hold`。**

这个池子很小，而且真正的瓶颈不在漏斗设计，在**剩余 18 个专家复核批次**——与 PR #54 M6「portfolio 受数据集限制而非 Gate 限制」的判断一致，只是这次结论建立在已批准证据上。此处预先写明，是为了避免结果出来后被误读为 Level 01 失效。

## 十一、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行 Level 01。
- 本仓库不得写入候选池、快照、证据、cache、result 或 weights。
- `DECISION-02` 未获裁决前，执行者不得自行改用严格方案。
