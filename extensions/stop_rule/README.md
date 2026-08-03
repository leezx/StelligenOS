# EXT-04 `stop_rule`

- 状态：`active_design`
- 优先级：最高
- 来源：`prompts/GPT-Feedback.md` `# v4` 一级风险四

## 要解决的问题

系统当前只会让证据越来越多、Gate 越来越多、Review 越来越多，但没有任何地方定义「够了」。后果是每个 Gate 都可以无限继续搜文献，一个药永远做不出来。

外部专家的原话是：这是很多 AI Scientist 最后掉进去的大坑。

## 设计逻辑

核心是给每个 Gate 配一份 `EvidenceSufficiencyContract`，把「够了」写成可判定的条件，然后由 `evaluate_stop_condition()` 对证据台账快照做出三值裁决。

### 五个判据

| 判据 | 含义 |
|---|---|
| `min_independent_evidence` | 至少需要多少组**独立**证据。方向中立，见下。 |
| `max_unresolved_conflicts` | 允许残留多少条未解决的证据冲突。 |
| `min_confidence` | 聚合置信度下限。 |
| `require_major_unknown_cleared` | 是否要求关键未知项已被清空。 |
| `max_evidence_search_iterations` | 搜索轮次的硬上限。 |

前四条决定「证据是否充分」，第五条决定「是否还允许继续找」。两者是独立的维度，这一点是本扩展设计上最关键的地方。

### 充分性必须方向中立

`min_independent_evidence` 的判定是 `max(独立支持证据, 独立反对证据) >= 阈值`，**不是**只看支持方向，也**不是**把两个方向相加。

如果只看支持方向，一个有 10 条独立反对证据、0 条支持证据的 target 永远无法达标，于是被无限继续搜索——而这正是 Stop Rule 要防的失败模式。充分性问的是「现在够不够做判断」，不是「答案是不是肯定的」。

两个方向也不能相加：2 条支持加 2 条反对是冲突，不是 4 份证据，所以取两个方向中较强的那一个。

裁决结果**不携带方向**。`StopDecision` 里没有任何字段说明证据偏向哪边，也没有 pass/fail 信号。方向由 Gate 判断，不由 Stop Rule 判断，因此充分的反对证据能结束搜索，但不会自动变成 FAIL。

### 三值裁决，而不是二值

```
SUFFICIENT              证据达标，停止搜索
INSUFFICIENT_CONTINUE   证据未达标，但还有搜索预算，继续找
INSUFFICIENT_EXHAUSTED  证据未达标，且搜索预算已耗尽 -> 升级为人类决策
```

`INSUFFICIENT_EXHAUSTED` 是本设计的要点。一个朴素的 Stop Rule 会在搜索耗尽时直接判 FAIL，但那等于把「我们没找到足够证据」偷偷变成「这个 target 不好」——这正是内核设计原则第 3 条（`unknown` 不是失败）所禁止的。因此耗尽路径产出的是一个必须由人类裁决的阻断状态，不是 FAIL。

这样做同时满足了两个看起来矛盾的要求：搜索一定会终止（因为有硬上限），但终止不会伪造结论（因为耗尽只能升级，不能定罪）。

### `SUFFICIENT` 不等于「可以进入 Gate 评分」

裁决和授权是两件事。能否据此进入 Gate 评分，只看 `StopDecision.actionable`：

```
actionable = (verdict == SUFFICIENT) AND (contract 已 expert_calibrated)
```

`DEFAULT_SUFFICIENCY_BASELINES` 的阈值是未校准的建议值。用这样的契约求值仍然会得到 `SUFFICIENT`——那是有信息量的，它说明「按建议阈值算已经够了」——但 `actionable` 保持 `False`，因为阈值本身还没被专家认可。这与 `extension.yaml` 中「专家校准前不得激活」一致。

`StopDecision` 在构造时强制三条不变式：未校准契约不得产出 `actionable=True`；非 `SUFFICIENT` 裁决不得 `actionable=True`；已校准契约的 `SUFFICIENT` 不得隐藏其 `actionable`。

### 为什么是 advisory_only

裁决结果只是 Gate 执行的前置判据，本身不写 Gate 分数、不改状态、不推动生命周期。这保持了内核「只有受治理的 Gate 执行才能产生 Gate 结果」的原则。

## 边界

不修改任何 `gate.yaml`、阈值、Profile 绑定或 45-Gate 拓扑。不接受任何证据数据进入仓库——`EvidenceLedgerSnapshot` 只接受聚合计数和 `external:` 引用。

## 已知限制

`min_independent_evidence` 依赖「独立证据」的定义，而当前这个定义不够严格：一篇综述、它引用的原始论文、以及 PubMed 上的同一条记录可能被计为三组独立证据。这是 `BACKLOG.zh-CN.md` 的 `BL-01`。在 BL-01 解决之前，本判据会偏向过早判定充分，且该偏差对支持与反对两个方向同时存在。

三个 gate group 的 baseline 阈值（`DEFAULT_SUFFICIENCY_BASELINES`）来自外部专家的建议值（独立证据 ≥ 3、冲突已解决、置信度 > 0.8），**不是经过校准的科学阈值**。它们被显式标记为 `proposed_baseline`，据此求值的裁决 `actionable` 恒为 `False`，激活前必须逐 Gate 由领域专家复核。

## 激活前必须回答

1. 45 个 Gate 各自的充分性阈值分别是多少？T-chain 的硬门（如 T7 肿瘤表面可及性）是否需要比 baseline 更严？
2. `max_evidence_search_iterations` 的单位是什么——检索轮次、专家复核轮次，还是外部运行次数？
3. `INSUFFICIENT_EXHAUSTED` 升级给谁？是单个专家签字，还是需要委员会？
4. BL-01 evidence independence 是先解决，还是明确接受其偏差并记录？
