# Handoff：ADC Pool Level 01 输入绑定与执行契约

- 日期：`2026-08-04`
- 任务分支：`task_20260804_adc-pool-level-01-input-binding`
- 基线：`main` @ `5e0458b`
- 前置：PR #57（Level 01 判据定义），已 `APPROVE` 并合并
- 交付物类型：**contract-only**
- 外部运行：**无。没有执行任何运行，没有产生任何 context、target、pair、disposition 或排序。**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（依据是 diff 范围，可由 `git diff --stat` 核验）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次范围

人类负责人要求给出 Level 01 的最终 output。核实后发现 Level 01 从未执行——PR #57 合并的是定义，不是结果，且 `BLOCK-02` 挡着执行。人类负责人选择「先起 CRC context 契约 PR」。

本次交付那个契约。但核实过程改变了它的形状，见下一节。

## 二、关键发现：不需要重跑枚举，`BLOCK-02` 的表述本身不准确

PR #57 的 `BLOCK-02` 写的是「唯一的 context 枚举来自被隔离的 2026-08-04 运行」。**这句话不准确，本 PR 予以更正。**

核实结果：2026-08-02 的枚举运行早已通过 **PR #29 `APPROVE`**，批准记录 `logs/chatgpt-review-2026-08-02-crc-target-enumeration-results-final.md` 明确写着「Authorized: use external enumeration output as input to a new target-level evidence extraction task」；target 级证据抽取又通过 **PR #31 `APPROVE`**。所以存在一条完整的、未被隔离的输入链。

`BLOCK-02` 的正确表述是「不得使用 2026-08-04 那次运行的产物」，而不是「没有可用的 context」。我原先把「被隔离」误推为「无可用输入」，那是一次过度推广，与我在 PR #53 上犯过的「把针对 `ff943e7` 的检查推广成全局结论」是同一类错误。

**后果：Level 01 不需要任何新的外部枚举运行。** 原先我告诉人类负责人的「两个契约 + 两次运行」缩减为「一个契约 + 一次 Level 01 执行」。

## 三、仓库内交付了什么

| 文件 | 作用 |
|---|---|
| `docs/tasks/ADC_POOL_LEVEL_01_INPUT_BINDING_CONTRACT.zh-CN.md` | 输入绑定与执行契约（面向操作者，中文） |
| `docs/pools/adc_pool_level_01_input_binding.yaml` | 机器可读绑定：允许来源＋SHA-256、禁止来源、状态上限、linkage 规则、输出验证 |
| `tests/test_adc_pool_level_01_input_binding.py` | 13 项校验，把绑定钉在已合并的 Level 01 契约与实际存在的批准记录上 |

## 四、绑定的输入

| 来源 | 授权 PR | 提供 | 实测规模 |
|---|---|---|---|
| `gen_iet_crc_target_enumeration_20260802` | #29 `APPROVE` | raw contexts、raw targets | 9 indications（36 endpoint 行）、41 targets |
| `gen_iet_crc_target_evidence_20260801T2235EDT` | #31 `APPROVE` | linkage 证据 | 292 units、41 genes |

10 个输入文件的 SHA-256 逐一记录，执行前必须校验，任一不一致即中止（`VAL-B05`）。

`indication_endpoint_target_pairs.tsv`（1,476 行）**不作为输入**——它按旧的 `indication + endpoint + target` 单元构建，而 Level 01 的单元是 `clinical context × target` 且 endpoint 不锁定。

两次被隔离的运行（#53、#54）明确列为 `barred_sources`，逐条写出禁止内容；`VAL-B06` 禁止那 4 个仅存在于被隔离运行的靶点出现在输出里。

## 五、三条实测得到的硬约束

**1. LOCK-02：最多只有 1 个 context 能 `eligible`。**
实测 9 个 context 的来源状态是 1 个 `canonical_c0`（confidence 0.93）、7 个 `derived_strategy`（`not_calibrated`）、1 个 `benchmark_subgroup`（`benchmark_only`）。PR #28 契约自身禁止「把 derived strategy 自动升级为 canonical clinical fact」，此处继承为 outcome 上限：未校准来源**强制 DEFER**，由测试机械保证不可能得到 RETAIN。所以 Eligible Universe Index 上限是 1 × |eligible_targets| ≤ 41 pairs。

**2. LOCK-01：既有 `disposition` 列不可继承。**
`target_evidence_catalog.tsv` 的 `disposition` 取值是 `benchmark`（19）／`candidate`（16）／`hold`（6）——不是 `CandidateFilterResult`。它们由 PR #28 的五条最小筛选层产生，判据与 LOCK-01 不同，且 41 行的 `gate_score_status` 全为 `not_scored_in_enumeration_run`、`gate_pass_status` 全为 `not_assessed`。测试断言这三个标签与 `CandidateDisposition` 取值无交集，防止混读。

**3. LOCK-03：证据只有 target 级、疾病级，不是 pair 级、亚群级。**
实测 292 units = 41 genes × 7 dimensions + 5 opposing，**没有 indication／context 列**；方向为 supporting 88／opposing 32／unknown 172；**292 个单元全部 `machine_extracted_requires_human_review`**，20 个专家复核批次只完成 2 个、覆盖 4 个靶点。因此疾病级证据只能支撑 canonical context，不能建立亚群特异 linkage（`LNK-02`）。`no_known_linkage_after_complete_search` 本次不可用，因为检索范围未闭合（`VAL-B03` 禁止其出现）。

## 六、`DECISION-02`（请审核方裁决）

**未经专家复核的 machine-extracted 证据是否满足 LOCK-03 的存在性？** 冻结为**满足**，附两条硬约束：每个 pair 必须携带 `linkage_evidence_review_status`；只有 machine-extracted 证据的 pair 可进 Level 01 active pool 但**不得晋级 Level 02**，直到通过专家复核。

理由：LOCK-03 问存在性不问有效性，每个单元都有 `source_id`／`source_path_or_url`／`evidence_locator` 可回溯，且 Level 01 召回优先。被否决的替代方案是「只有专家复核通过才算」——那 41 个靶点只剩 4 个可用，Level 01 报出接近空池，而每个靶点其实都有可回溯来源，反而失真。质量判断留给 Level 02，届时 review status 就在表里。

若审核方要严格方案，只需把 `machine_extracted_evidence_satisfies_existence` 置 `false`，规则与测试都已就位。

## 七、可以预见的结果形状（预先写明，避免误读）

按上述规则，执行后的预期是：**1 个 `eligible` context、8 个 `hold`；active pool 上限 41 个 pair，全部集中在 canonical MSS/pMMR mCRC 3L+；其余 328 个 pair 落 `hold`。**

池子很小，真正的瓶颈不在漏斗设计，在**剩余 18 个专家复核批次**。这与 PR #54 M6「portfolio 受数据集限制而非 Gate 限制」一致，只是这次建立在已批准证据上。预先写明是为了避免结果出来后被误读为 Level 01 失效。

## 八、明确没有做什么

- **没有执行 Level 01**，没有任何 context、target、pair、disposition、排序或推荐。
- 没有新的枚举运行；没有抓取文献、下载数据或运行分析。
- 没有引用两次被隔离运行的任何产物。
- 没有定义 Level 02／03；没有实现 PR #57 记录的六条缺口（`GAP-P01`..`GAP-P06`）。
- 没有改 `BLOCK-02` 在 PR #57 文件里的原文——那是已获批准的历史记录，更正写在本 PR，不回写历史。
- **没有补 #52／#53／#54／#57 的批准记录。** 人类负责人先要 Level 01，那件事中断在事实收集阶段、未写任何文件。已查明的事实一并留在这里，避免重做：#52 也没有记录（原以为只缺三份）；**四个 PR 在 GitHub 上都没有 review 记录**（`/reviews` 返回空）；已批准 head 与 merge commit 分别是 #52 `bfc04be`／`985edf8`、#53 `5318eca`／`09990c8`、#54 `8992563`／`58984e7`、#57 `6036c01`／`5e0458b`，其中 #54 与 #57 的合并 head 与获批 head 不同，差异都只是 main 经合并进入。四轮转述评审的逐字文本可从会话 transcript 恢复。
- 没有修 `requirements.txt` 注释里过期的「207 tests」（实测 264）。仍属无关改动。

## 九、验证结果

- `Ran 264 tests` 全部通过（`main` 基线 251 + 本次新增 13）。
- `scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- `git diff --check`：通过；零 `__pycache__`。
- 所有规模数字均由脚本读取外部产物实测：9 contexts、41 targets、369 pairs、36 endpoint 行、292 evidence units、41 genes、7 dimensions、supporting/opposing/unknown = 88/32/172、专家复核 2/20 批次覆盖 4 靶点、`cost_tier = low` 的 Gate 7 个。
- 10 个输入文件的 SHA-256 由 `shasum -a 256` 实算。

## 十、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行 Level 01。
- `DECISION-02` 未获裁决前，执行者不得自行改用严格方案。
- 本仓库不得写入候选池、快照、证据、cache、result 或 weights。
