# Opportunity Territory Map

版本：`OpportunityTerritory@0.1.0`、`OpportunityTerritoryMap@0.1.0`

这是 Work Package 2A，对应执行策略里的 **Pool 00（CRC Opportunity Territory
Map）** 与 **Stage 1**。

**本 PR 只有 schema，不含任何疾病内容。** territory 实例——包括全部 CRC
territories——按硬边界在仓库外产出。

## territory 是什么，不是什么

一个 territory 是一片**临床水域**：疾病阶段 × 分子亚型 × 治疗线次 × 既往治疗 ×
转移部位，加上那里当前如何失败、谁已经在里面、发起方能拿到什么数据。

它**不是候选**。这一层不出现任何靶点，也不生成任何靶点。

这正是新旧管线的分界：

```text
旧：CRC unmet need → 41 targets → 369 pairs      候选先生成，再收敛
新：Territory → ACTIVE → Wedge → Target          先约束搜索空间，再生成候选
```

Pool 00 的目的不是筛靶点，而是**发现哪些临床水域适合当前发起方**。

## 字段

| 组 | 字段 |
|---|---|
| 身份 | `territory_id` |
| 临床定义 | `disease_ref`、`clinical_population_ref`、`molecular_subtype_ref`、`treatment_line_ref`、`prior_therapy_refs`、`metastatic_site_refs` |
| 当前失败 | `current_soc_ref`、`clinical_failure_mode_ref`、`patient_size_band_ref` |
| 竞争 | `current_competitor_refs`、`leading_asset_refs`、`expected_readout_refs`、`position_occupancy_ref` |
| 可得性 | `known_target_biology_refs`、`available_patient_data_refs`、`available_model_refs` |
| 发起方 | `sponsor_evidence_advantage_ref`、`window_closure_risk_ref` |
| 路由 | `search_space_admission_ref`、`territory_status` |
| 溯源 | `source_refs` |

**竞争字段放在这一层是有意的。** 源文档指出旧管线把商业竞争分析放得太晚；
position occupancy 必须在 territory 阶段就参与判断，因为它决定**是否发起
Program Thesis**，而不是最后给一个分数。

### 两处命名判断

- 源文档写 `Stelligen_evidence_advantage`，这里的机器 ID 是
  `sponsor_evidence_advantage_ref`。发起方身份属于它引用的
  `DevelopmentSponsorProfile`，不该写进 schema 字段名。
- 源文档把 territory 状态写了**三套**：
  `ACTIVE_TERRITORY`／`WATCH_TERRITORY`／`PARTNER_DEPENDENT`／`OUT_OF_MANDATE`、
  `ACTIVE_TERRITORY`／`WATCH`／`PARTNER_ONLY`／`OUT_OF_MANDATE`、
  `ACTIVE`／`WATCH`／`PARTNER_ONLY`／`OUT`。
  本合同**不新增第四套**，直接 import 已冻结的 `SearchSpaceRoute`
  （`ACTIVE_SEARCH`／`WATCHLIST`／`PARTNER_ONLY`／`OUT_OF_MANDATE`）。

## 路由不在这一层重新裁定

territory 携带 `search_space_admission_ref` 并在 `territory_status` 中**镜像**
那个路由；**`SearchSpaceAdmission@0.1.0` 才是权威**。仓库只持有引用，不解引用
该 admission、不重算它的八个条件、不给 territory 重新路由。

这同时给了 `SearchSpaceAdmission` 它的**第一个消费者**——此前它和
`DevelopmentSponsorProfile`、`ProgramThesis` 一样是无人消费的形状合同。

**`ACTIVE_SEARCH` 不授权生成靶点。** 它只表示这片水域值得主动搜索。

## 空列表是合法状态

只有 `source_refs` 必须非空。没有竞争者、没有预期 readout、没有已知靶点生物学
——这些都是**真实且有信息量**的状态，不该被 schema 强行填满。

## 重复键在构造时就拒绝

`OpportunityTerritoryMap` 拒绝重复的 `territory_id`。重复键把两片临床水域悄悄
合并成一片，正是 `SRCADM-01` 审计事后才去找的那类缺陷；这次在入口就挡住。

## 边界

不定义 program wedge；不生成 wedge-specific target；不做三重预筛；不执行任何
Gate；不排序、不打分（有测试断言字段名中不含 `_score` 与 `rank`）；不纳入任何
CRC 内容（有测试断言模块源码中不出现 `CRC`／`MSS`／`HER2`／`TROP2`／`KRAS`／
`BRAF`／`colorectal`）。

模块 import 集合恰为 `{__future__, dataclasses, typing,
src.contracts.search_space_admission}`——最后一项只是那套冻结枚举，不是实例。

## 下游

WP3 的 program wedge 将消费 `ACTIVE_SEARCH` territories。**该合同尚不存在**，
因此 `downstream_relationship.consumed_by` 记为 `not_yet_defined`，不作任何
下游声明。
