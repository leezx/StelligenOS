# Handoff：SRCADM-01 准入绑定（极小 binding PR）

- 日期：`2026-08-06`
- 任务分支：`task_20260806_srcadm-01-admission-binding`
- 基线：`main` @ `e167c56`
- 授权依据：**PR #63 `APPROVE`**（记录见 `logs/chatgpt-review-2026-08-06-srcadm-01-admission-final.md`，由 PR #65 合入）
- 交付物类型：**准入绑定（无新证据、无执行）**
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、只做审核方指定的三件事

1. 更新 `SRCADM-01` 的 admission 状态与记录引用；
2. 把 `EVGAP-01` 的 `admission_record_ref` 指向 PR #65 新增的 #63 审核记录；
3. 在四项准入条件不变的前提下，授权**一次** `EVGAP-01` extraction。

| 字段 | 之前 | 之后 |
|---|---|---|
| `srcadm_01…yaml` `admission.status` | `pending_review` | `approved` |
| `srcadm_01…yaml` `admission_record_ref` | `null` | 指向审核记录 |
| `srcadm_01…yaml` `grants_admission_by_itself` | `false` | **`false`（未变）** |
| `evgap_01…yaml` `admission_status` | `pending_separate_admission_pr` | `admitted_with_conditions` |
| `evgap_01…yaml` `admission_record_ref` | `null` | 同一条记录 |
| `evgap_01…yaml` `authorises_extraction_run` | `false` | **`true`** |
| `evgap_01…yaml` `extraction_blocked_by` | `[SRCADM-01]` | `[]` |
| `evgap_01…yaml` `authorises_level_01_execution` | `false` | **`false`（未变）** |

`grants_admission_by_itself` 保持 `false` 是有意的：**准入不是这个文件授予的**，
是它所指向的那条审核记录授予的。该文件只承载指针。

新增 `authorises_extraction_run_count: 1`——授权范围是**一次**抽取，不是长期许可。

## 二、四项条件原样承接

`COND-01` 仅限该 snapshot／`COND-02` 仅限 PR #59 字段白名单／`COND-03` 依赖已归档 raw snapshot／
`COND-04` target 轴扩大或重复键进入判据时须重审。

`EVGAP-01` 侧新增 `admission_is_conditional: true` 与 `admission_conditions: [COND-01..04]`，
并有测试断言该列表与 `SRCADM-01` 实际冻结的四项**逐项相等**——防止两边日后漂移。

## 三、一处必须说明的形态不一致

PR #59 冻结的 `admission_record_path_pattern` 是：

```
logs/chatgpt-review-<date>-adc-surfaceome-reference-v0-3-0-admission-final.md
```

而 PR #65 实际合入并已获批的记录文件名是：

```
logs/chatgpt-review-2026-08-06-srcadm-01-admission-final.md
```

按 admission ID 命名，不是按数据集命名。

**处理方式：不重命名已合并且已获批的记录文件**，改为把形态对齐到实际约定，
并以 `admission_record_path_pattern_superseded` 保留原形态以便追溯。
重命名一份已被引用的审核记录，风险高于修正一条命名形态。

## 四、顺带修正的一个既有 YAML 缺陷（仅限本 PR 已触及的那一处）

`not_authorised` 里的条目若未加引号，YAML 会把 ` #59` 之后的内容当成注释：

```yaml
- 扩大 PR #59 的字段白名单        # 解析结果实为「扩大 PR」
```

该条目在机器可读层面**静默丢失了全部区分度**。本 PR 因绑定本就要重写这张表，
故一并加引号修正。

**同类缺陷在另外三处仍然存在**，但都在本 PR 未触及的文件里，属无关改动，**未修**：

| 文件 | 行 | 解析后退化为 |
|---|---|---|
| `adc_pool_level_01_input_binding.yaml` | 498 | `…绑定到 PR` |
| `evgap_01_surface_localization_extraction.yaml` | 551 | `把被隔离运行（PR` |
| `evgap_02_crc_linkage_extraction.yaml` | 1104 | `把被隔离运行（PR` |

影响有界：原文对人类读者仍可读，丢的只是机器解析后的内容；且现有测试断言的
都是其他条目，未被掩盖。**建议另开一个极小 PR 统一加引号，并加一条防回归检查。**

## 五、`not_authorised` 移出的两条

- 「授予准入」——已由 PR #63 的 `APPROVE` 成立；
- 「修改 `evgap_01…yaml` 的 `admission_record_ref`」——那正是本 PR 依授权所做的事。

其余全部保留，并把「执行 `EVGAP-01` 抽取」改写为
「本记录只支持授权，执行是另一次动作」，使授权与执行不被混为一谈。

## 六、本 PR 不做什么

**不执行 `EVGAP-01` 抽取**；不执行 Level 01；不解除 `EVGAP-01` 或 `EVGAP-02`；
不改 target 轴；不碰 `EVGAP-02` 契约；不纳入该数据集的其他版本；
不扩大 PR #59 的字段白名单；不纳入 `SRCADM-02`..`05` 的任何派生库。

`Ran 372 tests` OK，`scripts/verify_repository_boundary.sh` 通过。

## 七、后续顺序

1. 本 PR `APPROVE` 并合并。
2. **执行一次 `EVGAP-01` 抽取**（外部运行，产物不入仓）→ 结果 PR → 获批后另开 binding PR 解除 `EVGAP-01`。
3. `EVGAP-02` 侧独立推进：先处理 `GAP-P07`（四个身份待裁定的 target，其中 `CA19-9`
   是否属于膜蛋白 target universe 须由人裁定），再执行 `L-ASSERTION` 抽取。
4. **两个缺口都解除后**，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
