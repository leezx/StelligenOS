# `gen_indication_endpoint_target` 产品目的与动态需求

## 文档定位

这不是一次性冻结的技术规格，也不是数据库 schema。本文件记录
`gen_indication_endpoint_target` 当前要解决的问题、最终产品形态、证据原则和
需求演进方向。需求会随着人类认知、项目目标和新证据变化而迭代；旧版本不删除，
新版本必须说明改变了什么、为什么改变，以及对代码、数据边界和输出的影响。

## 当前产品目的

StelligenOS 的核心目的不是把数据存进软件仓库，也不是先建设一个复杂数据库。
它要从真实临床未满足需求出发，持续生成、比较和淘汰具有 ADC 可行性依据的：

`indication + endpoint + target`

系统要回答：哪个疾病场景缺少有效治疗、应该改善什么临床结果、哪个 ADC 靶点
值得进入候选池、当前证据支持到什么程度、哪里只是未知、哪里存在明确反对证据。

## 要解决的问题

1. 不能先凭兴趣选 target，再事后寻找 indication。
2. 不能只列癌种和靶点而不固定可以判断的 endpoint。
3. 不能把表达、定位或内吞线索直接写成已验证 biomarker 或 ADC 机会。
4. 不能只生成漂亮报告，却无法回答每个 Gate 的分数、证据量和反对证据。

本模块必须是从临床需求到候选 pair 的可重复、可追溯、可停止的计算流程，不能
停留在架构接口。

## 目标工作流

### 1. Clinical unmet need discovery

从旧 AssetGenOS 和外部数据工作区的版本化 clinical unmet-need reference
提取癌种、亚型、治疗线次、既往治疗、现有选择、临床缺口和优先级。例如 CRC
中的 MSS/pMMR metastatic colorectal cancer、标准治疗后、三线及以后，是一个
具体 indication 场景，不是泛化的“CRC 靶点挖掘”。

### 2. Endpoint lock

对每个 unmet-need 场景识别值得优化的 endpoint，并在 target mining 前固定
indication/endpoint 组合。每个 endpoint 必须记录名称、临床含义、适用人群和线次、
与 unmet need 的关系、来源、截止日期、证据等级，以及它是主要 endpoint、关键
次要 endpoint 还是探索性 proxy。无法可靠固定 endpoint 时必须 `HOLD`，不得偷偷
替换成方便计算的 surrogate。

### 3. Biomarker hypothesis generation

在 indication/endpoint 固定后，使用公共数据、文献和旧项目 evidence 生成
biomarker hypothesis，例如 oncofetal malignant-state、target-high malignant
cell state、亚型、治疗耐药状态、IHC/RNA/蛋白或组合标志物。每个 biomarker 必须
标记为 `hypothesis`、`supported_hypothesis` 或 `externally_validated`；相关性
不能自动升级为临床可用 biomarker。

### 4. ADC target discovery and filtering

候选 target 至少检查：细胞表面定位、receptor-mediated endocytosis/endocytosis
或 lysosomal-routing 线索、ADC precedent、soluble sink/shedding、正常组织风险，
以及 target evidence 是否与 indication/biomarker 假设相容。缺少内吞证据应为
`unknown` 或 `HOLD`，不能把数据库缺失当成不会内吞；只有明确相反事实才进入
`opposing_evidence` 或 `REJECT`。

### 5. Frozen Gate evaluation

每个 `indication + endpoint + target` pair 调用当前冻结的 45-Gate 评估体系。
每个 Gate 必须输出 Gate ID/版本/名称、score、confidence、status、decision、
支持证据数和引用、缺失信息数和引用、明确反对证据数和引用、推荐下一步验证。
Gate 评估不能修改 Registry、Gate 语义或 T/P/C 编号，也不能为了候选生成增加新 Gate。

### 6. Pair output

主输出应简单到一行就是一个候选 pair，至少包含：

- indication
- endpoint
- target
- biomarker_hypothesis
- overall_status
- gate_pass_count
- gate_hold_or_unknown_count
- gate_fail_count
- evidence_count
- opposing_evidence_count
- explicit_opposition
- next_best_action

详细 Gate trace、证据表、来源 checksum、模型版本和运行 manifest 作为外部结果
附件保存，不能让复杂报告取代 pair 主表。

## 判断语义

- `unknown`：当前没有足够证据判断。
- `HOLD`：有潜力但关键证据缺口必须先解决。
- `opposing_evidence`：存在与假设相反的明确证据。
- `REJECT`：明确反对证据或 Hard Gate 失败足以停止候选。
- `ADVANCE`：达到当前计算筛选标准，不代表临床验证、可销售资产或法律/监管结论。

没有数据库记录、文献未找到或模型未返回，不能自动写成反对证据。每个 pair 必须
区分版本化公共数据库、文献、旧项目 golden trace、计算推断、人工假设和未验证
biomarker hypothesis。LLM 不能凭空制造数值、临床事实或反对证据。

## 数据和软件边界

StelligenOS 是软件和架构仓库，不是数据库。以下必须留在外部工作区：clinical
unmet-need 数据、公共数据库和全文、运行数据库/cache/result/weights/report、
pair 输出表、evidence ledger、运行 manifest、真实 pilot、实验结果和资产包。

StelligenOS 只保存代码、合同、架构、Prompt、测试、规则说明和小型必要示例。
代码通过 `BIOWORKSPACE_ROOT`、external reference 或显式 runtime 参数访问数据，
不把机器路径写死在可复用逻辑中。

## 成功标准

一个可用版本必须能够：

1. 从版本化 unmet-need 数据自动提出 indication，而不是要求用户逐个手工输入 target。
2. 在 target mining 前固定 endpoint，并保留来源和理由。
3. 从公共数据/文献生成可审计 biomarker hypothesis。
4. 只输出有 ADC surface/internalization 依据的 target，或明确标记 `HOLD`。
5. 对每个 pair 给出 45-Gate 分数、证据数、通过/未知/失败状态和反对证据。
6. 生成简单可排序的 pair 表，同时保留详细外部证据链。
7. 缺证据时诚实停止，不把低置信度结果包装成已验证资产。
8. 不向 StelligenOS 写入数据或运行产物。

## 当前不属于目标

- 不是先开发完整 Binder、抗体序列或生产级资产工厂。
- 不是建立新的数据库系统。
- 不是让模型替代临床、实验、法律或监管判断。
- 不是追求所有候选都通过 Gate；`HOLD` 和 `REJECT` 都是有效输出。
- 不是把公共数据相关性升级成 biomarker validation。

## 需求版本

### v0.1 - 2026-08-01：从架构合同转向候选 pair 产品

用户与 Codex 的讨论确认：第一产品目标是从 clinical unmet need 出发，固定
indication/endpoint，生成 biomarker hypothesis，筛选 ADC target，并输出带 Gate
分数、证据数量和反对证据的 `indication + endpoint + target` pair。

已完成的 Phase 0-9 架构冻结仍然有效，但不再被视为产品目标已经完成；它们是
Pair Discovery runtime 的软件边界和审计基础。此前手工输入 TWEAKR/CRC 的运行
只是评估一个已有候选，不等于自动发现 pair。

## 需求变更规则

以后每次需求变化都新增一个版本段，记录变更时间和提出者、新需求、被替代或保留
的旧需求、变更原因、新证据、对架构/数据边界/输出/测试的影响，以及是否需要新的
ChatGPT 审核 PR。本文件记录产品方向，不替代 Phase report、Decision Log、handoff
或 ChatGPT review record。
