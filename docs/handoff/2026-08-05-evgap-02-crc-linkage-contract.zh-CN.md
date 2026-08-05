# Handoff：EVGAP-02 CRC-specific linkage 证据抽取契约

- 日期：`2026-08-05`
- 任务分支：`task_20260805_evgap-02-crc-linkage-contract`
- 基线：`main` @ `e30a430`
- 前置：PR #57、#58、#59，均已 `APPROVE` 并合并
- 交付物类型：**contract-only**
- 外部运行：**无。没有执行抽取，没有检索，没有产生任何证据、判定或候选。**
- 授权范围：**获 `APPROVE` 后可执行一次抽取；不授权执行 Level 01，不解除 `EVGAP-01`**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（依据是 diff 范围，可由 `git diff --stat` 核验）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次范围

人类负责人指示起 `EVGAP-02` 契约。这是 Track A，来源文档给出的优先级高于 `SRCADM-01`／`EVGAP-01`（Track B）。

`EVGAP-02` 阻断 `LOCK-03`：`crc_prevalence` 41 条全为 `not_available`，33 条 `adc_precedent` supporting 单元无一附 indication，因此 LOCK-03 对全部 369 个 pair 只能是 `unresolved`——这一点已在 2026-08-05 的 Level 01 Preview 中实测确认。

抽取范围、来源分层、四类判据、求值优先级、检索范围与输出验证均取自来源文档 `# EVGAP-02 应该具体抽取什么` 与 `# EVGAP-02 最小结果标准`。

## 二、仓库内交付了什么

| 文件 | 作用 |
|---|---|
| `docs/tasks/EVGAP_02_CRC_LINKAGE_EXTRACTION_CONTRACT.zh-CN.md` | 抽取契约（面向操作者，中文） |
| `docs/pools/evgap_02_crc_linkage_extraction.yaml` | 机器可读绑定：来源分层、四类 linkage、检索范围冻结、五条规则与优先级、输出 schema 与 15 条验证 |
| `tests/test_evgap_02_crc_linkage.py` | 29 项校验，含 32 种条件组合的穷举求值证明 |

## 三、与 EVGAP-01 独立，这决定了范围

`independent_of: [EVGAP-01, SRCADM-01]`，`blocked_by: [contract_approval]`——唯一阻断是本契约自身的审核，获批即可执行。

LOCK-03 问的是「target 为什么与这个 CRC clinical context 有关」，**与表面拓扑无关**，故不读 surfaceome 参考库、不受其准入状态影响。

因此抽取覆盖**全部 369 个 pair**，而不是 EVGAP-01 之后可能 eligible 的 22 个。**若只覆盖 22 个，本抽取就会依赖尚未获准入的 surfaceome 判定结果，既污染来源，也使两条 track 无法并行。**

## 四、核查发现：派生库未获准入是普遍状况，不是个例

**仓库内 `logs/chatgpt-review-*.md` 中没有任何一条提及过任何本地派生数据库。** PR #59 发现的 surfaceome 问题不是孤例。

据此把来源分成两层：

- **Tier 1 原始公开来源可直接使用**——PubMed／PMC、ClinicalTrials.gov、TCGA／GEO／HPA，加上已批准的枚举轴（PR #29）。依据是 PR #59 审核所作的区分：原始公开来源不是派生数据库，内容可由 `source_locator` 直接回溯到原始记录，不存在「构建逻辑是否遵守声明」的问题。**这一层足以支撑本次抽取，故本契约获批后即可执行，不需要等任何 admission。**
- **Tier 2 派生本地库一律禁用**，并登记四个待准入项：`SRCADM-02` ADCdb（B 类）、`SRCADM-03` CRC 文献库（A 类）、`SRCADM-04` CRC Atlas ledger（A 类）、`SRCADM-05` 竞争格局库（B 类），`admission_record_ref` 全为 `null`。后果写明：**检索完整性只在 Tier 1 声明范围内成立**；某个派生库日后获准入需另开 PR 扩大范围并重跑，不得静默扩大。

## 五、四类判据，其中 C 类是新增

**A CRC human tumor expression**：蛋白优先；**RNA 可证明 linkage 存在但绝不得替代 LOCK-01**，且必须标注。测试双向校验——本契约的 `rna_may_satisfy_lock_01: false` 与 Level 01 契约的 `rna_may_not_satisfy` 含 `LOCK-01` 必须同时成立。

**B CRC-specific ADC precedent**：CRC 试验／preclinical／cell line／PDO／PDX／动物模型。**仅其他癌种 precedent 不算 linkage**，降为 `metadata_only_hold`（`L3-04`）——与 #58 已冻结规则一致。

**C CRC-specific target-directed modality evidence（本契约新增）**：naked antibody、CAR-T、bispecific、radioimmunotherapy、immunotoxin、imaging antibody。它们证明 target 在 CRC 中可接近或可干预，满足 LOCK-03 存在性（该锁只问关联存在、不问 ADC 疗效），但**必须显式标注 `is_adc_efficacy_evidence: false`**。这是现有契约尚未涵盖的依据，来源文档点名要求加入。

**D Context-specific enrichment**：疾病级 CRC 证据只支持 canonical context，亚群必须有 D 类证据才能 RETAIN。

## 六、检索范围冻结是本契约最关键的一节

PR #58 判定 `no_known_linkage_after_complete_search` **不可用**，理由是检索范围未闭合。本契约冻结范围，正是使该 outcome 变为可用的前提——范围一旦冻结，「是否完成规定检索」就成为**可判定的事实**，而不是执行者的自我声明。

每个 target 必须对三类 Tier 1 来源各执行检索；必须记录 query template（target 符号与同义词、CRC 术语、类别特异术语、日期范围）；每次检索必须记录 `query_expression`、`executed_at`、`result_count`、`reachable`；**来源不可达即判该 target 检索未完成**，禁止静默跳过。

检索粒度也写明了：A／B／C 的疾病级检索按 target 一次（41），D 类按 pair（369）。避免「检索次数」这个数字被误读。

## 七、五条规则与穷举证明

优先级 `L3-01` → `L3-02` → `L3-03` → `L3-04` → `L3-05`。**先判检索是否完成——未完成时「没找到」无法与「不存在」区分。**

只有 `L3-02` 可 RETAIN，只有 `L3-05` 可 EXCLUDE，测试断言各自恰好一条。`L3-05` 的 EXCLUDE 严格限定为 `EXCLUDE_FROM_ACTIVE_POOL`，`is_scientific_disproof` 与 `is_killed` 均为 `false`，状态 `reactivation-eligible`，并须六项检索完整性字段齐备。

测试用参考实现穷举 `search_complete × crc_specific × canonical × class_d × other_cancer` 的全部 **32 种组合**，证明每种恰好命中一条、且五条规则都可达——这是 PR #59 阻断 4 的教训，这次一开始就做。

## 八、本契约有意不给预期结果形状

EVGAP-01 读固定数据集，结果可事先算出并逐项核对（22／19）。**EVGAP-02 是发现型检索，事先给出这类数字就是把预测冒充成结果**——来源文档列为第二种必须避免的混淆。

因此不预测计数，改为冻结检索范围、完整性定义、求值优先级、provenance 要求与输出验证。测试断言 `provided: false` 且不得以别名偷偷塞入计数（变异检验含此项）。

## 九、沿用前几轮教训的三处设计

- **provenance 三分**（PR #59 阻断 3）：`source_supported` / `no_evidence_found_after_complete_search` / `search_incomplete`，后两种允许 `source_ref` 为空但**禁止伪造**，出现非空即验证失败。
- **条件必填列必须在 schema 之内**（PR #59 阻断 2）：测试直接断言子集关系。
- **冻结优先级并穷举证明**（PR #59 阻断 4 与 #58 阻断 2）：见第七节。

## 十、明确没有做什么

- **没有执行抽取**，没有发起任何检索，没有产生任何证据行、disposition 或候选。
- 没有执行 Level 01，也不授权执行；**没有解除 `EVGAP-01`**。
- 没有读取任何 Tier 2 派生本地数据库；没有把任何派生数据库纳入已批准来源。
- 没有评估 T2、T7 或任何 Gate；没有排序、Tier 划分、资产推荐或实验建议。
- 没有新增靶点或 clinical context。
- 没有引用被隔离运行（PR #53、#54）的任何产物。
- 没有更新 `adc_pool_level_01_input_binding.yaml`——解除 `EVGAP-02` 须待抽取执行、结果 PR 获批后另开 PR。
- 没有预测结果计数（见第八节）。
- 未补 #52／#53／#54／#57／#58／#59／#60 的批准记录（现为七份），事实已查全但未写文件。
- 没有修 `requirements.txt` 注释里过期的「207 tests」（实测 338）。属无关改动。

## 十一、验证结果

- `Ran 338 tests` 全部通过（`main` 基线 309 + 本次新增 29）。
- `scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- `git diff --check`：通过；零 `__pycache__`。
- **13 个变异全部被捕获后精确回滚**，与备份 `diff -q` 一致、测试恢复 `OK`：让 RNA 满足 LOCK-01、把 C 类声明为 ADC 疗效证据、让泛癌 precedent 算作 linkage、让疾病级证据支撑亚群、把 `L3-03` 改判 RETAIN、把完整检索排除改判 killed、把检索完整性排到优先级最后、允许静默跳过来源、开放 Tier 2 派生库、自行填入 `SRCADM-02` 记录、偷偷加入预测计数、要求未找到证据的行也有 `source_ref`、把范围缩到依赖 LOCK-01 状态。
- 一处测试自身的错误已修：初稿断言「除 `L3-05` 外全部 DEFER」，漏了 `L3-02` 是 RETAIN 规则；改为逐规则断言并加「恰好一条 RETAIN、恰好一条 EXCLUDE」。

## 十二、后续顺序

1. 本契约 `APPROVE`。
2. 执行抽取 → 结果 PR → `APPROVE`。
3. 另开 PR 绑定产物并解除 `EVGAP-02`。
4. `EVGAP-01` 由 Track B 独立推进（`SRCADM-01` → 抽取 → 结果 → binding）。
5. **两个缺口都解除后，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。**

## 十三、当前阻断

- 本契约获 `APPROVE` 前，不得执行抽取。
- 抽取完成也**不**解除 `EVGAP-01`，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。

## 十四、第一轮审核裁决与修订（`REQUEST_CHANGES`，三条阻断全部接受）

ChatGPT 对 PR #61（HEAD `430e85f`）返回 `REQUEST_CHANGES`。三条**全部接受**。

### 阻断 1（接受）：D 类检索没有真正进入 search completeness，且 endpoint 覆盖语义未冻结

契约声明 A/B/C 按 target 检索、D 类按 369 个 pair 评估，但 `search_complete_definition` **只要求每个 target 完成三类 source-class 检索**，没有要求每个 pair 对 D 类完成可审计的检索。审核方指出的两个后果都成立：subgroup pair 可能在未真正检索 D 类时直接落 `L3-03`；「四类均无命中」的 `L3-05` 也可能在 D 类未检索时被错误触发。

同时，`peer_reviewed_literature` 有 PubMed 与 PMC 两个 endpoint、`public_molecular_dataset` 有三个，而契约只要求覆盖 source class——**执行者可以只查其中一个，结果不可复现。**

修订：

- 新增 `per_pair_required_class_d_search`，369 个 pair 全覆盖，每 pair 记录六个字段（`class_d_query_expression`／`class_d_executed_at`／`class_d_result_count`／`class_d_reachable`／`class_d_source_coverage_ref`／`class_d_search_complete`），六个字段同时进入 `disposition_columns`
- `incomplete_consequence: L3-01`——**D 类未完成必须落 `L3-01`，不得落 `L3-03` 或 `L3-05`**（`VAL-L18`）；`L3-03` 与 `L3-05` 都加 `requires_class_d_search_complete: true`；`L3-01` 加 `covers_both_completeness_levels: true`
- `search_complete_requires_both_levels: true`，两级为 target 级 endpoint 覆盖与 pair 级 D 类覆盖
- `coverage_unit: endpoint`，每个 source class 加 `all_endpoints_required: true` 与 `minimum_endpoint_set`（PubMed+PMC；ClinicalTrials.gov；TCGA+GEO+HPA），缺任一 endpoint 该 target 全部 pair 落 `L3-01`（`VAL-L19`）
- 新增 `unreachable_class_d_consequence: search_incomplete_for_that_pair`

### 阻断 2（接受）：disposition 与 evidence 之间没有稳定引用关系

初稿 disposition 表只有 `evidence_row_count`，**单条 disposition 无法证明自己由哪些 evidence 行支持**。而我的测试用两张表列的**并集**验证条件必填字段存在——审核方指出这恰好掩盖了问题。这条批评对测试方法本身，比对契约更准。

修订：

- evidence 表新增唯一 `evidence_id`（`evidence_row_key`／`evidence_id_unique`）
- disposition 表新增三组引用：`supporting_evidence_refs`、`class_d_evidence_refs`、`other_cancer_evidence_refs`
- 新增 `evidence_reference_requirements`，逐规则冻结「必须引用什么、必须不引用什么」，`L3-02` 按 canonical／subgroup 拆成两条：canonical 至少一条 A/B/C；subgroup 另需至少一条 D；`L3-03` 须有疾病级证据且 D refs 为空；`L3-04` supporting 必须为空、只能引用 other-cancer；`L3-05` 三组全空且检索 provenance 完整；`L3-01` 不得伪造
- 新增 `VAL-L16`（引用的 id 必须存在于 evidence 表且 `pair_id` 一致）、`VAL-L17`（逐规则引用约束）、`VAL-L20`（`evidence_row_count` 必须等于三组 refs 去重后总条数）
- 每个 `conditionally_required_columns` 块加 `table` 字段，**测试改为逐表检查，不再用并集**（`VAL-L09` 同步改写）

### 阻断 3（接受）：PR 不可合并

同步 `origin/main`（`0190a73`）。`logs/worklog.md` 冲突按时间顺序解决：main 的 12:45 EDT 在前、我的 13:30 在后，断言无残留冲突标记、两侧每个条目与每个标题都在。

合并后核验：相对 `main` 仍**只有 5 个文件**（本 handoff、契约 YAML、契约文档、worklog、测试），**未混入 PR #60 的 preview 结果**（`grep -c preview` = 0），未引入其他无关契约。

### 一处执行者操作失误，已自查并修复

中途为处理 PR #60 而切分支时执行了 `git stash -u`，把阻断 1／2 的未提交 YAML 改动一并藏入栈中，切回后未恢复，导致随后的编辑落在了未修订的版本上、测试报 `KeyError`。已定位 `stash@{0}`、丢弃冲突编辑、`git stash pop` 恢复全部 133 行改动后重做，无内容丢失。

### 本轮变异检验

12 个变异全部被捕获后精确回滚，与备份 `diff -q` 一致、测试恢复 `OK`：把 D 类改为非必需、让 D 类未完成落 `L3-03`、让 `L3-05` 不要求 D 类完成、让完整性只要 target 级、覆盖粒度退回 source class、只查 PubMed 就算覆盖 class、去掉 `evidence_id`、让 `L3-04` 可引用 supporting refs、让 subgroup RETAIN 不需 D refs、让 `L3-05` 可引用证据、把必填列声明到错误的表、删掉 `L3-03` 的 D refs 为空约束。

### 审核方认可、本轮未改动的部分

EVGAP-02 与 EVGAP-01／SRCADM-01 独立；覆盖全部 369 pairs 而非 provisional 22；Tier 1／Tier 2 分层合理且 Tier 2 在 admission 前保持禁用；A/B/C/D 四类框架完整；RNA 可支持 linkage 但不满足 LOCK-01；C 类可作 CRC linkage existence 但必须明确不是 ADC efficacy；disease-level 不能自动支持 subgroup；other-cancer precedent 只能作 metadata；`L3-05` 是可逆的 `EXCLUDE_FROM_ACTIVE_POOL` 而非科学证伪或 killed；不执行 Gate、不执行 Level 01、不解除 `EVGAP-01`；不预写 discovery run 的结果数量。

### 审核回写状态

审核方尝试通过 GitHub 连接器提交正式 `REQUEST_CHANGES`，连接器返回 403，未写回 GitHub。裁决以人类负责人转述为准，已记录于本节与 `logs/worklog.md`。
