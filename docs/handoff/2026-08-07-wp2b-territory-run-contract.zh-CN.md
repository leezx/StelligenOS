# Handoff：WP2B 运行契约（contract-only，未授权执行）

- 日期：`2026-08-07`
- 任务分支：`task_20260807_wp2b-territory-run-contract`
- 基线：`main` @ `fbc4f36`
- 交付物类型：**运行契约（无内容、无数据、未授权执行）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、为什么是契约而不是运行

WP2B 是**外部知识生产**。按 2026-08-04 对 PR #53／#54 的隔离裁决，顺序必须是：

> contract-only PR 预先冻结范围、语义、证据标准与输出验证 → `APPROVE` → 再运行。

那次裁决的代价是两个运行被整体隔离。本文件就是 WP2B 的那个前置契约，
与 PR #57 之于 Level 01 同一角色。

**本契约获批不等于可以开跑。** `approval_does_not_authorise_execution: true`，
且有测试断言 `authorises_run: false`、`authorises_run_count: 0`。

## 二、两个 blocker

### `BLOCK-01`：`DevelopmentSponsorProfile` 实例不存在

它是本运行的**上游输入**——territory-specific 优势评估没有基线可依。仓库内目前
只有 `DevelopmentSponsorProfile@0.1.0` 的**合同形状**（PR #67），没有任何实例。

**注意 profile 不是优势本身**，见第十节第二条修订。

按执行策略 Stage 0，该 profile 必须写**当前事实**而非理想中的未来公司：当前
优势、可通过合作获得的能力、当前不可独立承担的能力、默认交易终点。

**这份事实只有人类负责人能提供。**

### `BLOCK-02`：`SearchSpaceAdmission` 的 `route_policy_ref` 不存在

每个 territory 要指向一份 `SearchSpaceAdmission` 实例说明它被如何路由，而该合同
要求一个外部、可审计的 `route_policy_ref`。该 policy 目前不存在。

没有它，八个条件到四种路由的映射就没有依据，
`ACTIVE_SEARCH`／`WATCHLIST`／`PARTNER_ONLY`／`OUT_OF_MANDATE` 会退化为无据判断。

该 policy 必须定义四件事：八个条件各自的判定标准、条件状态组合到路由的映射、
`UNKNOWN` 的处理方式、重评估触发条件。

## 三、契约冻结了什么

| 段 | 内容 |
|---|---|
| `scope` | 疾病范围、territory 数量参考区间 15–30（**非判据**）、粒度可判定规则 |
| `relationship_to_legacy_level_01` | 不读、不引用、不复活 369-pair 轴；旧轴保持冻结且不删除 |
| `source_policy` | Tier 1 原始公开来源准入、Tier 2 派生库全面禁止、两个被隔离运行仍然 barred |
| `evidence_standards` | 六个字段组各自的来源要求与 `UNKNOWN`／空值语义 |
| `output` | 外部产出、符合 PR #77 的 schema、每 territory 必须有 admission、打包与校验规则 |
| `validation_rules` | `VAL-T01`..`VAL-T21` |
| `not_authorised` | 十条，第一条就是「执行本运行」 |

## 四、把已经付过代价的教训写进了校验规则

这批规则不是凭空拟的，每一条都对应本项目已经踩过的一个坑：

| 规则 | 来自 |
|---|---|
| `VAL-T02` territory_id 全局唯一 | `SRCADM-01` 事后才去找的重复键 |
| `VAL-T08` 不出现任何路由状态字段 | PR #77 的镜像双真源阻断 |
| `VAL-T09`／`VAL-T10` 无 target／gene／pair／score／rank | territory 不是候选 |
| `VAL-T11` 两个被隔离运行记为 barred 且 `used=false` | PR #53／#54 裁决 |
| `VAL-T12` 未读取 9×41×369 轴 | 本工作包存在的理由 |
| `VAL-T14` 空竞争字段须与「未调查」区分 | 空值不等于已核实为空 |
| `VAL-T16` 无 Tier 2 派生库 | PR #59「派生库不能自声明纳入」裁决 |
| `output.packaging_rules` | PR #60 第二轮「交付包版本不匹配」裁决 |

`known_target_biology_refs` 的约束也写进了 `evidence_standards`：它是**背景情报，
不是 target candidate**，本运行不得据此产出靶点，WP3 也不得把它当作候选生成的
权威——直接承接 PR #77 审核方的非阻断意见。

## 五、三处刻意的设计

**两个数量区间都不是达标要求。** `territory_count_band` 15–30 与
`expected_active_band` 4–8 均标注 `is_a_target: false` /
`is_a_reconciliation_reference: true`，只用于事后对账。把任一写成目标，都会让
知识生产去迎合漏斗形状——那正是本工作包要消灭的东西。（前者在第一轮审核后由
硬判据改为参考，见第十节。）

**`sponsor_fit_context` 允许 `UNKNOWN`，但规则写死了方向**：优势未知即记未知，
**不得因「看起来我们能做」而记为具有优势**；未知既不转为不具优势，也不转为
具有优势。这与 `SponsorFitAssessment` 的三值处理一致。

**`sponsor_evidence_advantage_ref` 必须逐 territory 各不相同。** 见第十节
第二条——共用一个引用等于没有证明任何 territory 存在优势。

## 六、一处执行失误，如实记录

初稿 YAML 无法解析：`VAL-T03` 的规则文本里有未加引号的 `external: `，YAML 把它
读成了嵌套映射。已加引号修正，并对全文件做了一次解析后扫描，确认没有任何字符串
被 `#` 或 `:` 静默截断。

**这与仓库里已登记的三处 YAML 引号缺陷（`v4-draft` 问题 17）是同一类缺陷。**
差别只在这次是在提交前被自己的测试挡下的。

## 七、本 PR 不做什么

不执行任何运行；不产出任何 territory；**不含任何 CRC 内容**（有测试断言文件中
不出现 `MSS`／`HER2`／`TROP2`／`KRAS`／`BRAF`／`G12C`／`MSI`，且解析后不存在
字面为 `territories` 的键）；不修改任何既有合同、schema、Gate、lifecycle 或 core objects；
不解除 `EVGAP-01`／`EVGAP-02`；不裁定 `GAP-P07`；不复活或修改 369-pair 轴。

## 八、验证

```
Ran 508 tests  OK              （合并前 468，净增 40；本文件 40）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
YAML 解析后全文件扫描              无截断
```

## 九、后续顺序

1. 本 PR `APPROVE` 并合并。**合并后仍不能开跑。**
2. **清除 `BLOCK-01`**：人类负责人提供 Stelligen 当前事实 → 冻结
   `DevelopmentSponsorProfile` 实例（外部）→ 审核接受。
3. **清除 `BLOCK-02`**：冻结 route policy → 审核接受。
4. 两个 blocker 都清除后，另开一个极小的 PR 把 `authorises_run` 转为 `true`、
   `blocked_by` 清空——**与 `SRCADM-01` 解除 `EVGAP-01` 的 binding PR（#66）同
   形态**，不在本 PR 预先写好。
5. 执行运行（外部）→ 结果 PR → 获批后进入 WP3。

建议先做第 2 步：profile 一变，所有 territory 的 sponsor advantage 判定都要重做。

## 十、第一轮审核裁决与修订（`REQUEST_CHANGES`，两条，均接受）

### 第一条：`territory_count_band` 不该是硬判据

审核方指出，初版把 15–30 写成 `VAL-T01` 的硬通过条件，与同一文件对
`expected_active_band` 的处理**自相矛盾**：4–8 被正确标注为只作对账，而 15–30
却成了 validity criterion。

后果很具体：若严格梳理后只有 12 个可区分、可判定的 territory，系统会为了通过
校验而硬拆出 3 个；若有 34 个合理 territory，又会被区间逼着合并。**先规定漏斗
形状、再让知识生产去迎合漏斗**——这正是本工作包存在的理由所反对的。接受。

修订：`territory_count_band` 加 `is_a_target: false`、
`is_a_reconciliation_reference: true`、`out_of_band_is_not_a_failure: true`、
`out_of_band_requires_reconciliation_note: true`；`VAL-T01` 改为「报告实际数量；
落在参考区间之外不构成失败，但须给出 reconciliation note」。

### 第二条：sponsor 优势的证据关系写错了

**这条是执行者的语义错误，不是措辞问题。** 初版写「每个 territory 的
`sponsor_evidence_advantage_ref` 都要指向 `DevelopmentSponsorProfile` 实例」。

审核方指出这不成立：profile 描述的是发起方的**稳定基线**（拥有什么能力、能接触
什么数据、缺什么能力、最大自研阶段、默认交易节点），而「在某个具体 territory
里是否存在非对称优势」是 **territory-relative 判断**。同一份 profile 对
oncofetal territory 可能优势很强，对另一片水域可能与所有人没有区别。

若 20 个 territory 全部指向同一份 profile，该字段就只是**「公司简介引用」**，
并未证明任何 territory 中存在非对称优势。接受。

修订：

1. 新增 `sponsor_evidence_advantage_semantics` 段单列该语义，写明推导链
   `profile + 该 territory 可触及的数据/模型/know-how + 该 territory 的证据要求
   → territory-specific 评估 → ref`，并把
   `ref_must_not_point_directly_at_the_profile` 与
   `ref_must_not_be_shared_across_territories` 写死。
2. `BLOCK-01` 的角色改为
   `upstream_input_not_the_advantage_evidence_itself`。
3. 拆开原 `sponsor` 字段组：`sponsor_fit_context`（`sponsor_evidence_advantage_ref`）
   与 `timing`（`window_closure_risk_ref`）。审核方指出后者**不能主要来自
   profile**——它来自 leading assets、competitor stage、expected readouts、监管
   时间、SOC 演进，加上发起方执行时间跨度；profile 最多提供后半段。两组均标
   `profile_alone_is_insufficient: true`。`timing` 并记明它是
   `SearchSpaceAdmission` 的 `time_fit` 的证据来源。
4. 新增 `VAL-T19`／`VAL-T20`／`VAL-T21` 给这套语义装上执行层面的牙齿，并把
   `sponsor_evidence_advantage.json` 加入必需产物。

**未新增正式评估合同**——审核方说除非必要否则不加；该评估先作为外部证据工件，
由运行产出。语义在此冻结，形态留待后续。

### 未处理的非阻断意见

审核方指出 `VAL-T13`（每个非空字段至少一条 source_ref）很严格，但需确保
`source_manifest.json` 真正支持「字段 → claim/evidence → source」的映射，而不是
只列一堆全局 sources；否则结果 PR 时可能出现「有 manifest 但无法证明哪个来源
支持哪个字段」。审核方判断可留到 execution authorization 或 result validator
再具体化。**因此本轮未改，登记备查。**

### 第二轮变异检验

| 变异 | 结果 |
|---|---|
| 把数量区间改回硬目标 | `FAILED (failures=1)` |
| 允许 ref 直接指向 profile | `FAILED (failures=1)` |
| 允许多个 territory 共用同一 ref | `FAILED (failures=1)` |
| 把 sponsor 与 timing 两组合并回去 | `FAILED (errors=1)` |
| 删除 `VAL-T20` | `FAILED (failures=1, errors=1)` |

五项回滚后 `diff -q` 均无差异。

### 一处测试自身的缺陷，顺带修正

边界测试原用 `assertNotIn("territories:", text)` 检查契约是否夹带 territory
内容。新增的 `ref_must_not_be_shared_across_territories:` 让它**误报**。已改为
结构化检查——递归遍历解析后的键名，断言不存在字面为 `territories` 的键。子串
匹配会被恰好以该词结尾的键绊倒。
