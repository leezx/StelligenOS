# Sponsor Fit Assessment

版本：`SponsorFitAssessment@0.1.0`

这是 Work Package 1 的第四份合同，补齐该工作包原定的四项交付
（`DevelopmentSponsorProfile`、`ProgramThesis`、`SponsorFitAssessment`、
`ValueInflectionPlan`）中此前缺失的一份。

它对应执行策略里的 **Decision 3（Sponsor Fit Qualification）** 与
**Stage 6（正式 Sponsor Fit Assessment）**，回答的是：

> 当前这个发起方是不是推进这个项目的合适主体？应该走哪条路线？

## 它与 Program Commitment Review 的分工

两者刻意分开，不能互相替代：

| | `SponsorFitAssessment@0.1.0` | `ProgramCommitmentReview@0.1.0` |
|---|---|---|
| 回答 | 是否适配、走哪条路线 | 是否承诺资本、投到哪个边界 |
| 性质 | **建议**，带证据 | **授权** |
| 位置 | 科学机会合格之后 | 承诺检查点，binder/de novo route 之前 |

`route` 是**建议不是授权**——合同以
`route_is_a_recommendation_not_an_authorisation` 明确登记这一点。

## 七个必答问题

`evidence_advantage`／`capability_fit`／`capital_fit`／`time_fit`／
`differentiation_visibility`／`ip_capture`／`partnerability`。

七项必须**各答一次、不多不少**，每项只能取 `SATISFIED`／`UNKNOWN`／
`UNSATISFIED`，且必须附外部证据引用。

## 三条让这个检查点真正起作用的规则

**1. 不使用总分。** 来源文档对此说得很直接：这里不要用总分。合同以
`aggregate_score: forbidden` 登记，并有测试断言数据类里不存在任何形如
`*_score` 的字段。

理由不是风格问题：一个总分会让「能力齐备」去补偿「没有非对称优势」，
而那恰恰是这个检查点存在的目的。

**2. 路线资格是正证据，不是「没有反证」。** 这是本合同最核心的一条。

一个路线被允许，是因为**已经存在足够的 sponsor-fit 正证据**，而不是因为
「没有任何一项被明确记为 `UNSATISFIED`」。七项关键问题大部分是 `UNKNOWN` 的
评估，并没有证明 sponsor fit 成立——它只是没能证伪。

具体门槛见下表。**没有豁免机制。** 本合同编码的是当前 Stelligen 的生存规则，
不是通用 Biotech 规则；逐案豁免等于给这个检查点留后门，而它存在的目的恰恰是
防止「这个项目我很喜欢，所以特殊批准继续做」。发起方能力变化时，应当更新
`DevelopmentSponsorProfile` 或升合同版本，而不是不断发豁免。

**3. 需要三期才能证明的差异不算可见差异。** 若
`differentiation_requires_phase_3` 为真，则
`differentiation_visibility` 不得记为 `SATISFIED`。

## 六条路线的资格门槛

| 路线 | 必须 `SATISFIED` | 不得 `UNSATISFIED` | 至少一项 `SATISFIED` |
|---|---|---|---|
| `SELF_DEVELOP` | `evidence_advantage`、`capability_fit`、`capital_fit`、`time_fit`、`differentiation_visibility`、`ip_capture` | — | — |
| `CO_DEVELOP` | `evidence_advantage`、`differentiation_visibility`、`partnerability` | `ip_capture` | — |
| `PARTNER_NOW` | `partnerability` | — | `evidence_advantage` 或 `differentiation_visibility` |
| `DATA_PACKAGE_ONLY` | — | — | — |
| `MONITOR` | — | — | — |
| `STOP_FOR_SPONSOR` | — | — | — |

几点用意：

- `SELF_DEVELOP` 刻意**不要求** `partnerability`——有些项目计划继续独立融资。
- `CO_DEVELOP` 允许 `capability_fit` 与 `capital_fit` 为 `UNKNOWN`，因为合作方
  正是用来补齐这两项的；但必须证明**存在值得合作的东西**。
- `PARTNER_NOW` 若连 `partnerability` 都不成立，这个名字就没有语义依据；
  若两项优势全无，拿什么去找 partner。
- `DATA_PACKAGE_ONLY` 允许大量 `UNKNOWN`——它本身就是「先用自己的数据优势
  降低特定风险，不承诺完整资产开发」。这对当前 Stelligen 可能是很重要的一条路径。
- `MONITOR` 是 `UNKNOWN` 的天然归宿。

## `UNKNOWN` 与 `UNSATISFIED` 严格分开

- `UNKNOWN` **不是失败，也永远不自动 KILL**。七项全 `UNKNOWN` 是一份完全合法的
  评估，只是它无法支撑任何承诺型路线。
- 但**关键 `UNKNOWN` 会阻断 asset-directed 路线，直到它被解决**。这与上一条
  不矛盾：不判死刑，也不放行。
- `UNSATISFIED` 同样不构成 KILL，`DATA_PACKAGE_ONLY`／`MONITOR`／
  `STOP_FOR_SPONSOR` 始终可达。

`STOP_FOR_SPONSOR` **不是科学 KILL**，与 45 个 Gate 的判定完全无关。

## 路线枚举为什么复用 Phase 3 的词汇

来源文档把 Decision 3 的输出写作 `PARTNER_BEFORE_CONJUGATION` 与 `WATCH`。
那是自然语言描述；Phase 3 已经把它们分别收敛为 `PARTNER_NOW` 与 `MONITOR`，
以避免机器 ID 漂移。本合同复用同一套六值词汇，使「建议」与「消费该建议的承诺」
可直接比对。

## Capability map 与 Resource map

`capability_map` 每项记录一项所需能力来自
`owned`／`collaborative`／`cro_accessible`／`license_required`／`unavailable`。

`resource_map` 每项把一个关键不确定性映射到：实验、会改变哪个决定、成本分档、
能力来源、失败后果。

`cost_band_ref` **只是外部估算分档的引用**，不是数字、不是预算，本模块不对它
做任何计算。

## 边界

不授予 program commitment；不授权资本；不执行 Gate、EVGAP、模型或数据采集；
不改变任何科学 Gate 事实；不修改 45 个 Gate、lifecycle、core objects、
`ClinicalHypothesis` 或 `TargetHypothesis`；实例全部在外部 runtime。

模块的 import 集合恰为 `{__future__, dataclasses, enum, typing}`，有测试断言。

## 尚未绑定

`ProgramCommitmentReview@0.1.0` 目前**不要求** `sponsor_fit_assessment_ref`。
给一份已冻结并合并的合同增加必填字段属 breaking change，应另立 binding PR
处理，形态与 PR #72 对 `BinderAdcRouteRequest` 的绑定相同。

在那之前，本合同与 Phase 1／Phase 2 一样**没有消费者**——这一点在
`downstream_relationship.binding_status: not_bound` 中显式登记，不含糊。
