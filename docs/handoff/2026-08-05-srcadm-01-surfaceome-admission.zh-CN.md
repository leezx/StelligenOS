# Handoff：SRCADM-01 surfaceome 来源准入审计

- 日期：`2026-08-05`
- 任务分支：`task_20260805_srcadm-01-surfaceome-admission`
- 基线：`main` @ `8aa7e87`
- 授权依据：审计范围 `AUD-01`..`AUD-09` 由 **PR #59** 冻结并获 `APPROVE`，即本审计的授权
- 交付物类型：**审计记录（contract-only，无外部运行产物）**
- 结论：**`admissible_with_conditions`**——有条件可纳入，四项条件
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次范围

人类负责人指示起 `SRCADM-01`。这是 Track B 的第一环，也是唯一挡住 `EVGAP-01` 的一环。

PR #59 明确「派生数据库不能靠自声明 + 哈希纳入」，并冻结九项必审内容。本次是那九项的实际审计——**读了 builder 源码、raw manifest、license 声明与 processed 表，而不是描述它们**。

**本 PR 不授予准入。** 准入由获 `APPROVE` 后成立，届时另开 PR 把 `EVGAP-01` 的 `admission_record_ref` 指向审核记录。

## 二、仓库内交付了什么

| 文件 | 作用 |
|---|---|
| `docs/tasks/SRCADM_01_SURFACEOME_ADMISSION_AUDIT.zh-CN.md` | 审计文档（面向操作者，中文） |
| `docs/pools/srcadm_01_surfaceome_admission.yaml` | 机器可读审计结论：九项 verdict 与依据、四项准入条件 |
| `tests/test_srcadm_01_surfaceome_admission.py` | 13 项校验 |

## 三、九项结论

`AUD-01` PASS｜`AUD-02` PASS（实算复核）｜`AUD-03` PASS_WITH_FINDING｜`AUD-04` PASS_WITH_FINDING｜`AUD-05` PASS｜`AUD-06` PASS_WITH_FINDING｜`AUD-07` PASS｜`AUD-08` PASS｜`AUD-09` PASS_WITH_FINDING

**无一项 FAIL**，四项带 finding 且全部界定了影响范围。

## 四、三个最关键的结论

**`AUD-05` 独立性成立，而且恰好避开了审核方点名的失效模式。** 三家族映射为 `curated_knowledge <- {goa_human, uniprot_reviewed_human}`、`imaging <- {hpa_subcellular_location}`、`cell_surface_capture_ms <- {cspa}`。**`goa_human` 与 `uniprot_reviewed_human` 同源**（GOA human 由 UniProt 策展流程产出），而 builder 把二者收进同一个家族，因此不会重复计数——`GUCY2C` 两来源皆 supported，`family_count` 仍为 1。两条加强验证：family 计数要求**支持性**证据（反例检验 11,334 个 HPA 有行但 `hpa_plasma_membrane=false` 的基因中，`imaging` 被计入的为 **0**）；`family_count >= 2` 必然包含至少一个实验型家族。

**`AUD-04` license 歧义存在但不触及 EVGAP-01 读取的字段。** 六个来源 license 有歧义（cellphonedb ×4、cellchatdb GPL-3.0、omnipath per-resource），**但没有任何一个出现在 `source_evidence.tsv` 中**——它们只喂已被 PR #59 禁用的 `cci_receptor_*`。进入的四个来源里三个是 CC BY 4.0。**该结论承重**：依赖 #59 的字段白名单，白名单一扩大准入即失效（`COND-02`）。

**`AUD-09` 完整性可验、可复现性有边界。** 19 个 raw 文件 `shasum -c` 全部 OK；builder 唯一时间依赖是时间戳字段、无 random。**但 `uniprot_reviewed_human` 与 `goa_human` 的 release 是 `current_at_download`，不是版本号**，从上游重新下载不保证逐字节复现。可复现性成立的前提是使用已归档 snapshot（`COND-03`）。

## 五、四项准入条件

`COND-01` 仅限这一个 snapshot（23 个校验和钉住）｜`COND-02` 仅限 #59 字段白名单｜`COND-03` 基于已归档 snapshot 而非可从上游复现｜`COND-04` 重复键不得进入 EVGAP-01 判据（靶点轴扩大须重查）

## 六、其余两项 finding

**`AUD-03`**：manifest 的 `release` 字段全部为 null，release 字符串由 builder 另行赋值；四个在用来源中两个是 `current_at_download`。

**`AUD-06`**：builder 中检索不到显式去重例程；实测 6 + 5 个重复键。受影响的 11 个基因**没有一个属于 41 个靶点**，且 family 计数取自 support 布尔值而非行数，故重复行结构上不可能抬高 `RQ-01`；41 个靶点的 `family_count` 与 `families` 列表实测 100% 一致。

## 七、一处如实记录的残留

`builder_version` 由 config 传入而非脚本内常量，故「0.3.0」这个版本号依赖 `build_manifest` 自述、**不能由脚本自身独立确证**。不构成阻断（snapshot 由校验和钉住，版本号只是标签），但记录在案。

## 八、明确没有做什么

- **没有授予准入**；没有修改 `evgap_01_surface_localization_extraction.yaml` 的 `admission_record_ref`（仍为 `null`，`authorises_extraction_run` 仍为 `false`）。
- 没有执行 `EVGAP-01` 抽取；没有执行 Level 01；没有解除 `EVGAP-01` 或 `EVGAP-02`。
- 没有纳入该数据集的其他版本或后续重建；没有扩大 PR #59 的字段白名单。
- 没有纳入 `SRCADM-02`..`SRCADM-05` 的任何派生库。
- 没有产生任何外部运行产物——本次是对既有文件的审计，未生成数据。
- 未补八份批准记录（现为九份，含 #62），事实已查全但未写文件。

## 九、验证结果

- `Ran 351 tests` 全部通过（`main` 基线 338 + 本次新增 13）。
- `scripts/verify_repository_boundary.sh` 通过；`git diff --check` 通过；零 `__pycache__`。
- 测试逐条把审计结论钉在 PR #59 冻结的范围上：九项 ID 集合必须与 `required_audit_items` 完全相等；无 `FAIL`；每项必须有可复核依据（`PASS_WITH_FINDING` 必须写出 finding）；`AUD-02` 的摘要必须是 64 位十六进制且与 #59 引用的前缀一致；`AUD-05` 必须点名同源来源对并引用实测反例数；`AUD-04` 依赖的 `cci_receptor_role` 必须确实在 #59 的 `barred_fields` 中；`AUD-06` 的影响界定必须针对 41 靶点轴；本审计不得授予准入。
- 一处测试自身的错误已修：初稿从 `source_admission_dependency` 读 `raw_manifest_sha256` 键，而该键在 #59 修订后并不存在（摘要写在 `AUD-02` 的条目文本里）。改为跨文件比对前缀并校验 64 位十六进制。
- **变异检验 11 个，全部被捕获后精确回滚**：自行授予准入、自填 `admission_record_ref`、删掉一项审计、`AUD-05` 去掉同源来源说明、`AUD-05` 声明「有行即计」、结论改为无条件可纳入、删掉白名单条件 `COND-02`、抹去 `AUD-09` 的可复现性限制、把 `AUD-06` 影响界定改成含糊表述、删掉受影响基因清单、把某项判为 `FAIL` 却不改总结论。
- **其中两个变异首轮逃逸，是我断言太松导致的**：`assertIn("current_at_download", finding)` 与 `assertIn("41", bound)` 在部分删除后仍能命中残留文本。已改为要求 `AUD-09` 的 finding 同时点名两个未钉版本的来源并写出「逐字节」不可复现，要求 `AUD-06` 的 bounded_impact 明确写出「没有一个属于」并列出受影响基因。重测三个变异全部被捕获。

## 十、后续顺序

1. 本审计 `APPROVE`，在 `logs/` 留审核记录。
2. **另开 PR** 把 `admission_record_ref` 指向该记录，`authorises_extraction_run` 转 `true`。
3. 执行 `EVGAP-01` 抽取 → 结果 PR → binding，解除 `EVGAP-01`。
4. `EVGAP-02` 抽取已执行，结果审核在 PR #62；获批后另开 PR 解除 `EVGAP-02`。
5. **两个缺口都解除后**才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
