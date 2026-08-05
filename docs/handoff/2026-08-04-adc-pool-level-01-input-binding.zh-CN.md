# Handoff：ADC Pool Level 01 输入绑定与执行契约

- 日期：`2026-08-04`
- 任务分支：`task_20260804_adc-pool-level-01-input-binding`
- 基线：`main` @ `5e0458b`
- 前置：PR #57（Level 01 判据定义），已 `APPROVE` 并合并
- 交付物类型：**contract-only**
- 授权范围：**仅绑定 raw 轴，不授权执行 Level 01**（第二轮审核后降级，见第十二节）
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
| `tests/test_adc_pool_level_01_input_binding.py` | 32 项校验，把绑定钉在已合并的 Level 01 契约与实际存在的批准记录上 |

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
实测 9 个 context 的来源状态是 1 个 `canonical_c0`（confidence 0.93）、7 个 `derived_strategy`（`not_calibrated`）、1 个 `benchmark_subgroup`（`benchmark_only`）。PR #28 契约自身禁止「把 derived strategy 自动升级为 canonical clinical fact」，此处继承为 outcome 上限：未校准来源**强制 DEFER**，由测试机械保证不可能得到 RETAIN。但 LOCK-01 给出 0 个 eligible target（见第十二节），故 Eligible Universe Index 为 1 × 0 = **0**。

**2. LOCK-01：既有 `disposition` 列不可继承。**
`target_evidence_catalog.tsv` 的 `disposition` 取值是 `benchmark`（19）／`candidate`（16）／`hold`（6）——不是 `CandidateFilterResult`。它们由 PR #28 的五条最小筛选层产生，判据与 LOCK-01 不同，且 41 行的 `gate_score_status` 全为 `not_scored_in_enumeration_run`、`gate_pass_status` 全为 `not_assessed`。测试断言这三个标签与 `CandidateDisposition` 取值无交集，防止混读。

**3. LOCK-03：证据只有 target 级、疾病级，不是 pair 级、亚群级。**
实测 292 units = 41 genes × 7 dimensions + 5 opposing，**没有 indication／context 列**；方向为 supporting 88／opposing 32／unknown 172；**292 个单元全部 `machine_extracted_requires_human_review`**，20 个专家复核批次只完成 2 个、覆盖 4 个靶点。因此疾病级证据只能支撑 canonical context，不能建立亚群特异 linkage（`LNK-02`）。`no_known_linkage_after_complete_search` 本次不可用，因为检索范围未闭合（`VAL-B03` 禁止其出现）。

## 六、`DECISION-02`（请审核方裁决）

**未经专家复核的 machine-extracted 证据是否满足 LOCK-03 的存在性？** 冻结为**满足**，附两条硬约束：每个 pair 必须携带 `linkage_evidence_review_status`；只有 machine-extracted 证据的 pair 可进 Level 01 active pool 但**不得晋级 Level 02**，直到通过专家复核。

理由：LOCK-03 问存在性不问有效性，每个单元都有 `source_id`／`source_path_or_url`／`evidence_locator` 可回溯，且 Level 01 召回优先。被否决的替代方案是「只有专家复核通过才算」——那 41 个靶点只剩 4 个可用，Level 01 报出接近空池，而每个靶点其实都有可回溯来源，反而失真。质量判断留给 Level 02，届时 review status 就在表里。

若审核方要严格方案，只需把 `machine_extracted_evidence_satisfies_existence` 置 `false`，规则与测试都已就位。

## 七、可以预见的结果形状（预先写明，避免误读）

**本节已被第十二节取代。** 第二轮审核后的推算是：Raw Enumeration Matrix **369**；context 资格 eligible **1**／hold **8**；target 资格 eligible **0**／hold **41**／killed **0**；Eligible Universe Index **0**；Pool Level 01 active **0**。`CNT-02` 对账 1 × 0 = 0，`CNT-03` 对账 0 = 0 + 0 + 0。这不是一次被授权运行的预期产物，而是**不授权执行的理由**。

池子很小，真正的瓶颈不在漏斗设计，在**剩余 18 个专家复核批次**。这与 PR #54 M6「portfolio 受数据集限制而非 Gate 限制」一致，只是这次建立在已批准证据上。预先写明是为了避免结果出来后被误读为 Level 01 失效。

## 八、明确没有做什么

- **没有执行 Level 01**，没有任何 context、target、pair、disposition、排序或推荐。
- 没有新的枚举运行；没有抓取文献、下载数据或运行分析。
- 没有引用两次被隔离运行的任何产物。
- 没有定义 Level 02／03；没有实现 PR #57 记录的六条缺口（`GAP-P01`..`GAP-P06`）。
- 没有改 `BLOCK-02` 在 PR #57 文件里的原文——那是已获批准的历史记录，更正写在本 PR，不回写历史。
- **没有补 #52／#53／#54／#57 的批准记录。** 人类负责人先要 Level 01，那件事中断在事实收集阶段、未写任何文件。已查明的事实一并留在这里，避免重做：#52 也没有记录（原以为只缺三份）；**四个 PR 在 GitHub 上都没有 review 记录**（`/reviews` 返回空）；已批准 head 与 merge commit 分别是 #52 `bfc04be`／`985edf8`、#53 `5318eca`／`09990c8`、#54 `8992563`／`58984e7`、#57 `6036c01`／`5e0458b`，其中 #54 与 #57 的合并 head 与获批 head 不同，差异都只是 main 经合并进入。四轮转述评审的逐字文本可从会话 transcript 恢复。
- 没有修 `requirements.txt` 注释里过期的「207 tests」（实测 283）。仍属无关改动。

## 九、验证结果

- `Ran 283 tests` 全部通过（`main` 基线 251 + 本次新增 32）。
- `scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- `git diff --check`：通过；零 `__pycache__`。
- 所有规模数字均由脚本读取外部产物实测：9 contexts、41 targets、369 pairs、36 endpoint 行、292 evidence units、41 genes、7 dimensions、supporting/opposing/unknown = 88/32/172、专家复核 2/20 批次覆盖 4 靶点、`cost_tier = low` 的 Gate 7 个。
- 10 个输入文件的 SHA-256 由 `shasum -a 256` 实算。

## 十、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行 Level 01。
- `DECISION-02` 未获裁决前，执行者不得自行改用严格方案。
- 本仓库不得写入候选池、快照、证据、cache、result 或 weights。

## 十一、第一轮审核裁决与修订（`REQUEST_CHANGES`，2026-08-04）

ChatGPT 对 PR #58（HEAD `8f5c85d`）返回 `REQUEST_CHANGES`，两条阻断**全部接受**。已在同一 PR 内做最小修订，未夹带无关改动。

### 阻断 1（接受）：LOCK-01 没有真正绑定到可执行证据

原契约只写「LOCK-01 必须独立推导」，没说怎么推导。审核方指出后果是实质的：41 个靶点最终有多少 eligible／hold／killed 取决于执行者自由解释，不可复现；而本 PR 又不授权新的检索，所以绑定只证明了「有 41 个 raw targets」，没证明能完成 LOCK-01。

先核实已批准层里到底有没有蛋白层面表面证据，再决定是补 mapping 还是降级授权。**结论是补 mapping**：`surface_reachability` 有 32 条来自 `transmembrane_segment_count` 的蛋白拓扑注释（direction `supporting`），9 条 `not_available`。

新增 `lock_01_derivation`：单一来源 `target_evidence_units.tsv`／`dimension = surface_reachability`／按 `gene_symbol` 连接／判决字段 `evidence_locator`；`barred_fields` 列出 7 个禁止参与推导的字段（含 `disposition`、`gate_score_status`、`gate_pass_status`）；RETAIN 白名单只有 `transmembrane_segment_count`，`rna_derived_locators_may_retain: false`；四条规则 `L1-01`..`L1-04`，缺失、冲突、RNA 一律 DEFER。

**两个 outcome 声明为本次不可用**：`not_surface_target` 需要阳性的 negative topology 证据，已批准层没有任何一条断言某靶点不是表面蛋白，故**本次不得排除任何靶点**；`identity_unresolved` 需要身份解析结论字段，已批准层没有。完备性 32 + 9 = 41，零自由裁量、零排除。另加 `VAL-B07`／`VAL-B08`。

  > **本段的 32 eligible 已被第十二节推翻。** 第二轮审核裁定跨膜段不足以判 eligible，现值为 **0 eligible + 41 hold + 0 killed**。原文保留以对照裁决前后差异。

### 阻断 2（接受）：36 endpoint rows → 9 clinical contexts 的转换规则未冻结

审核方指出 369 的算术没问题但语义不唯一——不同执行者都能产出 9 个 context 而 identity 与字段内容不同。

新增 `clinical_context_projection`：身份只由 `indication_id` 决定；`context_ref_template = external:clinical-context/crc/{indication_id}`；6 个 context 级字段必须组内一致（实测 9 个分组全部一致）；4 个 `endpoint_role` 折叠为 `endpoint_candidates` 且 `endpoint_maturity = not_locked_at_level_01`，`endpoint`／`endpoint_role`／`rationale` 不进入身份；排序键与去重键固定（实测重复 role 对为 0）；`CTX-01`／`CTX-02` 冲突与残缺一律 `undefined_context` DEFER；每个 context 记录全部 `source_row_keys`。另加 `VAL-B09`／`VAL-B10`。

测试用与真实 schema 同构的合成 fixture 实现这些规则，验证 36 行必得 9 个 context、正序／逆序／旋转结果完全相同、追加重复行不改结果、改字段值走 `undefined_context`、删 endpoint 行同样走该路径且不影响其他 context、36 行与引用集合一一对应、改 endpoint 值不改任何 `clinical_context_ref`。

### 自查发现的第三个错误：LOCK-03 只绑一个 dimension 会保证空池

修订过程中实测：**41 条 `crc_prevalence` 全部 `direction = unknown`、`locator = not_available`**，原始 statement 自述「CRC prevalence 未在该运行中调和」。而初稿把 LOCK-03 只绑到 `crc_prevalence`，那会让 active pool 恒为 **0**。

这是执行者的错误，不是审核方提出的。来源文档 Lock 3 列出的合格 linkage 形式本就包含「已有 CRC preclinical 或 clinical targeting evidence」，只绑表达类证据是漏读来源文档。改为两类依据：`LB-expression`（`crc_prevalence`，实测 0，声明为本次空）与 `LB-precedent`（`adc_precedent` supporting 且 locator 为 `clinical_adc_names;clinical_stage_max`，实测 33）。新增测试断言**至少存在一个非空依据**，且每个依据的 `vacuous_this_run` 必须与实测计数一致——将来若所有依据都变空，测试直接失败，而不是静默产出空池。

若不做这次实测，本契约会以「预期 active pool 上限 41」的说法通过审核，而真实结果是 0。

### 预期结果形状改为逐项精确值

原写「active pool 上限 41 个 pair」——技术上是上界但严重误导。改为算出的精确值并加入 `predicted_result_shape` 与对账测试：Raw Matrix **369**、context eligible **1**／hold **8**、target eligible **32**／hold **9**／killed **0**、Eligible Universe Index **32**、active **27**／hold **5**／reactivation-eligible **0**，`CNT-03` 对账 32 = 27 + 5 + 0。

  > **本段数字已被第十二节推翻**，现值为 target eligible **0**／hold **41**、Eligible Universe Index **0**、active **0**。原文保留以对照。

同时写入必须出现在结果报告里的结构性限制：**27 个 active pair 的 linkage 全部只有「已有临床 ADC 针对该靶点」这一类，没有任何一条 CRC 表达证据**，`adc_precedent` 原始 statement 也自述不建立 CRC 疗效或安全窗。因此本次的 `active` 仅表示「存在一条可回溯的 CRC-scoped ADC precedent」。

### 本轮变异检验

10 个变异全部被捕获后精确回滚，回滚后与备份 `diff -q` 一致、测试恢复 `OK`：允许 RNA locator RETAIN、把缺失证据改判 EXCLUDE／killed、把 `not_surface_target` 从不可用清单移除、从 `barred_fields` 删掉 `disposition`、把 `expected_count` 改成不对账的值、把 `endpoint_role` 塞进 context 身份、让 ref 模板依赖 `endpoint_role`、把冲突路径改判 EXCLUDE、从去重键里删掉 endpoint 字段、把 `endpoint_locked` 改成 `true`。

### 审核方认可、本轮未改动的部分

#53／#54 列为 barred sources；输入文件 SHA-256 固定且不一致即中止；旧 `indication_endpoint_target_pairs.tsv` 不作输入；`no_known_linkage_after_complete_search` 本轮禁用；疾病级证据不用于 derived／benchmark 亚群特异 linkage；`DECISION-02` 获接受；不执行 Gate、不评分、不排序；仓库不存候选、证据或结果；contract-only 范围与 GenModule／Gate 边界无污染。

### 审核回写状态

审核方尝试通过 GitHub 连接器提交正式 `REQUEST_CHANGES` review，连接器返回 403，未写回 GitHub。裁决以人类负责人转述为准，已完整记录于本节与 `logs/worklog.md`。

## 十二、第二轮审核裁决与修订（`REQUEST_CHANGES`，2026-08-04）

ChatGPT 对 PR #58（HEAD `8ac045e`）返回 `REQUEST_CHANGES`。上一轮两个工程问题被确认已修复；本轮暴露两个**更基础的科学语义问题**。两条**全部接受**，并导致本 PR 的授权范围被降级。

### 阻断 1（接受）：跨膜段证据不足以判定 `eligible_surface_target`

`transmembrane_segment_count` 只证明蛋白具有跨膜拓扑，不能单独证明质膜定位、细胞外结构域存在、表位可被抗体接近、位于 CRC tumor-cell surface，也不能排除内质网／高尔基／线粒体等细胞器膜蛋白。而 PR #57 冻结的 LOCK-01 问题是「是否存在有合理依据的**细胞外可及蛋白形式**」。把 32 个靶点判为 eligible 超过了输入证据能支持的强度。

原始 statement 本身就写着「supports a membrane-associated target hypothesis but **does not prove tumor-cell surface exposure**」——我读了这句话，还是把它升级成了 RETAIN。这是本轮最直接的错误。

修订：`eligible_surface_target` 现在要求同时满足 `RQ-01` plasma-membrane localization、`RQ-02` extracellular domain/topology、`RQ-03` protein-level provenance，三者缺一不可且全部要求蛋白层面来源。跨膜段单独 → `L1-02` `possible_surface_target` DEFER（32）；无注释 → `L1-03` DEFER（9）；细胞器定位或定位冲突 → `L1-04` DEFER。

**实测：已批准层无法满足 `RQ-01` 与 `RQ-02`。** `target_evidence_units.tsv` 中 `plasma membrane`／`extracellular`／`localization`／`signal peptide`／`GPI` 关键词命中数**均为 0**。故 `retain_requirements_satisfiable_by_approved_inputs: false`，**eligible = 0**。

### 阻断 2（接受）：泛癌 ADC precedent 不能直接证明 CRC linkage

「某靶点已有临床 ADC」可能发生在任何癌种，最多证明该 target 具有 ADC modality precedent，不能自动证明与 CRC clinical context 存在 linkage；而 `indication_fit` 若只是 catalog 派生或模型判断，也不能替代源级 CRC 证据。

修订：`LB-precedent` 现在要求源证据本身包含 CRC/colorectal indication，或 CRC 细胞系／PDO／PDX／动物模型的 ADC/preclinical targeting 证据，并记录 `precedent_indication` 与 `source_locator`。仅其他癌种的 precedent → `LNK-02b` DEFER，保留为 target/modality metadata。仅 `indication_fit` → `LNK-02c` DEFER。

**实测：`measured_source_level_crc_units = 0`。** 33 条 `adc_precedent` supporting 单元的实质主张都是「Local ADC Index contains ADC precedent for〈药名〉」，不附任何 indication。

**一个必须记录的实测陷阱**：这 33 条 statement 全部含 "CRC" 字样，但只出现在免责句「precedent does not establish CRC efficacy or a safe therapeutic window」里。我上一轮就是按「statement 是否包含 CRC」计数得到 33/33 的，那是假阳性。契约已写入 `measurement_trap` 禁止该判据。

### 两条阻断的合并后果：本 PR 降级为只绑定 raw 轴

两条修订各自独立地把可 RETAIN 的数量归零：

| 量 | 修订前 | 修订后 |
|---|---|---|
| target eligible | 32 | **0** |
| Eligible Universe Index | 32 | **0** |
| Pool Level 01 active | 27 | **0** |

因此**已批准证据包无法支撑 Level 01 执行**。执行只会产出空的 Eligible Universe Index 与空的 pool 快照，既无候选价值，又有被误读为「已筛完」的风险。

按审核方上一轮给出的退路，本 PR 降级：`scope_of_authorisation: raw_axis_binding_only`、`authorises_level_01_execution: false`，并登记两个证据缺口：

- **`EVGAP-01`**（阻断 `LOCK-01`）：缺蛋白层面的 plasma-membrane 定位与 extracellular domain/topology 证据。需要一次受控的 target-surface localization evidence extraction。
- **`EVGAP-02`**（阻断 `LOCK-03`）：缺源级 CRC-specific linkage 证据。需要一次受控的 CRC-specific target-context linkage evidence extraction。

两者各自需要独立的 contract-only PR 与 `APPROVE`，都不在本 PR 授权范围内。

### 测试的守卫方式改了

原有一条测试断言「至少存在一个非空 linkage 依据」。现在两类依据都空，那条断言若保留就会阻止提交一个**诚实**的绑定。改为：每个依据的 `vacuous_this_run` 必须与其**合格**计数一致（不是 supporting 计数——泛癌 precedent 是 supporting 但不合格），且**当没有任何依据合格时，`authorises_level_01_execution` 必须为 `false`**。守卫的对象从「必须有货」变成「没货就不许执行」，这才是正确的不变式。

### 本轮变异检验

10 个变异全部被捕获后精确回滚，回滚后与备份 `diff -q` 一致、测试恢复 `OK`：让跨膜段单独恢复 RETAIN、把 RETAIN 条件削减为只要 `RQ-01`、声明已批准输入可满足 RETAIN 要求、把细胞器定位改判 EXCLUDE、让 `indication_fit` 可替代源级证据、把泛癌 precedent 声明为合格、去掉 `requires_source_level_crc_indication`、在空池情况下声明授权执行、把 coverage 改回 32 eligible、把 `LNK-02b` 改判 RETAIN。

### 审核方认可、本轮未改动的部分

context identity 只由 `indication_id` 决定；endpoint 不进入 identity 也未被锁定；顺序变化与重复行不改投影；冲突与残缺 context 进入 DEFER；每个 source row 都有 provenance；#53／#54 来源明确禁止；输入 SHA-256 固定；`no_known_linkage_after_complete_search` 本轮不可用；machine-extracted 证据可满足存在性但不得直接晋级 Level 02；不运行 Gate、不评分、不排序；仓库未写入候选、证据或运行结果。

### 审核回写状态

审核方尝试通过 GitHub 连接器提交正式 `REQUEST_CHANGES` review，连接器返回 403，未写回 GitHub。裁决以人类负责人转述为准，已完整记录于本节与 `logs/worklog.md`。

## 十三、第三轮审核裁决与修订（`REQUEST_CHANGES`，2026-08-04）

ChatGPT 对 PR #58（HEAD `6720edb`）返回 `REQUEST_CHANGES`。第二轮两个科学语义问题确认已正确修复，降级为 `raw_axis_binding_only` 被认可，`EVGAP-01`／`EVGAP-02` 被确认足以作为后续两个受控抽取契约的范围依据。仅剩一处残留矛盾。

### 阻断（接受）：`VAL-B07` 仍保留旧计数

主体契约已改为 `eligible = 0`／`hold = 41`／`killed = 0`，`lock_01_derivation.coverage` 与 `predicted_result_shape` 都用这组值，但 `output_validation.additional_rules.VAL-B07` 仍写着 `32 eligible + 9 hold + 0 killed`。同一份机器可读契约同时规定两套互斥结果，未来验证无法确定权威值。**这是第二轮修订的漏改，执行者的错误。**

修订：

1. `VAL-B07` 的散文改为 `0 eligible + 41 hold + 0 killed`，并注明 `41 hold = 32 (L1-02，仅有跨膜拓扑) + 9 (L1-03，无任何注释)`。
2. 新增结构化字段 `expected_target_eligibility`，使计数可被机械比对而不必解析散文；并加 `validates: evidence_insufficient_binding_state` 与 `authorises_result_generation: false`，明确该规则用于验证「证据不足导致无法执行」的绑定状态，不代表授权生成 Level 01 结果。
3. 新增 `test_target_eligibility_counts_agree_in_all_three_places`，直接断言 `VAL-B07`、`lock_01_derivation.coverage`、`predicted_result_shape.target_eligibility` 三处逐键相等，并断言散文与结构化计数不矛盾。
4. 新增 `test_no_validation_rule_asserts_eligible_targets_while_blocked`：在未授权执行时，任何验证规则都不得要求存在 eligible target，且每条非空 LOCK-01 规则都必须 DEFER。

### 全文扫描结果

按验收标准逐处核对，仓库内已不存在任何把跨膜段对应的 32 个靶点写成 eligible 的**执行或验证要求**。剩余提到「32」的位置全部是描述性的：绑定 YAML 第 318 行说明 `41 hold = 32 + 9`；契约第 81 行把旧映射描述为错误；本 handoff 第十一节是第一轮的历史记录，已加取代标记指向第十二节；第十二节的对照表与变异清单本身就是记录修订的。

### 本轮变异检验

5 个变异全部被捕获后精确回滚，与备份 `diff -q` 一致、测试恢复 `OK`：把 `VAL-B07` 的结构化计数改回 32、只把散文改回 32 使其与结构化字段矛盾、把 `coverage` 改成与 `VAL-B07` 不一致、把 `predicted_result_shape` 改成与 `VAL-B07` 不一致、声明该规则可授权生成结果。

### 审核回写状态

审核方尝试通过 GitHub 连接器提交正式 `REQUEST_CHANGES` review，连接器返回 403，未写回 GitHub。裁决以人类负责人转述为准，已记录于本节与 `logs/worklog.md`。
