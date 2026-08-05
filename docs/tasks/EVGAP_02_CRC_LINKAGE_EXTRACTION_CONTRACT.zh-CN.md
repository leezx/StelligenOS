# EVGAP-02：CRC-specific target–context linkage 证据抽取契约

- 任务分支：`task_20260805_evgap-02-crc-linkage-contract`
- 前置工作包：PR #57（Level 01 判据定义）、#58（输入绑定与缺口登记）、#59（EVGAP-01 抽取契约），均已 `APPROVE` 并合并
- 机器可读绑定：[`../pools/evgap_02_crc_linkage_extraction.yaml`](../pools/evgap_02_crc_linkage_extraction.yaml)，由 `tests/test_evgap_02_crc_linkage.py` 校验
- 来源文档：`Zhixins-KB/2.Biotech/Asset-Generation-OS-architecture.md` 的 `# EVGAP-02 应该具体抽取什么` 与 `# EVGAP-02 最小结果标准`（只读取，未修改）
- 当前状态：**v0.2.0，`L-RETRIEVAL` 层已执行，`L-ASSERTION` 层未执行，等待 ChatGPT 审核**
- 授权范围：**不授权执行 Level 01，不解除 `EVGAP-01`，`EVGAP-02` 亦未解除。**

## 〇、v0.2.0 修订（PR #62 审核）

v0.1.0 有一个承重漏洞：它把 `evidence_direction` 与 `review_status` 列为**必需列，
却没有任何一条规则要求它们被解析**；`linkage_class` 也没有任何规则约束其来源。
于是一次**完全合规**的执行产出了 7,067 行 `evidence_direction = unknown` 的检索命中，
并据此判出 **168 条 RETAIN、9 条 EXCLUDE**。

**检索命中不是 linkage 证据。** 修必须修在契约上，因为执行并未违约。

### 三层结构

| layer | 产物 | 可支撑 LOCK-03 |
|---|---|---|
| `L-RETRIEVAL` | `retrieval_candidates` | **否** |
| `L-ASSERTION` | `linkage_assertions` | 是 |
| `L-DISPOSITION` | `pair_linkage_disposition` | 只能引用 assertion |

`assertion_requirements` 规定六个构成要件：target／CRC／context 实体消歧、
`relationship_type`、`assertion_direction`、`supporting_text_or_structured_field`。
**硬性禁止 `assertion_direction = unknown`**——这正是 v0.1.0 漏掉 7,067 行的那道检查（`VAL-L21`）。

`linkage_class` 由 assertion 内容判定；候选表改记 `query_class_label`，
且**候选表不得含 `linkage_class` 列**（`VAL-L25`）。

### `DECISION-02` 的正确读法

PR #58 允许机器抽取的证据满足 LOCK-03 existence，**前提是机器已抽出一条具体、可审计的 assertion**——
主体、癌种、关系、方向、出处俱全。v0.1.0 停在候选检索。人工复核要求不变。

### 实体消歧与 `L3-00`

新增 `L3-00` 置于优先级最前。关键在**不对称**：未消歧实体既不得 RETAIN，也**绝不得** EXCLUDE。

实测四个必须单列的实体：`Undisclosed`（缺失值占位符，被当基因符号检索，PMC 返回 1,384 条）、
`CA19-9`（糖类抗原，无 HGNC 符号，PMC 14,200 条）、`AG7`、
`EDBN`（11 个 endpoint 全部 0 命中，因而被 `L3-05` 排除——
**排除的唯一原因是这个缩写不通行于文献**）。

`L3-00` **不引入新 outcome**：LOCK-03 的词表由 PR #57 冻结，其中没有 `identity_unresolved`
（该 outcome 只属于 LOCK-01）。故复用 `linkage_evidence_missing`，
身份信息另由 `identity_resolution_status` 列承载。

### endpoint 命中证明了什么

新增 `endpoint_evidence_admissibility`。TCGA／HPA／GEO 三者 `admissible_as_class_a: false`
（gene index 存在性、页面存在性、数据集元数据匹配都不是表达证据），
但**仍为必查**，服务于覆盖与身份消歧，其命中不计入 `linkage_classes_hit`（`VAL-L26`）。
`ClinicalTrials.gov` 须记录五个结构化字段并满足**同臂**要求（`VAL-L28`）。

### 检索完整性

`search_complete` 现需四层：身份消歧、endpoint 覆盖、pair 级 D 类、**assertion 抽取完成**。
`retrieval_alone_is_not_search_complete: true`。

### 上游缺陷 `GAP-P07`

target 轴上四个实体不可消歧。`EVGAP-02` 无权改轴，故**只登记不修复**——
在本契约内给 `Undisclosed` 编一个身份等于静默改轴。修复须另开 PR。

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

完整性分**两级**，`search_complete_requires_both_levels: true`，两级都达标才算完成。

**第一级：target 级，按 endpoint 判定（不是按 source class 判定）。**

初稿只要求「覆盖 source class」，执行者可以只查 PubMed 不查 PMC、只查 TCGA 不查 GEO 与 HPA，结果不可复现——这是审核裁决指出的漏洞。现改为 `coverage_unit: endpoint`，每个 source class 都写明 `minimum_endpoint_set` 且 `all_endpoints_required: true`：

| source class | 必查 endpoints |
|---|---|
| `peer_reviewed_literature` | PubMed **与** PMC |
| `clinical_trial_registry` | ClinicalTrials.gov |
| `public_molecular_dataset` | TCGA **与** GEO **与** Human Protein Atlas |

缺任一 endpoint，该 target 的全部 pair 落 `L3-01`（`VAL-L19`）。

**第二级：pair 级 D 类检索，369 个 pair 全覆盖。**

D 类是 pair 级判据，初稿却没要求它进入 `search_complete`——后果是 subgroup pair 可能在从未检索 D 类的情况下直接落 `L3-03`，或使「四类均无命中」的 `L3-05` 被错误触发。现要求每个 pair 记录六个字段：`class_d_query_expression`、`class_d_executed_at`、`class_d_result_count`、`class_d_reachable`、`class_d_source_coverage_ref`、`class_d_search_complete`。

**某个 pair 的 D 类检索未完成时，该 pair 必须落 `L3-01`，不得落 `L3-03`，也不得落 `L3-05`**（`VAL-L18`）。`L3-03` 与 `L3-05` 都带 `requires_class_d_search_complete: true`。

**其他要求**：必须记录 query template（target 符号与同义词、CRC 术语、类别特异术语、日期范围）；每次检索记录 `query_expression`、`executed_at`、`result_count`、`reachable`；来源不可达 → 该 target 检索未完成，D 类不可达 → 该 pair 检索未完成；`silent_skip_forbidden: true`。

### 检索粒度

A／B／C 三类的疾病级检索对同一 target 在 9 个 context 下结果相同，**按 target 检索一次**（41 次）即可，避免 369 次冗余检索；D 类情境特异性富集**按 pair 判定**（369 次）。此项写明是为了让「检索次数」这个数字不被误读。

## 五、LOCK-03 求值规则与冻结优先级

优先级（v0.2.0）：`L3-00` → `L3-01` → `L3-02` → `L3-03` → `L3-04` → `L3-05`。

理由：**先判实体是否消歧——符号未消歧时检索结果既不能支持也不能排除**；
再判检索与 assertion 抽取是否完成——未完成时「没找到」无法与「不存在」区分；再判是否存在与该 context 匹配的 CRC-specific 证据；再判疾病级证据遇亚群 context 的降级；再判仅有其他癌种 precedent 的降级；以上都不成立且检索已完成，才允许判定完整检索后无 linkage。

| ID | 条件 | outcome | disposition | state |
|---|---|---|---|---|
| `L3-00` | target 符号不可消歧 | `linkage_evidence_missing` | DEFER | hold |
| `L3-01` | 未完成规定检索或 assertion 抽取 | `linkage_evidence_missing` | DEFER | hold |
| `L3-02` | 有 A/B/C 任一 CRC-specific 证据，且 context 为 canonical，或亚群且有 D 类证据 | `linkage_evidence_exists` | **RETAIN** | active |
| `L3-03` | 有 CRC 疾病级证据，但 context 为亚群且无 D 类 | `linkage_unassessed` | DEFER | hold |
| `L3-04` | 仅有其他癌种 precedent | `linkage_unassessed` | DEFER | hold |
| `L3-05` | 完成规定检索且四类均无命中 | `no_known_linkage_after_complete_search` | EXCLUDE | reactivation-eligible |

**只有 `L3-02` 可以 RETAIN，只有 `L3-05` 可以 EXCLUDE**，测试断言各自恰好一条。`L3-05` 的 EXCLUDE 语义严格限定为 `EXCLUDE_FROM_ACTIVE_POOL`：`is_scientific_disproof: false`、`is_killed: false`、`retained_in_eligible_universe_index: true`，并须六项检索完整性字段齐备。

测试用参考实现穷举 `identity_resolved × search_complete × crc_specific × canonical × class_d × other_cancer`
全部 **64 种组合**，证明每种恰好命中一条规则，且六条规则都可达。
另有一条专门的测试断言：**未消歧实体在任何组合下都落 `L3-00`，永远无法被 `L3-05` 排除。**

## 六、本契约不给出预期结果形状

这与 EVGAP-01 不同，且是有意的。

EVGAP-01 读取的是已固定的数据集，结果可以事先算出并逐项核对（22／19）。**EVGAP-02 是发现型检索，事先给出这类数字就会把预测冒充成结果**——正是来源文档列为第二种必须避免的混淆。

因此本契约不预测计数，改为冻结 `declared_search_scope`、`search_complete_definition`、`derivation_precedence`、provenance 要求与输出验证，使完整性与每一条 disposition 都可事后核验。测试断言 `predicted_result_shape.provided = false`，且不得以任何别名偷偷塞入计数。

## 七、输出与 provenance 分层

**两张表，且两表之间有稳定的一对一引用关系。**

`evidence` 表每条证据一行，**19 列**，含来源文档规定的 13 列必需最小集，外加 `evidence_id`（唯一）、`linkage_class`、`is_adc_efficacy_evidence`、`positive_fraction_or_prevalence`、`malignant_cell_attribution`、`retrieved_at`。

`disposition` 表每个 pair 一行，**30 列**，含 `rule_id`、六项检索完整性字段、六个 D 类 pair 级字段、`provenance_kind`、`provisional_only`、`may_advance_to_level_02`，以及**三组证据引用**：`supporting_evidence_refs`、`class_d_evidence_refs`、`other_cancer_evidence_refs`。

### 为什么需要这三组引用

初稿的 disposition 表只有 `evidence_row_count`——**单条 disposition 无法证明自己由哪些 evidence 行支持**。审核裁决指出，`L3-02` RETAIN 应当能回答：哪条 A/B/C 证据支持？subgroup RETAIN 时哪条 D 证据支持？是否有其他癌种 precedent 但没被错误算入 linkage？初稿都答不了。

每条规则必须引用什么、必须不引用什么，已逐条冻结（`VAL-L17`）：

| 规则 | `supporting_evidence_refs` | `class_d_evidence_refs` | `other_cancer_evidence_refs` |
|---|---|---|---|
| `L3-01` | 必须为空 | 必须为空 | 可空（不得伪造） |
| `L3-02` canonical | 至少一条 A/B/C | 可空 | 可有但不得计入 linkage |
| `L3-02` subgroup | 至少一条 A/B/C | **至少一条** | 可有但不得计入 linkage |
| `L3-03` | 至少一条疾病级 CRC 证据 | **必须为空** | 可空 |
| `L3-04` | **必须为空** | 必须为空 | 至少一条 |
| `L3-05` | 必须为空 | 必须为空 | 必须为空（检索 provenance 须完整） |

另加 `VAL-L16`（每个引用的 id 必须存在于 evidence 表，且所引用行的 `pair_id` 与该 disposition 一致）与 `VAL-L20`（`evidence_row_count` 必须等于三组 refs 去重后的总条数，不得只报计数不给 refs）。

**三种 `provenance_kind`，要求不同**（这是 PR #59 阻断 3 的教训）：

| kind | 必填 | 可空 |
|---|---|---|
| `source_supported` | `source_ref`、`source_locator`、`retrieved_at` | `no_evidence_found_reason` |
| `no_evidence_found_after_complete_search` | 六项检索完整性字段 + `no_evidence_found_reason` | `source_ref`、`source_locator` |
| `search_incomplete` | `search_complete`、`search_scope`、`searched_at`、`no_evidence_found_reason` | `source_ref`、`source_locator` |

后两种**禁止伪造 source evidence**；出现非空 `source_ref` 即为验证失败（`VAL-L08`）。

每个 `conditionally_required_columns` 块都写明 `table`（`evidence` 或 `disposition`），**测试逐表检查必填列，不再用两张表列的并集代替**（`VAL-L09`）——初稿用并集，恰好掩盖了阻断 2 那个问题。

**20 条**验证规则 `VAL-L01`..`VAL-L20` 见 YAML。

## 八、必须写进结果报告的六条

- **`MF-L01`**：LOCK-03 RETAIN 只表示存在可回溯的 CRC-specific linkage 证据，**不表示该靶点适合 ADC、不表示疗效、不表示治疗窗**。
- **`MF-L02`**：C 类证据证明 target 在 CRC 中可接近或可干预，**不是 ADC 疗效证据**，必须原样标注。
- **`MF-L03`**：本次抽取未使用任何派生本地数据库，检索完整性只在 Tier 1 声明范围内成立。
- **`MF-L04`**：LOCK-03 RETAIN **不使 pair 进入 Level 02**。`EVGAP-01` 未解除前 `may_advance_to_level_02` 恒为 `false`。
- **`MF-L05`**（v0.2.0）：检索命中不是 linkage 证据。报告必须分别给出 `retrieval_candidate_count` 与 `assertion_count`；只报候选数即冒充证据量。
- **`MF-L06`**（v0.2.0）：落 `L3-00` 的 pair 既未被支持也未被排除，**不得**与 `L3-05` 合并计数，也不得表述为「无 linkage」。

## 九、授权与不授权

**授权：** 按本契约执行抽取，读取 Tier 1 来源，覆盖全部 369 个 pair。
`L-RETRIEVAL` 层已执行一次（`gen_iet_evgap_02_crc_linkage_20260805T190453Z` revision 2）。

**不授权：** 执行 Level 01；解除 `EVGAP-01`；读取任何 Tier 2 派生本地数据库；把任何派生数据库纳入已批准来源；评估 T2、T7 或任何 Gate；新增靶点或 clinical context；任何筛选排序、Tier 划分、资产推荐或实验建议；引入被隔离运行（PR #53、#54）的任何产物。

## 十、后续顺序

1. v0.2.0 契约与 `L-RETRIEVAL` 层产物 `APPROVE`。
2. **另开 PR** 处理 `GAP-P07`：四个实体解析为标准符号、定义为非蛋白抗原，或移出轴。
   移出会改动 41／369 这两个冻结计数，故必须经审核。
3. `GAP-P07` 处理后执行 `L-ASSERTION` 抽取 → 结果 PR → `APPROVE`。
4. **再另开 PR** 更新 `adc_pool_level_01_input_binding.yaml`，绑定产物并解除 `EVGAP-02`。
5. `EVGAP-01` 由 Track B 独立推进（`SRCADM-01` → 抽取 → 结果 → binding）。
6. **两个缺口都解除后，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。**

## 十一、当前阻断

- `L-ASSERTION` 层未执行，故 **`EVGAP-02` 未解除**。
- `GAP-P07` 未处理前，36 个 pair 无法脱离 `L3-00`。
- `EVGAP-01` 亦未解除，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。
