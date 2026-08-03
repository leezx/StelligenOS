# EXT-01 `ground_truth_learning_loop`

- 状态：`shell_only`
- 优先级：低（等真实药物实验数据）
- 来源：`prompts/GPT-Feedback.md` `# v4` 一级风险一

## 要解决的问题

系统当前的信息流是单向的：

```
Evidence -> Gate -> Asset Generation -> Due Diligence
```

缺的是回流：

```
Clinical Outcome -> Rule -> Model -> Gate Calibration
```

文档里已经出现了 `calibration`、`Knowledge Ledger` 和 `model lifecycle` 这些词，但从来没有定义**哪一种真实结果可以改变系统**。

外部专家给的具体例子是：一个 ADC 三期失败了，到底应该改 Rule、改 Gate threshold、改某个 Model，还是只新增一条 evidence？目前没有治理，所以答案是「看当时谁在改」。

## 为什么这次只做壳子

当前还没走到有真实药物实验结局的阶段，闭环没有输入。但这件事的风险不在于晚做，而在于**将来有数据时临时决定**——那时候压力最大、最容易直接去改阈值。所以先把改动分类和治理级别固化下来。

## 设计逻辑（待激活）

核心是把「结局 → 系统变更」这条路径拆成受治理的改动类别，每一类绑定不同的治理强度：

| 改动类别 | 含义 | 治理级别 |
|---|---|---|
| `evidence_only` | 只新增一条证据，不改判据 | 常规 PR |
| `rule_calibration` | 调整历史 Rule 的适用性或置信度 | 常规 PR + 领域专家复核 |
| `model_recalibration` | 重新校准 Model，产生新 `model_id@SemVer` | 独立治理任务 + Model lifecycle 记录 |
| `gate_threshold_revision` | 改动 Gate 阈值或充分性判据 | 独立治理任务 + 专家签字，最高强度 |
| `no_change` | 结局不足以改变系统，显式记录为不改 | 常规 PR，但必须留痕 |

最后一类同样重要：显式记录「这个失败不改变系统」，比默认不记录要好，否则将来无法区分「评估过认为无关」和「没人看过」。

关键约束是**所有回写都是提案，不是应用**。`CalibrationProposal` 只描述建议的改动类别和依据，不携带执行能力。

## 边界

不修改内核。不在仓库内保存临床结局数据、模型权重或校准结果——这些全部是外部工作区的 `external:` 引用。

## 激活前必须回答

1. 一个结局要多强才够触发 `gate_threshold_revision`？单个三期失败够吗，还是需要多个独立案例？
2. 谁有权批准 `gate_threshold_revision`？
3. 阈值改动是否需要向后重算已有的 Gate 结果，还是只对新运行生效？如果重算，历史决策记录怎么处理？
4. 与 `BL-05`（Success Probability）和 `BL-07`（Portfolio Learning）的关系——它们都依赖本扩展提供的结局数据。
