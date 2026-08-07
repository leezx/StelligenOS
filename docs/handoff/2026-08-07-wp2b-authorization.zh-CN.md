# Handoff：WP2B 执行授权（`BLOCK-02` 已清；`BLOCK-01` 待人工批准）

- 日期：`2026-08-07`
- 任务分支：`task_20260807_wp2b-authorization`
- 基线：`main` @ `0c030c2`
- 交付物类型：**授权绑定（无新语义、无内容、**未授权执行**）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本 PR 当前做的事（第一轮审核后已收回授权）

1. 记录 `BLOCK-02` 已清——`search_space_admission_route_policy@0.1.0`
   已由 PR #79 合并（`0c030c2`）。
2. 为 `BLOCK-01` 建立**三项合取的清除条件**，并如实记录它**尚未清除**。
3. **保持 `authorises_run: false`、`authorises_run_count: 0`、
   `blocked_by: [BLOCK-01]`。**

初版曾把 `BLOCK-01` 记为已清并开启授权，第一轮审核判定该跳跃不成立，
已收回。详见第八节。

**不改任何语义、范围、来源策略、证据标准或校验规则。**

## 二、`BLOCK-01` 的机器校验证据（**尚不足以清除**）

外部包（**不入仓**）：

```
gen_sponsor_profile_stelligen_20260807T050000Z_frozen
ZIP SHA-256   5f057fde5739a4813114546dc292d20cb260a82a842fd6adeeabfc8efcd016ed
实例 SHA-256  65253e10cb37a5341c34ac5c5105d38c6d044fe99ea4382f0c4e138a206814ed
13,660 bytes，6 个文件
validate_profile.py -> 19/19 MATCH
```

校验脚本直接 import 仓库里冻结的 `DevelopmentSponsorProfile@0.1.0` 构造实例，
形状错会当场失败而不是留到下游。

### 这份 profile 最要紧的一条

> **创始人的科学接触不等于公司可用。**

`accessible_patient_samples` 是**空的**，并带
`empty_list_semantics: INVESTIGATED_AND_CONFIRMED_NONE_SPONSOR_CONTROLLED`
——空表示「查过、确认没有」，不是「没查」。

机构队列、未发表的机构空间／多组学数据集、学术实验室 organoid、机构小鼠与
PDX、以及机构雇佣下产生的发明，全部进 `NOT_YET_CONTROLLED` 登记表，各自写明
转化所需的法律工具（合作协议／SRA／MTA／DUA／正式 IP 裁定）。

校验脚本会扫 `accessible_data` 与 `accessible_models`，命中
`dfci`／`hospital`／`academic`／`institution`／`pdx` 即 FAIL。**这条不靠自觉。**

**为什么这是硬约束而非合规姿态：** 若把机构资源写成公司资产，
`asymmetric_evidence_advantage` 会评为 `SATISFIED`；而按 PR #79 合并的规则表，
它是 `ACTIVE_SEARCH` 必需的八项之一——系统会为一个法律上并不存在的资产投入真实
搜索资源。

### 其余被刻意保守化的字段

- **`capital_envelope` 用四档，不填数字。** 决策规则写的是「问题不是有多少钱，
  而是下一个价值拐点能否在当前边界内跨过去」。六位数以上默认需要外部资本；
  IND-enabling／GLP／GMP／临床完全在自有边界之外。
- **capacity 定 1–2 个 active**，第三个只能是 `DATA_PACKAGE_ONLY` 或
  `PARTNER_ONLY`。文件内写明这比早前规划文档的 1–3 更窄，是有意的。
- **`accessible_data` 只列公开源**，且 summary 中点明：公开数据人人可得，
  **本身不构成非对称优势**。
- **`partnered_capabilities` 标为 `OPERATING_ASSUMPTION` 而非事实**——今天没有
  任何 CRO 或合作方已签约。
- 每个字段都有 `CONFIRMED_CURRENT_FACT`／`OPERATING_ASSUMPTION`／`UNKNOWN` 的
  分类表，**操作假设不得被静默升格为事实**。

## 三、承接 PR #66 的非阻断意见

审核方当时指出 `authorises_extraction_run_count` 没有消费机制，只是声明字段。

本契约写明消费点，但**诚实标注它由流程而非代码强制**：

```yaml
run_count_consumed_by: result_pr
run_count_consumption_is_process_enforced_not_code_enforced: true
```

有测试断言第二个字段为 `true`，注释写着「计数器不得声称仓库并不具备的强制力」。
**这不是把问题解决了，是把问题标注清楚了**——仓库仍然不会自动递减。

`not_authorised` 现有两条相关项：首条「执行本运行——`BLOCK-01` 未清」，
另一条「在 `authorises_run_count` 归零后再次执行本运行」。

## 四、变异检验

见第八节的第二轮结果。测试要求「已清的 blocker 必须写明是什么清的，而不是只翻
一个布尔位」，并且**仅凭机器校验不得清除 `BLOCK-01`**。

## 五、本 PR 不做什么

**不执行运行。** 不产出任何 territory；不含任何 CRC 内容；不改范围、来源策略、
证据标准、校验规则或 `not_authorised` 的其余各条；不改 route policy、
`SponsorFitAssessment`、`SearchSpaceAdmission` 或任何科学 Gate；不解除
`EVGAP-01`／`EVGAP-02`；不裁定 `GAP-P07`；不复活 369-pair 轴；
**不把任何机构资源当作 Stelligen 资产**。

## 六、验证

```
Ran 544 tests  OK              （合并前 538，净增 6）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
外部包 validate_profile.py              19/19 MATCH
```

无数据、cache、result、database、model weights 或实例进入仓库。

## 七、后续顺序

1. **人类负责人审阅完整 profile**（人读摘要 + 逐字段 provenance 表），逐项答复
   此前标出的三处疑问，并明确接受或指出要改的字段。
2. 接受后更新本 PR：`BLOCK-01.cleared: true`、写入 `human_approval_ref`
   （形如 `external:human_approval/stelligen_sponsor_profile_20260807`）与
   `approved_instance_sha256`，再开启 `authorises_run`。
3. 本 PR `APPROVE` 并合并 —— **WP2B 才获得一次执行授权**。
4. 执行 CRC Territory Map（**外部运行**，产物不入仓）。按契约必须产出
   `territory_map.json`、`territories.tsv`、`search_space_admissions.json`、
   `sponsor_evidence_advantage.json`、`source_manifest.json`、`run_report.md`
   与包内可独立运行的 `verify_package.py`，逐文件 SHA-256，整包 SHA-256。
5. 结果 PR：`VAL-T01`..`VAL-T21` 全部校验，并把 `authorises_run_count` 归零。
6. 获批后进入 WP3 Program Wedge Generator。

### 一件后续必须注意的事

profile 一旦改版，按 route policy 的 `RT-03`，所有已路由 territory 的
`asymmetric_evidence_advantage`、`key_uncertainty_addressable` 与
`time_window_compatible` 都要重评估。因此 `NOT_YET_CONTROLLED` 登记表里任何一项
被法律工具转化为公司资源时，**不是改一行，而是升版本并触发重评估**。

## 八、第一轮审核裁决与修订（`REQUEST_CHANGES`，一条，接受）

### 阻断：把「已生成 + 机器校验通过」记成了「已获人工批准」

审核方指出，初版以「人类负责人确认并冻结」为由把 `BLOCK-01` 记为已清，但真正
要求的顺序是：**先出 profile → 停下来把完整内容交人工审核 → 确认后才清
blocker**。而机器能证明的只有：包名存在、SHA-256 长度正确、实例可按
`DevelopmentSponsorProfile@0.1.0` 构造、机构关键词未混入 accessible 字段。

它**证明不了**：capital envelope、time horizon、1–2 active programs、最大自研
阶段、transaction stage、risk tolerance、IP strategy，以及
`accessible_patient_samples = none sponsor-controlled` 的具体边界，是否为人类
负责人认可的经营事实。**而这些恰恰是 `BLOCK-01` 的主体。**

**执行者的错在于**：人类负责人确实回了「确认」，但执行者此前明确标出过三处需要
逐项答复的疑问（`partnered_capabilities` 的分类、`company_stage`、
`risk_tolerance`／`geographic_scope`），一个笼统的「确认」并未逐项解决它们；
且全程没有产生任何可引用的批准工件。**执行者把一个全局回复读成了对逐项问题的
答复。** 阻断成立，接受。

### 修订

1. `authorises_run` 收回为 `false`，`authorises_run_count` 归 `0`，
   `blocked_by` 恢复 `[BLOCK-01]`，`approval_does_not_authorise_execution`
   恢复 `true`。
2. `BLOCK-01` 记 `cleared: false`，并新增字段：`machine_validation: PASS`、
   `human_approval_ref: null`、`approved_instance_sha256: null`、
   `not_yet_cleared_because`（写明哪些字段是主观经营承诺而非可脚本判定的事实）。
3. 新增审核方建议的**合取**不变量：

```yaml
clearing_conditions:
  - machine_validation == PASS
  - human_approval_ref exists
  - approved_instance_sha256 == frozen instance sha256
clearing_conditions_are_conjunctive: true
```

4. `BLOCK-02` 补 `human_approval_ref` 指向其 `APPROVE`（PR #79），并说明
   route policy 是规则而非经营承诺，不需要 profile 式的独立批准工件。
5. `not_authorised` 恢复首条「执行本运行——`BLOCK-01` 未清」。

### 测试

新增 `test_block_01_requires_human_approval_not_only_machine_validation`
（断言三条件合取，且 `cleared` 等于三者之与）与
`test_machine_validation_alone_never_clears_block_01`。
`test_an_uncleared_blocker_stays_in_blocked_by` 把 `blocked_by` 与未清 blocker
列表绑定，防止两处各说各话。

### 第二轮变异检验

| 变异 | 结果 |
|---|---|
| **仅凭机器校验就清 `BLOCK-01`** | `FAILED (failures=4)` |
| `BLOCK-01` 未清却开启授权 | `FAILED (failures=1)` |
| 未清却清空 `blocked_by` | `FAILED (failures=1)` |
| 把三条件改成析取 | `FAILED (failures=1)` |
| 删掉 `human_approval_ref` 条件 | `FAILED (failures=1)` |

第一项正是本轮阻断的行为本身。五项回滚后 `diff -q` 均无差异。

### 未改的部分

profile 内容、外部包、机构资源边界处理、授权机制本身一律未动——审核方确认这些
方向正确。
