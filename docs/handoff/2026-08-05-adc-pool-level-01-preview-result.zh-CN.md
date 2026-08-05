# Handoff：ADC Pool Level 01 Preview 结果审核

- 日期：`2026-08-05`
- 任务分支：`task_20260805_adc-pool-level-01-preview-result`
- 基线：`main` @ `e30a430`
- 前置：PR #57、#58、#59，均已 `APPROVE` 并合并
- 交付物类型：**结果审核（外部运行留痕）**
- 外部运行：`gen_iet_adc_pool_level_01_preview_20260805T160125Z`
- **产物状态：`PROVISIONAL_NOT_AUTHORIZED_FOR_ADVANCEMENT`**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（本 PR 只含本 handoff 与一条 worklog）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、这次做了什么，以及它不是什么

人类负责人给出明确指令：基于已合并的 #57／#58／#59 契约生成 **ADC Pool Level 01 Preview**，十项约束、六个指定输出，**不得声明为正式执行结果**，完成后只提结果审核 PR，不更新 Level 01 binding、不解除 `EVGAP-01` 或 `EVGAP-02`。

指令来自 `Zhixins-KB/2.Biotech/Asset-Generation-OS-architecture.md` 的 `# ADC pool Level 01` 一节（第 20915–21257 行，文件已增长至 21,257 行，只读取未修改）。该节引入 Preview／Accepted 两层拆分，并指出我此前把治理链造得过于串行——「一直在造审核链，而不是造 candidate pool」。这个批评成立，本次按其方案执行。

**这不是正式的 Level 01 执行结果。** 不得作为 Gate 输入、不得进入 Level 02、不得作为资产决策依据。`ADC_POOL_LEVEL_01_ACCEPTED` 只有在 `SRCADM-01`、`EVGAP-01` 抽取结果与 binding、`EVGAP-02` 抽取结果与 binding **五项全部批准**后才能生成。

## 二、必须先讲清的治理事实

本 Preview 读取了 `ADC_surfaceome_reference@0.3.0`，而**该数据库尚未通过审核**——`SRCADM-01` 未完成，PR #59 的 `admission_record_ref` 为空。

这正是：

- 22 个靶点只能标 `provisional_surface_eligible`、**不能**标 `eligible_surface_target` 的根本原因；
- 本 Preview 整体为 provisional 的原因。

`source_manifest.json` 中该来源的 `admission_status` 明确记为 `NOT_ADMITTED_PENDING_SRCADM_01`，并附说明。已批准来源只有 `gen_iet_crc_target_enumeration_20260802`（PR #29 `APPROVE`）。

被隔离的两次运行（PR #53、#54）列为 `barred_inputs` 且 `used: false`——没有贡献任何场景、靶点、disposition 或结论。

## 三、结果

| 量 | 值 |
|---|---|
| raw clinical contexts | **9** |
| raw targets | **41** |
| Raw Enumeration Matrix | **369** pairs（9 × 41，全部保留） |
| context 资格 | eligible **1** / hold **8** |
| target 资格 | `provisional_surface_eligible` **22** / `hold_surface_evidence` **19** |
| provisional eligible universe index | **22** pairs |
| `HOLD_PENDING_CRC_LINKAGE` | **22** |
| `RAW_MATRIX_ONLY` | **347** |
| LOCK-03 | `unresolved`，**369 / 369** |
| active-for-Level-02 | **0** |
| 被排除的候选 | **0** |

### `active = 0` 不等于 pool 为空

它真正表示：**目前没有任何 pair 同时满足三把锁，但已有 22 个 pair 通过了 provisional context × target identity，正在等待 CRC linkage。**

`HOLD` 是待证据，不是否定。369 个 pair 一个都没有被删除或排除。

## 四、判据如何应用

**LOCK-02**：按 #58 冻结的 context projection——按 `indication_id` 分组、校验 6 个 context 级字段组内一致且 4 个 endpoint role 齐备、endpoint 折叠为 `endpoint_candidates` 且 `endpoint_maturity = not_locked_at_level_01`。状态上限照旧：1 个 `canonical_c0` → `validated_unmet_context` eligible；7 个 `not_calibrated` derived strategy → `plausible_unmet_context` 强制 DEFER；1 个 `benchmark_only` → `weak_context` 强制 DEFER。

**LOCK-01**：按 #59 冻结的优先级 `E1-05` → `E1-04` → `E1-04b` → `E1-03` → `E1-02` → `E1-01`，每个靶点恰好命中一条。实测规则分布 `E1-01` 22、`E1-02` 6、`E1-03` 3、`E1-04` 6、`E1-04b` **0**、`E1-05` 4——与 #59 契约的 `predicted_result_shape` 逐项一致。

**LOCK-03**：全部 369 个 pair 保持 `unresolved`。`EVGAP-02` 未完成，该锁**无法求值**；没有被猜测、没有取默认值、没有被跳过。

## 五、三条必须原样记录的发现

- **`MF-01`：GUCY2C 落 hold。** 在参考库中只有 `curated_knowledge` 一个独立证据家族，`consensus_class` 为 `supported_surface` 而非 `confirmed_surface`。**这与此前多模型共识把 GUCY2C 列为首选、以及被隔离运行（PR #53）的 Tier A 选择相反。** 按实测原样写出，未因与既有偏好冲突而弱化。
- **`MF-02`：`provisional_surface_eligible` 只表示身份与拓扑层面存在有合理依据的细胞外可及蛋白形式**，不表示在 CRC 肿瘤细胞表面可得。每个 target 行带 `t7_tumor_surface_validated = not_assessed_level_02_scope`。
- **`MF-03`：零排除。** 没有任何靶点被判 `not_surface_target`。

## 六、22 个靶点中两处留给下游的问题

来源文档点名的两处，本次**不在 Level 01 清除**：

- **FAP** 很可能主要位于 stromal compartment。LOCK-01 只证明存在细胞外可及形式，不证明它是 tumor-cell target。**该问题属 T7。**
- **CD274、EGFR、EPCAM** 存在正常组织或 immune-cell expression，将在 **T11** therapeutic-index pre-screen 中分层。

两条是同一纪律：Level 01 不代替 Level 02 做判断。

Provisional Surface-Eligible Target Set（22）：ADAM9、ADGRG1、ALCAM、CD274、CDH17、CEACAM5、CLDN2、DDR1、EGFR、EPCAM、ERBB2、ERBB3、FAP、FOLR1、MELTF、MSLN、MUC1、NECTIN4、PTK7、ROR1、SLC3A2、TPBG。

hold（19）及原因：独立定位家族数 < 2（CLDN18、**GUCY2C**、LGR5、PRLR、RNF43、SLC44A4）；无细胞外结构域证据（LAMP1、TDGF1、TM4SF1）；定位证据冲突（CD276、F3、IL2RA、MET、MST1R、TACSTD2）；不在参考库中（AG7、CA19-9、EDBN、Undisclosed）。

## 七、五种必须避免的混淆，以及机械防护

来源文档列出的五条：把 provisional 写成 accepted；把预测数字写成实际运行结果；把 hold 写成 negative；把 Level 01 target identity 写成 T7 tumor surface validation；让 provisional candidate 自动进入 Level 02。

本次的防护：每个 TSV 的**每一行**都带 `provisional_only = true` 与 `may_advance_to_level_02 = false`；target 行带 `t7_tumor_surface_validated = not_assessed_level_02_scope`；`pool_state` 只有 `HOLD_PENDING_CRC_LINKAGE` 与 `RAW_MATRIX_ONLY` 两种取值，不存在任何 `active` 态；manifest 顶层四个状态标记齐备且 `is_formal_level_01_execution_result: false`、`may_be_used_as_gate_input: false`、`may_be_used_for_asset_decisions: false`。

## 八、明确没有做什么

- **没有运行任何 Gate、没有赋任何分数、没有排序、没有推荐资产、没有给出实验建议。**
- 没有评估 T7 或任何肿瘤细胞表面可得性。
- 没有新增靶点或 clinical context（0 / 0）。
- 没有排除任何候选（0）。
- 没有读取 #59 禁读的四个 Level 02 文件（`tumor_surface_measurement.tsv`、`tumor_protein_context.tsv`、`treatment_surface_response.tsv`、`receptor_evidence.tsv`）或禁读字段。
- 没有引用被隔离运行的任何产物。
- **没有更新 Level 01 binding，没有解除 `EVGAP-01` 或 `EVGAP-02`。** 两者在 `main` 上仍分别为 `pending_source_admission_and_extraction` 与 `not_completed`。
- 没有把任何文件写入仓库——产物全部在外部 `DATA` 运行目录。
- 没有把 `ADC_surfaceome_reference` 纳入已批准来源。
- 未补 #52／#53／#54／#57／#58／#59 的批准记录（现为六份），事实已查全但未写文件。

## 九、验证结果

十项指令约束逐条核验，全部 `PASS`：369 行 Raw Matrix；context projection 与冻结规则一致；22 个 `provisional_surface_eligible` 且全库不出现 accepted `eligible_surface_target`；19 个 hold；LOCK-03 唯一取值 `unresolved`；无任何 active 态且 `may_advance_to_level_02` 全为 false；产物全在外部 `DATA`；四个状态标记齐备；六个指定输出齐备；无 Gate／评分／排序／推荐／建议且零排除零新增。

- 仓库侧：`Ran 309 tests` 全部通过；`scripts/verify_repository_boundary.sh` 通过；`git status --short` 在运行期间保持干净。
- 七个产物文件的 SHA-256 见附录 A，并已写入 `source_manifest.json`。

## 十、下一步

按来源文档的优先级：**Track A 先做 `EVGAP-02` 契约，Track B 并行做 `SRCADM-01`。** 理由是 Level 01 的价值主要来自「target 为什么与 CRC clinical context 有关」；22 个靶点即使全部通过 surface identity，没有 CRC linkage 仍只是泛癌 surface targets，不是 CRC indication–target seeds。

`EVGAP-02` 的抽取范围来源文档已给定：四类 pair-level linkage（A CRC human tumor expression、B CRC-specific ADC precedent、C CRC-specific target-directed modality evidence 含 CAR-T／bispecific／RIT／immunotoxin／imaging antibody、D context-specific enrichment）与 13 列最小结果 schema。其中 C 类是现有契约尚未涵盖的新增依据，需要在 `EVGAP-02` 契约中加入。

## 附录 A：产物 SHA-256

| 文件 | SHA-256 |
|---|---|
| `raw_clinical_contexts.tsv` | `d21ff96322298f8ec63cb99815157a0bcb0c1e4602af50731fa02a3852892d19` |
| `raw_targets.tsv` | `b227fac291ee1d50cd55412656cef5728a40dda87431f6aaacb726f4d13404a4` |
| `raw_enumeration_matrix.tsv` | `bbf56c033b086b69259f0d4c404f45398ec7bca9b85d0aa6a19e83636ef0c7b9` |
| `pool_level_01_preview.tsv` | `0def1f20f39fbd02190e8a8db73fb5b293364114a45151379801b86c668ab8e8` |
| `pool_level_01_preview_report.md` | `cc47720e9e53d80c2afbe0d40968c4ebde1b4aa30ed63ba762d2b383b76c2e3c` |
| `external_run_worklog.md` | `fb4b62613242473a9127fb1746782246c4c1892bbceb2bcb13a8d0f512696bea` |
| `source_manifest.json` | `a2430324ea1d272eeef8461036bab8db365df5e72d2ae5fbd3922ed94d78ad0a` |

运行目录：`external:result/gen_iet_adc_pool_level_01_preview_20260805T160125Z`
