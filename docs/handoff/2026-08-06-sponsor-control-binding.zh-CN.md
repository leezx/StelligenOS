# Handoff：Sponsor Control Binding（把 Phase 3–4 硬控制接进 Binder/ADC route request）

- 日期：`2026-08-06`
- 任务分支：`task_20260806_sponsor-control-binding`
- 基线：`main` @ `4ea075a`
- 交付物类型：**契约绑定（无新科学逻辑、无新 sponsor 决策逻辑、无执行）**
- 架构变更：`BREAKING_CONTRACT_CHANGE`（`BinderAdcRouteRequest` 新增三个必填字段）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、为什么需要这个 PR

Phase 3 与 Phase 4 的架构文档各自写了一条**硬控制**：

> 没有 `ProgramCommitmentReview`，不得进入 binder 或 de novo route。（Phase 3）
>
> 没有 `ValueInflectionPlan` 不得开始 Asset Generation。（Phase 4）

核查后确认：这两条在合并时**只存在于文档里**。

```
grep -rn "program_commitment_review|value_inflection_plan" src/ --include=*.py
  排除 src/contracts/ 自身后：0 处命中
BinderAdcRouteRequest 当时的必填字段：
  route_id / input_ref / opportunity_ref / policy_ref
  / tool_environment_ref / run_context_ref
```

四个 sponsor-relative 合同是各自独立的形状校验器，带自己的测试，但没有接进任何
调用路径。因此在本 PR 之前，**可以完整构造并执行一次 binder route 而不提供任何
commitment 记录，且全量测试不会失败**。声明了约束但没有消费者，与审核方此前对
`authorises_extraction_run_count` 的非阻断意见属同一类缺陷；区别在于这两条是
文档明写的「硬控制」。

本 PR 只做绑定，不引入任何新的科学或 sponsor 判断。

## 二、改了什么

### 1. `src/capabilities/binder_adc_routes.py`

`BinderAdcRouteRequest` 新增三个**无默认值**的必填字段：

| 字段 | 含义 |
|---|---|
| `program_commitment_review_ref` | 指向外部 `ProgramCommitmentReview@0.1.0` 实例 |
| `value_inflection_plan_ref` | 指向外部 `ValueInflectionPlan@0.1.0` 实例 |
| `asset_generation_authorization_ref` | 外部 human handoff 已确认前两者允许进入当前 route |

字段顺序按审核方给出的代码形态，三者置于 `opportunity_ref` 与 `policy_ref`
之间。这不只是排版：三个必填字段夹在其余必填字段中间后，**给其中任何一个加
默认值都会让模块在类定义阶段直接 `TypeError`**（non-default argument follows
default argument），比任何测试都更早失败。

校验按审核方形态收敛为**一个统一循环**，覆盖全部八个引用字段，使用
`isinstance` 守卫与统一错误文案 `"<field> must be a non-empty external:
reference"`；并按该文案的字面含义补上非空校验——`external:` 与 `external:   `
在八个字段上一律被拒。

无默认值是刻意的：默认值会让缺失的控制悄悄变回「已满足」，等于把这个 PR 的
作用取消。测试对此有专门断言。

`contract_version` 由 `0.1.0` 升为 `0.2.0`。新增必填字段是 breaking change。
`BinderAdcRouteResult` 未变动，**刻意保留 `0.1.0`**。

模块的 import 仍然只有 `dataclasses` 和 `typing`：**不 import
`ProgramCommitmentReview` 或 `ValueInflectionPlan` 类，不把外部实例拉回仓库
runtime**。有测试用 AST 解析源文件断言这一点。

### 2. `src/contracts/binder_adc_routes.yaml`

新增 `sponsor_control_binding` 段，把绑定写成机器可读形态——本 PR 的要点正是
「控制不能只存在于散文里」，所以绑定本身也不能只写在散文里：

```yaml
sponsor_control_binding:
  bound_contracts:
    program_commitment_review: ProgramCommitmentReview@0.1.0
    value_inflection_plan: ValueInflectionPlan@0.1.0
  required_request_refs: [三个新字段]
  required_request_reference_fields: [全部八个引用字段]
  reference_scheme: external_only
  empty_reference_body: forbidden
  default_values: forbidden
  reference_validation: uniform_across_all_required_request_refs
  blocked_commitment_outcomes_stay_blocked: [MONITOR, DATA_PACKAGE_ONLY, STOP_FOR_SPONSOR]
  field_presence_is_not_a_decision: true
  authorization_read_by_repository: forbidden
  authorization_re_adjudicated_by_repository: forbidden
  authorization_generated_by_repository: forbidden
  contract_class_import_by_capability: forbidden
  external_instance_materialisation: forbidden
```

同时把 `contract_version` 升为 `0.2.0`，并新增 `request_contract_version: 0.2.0`
与 `result_contract_version: 0.1.0`。

**这里做了一个超出字面指令的判断，需要审核方确认**：指令只要求升 dataclass 的
`contract_version`。但 YAML 是同一份合同的机器可读声明；只改代码会让 YAML 停在
`0.1.0` 而代码是 `0.2.0`，正好复制 `docs/architecture/…v3` §6.2 已登记的
`GateInputEnvelope` `2.0.0`/`2.1.0` 漂移问题。为不新增一处同类缺陷，两侧一并
对齐，并用两个 envelope 级字段说明 result 未变。若审核方认为应严格照字面只改
代码，可退回该 YAML 版本改动。

### 3. `genmodules/README.md`

「Architecture mapping」一节补一段 route 侧说明：进入任一 route 现在额外要求
三个不可省略、不可默认的 external reference，并写明 `MONITOR`、
`DATA_PACKAGE_ONLY`、`STOP_FOR_SPONSOR` 三种 outcome 仍保持
`BLOCKED_NO_COMMITMENT`——**字段存在本身不是决定**。这正是
`asset_generation_authorization_ref` 存在的理由：只要求
`program_commitment_review_ref`，一份 `MONITOR` review 同样能满足存在性检查。

### 4. `tests/test_phase5_binder_adc_routes.py`

原 fixture 已更新为提供三个新引用。新增 `SponsorControlBindingTests`，本文件共
23 个测试，覆盖：

- 三个字段各自缺失时**无法构造** request（`TypeError`）；
- 三个字段各自使用 `local:` 时被拒绝（三条字面命名的测试，外加一条参数化）；
- 全部八个引用字段对空串、`external:`、`external:   `、`local:x/1`、`1`、`None`
  以及一个 `__str__` 伪装成 external 的非字符串对象一律拒绝；
- 三个字段都**没有默认值**；
- 合法 external refs 可构造，两条 route 都验证；
- `contract_version` 为 `0.2.0`，result 仍为 `0.1.0`；
- 构造 request **不执行 route**（request 不暴露任何可调用属性）；
- 构造 request **不创建 result**（对 `BinderAdcRouteResult.__post_init__` 挂探针，
  断言从未被触发）；
- 构造 request **不推进 lifecycle**（`state_machine` 与 `clinical_lock` 的公开
  符号快照前后相等）；
- 构造 request **不写仓库状态**（构造前后仓库文件树快照相等）；
- request 为 frozen，不持有解析后的实例；
- 模块 import 集合恰为 `{dataclasses, typing}`；
- YAML 的 `sponsor_control_binding` 与代码常量逐项一致。

## 三、变异测试

按既有纪律，先改坏、确认 FAILED、再用 `diff -q` 回滚验证：

| 变异 | 结果 |
|---|---|
| 给 `asset_generation_authorization_ref` 加默认值 | 类定义阶段 `TypeError`，模块无法载入 |
| 给该字段及其后全部字段加默认值 | `FAILED (failures=2)` |
| 删除非空内容校验 | `FAILED (failures=16)` |
| 从 `SPONSOR_CONTROL_REQUEST_FIELDS` 删掉 `value_inflection_plan_ref` | `FAILED (failures=2)` |
| 从 `REQUIRED_REQUEST_REFERENCE_FIELDS` 删掉同一字段 | `FAILED (failures=4)` |
| 把 `contract_version` 退回 `0.1.0` | `FAILED (failures=1)` |
| 把 `isinstance` 守卫换成 `str()` 强制转换 | `FAILED (errors=8)` |

两处**第一轮未被捕获，已在本 PR 内修正**：

1. 删除控制字段元组中的条目时首轮只触发 1 条失败——参数化测试遍历的正是它要
   验证的那个常量，删掉字段也就删掉了对应用例，属自我收缩的重言测试。补了字面
   列出字段名的断言与三条字面命名的 `local:` 测试。
2. 把 `isinstance` 守卫换成 `str()` 强制转换时首轮**通过**。这是一次
   **无效变异，不是覆盖证明**：测试用的 `1` 和 `None` 经 `str()` 后同样不以
   `external:` 开头，两种实现无法区分。补了一个 `__str__` 返回
   `"external:impostor/1"` 的非字符串对象后，该变异升为 `errors=8`。

七项变异回滚后 `diff -q` 均无差异。

## 四、本 PR 明确不做什么

不修改 45 个 Gate；不修改 T12；不修改 lifecycle 或 core objects；不自动选择
binder/de novo route；不执行 Asset Generation；不生成 `ProgramCommitmentReview`、
`ValueInflectionPlan` 或 authorization 实例；不读取、不解析、不重新裁定
authorization；不修改 Phase 1–4 的四个合同本身；不执行任何外部运行；
**不更新 `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`**
——该文档的 v4 refresh 另立 PR。

## 五、验证

```
Ran 413 tests  OK              （合并前 393，净增 20；本文件 23）
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
git status --short                      仅本 PR 涉及的文件
```

无数据、cache、result、database、model weights 或任何实例进入仓库。

## 六、已知遗留（本 PR 未处理，登记备查）

1. **其余三个 sponsor-relative 合同仍未接线。** `DevelopmentSponsorProfile`、
   `ProgramThesis`、`SearchSpaceAdmission` 目前仍只有形状校验器，没有消费者。
   本 PR 只按指令绑定 Phase 3–4 两条硬控制。
2. **架构文档 v3 已过期。** 基线仍写 `main@8aa7e87`，落后 35 个 commit；§10.2
   仍把 PR #62/#63/#55 记为开放；§12 的运行流程图从 T12 直接走到 route
   selection，未含本 PR 绑定的控制点；§13 仍写 338 项测试。留待 v4 refresh。

## 七、后续顺序

1. 本 PR `APPROVE` 并合并。
2. 架构 v4 refresh PR：纳入 Phase 1–4、纠正过期基线与计数、在 §12 流程图中补上
   commitment 控制点、把上述遗留登记为审核问题。
3. `EVGAP-01` 抽取仍是已授权未执行状态，与本 PR 无关，不因本 PR 变化。
