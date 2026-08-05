# EVGAP-01：target surface localization 证据抽取契约

- 任务分支：`task_20260804_evgap-01-surface-localization-contract`
- 前置工作包：PR #57（Level 01 判据定义）、PR #58（输入绑定与缺口登记），均已 `APPROVE` 并合并
- 机器可读绑定：[`../pools/evgap_01_surface_localization_extraction.yaml`](../pools/evgap_01_surface_localization_extraction.yaml)，由 `tests/test_evgap_01_surface_localization.py` 校验
- 当前状态：**contract-only，未执行，等待 ChatGPT 审核**
- 授权范围：**只冻结抽取边界。抽取本身尚未获授权**——所依赖的数据库 snapshot 必须先通过独立的 source admission PR 取得自己的 `APPROVE`（`SRCADM-01`）。也不授权执行 Level 01。

## 目的

解除 PR #58 登记的 `EVGAP-01`，使 Level 01 的 `LOCK-01` 能够真正产出 `eligible_surface_target`。

PR #58 的实测结论是：已批准证据层里 `plasma membrane`／`extracellular`／`localization`／`signal peptide`／`GPI` 关键词命中数**均为 0**，只有 `transmembrane_segment_count`，而跨膜拓扑不足以判定细胞外可及。因此 41 个靶点全部落 `possible_surface_target`，`eligible = 0`，Level 01 无法录入任何 pair。

本契约冻结一次抽取运行的范围、字段白名单、判据映射与输出验证。**不执行抽取，不执行 Level 01，也不批准所依赖的数据库。**

## 一、所依赖的数据库不由本契约批准（`SRCADM-01`）

所需数据**已经存在于本地**：`DATA/1.Databases/ADC_surfaceome_reference/processed/v0.3.0`。它的治理状态是：

> **该数据库从未被审核批准。** 仓库内 `logs/chatgpt-review-*.md` 没有任何一条提及 surfaceome；`logs/worklog.md` 里唯一的提及是 2026-08-01 一次 mock 运行。已获批的证据抽取（PR #31）在其 `source_manifest.json` 中声明的来源是 `ADC_internalization_reference`，**没有接入本库**——这正是已批准层只有跨膜段注释、没有质膜定位证据的直接原因。

**初稿试图在本契约内直接把它升级为 approved source，那是错的，已按审核裁决更正。** 它是**派生数据库**，不是原始公开数据源。哈希与它自己的语义声明只能证明「读到的就是这个版本」，**不能证明该版本确实遵守它所声明的规则**。

因此纳入已批准来源改由**独立的 source admission PR** 完成，本契约只引用其结论：

- `admission_status: pending_separate_admission_pr`
- `admission_record_ref: null`（本契约不得代填）
- `authorises_extraction_run: false`，`extraction_blocked_by: [SRCADM-01]`
- `VAL-E13`：抽取执行前 `admission_record_ref` 必须指向一份实际存在的独立 `APPROVE` 记录，为空即不得执行

### 那个 admission PR 必须逐项审计的内容

哈希与自声明**不在其列**。

| ID | 审计项 |
|---|---|
| `AUD-01` | builder 实现与版本（`build_t7_surfaceome_reference.py@0.3.0`） |
| `AUD-02` | raw manifest 与 `raw_manifest_sha256 884f4191…` 的对应关系 |
| `AUD-03` | 原始来源清单与各自 release 版本 |
| `AUD-04` | 每个原始来源的 license 与再分发条件 |
| `AUD-05` | `independent_evidence_family` 的独立性是否真实成立，而非同源数据的重复计数 |
| `AUD-06` | 来源去重逻辑 |
| `AUD-07` | `discordance_flags` 的生成规则与覆盖范围 |
| `AUD-08` | 代表性靶点的逐行来源回溯 |
| `AUD-09` | snapshot 是否可由 builder 与 raw manifest 复现 |

### 该库的自声明守卫：待验证项，不是已验证结论

以下六条在本契约中一律标记 `status: claim_pending_audit`。它们是主张 admission 的**理由**，不是 admission 已完成的**证据**：

`membrane_topology_is_independent_surface_localization: false`（正是 PR #58 第二轮阻断本身）、`absence_is_negative_evidence: false`、`generic_membrane_is_surface_confirmation: false`、`cci_receptor_role_is_surface_confirmation: false`、`tumor_ihc_is_surface_density: false`、以及因 RNA FPKM 排除 `GSE160572_MM_surfaceome.csv.gz`。

四个文件的 SHA-256 仍记录，但角色降为 `files_pinned_for_integrity_only`——版本固定手段，不是批准依据。

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

**两个计数必须分开：满足某条路径 ≠ 最终 eligible。** 满足 `RQ-02` 的靶点还可能因独立家族数不足或定位证据冲突而落 hold。初稿把二者混为一谈，已按审核裁决更正。

| 路径 | 条件 | 路径命中 | 其中最终 eligible |
|---|---|---|---|
| `ECD-a` | `uniprot_ecd_meets_min_length = true` | **30** | **18** |
| `ECD-b` | `uniprot_gpi_anchor` 且 `uniprot_signal_peptide` 且 `transmembrane_segment_count = 0` | **4** | **4** |

两条路径在本 snapshot 下无重叠（`measured_path_overlap: 0`）。`RQ-02` 阳性总数的分解恒等式：

> **34 个 RQ-02 阳性 = 22 最终 eligible + 6 独立家族数不足（`E1-02`）+ 6 定位证据冲突（`E1-04` 中 RQ-02 阳性者）**

`VAL-E12` 要求每条路径同时报出两个计数，不得只报其一或用后者冒充前者。

**`ECD-b` 是必需的，理由是修正数据表示假象而不是放宽标准。** UniProt 的 extracellular domain 字段由跨膜蛋白的 TOPO_DOM 推导；GPI 锚定蛋白零跨膜段、没有 TOPO_DOM，该字段一律读成 `false`。若只用 `ECD-a`，`CEACAM5`、`MSLN`、`FOLR1`、`MELTF` 会因此落 hold——而四者在本库中都是 `confirmed_surface`，都带信号肽与 GPI 锚，成熟蛋白整体位于细胞外侧。GPI 锚 + 信号肽 + 零跨膜段在结构上即意味着全长成熟蛋白朝向胞外，其胞外长度等于成熟蛋白长度。

**腔内结构域不算胞外。** `LAMP1` 即属此类：有跨膜段与信号肽，但无胞外 TOPO_DOM，两条路径都不满足，落 hold。这正是审核方要求的「细胞器膜定位必须 DEFER」，规则自然落在正确一侧。

### `RQ-03` 蛋白层面 provenance

分两类，不得混用。RNA 来源行一概不可采纳。

**库中覆盖的靶点**：要求 `source_evidence.tsv` 有对应行，且 `source_id`、`source_release`、`evidence_family`、`source_url`、`license` 均非空。

**覆盖靶点若 `RQ-03` 不成立** → 归入 `E1-04b`，DEFER（见第五、六节）。

**库中未覆盖的靶点（`E1-05`）**：`source_evidence.tsv` 里本就没有它们的行。**初稿要求所有行都有来源 provenance，那会让合法的 `E1-05` hold 行无法通过验证，或迫使执行者伪造 provenance**——已按审核裁决更正。改为要求「缺失 provenance」六列：`reference_dataset_id`、`reference_dataset_version`、`reference_snapshot_id`、`target_axis_ref`、`absence_reason`（只能取 `gene_symbol_not_present_in_reference`）、`lookup_at`。**这六列全部在 `output_schema.per_target_columns` 之内**（初稿只加了后三列，导致 `VAL-E05b` 要求的字段 schema 里没有——已按审核裁决补齐）。前三列必须分别等于 admission snapshot 的 `ADC_surfaceome_reference`／`0.3.0`／`2026-07-29-quant-topology-mm`，不得自由填写（`VAL-E05d`）。

`source_*` 字段允许为空，但**禁止伪造 source evidence**，也**禁止把缺失表述为 source-supported**：`provenance_kind = reference_absent` 的行若出现非空 `source_ids` 即为验证失败（`VAL-E05b`／`VAL-E05c`）。

## 五、规则求值优先级（必须冻结）

五条规则的条件**并非天然互斥**——同一靶点可能同时满足「两条 ECD 路径都不满足」与「独立家族数 < 2」。实测本 snapshot 下有 **2 个**这样的靶点：`TM4SF1` 与 `TDGF1`。初稿没有定义优先级，`VAL-E01` 的「命中且仅命中一条」无从保证，已按审核裁决更正。

冻结顺序，取第一个命中者：

> `E1-05` 不在库中 → `E1-04` 定位证据冲突 → `E1-04b` provenance 不成立 → `E1-03` 无细胞外结构域 → `E1-02` 独立家族数不足 → `E1-01` eligible

理由：先判「不在库中」，因为无数据时其余条件都无法求值；再判冲突，因为冲突使后续判据不可信；**再判 provenance 是否成立，因为 provenance 不成立时该行证据本身不可引用，再谈拓扑与家族数没有意义**；再判细胞外结构域，再判独立家族数；全部通过才 eligible。

`TM4SF1` 与 `TDGF1` 同时命中 `E1-03` 与 `E1-02`，按优先级解析到 **`E1-03`**，并须在结果中记录被压制的条件（`VAL-E11`）。测试用等价 fixture 覆盖了每一种重叠组合，逐例证明恰好命中一条。

## 六、确定性映射：五条规则覆盖 41 个靶点，零排除

| ID | 条件 | outcome | disposition | 数量 |
|---|---|---|---|---|
| `E1-01` | `RQ-01`＋`RQ-02`＋`RQ-03` 全满足且无冲突 | `eligible_surface_target` | RETAIN | **22** |
| `E1-02` | `RQ-02` 满足但独立家族数 < 2 | `possible_surface_target` | DEFER | **6** |
| `E1-03` | 两条 `RQ-02` 路径都不满足（含腔内结构域） | `possible_surface_target` | DEFER | **3** |
| `E1-04` | `discordance_flags` 非空 | `possible_surface_target` | DEFER | **6** |
| `E1-04b` | 在库中但 `RQ-03` provenance 不成立 | `possible_surface_target` | DEFER | **0**（空规则） |
| `E1-05` | 靶点不在参考库中 | `possible_surface_target` | DEFER | **4** |

22 + 6 + 3 + 6 + 0 + 4 = 41。**零自由裁量、零排除。**

**`E1-04b` 是按审核裁决新增的。** 初稿漏了一种组合：覆盖靶点 `RQ-01` 与 `RQ-02` 满足、无冲突，但 `source_evidence.tsv` 字段不全导致 `RQ-03` 不满足——它不命中 `E1-01`（RQ-03 未满足）、不命中 `E1-02`（家族数不低）、不命中 `E1-03`（RQ-02 满足）、不命中 `E1-04`（无冲突）、不命中 `E1-05`（在库中），因此 `VAL-E01` 的「恰好命中一条」无从满足；`VAL-E05` 只写「降为 hold」却没说降到哪条规则、也没有对应 `rule_id`。

实测 **37 个覆盖靶点全部满足 `RQ-03`**，故本规则在本 snapshot 下为空规则，计数不变。但它必须存在——provenance 完整性不由本契约保证，抽取时可能失败。其 disposition 只能是 DEFER：既不得 RETAIN（无可回溯来源），也不得 EXCLUDE（缺 provenance 不是否定证据）。

- `E1-02`：`CLDN18`、`GUCY2C`、`LGR5`、`PRLR`、`RNF43`、`SLC44A4`
- `E1-03`：`LAMP1`、`TDGF1`、`TM4SF1`
- `E1-04`：`CD276`、`F3`、`IL2RA`、`MET`、`MST1R`、`TACSTD2`
- `E1-05`：`AG7`、`CA19-9`、`EDBN`、`Undisclosed`

`not_surface_target` 与 `identity_unresolved` **仍然不可用**：该库明确 `absence_is_negative_evidence: false`，不产出「该靶点不是表面蛋白」这类阳性否定断言；`consensus_class = no_surface_support` 只表示无支持证据，不等于已证伪。**本次抽取不得排除任何靶点。**

## 七、抽取后的预期结果，逐项可核对

| 量 | 值 |
|---|---|
| 靶点总数 | 41 |
| eligible | **22**（经 `ECD-a` 18 + 经 `ECD-b` 4） |
| hold | **19**（6 + 3 + 6 + 4） |
| killed | **0** |

**执行结果必须逐项等于上表，任一项不符即视为偏离本契约。**

## 八、必须写进结果报告的三条发现

- **`MF-01`：`GUCY2C` 落 hold。** 它在本参考库中只有 `curated_knowledge` 一个独立证据家族，未达两家族门槛，`consensus_class` 是 `supported_surface` 而非 `confirmed_surface`。**这与此前多模型共识把 GUCY2C 列为首选、以及被隔离运行的 Tier A 选择相反。** 结果报告必须原样写出，不得因与既有偏好冲突而弱化。
- **`MF-02`：`eligible` 只表示身份与拓扑层面存在有合理依据的细胞外可及蛋白形式**，不表示该靶点在 CRC 肿瘤细胞表面可得。后者是 Level 02 的 T7，本次未评估。
- **`MF-03`：零排除。** 41 个靶点中没有任何一个被判为 `not_surface_target`。hold 不是淘汰，是待证据。

## 九、输出与验证

输出为每靶点一行、**29 列**（见 YAML `output_schema`），必含 `rule_id`、`rq_02_path`、`evaluation_status`、`provenance_kind`、`absence_reason`、`target_axis_ref`、`lookup_at` 与 `row_checksum`。

**16 条**验证规则 `VAL-E01`..`VAL-E13`（含 `VAL-E05b`／`c`／`d`） 见 YAML。要点：41 行且每行按优先级命中且仅命中一条规则（`VAL-E01`／`VAL-E11`）；计数等于第七节且 `RQ-02` 分解恒等式成立（`VAL-E02`／`VAL-E12`）；不得出现 `not_surface_target` 或 `identity_unresolved`；每个 eligible 必记 `rq_02_path`；覆盖行须有完整来源 provenance、未覆盖行须有完整缺失 provenance 且禁止伪造（`VAL-E05`／`E05b`／`E05c`）；输入 SHA-256 不一致即中止；不得读取被禁文件或字段；输出中不得出现任何 Gate 分数、Gate 状态、T7 判定或肿瘤表面定量；三条 `mandatory_findings` 必须原样出现；每个产物文件逐文件记录 SHA-256；**抽取前 `admission_record_ref` 必须指向实际存在的独立 `APPROVE` 记录，为空即不得执行（`VAL-E13`）**。

## 十、本契约授权与不授权

**授权：** 冻结本次抽取的范围、字段白名单、判据映射、求值优先级与输出验证。

**不授权：** 在 `SRCADM-01` 取得独立 `APPROVE` 记录前执行抽取；把 `ADC_surfaceome_reference` 纳入已批准来源（本契约只引用，不批准）；执行 Level 01；评估 T7 或任何肿瘤细胞表面可得性；新增任何靶点或 clinical context；任何筛选排序、Tier 划分、资产推荐或实验建议；任何 Gate 执行或评分；读取被禁文件或字段；把被隔离运行（PR #53、#54）的任何产物引入。

## 十一、后续顺序

1. 本契约获 `APPROVE`。
2. **`SRCADM-01` 独立 source admission PR** 审计 `AUD-01`..`AUD-09` → `APPROVE`，并在 `logs/` 留下记录。
3. 把 `admission_record_ref` 指向该记录，执行抽取 → 结果 PR → `APPROVE`。
4. **另开一个 PR** 更新 `adc_pool_level_01_input_binding.yaml`，把抽取产物绑为 `LOCK-01` 的来源并解除 `EVGAP-01`。该 PR 不在本契约授权范围内。
5. `EVGAP-02`（`LOCK-03` 的源级 CRC linkage 证据）仍未解除，需其独立契约。**两个缺口都解除后，Level 01 才能执行。**

## 十二、当前阻断

- 本契约获 ChatGPT `APPROVE` 前，不得执行抽取。
- **本契约获 `APPROVE` 后仍不得执行抽取**，直到 `SRCADM-01` 取得独立 `APPROVE` 记录。
- 抽取完成也**不**解除 `EVGAP-02`，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。
