# Handoff：EVGAP-02 Tier 1 检索候选层 + 契约 v0.2.0（revision 2）

- 日期：`2026-08-05`
- 任务分支：`task_20260805_evgap-02-extraction-result`
- 基线：`main` @ `8aa7e87`
- 本修订依据：**PR #62 审核 `REQUEST_CHANGES`**
- 外部运行：`gen_iet_evgap_02_crc_linkage_20260805T190453Z` **revision 2**
- 交付物类型：**契约修订 + 结果降级（外部运行留痕）**
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**
- **结论：`EVGAP-02` 未解除。本运行只完成 `L-RETRIEVAL` 层。**

## 一、审核意见成立，逐条实测复核

审核方指出：这些是搜索命中，不是 linkage evidence。**在改动任何东西之前先对实际文件逐条核验，全部成立。**

1. **7,067 行全部 `evidence_direction = unknown`、`review_status = machine_retrieved_requires_human_review`。**
2. **没有任何一行带有已解析的断言字段**——实测比审核描述更彻底：
   `positive_fraction_or_prevalence` 在 7,067 行中**全为空**，
   `is_adc_efficacy_evidence` 全为 `false`，
   `malignant_cell_attribution` 全为 `unresolved`／`not_applicable`，
   5,699 条文献行的 `protein_or_rna` 全为 `unresolved`。**一条已抽取的断言都没有。**
3. **实体消歧从未做过。**
4. **`ClinicalTrials.gov` 只用宽查询**，未解析 intervention／target／modality／indication，未验证同臂。
5. **`GEO` 的 `db=gds` 元数据命中被登记为 A 类**（666 行）。
6. **D 类 218 行全部 `literature_record`，prevalence 空、attribution `unresolved`**——共现而非富集。

### 一处需要更正的细节

审核意见说 TCGA 与 HPA 的命中「被算作 A 类证据」。**实测：它们没有产生任何证据行。**
证据表的 `source_ref` 前缀只有四种：`PMC` 3,240、`PubMed` 2,459、`ClinicalTrials.gov` 702、`GEO` 666。
两者的检索被执行并计入覆盖，但未登记为证据。

**原则完全成立，实际的实例是 `GEO`。** v0.2.0 把三个 dataset endpoint 一并禁用为 A 类依据。

### 一处比审核意见更严重的发现

**`Undisclosed` 不是实体，是缺失值占位符**，却被当作基因符号检索：`PMC/A` 返回 **1,384** 条，产出 1 个 RETAIN。

`CA19-9`（糖类抗原，无 HGNC 符号）：`PMC/A` **14,200** 条，9 个 pair 中 **8 个 RETAIN**。

`EDBN`：11 个 endpoint **全部 0 命中**，9 个 pair 落 `L3-05` **EXCLUDE**。
它疑指 fibronectin 的 extra domain B（标准符号 `FN1`）——
**被排除的唯一原因是这个缩写本身不通行于文献。消歧失败被当成了完整检索后的阴性结论。**

### 一处自查发现、审核未提的缺陷

**未披露的检索截断。** 451 次检索报告命中合计 **718,140**，实际登记 **979** 条；
**333／451 次检索被截断**，绝大多数每组只留 **3** 条。revision 1 未声明此上限却宣称检索完整。

## 二、根因在契约，不只在执行

v0.1.0 把 `evidence_direction` 与 `review_status` 列为**必需列，却没有任何一条规则要求它们被解析**。
`linkage_class` 也没有任何规则约束其来源，于是它由**查询类别**决定。
**一次完全合规的执行因此产出了 168 条 RETAIN。** 这是契约漏洞，修必须修在契约上。

## 三、契约 v0.2.0

### 三层结构

| layer | 产物 | 可支撑 LOCK-03 |
|---|---|---|
| `L-RETRIEVAL` | `retrieval_candidates` | **否** |
| `L-ASSERTION` | `linkage_assertions` | 是 |
| `L-DISPOSITION` | `pair_linkage_disposition` | 只能引用 assertion |

`assertion_requirements` 规定六个构成要件（target／CRC／context 实体消歧、`relationship_type`、
`assertion_direction`、`supporting_text_or_structured_field`），并**硬性禁止 `assertion_direction = unknown`**——
这正是 v0.1.0 漏掉 7,067 行的那道检查。

`linkage_class` 由 assertion 内容判定；候选表改记 `query_class_label`，且**候选表不得含 `linkage_class` 列**。

### 关于 `DECISION-02`

PR #58 允许机器抽取的证据满足 LOCK-03 existence——**前提是机器已抽出一条具体、可审计的 assertion**。
v0.1.0 停在候选。这一读法写进了 `L-ASSERTION.machine_extraction_permitted_basis`，人工复核要求不变。

### 实体消歧与 `L3-00`

新增 `L3-00`，置于优先级最前。关键是**不对称**：未消歧实体既不得 RETAIN，
也**绝不得** EXCLUDE——`unresolved_may_not_exclude` 直接以 `EDBN` 为例写明。

`L3-00` **不引入新 outcome**：LOCK-03 的词表由 PR #57 冻结，其中没有 `identity_unresolved`
（该 outcome 只属于 LOCK-01）。故 `L3-00` 复用 `linkage_evidence_missing`，
其 `evidence_state = absent_incomplete_search` 恰好正确，身份信息另由
`identity_resolution_status` 列承载。

四个实体在 target 轴上同属 `rq_01_family_count = 0`、规则 `E1-05`，
故识别它们**不依赖自由裁量**（`mechanical_precondition`）。

### endpoint 命中证明了什么

新增 `endpoint_evidence_admissibility`，逐 endpoint 写明 `hit_proves` 与 `hit_does_not_prove`。
TCGA／HPA／GEO 三者 `admissible_as_class_a: false`，
但**仍为必查**（服务于覆盖与身份消歧），其命中不计入 `linkage_classes_hit`。
`ClinicalTrials.gov` 须记录五个结构化字段并满足**同臂**要求。

### 检索完整性

`search_complete` 现在需要四层：身份消歧、endpoint 覆盖、pair 级 D 类、**assertion 抽取完成**。
`retrieval_alone_is_not_search_complete: true`。

新增 `VAL-L21`..`VAL-L28`。

## 四、结果降级（revision 2）

| | revision 1 | revision 2 |
|---|---|---|
| 证据表 | `pair_linkage_evidence.tsv` 7,067 行 | 撤销 → `retrieval_candidates.tsv` **979** + `linkage_assertions.tsv` **0** |
| `L3-02` RETAIN | 168 | **0** |
| `L3-03` | 192 | 0 |
| `L3-05` EXCLUDE | 9 | **0** |
| 全部 369 pair | 三分 | **全部 DEFER / hold** |

**未重复任何网络调用，未丢弃任何已检索记录。**

979 与 7,067 的关系：A/B/C 按 target 检索一次，revision 1 把每条记录复制到 9 个 context 上。
`A 2808/9=312`、`B 2295/9=255`、`C 1746/9=194`、`D 218`（pair 级不复制），合计 **979**。
**「7,067 条证据」实为 979 条记录乘以 9。**

369 个 pair：`L3-00` **36**（4 个不可消歧实体 × 9）、`L3-01` **333**（assertion 层未执行）。
三组 `*_evidence_refs` 在 369 行中全空。

## 五、上游缺陷 GAP-P07（登记，不修）

PR #58 冻结的 41 个 target 中至少四个不是可消歧的蛋白实体。
`EVGAP-02` 无权改轴——在本契约内给 `Undisclosed` 编一个身份等于静默改轴。

**binding 本身已察觉这一点**：它把 `identity_unresolved` 列入 `unavailable_outcomes`，
理由是「已批准层没有身份解析结论字段」。四个实体因此以 `E1-05` 留在轴上。
**缺陷在 PR #58 时已可见，只是当时无法表达。**

修复须另开 PR，且会改动 41／369 这两个冻结计数。

## 六、产物与校验

外部包 **revision 2**（仓库内无任何数据文件）：

| 文件 | 行数 | SHA-256 |
|---|---|---|
| `retrieval_candidates.tsv` | 979 | `09a2aa75ee7885ed9be3807d8c074e8a31fb81bef6bfff27728181831e5c326a` |
| `linkage_assertions.tsv` | 0 | `f0c83e0e2fb0aa13e354babe00164d9287c226bd6d7229c29434d664f744ee8b` |
| `pair_linkage_disposition.tsv` | 369 | `a43b47c874f9a70e3e3b4de11941ef9c87765f06bce5098247ac87d06351598d` |
| `search_log.tsv` | 451 | `dd0569c572bfd09f74f034f1844811c918182c767118e963afc9ed0a14c7ce08` |
| `run_report.md` | — | `9359ac1cc0c25ea3a3e7de06f8f5bd23270bed390db1a6fe7bdbe246e4846059` |
| `external_run_worklog.md` | — | `028a7c2f11a2b6b15b5f651c9f5826f6ee3eeee6f05cd7ebc3c2488e7c361c96` |
| `source_manifest.json` | — | `9fb1f2f75429e438d343a097eabdedeff44ae0f819cc346f71212f64b1647202` |

**打包件**（按 PR #60 审核后确立的规则，每个修订单独出包并各带自己的 SHA-256）：

- `gen_iet_evgap_02_crc_linkage_20260805T190453Z_rev2.zip`
- SHA-256 `e8f2a7f5ce9fae25265994f0d9a1fae1e371a1bb55ccafea2026835bd5120d3d`
- 41,734 bytes，8 个条目

仓库内变更：契约 v0.2.0、契约文档、测试、本 handoff、一条 worklog。
`tests/test_evgap_02_crc_linkage.py` **44 个测试**通过；全库 `Ran 353 tests` OK。
外部产物另经 25 项 v0.2.0 规则核验，全通过。

## 七、边界

未运行任何 Gate，无评分、无排序、无 Tier、无资产推荐、无实验建议；
未新增或修改靶点与 clinical context；未读取任何 Tier 2 派生库；
未引用被隔离运行（PR #53、#54）的任何产物；未写入任何数据文件到仓库。
369 个 pair 的 `may_advance_to_level_02` 全部 `false`。

## 八、后续顺序

1. 本 PR `APPROVE`（契约 v0.2.0 + `L-RETRIEVAL` 层产物），在 `logs/` 留审核记录。
2. **另开 PR** 处理 `GAP-P07`：四个实体解析为标准符号、定义为非蛋白抗原，或移出轴。
3. `GAP-P07` 处理后执行 `L-ASSERTION` 抽取 → 结果 PR。
4. 两层齐备后才谈解除 `EVGAP-02`。
5. `EVGAP-01` 走另一条独立轨道（`SRCADM-01` 在 PR #63 待审）。
6. **两个缺口都解除后**，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
