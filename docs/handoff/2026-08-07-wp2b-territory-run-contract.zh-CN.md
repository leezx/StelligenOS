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

每个 territory 的 `sponsor_evidence_advantage_ref` 都要指向它。仓库内目前只有
`DevelopmentSponsorProfile@0.1.0` 的**合同形状**（PR #67），没有任何实例。

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
| `scope` | 疾病范围、territory 数量区间 15–30、粒度可判定规则 |
| `relationship_to_legacy_level_01` | 不读、不引用、不复活 369-pair 轴；旧轴保持冻结且不删除 |
| `source_policy` | Tier 1 原始公开来源准入、Tier 2 派生库全面禁止、两个被隔离运行仍然 barred |
| `evidence_standards` | 五个字段组各自的来源要求与 `UNKNOWN`／空值语义 |
| `output` | 外部产出、符合 PR #77 的 schema、每 territory 必须有 admission、打包与校验规则 |
| `validation_rules` | `VAL-T01`..`VAL-T18` |
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

## 五、两处刻意的设计

**`expected_active_band` 4–8 不是达标要求。** 它标注为
`is_a_target: false` / `is_a_reconciliation_reference: true`，只用于事后对账。
把它写成目标会让路由变成凑数字，而路由应当由 route policy 与实际证据决定。

**`sponsor` 字段组允许 `UNKNOWN`，但规则写死了方向**：优势未知即记未知，
**不得因「看起来我们能做」而记为具有优势**；未知既不转为不具优势，也不转为
具有优势。这与 `SponsorFitAssessment` 的三值处理一致。

## 六、一处执行失误，如实记录

初稿 YAML 无法解析：`VAL-T03` 的规则文本里有未加引号的 `external: `，YAML 把它
读成了嵌套映射。已加引号修正，并对全文件做了一次解析后扫描，确认没有任何字符串
被 `#` 或 `:` 静默截断。

**这与仓库里已登记的三处 YAML 引号缺陷（`v4-draft` 问题 17）是同一类缺陷。**
差别只在这次是在提交前被自己的测试挡下的。

## 七、本 PR 不做什么

不执行任何运行；不产出任何 territory；**不含任何 CRC 内容**（有测试断言文件中
不出现 `MSS`／`HER2`／`TROP2`／`KRAS`／`BRAF`／`G12C`／`MSI`，也不含
`territories:` 键）；不修改任何既有合同、schema、Gate、lifecycle 或 core objects；
不解除 `EVGAP-01`／`EVGAP-02`；不裁定 `GAP-P07`；不复活或修改 369-pair 轴。

## 八、验证

```
Ran 500 tests  OK              （合并前 468，净增 32）
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
