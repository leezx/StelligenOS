# EVGAP-02：CRC-specific target–context linkage 证据抽取契约

- 任务分支：`task_20260805_evgap-02-crc-linkage-contract`
- 前置工作包：PR #57（Level 01 判据定义）、#58（输入绑定与缺口登记）、#59（EVGAP-01 抽取契约），均已 `APPROVE` 并合并
- 机器可读绑定：[`../pools/evgap_02_crc_linkage_extraction.yaml`](../pools/evgap_02_crc_linkage_extraction.yaml)，由 `tests/test_evgap_02_crc_linkage.py` 校验
- 来源文档：`Zhixins-KB/2.Biotech/Asset-Generation-OS-architecture.md` 的 `# EVGAP-02 应该具体抽取什么` 与 `# EVGAP-02 最小结果标准`（只读取，未修改）
- 当前状态：**contract-only，未执行，等待 ChatGPT 审核**
- 授权范围：**获 `APPROVE` 后即可执行一次抽取。不授权执行 Level 01，不解除 `EVGAP-01`。**

## 目的

解除 PR #58 登记的 `EVGAP-02`，使 Level 01 的 `LOCK-03` 可以真正求值。

现状是：`crc_prevalence` 41 条全为 `not_available`，33 条 `adc_precedent` supporting 单元无一附 indication，因此 LOCK-03 对全部 369 个 pair 只能是 `unresolved`（已在 2026-08-05 的 Preview 中实测确认）。

本契约冻结抽取范围、来源分层、四类 linkage 判据、求值优先级、**检索范围**与输出验证。**不执行抽取。**

## 一、本契约与 EVGAP-01 完全独立，可并行执行

`independent_of: [EVGAP-01, SRCADM-01]`，`blocked_by: [contract_approval]`——唯一的阻断是本契约自身的审核。

理由：LOCK-03 问的是「target 为什么与这个 CRC clinical context 有关」，**与表面拓扑无关**，因此不读取 surfaceome 参考库，也不受其准入状态影响。

这也是抽取范围必须覆盖**全部 369 个 pair**而不是 EVGAP-01 之后可能 eligible 的 22 个的原因：若只覆盖 22 个，本抽取就会依赖尚未获准入的 surfaceome 判定结果，既污染来源，也使两条 track 无法并行。

来源文档给出的优先级是 **Track A 先做 `EVGAP-02`，Track B 并行做 `SRCADM-01`**——因为 22 个靶点即使全部通过 surface identity，没有 CRC linkage 仍只是泛癌 surface targets，不是 CRC indication–target seeds。

## 二、来源分层：一个必须先讲清的普遍问题

核查结果：**仓库内 `logs/chatgpt-review-*.md` 中没有任何一条提及过任何本地派生数据库。** PR #59 发现的 surfaceome 准入问题不是个例，而是普遍状况。

因此本契约把来源分成两层。

### Tier 1：原始公开来源，可直接使用

| 来源类 | endpoints | 必须记录 |
|---|---|---|
| `peer_reviewed_literature` | PubMed、PMC | pmid_or_pmcid、title、journal、year、retrieved_at |
| `clinical_trial_registry` | ClinicalTrials.gov | nct_id、phase、status、indication_text、retrieved_at |
| `public_molecular_dataset` | TCGA、GEO、Human Protein Atlas | dataset_accession、dataset_version_or_release、query_expression、retrieved_at |
| `approved_internal_result` | `gen_iet_crc_target_enumeration_20260802`（PR #29） | source_id、sha256 |

依据是 PR #59 审核所作的区分：原始公开来源**不是派生数据库**，其内容可由 `source_locator` 直接回溯到原始记录，不存在「构建逻辑是否遵守声明」的问题。

**这一层足以支撑本次抽取**——CRC-specific linkage 证据正是存在于文献、试验注册库与公开数据集中。所以本契约获批后即可执行，无需等待任何 admission。

### Tier 2：派生本地数据库，一律禁用至各自获准入

| ID | 数据库 | 本会服务的 linkage 类 | admission 记录 |
|---|---|---|---|
| `SRCADM-02` | `ADCdb` | B | `null` |
| `SRCADM-03` | `CRC_journal_whitelist_literature` | A | `null` |
| `SRCADM-04` | `CRC_Atlas_fulltext_accession_ledger` | A | `null` |
| `SRCADM-05` | `ADC_competitive_landscape_reference` | B | `null` |

本次抽取**不使用**它们（`used_by_this_extraction: false`，`VAL-L10` 强制）。后果必须写明：**检索完整性只在 Tier 1 声明范围内成立。** 若将来某个派生库获准入，需另开 PR 扩大 `declared_search_scope` 并重跑，**不得静默扩大**。

## 三、四类 linkage 判据

### A. CRC human tumor expression

接受 CRC patient samples、primary tumour、metastatic lesion、treatment-resistant context；可得时必须记录 `positive_fraction_or_prevalence` 与 `malignant_cell_attribution`。

**蛋白证据优先。RNA 可以证明 linkage 存在，但绝不得替代 LOCK-01 的蛋白层面判据**（`rna_admissible_for_linkage_existence: true`，`rna_may_satisfy_lock_01: false`，且必须标注）。这与 Level 01 契约「RNA 不得满足 LOCK-01」一致，测试双向校验。

### B. CRC-specific ADC precedent

接受 CRC clinical trial、CRC preclinical ADC、CRC cell line、CRC PDO、CRC PDX、CRC animal model。

**仅其他癌种的 ADC precedent 不算 linkage**，降为 `metadata_only_hold`（`L3-04`）。这条与 #58 已冻结的规则一致。

### C. CRC-specific target-directed modality evidence（本契约新增）

接受 naked antibody、CAR-T、bispecific、radioimmunotherapy、immunotoxin、imaging antibody。

它们证明 **target 在 CRC 中可接近或可干预**，因此满足 LOCK-03 的存在性——LOCK-03 只问「是否存在公开证据表明该 target 与该 CRC context 有关」，不问 ADC 疗效。

但必须显式标注 **`is_adc_efficacy_evidence: false`**（`VAL-L04`，`MF-L02`）。这是现有契约尚未涵盖的新增依据。

### D. Context-specific enrichment

接受 MSS/pMMR、post-anti-EGFR、liver metastasis、treatment-resistant、HER2-positive、refractory metastatic CRC。

**疾病级 CRC 证据只支持 canonical context，不自动支持任何亚群**；亚群 context 必须有 D 类证据才能 RETAIN。

## 四、检索范围冻结：使完整性成为可判定事实

PR #58 曾判定 `no_known_linkage_after_complete_search` **不可用**，理由是检索范围未闭合。本节正是使该 outcome 变为可用的前提——范围一旦冻结，「是否完成规定检索」就成为可判定的事实，而不是执行者的自我声明。

- 每个 target 必须对三类 Tier 1 来源（文献、试验注册库、公开分子数据集）各执行检索
- 必须记录 query template，含 target 符号与同义词、CRC 术语、类别特异术语、日期范围
- 每次检索必须记录 `source_class`、`endpoint`、`query_expression`、`executed_at`、`result_count`、`reachable`
- **来源不可达 → 该 target 判为检索未完成**（`search_incomplete_for_that_target`），不得静默跳过（`silent_skip_forbidden: true`）

### 检索粒度

A／B／C 三类的疾病级检索对同一 target 在 9 个 context 下结果相同，**按 target 检索一次**（41 次）即可，避免 369 次冗余检索；D 类情境特异性富集**按 pair 判定**（369 次）。此项写明是为了让「检索次数」这个数字不被误读。

## 五、LOCK-03 求值规则与冻结优先级

优先级：`L3-01` → `L3-02` → `L3-03` → `L3-04` → `L3-05`。

理由：**先判检索是否完成——未完成时「没找到」无法与「不存在」区分**；再判是否存在与该 context 匹配的 CRC-specific 证据；再判疾病级证据遇亚群 context 的降级；再判仅有其他癌种 precedent 的降级；以上都不成立且检索已完成，才允许判定完整检索后无 linkage。

| ID | 条件 | outcome | disposition | state |
|---|---|---|---|---|
| `L3-01` | 未完成规定检索 | `linkage_evidence_missing` | DEFER | hold |
| `L3-02` | 有 A/B/C 任一 CRC-specific 证据，且 context 为 canonical，或亚群且有 D 类证据 | `linkage_evidence_exists` | **RETAIN** | active |
| `L3-03` | 有 CRC 疾病级证据，但 context 为亚群且无 D 类 | `linkage_unassessed` | DEFER | hold |
| `L3-04` | 仅有其他癌种 precedent | `linkage_unassessed` | DEFER | hold |
| `L3-05` | 完成规定检索且四类均无命中 | `no_known_linkage_after_complete_search` | EXCLUDE | reactivation-eligible |

**只有 `L3-02` 可以 RETAIN，只有 `L3-05` 可以 EXCLUDE**，测试断言各自恰好一条。`L3-05` 的 EXCLUDE 语义严格限定为 `EXCLUDE_FROM_ACTIVE_POOL`：`is_scientific_disproof: false`、`is_killed: false`、`retained_in_eligible_universe_index: true`，并须六项检索完整性字段齐备。

测试用参考实现穷举 `search_complete × crc_specific × canonical × class_d × other_cancer` 全部 **32 种组合**，证明每种恰好命中一条规则，且五条规则都可达。

## 六、本契约不给出预期结果形状

这与 EVGAP-01 不同，且是有意的。

EVGAP-01 读取的是已固定的数据集，结果可以事先算出并逐项核对（22／19）。**EVGAP-02 是发现型检索，事先给出这类数字就会把预测冒充成结果**——正是来源文档列为第二种必须避免的混淆。

因此本契约不预测计数，改为冻结 `declared_search_scope`、`search_complete_definition`、`derivation_precedence`、provenance 要求与输出验证，使完整性与每一条 disposition 都可事后核验。测试断言 `predicted_result_shape.provided = false`，且不得以任何别名偷偷塞入计数。

## 七、输出与 provenance 分层

**两张表。** `evidence` 表每条证据一行，含来源文档规定的 13 列必需最小集，另加 `linkage_class`、`is_adc_efficacy_evidence`、`positive_fraction_or_prevalence`、`malignant_cell_attribution`、`retrieved_at`。`disposition` 表每个 pair 一行，21 列，含 `rule_id`、六项检索完整性字段、`provenance_kind`、`provisional_only`、`may_advance_to_level_02`。

**三种 `provenance_kind`，要求不同**（这是 PR #59 阻断 3 的教训）：

| kind | 必填 | 可空 |
|---|---|---|
| `source_supported` | `source_ref`、`source_locator`、`retrieved_at` | `no_evidence_found_reason` |
| `no_evidence_found_after_complete_search` | 六项检索完整性字段 + `no_evidence_found_reason` | `source_ref`、`source_locator` |
| `search_incomplete` | `search_complete`、`search_scope`、`searched_at`、`no_evidence_found_reason` | `source_ref`、`source_locator` |

后两种**禁止伪造 source evidence**；出现非空 `source_ref` 即为验证失败（`VAL-L08`）。测试断言所有条件必填列都在输出 schema 之内（PR #59 阻断 2 的教训）。

15 条验证规则 `VAL-L01`..`VAL-L15` 见 YAML。

## 八、必须写进结果报告的四条

- **`MF-L01`**：LOCK-03 RETAIN 只表示存在可回溯的 CRC-specific linkage 证据，**不表示该靶点适合 ADC、不表示疗效、不表示治疗窗**。
- **`MF-L02`**：C 类证据证明 target 在 CRC 中可接近或可干预，**不是 ADC 疗效证据**，必须原样标注。
- **`MF-L03`**：本次抽取未使用任何派生本地数据库，检索完整性只在 Tier 1 声明范围内成立。
- **`MF-L04`**：LOCK-03 RETAIN **不使 pair 进入 Level 02**。`EVGAP-01` 未解除前 `may_advance_to_level_02` 恒为 `false`。

## 九、授权与不授权

**授权：** 获 `APPROVE` 后按本契约执行**一次**抽取，读取 Tier 1 来源，覆盖全部 369 个 pair。

**不授权：** 执行 Level 01；解除 `EVGAP-01`；读取任何 Tier 2 派生本地数据库；把任何派生数据库纳入已批准来源；评估 T2、T7 或任何 Gate；新增靶点或 clinical context；任何筛选排序、Tier 划分、资产推荐或实验建议；引入被隔离运行（PR #53、#54）的任何产物。

## 十、后续顺序

1. 本契约 `APPROVE`。
2. 执行抽取 → 结果 PR → `APPROVE`。
3. **另开 PR** 更新 `adc_pool_level_01_input_binding.yaml`，绑定抽取产物并解除 `EVGAP-02`。
4. `EVGAP-01` 由 Track B 独立推进（`SRCADM-01` → 抽取 → 结果 → binding）。
5. **两个缺口都解除后，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。**

## 十一、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行抽取。
- 抽取完成也**不**解除 `EVGAP-01`，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。
