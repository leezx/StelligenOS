# CRC indication/endpoint/target 全靶点枚举任务请求

## 任务状态

- Task ID: `task_20260802_crc-target-enumeration`
- 当前状态：`PENDING_CHATGPT_APPROVAL`
- PR：https://github.com/leezx/StelligenOS/pull/28
- Review tip observed: `2f1c17b`
- 目标基线：`task_20260801_gen-iet-phase8-external-pilot`
- 本文件是执行契约，不是运行结果，不包含数据。

## 目标

针对结直肠癌（CRC）已确认和已标记来源的 clinical unmet need indication，固定其临床 endpoint 层级，并系统枚举可能的 ADC target，最终形成可审计的：

```text
indication + endpoint + target
```

每个 pair 必须能够回溯到来源、证据类型、靶点身份、ADC 可开发性证据和反对证据；不能把假设、文献线索或单一表达数据包装成已验证结论。

## 当前范围

### Indication

以外部 CRC 试运行已生成的 9 个 indication 作为初始范围，但保留来源状态：

- 1 个 canonical C0：MSS/pMMR mCRC after standard therapy, 3L+
- 其余 derived strategy 或 benchmark subgroup：RAS-mutant 3L+、anti-EGFR resistant、CMS4/EMT/oncofetal/revCSC-high、1L/2L window、HER2-positive、KRAS G12C、BRAF V600E、MSI-H/dMMR IO-resistant

不得将 derived strategy 自动升级为 canonical clinical fact。

### Endpoint

- Ultimate regulatory outcome：OS
- Pivotal supporting efficacy：PFS
- Early ADC proof：ORR + DOR + safety
- Supportive/exploratory：DCR、ctDNA response/clearance、症状/QoL
- mCRC first indication 不使用 RFS 作为默认 endpoint

### Target

候选 target 必须满足以下最小筛选层：

1. 人类可识别的表面/膜相关靶点或 ADC 文献中明确可达的靶点；
2. 有 CRC、恶性状态、肿瘤细胞群或相邻适应症的公共表达/蛋白/组织证据；
3. 有内吞、溶酶体递送、ADC 活性、抗体结合或临床 ADC precedent 中至少一类证据，证据不足必须标记 `unknown`；
4. 记录正常组织表达、on-target/off-tumor 风险、异质性、抗原脱落、内吞/递送限制和明确反对证据；
5. 对已存在临床 ADC precedent 的 pair 与新假设 pair 分开标记。

## 允许来源

- 本地 ADC Drug Index/ADCdb：临床阶段、CRC indication、target、公开活动和 trial identifier；
- 公共文献：PubMed/PMC、原始研究、临床研究、综述仅用于分层背景；
- 公共数据分析：TCGA、GEO、单细胞/空间转录组、蛋白组、Human Protein Atlas、DepMap/CCLE 等，必须保留数据集版本、查询条件和分析脚本/manifest；
- 临床试验注册库和公开监管材料，用于 endpoint、阶段、状态和临床 precedent 核验。

## 禁止事项

- 获批前不得抓取文献、下载数据、运行分析或生成 pair 结果；
- 不得把外部数据、cache、result、数据库、模型权重或大文件写入 StelligenOS；
- 不得将文献线索自动当作 target 通过；
- 不得把公共 ADC precedent 等同于疗效确认；
- 不得修改 Gate、Model、Rule、Registry 或架构冻结内容；
- 不得进入下一任务或扩展到非 CRC indication，除非重新建立 PR 审核范围。

## 外部输出规划

所有运行输入、缓存、原始来源、处理结果和报告写入：

`/Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/gen_iet_crc_target_enumeration_<run_id>/`

计划输出包括：

- `indication_endpoint_universe.tsv`
- `target_evidence_catalog.tsv`
- `indication_endpoint_target_pairs.tsv`
- `opposing_evidence.tsv`
- `source_manifest.json`
- `run_report.md`

## 通过标准

- indication、endpoint、target 三个维度均有稳定 ID 和来源引用；
- canonical、derived、benchmark、hypothesis 状态不混淆；
- 每个 target 至少记录证据类型、证据数量、来源、限制和反对证据状态；
- endpoint 记录临床开发阶段和 endpoint role，不把策略 endpoint 冒充实际 trial primary endpoint；
- 所有外部文件具有运行 ID、数据版本、代码 commit、查询/分析配置和校验信息；
- unknown、insufficient evidence、opposing evidence 和 hold 状态被保留，不强行排序或生成资产；
- 输出经过独立 ChatGPT PR 审核后，才允许进入下一步运行或 pair 生成。

## 审核门

本 PR 只审核执行契约和范围。只有 ChatGPT 明确返回 `APPROVE` 后，才允许执行外部文献/公共数据枚举；运行完成后仍需通过结果 PR 再次审核。
