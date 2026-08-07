# Handoff：WP2B 执行授权（清除 `BLOCK-01` 与 `BLOCK-02`）

- 日期：`2026-08-07`
- 任务分支：`task_20260807_wp2b-authorization`
- 基线：`main` @ `0c030c2`
- 交付物类型：**授权绑定（无新语义、无内容、未执行）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本 PR 做的三件事

1. 记录 `BLOCK-01` 已清——`DevelopmentSponsorProfile@0.1.0` 外部实例已由人类
   负责人确认并冻结。
2. 记录 `BLOCK-02` 已清——`search_space_admission_route_policy@0.1.0`
   已由 PR #79 合并（`0c030c2`）。
3. 把 `authorises_run` 转为 `true`，`authorises_run_count` 设为 **1**，
   `blocked_by` 清空。

形态与 PR #66 解除 `EVGAP-01` 的 binding PR 相同。**不改任何语义、范围、
来源策略、证据标准或校验规则。**

## 二、`BLOCK-01` 的清除证据

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

`not_authorised` 的第一条相应由「执行本运行」改为
「在 `authorises_run_count` 归零后再次执行本运行」。

## 四、变异检验

| 变异 | 结果 |
|---|---|
| 授权次数改为 3 | `FAILED (failures=1)` |
| 把计数器标成代码强制 | `FAILED (failures=1)` |
| 清除 blocker 但不给证据包 | `FAILED (failures=1)` |
| 截断实例哈希 | `FAILED (failures=1)` |
| 标记 blocker 已清但证据为空 | `FAILED (failures=1)` |

五项回滚后 `diff -q` 均无差异。测试要求「已清的 blocker 必须写明是什么清的，
而不是只翻一个布尔位」。

## 五、本 PR 不做什么

**不执行运行。** 不产出任何 territory；不含任何 CRC 内容；不改范围、来源策略、
证据标准、校验规则或 `not_authorised` 的其余各条；不改 route policy、
`SponsorFitAssessment`、`SearchSpaceAdmission` 或任何科学 Gate；不解除
`EVGAP-01`／`EVGAP-02`；不裁定 `GAP-P07`；不复活 369-pair 轴；
**不把任何机构资源当作 Stelligen 资产**。

## 六、验证

```
Ran 541 tests  OK              （合并前 538，净增 3）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
外部包 validate_profile.py              19/19 MATCH
```

无数据、cache、result、database、model weights 或实例进入仓库。

## 七、后续顺序

1. 本 PR `APPROVE` 并合并 —— **WP2B 获得一次执行授权**。
2. 执行 CRC Territory Map（**外部运行**，产物不入仓）。按契约必须产出
   `territory_map.json`、`territories.tsv`、`search_space_admissions.json`、
   `sponsor_evidence_advantage.json`、`source_manifest.json`、`run_report.md`
   与包内可独立运行的 `verify_package.py`，逐文件 SHA-256，整包 SHA-256。
3. 结果 PR：`VAL-T01`..`VAL-T21` 全部校验，并把 `authorises_run_count` 归零。
4. 获批后进入 WP3 Program Wedge Generator。

### 一件后续必须注意的事

profile 一旦改版，按 route policy 的 `RT-03`，所有已路由 territory 的
`asymmetric_evidence_advantage`、`key_uncertainty_addressable` 与
`time_window_compatible` 都要重评估。因此 `NOT_YET_CONTROLLED` 登记表里任何一项
被法律工具转化为公司资源时，**不是改一行，而是升版本并触发重评估**。
