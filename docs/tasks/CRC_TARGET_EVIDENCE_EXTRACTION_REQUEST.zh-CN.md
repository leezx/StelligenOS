# CRC target-level evidence extraction 执行契约

## 任务信息

- 任务编号：`task_20260802_crc-target-evidence-extraction`
- 前置结果审核：PR #29 已获 ChatGPT `APPROVE`
- 前置批准基线：`2ba4457`
- 当前分支：`task_20260802_crc-target-evidence-extraction`
- 当前阶段：contract-only，等待 ChatGPT 审核
- 输入结果：`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_enumeration_20260802/`

## 目标

对已枚举的 CRC target 候选逐个提取可追溯公共证据，形成 target-level evidence catalog，为后续 Gate 评分提供结构化输入。此任务不负责 Gate 评分、排序、资产推荐或新的 indication/endpoint 扩展。

## 证据维度

每个 target 至少建立以下字段，并保留原始来源、定位信息、证据方向和证据强度：

1. `surface_reachability`：是否为可从细胞外接近的表面抗原；亚细胞定位和 assay 类型。
2. `crc_prevalence`：CRC 总体、indication 亚型和恶性细胞/状态中的表达或阳性率。
3. `state_specificity`：MSS/pMMR、RAS、CMS、EMT、CSC 或治疗耐药状态的适配性。
4. `internalization_trafficking`：抗体结合后的内吞、内体/溶酶体递送和 payload 释放支持。
5. `adc_precedent`：ADC、抗体药物、临床项目或可靠的构建/结合先例。
6. `normal_tissue_risk`：正常组织表达、on-target/off-tumor、可预期安全窗。
7. `heterogeneity_shedding`：肿瘤内异质性、克隆覆盖、抗原脱落和 sink 风险。
8. `opposing_evidence`：明确反对证据、阴性结果、失败项目、机制矛盾或关键缺口。
9. `unknowns`：尚未解决且不能用“无证据”替代的未知状态。

## 允许来源

- 已审核外部枚举结果中的 target catalog 和 pair 表。
- 公共论文、PubMed/PMC、临床注册和监管文件。
- ADC Drug Index/ADCdb 及项目原始公开资料。
- TCGA、GEO、单细胞/空间转录组、蛋白组、HPA、DepMap/CCLE 等公共数据。

每条证据必须记录 `source_id`、URL 或本地公开来源路径、标题/项目、年份、证据定位、抓取时间和复核状态。不能只记录搜索摘要或模型推断。

## 输出

所有输出只能写入：

`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_evidence_<run_id>/`

计划文件：

- `target_evidence_units.tsv`
- `target_evidence_summary.tsv`
- `target_opposing_evidence.tsv`
- `target_unknowns.tsv`
- `source_manifest.json`
- `run_report.md`
- `external_run_worklog.md`

仓库内不得写入数据、cache、数据库、下载文件、模型权重或结果表。

## 不执行范围

- 不执行 Gate 分数或 pass/fail 判定。
- 不生成 target ranking、推荐资产或开发决策。
- 不新增 indication、endpoint 或 pair。
- 不把“没有检索到证据”写成阴性证据。
- 不把单篇综述中的候选描述升级为已验证 ADC 靶点。

## 审核门

- 本契约必须通过独立 PR 提交 ChatGPT 审核。
- ChatGPT `APPROVE` 前，不抓取公共数据、不下载文献、不进行证据提取或处理。
- 若 `REQUEST_CHANGES`，只在同一 PR 修正并重新审核。
- 外部运行完成后，必须再建独立结果审核 PR。
- 每个命令、失败、修正、验证和审核结论必须写入 `logs/worklog.md`，并同步 handoff。
