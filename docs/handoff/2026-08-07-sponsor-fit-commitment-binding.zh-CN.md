# Handoff：Sponsor Fit → Program Commitment 绑定

- 日期：`2026-08-07`
- 任务分支：`task_20260807_sponsor-fit-commitment-binding`
- 基线：`main` @ `cb5c7f1`
- 交付物类型：**契约绑定（无新语义、无新决策逻辑、无执行）**
- 架构变更：`BREAKING_CONTRACT_CHANGE`（`ProgramCommitmentReview` 新增必填字段）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、为什么先做这个，而不是先做 WP2

PR #75 合并后，`SponsorFitAssessment@0.1.0` 存在但**没有任何消费者**。如果直接
进入 WP2 开始产生 territory、wedge、candidate，链路很容易变成：

```text
Territory → Wedge → Candidate → T Gates
```

Sponsor Fit 又被绕过去了——这正是本仓库反复出现并反复登记的那类问题：
**合同存在、运行时无人消费**（`authorises_extraction_run_count`、Phase 1／2、
以及 PR #72 之前的 Phase 3／4 都是同一类）。

本 PR 只做一件事，把这个洞补上。

## 二、改了什么

`ProgramCommitmentReview` 新增一个**无默认值**的必填字段：

```python
sponsor_fit_assessment_ref: str
```

字段位置在 `buyer_map_ref` 与 `value_inflection_plan_ref` 之间——两个前置工件
放在一起，且**夹在必填字段中间**，因此给它加默认值会在类定义阶段直接
`TypeError`，比任何测试更早失败（与 PR #72 的字段排布同理）。

校验沿用既有的 `_require_external_ref`：必须非空、必须 `external:` 前缀。

新增两条 invariant：

```yaml
- program_commitment_cannot_exist_without_sponsor_fit
- sponsor_fit_assessment_ref_is_opaque_and_never_dereferenced_here
```

第二条很重要：**仓库只持有引用，不解引用、不重新裁定它推荐的路线、不生成它。**
有测试用 AST 断言 `program_commitment_review.py` 的 import 集合恰为
`{__future__, dataclasses, enum, typing}`——绑定没有把 `SponsorFitAssessment`
拉进消费者。

## 三、闭环现状

```text
Scientific Opportunity (T12)
      ↓
SponsorFitAssessment@0.1.0
      ↓ required ref          ← 本 PR
ProgramCommitmentReview@0.2.0
      ↓ required ref          ← PR #72
BinderAdcRouteRequest@0.2.0
      ↓
Binder / de novo route
```

审核方提出的那个检验问题——**没有 `SponsorFitAssessment` 还能不能绕路进入
`ProgramCommitment`？**——现在的答案是不能：缺该字段时 Python 层面无法构造。
有一条测试逐个 decision 验证，**包括 `STOP_FOR_SPONSOR` 与 `MONITOR`**：
即使是不承诺的结论，也必须写明它基于哪份评估。

## 四、版本处理

新增必填字段是 breaking change，因此 `ProgramCommitmentReview@0.1.0` →
`@0.2.0`，YAML 的 `version` 同步升到 `0.2.0`，并加 `version_change_reason`。

**同时更新了所有指名该版本的引用**，否则会复制架构文档 `v4-draft` §6.2 已登记的
`GateInputEnvelope` `2.0.0`/`2.1.0` 漂移问题：

| 文件 | 改动 |
|---|---|
| `src/contracts/binder_adc_routes.yaml` | `bound_contracts` 中的版本串 |
| `src/capabilities/binder_adc_routes.py` | 模块 docstring |
| `src/contracts/sponsor_fit_assessment.{py,yaml}` | `consumed_by`、docstring |
| `src/contracts/README.md`、`genmodules/README.md` | 说明文字 |
| `docs/architecture/program-commitment-review.zh-CN.md` | 版本行 |
| `tests/test_phase5_binder_adc_routes.py` | `bound_contracts` 断言 |

`sponsor_fit_assessment.yaml` 的 `binding_status` 由 `not_bound` 改为 `bound`
——该字段的作用就是如实反映绑定状态，绑定后不改它就是留下一处假话。审核方要求
「不要碰 `SponsorFitAssessment`」，此处只改这一个状态字段与 `consumed_by` 的
版本串，**未触碰它的任何语义、门槛或枚举**。

## 五、刻意未改的一处

**架构说明文档 `v4-draft` 第 253 行仍写 `ProgramCommitmentReview@0.1.0`。**

不改的理由：该文档在第 0 节声明了自己的仓库基线 `main@4d895d7` 与版本状态，
改动正文会让它与自己声明的基线不符。按其第 17 节规则，实质更新应升到
`v5-draft` 另立 PR。**此处登记，不在本 PR 修。**

同理未回写任何历史 handoff、审核记录或 worklog。

## 六、变异检验

| 变异 | 结果 |
|---|---|
| 给绑定字段加默认值 | 类定义阶段 `TypeError`，模块无法载入 |
| 把它从校验列表中删除 | `FAILED (failures=3)` |
| 整个删除该字段 | `FAILED (errors=13)` |
| 删除 `program_commitment_cannot_exist_without_sponsor_fit` invariant | `FAILED (failures=1)` |

四项回滚后 `diff -q` 均无差异。

## 七、本 PR 不做什么

不修改 `SponsorFitAssessment` 的语义、门槛或枚举；不修改
`ProgramCommitmentReview` 的六个决定、承诺状态、下游状态或任何既有判定逻辑；
不修改 45 个 Gate、T12、lifecycle、core objects；不解引用或重新裁定任何外部
实例；不生成任何实例；不执行 Gate、EVGAP、模型或数据采集；不推进 WP2..WP6；
不更新架构说明文档。

## 八、验证

```
Ran 448 tests  OK              （合并前 442，净增 6）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
```

无数据、cache、result、database、model weights 或实例进入仓库。

## 九、后续顺序

1. 本 PR `APPROVE` 并合并——**sponsor-relative 链路闭环完成**。
2. **WP2A：CRC Opportunity Territory Schema。** 纯 schema，不含任何 CRC 内容：
   字段、合同、状态机、`ACTIVE`／`WATCH`／`PARTNER_ONLY`／`OUT`。
3. **WP2B：CRC territories 内容。** MSS 后线、HER2+、KRAS G12C、肝转移、腹膜
   转移、drug-tolerant state 等。**按硬边界，这部分是数据与知识内容，必须在
   仓库外产出，再走结果 PR。**
4. WP3 Program Wedge Generator → WP4 Target Generation 与三重预筛 →
   WP5 T0–T12 分批验证 → WP6 Commitment 与 Value-Inflection。

绑定完成后仍**没有消费者**的 sponsor-relative 合同还剩三份：
`DevelopmentSponsorProfile`、`ProgramThesis`、`SearchSpaceAdmission`。
其中 `SearchSpaceAdmission` 的天然消费者正是 WP2 的 territory 路由，
届时一并处理。
