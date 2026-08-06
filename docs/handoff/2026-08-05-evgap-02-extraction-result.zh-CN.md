# Handoff：EVGAP-02 Tier 1 检索候选层 + 契约 v0.2.0（revision 3）

- 日期：`2026-08-05`
- 任务分支：`task_20260805_evgap-02-extraction-result`
- 基线：`main` @ `8aa7e87`
- 本修订依据：**PR #62 第一轮与第二轮 `REQUEST_CHANGES`**
- 外部运行：`gen_iet_evgap_02_crc_linkage_20260805T190453Z` **revision 3**
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
故**筛出**它们不依赖自由裁量。但该字段只用于筛候选，**不决定** `resolution_status`，
也不决定是否落 `L3-00`——`CA19-9` 同属 `E1-05`，却已消歧。这正是第二轮的教训。

### endpoint 命中证明了什么

新增 `endpoint_evidence_admissibility`，逐 endpoint 写明 `hit_proves` 与 `hit_does_not_prove`。
TCGA／HPA／GEO 三者 `admissible_as_class_a: false`，
但**仍为必查**（服务于覆盖与身份消歧），其命中不计入 `linkage_classes_hit`。
`ClinicalTrials.gov` 须记录五个结构化字段并满足**同臂**要求。

### 检索完整性

`search_complete` 现在需要四层：身份消歧、endpoint 覆盖、pair 级 D 类、**assertion 抽取完成**。
`retrieval_alone_is_not_search_complete: true`。

新增 `VAL-L21`..`VAL-L29`。

## 四、结果降级（revision 3）

| | revision 1 | revision 3 |
|---|---|---|
| 证据表 | `pair_linkage_evidence.tsv` 7,067 行 | 撤销 → `retrieval_candidates.tsv` **979** + `linkage_assertions.tsv` **0** |
| `L3-02` RETAIN | 168 | **0** |
| `L3-03` | 192 | 0 |
| `L3-05` EXCLUDE | 9 | **0** |
| 全部 369 pair | 三分 | **全部 DEFER / hold**（`L3-00` 27 + `L3-01` 342） |

**未重复任何网络调用，未丢弃任何已检索记录。**

979 与 7,067 的关系：A/B/C 按 target 检索一次，revision 1 把每条记录复制到 9 个 context 上。
`A 2808/9=312`、`B 2295/9=255`、`C 1746/9=194`、`D 218`（pair 级不复制），合计 **979**。
**「7,067 条证据」实为 979 条记录乘以 9。**

369 个 pair：`L3-00` **27**（3 个**不可消歧**实体 `Undisclosed`／`EDBN`／`AG7` × 9）、
`L3-01` **342**（assertion 层未执行，含 `CA19-9` 的 9 个 pair）。
三组 `*_evidence_refs` 在 369 行中全空。

### 第二轮审核指出的矛盾，以及我为什么会犯

revision 2 给出 36／333，把 `CA19-9` 也放进 `L3-00`。**这与契约直接冲突**：
契约把它定为 `resolved_as_non_protein_antigen`，而 `search_complete_definition`
明确接受该 status——**它是已消歧的实体，不是身份未解析**。

根因在我自己的命名与实现：契约那张表叫 `known_unresolved_entities`，
里面却有一个 **resolved** 的条目；重建脚本按**表成员身份**而非按 `resolution_status`
赋 `L3-00`。**名字招来了这个 bug，脚本接受了邀请。**

修在失效点而非症状：表改名 `known_identity_findings`；新增 `l3_00_statuses`；
`l3_00_membership_test: resolution_status`；`l3_00_membership_by_list_forbidden: true`；
每个条目显式声明其 status 蕴含的 `lock_03_rule`。

采用审核建议的**方案一**：`CA19-9` 保持 `resolved_as_non_protein_antigen`，转入 `L3-01`。
它 defer 的原因是 assertion 层未执行，**外加** v0.1.0 按基因符号检索糖类抗原的查询形式无效——
**不是**身份不明。新增 `non_protein_antigen_search_requirements` 与 `VAL-L29` 固定这一区分。

验证脚本的 `L3-00` 期望集**由契约推导**（按 `resolution_status` 过滤），不是硬编码，
因此同类错误再犯会被捕获。

## 五、上游缺陷 GAP-P07（登记，不修）

PR #58 冻结的 41 个 target 中至少四个的身份需单独裁定，且**四者性质不同**：
`Undisclosed` 不是实体；`EDBN`、`AG7` 是无法消歧的缩写；
**`CA19-9` 已消歧，只是不是蛋白**——非蛋白抗原是否属于「所有潜在 ADC 膜蛋白靶点」
这一 target universe，才是 `GAP-P07` 真正要回答的问题。

`EVGAP-02` 无权改轴——在本契约内给 `Undisclosed` 编一个身份等于静默改轴。

**binding 本身已察觉这一点**：它把 `identity_unresolved` 列入 `unavailable_outcomes`，
理由是「已批准层没有身份解析结论字段」。四个实体因此以 `E1-05` 留在轴上。
**缺陷在 PR #58 时已可见，只是当时无法表达。**

修复须另开 PR，且会改动 41／369 这两个冻结计数。

## 六、产物与校验

外部包 **revision 3**（仓库内无任何数据文件）。**8 个文件**，ZIP 内 9 个条目（多出的一条是目录条目）：

| 文件 | 行数 | SHA-256 |
|---|---|---|
| `retrieval_candidates.tsv` | 979 | `09a2aa75ee7885ed9be3807d8c074e8a31fb81bef6bfff27728181831e5c326a` |
| `linkage_assertions.tsv` | 0 | `f0c83e0e2fb0aa13e354babe00164d9287c226bd6d7229c29434d664f744ee8b` |
| `pair_linkage_disposition.tsv` | 369 | `33674913edf0d1efb82f4bc2a8303e55e18f2a39a32ba7b2dd3152c5f6734dad` |
| `search_log.tsv` | 451 | `dd0569c572bfd09f74f034f1844811c918182c767118e963afc9ed0a14c7ce08` |
| `run_report.md` | — | `4c4def27c73853ab175c9610c58bcb41c6765276cec133e71f161ee9a7dfc2ac` |
| `external_run_worklog.md` | — | `0db30b1e0e0fa5e98637619275d595729cb30c2b90fdcaad913ae7e8a1565cd7` |
| `verify_package.py` | — | `63bd46eb220a6d12be594ad809b03a933dbd3b2901d7d5d9a4d1e7d9b3701bcf` |
| `source_manifest.json` | — | `776677c571725060175e3e480936e8f17eeeebb3ee67d5472c2a52c114a5265f` |

**打包件（唯一正式受审包）：**

- `gen_iet_evgap_02_crc_linkage_20260805T190453Z_rev3.zip`
- SHA-256 `81baa45f23f180c68b16d18c83284b60bdee725c017e668e590d4e80b04176e9`
- 46,292 bytes，8 个文件（ZIP 内 9 个条目）
- `revision = 3`

**上一版声明的 ZIP SHA-256 `ef268fd2…` 作废**——包内新增了 `verify_package.py`，
内容变了哈希必然变。**以本表为准。**

同时更正上一版 handoff 的一处笔误：`pair_linkage_disposition.tsv` 曾被写成
`4c4def27…`，那其实是 `run_report.md` 的哈希。本表由 `source_manifest.json` 直接生成，
不再手抄。

### 包内自带验证脚本

```
python3 verify_package.py .
python3 verify_package.py . --zip ../<pkg>.zip --zip-sha256 <expected>
```

只读包内文件，无网络、无写入、不依赖包外路径，解压即可运行，退出码 0 表示全通过。
逐项检查：文件数、每个文件的 SHA-256 与字节数、清单未遗漏文件、`revision = 3`、
`979 / 0 / 369`、schema（候选表无 `linkage_class`、三个标记列齐备）、
候选表三个固定值、`L3-00 27` / `L3-01 342` / `L3-02..L3-05` 全为 `0`、
无 RETAIN 无 EXCLUDE、369 行全 DEFER/hold、三组 refs 全空、
`may_advance_to_level_02` 全 `false`、三个不可消歧 target 各 9 个 pair 全 `L3-00`、
`CA19-9` 9 个 pair 全 `L3-01` 且 `identity_resolution_status =
resolved_as_non_protein_antigen`、`EVGAP-02` 未解除。

**实测（从全新解压目录运行，含 ZIP 哈希校验）：`65/65 MATCH`，退出码 0。**

仓库内变更：契约 v0.2.0、契约文档、测试、本 handoff、一条 worklog。
`tests/test_evgap_02_crc_linkage.py` **47 个测试**通过；全库 `Ran 356 tests` OK。
外部产物另经包内 `verify_package.py` 核验：**65/65 MATCH**，退出码 0。

## 七、边界

未运行任何 Gate，无评分、无排序、无 Tier、无资产推荐、无实验建议；
未新增或修改靶点与 clinical context；未读取任何 Tier 2 派生库；
未引用被隔离运行（PR #53、#54）的任何产物；未写入任何数据文件到仓库。
369 个 pair 的 `may_advance_to_level_02` 全部 `false`。

## 八、后续顺序

1. 本 PR `APPROVE`（契约 v0.2.0 + `L-RETRIEVAL` 层产物），在 `logs/` 留审核记录。
2. **另开 PR** 处理 `GAP-P07`：`Undisclosed`／`EDBN`／`AG7` 解析为标准符号或移出轴；
   `CA19-9` 则须裁定非蛋白抗原是否属于本 target universe。
3. `GAP-P07` 处理后执行 `L-ASSERTION` 抽取 → 结果 PR。
4. 两层齐备后才谈解除 `EVGAP-02`。
5. `EVGAP-01` 走另一条独立轨道（`SRCADM-01` 在 PR #63 待审）。
6. **两个缺口都解除后**，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
