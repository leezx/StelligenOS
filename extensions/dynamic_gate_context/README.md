# EXT-02 `dynamic_gate_context`

- 状态：`shell_only`
- 优先级：中
- 来源：`prompts/GPT-Feedback.md` `# v4` 一级风险二

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

专家建议最终把 Gate 输入抽象成 `ClinicalOpportunity` 而不是 `Target`，这样 ADC、TCE、Radioligand 可以统一到同一套 Gate 上。这是内核级变更，必须另立治理任务。本扩展只做到「复合身份」这一层，为那次变更铺路而不代替它。

## 激活前必须回答

1. 五个轴各自的取值域是什么？是自由文本、受控词表，还是引用外部本体？
2. 哪些 Gate 的结果可以跨 context 复用？（例如表位可实现性可能可以，肿瘤表面可及性肯定不行。）
3. context 的粒度到哪一层？「三线 CRC」和「三线 MSS CRC」是同一个 context 还是两个？
4. 已经产出的 CRC 试运行结果（9 indication / 36 endpoint / 41 target）如何映射到复合身份？
