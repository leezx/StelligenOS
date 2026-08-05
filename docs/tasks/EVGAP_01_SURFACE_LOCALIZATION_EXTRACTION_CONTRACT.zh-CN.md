# EVGAP-01：target surface localization 证据抽取契约

- 任务分支：`task_20260804_evgap-01-surface-localization-contract`
- 前置工作包：PR #57（Level 01 判据定义）、PR #58（输入绑定与缺口登记），均已 `APPROVE` 并合并
- 机器可读绑定：[`../pools/evgap_01_surface_localization_extraction.yaml`](../pools/evgap_01_surface_localization_extraction.yaml)，由 `tests/test_evgap_01_surface_localization.py` 校验
- 当前状态：**contract-only，未执行，等待 ChatGPT 审核**
- 授权范围：**一次证据抽取运行。不授权执行 Level 01。**

## 目的

解除 PR #58 登记的 `EVGAP-01`，使 Level 01 的 `LOCK-01` 能够真正产出 `eligible_surface_target`。

PR #58 的实测结论是：已批准证据层里 `plasma membrane`／`extracellular`／`localization`／`signal peptide`／`GPI` 关键词命中数**均为 0**，只有 `transmembrane_segment_count`，而跨膜拓扑不足以判定细胞外可及。因此 41 个靶点全部落 `possible_surface_target`，`eligible = 0`，Level 01 无法录入任何 pair。

本契约冻结一次抽取运行的范围、来源、字段白名单、判据映射与输出验证。**不执行抽取，不执行 Level 01。**

## 一、需要审核方裁决的治理事实：本次请求纳入一个从未被批准的数据库

所需数据**已经存在于本地**：`DATA/1.Databases/ADC_surfaceome_reference/processed/v0.3.0`。但必须先讲清楚它的治理状态：

> **`ADC_surfaceome_reference` 从未被审核批准过。** 仓库内 `logs/chatgpt-review-*.md` 没有任何一条提及 surfaceome；`logs/worklog.md` 里唯一的提及是 2026-08-01 一次 mock 运行。已获批的证据抽取（PR #31）在其 `source_manifest.json` 中声明的来源是 `ADC_internalization_reference`，**没有接入本库**——这正是已批准层只有跨膜段注释、没有质膜定位证据的直接原因。

因此本 PR 请求把**这一个版本**纳入已批准来源集合：`dataset_version 0.3.0`、`snapshot_id 2026-07-29-quant-topology-mm`、`raw_manifest_sha256 884f4191…`，四个文件逐一记录 SHA-256（`surfaceome_consensus.tsv` 20,797 行、`membrane_topology_evidence.tsv` 4,863 行、`source_evidence.tsv` 41,204 行、`build_manifest.json`）。执行前必须逐个校验，任一不一致即中止（`VAL-E06`）。

### 主张纳入它的核心理由：守卫是它构建时就写死的，不是本契约事后附加的

该库自身的 `build_manifest.json` → `consensus_semantics` 已经编码了本仓库反复要求的语义：

| 该库的声明 | 对应仓库规则 |
|---|---|
| `absence_is_negative_evidence: false` | 缺失证据一律 DEFER，永不 EXCLUDE |
| `membrane_topology_is_independent_surface_localization: false` | **PR #58 第二轮阻断本身**——跨膜段不足以判定细胞外可及 |
| `generic_membrane_is_surface_confirmation: false` | 泛膜注释不等于质膜定位 |
| `cci_receptor_role_is_surface_confirmation: false` | 受体角色推断不等于定位证据 |
| `tumor_ihc_is_surface_density: false` | 表达强度不等于表面密度（属 Level 02 T7） |
| 排除 `GSE160572_MM_surfaceome.csv.gz`，理由是「processed values are RNA FPKM, not direct surface-protein measurements」 | RNA 不得当作蛋白层面验证，无例外 |

该库还自设 `full_t7_gate_confidence_cap: 0.55`，并在 note 中明确它「does not establish a general malignant-cell positive fraction, isoform usage, calibrated treatment stability, or ADC accessibility」——即它自己就把 Level 02 的边界划开了。

## 二、抽取范围

只处理已批准枚举的 41 个靶点（`target_evidence_catalog.tsv`，SHA-256 `27bb81eb…`），**不新增任何靶点**，按 `gene_symbol` 连接。

实测覆盖：**37 覆盖 / 4 未覆盖**。未覆盖的是 `AG7`、`CA19-9`、`EDBN`、`Undisclosed`——两个占位符、一个碳水化合物抗原、一个非标准符号。四者一律落 `possible_surface_target` DEFER（`E1-05`）。

## 三、字段白名单与明确禁止读取的内容

只允许读 `surfaceome_consensus.tsv` 的 16 个字段与 `source_evidence.tsv` 的 8 个字段（清单见 YAML `allowed_fields`）。

**禁止读取以下文件**，读入即重演 PR #58 被阻断的越界：

| 文件 | 理由 |
|---|---|
| `tumor_surface_measurement.tsv` | 肿瘤表面定量属 Level 02 T7 |
| `tumor_protein_context.tsv` | 肿瘤上下文蛋白组属 Level 02 T7 |
| `treatment_surface_response.tsv` | 治疗后表面变化属 T5／T7 |
| `receptor_evidence.tsv` | 受体角色推断不构成定位证据（该库自身亦声明 `cci_receptor_role_is_surface_confirmation: false`） |

**禁止读取以下字段**：`cci_receptor_role`（角色不是定位）、`uniprot_generic_membrane`（泛膜不等于质膜）、`full_t7_gate_confidence_cap`（T7 置信属 Level 02）。

## 四、判据映射

### `RQ-01` 质膜定位：要求 ≥ 2 个独立证据家族

判决字段是 `independent_evidence_family_count`。该库定义的三个独立家族为 `curated_knowledge`／`imaging`／`cell_surface_capture_ms`，且**已把拓扑与泛膜排除在家族计数之外**——所以家族计数在结构上不可能把跨膜段当成定位证据。RNA 不得满足。

### `RQ-02` 细胞外结构域：两条合格路径

| 路径 | 条件 | 适用 | 实测 |
|---|---|---|---|
| `ECD-a` | `uniprot_ecd_meets_min_length = true` | 有跨膜段且带 TOPO_DOM Extracellular 注释 | **18** |
| `ECD-b` | `uniprot_gpi_anchor = true` 且 `uniprot_signal_peptide = true` 且 `uniprot_transmembrane_segment_count = 0` | GPI 锚定、带信号肽、零跨膜段 | **4** |

**`ECD-b` 是必需的，理由是修正数据表示假象而不是放宽标准。** UniProt 的 extracellular domain 字段由跨膜蛋白的 TOPO_DOM 推导；GPI 锚定蛋白零跨膜段、没有 TOPO_DOM，该字段一律读成 `false`。若只用 `ECD-a`，`CEACAM5`、`MSLN`、`FOLR1`、`MELTF` 会因此落 hold——而四者在本库中都是 `confirmed_surface`，都带信号肽与 GPI 锚，成熟蛋白整体位于细胞外侧。GPI 锚 + 信号肽 + 零跨膜段在结构上即意味着全长成熟蛋白朝向胞外，其胞外长度等于成熟蛋白长度。

**腔内结构域不算胞外。** `LAMP1` 即属此类：有跨膜段与信号肽，但无胞外 TOPO_DOM，两条路径都不满足，落 hold。这正是审核方要求的「细胞器膜定位必须 DEFER」，规则自然落在正确一侧。

### `RQ-03` 蛋白层面 provenance

要求 `source_evidence.tsv` 中存在对应行，且 `source_id`、`source_release`、`evidence_family`、`source_url`、`license` 均非空。RNA 来源行不可采纳。

## 五、确定性映射：五条规则覆盖 41 个靶点，零排除

| ID | 条件 | outcome | disposition | 数量 |
|---|---|---|---|---|
| `E1-01` | `RQ-01`＋`RQ-02`＋`RQ-03` 全满足且无冲突 | `eligible_surface_target` | RETAIN | **22** |
| `E1-02` | `RQ-02` 满足但独立家族数 < 2 | `possible_surface_target` | DEFER | **6** |
| `E1-03` | 两条 `RQ-02` 路径都不满足（含腔内结构域） | `possible_surface_target` | DEFER | **3** |
| `E1-04` | `discordance_flags` 非空 | `possible_surface_target` | DEFER | **6** |
| `E1-05` | 靶点不在参考库中 | `possible_surface_target` | DEFER | **4** |

22 + 6 + 3 + 6 + 4 = 41。**零自由裁量、零排除。**

- `E1-02`：`CLDN18`、`GUCY2C`、`LGR5`、`PRLR`、`RNF43`、`SLC44A4`
- `E1-03`：`LAMP1`、`TDGF1`、`TM4SF1`
- `E1-04`：`CD276`、`F3`、`IL2RA`、`MET`、`MST1R`、`TACSTD2`
- `E1-05`：`AG7`、`CA19-9`、`EDBN`、`Undisclosed`

`not_surface_target` 与 `identity_unresolved` **仍然不可用**：该库明确 `absence_is_negative_evidence: false`，不产出「该靶点不是表面蛋白」这类阳性否定断言；`consensus_class = no_surface_support` 只表示无支持证据，不等于已证伪。**本次抽取不得排除任何靶点。**

## 六、抽取后的预期结果，逐项可核对

| 量 | 值 |
|---|---|
| 靶点总数 | 41 |
| eligible | **22**（`ECD-a` 18 + `ECD-b` 4） |
| hold | **19**（6 + 3 + 6 + 4） |
| killed | **0** |

**执行结果必须逐项等于上表，任一项不符即视为偏离本契约。**

## 七、必须写进结果报告的三条发现

- **`MF-01`：`GUCY2C` 落 hold。** 它在本参考库中只有 `curated_knowledge` 一个独立证据家族，未达两家族门槛，`consensus_class` 是 `supported_surface` 而非 `confirmed_surface`。**这与此前多模型共识把 GUCY2C 列为首选、以及被隔离运行的 Tier A 选择相反。** 结果报告必须原样写出，不得因与既有偏好冲突而弱化。
- **`MF-02`：`eligible` 只表示身份与拓扑层面存在有合理依据的细胞外可及蛋白形式**，不表示该靶点在 CRC 肿瘤细胞表面可得。后者是 Level 02 的 T7，本次未评估。
- **`MF-03`：零排除。** 41 个靶点中没有任何一个被判为 `not_surface_target`。hold 不是淘汰，是待证据。

## 八、输出与验证

输出为每靶点一行、21 列（见 YAML `output_schema`），必含 `rule_id`、`rq_02_path`、`evaluation_status`、provenance 与 `row_checksum`。十条验证规则 `VAL-E01`..`VAL-E10` 见 YAML，要点：41 行且每行命中且仅命中一条规则；计数等于第六节；不得出现 `not_surface_target` 或 `identity_unresolved`；每个 eligible 必记 `rq_02_path`；provenance 缺失即降为 hold；输入 SHA-256 不一致即中止；不得读取被禁文件或字段；输出中不得出现任何 Gate 分数、Gate 状态、T7 判定或肿瘤表面定量；三条 `mandatory_findings` 必须原样出现；每个产物文件逐文件记录 SHA-256。

## 九、本契约授权与不授权

**授权：** 把 `ADC_surfaceome_reference@0.3.0`（指定 snapshot 与校验和）纳入已批准来源；按本契约执行**一次**抽取运行。

**不授权：** 执行 Level 01；评估 T7 或任何肿瘤细胞表面可得性；新增任何靶点或 clinical context；任何筛选排序、Tier 划分、资产推荐或实验建议；任何 Gate 执行或评分；读取被禁文件或字段；把被隔离运行（PR #53、#54）的任何产物引入。

## 十、后续顺序

1. 本契约获 `APPROVE`。
2. 执行抽取 → 结果 PR → `APPROVE`。
3. **另开一个 PR** 更新 `adc_pool_level_01_input_binding.yaml`，把抽取产物绑为 `LOCK-01` 的来源并解除 `EVGAP-01`。该 PR 不在本契约授权范围内。
4. `EVGAP-02`（`LOCK-03` 的源级 CRC linkage 证据）仍未解除，需其独立契约。**两个缺口都解除后，Level 01 才能执行。**

## 十一、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行抽取。
- 抽取完成也**不**解除 `EVGAP-02`，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。
