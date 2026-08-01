# 工作日志 — antibody_binder_asset_engineering（中文版）

模块级日志。**只追加**：需要修正时新增条目，不改写既有条目。

英文版：`WORKLOG.md`。原理与架构说明：`GUIDE.zh-CN.md`。
v0.2.0 的日志与说明保留在 `genmodules/archive/antibody_binder_asset_engineering/v0.2.0/`。

---

## 2026-07-30（第二次）— v0.2.0 → v0.3.0，双轨表型化改造

**目的。** 依据 `Zhixins-KB/antibody_binder_asset_engineering v0.2.0优化指南.md` 的判断，
把模块从 "sequence-centric developability optimization" 升级为
"phenotype-conditioned ADC carrier engineering"，并归档 v0.2.0。

**触发这次升级的核心论断**（来自优化指南，我认同）：

> v0.2.0 主要在优化"一个更干净、更人源化、更可开发的抗体"，
> 还没有真正优化"一个能够安全、有效递送载荷的 ADC 抗体"。

对普通 therapeutic antibody，v0.2.0 已接近合格；对 ADC asset engineering，缺少最关键的
**表型驱动层**。

---

### 1. 归档

v0.2.0 完整树复制到 `genmodules/archive/antibody_binder_asset_engineering/v0.2.0/`，
附 `FROZEN.md` 说明冻结原因、被取代的理由、以及保留下来的已验证行为（40 测试、两次
enavatuzumab 运行、永不输出 readiness 分数、adverse/gap 三态区分）。

同时给 `genmodules/scripts/update_readme.py` 加了 `SKIP_DIRS = {"scripts", "archive"}`。
原因：归档树里有完整的 `module.yaml`，生成器按目录扫描时**有可能把它当成活跃模块发现**。
虽然当前嵌套层级恰好躲过了，但这属于"现在不坏、以后会坏"，所以显式排除，并写了回归测试。

（写这段代码时我先误用了 JavaScript 风格的 `//` 注释写进 Python 文件，随即修正为 `#`。）

---

### 2. v0.3.0 的六项结构性改动

#### 2.1 拆成两条正交轨道

```text
Track A  Binder molecule quality（计算）→ sequence_computational_developability_rank
Track B  ADC carrier phenotype（实测）→ adc_carrier_quality_score
```

**两轨只在 Pareto 前沿相遇，绝不相加。** 理由写进了 `module.yaml` 的 `withheld_scores`：
加权求和允许"一个干净的序列"补偿"一个不内化的分子"，这是载荷递送项目唯一不能做的交换。
所以 `combined_binder_and_carrier_score` 被列为**永不输出**。

#### 2.2 新增 `lib/phenotype.py`：五步递送级联

把单一 `internalization` 判据拆成 5 个物理上不同的 criterion：
`surface_departure` → `endosomal_entry` → `lysosomal_delivery` → `linker_processing`
→ `cytotoxic_sufficiency`。

抗体可以通过 step 1 而在 step 3 失败（recycling 占主导），也可以通过 step 3 而在 step 4
失败（linker 选错）。合并成一个判据，这些失败模式全部不可见。

15 种测量类型，8 个强制元数据字段。三条硬性规则：

- **缺任何元数据 → 观测 `unusable`**，不能支持任何 step。不是部分采信——一个不知道细胞系、
  时间点、浓度的测量值无法与任何其他值比较。
- **分数必须有分母**：`*_fraction` 类测量必须声明 `normalization_basis`。关键判据不是
  "看到 puncta"，而是"单位表面结合抗体中有多少比例在合理时间内进入 lysosome"。
- **杀伤必须有 antigen-negative counter-screen**，否则不能支持 `cytotoxic_sufficiency`。
  要主张的是抗原依赖的杀伤，单看杀伤不能建立依赖性。

以及最关键的语义约定：**`adc_carrier_quality_score = null` 表示"未测"，不表示"差"。**
若返回 0，缺失的数据会在排序里变成负面结论。

另外把优化指南第六节的继续/停止判据编码成 7 条 continue + 8 条 stop 规则，输出三种
`decision`。需要跨构造比较的条件在单构造数据下明确报"不可评估"，而不是默认未满足。

#### 2.3 新增 `lib/failure_modes.py`：因果失效树替代 checklist

两棵树、15 个失效模式（efficacy 8 + toxicity 7），其中 6 个标为 `route_terminating`
（不可被别处优秀表现补偿）。11 个实验各自声明能 `excludes` / `supports` 哪些模式——
只列真正能判别的，因为一个无论模式成立与否都给相同结果的实验信息增益为零。

输出**按信息增益排序的下一步实验**，而不是"还剩几个 gap"。

#### 2.4 新增 `lib/pareto.py`：二维前沿

支配关系 + 缺失轴归入 `incomparable`（不置 0）。无 carrier 数据时状态为
`carrier_axis_unmeasured`，**明确拒绝命名 lead**，并说明 Track A 排序只是轨内预筛。

另有一条硬规则写在 10 阶段：**carrier 能力永远不由变体从亲本继承**——一个 CDR 取代就
可能在不改变任何序列描述符的情况下摧毁内化。

#### 2.5 新增四个候选家族，且与序列家族显式分离

| 家族 | `entry_kind` | 为什么不能给序列 |
|---|---|---|
`function_silenced` | `construct_specification` | 功能沉默在 Fc，输入未提供恒定区 |
`valency_clustering` | `construct_specification` | 价态是格式改变，同上 |
`kinetic_ladder` | `campaign_specification` | 预测亲和力改变的方向与幅度需要抗原复合物结构或训练过的模型，本模块都没有 |
`conjugation_format` | 产品实体 | 归 `lib/product.py` |

**发明 Fc 序列或亲和力变体序列就是编造**，所以这四类作为"规格"发出。湿实验人员必须
一眼看出哪些能当基因下单、哪些需要筛选战役。

`function_silenced` 家族带一条关键警告：Fc 沉默可以去除 FcγR 依赖的激动，但**不保证**
去除二价 Fv 自身受体聚簇引发的激动，signaling 必须在每个构造上实测。

#### 2.6 新增 `lib/product.py`：三实体产品模型

```text
AntibodyCandidate × ConjugationVariant → ADCProductCandidate
```

4 种偶联化学 × 10 个产品属性。**没有任何属性被估算**，状态只有 `requires_input` /
`requires_experiment` / `flagged_by_computation`。理由：偶联物行为由 payload 理化性质与
恒定区上下文主导，二者都无法从 Fv 推断。把裸 Fv 排名搬到产品上等于假设 payload 是惰性的。

Fv-only 输入唯一真正支撑的偶联结论：CDR 内溶剂可及赖氨酸。

---

### 3. 在本次工作中发现并修复的缺陷

这一条是本次最重要的记录，因为它**改变了科学结论**，而且是靠核对输出发现的，不是靠
测试失败。

#### 信息增益的朴素实现给出了科学上错误的实验顺序

首个实现：增益 = 能判别的**未定**失效模式数量，路线终止级计双倍。

首次实跑结果：

```text
gain=4  lysosomal_flux_quantification         ← 排第 1
gain=3  modality_kill_internalization_panel   ← 排第 2
```

**这是反的。** 两个独立的错误：

**错误一：忽略了"推翻"的价值。**
`surface_retention` 已被 Purcell 2014 的一句 "data not shown" 标为 `supported`，于是朴素
计数把它当作**已定论**、不给分。所以直接测内化的实验对这条得 0。

但一个被支持的路线终止级模式，恰恰是**最该去测的东西**——尤其当支持它的证据这么弱时。
支持它的是一句未展示数据，而要据此停掉一个项目所需的证据强度远高于此。

修复：能**排除**一个当前被支持的模式 → 给最高权重（路线终止级 4 分，其他 2 分）。

**错误二：忽略了级联的前置结构。**
递送级联是有序的，在 step 1 尚未建立时 step 3 的测量**无法解释**——一个"溶酶体递送分数"
没有表面结合分母和内化基线就没有意义。

修复：实验可声明 `prerequisite_steps`，前置未满足的实验标 `ready_to_run: false`，排序时
**无论原始增益多高都排在就绪实验之后**。

修复后：

```text
gain=7  READY                            modality_kill_internalization_panel  overturn=[surface_retention]
gain=5  READY                            construct_signaling_comparison       overturn=[receptor_agonism]
gain=4  READY                            normal_cell_uptake_panel             overturn=[normal_tissue_target_expression]
gain=4  BLOCKED(endosomal_entry)         lysosomal_flux_quantification
gain=3  BLOCKED(lysosomal_delivery)      proof_of_modality_adc_cytotoxicity
```

与优化指南的 Phase 0 优先级完全一致。

另外还加了一条保护规则：**已被支持的失效模式不会被更弱的证据降级为 `excluded`。**

#### 报告低估了首选实验的理由

修好排序后，报告只列出 `resolves_unresolved_modes`，没有列 `can_overturn_supported_modes`
——而后者才是它排第一的原因。已修正：报告现在高亮"可推翻的当前阻塞发现"，并解释为什么
这值得优先（阻塞发现背后的证据往往弱于据此行动所需的证据强度）。关键路径表格也补了
`Ready` 列，避免被前置条件阻塞的实验混在就绪实验里看不出来。

---

### 4. 重命名与诚实性修正

```text
developability_score            → sequence_computational_developability_score
developability_rank             → sequence_computational_developability_rank
04_ai_guided_engineering        → 04_binder_engineering_design
06_computational_triage         → 06_binder_quality_triage
09_adc_readiness                → 09_adc_failure_mode_analysis
```

长名字是刻意的：v0.2.0 的短名字诱导读者把榜首行当成"总体最优候选"，而它只是轨内序列预筛。

`04_ai_guided_engineering` 更名同理——这个 stage 是规则驱动的，叫 "AI-guided" 是误导。

新增 3 条禁止声明：仅凭序列声明 carrier 能力；把内化当单一布尔判据；变体继承亲本表型测量。

Stage 编号变动的完整映射写在 `stages.py` 的 `STAGE_MIGRATION_FROM_0_2_0`，并有测试保证
它覆盖 v0.2.0 全部 11 个 stage。

---

### 5. 明确**不**做的事

**没有接 ProteinMPNN，这是刻意的。** v0.2.0 把"没有学习模型"列为主要遗留项，这个判断
只对了一半。当前瓶颈不是 proposal generator 不够聪明，而是**目标函数缺失**。

若不知道该优化非激动、高内化、高 lysosomal flux、低正常组织摄取、偶联后稳定性，模型只会
**更高效地优化错误的目标**。写进代码的一句话：只用序列描述符训练出来的模型，只会预测
序列描述符。

所以 `12_active_learning` 当前不拟合模型是**正确的**；v0.3.0 让它先成为严格的数据闭环
（变体进、表型出、元数据强制），并把"模型就绪的 5 步顺序"写进
`sequencing_for_model_readiness` 字段。

**没有随附"有数据"的示例。** 附一份虚构的 enavatuzumab 表型数据集有被误当真实数据的
风险。有数据的正向路径由测试覆盖（用明显合成的数值）。

---

### 6. enavatuzumab 运行结果（v0.3.0）

`status: complete`，无阻塞 stage，13 秒（ABodyBuilder2 权重已缓存）。

#### Track B：0 条可用观测——这是发现，不是遗漏

enavatuzumab 所有可得的 trafficking 表述要么是文本摘要、要么是未展示数据，**没有一条
携带 carrier 观测所需的元数据**。0.3.0 schema 下这样的表述不是可用观测。

结果链条自洽：

```text
usable observations = 0
→ 五步级联全部 no_data，step 1 起即未解决
→ adc_carrier_quality_score = null（未测，非差）
→ 无二维 Pareto 前沿，28 条候选全部 incomparable
→ modality decision = modality_unproven_run_kill_experiment
→ 继续条件满足 0 / 7
```

那条唯一相关的文献表述记录在 `known_evidence.internalization`
（`direction: absent_with_negative_indication`），在失效树里正确地把 `surface_retention`
标为 supported，**而没有被升格为它并不是的"测量"**。

#### 失效树位置

15 个模式：**3 supported、2 excluded、10 unresolved**。三个被支持的全是路线终止级：
`surface_retention`（Purcell 2014）、`receptor_agonism`（Lam 2018 肝胰毒性，归因于经受体的
激动信号）、`normal_tissue_target_expression`（Choi 2017 肾/胰/胆管）。

两个被排除：`target_density_insufficient`、`antibody_binding_insufficient`（KD 5.5 nM）。

#### 产品矩阵

48 个产品候选（12 carrier 候选 × 4 偶联化学），**0 个当前可造**（缺恒定区、未声明
linker/payload）。唯一计算结论：`H59` 是 CDR 内溶剂可及赖氨酸 → 推荐首选
`site_specific_engineered_cysteine`。

#### Track A（仍有效，只是不是当前约束）

framework 一致度 VH 92.5% / VL 93.7%；16 条 flag，暴露度加权 burden 44.0 → 28.16，
11 条降级；42 条提议，17 条需结合确认，1 条 dual-benefit（`VL-M37L`）；
28 条序列候选 + 11 条构造/战役规格。

---

### 7. 验证

```
.venv/bin/python -m pytest genmodules/antibody_binder_asset_engineering/tests/ -q
63 passed
```

测试从 40 增至 63。新增覆盖重点：

- **元数据强制**：缺字段 / 缺分母 / 单一重复 / 未知测量类型，四种都必须 `unusable`
- **五步级联独立性**：断言 `CASCADE_STEPS` 就是那五个 id
- **`null` ≠ 0**：carrier 分数未测时为 `null`，且解释里含 "not a low score"
- **counter-screen 强制**：无对照的杀伤不能支持 `cytotoxic_sufficiency`；补上对照后可以
- **冲突观测**报 `conflicting`，而非任选一边
- **推翻信用**：能推翻阻塞发现的实验必须排第一
- **前置门控**：下游级联实验必须被阻塞；前置满足后必须解除
- **已支持模式不被弱证据降级**
- **Pareto**：权衡对都留在前沿；缺失轴 `incomparable` 而非 0；无数据时拒绝命名 lead
- **构造规格不是序列**：`sequence_available` 必须为 false 且带 blocker；补齐恒定区后转为 true
- **kinetic ladder 拒绝编造**亲和力变体
- **产品属性无一被估算**；CDR 赖氨酸驱动位点特异性推荐
- **归档不可发现**：`FROZEN.md` 存在、归档 `module.yaml` 仍是 0.2.0、生成器 `SKIP_DIRS` 含 archive
- **向后兼容**：0.1.0 形态输入仍能通过校验
- 端到端：enavatuzumab 必须给出 kill-experiment 结论、序列/构造家族必须可区分、
  实验设计必须延后序列工作

保留自 v0.2.0 且**边界未变**的断言：`adc_readiness_score` 永不输出（即使全部证据齐备）、
`dar_estimate` 不可从可变区推断、adverse 与 gap 区分、overlap-safe 基序扫描、埋藏降风险
但不删旗标、framework 一致度双向可动、dual-benefit 合并。

---

### 8. 未完成 / 后续工作

- **Track B 需要真实数据才有价值。** 目前它只能给出"去测"这一个结论——这是正确的，
  但意味着 v0.3.0 的价值有一半在于它**拒绝**做的事。
- 失效树是穷举建模的模式，不是所有可能失效；`excluded` 只在其 `basis` 证据强度内成立。
- 信息增益不是成本收益比，不含 assay 难度与周期，只给 `cost_tier` 供人工权衡。
- 产品属性全部待补输入或补实验；构造规格需恒定区序列才能表达为序列；
  kinetic ladder 需筛选战役。
- SASA 仍是孤立 Fv 单一构象，framework 可及性是上界，且结构预测有运行间波动。
- 8 个数据根目录仍未注册，02 / 13 阶段仍是检索方案。
- `AntibodyAssetEngineeringPackage@0.3.0` 无机器可读契约文件。

---

### 9. 沿用自上一条目、仍未修复的既有问题

`configs/historical_adc_benchmark.yaml:4` 指向
`../Zhixins-KB/3.Distill/3.Agents/5.ADC_Expert/ADC_Drugs`，而该 KB 树现位于
`../Zhixins-KB/2.Biotech/5.ADC_Expert/ADC_Drugs`。这条过期路径是 `tests/test_historical.py`
4 个用例失败的原因，与本模块无关。仍选择报告而不改：属共享配置且在本任务范围外，应先
确认 KB 重组是有意的。

---

## 2026-07-30 — v0.3.0 → v0.3.1，由 TPP-2658（抗 TWEAKR，拜耳）实跑驱动

**目的。** 用手上已有的序列优化 TPP-2658。结果这次实跑暴露了 0.3.0 里四个**风险
分类缺陷**，每一个都把危险的突变标成了安全的。修完之后 TPP-2658 的结论完全变了，
所以记为缺陷，不是改良。

### 1. 基线：0.3.0 给 TPP-2658 的建议

3 个家族、23 个候选。第 2 名 `DEV-C01`（0.5991）里打包了 `VH-D62E` 和 `VH-W110F`。
还建了一个 4 个候选的 `germline_reverted` 家族（`VH-I35S`、`VH-Y50A`、`VH-H59Y`）。
26 个提议里只有 4 个被标为需要结合确认。

上面这些具体输出**全部是错的**。

### 2. 缺陷：region 只用 IMGT 一套定义

`region` 一路喂给 `liabilities.FUNCTIONAL_CONSEQUENCE` 和
`design.RISK_TIER_BY_REGION`。逐残基核对后确认：TPP-2658 的 VH 有 18 个位点、
VL 有 9 个位点，IMGT 和 Kabat 的判定不一致。按 IMGT，**Kabat CDR-H1 的 34-35 和
Kabat CDR-H2 的尾部 58-65 落在 FR2/FR3 里**。

具体后果：`VH-D62E` 是优先级第二高的提议，标成 FR3、`engineering_risk: low`、
`requires_binding_confirmation: false`。但 D62 就在 `YISPSGGSTHYADSVKG` 里面——
**这是专利自己给这个抗体写的 CDR-H2 共识序列**。也就是说，模块把一个位于亲和力成熟
过的 CDR 正中间的突变，当作"框架区顺手清理、不需要测亲和力"推荐了出来。

**修法。** `numbering._union_map` 按线性位置合并两套图，并断言残基一致（不一致就
退回纯 IMGT，绝不混用）。`region` 取"改动代价更高"的那个判定；`imgt_region`、
`kabat_region`、`region_definitions_agree` 在每条 hit 和每条提议上都报出来。框架
同一性仍然只用 IMGT 框架计算，所以 humanness 数字仍可与文献比较——**并集只管风险，
不管同一性**。

现在 `VH-D62E` 是 CDR2、`high`、需要结合确认，并被逐出保守家族。

### 3. 缺陷：没有"保守结构锚定位点"的概念

模块提议了 `VH-W36F/Y`（IMGT H41）、`VH-W110F/Y`（IMGT H118）、`VL-W35F/Y`
（IMGT L41），全部标 `engineering_risk: low`。这三个是**两个核心色氨酸和 J 区色氨酸**
——免疫球蛋白折叠的不变地标。其中 `VH-W110F` 还被打包进了第 2 名候选里。

**修法。** `numbering.STRUCTURAL_ANCHORS` 覆盖 IMGT 23、41、89、104、118。这些位置
的提议被**拒绝**并写入 `rejected_proposals`，附锚定位点名称和处置建议（用配方、顶空、
避光控制氧化，而不是改序列）。

为什么是拒绝而不是加警告：模块里其他所有提议都是审阅者**可以合理选择**的权衡，
这一类不是——锚定位点是整个折叠层面的不变量，不只是这个谱系里保守。保留在记录里，
是为了让"这个 liability 被看见了、并且被明确拒绝了"可查。锚定位点的
`remediation_risk` 直接钉在 3。

### 4. 缺陷：埋藏只降低了优先级，没有提高风险

`_exposure_factor` 对埋藏残基下调化学风险——这是对的，溶剂和过氧化物确实更难接触
——然后就没有别的动作了。结果**埋在核心里的突变反而成了最便宜的修法**，标 `low`
且不需要任何确认。

这两个轴是**反向**的。埋藏降低化学紧迫性，同时提高补救代价，因为埋藏侧链是和邻居
堆叠在一起的。所以埋藏型 liability 是**最不紧迫、也最贵**的那一类。

**修法。** `REMEDIATION_COST_BY_EXPOSURE` 给 `remediation_risk` 加埋藏罚分。
`FOLD_RISK_ESCALATION` 按档提升 `engineering_risk` 并置
`requires_fold_confirmation`——**故意不是** `requires_binding_confirmation`：埋藏
问题由表达量和热稳定性回答，不是由亲和力实验回答。

`VH-W47F`、`VH-M83L`、`VH-D90E` 从 `low` 变 `high`；`VL-M4L` 从 `low` 变 `moderate`。

### 5. 缺陷：胚系编码的 liability 被当成了抗体自身的缺陷

三个 FR3 脱酰胺修法 `VH-N74Q/N77Q/N84Q` 构成了整个 `conservative_liability_removal`
家族——号称"改进母本最安全的方式"。但打分把这三个**都排在未修改的母本之下**，正是
这个反常促使我去查：N82、N85、N92（IMGT）**就是 IGHV3-23 的胚系残基**。去掉它们会
降低框架同一性。打分按 humanness 0.20 对 burden 0.35 的权重把这个代价算对了，但输出
里没有任何一句话说明原因，所以那个排名看起来像打分 bug，而不是一个发现。

**修法。** 每条 hit 带三态 `germline_encoded`，每条提议带
`reduces_framework_humanness`，并把代价写进 rationale 文本。`null` 表示该位点落在
V 基因框架比对之外（CDR3 是接合区，FR4 来自 J 基因），**不能读成"体细胞突变"**——
这沿用模块既有的原则：缺数据不等于负结果。摘要计数拆成 `germline_encoded_hits`、
`somatic_hits`、`germline_comparison_unavailable_hits`。

对 TPP-2658 而言这一条是决定性的：**11 个胚系编码，0 个体细胞，2 个不可比较。**

### 6. 对候选家族的连带影响

- `conservative_liability_removal` 现在要求**两套定义都判为框架** *且* 风险档位
  未被提升，这样埋藏核心突变就进不了那个自称最安全的家族。
- `germline_reverted` 现在要求两套定义都判为框架。TPP-2658 的三个 IMGT 框架胚系
  偏离**全部**是 Kabat CDR 残基，所以这个家族**正确地空了**——之前模块凭空造出了
  4 个本不该存在的候选。
- 新增 `proposals_in_no_family`，这样收紧过滤条件不会让活的提议在 stage 04 到
  stage 05 之间凭空消失。

### 7. 打分表达不了这些，所以标记必须并列显示

Track A 给 liability burden 0.35 的权重，所以一个打包多个突变的组合候选几乎不管
打包了什么都会排得靠前。`DEV-C01` 现在仍然排第 2（0.66）。**修法不是重新调权重**
——它本来就是计算描述符的比较，`promotion_eligible: false`——而是把标记放进同一张
表。`highest_engineering_risk`、`requires_fold_confirmation`、
`reduces_framework_humanness` 现在跟在每一行 triage 上，报告里也附了"打分不包含
这些"的说明。

### 8. 验证

81 个测试通过（原 63）。新测试覆盖：并集图正确采用 Kabat 的 CDR 判定、残基不一致时
退回 IMGT、胚系三态标记；锚定位点 liability 被上报但绝不被提议；埋藏使两个轴反向
移动；埋藏突变要求折叠检查而非结合检查；humanness 代价 rationale；以及 5 个
TPP-2658 集成断言（含空胚系家族、D62E 的争议 region）。

版本测试和报告断言现在都从 `module.yaml` 读版本号，所以升版本不会既让测试挂掉、
又留下版本号写错的报告。

### 9. 本次未改变的已知缺口

- TPP-2658 的 Track B 仍然无数据。`adc_carrier_quality_score` 为 `null`，含义是
  **未测量**，不是差。
- `STRUCTURAL_ANCHORS` 只覆盖 5 个 IMGT 地标。高度保守但不属于 IMGT 锚定位点的
  位置（VH 47 最典型）目前只靠埋藏兜住，不是靠保守性。要正确覆盖需要一张逐位点的
  胚系频率表。
- region 并集只查了 IMGT 和 Kabat，没查 Chothia 和 contact 定义。
- `configs/historical_adc_benchmark.yaml:4` 仍指向已移动的 ADC 药物目录，
  `tests/test_historical.py` 仍有 4 个既有失败。那是本模块之外的共享配置：
  **只上报，未改动**。

## 2026-07-31 — v0.3.1 正式契约稳定化

- 正式执行目录冻结为 14 stages；evidence graph 与 cross-asset retrieval 代码保留为
  未注册原型，不属于 v0.3.1 输出契约。
- 发布并实际执行两份 v0.3.1 YAML 契约；runner 现在记录来源输入版本、统一归一化版本、
  manifest identity、stage catalogue hash、相对 artifact 引用及逐文件 SHA-256。
- 活跃版本身份统一为 module/input/output/manifest `0.3.1` 与 14 stages。
- 原 TPP-2658 run 未修改并被隔离；新 run
  `v031-tpp2658-contract-consistent` 完整复跑且 contract validation 通过。
- 聚焦回归结果：107 个测试全部通过。

---

## 2026-07-31 — v0.3.1 → v0.4.0，三层证据能力

**目的。** 之前的 pipeline 能给出建议，**但没法为建议辩护**。它报 `internalization =
adverse`、把 kill 实验排第一，而 reviewer 问"为什么不是 lysosomal trafficking"时，只能
去读排序函数。而且它把每个资产**孤立分析**，旁边就摆着 379 个临床 ADC 的语料。

### 一、证据分层与置信传播（`lib/evidence.py`）

六级阶梯（由弱到强）：patent、literature、internal_assay、adc_precedent、
animal_efficacy、human_evidence。**这个顺序是声明的项目政策**，可争论、可在一个元组里
改，不是关于世界的事实。

五个量**分开报告**，因为把它们揉成一个数正是置信度不可信的根源：

```
direction_agreement   分层加权的有向一致性，[-1, 1]
evidence_count        有几条证据涉及该准则
evidence_diversity    横跨几个层级
evidence_freshness    最新一条多旧（分档）
confidence_band       由层级/多样性/新鲜度合成的定性标签
```

`direction_agreement` **故意与规模无关**：十条互相印证的专利句得 1.0，因为那是一个层级
重复了十次，不是更强的证据。这种情况下 `confidence_band` 仍然是 `weak` —— 两者并存的
意义就在这里。

新鲜度用**运行 manifest 的时间戳**，不用系统时钟，所以在旧 run 目录里重跑某个 stage 会
复现原来的数字。

### 二、推理图（`lib/evidence_graph.py`，stage 15）

Observation → Hypothesis → Failure mode → Decision → Experiment，每条边带 `because`。

**它不做任何新推理** —— 每条边在 stage 07/09 里都已经算出来了，只是此前仅以控制流的形式
存在。它唯一真正新增的是 `rejected_alternatives`：**每一个未被选中的实验都有
`reason_code` 和一句话理由**。

在 TPP-2658 上这一条是承重的：`lysosomal_flux_quantification` 的信息增益与冠军**并列
（4 比 4）**，区分它们的只有一个未满足的前置条件。没有拒绝记录，那个排序看起来就是随意的。

### 三、跨资产检索（`lib/cross_asset.py`，stage 16）

379 个案例，其中 219 个有可用属性 frontmatter。按 target / payload 家族 / 可裂解性 /
偶联化学 / DAR 档做加权匹配，**匹配、差异、不可比三类属性全部报出** —— "差在哪"才是可
行动的那一半。

**刻意不用 embedding**：embedding 会给出排序却不让 reviewer 看到是哪个属性驱动了它，
那正好与这一层的目的相反。

测试里有个验证探针：HER2 + DXd 的输入**必须**首位返回 Enhertu，匹配权重 11/12。达不到
就说明这一层坏了。

### 建设过程中发现并修掉的 5 个缺陷

1. **`internal_assay` 的关键词匹配到了 "internalisation"** —— 一条文献证据被标成自有
   实验数据。已改为词边界 + 短语锚定。
2. **通用词制造假的"同靶点"匹配** —— "TWEAK receptor (Fn14)" 与 ROR1、CD71、FRα 共享
   token `receptor`，检索把三者都报为同靶点比较对象。**这是这一层能产生的最具误导性的
   输出。** 已加 `TARGET_STOPWORDS`。
3. **属性大量不可比时相似度虚高** —— 四个属性不可比、只中一个的对象，排名反而高过被全面
   比较的对象。改为按绝对匹配权重排序，并加 `similarity_is_partial`。
4. **一串并列项被读成"这就是你的比较对象"，而真实答案是"没有"** —— TPP-2658 在语料里
   既无同靶点、也无同 payload 类的对象。已加显式 `no_close_precedent` 判定：**两个轴上
   都没有先例，本身就是一个发现。**
5. **`evaluate_cascade` 从未输出过名为 `observations` 的键**，而图正是读这个名字。于是
   **测量证据层在每一张图里都是缺失的**，且恰恰在没有 carrier 数据的抗体上看不出来 ——
   那时候"缺一层"看起来是对的。现已输出 `usable_observations`。

第 1、2、5 条都是**看输出**发现的，不是测试发现的。第 5 条是原型评审时被提出的异议，
**它是对的**。

### 关于命名的异议，以及为什么它成立

原型评审提出："signed evidence direction 不是一个 epistemic-confidence 契约。"
**正确。** 一个叫 `confidence` 、实际测量"来源是否指向同一方向"的字段，恰恰会诱发它本该
防止的误读。已改名 `direction_agreement`，语义串里写明这一点，并新增
`confidence_band` 作为 reviewer 真正想要的那个合成量。

### 契约

`ExistingBinderAssetInput@0.4.0`（形状未变，版本跟随模块，便于消费方成对锁定）与
`AntibodyAssetEngineeringPackage@0.4.0`：把两个 stage 从 `explicitly_not_registered`
移入正式目录、加入它们的必需字段、给 stage 09 加 `evidence_confidence`，并新增
`evidence_semantics` 段，**使消费方不可能把 `direction_agreement` 读成概率**。

### 验证

**108 通过、1 跳过。** 两个示例抗体都跑满 16 个 stage，
`contract_validation.status: passed`、`errors: []`。

那个跳过：`genmodules/scripts/update_readme.py` 已从工作区移除，所以该测试的后半段跳过
（冻结断言仍在跑，生成器一旦回来检查自动重新生效）。**这意味着 `genmodules/README.md`
已无法再生成 —— 只上报，未修复，因为它在本模块之外。**

### 已知缺口

- 检索只读属性 frontmatter。379 个文件中有 160 个没有，所以**"不在比较列表里"不等于
  "不存在比较对象"**。
- Gate 向量检索未实现，**也不应该在这里实现** —— 本模块不得计算 Gate 分数，那属于 Gate 层。
- 层级推断是基于来源文本的关键词。输入里的 `evidence_tier` 可覆盖它，凡是层级重要的场合
  都应显式声明。
- `confidence_band` 的阈值是规则，不是标定结果。
