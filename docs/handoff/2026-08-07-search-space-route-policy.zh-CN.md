# Handoff：Search-Space Admission Route Policy（清除 `BLOCK-02`）

- 日期：`2026-08-07`
- 任务分支：`task_20260807_search-space-route-policy`
- 基线：`main` @ `a651dea`
- 交付物类型：**规则（无数据、无疾病内容、未授权任何运行）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、清的是哪个 blocker

`BLOCK-02`：`SearchSpaceAdmission@0.1.0` 要求每条 admission 引用一个外部、可审计
的 `route_policy_ref`，而该 policy 此前不存在。没有它，八个条件到四种路由的映射
没有依据，四种路由会退化为无据判断。

契约要求该 policy 定义四件事，本文件逐项交付：

| 要求 | 交付 |
|---|---|
| 八个条件各自的判定标准 | `criteria`，每条含 `satisfied_when`／`unsatisfied_when`／`unknown_when`／`evidence_from` |
| 条件组合到四种路由的映射 | `routing.rules`，7 条按优先级排列 |
| `UNKNOWN` 的处理方式 | `unknown_handling` |
| 重评估触发条件 | `reassessment_triggers`，`RT-01`..`RT-07` |

## 二、一处需要审核方裁定的边界判断

**policy 是规则，不是数据，因此正文放在仓库内。** 它不含任何 CRC 内容、任何
territory、任何靶点——有测试断言规范段落中不出现 `CRC`／`MSS`／`HER2`／
`TROP2`／`KRAS`／`BRAF`／`colorectal`。

但 `route_policy_ref` 必须是 `external:` 引用。两者的关系定为：

```
仓库持有规范正文（policy_id@policy_version）
外部 route_policy_ref 是对它的引证，须解析到 search_space_admission_route_policy@0.1.0
```

WP2B 契约的 `VAL-T07` 已经要求「每条 admission 引用的 `route_policy_ref` 与
`BLOCK-02` 冻结的 policy 一致」，本设计与之吻合。

**并且仓库仍然不为任何 territory 计算路由。** `repository_computes_routes:
false`，`src/` 中不含任何路由求值器（有测试断言
`search_space_admission.py` 中不出现 `def resolve`／`def route(`／`def derive`／
`ROUTE_RULES`）。测试里的求值器只对**假设的状态元组**应用规则表以证明表本身的
性质，从不接触任何 admission 或 territory 实例。

## 三、规则表：7 条，按优先级

| # | 规则 | 路由 | 条件 |
|---|---|---|---|
| 1 | `OUT-01` | `OUT_OF_MANDATE` | `clinical_value_exists` 不成立 |
| 2 | `OUT-02` | `OUT_OF_MANDATE` | 窗口已关 **且** 无人接手 |
| 3 | `PARTNER-01` | `PARTNER_ONLY` | 位置已锁，但价值真实且有合作方 |
| 4 | `OUT-03` | `OUT_OF_MANDATE` | 位置已锁 **且** 无人接手 |
| 5 | `PARTNER-02` | `PARTNER_ONLY` | 无非对称优势，但价值真实且有合作方 |
| 6 | `ACTIVE-01` | `ACTIVE_SEARCH` | **八项全部 `SATISFIED`** |
| 7 | `WATCH-01` | `WATCHLIST` | catch-all |

第 3 条是 `HER2`／`TROP2` 那类成熟热门靶点的归宿——**「进入门槛高」，不是科学
失败**。规则上标了 `not_a_scientific_kill: true`。

`ACTIVE_SEARCH` 是唯一会消耗后续主动搜索资源的路由，因此要求**八项全部正向**
——不接受「没有反证」。（初版只要求四项，第一轮审核后收紧，见第十节。）

## 四、`UNKNOWN` 的处理：不判死刑，也不放行

- `UNKNOWN` 不是失败，永不自动转 `UNSATISFIED`。
- **`UNKNOWN` 永远不产生 `OUT_OF_MANDATE`。** 全部 `OUT` 规则只 key 在
  `UNSATISFIED` 上。
- `UNKNOWN` 阻断 `ACTIVE_SEARCH`。
- **八项全 `UNKNOWN` → `WATCHLIST`。**

最后一条是本文件的核心对称性：把全未知判成 `OUT_OF_MANDATE` 会是「不知道所以
放弃」——与 `SponsorFitAssessment` 第一轮被否掉的「没有反证所以推进」是**同一个
错误的镜像**。

## 五、规则表的完备性与确定性做了枚举证明

测试枚举全部 `3^8 = 6561` 种状态组合，逐一证明：

- 表是**完备的**（每种组合都能解析）与**确定的**（first-match-wins）；
- 任何 `OUT_OF_MANDATE` 结果都伴随至少一个 `UNSATISFIED`；
- 任何 `ACTIVE_SEARCH` 结果都伴随**八项** `SATISFIED`；
- 任何 `PARTNER_ONLY` 结果都伴随 `plausible_buyer_partner_map = SATISFIED`
  ——否则这个路由名没有依据；
- 四种路由**全部可达**。

实际分布（供审核方核对，非达标要求）：

```
WATCHLIST       3158  48.13%
OUT_OF_MANDATE  2997  45.68%   其中 OUT-01 占 2187
PARTNER_ONLY     405   6.17%
ACTIVE_SEARCH      1   0.02%
```

**`ACTIVE_SEARCH` 现在恰好只有 1 种组合可达**——八项全 `SATISFIED`。这是收紧后
的直接结果，有专门测试断言。数字看起来极端，但它衡量的是「状态组合空间」而不是
「真实 territory 的分布」：八个条件都只是 territory 级的初步可行性，一片真正值得
主动搜索的水域本来就应该八项都能说清。

## 六、变异检验，两处首轮逃逸

| 变异 | 结果 |
|---|---|
| 把 `OUT-02` 的条件由 `UNSATISFIED` 改为 `UNKNOWN` | 首轮 **`OK`** |
| 把 `ACTIVE-01` 削弱为只要一项 | `FAILED (failures=1)` |
| `PARTNER_ONLY` 不要求 partner map | `FAILED (failures=1)` |
| 去掉 catch-all | `FAILED (failures=7)` |
| 改掉一个条件的 id | `FAILED (failures=1)` |
| 把某触发器的 `affects` 改指他项 | 首轮 **`OK`** |

**两处首轮逃逸都是我的测试写弱了，不是变异无效：**

1. `test_unknown_never_produces_out_of_mandate` 只断言「结果为 OUT 时元组里
   存在某个 `UNSATISFIED`」。规则改 key 在 `UNKNOWN` 上后，仍可由元组里**无关的**
   另一个负项满足该断言。已补
   `test_no_out_of_mandate_rule_keys_on_unknown`：**每条 OUT 规则的 `when` 里
   所有值必须是 `UNSATISFIED`**——这才是真正想要的不变量。
2. `test_every_criterion_can_be_reopened_by_some_trigger` 因为 `RT-07` 的
   `affects: all` 而**恒真**，属重言测试。已改为只统计具体触发器，`RT-07`
   单独断言存在。

两条重跑后均 `FAILED (failures=1)`。六项回滚后 `diff -q` 均无差异。

## 七、本 PR 不做什么

不授权任何运行（`BLOCK-01` 仍未清）；不产出任何 territory；不含任何疾病内容；
不修改 `SearchSpaceAdmission` 合同或任何既有 schema；不在 `src/` 增加任何路由
求值器；不执行 Gate；不生成 target 或 wedge；不评价任何科学证据。

**四种路由没有一种是科学 KILL**，`boundaries` 段逐条写死并有测试断言。

## 八、验证

```
Ran 538 tests  OK              （合并前 508，净增 30；本文件 30）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
YAML 解析后全文件扫描              无截断
```

## 九、后续顺序

1. 本 PR `APPROVE` 并合并 —— **`BLOCK-02` 清除**。
2. **`BLOCK-01` 仍未清**：需要人类负责人提供 Stelligen 当前事实，才能冻结
   `DevelopmentSponsorProfile` 实例。缺的是文档未写、只有负责人知道的几项：
   资本与时间边界分档、患者样本与模型的实际清单与自有／合作划分、
   可承担的 active program 数量、风险容忍度、地域范围、IP 策略。
3. 两个 blocker 都清除后，另开极小 authorization PR 把 `authorises_run` 转
   `true`、`blocked_by` 清空（形态同 PR #66）。
4. 然后才执行 CRC Territory Map（外部运行）→ 结果 PR。

## 十、第一轮审核裁决与修订（`REQUEST_CHANGES`，一条阻断，接受）

### 阻断：八个条件里有四个管不住唯一会花钱的路由

审核方指出，policy 声明了八个准入条件，`ACTIVE-01` 却只要求其中四项。因此下面
这种组合在初版中会命中 `ACTIVE_SEARCH`：

```text
clinical_value_exists               SATISFIED
competitive_position_not_locked     SATISFIED
asymmetric_evidence_advantage       SATISFIED
key_uncertainty_addressable         SATISFIED
differentiation_visible_preclinical UNSATISFIED
defensible_ip_path                  UNSATISFIED
plausible_buyer_partner_map         UNSATISFIED
time_window_compatible              SATISFIED
```

——已经明确没有可保护的 IP 路径、没有可见的临床前差异、没有任何合理买家，却仍然
进入主动搜索、消耗 Stelligen 资源。

审核方的判断是对的：后四项**不是「以后再看的商业 Gate」**，它们正是把大药企式
搜索改造成小微 Biotech 搜索的新增内容。否则系统仍然会「科学上有意思 + 我能做
实验 → ACTIVE」，做到后面才发现没 IP、没买家、差异只能靠三期证明——**那就是旧
架构的问题原样搬了过来**。这也正是 Search-Space Admission 被放在 target
generation 之前的理由。**阻断成立，接受。**

### 修订

`ACTIVE-01` 改为要求**八项全部 `SATISFIED`**。审核方同时否掉了较松的变体
（后四项只要求 `!= UNSATISFIED`），理由是那会重新引入「`UNKNOWN` 不阻断
`ACTIVE`」，与本文件自己写的 `UNKNOWN` 语义冲突。接受该理由，采用八项全 SAT。

合同中并记明这不是苛刻门槛：八项都只是 territory 级初步可行性——IP 不是完整
FTO，只要求存在可主张的入口；buyer 不是已签 BD，只要求存在合理接手方类型；
differentiation 不是证明临床优效，只要求能在临床前展示；time fit 不是预测未来，
只要求当前已知的竞争时钟没有明显关窗。

`unknown_handling` 增补 `unknown_blocks_active_search_scope: all_eight_criteria`。

### 测试

`test_active_search_always_rests_on_four_affirmative_criteria` 升级为
`..._requires_all_eight_affirmative_criteria`，并新增四条：

- `test_exactly_one_status_tuple_reaches_active_search`
- `test_a_declared_negative_on_any_criterion_blocks_active_search`（遍历八项）
- `test_an_unsatisfied_commercial_criterion_is_named_explicitly`（四项**字面
  列名**，避免参数化测试随常量自我收缩——这是我在 PR #72、#77 上各犯过一次的错）
- `test_any_single_unknown_falls_through_to_the_watchlist`

### 第二轮变异检验

| 变异 | 结果 |
|---|---|
| 从 `ACTIVE-01` 去掉 `defensible_ip_path` | `FAILED (failures=5)` |
| 去掉 `plausible_buyer_partner_map` | `FAILED (failures=5)` |
| 去掉 `differentiation_visible_preclinical` | `FAILED (failures=5)` |
| **退回初版的四项** | `FAILED (failures=14)` |
| 让 `ACTIVE` 接受 IP 为 `UNKNOWN` | `FAILED (failures=4)` |

五项回滚后 `diff -q` 均无差异。

### 范围未扩大

未改 OUT／PARTNER 语义、blocker 状态、执行授权、`SearchSpaceAdmission` schema，
未加任何疾病内容。
