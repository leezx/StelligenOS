# EXT-03 `asset_search_engine`

- 状态：`shell_only`
- 优先级：中
- 来源：`prompts/GPT-Feedback.md` `# v4` 一级风险三

## 要解决的问题

目前 Asset Generation 只有两条路线：existing binder 和 de novo binder。但真实 ADC 优化远不止 binder——payload、linker、DAR、位点特异偶联、Fc 工程、半衰期调节、亲和力调节、表位位移、内吞增强，全部属于资产搜索空间。

现在的分工是：Product Realization Gate（P-chain 16 个 Gate）负责**评价**这些维度，但没有任何模块负责**主动搜索**它们。也就是说系统能判断一个 ADC 设计好不好，却只会生成 binder。

## 当前的显式决策

人类负责人的当前决策是：先做第一步 ADC 抗体，下游先用标准 ADC 平台参数垫着，不一次性优化全部搜索轴。

这个决策是合理的取舍，本扩展不推翻它。本扩展存在的意义是把被推迟的搜索轴**明确登记为推迟**，而不是让「标准平台垫着」在无人注意的情况下慢慢变成永久默认。这是壳子本身的价值：它让一个临时妥协保持可见。

## 设计逻辑（待激活）

搜索空间按轴划分，每个轴挂若干 generator：

| 搜索轴 | 当前状态 |
|---|---|
| `binder` | 内核已有两条路线（existing binder / de novo），权威实现 |
| `payload` | 标准平台默认值，未搜索 |
| `linker` | 标准平台默认值，未搜索 |
| `dar` | 标准平台默认值，未搜索 |
| `conjugation_site` | 标准平台默认值，未搜索 |
| `fc_design` | 未搜索 |
| `half_life` | 未搜索 |
| `affinity_tuning` | 未搜索 |
| `epitope_shifting` | 未搜索 |
| `internalization_enhancement` | 未搜索 |

所有 generator 的输出统一进入既有的 Product Realization Gate 评价，不新开评价通道。这一点很重要：搜索能力的扩展不应该带来第二套评价标准。

内核的两条路线仍然是权威实现，在这里只是被登记为 `binder` 轴上已实现的 generator。

## 边界

不取代、不修改内核的两条生成路线。不绕过 Product Realization Gate。不自动扩大搜索空间——每个 generator 的启用都需要显式决策。生成结果、序列库和搜索中间产物全部留在外部工作区。

## 激活前必须回答

1. 哪个轴的优先级最高？（`payload` 和 `linker` 的搜索空间最大，但也最依赖外部湿实验数据。）
2. 多轴联合搜索的组合爆炸怎么控制？这与 `EXT-04 stop_rule` 和 `BL-02`（动态排序剪枝）是同一类问题。
3. 「标准 ADC 平台默认值」具体指哪一组参数？这组默认值本身需要被版本化记录，否则将来无法解释历史资产为什么长这样。
4. 每个 generator 依赖哪些外部科学工具，工具不可用时的行为是什么？（内核的 de novo 路线已有先例：工具不可用时只固化约束和实验包，不虚构序列。）
