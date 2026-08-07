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

## 二、`BLOCK-01` 的候选实例（**尚不足以清除**）

外部包（**不入仓**）。第二轮审核后已换为 v0.1.1：

```
gen_sponsor_profile_stelligen_v0.1.1_20260807T130000Z_draft
ZIP SHA-256   cf410e6278f8d78fa2e9aa937b14a72bc878cb9533059ae66374af0e5eb5f8a8
实例 SHA-256  7582ca157ec769c170c390e6dc8a99d55adf2e1dffc3d1af461434797e0ec421
22,972 bytes，7 个文件
validate_profile.py -> 47/47 MATCH
```

**v0.1.0 全部作废**，实例 SHA-256 `65253e10…` 写入契约的
`withdrawn_candidates`，并带 `must_never_be_approved_instance_sha256: true`。
作废理由见第九节。旧包保持原样不动（SHA 仍可验证），作废说明写在包外的同名
`.WITHDRAWN.md` 里，不改动包内字节。

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
  任何 CRO 或合作方已签约。v0.1.1 起，这句限定写进实例本身的每一条能力条目，
  不再只写在分类表里。
- 每个字段都有 `CONFIRMED_CURRENT_FACT`／`OPERATING_ASSUMPTION`／`UNKNOWN` 的
  分类表，**操作假设不得被静默升格为事实**。19 个字段中 9 个事实、9 个操作假设、
  1 个逐条分类。

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

1. **人类负责人审阅 v0.1.1 完整 profile**（人读摘要 + 逐字段 provenance 表），
   明确接受或指出要改的字段。
2. 接受后填写包内 `human_approval_template.json`——它要求记录被批准的版本、
   实例 SHA-256、时间戳、批准角色，以及两项显式承认（操作假设是当前政策而非
   事实；未把任何机构资源计为公司资产）。**签署后的工件才是
   `human_approval_ref`。**
3. 再更新本 PR：`BLOCK-01.cleared: true`、写入 `human_approval_ref` 与
   `approved_instance_sha256`（须等于 `7582ca15…`），并把 profile 重新以
   `FROZEN` 出包，再开启 `authorises_run`。
4. 本 PR `APPROVE` 并合并 —— **WP2B 才获得一次执行授权**。
5. 执行 CRC Territory Map（**外部运行**，产物不入仓）。按契约必须产出
   `territory_map.json`、`territories.tsv`、`search_space_admissions.json`、
   `sponsor_evidence_advantage.json`、`source_manifest.json`、`run_report.md`
   与包内可独立运行的 `verify_package.py`，逐文件 SHA-256，整包 SHA-256。
6. 结果 PR：`VAL-T01`..`VAL-T21` 全部校验，并把 `authorises_run_count` 归零。
7. 获批后进入 WP3 Program Wedge Generator。

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

## 九、第二轮审核裁决与修订（`REQUEST_CHANGES`，三条，全部接受）

审核方判定「方向通过，但暂不批准当前 artifact」，并逐项裁定了此前标出的三处疑问。

### 三处疑问的裁定（照办，未改内容实质）

| 项 | 裁定 |
|---|---|
| `partnered_capabilities` | 维持 `OPERATING_ASSUMPTION`。今天没有任何 CRO／合作方签约或被 Stelligen 锁定。更准确的语义是「可通过市场采购或合作获得」，不是「已 partnered」。**不得升为事实。** |
| `company_stage` | 维持 `pre_company_founder_led_micro_biotech_asset_studio`。无证据证明已有独立法律实体；**不得为了「像公司」而假定存在实体**。 |
| `risk_tolerance`／`geographic_scope` | 两项均归 `OPERATING_ASSUMPTION`。风险偏好是当前研发经营策略，不是客观事实——融资、合作结构、团队能力变化都可能改变它。内容本身接受。 |

### 阻断一：`maximum_self_funded_stage` 与资本边界自相矛盾

v0.1.0 把最大自研阶段写成「带现成 linker-payload 原型的 focused translational
POC」，而同一份实例的资本边界又说六位数以上需要外部资本。抗体生成、偶联、
分析表征、多构建体、organoid panel、xenograft——这些放不进「低万美元级」。

**为什么这比措辞重要：** `key_uncertainty_addressable` 读的就是最大自研阶段。
按旧值，系统会认为「这个关键不确定性 Stelligen 自己有能力买下来」，把本该
`ONLY_WITH_EXTERNAL_CAPITAL_OR_PARTNER` 的项判成 `SATISFIED`。

修订：两个字段承担两个不同含义。

- `maximum_self_funded_stage` 收紧为
  `target_state_and_biomarker_validation_plus_focused_low_cost_in_vitro_feasibility`
  ——今天自己掏钱能做到哪里。
- `preferred_transaction_stage` **保持不变**，但显式标注
  `preferred_transaction_stage_is_not_self_funded: true`，并写明到达它可能需要
  partner／grant／NewCo／外部融资。

实例另加 `key_uncertainty_addressable_semantics`，逐条列出哪些不确定性落在自研
阶段内、哪些必须外部资本或合作方。

### 阻断二：公开数据不足以形成非对称证据优势

v0.1.0 的 summary 已意识到这点，但只写在散文里。审核方要求写成硬不变量，理由是
「我比别人分析得更聪明」本身很容易成为自我叙事。

修订：`hard_invariants` 新增

> public data plus generic bioinformatics competence is insufficient to mark
> `asymmetric_evidence_advantage = SATISFIED`; the territory-specific assessment
> must identify a concrete, reproducible and non-trivial derived advantage.

并新增 `asymmetric_evidence_advantage_semantics`，列出六种可审计的合格形式，
外加一条 `self_narrative_is_not_a_qualifying_advantage`。

### 阻断三：上传包内部状态自相矛盾（审核方直接检查文件发现）

同一个 ZIP 里，`development_sponsor_profile.json` 与 `source_manifest.json` 写
`FROZEN`／`frozen: true`／`clears_block_01: true`／`frozen_by: human lead
confirmation`；而 `profile_summary.md` 与 `provenance_table.md` 写
`DRAFT_PENDING_HUMAN_REVIEW`／未冻结／`BLOCK-01` 未清。

**成因（执行者的错）：** 冻结时只重新生成了 JSON 与 manifest，两份 markdown 是从
草稿包整份沿用的。`diff -q` 对两份文件均无差异——即 100% 未更新。
**这是本轮最严重的审计问题**：#80 已经收回授权，外部证据包却仍自称已获人工确认。

修订不是改那两行，而是改生成方式：

- 新包 v0.1.1，`STATUS`／`FROZEN`／`CLEARS_BLOCK_01` 三个常量在构建脚本里只写
  一处，四个文件的状态行全部由它派生；
- `provenance_table.md` 改为**由实例里的 `field_provenance` 生成**，不再手写，
  两者不可能再各说各话；
- 校验脚本新增跨文件状态一致性检查——instance／manifest 三个状态字段必须相等，
  summary 与 provenance 必须出现同一个状态 token 且不得出现相反的状态行。

### 其余采纳的修订

- `accessible_patient_samples` 拆成两问：**当前**没有任何 sponsor-controlled 样本
  是 `CONFIRMED_CURRENT_FACT`；**将来**能否通过协议获得哪些具体样本才是 `UNKNOWN`。
  v0.1.0 把两者混成一类。
- `accessible_models` 改为 `MIXED_PER_ITEM`：商业可得细胞系是当前事实，CRO
  organoid／xenograft 服务是可采购的操作假设，学术 organoid／PDX 整体排除在字段外。
- 九个经营政策字段（partnered capabilities、capital envelope、time horizon、
  最大自研阶段、transaction stage、capacity、risk tolerance、geographic scope、
  IP strategy）统一归 `OPERATING_ASSUMPTION`。
- 新增 `human_approval_template.json`：批准工件必须记录版本、实例 SHA-256、
  时间戳、批准角色，以及两项显式承认。**「用户说 OK」不构成批准工件。**
- 校验脚本设 `sys.dont_write_bytecode = True`——它 import 仓库合同，此前会在
  data-free 的仓库里留下 `__pycache__`。

### 契约侧改动（仓库内，仍不开启授权）

`BLOCK-01` 新增 `candidate_instance_sha256`／`candidate_instance_version`／
`candidate_is_not_approved: true`／`withdrawn_candidates`／
`human_approval_artifact_must_record`。`machine_validation_evidence` 指向 v0.1.1。
**`authorises_run` 仍为 `false`，`blocked_by` 仍为 `[BLOCK-01]`。**

### 变异检验

外部包 16 项，全部 CAUGHT，回滚后整树 SHA-256 逐次比对无差异：

| 变异 | 结果 |
|---|---|
| manifest 写 FROZEN 而 instance 写 DRAFT（**v0.1.0 的原始缺陷**） | `45/47` FAIL |
| summary 状态行翻成 FROZEN | `44/47` FAIL |
| 草稿自称清除 `BLOCK-01` | `44/47` FAIL |
| 无工件却记 human approval received | `45/47` FAIL |
| `risk_tolerance` 改回 `CONFIRMED_CURRENT_FACT` | `44/47` FAIL |
| `maximum_self_funded_stage` 还原为 v0.1.0 的值 | `45/47` FAIL |
| 自研阶段与 transaction stage 设为相同 | `44/47` FAIL |
| 从 `hard_invariants` 删掉公开数据不足条 | `45/47` FAIL |
| 公开数据不足标志翻为 false | `45/47` FAIL |
| 关键不确定性规则去掉自研阶段约束 | `45/47` FAIL |
| 当前样本缺失塌回 `UNKNOWN` | `45/47` FAIL |
| `accessible_models` 改回统一分类 | `45/47` FAIL |
| 某项 partnered capability 写成已签约 | `45/47` FAIL |
| 机构 PDX 混入 `accessible_models` | `45/47` FAIL |
| 删掉某个字段的 provenance 条目 | `45/47` FAIL |
| 批准模板预填版本号 | `46/47` FAIL |

仓库侧 4 项：把候选 SHA 提升为已批准（`failures=1`）、把已作废 SHA 写成已批准
（`failures=2`）、删掉一项承认字段（`failures=1`）、`machine_validation_evidence`
指回已作废的包（`failures=1`）。回滚后 `diff -q` 无差异。

**一处自查修正：** 「删掉 provenance 条目」最初是靠 `KeyError` 崩溃退出而非报
FAIL，后面的检查全部丢失。已改为所有 `field_provenance` 访问走 `class_of()`，
缺失报 `<MISSING>` 并正常出报告。**退出码正确不等于检查有效。**

### 验证

```
Ran 547 tests  OK              （上一轮 544，净增 3）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
外部包 validate_profile.py              47/47 MATCH（上一轮 19/19）
```

### 未改的部分

profile 的实质内容方向、机构资源边界处理、`company_stage`、
`preferred_transaction_stage` 的内容、`geographic_scope` 的内容、
`BLOCK-01` 三条件合取不变量、授权机制本身——一律未动。

## 十、第三轮审核裁决与修订（`REQUEST_CHANGES`，一条，接受）

### 阻断：`evidence_standards` 里残留「`BLOCK-01`，已清」

`sponsor_fit_context` 的 `requires` 仍写着「已冻结的
`DevelopmentSponsorProfile@0.1.0` 实例（`BLOCK-01`，已清）」，而同一文件上方
`BLOCK-01` 是 `cleared: false`、`human_approval_ref: null`、
`approved_instance_sha256: null`。文件内部自相矛盾。

**成因，且与前两轮是同一个漏洞：** 这句是第一版开启授权时改的。第一轮收回授权
时，我改了 blocker 条目本身，**没有回改依赖它的散文**。v0.1.0 包里 markdown 未
随 JSON 更新，是同一类错误的另一种形式——改了状态源，没有改引用状态的地方。

**为什么不是 typo：** 它位于 `evidence_standards`，runtime 与后续审核者会据此
理解 sponsor baseline 已正式生效，而目前只有候选 profile。

### 修订

```yaml
requires: >-
  已获人工批准并冻结的 DevelopmentSponsorProfile 实例（须先按 clearing_conditions
  清除 BLOCK-01；候选实例在清除前不得作为基线）**加上**该 territory 可
  触及的数据／模型／know-how 与该 territory 的证据要求……
```

去掉了版本号 `@0.1.0`——基线是哪一版由批准工件决定，不该在证据标准里写死。

### 测试

审核方建议「字符串检查就够」。实际做成解析后遍历，而不是原文 `grep`：
`test_no_section_claims_an_uncleared_blocker_is_cleared` 递归走整份契约的**解析
结果**，只豁免 `blockers` 子树（那里本就在讨论清除状态），对每个 `cleared: false`
的 blocker，断言没有任何字符串同时出现它的 id 与「已清／已解除／cleared」。

这样做的理由是 PR #78 的教训：`assertNotIn("territories:", text)` 曾被新键
`ref_must_not_be_shared_across_territories:` 误中。原文匹配会重演。

另加 `test_the_advantage_baseline_waits_for_human_approval`，锁住
`sponsor_fit_context` 必须要求「已获人工批准」而非候选实例。

### 变异检验（含两项反向对照）

| 变异 | 结果 |
|---|---|
| 还原为「（`BLOCK-01`，已清）」原句 | `failures=2` |
| 在 `run` 段另写「`BLOCK-01` 已清，可直接读取 sponsor baseline」 | `failures=1` |
| 用英文写 `BLOCK-01 is cleared` | `failures=1` |
| **反向对照**：既有的「`BLOCK-01` 未清」措辞 | `OK`（未误报） |
| **反向对照**：新增「清除 `BLOCK-01` 之后方可使用」 | `OK`（未误报） |

反向对照是必要的：只验证会 FAIL，不能证明它不会把正确措辞也判为矛盾。回滚后
`diff -q` 无差异。

### 验证

```
Ran 549 tests  OK              （上一轮 547，净增 2）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
```

### 未改的部分

按审核方要求，**其他一律未动**。`authorises_run: false`、
`authorises_run_count: 0`、`blocked_by: [BLOCK-01]`、`cleared: false`、
两个 null 均保持不变。外部包 v0.1.1 未重新生成，实例 SHA-256 仍为
`7582ca157ec769c170c390e6dc8a99d55adf2e1dffc3d1af461434797e0ec421`。

### 审核方尚未能独立验证的一项（如实记录）

审核方指出：v0.1.1 外部包不在仓库内，其手上的 ZIP 仍是 v0.1.0，因此目前只能确认
本 PR 对新包的声明与机器校验记录，**无法逐字段独立验证 v0.1.1 的文件内容**。
这不影响当前「未授权」状态，但人工批准前必须先看到 v0.1.1 本体。

供审核的路径（**不入仓**）：

```
…/result/gen_sponsor_profile_stelligen_v0.1.1_20260807T130000Z_draft.zip
ZIP SHA-256  cf410e6278f8d78fa2e9aa937b14a72bc878cb9533059ae66374af0e5eb5f8a8
```
