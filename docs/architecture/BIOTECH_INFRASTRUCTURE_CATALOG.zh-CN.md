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
