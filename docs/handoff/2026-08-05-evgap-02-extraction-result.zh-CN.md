# Handoff：EVGAP-02 CRC linkage 抽取结果审核

- 日期：`2026-08-05`
- 任务分支：`task_20260805_evgap-02-extraction-result`
- 基线：`main` @ `8aa7e87`
- 授权依据：PR #61（`docs/pools/evgap_02_crc_linkage_extraction.yaml`），已 `APPROVE` 并合并；该契约 `authorises_extraction_run_after_approve: true`、`blocked_by: [contract_approval]`，条件已满足
- 外部运行：`gen_iet_evgap_02_crc_linkage_20260805T190453Z`
- 交付物类型：**结果审核（外部运行留痕）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（本 PR 只含本 handoff 与一条 worklog）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次做了什么

按 PR #61 已获批的契约执行一次 Tier 1 抽取，解除 `EVGAP-02`（LOCK-03 的证据缺口）。

**这不解除 `EVGAP-01`，不授权执行 Level 01，不使任何 pair 进入 Level 02。**

## 二、执行前先测可达性

契约把来源不可达定为**须记录的事实**而非可静默跳过，因此执行前逐个测试六个必查 endpoint，全部应答：

| source class | endpoint | API |
|---|---|---|
| `peer_reviewed_literature` | PubMed、PMC | NCBI E-utilities `esearch` |
| `clinical_trial_registry` | ClinicalTrials.gov | API v2 `/studies` |
| `public_molecular_dataset` | TCGA、GEO、Human Protein Atlas | GDC genes API；E-utilities `db=gds`；HPA `search_download` |

## 三、检索完整性

| 项 | 值 |
|---|---|
| 检索次数 | **451** |
| 不可达检索 | **0** |
| target 级检索完整 | **41 / 41** |
| pair 级 D 类检索完整 | **369 / 369** |

target 级按 endpoint 判定覆盖（不是按 source class），A/B/C 用类别特异术语；D 类按 pair 判定，369 个 pair 全部记录六个完整性字段。

## 四、LOCK-03 结果

| 规则 | outcome | disposition | state | 数量 |
|---|---|---|---|---|
| `L3-02` | `linkage_evidence_exists` | RETAIN | active | **168** |
| `L3-03` | `linkage_unassessed` | DEFER | hold | **192** |
| `L3-05` | `no_known_linkage_after_complete_search` | `EXCLUDE_FROM_ACTIVE_POOL` | reactivation-eligible | **9** |

168 + 192 + 9 = 369。**`L3-01` 与 `L3-04` 本次为空规则**——无检索不完整的 pair，也未采集到「仅其他癌种 precedent」的证据。

### active 的分布，以及 192 个 hold 的来由

| context | active |
|---|---|
| `crc_mss_pmMR_mcrc_3l_plus`（canonical） | **40** |
| `crc_cms4_emt_oncofetal_revCSC_high` | 33 |
| `crc_mss_ras_mut_1l_2l_post_chemo_bev` | 19 |
| `crc_msi_h_dmmr_io_resistant` | 17 |
| `crc_mss_ras_mut_3l_plus` | 17 |
| `crc_braf_v600e_post_targeted` | 14 |
| `crc_her2_positive_post_treatment` | 11 |
| `crc_kras_g12c_post_targeted` | 11 |
| `crc_mss_ras_wt_antiegfr_resistant` | 6 |

canonical context 只要有 A/B/C 证据即可 RETAIN，故 40 个靶点全部 active（41 个中只有 `EDBN` 无 A/B/C 证据）。**8 个亚群 context 必须同时有 D 类情境特异证据才能 RETAIN**——这正是那 192 个 `L3-03` 的差别所在：有疾病级 CRC 证据，但该亚群没有情境特异富集证据。

### 证据行

**7,067 行**：A 2,808 / B 2,295 / C 1,746 / D 218。`context_specific = true` 仅 D 类的 218 行——A/B/C 按契约是疾病级检索，按构造不具情境特异性。

## 五、必须原样记录的四条

- **`MF-L01`**：LOCK-03 的 RETAIN 只表示**存在可回溯的 CRC-specific linkage 证据记录**，**不表示该靶点适合 ADC、不表示疗效、不表示治疗窗**。
- **`MF-L02`**：C 类 1,746 行（naked antibody／CAR-T／bispecific／RIT／immunotoxin／imaging antibody）证明 target 在 CRC 中可接近或可干预，**不是 ADC 疗效证据**。全部 C 类行 `is_adc_efficacy_evidence = false`。
- **`MF-L03`**：未使用任何派生本地数据库。**检索完整性只在 Tier 1 声明范围内成立。** ADCdb、CRC 文献库、CRC Atlas ledger、竞争格局库仍待 `SRCADM-02`..`05`；日后任一获准入需另开 PR 扩大范围并重跑。
- **`MF-L04`**：RETAIN **不使 pair 进入 Level 02**。`EVGAP-01` 未解除前 `may_advance_to_level_02` 恒为 `false`，369 行全部如此。

## 六、一条必须写明的证据强度限制

**全部 7,067 行 `review_status = machine_retrieved_requires_human_review`，`evidence_direction = unknown`。**

这些是**按冻结查询式检索到的公开记录**——PMID、PMCID、NCT 号、GEO 登记号都可点击回溯，但**其内容未被阅读、未被人工判读**。按 PR #58 已获接受的 `DECISION-02`，machine-retrieved 证据满足 LOCK-03 的**存在性**，但携带该状态的 pair **不得晋级 Level 02**。

因此 **168 个 active 的含义是「存在待复核的 CRC-specific linkage 记录」，不是「linkage 已确证」。** 这一句必须原样出现在任何引用本结果的地方。

## 七、只有一个靶点完整检索后无任何 linkage

`EDBN`，9 个 pair 全部 `L3-05`。它是非标准符号（fibronectin EDB 结构域），在 2026-08-05 的 Level 01 Preview 中也是 `E1-05`（不在 surfaceome 参考库）。

`L3-05` 是**可逆**的：`is_scientific_disproof = false`、`is_killed = false`、状态 `reactivation-eligible`，仍留在 Eligible Universe Index。**不是科学证伪，不是淘汰。**

## 八、一处执行者自查并修正的问题

首版 evidence 表缺少契约要求的 4 列（`pair_id`、`clinical_context_id`、`context_specific`、`linkage_outcome`）；而且 A/B/C 按契约是**按 target 检索一次**，导致单条证据行无法携带唯一 `pair_id`，`VAL-L16`「引用行的 `pair_id` 必须与 disposition 一致」不可满足。

这是我在设计输出时没把「按 target 检索」与「按 pair 记录证据」这两件事对齐。修正方式是**让输出符合已冻结的 schema，而不是改契约**：把 target 级记录按 pair 展开为 7,067 行 pair 级证据行，**未重复任何网络调用、未改变任何已检索事实**，只改表示形式。

## 九、验证结果

**契约 20 条验证规则 `VAL-L01`..`VAL-L20` 逐条对实际产物核验，全部 `PASS`**，包括：

- `VAL-L01` 369 行、每行命中且仅命中一条规则、`pair_id` 唯一
- `VAL-L02` 每行 outcome／disposition／state 与其 `rule_id` 的契约声明逐项一致
- `VAL-L04` 全部 C 类行 `is_adc_efficacy_evidence = false`
- `VAL-L06` 全部亚群 `L3-02` 行都有非空 `class_d_evidence_refs`
- `VAL-L07` 全部 `L3-05` 行六项完整性字段齐备、`search_complete = true`、语义为 `EXCLUDE_FROM_ACTIVE_POOL`、`reactivation-eligible`
- `VAL-L09` 两张表的列集合与契约**逐表**相等
- `VAL-L11`／`VAL-L19` 41 个 target 全部覆盖六个必查 endpoint
- `VAL-L16` 全部引用 id 存在于 evidence 表且 `pair_id` 一致，7,067 个 id 无重复
- `VAL-L17` 逐规则引用约束全部满足
- `VAL-L18` 369 个 pair 全部有六个 D 类字段且 `class_d_search_complete = true`
- `VAL-L20` `evidence_row_count` 全部等于三组 refs 去重后总数

仓库侧：`Ran 338 tests` 全部通过；`scripts/verify_repository_boundary.sh` 通过；运行期间仓库零写入。

## 十、明确没有做什么

- 未运行任何 Gate、未赋任何分数、未评估 T2 或 T7。
- 未排序、未划 Tier、未推荐资产、未给实验建议。
- 未新增靶点或 clinical context（0／0）。
- **未打开任何 Tier 2 派生本地数据库**；未把任何派生库纳入已批准来源。
- 未引用被隔离运行（PR #53、#54）的任何产物。
- **未解除 `EVGAP-01`；未更新 `adc_pool_level_01_input_binding.yaml`；Level 01 仍不可执行。** 解除 `EVGAP-02` 须待本结果获批后另开 PR。
- 未生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
- 未补八份批准记录（#52／#53／#54／#57／#58／#59／#60／#61），事实已查全但未写文件。

## 十一、下一步

1. 本结果 `APPROVE`。
2. **另开 PR** 更新 Level 01 输入绑定，把本抽取产物绑为 `LOCK-03` 的来源并**解除 `EVGAP-02`**。
3. Track B：`SRCADM-01` → `EVGAP-01` 抽取 → 结果 → binding。
4. **两个缺口都解除后**，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。

## 附录 A：产物 SHA-256

| 文件 | SHA-256 |
|---|---|
| `pair_linkage_evidence.tsv` | `333a5c4132174075691f1952e839cd6737ccdc68c238e2b497e6f666951c8e09` |
| `pair_linkage_disposition.tsv` | `464d75d426921d73cc417c0c33d27ec0cf8408ba031fae75e2d8331b8e31a9cc` |
| `search_log.tsv` | `dd0569c572bfd09f74f034f1844811c918182c767118e963afc9ed0a14c7ce08` |
| `run_report.md` | `ef3914954f9fc9f7a0e78c50a1495dd045e79ebc1cbd4c2768a6ce8f2f05786b` |
| `external_run_worklog.md` | `878dd8f863e61467128321c2e4fd464fba163a1cdeeac48ada323e929f05a88a` |
| `source_manifest.json` | `a143d4b3e00de7d4cedb325f4abe49a00b62c27c22a8f91e68c153bc461194b9` |

运行目录：`external:result/gen_iet_evgap_02_crc_linkage_20260805T190453Z`

### 供上传审核的打包

`external:result/gen_iet_evgap_02_crc_linkage_20260805T190453Z.zip`

- ZIP SHA-256：`9c9c184e7b66e2999950831a18e059847c3b7dfd4a5b6f92ac78ac9dce259ece`
- 148,063 bytes，含且仅含上表六个文件

（按 PR #60 第二轮裁决后我自我约束的规则：外部产物每次交付都必须同时产出带校验和的打包，只改 handoff 不算完成交付。）
