# Biotech 基础设施复用目录

## 目的

本文档把 Asset-Generation-OS 架构中可直接复用的外部生物技术基础设施
登记为未来 provider/adapter 的调用来源。本文档只定义复用边界和接入方向，
暂不下载数据、暂不实现 adapter、暂不引入运行时依赖。

核心原则：

> 底层数据接入、标准化、索引、检索和基础分析尽量复用成熟公共基础设施；
> ADC 语义、证据解释、证据可采纳性、Gate、Rule 和资产决策必须由
> StelligenOS 自己定义并审计。

## 可直接复用的外部基础设施

以下服务未来应作为可替换的外部 provider 使用。数据、缓存、运行结果和
下载文件全部位于仓库外部的 `DATA/` 工作区；本仓库只保存 schema、adapter、
查询规范、证据合同、provenance、标准化规则、Gate 映射、决策逻辑和测试。

| 能力层 | 可复用基础设施 | 未来用途 | 当前定位 |
|---|---|---|---|
| 文献 | [Europe PMC](https://europepmc.org/RestfulWebService)、[PMC OA/BioC](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/) | 文献元数据、JATS XML、开放全文、supplementary、引用关系、文本挖掘 | 第一优先级 |
| 临床试验 | [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api)、[AACT](https://aact.ctti-clinicaltrials.org/points_to_consider) | ADC trial、适应症、干预、endpoint、阶段、状态、公开结果和 AE | 第一优先级 |
| Target-disease | [Open Targets](https://platform.opentargets.org/api) | target identity、疾病本体、target-disease association、tractability、safety、已知药物 | 第一优先级；不直接继承其总分 |
| 单细胞 | [CZ CELLxGENE Census](https://chanzuckerberg.github.io/cellxgene-census/) | tumor/normal/cell-state expression、细胞类型特异性、共表达和疾病上下文 | 第一优先级 |
| 专利 | [EPO OPS](https://www.epo.org/en/searching-for-patents/data/web-services/ops)、[WIPO PATENTSCOPE](https://www.wipo.int/en/web/patentscope)、[Lens API](https://support.lens.org/knowledge-base/lens-patent-and-scholar-api/) | 专利全文、族、claims、申请人、引证和 patent-paper linkage | 第一优先级；不是自动 FTO |
| 正常组织 | [GTEx](https://gtexportal.org/)、[Human Protein Atlas](https://www.proteinatlas.org/) | normal tissue RNA、IHC、蛋白定位、组织/细胞类型分布、on-target/off-tumor 初筛 | 第二优先级 |
| 癌症组学 | [GDC/TCGA](https://gdc.cancer.gov/)、[cBioPortal](https://www.cbioportal.org/)、[DepMap](https://depmap.org/portal/) | cohort expression、CNV、mutation、临床结局、dependency、lineage 和 payload context | 第二优先级 |
| 蛋白与结构 | [UniProt](https://www.uniprot.org/)、[PDB](https://www.rcsb.org/)、[AlphaFold DB](https://alphafold.ebi.ac.uk/)、[InterPro](https://www.ebi.ac.uk/interpro/) | protein identity、isoform、topology、胞外区、跨膜区、domain、结构和 epitope 基础 | 第二优先级 |
| 化合物与活性 | [ChEMBL](https://www.ebi.ac.uk/chembl/)、[PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest-tutorial)、[BindingDB](https://www.bindingdb.org/rwd/bind/BindingDBRESTfulAPI.jsp) | payload、linker-warhead、靶点配体、bioactivity、assay 和竞争性 modality | 第二优先级 |
| 监管与公司披露 | FDA、EMA、公司公告和监管文件 | 临床结果、标签、警告、终止原因、产品和竞争格局交叉核对 | provider 组合 |

## 未来 provider 接口方向

未来接入时优先保持 provider 可替换，不把任何单一平台的 proprietary score
变成 StelligenOS 核心语义。建议的接口边界如下：

```text
LiteratureProvider       -> Europe PMC / PMC OA / Crossref
ClinicalTrialProvider    -> ClinicalTrials.gov API / AACT
TargetEvidenceProvider   -> Open Targets
SingleCellProvider       -> CELLxGENE Census
CancerGenomicsProvider   -> GDC / cBioPortal / DepMap
NormalTissueProvider     -> GTEx / Human Protein Atlas
ProteinProvider          -> UniProt / PDB / AlphaFold DB / InterPro
ChemistryProvider        -> ChEMBL / PubChem / BindingDB
PatentProvider            -> EPO OPS / PATENTSCOPE / Lens
RegulatoryProvider        -> FDA / EMA / company filings
```

每个 provider 未来至少需要返回：

- 外部来源身份和版本；
- 查询条件与时间戳；
- 原始记录引用，而不是把原始数据复制到仓库；
- 标准化对象和字段映射；
- provenance、license 和 checksum 信息；
- 未找到、冲突、不可解析和权限受限状态。

## 不可直接外包给公共平台的层

公共平台提供的是上游事实或聚合证据，不直接替代以下 StelligenOS 逻辑：

1. ADC-specific target identity、胞外可达性、表面定位和 internalization 解释。
2. RNA、蛋白、表面抗原密度、epitope accessibility 和 shedding 的证据分层。
3. evidence claim 与 source span 的绑定、证据 admissibility 和冲突处理。
4. indication、clinical context、endpoint、target、product 和 Gate 的归属。
5. modality-specific risk、therapeutic-window、fatal-first 和 Gate 映射。
6. Rule、资产决策、下一步实验以及人类审批记录。
7. 专利 claim construction、CDR/epitope scope、Markush mapping、司法辖区可执行性和最终 FTO 结论。

特别约束：

- Open Targets 分数不能直接映射为 ADC T Gate 分数。
- 单细胞 RNA 证据不能自动升格为蛋白表面表达、抗原密度或 ADC 可行性。
- DepMap dependency 不是 ADC 必需条件；ADC 可以利用非驱动型表面抗原递送 payload。
- HPA IHC 是初筛证据，不是临床 therapeutic-window 证据。
- ClinicalTrials.gov/AACT 不是完整 outcome 数据库，论文、会议、公司和监管来源需要交叉核对。
- 专利数据库是 patent data infrastructure，不是 FTO engine。

## 当前仓库可以直接复用的内部基础

当前仓库已经提供、未来 provider 不应重复造的内部承载层：

- `src/` 的核心对象、生命周期、能力和合同边界；
- `genmodules/` 的 GenModule 合同、模块说明、Gate/Model 注册和外部运行边界；
- `genmodules/target_safety_therapeutic_window_prescreen/` 的 target-level ADC 安全预筛合同与保守决策逻辑；
- `genmodules/assetgenos_catalog/` 的 indication、endpoint、target opportunity、product realization 和商业执行目录；
- `src/capabilities/` 中的 evidence sufficiency 和 clinical frame 能力；
- `scripts/verify_repository_boundary.sh`、CI 和测试体系；
- `logs/`、`docs/handoff/` 和 external reference 约束形成的审计留痕机制。

这些模块目前是合同和决策层，不等于已经接通上述公共数据源。未来接入应新增
小而明确的 provider adapter 和外部运行配置，不应把数据集、数据库、cache 或
result 写进本仓库。

## 实施顺序

### 第一批

1. Europe PMC/PMC OA：文献全文和证据定位。
2. ClinicalTrials.gov + AACT：临床 ADC 资产和 trial outcome 骨架。
3. Open Targets：target baseline context，不继承其最终分数。
4. CELLxGENE Census：tumor/normal/cell-state expression evidence。
5. EPO OPS + PATENTSCOPE：专利检索、族和 claim 文档层。

### 第二批

GTEx/HPA、DepMap、GDC/cBioPortal、UniProt/PDB/AlphaFold/InterPro、
ChEMBL/PubChem/BindingDB，以及监管与公司披露 provider。

Paper2Agent 可作为独立的 tool onboarding / method reproduction 小试验，
用于复现有公开代码的单细胞或抗体设计论文，但不应集成进核心 Evidence
Engine。Virtual Lab 的 specialist、critic、meeting transcript 和 human
intervention 编排模式可以参考，但不应取代现有 GenModule、Gate、PR review
和外部 DATA 约束。没有明确成熟、稳定官方仓库的工具不列为生产依赖。

## 仓库边界声明

本目录是架构参考文档，不是 provider 实现清单，不产生数据，也不授权自动
下载、自动评分或自动做资产决策。任何未来实施仍必须单独定义输入/输出合同、
外部 DATA 路径、provenance、测试、失败状态和人类审核边界。

# 2026-08-05补充

你的总分类方向是对的，但入库前必须纠正一个关键概念：

> **TCGA、HTAN、CPTAC、GENIE 是直接测量患者或患者肿瘤的数据；DepMap、PDO、PDX 则主要是患者来源模型上的数据。**

二者不能都标成 `patient_data`。否则后面做证据聚合时，Stelligen 会把“患者体内观察”“离体模型扰动”“长期培养细胞系扰动”错误地放在同一证据层级。

建议将这一整套命名为：

## Cancer Patient–Anchored Data Infrastructure

即：

> 以癌症患者为原始锚点，覆盖患者直接观测、患者来源模型、遗传/药物扰动和临床结局的数据基础设施。

---

## 一、Stelligen 的总分层

建议统一分成四层，而不是简单分成“观测”和“扰动”。

### Layer P1：Direct Patient Observation

直接来自患者肿瘤、正常组织、血液、影像或临床记录。

回答的是：

* 患者中存在什么？
* 在什么癌种、分期、治疗状态和人群中存在？
* 与临床结局有什么关系？
* 空间上位于哪里？
* 哪些细胞群体表达或激活了目标？

这是患者真实性最高的一层，但通常只能建立关联，不能单独建立干预因果。

### Layer P2：Patient-Derived Living Models

由患者肿瘤建立的可培养或可移植模型：

* PDO；
* PDX；
* conditionally reprogrammed cells；
* neurospheres；
* low-passage patient-derived cultures。

回答的是：

* 患者肿瘤能否在实验系统中被保留？
* 哪些状态和分子特征可以稳定建模？
* 是否可以进行重复扰动？
* 模型与原始肿瘤保持了多少一致性？

这一层是患者观测与实验因果之间的桥梁。

### Layer P3：Model Perturbation

在 cell line、PDO、PDX 或其他模型上实施：

* CRISPR knockout；
* CRISPRi/a；
* RNAi；
* small-molecule treatment；
* biologics treatment；
* drug combination；
* resistance selection；
* lineage tracing；
* temporal perturbation。

回答的是：

* 某个基因或通路是否为 dependency？
* 哪些分子特征预测扰动响应？
* 干预是否改变生长、死亡、状态、分化或药物敏感性？
* 是否存在 synthetic lethality 或 resistance mechanism？

这里才是主要的实验因果层。

### Layer P4：Clinical Intervention and Outcome

来自临床试验、真实世界治疗和纵向临床记录：

* 治疗暴露；
* response；
* progression；
* recurrence；
* survival；
* toxicity；
* biomarker-defined response；
* treatment sequence。

回答的是：

* 对真实患者实施干预后发生了什么？
* 哪个患者群体获益？
* 获益对应什么 endpoint？
* biomarker 是否具有临床预测价值？

这是距离产品假设和临床 endpoint 最近的一层。

---

## 二、核心患者观测基础设施

### 1. TCGA

**分类**

`P1_DIRECT_PATIENT_OBSERVATION`

**主要数据**

* 肿瘤和部分配对正常组织；
* somatic mutation；
* copy-number alteration；
* DNA methylation；
* bulk RNA-seq；
* miRNA；
* 部分蛋白数据；
* 病理及基础临床信息。

**主要价值**

* 泛癌基因改变和表达基线；
* 癌种特异性；
* molecular subtype；
* alteration–expression association；
* primary untreated tumour 的群体分布；
* target prevalence 的初步估计。

**主要限制**

* 以原发、手术切除肿瘤为主；
* 许多患者缺乏完整治疗和长期结局；
* bulk 数据无法精确判断信号来自 malignant、immune 还是 stromal cells；
* 对复发、转移、治疗后残留状态覆盖有限。

**Stelligen 中的角色**

`population_baseline_resource`

主要支持：

* indication prevalence；
* molecular context；
* alteration frequency；
* bulk expression；
* preliminary outcome association。

但不应单独支持：

* intervention causality；
* cell-surface availability；
* internalization；
* drug response causality。

---

### 2. HTAN

**分类**

`P1_DIRECT_PATIENT_OBSERVATION`

HTAN 建立癌症从癌前病变到晚期疾病演化过程的三维图谱，包含 single-cell、spatial、genomic、transcriptomic、proteomic 和 imaging 数据。其数据通过 HTAN Portal、Synapse、Imaging Data Commons 等渠道提供；截至 2026 年 8 月，门户已经发布 Phase 2 数据。([Human Tumor Atlas][1])

**主要价值**

* malignant cell state；
* immune/stromal ecosystem；
* spatial organization；
* tumour evolution；
* precancer–primary–metastasis transition；
* treatment-related state；
* endpoint-driving cell population 的候选识别。

**主要限制**

* 不同 atlas 的癌种、技术和设计差异较大；
* cohort 往往比 TCGA 小；
* 许多数据是横截面的；
* 不同平台间直接整合困难；
* 单细胞或空间 abundance 不等于功能 dependency。

**Stelligen 中的角色**

`cell_state_and_spatial_context_resource`

重点支持：

* endpoint-driving population；
* target-to-population mapping；
* state specificity；
* intratumoral accessibility；
* normal-cell and stromal context；
* treatment-induced state hypothesis。

这是 Stelligen 识别 **谁在驱动临床问题** 的核心资源。

---

### 3. CPTAC

**分类**

`P1_DIRECT_PATIENT_OBSERVATION`

CPTAC 通过 proteogenomics 把基因组、转录组、蛋白组和磷酸化蛋白组连接起来。其目标是识别由癌症基因改变引起的蛋白层变化，并帮助优先排序 driver 和患者亚型；数据通过 GDC 和 Proteomic Data Commons 提供。([NCI Genomic Data Commons][2])

**主要价值**

* RNA 到 protein 的一致性；
* pathway activation；
* phosphoproteomic state；
* target protein abundance；
* post-translational regulation；
* genomic alteration 是否真正传导至蛋白层。

**主要限制**

* 组织水平蛋白组仍然是混合细胞信号；
* total protein abundance 不等于膜表面 abundance；
* mass spectrometry 对低丰度膜蛋白不一定敏感；
  -不能证明抗体可结合表位、内吞或正常组织治疗窗口。

**Stelligen 中的角色**

`protein_translation_and_pathway_activity_resource`

支持：

* transcript-to-protein confirmation；
* pathway activity；
* protein-level target prioritization；
* phosphosignalling context。

对 ADC 而言只能作为：

`supportive_surface_expression_evidence`

不能作为：

`direct_surface_availability_evidence`。

---

### 4. AACR Project GENIE

**分类**

`P1_DIRECT_PATIENT_OBSERVATION`
加
`P4_CLINICAL_OUTCOME`

GENIE 是来自国际癌症中心的真实世界临床基因组 registry。官方当前页面报告其包含超过 20 万患者和超过 23 万份临床级基因组样本，并持续加入新病例；最新公开版本继续扩展 longitudinal clinico-genomic data。([AACR][3])

**主要价值**

* 临床检测环境中的 mutation prevalence；
* 晚期和转移性患者；
* 稀有 genomic subgroup；
* biomarker–treatment–outcome；
* clinical trial feasibility；
* real-world treatment pattern；
* longitudinal disease course。

**主要限制**

* 测序 panel 不统一；
* 缺失未检测区域不能解释为野生型；
* 治疗和 outcome 数据完整度不均；
* referral-center selection bias；
* 观察性治疗数据存在 indication bias 和 confounding。

**Stelligen 中的角色**

`real_world_clinico_genomic_resource`

支持：

* anchor clinical context；
* biomarker population size；
* treatment exposure；
* observed endpoint performance；
* resistance evolution；
* trial feasibility。

---

### 5. ICGC / ICGC ARGO

**分类**

`P1_DIRECT_PATIENT_OBSERVATION`
加
`P4_CLINICAL_OUTCOME`

ICGC ARGO 旨在将高质量临床信息和统一处理的癌症基因组数据连接起来。平台目标是覆盖大规模国际患者队列，并采用统一参考基因组和分析流程。([ICGC Argo][4])

**主要价值**

* 国际患者群体；
* 非美国队列；
* longitudinal clinical data；
* clinical trial 或深度临床注释队列；
* WGS-level alteration；
* mutational process；
* ancestry 和地理多样性。

**主要限制**

* 多数受控数据需要审批；
* 各 program 临床字段完整度不同；
* 数据规模和成熟度随 release 变化；
* 跨项目 harmonization 仍需要额外处理。

**Stelligen 中的角色**

`international_clinical_genomics_resource`

主要用于补充：

* TCGA 的原发肿瘤偏倚；
* GENIE 的 panel sequencing 局限；
* 国际和祖源代表性；
* treatment-linked genomic evolution。

---

## 三、患者来源活模型基础设施

### 6. HCMI

**分类**

`P2_PATIENT_DERIVED_MODEL`

HCMI 建立患者来源 next-generation cancer models，包括 organoid、conditionally reprogrammed cells、neurospheres 和其他低传代培养模型，同时提供原始组织、模型、正常组织、临床和分子表征信息。([Cancer.gov][5])

**主要价值**

* 原始患者和模型之间的配对；
* 模型可获得性；
* genomic fidelity；
* 临床注释；
* rare cancer representation；
* 可重复开展后续实验。

**主要限制**

* 模型建立成功存在非随机选择；
* 培养基会重塑细胞状态；
* 微环境大量丢失；
* 模型长期传代后可能发生漂移；
* 并不是所有模型都拥有系统扰动数据。

**Stelligen 中的角色**

`patient_to_model_bridge_resource`

核心作用不是直接证明 dependency，而是证明：

* 某种患者肿瘤是否已有 living model；
* 模型是否保留关键分子特征；
* 是否具备进一步验证条件。

---

### 7. Sanger Cell Model Passports / Organoid Dependency Map

**分类**

`P2_PATIENT_DERIVED_MODEL`
加
`P3_MODEL_PERTURBATION`

Sanger Dependency Map 目前同时包括 cell lines 和 organoids，并通过 Cell Model Passports 提供模型注释和数据。([DepMap][6])

**主要数据**

* patient-derived organoid；
* matched tumour/model genomics；
* RNA expression；
* CRISPR dependency；
* drug response；
* model culture and provenance；
* 部分治疗前后或临床状态注释。

**主要价值**

* patient-derived context 中的 genetic dependency；
* dependency–biomarker association；
* 2D 与 PDO dependency 差异；
* 癌种或分子亚型选择性；
* 可直接获得模型开展实验。

**主要限制**

* viability screen 是主要 readout；
* cohort 在细分癌种后迅速变小；
* establishment bias；
* culture-condition dependency；
* 缺少完整免疫和基质生态；
* organoid growth effect 不等同于患者临床获益。

**Stelligen 中的角色**

`patient_derived_functional_genomics_resource`

---

### 8. PDXNet / PDMR / PDX Data Commons

**分类**

`P2_PATIENT_DERIVED_MODEL`
加
`P3_MODEL_PERTURBATION`

PDXNet 通过大规模患者来源异种移植模型测试治疗策略，目标是覆盖分子多样性、评估药物组合并推进到临床验证。NCI 也通过 PDMR 建立、表征和分发 patient-derived models。([Cancer Treatment & Diagnosis][7])

**主要价值**

* 体内药物暴露；
* tumour growth inhibition；
* response duration；
* combination response；
* resistance；
* pharmacology；
* 一定程度保留组织结构和克隆异质性。

**主要限制**

* 小鼠宿主；
* 多数模型使用免疫缺陷小鼠；
* 人类 stromal components 会逐渐被鼠源成分替代；
* 成本高、通量低；
* implantation selection；
* 药代动力学和人体不完全一致。

**Stelligen 中的角色**

`in_vivo_patient_derived_intervention_resource`

用于加强：

* intervention response；
* combination hypothesis；
* resistance；
* in vivo efficacy；
* response heterogeneity。

但不能替代：

* human toxicity；
* human immune response；
* clinical endpoint evidence。

---

## 四、扰动基础设施

### 9. Broad DepMap

**分类**

`P3_MODEL_PERTURBATION`

需要明确：经典 DepMap 的主体是长期培养的癌细胞系，不是直接患者数据。它提供开放的癌症 dependency、分子表征和分析工具，用于发现癌症 vulnerabilities。([DepMap][8])

**主要数据**

* CRISPR gene effect；
* legacy RNAi；
* copy number；
* mutation；
* gene expression；
* methylation；
* proteomics；
* metabolomics；
* lineage；
* model annotation；
* compound response 的关联数据。

**主要价值**

* 泛癌 genetic dependency；
* common essentiality；
* selective dependency；
* lineage dependency；
* biomarker association；
* synthetic lethal hypothesis；
* 大规模统一筛选。

**主要限制**

* 经典 cell line 与患者肿瘤存在状态差异；
* 无完整微环境；
* viability-centric；
* 培养适应；
* gene knockout 不等同于药物抑制；
* dependency 不能自动转换为 druggability；
* 对 ADC target 的直接意义有限。

**Stelligen 中的角色**

`high_throughput_genetic_dependency_resource`

主要支持：

* intervention causality 的前临床部分；
* target essentiality；
* context selectivity；
* resistance mechanism；
* payload sensitivity context。

不能直接支持：

* patient prevalence；
* surface availability；
* therapeutic window；
* clinical benefit。

---

### 10. GDSC、PRISM及其他药物反应资源

**分类**

`P3_MODEL_PERTURBATION`

建议把这类资源作为一个统一 resource family，而不是每个数据库建立完全不同的对象。

**主要数据**

* cell line × compound；
* dose response；
* viability；
* sensitivity metric；
* molecular biomarker；
* combination response，视具体项目而定。

**主要价值**

* pharmacological dependency；
* gene–drug association；
* pathway sensitivity；
* payload class sensitivity；
* resistance phenotype；
* CRISPR dependency 与药物效应的一致性验证。

**主要限制**

* drug polypharmacology；
* assay duration 差异；
* dose 和 exposure 不一定具有临床可达性；
* viability readout；
* cell line context；
* 不同项目的 response metric 不可直接混合。

**Stelligen 中的角色**

`pharmacological_perturbation_resource`

对于 ADC 尤其可以用于：

* payload susceptibility；
* DNA-damage sensitivity；
* topoisomerase-I inhibitor sensitivity；
* tubulin inhibitor sensitivity；
* resistance mechanism；
* target-independent payload ceiling。

---

## 五、Stelligen 应采用的统一资源目录

建议第一版只收录以下十个 canonical resource family：

| resource_id        | 资源                                           |   数据层 |  是否直接患者测量 |   是否含扰动 | 核心用途                      |
| ------------------ | -------------------------------------------- | ----: | --------: | ------: | ------------------------- |
| TCGA               | The Cancer Genome Atlas                      |    P1 |         是 |       否 | 泛癌基线、组学、亚型                |
| HTAN               | Human Tumor Atlas Network                    |    P1 |         是 | 少量/项目特异 | 单细胞、空间、演化状态               |
| CPTAC              | Clinical Proteomic Tumor Analysis Consortium |    P1 |         是 |       否 | 蛋白和通路活性                   |
| GENIE              | AACR Project GENIE                           | P1/P4 |         是 |  临床治疗暴露 | 临床基因组、真实世界结局              |
| ICGC_ARGO          | ICGC ARGO                                    | P1/P4 |         是 |  临床治疗暴露 | 国际临床基因组                   |
| HCMI               | Human Cancer Models Initiative               |    P2 |   间接，患者来源 |      部分 | living model 和患者–模型连接     |
| SANGER_DEPMAP      | Sanger Dependency Map                        | P2/P3 | 间接，部分 PDO |       是 | PDO/细胞系 dependency        |
| BROAD_DEPMAP       | Broad DepMap                                 |    P3 |    否，模型来源 |       是 | 大规模遗传 dependency          |
| PDXNET_PDMR        | PDXNet/PDMR                                  | P2/P3 |   间接，患者来源 |       是 | 体内药物反应                    |
| DRUG_RESPONSE_MAPS | GDSC/PRISM 等                                 |    P3 |    否，模型来源 |       是 | 药理依赖和 payload sensitivity |

---

## 六、不要把“数据集”和“入口门户”混在一起

Stelligen 入库时需要区分三种实体。

### 1. Resource program

产生数据的科学计划：

* TCGA；
* HTAN；
* CPTAC；
* HCMI；
* DepMap。

### 2. Data repository

实际托管文件的地方：

* GDC；
* PDC；
* IDC；
* Synapse；
* dbGaP；
* AnVIL；
* Terra；
* Cell Model Passports。

### 3. Analysis portal

提供查询、可视化或二次整理的入口：

* cBioPortal；
* DepMap Portal；
* HTAN Portal；
* Cell Model Passports；
* GENIE Portal。

例如：

```text
resource_program: CPTAC
data_repository:
  - GDC
  - PDC
  - IDC
analysis_portal:
  - CPTAC Pan-Cancer portal
```

不能把 GDC、TCGA、CPTAC 和 cBioPortal 当成四个平行数据源。它们分别属于计划、托管层和访问层。

---

## 七、建议的 Stelligen 数据对象

每条基础设施记录至少包含以下字段。

```yaml
resource_id: HTAN
resource_name: Human Tumor Atlas Network
resource_version: "V8.0"
release_date: "2026-08-03"

resource_class:
  - direct_patient_observation
  - single_cell_atlas
  - spatial_atlas

patient_anchor_type: direct_patient_specimen

model_type:
  - none

perturbation_status: primarily_observational

data_modalities:
  - scRNA_seq
  - scATAC_seq
  - spatial_transcriptomics
  - imaging
  - genomics
  - proteomics

clinical_context_fields:
  - cancer_type
  - disease_stage
  - specimen_site
  - primary_or_metastatic
  - treatment_status
  - timepoint

evidence_capabilities:
  - malignant_cell_state
  - endpoint_driving_population
  - target_population_mapping
  - spatial_accessibility
  - treatment_state
  - ecosystem_context

evidence_non_capabilities:
  - direct_intervention_causality
  - antibody_internalization
  - clinical_efficacy
  - therapeutic_window

access:
  open_processed_data: true
  controlled_raw_data: true
  repositories:
    - Synapse
    - Imaging Data Commons

provenance:
  official_program: NCI_HTAN
  source_url: canonical_url
  retrieved_at: timestamp

known_biases:
  - cohort_selection
  - assay_heterogeneity
  - center_effect
  - cross_sectional_sampling
  - limited_sample_size

ingestion_priority: P0
```

---

## 八、每条证据必须继承的数据血缘

数据入库不能只保存：

```text
gene = FAP
expression = high
source = HTAN
```

至少要保留：

```text
resource
release_version
project_or_cohort
patient_id
specimen_id
sample_id
model_id
assay_id
data_modality
processing_level
cancer_type
histology
primary_site
specimen_site
primary_or_metastatic
pretreatment_or_posttreatment
therapy_context
timepoint
cell_type_or_state
perturbation_type
perturbation_agent
dose
duration
readout
endpoint
effect_direction
effect_size
uncertainty
source_file
source_record_id
access_level
license
```

尤其必须分开以下 ID：

* patient；
* tumour specimen；
* aliquot；
* derived model；
* model replicate；
* perturbation experiment。

不能把同一患者建立的多个模型、同一模型的多个实验或同一肿瘤的多个区域当作独立患者。

---

## 九、Stelligen 证据强度不能按数据库名决定

建议采用二维证据坐标。

### 维度 A：与患者的距离

```text
A0 direct clinical intervention in patients
A1 direct patient longitudinal observation
A2 direct patient cross-sectional observation
A3 low-passage patient-derived model
A4 PDX
A5 established cell line
A6 engineered or non-tumour model
```

这里不宜简单认定 PDX 一定高于 PDO。二者保留的生物学不同：

* PDX 更接近体内生长和药代环境；
* PDO 更适合高通量和人源 epithelial state；
* 两者都存在特定选择偏差。

### 维度 B：因果强度

```text
B0 randomized clinical intervention
B1 prospective clinical intervention
B2 controlled in vivo perturbation
B3 controlled patient-derived ex vivo perturbation
B4 controlled cell-line perturbation
B5 longitudinal natural experiment
B6 observational association
B7 descriptive presence or absence
```

因此：

* TCGA RNA expression：`A2 × B6/B7`
* HTAN treatment-paired scRNA：`A1 × B5/B6`
* PDO CRISPR：`A3 × B3`
* PDX drug trial：`A4 × B2`
* DepMap CRISPR：`A5 × B4`
* Phase III biomarker trial：`A0 × B0`

这比设置一个粗糙的 `evidence_strength = high/medium/low` 更可靠。

---

## 十、映射到 Stelligen Gate

### 患者群体与临床背景

主要数据源：

* GENIE；
* ICGC ARGO；
* TCGA；
* clinical trial datasets。

支持：

* anchor clinical context；
* patient prevalence；
* treatment history；
* molecular subgroup；
* intended benefit；
* observed endpoint。

### Endpoint-driving population

主要数据源：

* HTAN；
* 单细胞/空间患者 cohort；
* longitudinal patient samples；
* pathology and imaging。

支持：

* malignant state；
* residual population；
* metastatic population；
* treatment-induced population；
* spatial niche。

### Intervention causality

主要数据源：

* PDO CRISPR；
* PDO drug screen；
* DepMap；
* PDXNet；
* clinical intervention datasets。

支持：

* dependency；
* drug response；
* resistance；
* synthetic lethality；
* combination response。

### Target presence and modality realization

主要数据源：

* HTAN；
* CPTAC；
* HCMI/PDO；
* dedicated surface proteomics；
* internalization assays；
* antibody-binding experiments。

必须注意：

TCGA、HTAN 和 CPTAC 最多帮助提出 ADC target hypothesis，不能替代：

* membrane density；
* extracellular epitope；
* internalization；
* lysosomal trafficking；
* normal-tissue accessibility；
* ADC payload release。

---

## 十一、第一阶段入库边界

建议不要一开始把所有原始矩阵下载进 Stelligen。第一阶段只建立 **Resource Registry + Dataset Registry + Evidence Capability Registry**。

### Phase 1：Resource registry

入库十个 canonical resource family，记录：

* 资源定义；
* 数据类型；
* 患者距离；
* 扰动类型；
* access；
* version；
* limitations；
* Gate applicability。

### Phase 2：Dataset registry

再拆到具体 cohort 或 release：

```text
TCGA_COAD
TCGA_READ
HTAN_CRC_ATLAS_X
CPTAC_COAD
GENIE_CRC_PUBLIC_19
HCMI_CRC_MODELS
SANGER_CRC_ORGANOID_DEPENDENCY
DEPMAP_CRC_26Q2
PDXNET_CRC_DRUG_RESPONSE
```

### Phase 3：Evidence ingestion

只抽取能够服务当前问题的证据：

* CRC；
* endpoint-driving state；
* surface target；
* dependency；
* treatment resistance；
* ADC payload sensitivity。

### Phase 4：Raw-data compute

只有在已有明确问题时，才下载并重分析：

* scRNA matrix；
* spatial images；
* CRISPR matrices；
* WES/WGS；
* proteomics；
* drug-response curves。

否则会迅速变成一个存储量巨大的数据坟场。

---

## 最终定义

可以把 Stelligen 的这部分正式定义为：

> **Cancer Patient–Anchored Data Infrastructure：以癌症患者、患者肿瘤及其派生模型为锚点，整合直接患者观测、单细胞和空间状态、临床基因组、蛋白组、患者来源活模型、遗传扰动、药物扰动及临床结局的数据基础设施。**

其内部不是一个扁平数据库，而是四层证据空间：

```text
P1 Patient Observation
        ↓
P2 Patient-Derived Models
        ↓
P3 Experimental Perturbation
        ↓
P4 Clinical Intervention and Outcome
```

Stelligen 的价值不在于重新保存所有原始数据，而在于维护：

```text
Patient context
× Cell state
× Molecular feature
× Living model
× Perturbation
× Phenotype
× Clinical endpoint
× Provenance
```

这套结构可以直接作为你的基础设施入库总纲。最重要的硬规则是：

> **患者直接观测、患者来源模型和长期细胞系数据必须分层；observational association、experimental causality 和 clinical causality 必须分层；数据库存在某个字段，不等于该数据库能够支持对应 Gate。**

[1]: https://humantumoratlas.org/?utm_source=chatgpt.com "NCI Human Tumor Atlas Network"
[2]: https://gdc.cancer.gov/about-gdc/contributed-genomic-data-cancer-research/clinical-proteomic-tumor-analysis-consortium-cptac?utm_source=chatgpt.com "Clinical Proteomic Tumor Analysis Consortium (CPTAC)"
[3]: https://www.aacr.org/professionals/research/aacr-project-genie/collaborate/registry/?utm_source=chatgpt.com "Registry | Project GENIE | AACR"
[4]: https://www.icgc-argo.org/?utm_source=chatgpt.com "ICGC ARGO - Home"
[5]: https://www.cancer.gov/ccg/research/functional-genomics/hcmi?utm_source=chatgpt.com "Human Cancer Models Initiative (HCMI)"
[6]: https://depmap.sanger.ac.uk/documentation/cell-models/?utm_source=chatgpt.com "Models - The Cancer Dependency Map at Sanger"
[7]: https://dctd.cancer.gov/research/networks/precision-medicine-oncology/pdxnet?utm_source=chatgpt.com "PDXNet - NCI"
[8]: https://depmap.org/?utm_source=chatgpt.com "DepMap: The Cancer Dependency Map Project at Broad ..."
