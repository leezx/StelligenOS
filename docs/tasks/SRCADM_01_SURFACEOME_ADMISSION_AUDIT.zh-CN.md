# SRCADM-01：`ADC_surfaceome_reference@0.3.0` 来源准入审计

- 任务分支：`task_20260805_srcadm-01-surfaceome-admission`
- 授权依据：审计范围 `AUD-01`..`AUD-09` 由 **PR #59** 冻结并获 ChatGPT `APPROVE`
- 机器可读记录：[`../pools/srcadm_01_surfaceome_admission.yaml`](../pools/srcadm_01_surfaceome_admission.yaml)，由 `tests/test_srcadm_01_surfaceome_admission.py` 校验
- 当前状态：**审计已完成，结论待审核**
- 可独立复核的审计包：`external:result/gen_iet_srcadm_01_audit_bundle_20260806T000000Z`，
  ZIP SHA-256 `2dbe88af1a2e9aee8004b9cbdd894c48f2f91197726678898aadf5da3f75e931`
- 结论：**`admissible_with_conditions`——有条件可纳入，四项条件见第三节**

## 目的

`EVGAP-01` 的抽取被 `SRCADM-01` 阻断：`ADC_surfaceome_reference@0.3.0` 从未被审核，PR #59 明确「派生数据库不能靠自声明 + 哈希纳入」，并冻结了九项必审内容。

本文件是那九项的审计结论。**本文件不授予准入**——准入由本 PR 获 `APPROVE` 后成立，届时另开 PR 把 `EVGAP-01` 契约的 `admission_record_ref` 指向审核记录。

## 〇、审计包（第一轮审核后补）

第一轮审核指出：**审计结论的核心事实全部来自仓库外文件，而仓库内的测试只验证审计文档
自洽，不能证明外部事实为真。** 这个意见成立——所以本轮补一个只读复核包。

解包后运行：

```
python3 verify_audit.py .
```

脚本只读包内文件，**重算 48 项审计事实**，逐项输出 `MATCH` / `MISMATCH`。
本次结果：**48 / 48 全部 `MATCH`**。

三张 processed 表**未做子集裁剪**（`source_evidence` 11.8 MB、`surfaceome_consensus` 8.9 MB、
`membrane_topology_evidence` 3.5 MB），因此 11,334、6／5 重复键、家族映射等数字都能**精确重算**，
而不是只能核对代表性行。整包压缩后 2.6 MB。

### 唯一不能在包内独立重算的一项

**19 个 raw 文件未随包提供**（合计数 GB）。其校验和在审计时已从归档 snapshot 实算，
结果记在 `raw_checksum_verification.json`（**19／19 `OK`**）。要独立重算这一项需要归档
snapshot 本身——**这正是 `COND-03` 已声明的边界**，不是新增限制。

`download_manifest.json` 本身随包提供，故 **`AUD-02` 的 SHA-256 对应关系可在包内完整重算**。

### 重算过程中发现的一处表述问题

审计原文写「HPA 有行但 `hpa_plasma_membrane = false` 的基因共 **11,334** 个」。
重算脚本首版按「consensus 中 `hpa_plasma_membrane = false`」计数，得 **18,534**。

**11,334 这个数字是对的**：HPA 实际覆盖 **13,597** 个基因，其中 11,334 个 `plasma_membrane = false`。
18,534 里多出的部分是**从未被 HPA 覆盖**的基因——该字段对它们同样是 `false`。

原文的「有行」二字承载了全部区分度，容易读漏。现已在机器可读记录与脚本中同时报出
13,597／18,534／11,334 三个数。**两种口径下 `imaging` 被错误计入的基因都是 0 个**，
故 `AUD-05` 的结论不变。

### 另一处更正

`AUD-01` 原写「`AssetGenOS/scripts/build_t7_surfaceome_reference.py`」有歧义——
该路径**在 StelligenOS 仓库之外**，是同级的 `AssetGenOS` 仓库
（`/Volumes/Stelligen_SSD/Stelligen/AssetGenOS/scripts/`）。已更正，副本随包提供。

## 一、九项逐条结论

| ID | 审计项 | 结论 |
|---|---|---|
| `AUD-01` | builder 实现与版本 | **PASS** |
| `AUD-02` | raw manifest 与 `raw_manifest_sha256` 的对应 | **PASS**（实算复核） |
| `AUD-03` | 原始来源清单与 release 版本 | **PASS_WITH_FINDING** |
| `AUD-04` | license 与再分发条件 | **PASS_WITH_FINDING** |
| `AUD-05` | evidence family 独立性 | **PASS** |
| `AUD-06` | 来源去重逻辑 | **PASS_WITH_FINDING** |
| `AUD-07` | `discordance_flags` 生成规则 | **PASS** |
| `AUD-08` | 代表性靶点逐行回溯 | **PASS** |
| `AUD-09` | snapshot 可复现性 | **PASS_WITH_FINDING** |

无一项 `FAIL`。四项带 finding，全部已界定影响范围。

## 二、三个最关键的结论

### `AUD-05` 独立性成立，而且恰好避开了审核方点名的失效模式

审核方要审的是「family independence 是否真正独立，而非同源数据的重复计数」。实测三个家族的来源映射：

```
curated_knowledge        <- {goa_human, uniprot_reviewed_human}
imaging                  <- {hpa_subcellular_location}
cell_surface_capture_ms  <- {cspa}
```

**`goa_human` 与 `uniprot_reviewed_human` 是同源的**——GOA human 由 UniProt 策展流程产出。builder 把二者收进**同一个** `curated_knowledge` 家族，因此不会被计成两个独立家族。**这正是那个失效模式，builder 避开了它。** 实例：`GUCY2C` 两个来源都 `supported`，`family_count` 仍为 **1**。

两条进一步的验证：

1. **family 计数要求支持性证据，不是「有行即计」。** 判据在 builder 第 2112–2118 行，取自 consensus 的 support 布尔值。反例检验：HPA 有行但 `hpa_plasma_membrane = false` 的基因共 **11,334** 个，其中 `imaging` 被计入家族的为 **0 个**。
2. **`family_count >= 2` 必然包含至少一个实验型家族。** 因为 `curated_knowledge` 是唯一可由两个来源喂养但只计一次的家族，要凑到 2 就必须再有 `imaging` 或 `cell_surface_capture_ms`。所以 `RQ-01` 的两家族门槛不是形式门槛。

### `AUD-04` license 歧义存在，但不触及 EVGAP-01 读取的任何字段

19 个来源全部声明 license，无缺失。但六个有歧义：`cellphonedb_gene`／`protein`／`complex`／`interaction`（「not declared in cellphonedb…」）、`cellchatdb_human`（GPL-3.0 repository license）、`omnipath_intercell_receptor`（per-resource licenses retained）。

**决定性检查：这六个来源没有任何一个出现在 `source_evidence.tsv` 中。** 它们只喂 `cci_receptor_*` 字段，而该字段已被 PR #59 的 `barred_fields` 禁用。

进入 `source_evidence.tsv` 的只有四个来源，其中 `goa_human`／`hpa_subcellular_location`／`uniprot_reviewed_human` 为 **CC BY 4.0**。

**这个结论是承重的**：它依赖 PR #59 的字段白名单。若白名单日后扩大到 `cci_receptor_*`，本准入必须重新审——已写入 `COND-02`。

顺带一处命名不一致：processed 表用 `source_id = cspa`，而 manifest 用 `cspa_validated_surfaceome` 与 `cspa_cell_type_matrix`，两者无法直接 join。

### `AUD-09` 完整性可验，但可复现性有边界

`shasum -a 256 -c checksums.sha256` 对 raw snapshot 的 **19 个文件全部 OK**。builder 中唯一的时间依赖是第 268 行 `datetime.now()` 用于 `processed_at_utc` 时间戳字段，不参与任何计算；无 `random`、无 `shuffle`。**给定同一 raw snapshot，构建结果确定。**

**但 raw snapshot 本身对 `uniprot_reviewed_human` 与 `goa_human` 未钉版本**——它们的 release 是 `current_at_download`，只钉下载时刻不钉上游版本。因此从上游重新下载并重建**不能**保证逐字节复现该 snapshot。

可复现性成立的前提是**使用已归档的 raw snapshot**，而不是从来源重新获取——已写入 `COND-03`。

## 三、四项准入条件

任一条被破坏即须重新审。

| ID | 条件 |
|---|---|
| `COND-01` | **准入仅限这一个 snapshot**：`0.3.0` / `2026-07-29-quant-topology-mm`，由 19 个 raw 校验和与 4 个 processed 校验和共同钉住。不覆盖其他版本，不覆盖任何后续重建。 |
| `COND-02` | **准入仅限 PR #59 的字段白名单**。license 歧义来源只喂已禁用的 `cci_receptor_*`，这是 `AUD-04` 结论成立的前提。白名单一扩大，准入即失效。 |
| `COND-03` | **准入基于已归档 snapshot，不基于可从上游复现**。两个来源为 `current_at_download`，归档副本即事实来源。 |
| `COND-04` | **重复键不得进入 EVGAP-01 的判据**。已实测 11 个受影响基因全在 41 个靶点之外；若靶点轴日后扩大，须重新检查。 |

## 四、其余带 finding 的两项

**`AUD-03`**：manifest 的 `files` 条目里 `release` 字段**全部为 null**；release 字符串由 builder 另行赋值，且在 processed 表中确有实义取值（`HPA 25.1; Ensembl 109`、`PLOS ONE 2015 supplementary file S2` 等）。但 EVGAP-01 实际使用的四个来源里，`uniprot_reviewed_human` 与 `goa_human` 的 release 是 `current_at_download`，**不是版本号**。后果见 `AUD-09`。

**`AUD-06`**：builder 中**检索不到显式去重例程**。实测 `source_evidence.tsv` 在 `(gene_symbol, source_id, evidence_kind)` 上有 **6** 个重复键，`membrane_topology_evidence.tsv` 在 `(gene_symbol, source_id)` 上有 **5** 个；`surfaceome_consensus.tsv` 在 `gene_symbol` 上无重复。

影响已界定：受影响基因为 `HERC3`、`MATR3`、`NPIPA9`、`PINX1`、`POLR2J3`、`PRODH`、`ERVK-7`、`NRXN1`、`NRXN2`、`NRXN3`、`SIRPB1`，**没有一个属于 EVGAP-01 的 41 个靶点**。且 family 计数取自 consensus 的 support 布尔值而非行数，故重复行在结构上不可能抬高 `RQ-01` 的家族数；41 个靶点的 `family_count` 与 `families` 列表实测 100% 一致。

## 五、`AUD-07` 与 `AUD-08`

**`AUD-07`**：builder 第 2121–2129 行，四条确定性规则——`hpa_plasma_membrane_uncertain`、`cspa_support_without_uniprot_explicit_surface`、`hpa_only_vs_curated_knowledge`、`generic_membrane_without_surface_localization`。PR #59 的 `E1-04` 把 `discordance_flags` 非空一律判 DEFER，故这四条规则只把冲突显式化并触发 DEFER，**不会产生 RETAIN**。

**`AUD-08`**：三个代表性靶点逐行回溯成功，每条主张都落到 `source_id` + `surface_supported` + `source_release` + `source_url`：

- `CDH17`：`confirmed_surface`，families `cell_surface_capture_ms` + `curated_knowledge`（n=2），ECD-a 路径
- `CEACAM5`：`confirmed_surface`，families `curated_knowledge` + `imaging`（n=2），ECD-b GPI 路径
- `GUCY2C`：`supported_surface`，families 仅 `curated_knowledge`（n=1），在 PR #59 规则下落 `E1-02` hold

## 六、`AUD-01` 的一处残留说明

builder 存在、2,721 行、可读，family 计数与 discordance 生成均为显式条件分支，无隐藏启发式。

但 `builder_version` 由 config 传入而非脚本内常量，因此「0.3.0」这个版本号依赖 `build_manifest` 的自述，**不能由脚本自身独立确证**。这不构成阻断——snapshot 由 23 个校验和钉住，版本号只是标签——但如实记录。

## 七、本审计不做什么

不授予准入；不修改 `evgap_01_surface_localization_extraction.yaml` 的 `admission_record_ref`；不执行 `EVGAP-01` 抽取；不执行 Level 01；不解除 `EVGAP-01` 或 `EVGAP-02`；不纳入该数据集的其他版本或后续重建；不扩大 PR #59 的字段白名单；不纳入 `SRCADM-02`..`SRCADM-05` 的任何派生库。

## 八、后续顺序

1. 本审计连同审计包 `APPROVE`，在 `logs/` 留下审核记录。
2. **另开 PR** 把 `EVGAP-01` 契约的 `admission_record_ref` 指向该记录，`authorises_extraction_run` 转为 `true`。
3. 执行 `EVGAP-01` 抽取 → 结果 PR → binding，解除 `EVGAP-01`。
4. `EVGAP-02` 的抽取已执行，结果审核在 PR #62；获批后另开 PR 解除 `EVGAP-02`。
5. **两个缺口都解除后**，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
