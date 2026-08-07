# Handoff：WP2A —— Opportunity Territory Schema

- 日期：`2026-08-07`
- 任务分支：`task_20260807_opportunity-territory-schema`
- 基线：`main` @ `822440c`
- 交付物类型：**schema 合同（无实例、无疾病内容、无执行）**
- 架构变更：`NEW_CONTRACT_NO_EXISTING_CONTRACT_MODIFIED`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、定位

Work Package 2A，对应执行策略的 **Pool 00** 与 **Stage 1**。按审核方要求把 WP2
拆成两半，本 PR 只做 **2A：纯 schema，一条 CRC 内容都没有**。

这是新旧管线真正分界的地方：

```text
旧：CRC unmet need → 41 targets → 369 pairs      候选先生成，再收敛
新：Territory → ACTIVE → Wedge → Target          先约束搜索空间，再生成候选
```

## 二、交付

`OpportunityTerritory@0.1.0`（一行 = 一片临床水域）与
`OpportunityTerritoryMap@0.1.0`（整张图）。

字段按源文档 Stage 1 的推荐清单逐项落地：临床定义、当前失败、竞争、可得性、
发起方优势、路由、溯源。

**竞争字段放在这一层是有意的。** 源文档指出旧管线把商业竞争分析放得太晚；
position occupancy 必须在 territory 阶段参与判断，因为它决定**是否发起 Program
Thesis**，而不是最后给一个分数。

## 三、三处需要审核方注意的判断

### 1. 不新增第四套状态词汇

源文档把 territory 状态写了**三套**：

```text
ACTIVE_TERRITORY / WATCH_TERRITORY / PARTNER_DEPENDENT / OUT_OF_MANDATE
ACTIVE_TERRITORY / WATCH           / PARTNER_ONLY      / OUT_OF_MANDATE
ACTIVE           / WATCH           / PARTNER_ONLY      / OUT
```

本合同直接 import 已冻结的 `SearchSpaceRoute`
（`ACTIVE_SEARCH`／`WATCHLIST`／`PARTNER_ONLY`／`OUT_OF_MANDATE`），不再声明第四
套。这与 `SponsorFitRoute` 复用 `ProgramCommitmentDecision` 词汇是同一处理。

### 2. 路由不在这一层重新裁定，并顺带给了 `SearchSpaceAdmission` 第一个消费者

territory 携带 `search_space_admission_ref` 并在 `territory_status` 中镜像该
路由；**admission 才是权威**。仓库只持有引用，不解引用、不重算它的八个条件、
不给 territory 重新路由。

审核方说过「下一阶段不应该再补 binding 细节」。**本 PR 不是 binding PR**——
territory 本来就必须记录它被谁路由，否则这一层会变成第二套路由逻辑。副作用是
`SearchSpaceAdmission` 从此有了消费者，不再是无人消费的形状合同。若审核方认为
这一步应拆出，可以退回 `search_space_admission_ref`，但那样 `territory_status`
就会成为无出处的自declared 值。

### 3. `Stelligen_evidence_advantage` → `sponsor_evidence_advantage_ref`

发起方身份属于它引用的 `DevelopmentSponsorProfile`，不该写进 schema 字段名。

## 四、两条刻意宽松的规则

**空列表是合法状态。** 只有 `source_refs` 必须非空。没有竞争者、没有预期
readout、没有已知靶点生物学——这些都是真实且有信息量的状态，不该被 schema
强行填满。

**空 map 合法。** 一个疾病范围可以先建图、再逐步纳入 territory。

## 五、一条刻意收紧的规则

`OpportunityTerritoryMap` 在**构造时**拒绝重复 `territory_id`。重复键把两片临床
水域悄悄合并成一片，正是 `SRCADM-01` 审计事后才去找的那类缺陷。

本合同的 external-ref 校验也比既有几份严：除 `external:` 前缀外，还要求前缀后
**内容非空**（`external:` 与 `external:   ` 均拒）。

**由此产生一处跨合同不一致，登记不修：** `search_space_admission.py`、
`sponsor_fit_assessment.py`、`program_commitment_review.py` 仍只校验前缀，允许
裸 `external:`。新合同从严是免费的，回头统一收紧既有三份属独立范围，不在本 PR
夹带。

## 六、变异检验

| 变异 | 结果 |
|---|---|
| 允许重复 `territory_id` | `FAILED (failures=1)` |
| 允许字符串状态（等于放行第四套词汇） | `FAILED (failures=1)` |
| 把 `search_space_admission_ref` 移出校验列表 | 首轮 **`OK`** |
| 强制所有列表非空 | `FAILED (failures=2, errors=1)` |
| 去掉裸 scheme 检查 | `FAILED (failures=22)` |
| 让 `with_status` 反向筛选 | `FAILED (failures=1)` |

第三项首轮通过，是**自我收缩的重言测试**——参数化测试遍历的正是它要验证的那个
常量，删掉字段也就删掉了用例。**这是我在 PR #72 上犯过的同一个错误。** 已补
两条：字面列出两个字段清单的断言，以及专门针对 `search_space_admission_ref`
的命名测试（它承载整个上游绑定，本就该有独立测试）。重跑后该变异升为
`FAILED (failures=6)`。六项回滚后 `diff -q` 均无差异。

## 七、本 PR 不做什么

不定义 program wedge；不生成 wedge-specific target；不做三重预筛；不执行任何
Gate；不排序、不打分；**不纳入任何 CRC 内容**；不修改任何既有合同、45 个 Gate、
T12、lifecycle 或 core objects；不推进 WP2B..WP6。

有测试断言：字段名中不含 `target_id`／`gene`／`pair`／`_score`／`rank`；模块源码
（去掉注释与 docstring 后）不出现 `CRC`／`MSS`／`HER2`／`TROP2`／`KRAS`／`BRAF`／
`colorectal`；import 集合恰为
`{__future__, dataclasses, typing, src.contracts.search_space_admission}`。

## 八、验证

```
Ran 469 tests  OK              （合并前 448，净增 21）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
```

无数据、cache、result、database、model weights 或实例进入仓库。

## 九、下游未声明

WP3 的 program wedge 将消费 `ACTIVE_SEARCH` territories。**该合同尚不存在**，
故 `downstream_relationship.consumed_by` 记为 `not_yet_defined`，不作任何下游
声明——不重演「文档声称硬控制、代码无人消费」。

## 十、后续顺序

1. 本 PR `APPROVE` 并合并。
2. **WP2B：CRC territories 内容。** MSS 后线、HER2+、KRAS G12C、肝转移、腹膜
   转移、drug-tolerant state 等。**按硬边界这部分是知识内容与数据，必须在仓库外
   产出，再走结果 PR。** 每个 territory 还需要一份 `SearchSpaceAdmission` 实例
   给出它的路由。
3. WP3 Program Wedge Generator → WP4 Target Generation 与三重预筛 →
   WP5 T0–T12 分批验证 → WP6 Commitment 与 Value-Inflection。

仍无消费者的 sponsor-relative 合同现在剩两份：`DevelopmentSponsorProfile`、
`ProgramThesis`。前者被本合同与 `SponsorFitAssessment` 以 `sponsor_profile_ref`
引用，但没有强制关系；后者的天然消费者是 WP3 的 wedge。
