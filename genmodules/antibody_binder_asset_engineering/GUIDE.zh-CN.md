# Existing-Binder Antibody Asset Engineering — 完整说明（v0.3.1）

模块 ID：`antibody_binder_asset_engineering`
版本：`0.3.1`（前身 `0.3.0`；最后独立归档版本为 `0.2.0`）

本文是 v0.3.1 的完整中文说明：定位、双轨架构、每个 stage 的作用、核心算法原理、
以及边界在哪里。

配套文档：

- `WORKLOG.zh-CN.md` — 中文工作日志（本次升级的缺陷清单、验证结果、遗留问题）
- `DESIGN.md` / `README.md` — 契约定义与快速上手（英文）
- 归档目录里的 `GUIDE.zh-CN.md` — v0.2.0 的原理说明，仍然有效，可对照阅读

---

## 目录

1. [v0.3.0 为什么存在](#1-v030-为什么存在)
2. [双轨架构](#2-双轨架构)
3. [14 个 Stage](#3-14-个-stage)
4. [核心机制一：ADC carrier phenotype 数据模型](#4-核心机制一adc-carrier-phenotype-数据模型)
5. [核心机制二：因果失效树与信息增益](#5-核心机制二因果失效树与信息增益)
6. [核心机制三：二维 Pareto 选择](#6-核心机制三二维-pareto-选择)
7. [核心机制四：七个候选家族](#7-核心机制四七个候选家族)
8. [核心机制五：ADC 产品实体模型](#8-核心机制五adc-产品实体模型)
9. [为什么不先接 ProteinMPNN](#9-为什么不先接-proteinmpnn)
10. [分数与禁止声明](#10-分数与禁止声明)
11. [从 v0.2.0 迁移](#11-从-v020-迁移)
12. [已知局限](#12-已知局限)
13. [使用方法](#13-使用方法)
14. [enavatuzumab 结果解读](#14-enavatuzumab-结果解读)
15. [核心机制六：region 并集、结构锚定位点、三条风险轴](#15-核心机制六region-并集结构锚定位点三条风险轴)

---

## 1. v0.3.0 为什么存在

v0.2.0 完成了第一次跃迁：从"工作包生成器"变成可执行的抗体**序列**工程 pipeline。它会编号、
会扫 liability、会用结构暴露度加权、会生成真实候选序列并排名。

但它的结构性问题不在机器，而在**目标函数**：

> v0.2.0 优化的是"一个更干净、更人源化、更可开发的**抗体**"，
> 而不是"一个能安全有效**递送载荷**的 ADC carrier"。

ADC 不是"更可开发的裸抗体 + payload"。两者的最优解可能完全相反：

| 维度 | 裸抗体倾向 | ADC carrier 倾向 |
|---|---|---|
| 受体信号 | 追求强功能、激动、Fc 效应 | 可能需要**功能沉默** |
| 亲和力 | 越高越好 | 可能牺牲亲和力换肿瘤穿透与受体周转 |
| 偶联 | 接受随机 Lys 偶联 | 优先位点特异性偶联 |
| 稳定性 | 只需游离态稳定 | 还要承受疏水 payload 对聚集、清除、非特异摄取的影响 |

v0.2.0 没有表型层，所以"内化""溶酶体递送""偶联后行为"只能以自由文本形式存在于一个证据
字段里——那不是数据，那是断言。

v0.3.0 的核心升级：

> 从 "sequence-centric developability optimization"
> 升级为 "phenotype-conditioned ADC carrier engineering"。

---

## 2. 双轨架构

```text
Track A：Binder molecule quality（计算得来）
  序列完整性 → liability → humanness → 候选序列
  → sequence_computational_developability_rank

Track B：ADC carrier phenotype（实测得来）
  内源细胞结合 → 五步递送级联 → 偶联耐受 → 偶联后行为
  → adc_carrier_quality_score
```

**两轨只在 Pareto 前沿相遇，绝不相加。**

为什么不能相加：加权求和允许"一个干净的序列"补偿"一个不内化的分子"。这恰恰是载荷递送
项目**唯一不能做的交换**。所以两轨各占一个坐标轴，用 Pareto 支配关系比较。

轨道的性质也不同，这一点必须记住：

- **Track A 是算出来的。** 只要有序列就能算，成本为零，但它不知道分子会不会递送载荷。
- **Track B 是测出来的。** 没有实验就没有数据，而**没有数据不等于差**（见第 4 节）。

---

## 3. 14 个 Stage

v0.3.0 的声明顺序与执行顺序**重新一致**了。v0.2.0 需要让 09 在 07 之前执行，v0.3.0 从
结构上解决：表型与失效树 stage 本身就排在前面。

| # | Stage | 轨道 | 作用 |
|---|---|---|---|
| 01 | `binder_intake` | A | 编号、区域划分、germline、liability、生物物理描述符 |
| 02 | `ip_fto_landscape` | — | 技术检索方案（含 epitope 权利要求提示） |
| 03 | `structural_analysis` | A | ABodyBuilder2 结构 + 每残基 SASA，暴露度加权 liability |
| 04 | `binder_engineering_design` | A | 序列突变提议 + 四个 construct 规格家族 |
| 05 | `candidate_family_generation` | A | 生成真实候选序列；构造规格另列 |
| 06 | `binder_quality_triage` | **A 出口** | Track A 排名 |
| 07 | `adc_carrier_phenotype` | **B 核心** | 五步递送级联、carrier 分数、模态决策 |
| 08 | `adc_product_assembly` | B | 抗体 × 偶联变体 → ADC 产品矩阵 |
| 09 | `adc_failure_mode_analysis` | — | 因果失效树 + 信息增益排序 |
| 10 | `pareto_selection` | A×B | 二维前沿；无 carrier 数据时拒绝选 lead |
| 11 | `experimental_design` | — | 按信息增益排序的关键路径 |
| 12 | `active_learning` | — | 严格数据闭环（不拟合模型） |
| 13 | `patent_package` | — | 面向律师的技术提纲 |
| 14 | `asset_report` | — | 汇总报告，以模态决策开头 |

02 阶段新增一条重要提示：

> 如果亲本 epitope 已被权利要求覆盖，围绕亲本做序列工程**逃不出 epitope claim**。
> 只有换 epitope 才行，而那是抗体发现任务，不是工程任务。

---

## 4. 核心机制一：ADC carrier phenotype 数据模型

这是 v0.3.0 最重要的新增，文件在 `lib/phenotype.py`。

### 4.1 为什么 `internalization: true` 几乎没有工程价值

一个布尔字段把**五件物理上不同的事**压成了一个词，而 ADC 只要其中任何一件缺失就会失败：

```text
step 1  surface_departure      抗体离开细胞表面
step 2  endosomal_entry        进入 early endosome
step 3  lysosomal_delivery     到达 lysosome（而不是被 recycle 回去）
step 4  linker_processing      linker 被加工，释放活性代谢物
step 5  cytotoxic_sufficiency  释放量足以杀死目标细胞，且依赖靶点表达
```

抗体可以**通过 step 1 而在 step 3 失败**（recycling 占主导）；也可以**通过 step 3 而在
step 4 失败**（linker 选错）。合并成一个 criterion，这些失败就全部不可见了。

所以 v0.3.0 把它们保留为五个独立 criterion，各自记录哪些观测支持它。

每个 step 还记录 `failure_meaning`——它失败意味着什么，而不只是"未满足"。

### 4.2 强制元数据：区分"数据"与"断言"

15 种测量类型，每条观测**必须**携带 8 个元数据字段：

```yaml
adc_carrier_observations:
  - measurement: acid_wash_internalized_fraction
    cell_line: SN12C
    endogenous_or_engineered: endogenous     # 内源表达还是转染子
    target_density: {value: 45000, unit: receptors_per_cell, method: QIFIKIT}
    timepoint: {value: 4, unit: h}
    concentration: {value: 10, unit: ug/mL}
    assay_method: acid wash + flow cytometry
    biological_replicates: 3
    uncertainty: {type: sd, value: 0.05}
    normalized_value: 0.42
    normalization_basis: surface_binding_4c   # 部分测量必需
    construct: PDL192-IgG1
```

**缺任何一个 → 该观测标记 `unusable`，不能支持任何 cascade step。**

不是部分接受、不是打折采信——因为一个不知道细胞系、时间点、浓度的测量值，**无法与任何
其他测量值比较**，它不构成证据。

三条额外的强制规则：

**规则一：分数必须有分母。**
`acid_wash_internalized_fraction`、`per_cell_accumulation`、`lysosomal_delivery_fraction`
必须声明 `normalization_basis`。理由（也是这一层的关键判据）：

> 关键问题从来不是"看到了一些 puncta"，而是
> **单位表面结合抗体中，有多少比例在合理时间内进入了 lysosome。**

没有声明分母的"fraction"不是 fraction。

**规则二：至少两个生物学重复。** `biological_replicates < 2` 直接不可用。

**规则三：杀伤必须有 antigen-negative counter-screen。**
`payload_dependent_killing` 若没有配套的 `antigen_negative_counter_screen`，
**不能**支持 `cytotoxic_sufficiency`，会被记录到 `blocked_observations` 并说明原因。
因为要主张的是"抗原依赖的杀伤"，单看杀伤不能建立依赖性。

### 4.3 级联是有序的

后面的 step 不能在前面 step 无数据时被采信——测量对象根本不存在。所以每个被前置步骤
阻塞的 step 会带 `gated_by` 字段。

### 4.4 `null` 表示"未测"，不表示"差"

这是全模块最关键的一条语义约定。

`carrier_quality()` 在没有可用观测时返回：

```yaml
adc_carrier_quality_score: null
basis: no_usable_observations
interpretation: >-
  没有任何带完整元数据的观测，所以 carrier 能力是"未测"。
  这不是低分：在递送级联被测量之前，该候选根本无法放到 carrier 轴上。
```

如果这里返回 0，缺失的数据就会在排序中变成一个负面结论——把"没测"伪装成"不行"。

有数据时，分数 = 已支持 step 的加权比例 / 有数据的 step 权重之和，并同时输出
`coverage`。权重：

| step | 权重 | 理由 |
|---|---|---|
`surface_departure` | 0.10 | 必要但门槛低 |
`endosomal_entry` | 0.20 | |
`lysosomal_delivery` | 0.35 | **最高**：载荷释放发生地，也是 recycling 与降解的分水岭 |
`linker_processing` | 0.15 | |
`cytotoxic_sufficiency` | 0.20 | |

`conflicting` 状态按半权计入。**读分数必须同时读 coverage**：低覆盖下的高分没有意义。

### 4.5 模态决策：继续 / 停止规则

7 条继续条件（须全部满足）与 8 条停止条件（任一成立即停）被编码成规则，逐条映射到级联
证据而不是主观判断。三种结论：

| decision | 触发 | 含义 |
|---|---|---|
`stop_this_route` | 任一停止条件成立 | **停这条路线不等于停这个靶点**，可能意味着要换 epitope 或换模态 |
`proceed_to_antibody_optimization` | 全部继续条件满足 | 序列优化才有正当性 |
`modality_unproven_run_kill_experiment` | 其余情况 | 先做 kill experiment，再谈优化 |

需要跨构造比较（parent IgG1 vs Fc-silent vs Fab）的条件，在单构造数据下会被明确报为
**不可评估**，而不是默认未满足。

---

## 5. 核心机制二：因果失效树与信息增益

文件在 `lib/failure_modes.py`。

### 5.1 为什么 checklist 不够

v0.2.0 的 12 条三态矩阵适合**证据记账**，但不支持工程决策。它回答的是"还剩几个 gap"，
而这不能告诉你下一步做什么——因为 gap 的信息量不相等，而且一个实验可以同时关掉好几个。

### 5.2 两棵因果树，15 个失效模式

```text
adc_activity_absent（8 个）
├── target_density_insufficient        ← 路线终止级
├── antibody_binding_insufficient
├── surface_retention                  ← 路线终止级
├── recycling_dominates_degradation    ← 路线终止级
├── lysosomal_delivery_insufficient    ← 路线终止级
├── linker_not_processed
├── payload_resistance
└── bystander_context_mismatch

adc_toxicity（7 个）
├── receptor_agonism                   ← 路线终止级
├── fcgr_dependent_crosslinking
├── normal_tissue_target_expression    ← 路线终止级
├── circulating_target_sink
├── linker_instability
├── payload_nonspecific_toxicity
└── conjugate_aggregation_rapid_clearance
```

6 个标记为 `route_terminating`（路线终止级）——含义是**不可被别处的优秀表现补偿**。

每个模式三态：`excluded`（被排除）/ `supported`（有证据支持它成立）/ `unresolved`（未定），
并记录 `basis`（凭什么这么判定）。

有一条保护规则：**已被支持的失效模式不会被更弱的证据降级为 excluded。**

### 5.3 11 个实验，各自声明能判别什么

每个实验声明 `excludes`（干净结果可排除哪些模式）与 `supports`（阳性结果支持哪些模式）。
**只列它真正能判别的模式**——一个无论该模式成立与否都给出相同结果的实验，对该模式的
信息增益是零，不管它多贵。

### 5.4 信息增益：两次关键修正

朴素做法是"数它能判别多少个未定模式"。这个做法在实跑中给出了**科学上错误的顺序**，
必须修正两处：

**修正一：overturn credit（推翻信用）。**

朴素计数把"已被支持"的模式当作已定论，不给分。这是反的：**一个被支持的路线终止级模式，
恰恰是最该去测的东西**——尤其当支持它的证据很弱时。

enavatuzumab 的实例：`surface_retention` 被 Purcell 2014 的一句"data not shown"支持。
朴素计数下，直接测内化的实验对这条得 0 分。但它显然是最该做的实验。

所以：能**排除**一个当前被支持的模式 → 给最高权重。

| 情形 | 权重 |
|---|---|
排除一个被支持的**路线终止级**模式 | **4** |
排除一个被支持的其他模式 | 2 |
判别一个未定的**路线终止级**模式 | 2 |
判别一个未定的其他模式 | 1 |

**修正二：prerequisite gating（前置条件门控）。**

递送级联是有序的，所以在 step 1 尚未建立时，step 3 的测量**无法解释**——一个"溶酶体
递送分数"没有表面结合分母和内化基线就没有意义。

所以实验可以声明 `prerequisite_steps`，前置未满足的实验被标 `ready_to_run: false`，
排序时**无论原始增益多高都排在就绪实验之后**。

修正前后对比（enavatuzumab）：

| | 修正前 | 修正后 |
|---|---|---|
第一名 | `lysosomal_flux_quantification`（gain 4） | `modality_kill_internalization_panel`（gain 7） |
问题 | 在不知道是否内化时先测溶酶体分数 | 先测内化，且直接挑战 `surface_retention` |

修正后的顺序与优化指南的 Phase 0 完全一致。

---

## 6. 核心机制三：二维 Pareto 选择

文件在 `lib/pareto.py`。

### 6.1 支配关系

候选 A 支配 B，当且仅当 A 在**两个轴上都不差**，且**至少一个轴上更好**。非支配集即前沿。

权衡对（一个序列好、一个递送好）**都留在前沿**——这正是要保留的信息，加权求和会把它抹掉。

### 6.2 缺失轴 = 不可比，不是 0

某轴为 `None` 的候选被放进 `incomparable`，**不是**置 0 参与排序。

### 6.3 无 carrier 数据时拒绝选 lead

三种状态：

| status | 含义 |
|---|---|
`carrier_axis_unmeasured` | **没有二维前沿。** 明确说明：不能仅凭序列描述符为 ADC 用途排名；Track A 的排序只是"决定先造什么"的轨内预筛，不是 lead ranking |
`carrier_axis_partially_measured` | 前沿只覆盖有测量的那些；其余是**不可比**而非更差 |
`both_axes_measured` | 正常前沿 |

并且 Pareto 只识别"没有在两个轴上同时被打败"的候选，**它不在这些候选之间做选择**——
那需要一个"愿意用多少 binder quality 换递送能力"的项目决策，本模块不做这个决策。

### 6.4 carrier 分数不可继承

10 阶段有一条硬规则：

> **carrier 能力永远不由变体从亲本继承。**
> 每个构造的递送行为必须在该构造上实测：一个 CDR 取代就可能在不改变任何序列描述符的
> 情况下摧毁内化。

所以即使亲本测过，28 条序列变体在 carrier 轴上依然全部是 `incomparable`。

---

## 7. 核心机制四：七个候选家族

### 7.1 三个序列家族（v0.2.0 已有，可直接下单合成）

| 家族 | 定位 |
|---|---|
`conservative_liability_removal` | 只改 FR 区 liability，功能风险最低 |
`developability_optimized` | 任何位置含 CDR，收益最大风险最高 |
`germline_reverted` | FR 回复人源 germline，针对 humanness |

这三个都属于**分子质量优化**家族。

### 7.2 四个新家族：构造规格 / 战役规格

ADC 场景至少还需要四类，但它们**不是点突变**，所以不能作为序列发出：

| 家族 | `entry_kind` | 内容 | 为什么不能给序列 |
|---|---|---|---|
`function_silenced` | `construct_specification` | P0 parent IgG1 / P1 Fc-silent / P2 Fab / P3 F(ab')2 | 功能沉默在 **Fc**，输入未提供恒定区 |
`valency_clustering` | `construct_specification` | 单价 Fab / 二价 IgG / 二价 Fc-silent / 受控多价对照 | 价态是格式改变，同上 |
`kinetic_ladder` | `campaign_specification` | 亲本样 / 适度减弱 3-10× / 适度增强 3-10× | **预测亲和力改变的方向与幅度需要抗原复合物结构或训练过的模型，本模块都没有** |
`conjugation_format` | 产品实体 | 随机 Lys / 还原链间 Cys / 位点特异 / 不同 DAR | 属于 ADC 产品实体，见第 8 节 |

**把两类家族显式分开是刻意的设计。** 湿实验人员必须一眼看出：哪些能当基因下单，
哪些需要一个筛选战役。发明 Fc 序列或亲和力变体序列就是**编造**。

### 7.3 function_silenced 家族的关键警告

```text
Fc 沉默可以去除 FcγR 依赖的激动，但不保证去除
二价 Fv 自身受体聚簇引发的激动。
signaling 必须在每个构造上实测，不能从格式推断。
```

这个家族的目的**不是**最终一定用这些格式，而是把毒性来源解耦：

```text
单纯抗原结合 / 二价受体聚簇 / FcγR 二次交联 / Fc effector function / payload
```

必须同步测量的 7 项写在 `must_measure_together` 字段里（canonical NF-κB、
alternative NF-κB、cytokine release、receptor clustering、内化、溶酶体转运、
偶联物细胞毒）。

### 7.4 kinetic_ladder 的警告

```text
不要默认"亲和力越高越好"。
对 carrier 而言，亲和力要与肿瘤穿透、受体 recycling、antigen sink 权衡。
载荷递送的最优亲和力不一定是结合的最优亲和力。
```

### 7.5 04 阶段的 paratope-first 警告

pipeline 输出 17 条需要结合确认的 CDR 提议，但报告里明确写：

> **不要直接合成所有 CDR liability 修复。** 先做 paratope 图谱（alanine 或低复杂度
> substitution scan、display 筛选、亲本竞争结合），并**并行测量 signaling 与内化**，
> 把位点分成三类：binding-critical / signaling-biasing / engineering-tolerant。
>
> 一个"保留结合与内化、但降低 agonism"的 CDR 变体，比任何 liability burden 的下降
> 都更有价值。

---

## 8. 核心机制五：ADC 产品实体模型

文件在 `lib/product.py`。

### 8.1 三个实体

```text
AntibodyCandidate（Fv + 格式 + Fc 规格）
  × ConjugationVariant（位点化学 + DAR）
  → ADCProductCandidate
```

v0.2.0 只建模一个实体（Fv），并正确地拒绝从它推断 DAR。拒绝是对的，但不够：
**项目实际决策的对象是产品**，而一个抗体对应多个产品。

```text
Fv-A + Fc-silent   + 工程化 Cys 位点 + linker-Y + payload-Z + DAR2
Fv-A + Fc-silent   + 工程化 Cys 位点 + linker-Y + payload-Z + DAR4
Fv-A + 野生型 Fc   + 随机 Lys        + linker-Y + payload-Z + DAR~3.5
```

这三者在疏水性、聚集、电荷异质性、结合保留、血浆稳定性、清除上行为不同。把裸 Fv 的
排名直接搬到产品上，等于**假设 payload 是惰性的**——而这恰好与事实相反。

### 8.2 4 种偶联化学 × 10 个产品属性

10 个属性各自声明 `depends_on` 与解决途径，状态只有三种：

| 状态 | 含义 |
|---|---|
`requires_input` | 需要补输入（如 Fc 序列） |
`requires_experiment` | 需要实验（给出具体 assay） |
`flagged_by_computation` | **本模块真的算出了一个发现** |

**没有任何属性被估算。** 偶联物行为由 payload 理化性质与恒定区上下文主导，二者都无法
从 Fv 推断。

### 8.3 Fv-only 输入唯一真正支撑的偶联结论

CDR 内溶剂可及的赖氨酸。enavatuzumab 上找到 **`H59`**，于是：

- `paratope_conjugation_risk: present`
- `recommended_variant: site_specific_engineered_cysteine`
- 理由：CDR 可及赖氨酸让随机 Lys 偶联成为 paratope 风险，首个偶联物应优先用位点可控化学

这是一个真实、可行动、且完全由计算支撑的发现。

---

## 9. 为什么不先接 ProteinMPNN

v0.2.0 把"没有接学习模型"列为主要遗留项。这个判断**只对了一半**。

当前最大的瓶颈**不是** proposal generator 不够聪明，而是**目标函数缺失**。

ProteinMPNN、Rosetta 或任何 sequence designer 都能生成更多合理序列。但如果不知道应该
优化：

- 非激动
- 高内化
- 高 lysosomal flux
- 低正常组织摄取
- 偶联后稳定性

那么模型只会**更高效地优化错误的目标**。

正确顺序（写在 `12_active_learning` 的 `sequencing_for_model_readiness` 字段里）：

```text
1. 先建立 ADC phenotype assay schema      ← v0.3.0 已完成（07 阶段）
2. 收集亲本与小规模 rational 构造面板的真实数据
3. 建立 variant–phenotype 数据集（强制元数据）
4. 再接结构模型或学习模型
5. 用 active learning 选下一批变体
```

所以 `12_active_learning` 当前不拟合模型是**正确的**。v0.3.0 的目标不是让它开始拟合，
而是让它先成为一个**严格的数据闭环**：变体进、表型出、元数据强制。

一句写进代码的话：**只用序列描述符训练出来的模型，只会预测序列描述符。**

---

## 10. 分数与禁止声明

| 分数 | 状态 | 说明 |
|---|---|---|
`sequence_computational_developability_score` | 输出 | Track A；仅本次运行内可比；`promotion_eligible: false` |
`adc_carrier_quality_score` | 有数据才输出 | Track B；无数据时 `null` = **未测**，不是差；**不可继承** |
`adc_readiness_score` | **永不输出** | 需要每条 gating 准则的版本化实验证据，属 Gate 系统职责 |
`dar_estimate` | **永不输出** | 不可从可变区推断 |
`combined_binder_and_carrier_score` | **永不输出** | 相加会让干净序列补偿不递送的分子 |

### 重命名

```text
developability_score  →  sequence_computational_developability_score
developability_rank   →  sequence_computational_developability_rank
```

长名字是刻意的：v0.2.0 的短名字诱导读者把榜首行当成"总体最优候选"，而它只是**轨内序列
预筛**。

### 禁止声明（新增 3 条）

除 v0.2.0 的 6 条外，新增：

- carrier capability from sequence alone（仅凭序列声明 carrier 能力）
- internalisation as a single boolean criterion（把内化当成单一布尔判据）
- inheritance of a parent's phenotype measurement by a variant（变体继承亲本表型测量）

---

## 11. 从 v0.2.0 迁移

Stage 编号变了。映射表在 `stages.py` 的 `STAGE_MIGRATION_FROM_0_2_0`：

| v0.2.0 | v0.3.0 |
|---|---|
`04_ai_guided_engineering` | `04_binder_engineering_design` |
`06_computational_triage` | `06_binder_quality_triage` |
`07_experimental_design` | `11_experimental_design` |
`08_active_learning` | `12_active_learning` |
`09_adc_readiness` | `09_adc_failure_mode_analysis` |
`10_patent_package` | `13_patent_package` |
`11_asset_report` | `14_asset_report` |

其余 01/02/03/05 编号不变。

**输入向后兼容**：0.1.0 的标量证据值、0.2.0 的证据映射都仍然接受。新增可选字段
`adc_carrier_observations` 与 `payload`。

`04_ai_guided_engineering` 更名为 `binder_engineering_design` 是诚实性修正：这个 stage
是规则驱动的，叫 "AI-guided" 是误导。

---

## 12. 已知局限

1. **Track B 需要数据才有用。** 没有观测时它只能给出"去测"这个结论——这是正确的，但
   意味着 v0.3.0 的价值一半在于它**拒绝**做的事。
2. **失效树是穷举建模的模式，不是所有可能的失效。** 被 `excluded` 的模式，只在其
   `basis` 所引用证据的强度范围内被排除。
3. **信息增益不是成本收益比。** 它不考虑 assay 难度、周期与费用，只输出 `cost_tier`
   供人工权衡。
4. **设计提议仍是规则驱动。** 这是刻意的（第 9 节），不是遗漏。
5. **SASA 仍来自孤立 Fv 的单一构象**，framework 可及性是上界；且结构预测有运行间波动，
   暴露度衍生数值应视为有噪声。
6. **产品属性全部需要补输入或补实验**，模块只输出矩阵与要求，不估值。
7. **构造规格无法表达为序列**，除非补齐恒定区。
8. **kinetic ladder 没有序列**，需要筛选战役。
9. 输入输出机器契约已发布在模块的 `contracts/` 下；任何缺少契约校验回执或
   artifact checksum 的旧 run 都必须默认拒绝，不能作为稳定 fixture。
10. **没有随附"有数据"的示例。** 刻意如此：附一份虚构的 enavatuzumab 表型数据集，
    有被误当真实数据的风险。有数据的正向路径由测试覆盖（用明显合成的数值）。

---

## 13. 使用方法

```bash
cd "/path/to/StelligenOS"

.venv/bin/python genmodules/antibody_binder_asset_engineering/run_pipeline.py list-steps
.venv/bin/python genmodules/antibody_binder_asset_engineering/run_pipeline.py doctor

run_root="/external/workspace/runs/antibody-binder"
.venv/bin/python genmodules/antibody_binder_asset_engineering/run_pipeline.py run \
  --binder /external/workspace/input/binder.yaml \
  --output-root "${run_root}" \
  --mode execute \
  --allow-external
```

参数与 v0.2.0 相同。仍然**强烈建议加 `--allow-external`**：不加则暴露度未知，会提议
CDR 取代去修结构上并不暴露的 liability。ABodyBuilder2 权重已缓存，整条 pipeline 约 13 秒。

### 输出结构

```text
<output-root>/<asset_id>/<run_id>/
├── run_manifest.yaml
├── normalized_input.yaml
├── software_status.yaml
├── 01_binder_intake/result.yaml
├── 03_structural_analysis/{result.yaml, fv_model.pdb}
├── 07_adc_carrier_phenotype/result.yaml    ← Track B 核心
├── 09_adc_failure_mode_analysis/result.yaml
├── 10_pareto_selection/result.yaml
├── ...
└── asset_report.md                          ← 以模态决策开头
```

### 测试

```bash
.venv/bin/python -m pytest genmodules/antibody_binder_asset_engineering/tests/ -q
# 63 passed
```

---

## 14. enavatuzumab 结果解读

### 14.1 Track B：没有一条可用观测

`adc_carrier_observations: []`——**这是发现，不是遗漏。**

enavatuzumab 所有可得的 trafficking 表述，要么是文本摘要，要么是未展示数据，没有一条
携带 carrier 观测所需的元数据。在 0.3.0 schema 下，这样的表述**不是可用观测**。

结果链条完全自洽：

```text
usable observations = 0
→ 五步级联全部 no_data，step 1 起即未解决
→ adc_carrier_quality_score = null（未测，非差）
→ 没有二维 Pareto 前沿（28 条候选全部 incomparable）
→ modality decision = modality_unproven_run_kill_experiment
→ 继续条件满足 0 / 7
```

那条唯一相关的文献表述被记录在 `known_evidence.internalization`，
`direction: absent_with_negative_indication`，在失效树里正确地把
`surface_retention` 标为 supported——**而没有被升格为它并不是的"测量"**。

### 14.2 失效树位置

15 个模式中：**3 supported、2 excluded、10 unresolved**。

三个被支持的都是**路线终止级**：

| 模式 | 依据 |
|---|---|
`surface_retention` | Purcell 2014「抗体结合后 TweakR 维持在细胞表面」（data not shown） |
`receptor_agonism` | Lam 2018 I 期肝胰毒性，归因于经受体的激动信号 |
`normal_tissue_target_expression` | Choi 2017 肾 Bowman 囊、胰腺、炎症肝胆管 |

两个被排除：`target_density_insufficient`（Culp 2010 / Purcell 2014 表达数据）、
`antibody_binding_insufficient`（KD 5.5 nM）。

### 14.3 最高信息增益实验

```text
第 1 名  内化面板（跨构造 + 跨靶点密度分层）      gain 7  READY
         可推翻：surface_retention（当前的阻塞发现）
         另可判别：fcgr_dependent_crosslinking、recycling_dominates_degradation

第 2 名  跨构造 signaling / cytokine 比较        gain 5  READY
         可推翻：receptor_agonism

第 3 名  正常细胞摄取与毒性面板                   gain 4  READY
         可推翻：normal_tissue_target_expression

被前置条件阻塞：
  lysosomal_flux_quantification        需要 endosomal_entry
  proof_of_modality_adc_cytotoxicity   需要 lysosomal_delivery
  target_heterogeneity_and_bystander   需要 cytotoxic_sufficiency
```

11 阶段还把序列优化实验放进 `deferred_until_modality_resolved`：

> 表达/SEC、forced degradation、变体 SPR——**在模态决策解决之前不要跑**。

### 14.4 Track A（仍然有效，只是不是当前约束）

- framework 一致度 VH 92.5% / VL 93.7%（合并 93.08%）
- 16 条 liability flag，暴露度加权后 burden 44.0 → 28.16，11 条降级
- 42 条提议，17 条需结合确认，1 条 dual-benefit（`VL-M37L`）
- 28 条序列候选（3 家族）+ 11 条构造/战役规格（3 家族）

### 14.5 ADC 产品矩阵

- 枚举 **48** 个产品候选（12 个 carrier 候选 × 4 种偶联化学）
- **0 个当前可造**——缺恒定区序列，也未声明 linker/payload
- 唯一计算结论：`H59` 是 CDR 内溶剂可及赖氨酸 → 推荐首选
  `site_specific_engineered_cysteine`

### 14.6 结论

这与优化指南的判断一致：**不应把 enavatuzumab 直接优化成 ADC。**

它更适合被定位成：

> 一个临床验证过的 TWEAKR-binding scaffold、epitope-defined reference antibody
> 和 toxicity reference，而不是默认的 ADC lead。

正确路线是先用它快速完成 TWEAKR ADC 的 **modality proof**；若结果成立，再以
"非激动、强内化、不同 epitope、位点特异性偶联"的新抗体作为真正的 IP 资产。

v0.3.0 的输出现在**自己就会这么说**——而不是给出一个计算榜首然后让人误以为那是 lead。

---

## 15. 核心机制六：region 并集、结构锚定位点、三条风险轴

v0.3.1 新增。这一节讲的四个机制不是新能力，而是**修正 v0.3.0 的错判**。它们全部由
TPP-2658 的实跑逼出来：0.3.0 把一个位于亲和力成熟 CDR-H2 正中间的突变，标成了
"框架区、低风险、不需要测亲和力"。

### 15.1 为什么 region 必须取 IMGT 和 Kabat 的并集

`region` 决定 `functional_consequence`（liability 有多要紧）和
`RISK_TIER_BY_REGION`（改掉它有多危险）。所以 region 判错，两条风险同时判错。

问题在于 IMGT 和 Kabat 划界方式不同，而且**分歧不小**。以 TPP-2658 为例，逐残基核对
的结果是 VH 18 个位点、VL 9 个位点判定不一致：

| 线性位置 | 残基 | IMGT | Kabat |
|---|---|---|---|
| VH 34 | M | FR2 | **CDR1** |
| VH 35 | I | FR2 | **CDR1** |
| VH 50 | Y | FR2 | **CDR2** |
| VH 59-66 | HYADSVKG | FR3 | **CDR2** |
| VL 33-34 | LN | FR2 | **CDR1** |
| VL 53-56 | SLQS | FR3 | **CDR2** |

两套定义**不是互相竞争的真理**：IMGT 的边界是结构性的，Kabat 的边界是变异度推出来的。
一个被其中一套漏掉的抗原结合位点残基，**照样在结合抗原**。所以：

> 只要 IMGT 或 Kabat 有**任何一套**判它是 CDR，风险上就当 CDR 处理。

实现是 `numbering._union_map`，按线性位置合并，并**断言残基一致**——两套图如果在某个
位置对不上（残基不同），就退回纯 IMGT，绝不混用。输出里 `imgt_region`、
`kabat_region`、`region_definitions_agree` 三个字段都保留，所以争议位点是显式可查的，
不是被悄悄裁决掉的。

**一个关键的边界**：框架同一性（humanness）**仍然只用 IMGT 框架**计算。因为
humanness 数字要能和文献比较，而文献用 IMGT。**并集只管风险，不管同一性。**

对 TPP-2658 的实际后果：`VH-D62E` 从「FR3 / low / 不需结合确认」变成
「CDR2 / high / 需要结合确认」，并被逐出保守家族。D62 就在专利自己写的 CDR-H2
共识式 `YISPSGGSTHYADSVKG` 里面。

### 15.2 结构锚定位点：报告，但不提议

IMGT 定义了 5 个 V 结构域的**不变地标**：

| IMGT 位置 | 身份 |
|---|---|
| 23 | 1st-CYS，链内二硫键 |
| 41 | 核心保守色氨酸 |
| 89 | 内层 β 片的疏水支点 |
| 104 | 2nd-CYS，链内二硫键 |
| 118 | J 区 TRP/PHE，把 FR4 锚在核心上 |

液相 liability 扫描会把 41 和 118 的色氨酸标成易氧化——**这是对的，应该报**。但在这些
位置**提议突变**是另一回事：那不是 developability 修法，那是改折叠。

v0.3.0 提议了 `VH-W36F/Y`（H41）、`VH-W110F/Y`（H118）、`VL-W35F/Y`（L41），全标
`low`，其中 `VH-W110F` 还进了第 2 名组合候选。

**这里的设计选择需要说明。** 模块的一般哲学是"CDR 提议照样发出，逐条加标记，不做
静默抑制"。锚定位点是**例外**，因为：

> 其他提议都是审阅者**可以合理选择**的权衡；锚定位点不是——它是整个免疫球蛋白折叠层面
> 的不变量，不只是这个谱系里保守。

所以做法是**拒绝，但写进 `rejected_proposals`**，附锚定位点名称和处置建议（用配方、
顶空、避光控制氧化，而不是改序列）。保留记录，是为了让"这个 liability 被看见了、
并且被明确拒绝了"可审计——这比静默丢掉好得多。

### 15.3 埋藏：两条轴是反向的

v0.3.0 的 `_exposure_factor` 对埋藏残基**下调**化学风险，这没错：溶剂、过氧化物、光
都更难接触埋藏侧链，所以化学反应更慢，**紧迫性确实下降**。

问题是它到此为止了。于是埋在核心里的突变浮出来成了"最便宜的修法"。

真相是两条轴**反向移动**：

```
埋藏 ↓ 化学紧迫性     （溶剂接触少 → 反应慢）
埋藏 ↑ 补救代价       （侧链和邻居堆叠 → 改它就是改核心堆积）
```

> **埋藏型 liability 是最不紧迫、同时最贵的那一类。** 不是最安全的。

实现：`REMEDIATION_COST_BY_EXPOSURE` 给 `remediation_risk` 加埋藏罚分；
`FOLD_RISK_ESCALATION` 按档提升 `engineering_risk`。

### 15.4 三条风险轴分开，因为它们由不同实验回答

这是 15.3 里最容易做错的地方：埋藏提升的**不是** `requires_binding_confirmation`。

| 标记 | 含义 | 由什么实验回答 |
|---|---|---|
| `requires_binding_confirmation` | IMGT 或 Kabat 判为 CDR | 重测亲和力 |
| `requires_fold_confirmation` | 侧链埋藏或部分埋藏 | 表达量、热稳定性 |
| `reduces_framework_humanness` | 被去掉的残基就是胚系残基 | 无——这是已知代价 |

一条提议可以同时带三个。分开的理由很实际：把埋藏问题标成"需要测亲和力"，会让人去做
一个**回答不了这个问题**的实验。

### 15.5 胚系编码的 liability：三态，且默认不该动

这一条是 TPP-2658 里最有价值的发现，而且是被一个反常现象揪出来的：三个 FR3 脱酰胺
修法构成了整个"最安全"家族，但打分把它们**全排在未修改的母本之下**。

原因：N82、N85、N92（IMGT）**就是 IGHV3-23 的胚系残基**。

> 一个 liability 如果它的残基**就是**最近人类胚系残基，那么它是**人类胚系自己编码的**，
> 和所有建在这个 V 基因上的抗体共享。它在已获批药物里的普遍存在，本身就是"这个风险在
> 实践中可被容忍"的证据。去掉它，是拿框架同一性去换一个人类抗体库本来就带着的风险。

打分其实算对了（humanness 0.20 对 burden 0.35），但输出里**没有一句话说明原因**，所以
那个排名看起来像 bug 而不是发现。现在：

- 每条 hit 带 `germline_encoded`（三态）
- 每条提议带 `reduces_framework_humanness`，并把代价写进 rationale 文本
- 摘要拆成 `germline_encoded_hits` / `somatic_hits` /
  `germline_comparison_unavailable_hits`

**为什么必须是三态而不是布尔值。** `null` 表示该位点**落在 V 基因框架比对之外**——
CDR3 是接合区（V-D-J 拼接产生），FR4 来自 J 基因。把这些报成 `false`（"体细胞的"）
就是把"没比较过"说成了"比较过且不是胚系"。这沿用模块既有的核心原则：

> **缺数据不等于负结果。**（同一原则也用在 `adc_carrier_quality_score = null` 上。）

TPP-2658 的结果：**11 个胚系编码、0 个体细胞、2 个不可比较**。也就是说，
**可工程化的集合就是 somatic 那一子集，而它是空的**——唯一真正值得动的位点落在那
2 个"不可比较"里（CDR3 的 D101）。

### 15.6 为什么打分表达不了这些，标记必须并列显示

Track A 给 liability burden 0.35 的权重。后果是：**一个打包多个突变的组合候选，几乎
不管打包了什么都会排得靠前**。`DEV-C01` 修完之后仍然排第 2（0.66），而它同时带着
一个 paratope 改动、三个降低 humanness 的改动、一个埋藏改动。

**修法不是重新调权重。** Track A 本来就是计算描述符之间的比较，
`promotion_eligible: false`，"排名不等于推荐"是它写在契约里的性质。修法是**把标记放进
同一张表**：

```
rank candidate             score    risk    bind  fold  human muts
1    TPP-2658-DEV-S01      0.6794   high    yes   no    no    D101E
2    TPP-2658-DEV-C01      0.66     high    yes   yes   yes   D101E,D62E,N74Q,N77Q,N84Q,M4F
3    TPP-2658-DEV-S02      0.599    high    yes   no    yes   D62E
4    TPP-2658-PARENT       0.4      -       no    no    no    （母本）
5    TPP-2658-CONS-S01     0.3836   low     no    no    yes   N74Q
```

报告里同时印一句：**后四列不计入分数，先读标记再读排名。**

这张表现在自己就把结论讲清楚了：第 1 名是唯一"高价值 + 无 humanness 代价 + 无折叠
风险"的候选，只需要一个结合确认；第 2 名三个标记全亮。
