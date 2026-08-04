# EXT-02 `dynamic_gate_context`

- 状态：`partially_absorbed`（核心概念已进内核，剩余范围未做）
- 优先级：中
- 来源：`prompts/GPT-Feedback.md` `# v4` 一级风险二

## 状态变更说明（2026-08-04）

本扩展的核心论点**已经由内核实现**，而且是改在内核里，不是像本扩展原先设想的那样用适配器绕过去。

v5 clinical hypothesis 架构（PR #45，合并为 `a5bf77f`）把早期研发单元从
`target-indication-endpoint` 三元组改成了：

`Target × Anchor Clinical Context × Intended Benefit/Product Hypothesis`

也就是下文「要解决的问题」一节所主张的那件事。因此：

- 状态从 `shell_only` 改为 `partially_absorbed`。
- 原先的 `design_constraint`「以适配器方式实现，不改内核」不再是对现实的描述，已改为只约束**剩余范围**。
- 下文的论证和五轴设计**原样保留**，作为这次内核变更的来源记录，不删。

### 内核已经覆盖的部分

| 本扩展原主张 | v5 内核实现 |
|---|---|
| 评分对象不应是裸 `Target` | `ClinicalHypothesis` 组合 target、anchor context、intended benefit、biomarker、product hypothesis |
| context 应是身份的一部分，不是属性 | `AnchorClinicalContext` 是独立对象，`ClinicalHypothesis` 按引用组合 |
| Gate 输入需带 context | Gate 输入携带 `clinical_hypothesis_ref` 与递进 lock state |

### 剩余范围（本扩展仍然负责）

| ID | 项 | 为什么 v5 没覆盖 |
|---|---|---|
| `RS-01` | 五个 context 轴的取值域 | v5 给了 `AnchorClinicalContext` 这个容器，没定义各轴是自由文本、受控词表还是外部本体。 |
| `RS-02` | 逐 Gate 的跨 context 复用策略 | v5 完全没触及。`contracts.py` 的 `GateContextBinding` 默认 `undecided`，45 个 Gate 需专家逐个标注。 |
| `RS-03` | context 变化时既有 Gate 结果的失效规则 | v5 引入的 lock state 表达的是承诺程度，不是 context 失效；「既不自动继承也不自动重置」仍未实现。 |
| `RS-04` | context 粒度 | 「三线 CRC」与「三线 MSS CRC」是一个还是两个 context，仍未定。 |
| `RS-05` | 既有 CRC 试运行结果的映射 | 9 indication / 36 endpoint / 41 target 如何映射到 `ClinicalHypothesis` 身份，仍未定。 |

`RS-02` 是剩余范围里工作量最大也最不能自动化的一项。

## 要解决的问题

45 个 Gate 几乎全部假设 target 是一个固定对象。但真实 ADC 里，一个 target 的意义完全依赖临床背景：

HER2 在乳腺癌、在 CRC、在 HER2-low，是三件不同的事。同一个 gate_id 对这三者给出的答案不应该是同一条记录。

所以真正的评分对象不是 `Target`，而是 `Target × Clinical Context`。

架构文档第 2 节的第一条原则已经是「临床问题先行」，方向是对的；但 Gate 的输入对象仍然偏向 `TargetHypothesis`，context 只是它的属性，而不是身份的一部分。结果是同一个 target 在不同背景下的结论有折叠风险。

## 设计逻辑（待激活）

用**适配器**方式解决，而不是改内核。

五个 context 轴：

| 轴 | 说明 |
|---|---|
| `indication` | 适应症 |
| `disease_stage` | 疾病阶段 |
| `line_of_therapy` | 治疗线 |
| `biomarker_status` | biomarker 状态（例如 HER2-low 与 HER2-positive 是不同取值） |
| `combination_setting` | 单药还是联合，以及联合对象 |

这五个轴加上 target 构成 `ScoringSubjectRef`——一个 context 限定的复合身份。Gate 结果按这个复合身份存放，于是 HER2-in-CRC 和 HER2-in-breast 永远不会折叠成一条。

内核侧不动：`gate_id` 不变，`GateInputEnvelope@2.0.0` 不变，45-Gate 拓扑不变。扩展只负责生成和解析复合身份。

一条重要约束：context 变化时，既有 Gate 结果**既不自动继承也不自动重置**。自动继承会把乳腺癌的结论偷渡到 CRC；自动重置会丢掉真正可复用的 target 生物学证据（比如蛋白序列层面的表位可实现性，本来就与适应症无关）。所以哪些 Gate 的结果可跨 context 复用，必须逐 Gate 由专家标注，这是激活前的主要工作量。

## 未来方向（不在本扩展范围）

专家建议最终把 Gate 输入抽象成 `ClinicalOpportunity` 而不是 `Target`，这样 ADC、TCE、Radioligand 可以统一到同一套 Gate 上。

v5 的 `ClinicalHypothesis` 已经朝这个方向走了一步，但它仍以 ADC 为唯一落地形态，没有抽象到跨模态。跨模态统一仍是内核级变更，必须另立治理任务。

## 激活前必须回答

1. 五个轴各自的取值域是什么？是自由文本、受控词表，还是引用外部本体？（`RS-01`）
2. 哪些 Gate 的结果可以跨 context 复用？（例如表位可实现性可能可以，肿瘤表面可及性肯定不行。）（`RS-02`）
3. context 的粒度到哪一层？「三线 CRC」和「三线 MSS CRC」是同一个 context 还是两个？（`RS-04`）
4. 已经产出的 CRC 试运行结果（9 indication / 36 endpoint / 41 target）如何映射到 v5 的 `ClinicalHypothesis` 身份？（`RS-05`）

上述四问在 v5 之后**全部仍然成立**，v5 没有回答其中任何一个。
