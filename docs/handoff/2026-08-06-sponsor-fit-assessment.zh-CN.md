# Handoff：Work Package 1 补齐 —— `SponsorFitAssessment@0.1.0`

- 日期：`2026-08-06`
- 任务分支：`task_20260806_sponsor-fit-assessment`
- 基线：`main` @ `4a5c673`
- 交付物类型：**合同形状（无实例、无数据、无执行）**
- 架构变更：`NEW_CONTRACT_NO_EXISTING_CONTRACT_MODIFIED`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、依据与定位

依据 `Zhixins-KB/2.Biotech/Asset-Generation-OS-architecture.md` 的
「小微 Biotech 后的执行策略」一节，按其第十节「分布式执行建议」的六个工作包
顺序执行。**本 PR 是 Work Package 1。**

### 核查结果：WP1 只差这一份

WP1 原定交付四份合同。核查当前 `main`：

| WP1 交付 | 仓库现状 |
|---|---|
| `DevelopmentSponsorProfile@0.1.0` | ✅ 已合并（PR #67） |
| `ProgramThesis@0.1.0` | ✅ 已合并（PR #67） |
| `SponsorFitAssessment@0.1.0` | ❌ **缺失** |
| `ValueInflectionPlan@0.1.0` | ✅ 已合并（Phase 4） |

`grep -rn "SponsorFitAssessment\|sponsor_fit"` 在 `src/` 与 `tests/` 中零命中；
仅有的三处出现都在 Phase 1 的 handoff、审核记录与 worklog 里，且都是
「**本 PR 不实现 SponsorFitAssessment**」这类排除性表述。

因此本 PR 只做一件事：补齐这一份，使 WP1 完整。

### 对应源文档的哪一部分

Decision 3（Sponsor Fit Qualification）与 Stage 6（正式 Sponsor Fit
Assessment）。

## 二、与 `ProgramCommitmentReview@0.1.0` 的分工

源文档把 Decision 3／Stage 6 与 Stage 8（Program Commitment）当作**两个不同
阶段**，本 PR 保持这个区分：

| | `SponsorFitAssessment` | `ProgramCommitmentReview` |
|---|---|---|
| 回答 | 是否适配、走哪条路线 | 是否承诺资本、投到哪个边界 |
| 性质 | **建议**，带证据 | **授权** |

以 `route_is_a_recommendation_not_an_authorisation` 显式登记。数据类里
**没有** `commitment_status` 与 `downstream_status` 两个字段，有测试断言。

## 三、三条让这个检查点真正起作用的规则

**1. 不使用总分。** 源文档原话是「这里不要用总分」。合同以
`aggregate_score: forbidden` 登记，并有测试断言数据类中不存在任何形如
`*_score` 的字段。理由不是风格：总分会让「能力齐备」补偿「没有非对称优势」，
而那正是这个检查点存在的目的。

**2. 缺少非对称证据优势通常不能 `SELF_DEVELOP`。** 源文档写的是「**通常**」。
本合同把这个「通常」编码为**显式外部豁免**而非沉默：`evidence_advantage` 非
`SATISFIED` 时若仍走 `SELF_DEVELOP`，必须提供
`asymmetric_advantage_waiver_ref`（外部人类决定）；该豁免只对 `SELF_DEVELOP`
有效，挂到其他路线上会被拒绝。

**这是本 PR 唯一一处超出源文档字面的设计判断，请审核方裁定。** 备选是把它写成
硬禁止，但那会把「通常」读成「一律」；写成注释则等于没有约束。

**3. 需要三期才能证明的差异不算可见差异。** `differentiation_requires_phase_3`
为真时，`differentiation_visibility` 不得记为 `SATISFIED`。这是源文档「无效
差异」清单里最可机器检查的一条。

## 四、`UNKNOWN` 与 `UNSATISFIED` 严格分开

- `UNKNOWN` 是信息缺失，不得自动转为 `UNSATISFIED` 或 KILL，**单独不阻断任何
  路线**（有专门测试）。
- `UNSATISFIED` 不能支撑 asset-directed 路线（`SELF_DEVELOP`／`CO_DEVELOP`），
  但仍可走 `PARTNER_NOW`／`DATA_PACKAGE_ONLY`／`MONITOR`／`STOP_FOR_SPONSOR`
  ——`STOP_FOR_SPONSOR` 必须始终可达，它**不是科学 KILL**。

## 五、路线枚举复用 Phase 3 词汇

源文档把 Decision 3 输出写作 `PARTNER_BEFORE_CONJUGATION` 与 `WATCH`。那是
自然语言描述；Phase 3 已把它们分别收敛为 `PARTNER_NOW` 与 `MONITOR` 以避免
机器 ID 漂移。本合同复用同一套六值词汇，使「建议」与「消费该建议的承诺」可直接
比对。这一决定连同理由写进了 YAML 的 `route_vocabulary_note`。

## 六、变异检验

| 变异 | 结果 |
|---|---|
| 把 `UNKNOWN` 当作 `UNSATISFIED` 处理 | `FAILED (errors=2)` |
| 允许三期才可证明的差异记为 `SATISFIED` | `FAILED (failures=1)` |
| 去掉「七问各答一次」检查 | `FAILED (failures=2)` |
| 允许豁免挂到任意路线 | `FAILED (failures=1)` |
| 把 `MONITOR` 加入 asset-directed 路线 | `FAILED (errors=1)` |
| 去掉 `SELF_DEVELOP` 的豁免要求 | 首轮 **`OK`** |

最后一项首轮通过，经查是**无效变异而非覆盖缺失**：该变异把 `if waiver is None:
raise` 改成 `pass`，但下一行 `_require_external_ref(None, ...)` 仍会因 `None`
不是字符串而抛 `ValueError`——规则从未被真正关闭。改用真正关闭该规则的变异
（把 `if statuses["evidence_advantage"] is not SATISFIED:` 改成 `if False:`）
重跑，得 `FAILED (failures=2)`。六项回滚后 `diff -q` 均无差异。

## 七、本 PR 不做什么

不修改任何已有合同（`ProgramCommitmentReview` 一个字未动）；不修改 45 个
Gate、T12、lifecycle、core objects、`ClinicalHypothesis` 或 `TargetHypothesis`；
不绑定到任何入口；不生成任何实例；不执行 Gate、EVGAP、模型或数据采集；
不推进 WP2..WP6；不修改架构说明文档 `v4-draft`。

## 八、验证

```
Ran 436 tests  OK              （合并前 413，净增 23）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
```

无数据、cache、result、database、model weights 或实例进入仓库。

## 九、尚未绑定，且这次不绑

`ProgramCommitmentReview@0.1.0` 目前不要求 `sponsor_fit_assessment_ref`。给一份
已冻结并合并的合同增加必填字段属 breaking change，应另立 binding PR，形态与
PR #72 对 `BinderAdcRouteRequest` 的绑定相同。

在那之前，本合同与 Phase 1／Phase 2 一样**没有消费者**——已在
`downstream_relationship.binding_status: not_bound` 显式登记，并有测试断言，
避免重演「文档声称硬控制、代码无人消费」那类问题。

## 十、后续顺序

1. 本 PR `APPROVE` 并合并 —— **WP1 完成**。
2. **WP2：CRC Opportunity Territory Map。** 注意它天然分两半：territory schema
   属仓库内合同；而 territories 本身（竞争格局、readout 日历、数据可得性）是
   内容与数据，按硬边界必须在仓库外产出，再走结果 PR。建议先只做 schema。
3. WP3 Program Wedge Generator → WP4 Target Generation 与三重预筛 →
   WP5 T0–T12 分批验证 → WP6 Commitment 与 Value-Inflection。
4. 源文档明确指出：**下一步不再是继续补全 369 个 pairs。** 现有 `EVGAP-01`
   抽取授权与 `GAP-P07` 裁定仍然开着，但它们属于旧管线，不因本 PR 变化。
