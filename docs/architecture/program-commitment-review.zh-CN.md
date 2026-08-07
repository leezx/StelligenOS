# Program Commitment Review

版本：`ProgramCommitmentReview@0.1.0`

这是小微 Biotech 架构调整的第 3 步。它位于外部 T12 opportunity decision 与 binder/ADC route selection 之间，回答的不是“科学机会是否成立”，而是“当前 sponsor 是否承诺投入到一个明确的风险转移边界”。

## 六个正式结果

- `SELF_DEVELOP`：当前 sponsor 可独立推进到目标交易节点，但仍需人类 handoff。
- `CO_DEVELOP`：需要在当前阶段引入 ADC 平台、抗体或其他合作伙伴共同推进。
- `DATA_PACKAGE_ONLY`：当前承诺只购买数据/biomarker package，不进入完整药物生成。
- `PARTNER_NOW`：需要先引入合作伙伴，再决定是否进入 conjugation 或其他产品工程。
- `MONITOR`：暂不承诺资源，持续观察窗口或关键未知。
- `STOP_FOR_SPONSOR`：当前 sponsor 不推进；这不是科学 Gate 的 KILL，也不否定机会本身。

前文讨论中的 `PARTNER_BEFORE_CONJUGATION` 和 `GENERATE_DATA_ONLY` 是自然语言描述；本合同分别收敛为 `PARTNER_NOW` 和 `DATA_PACKAGE_ONLY`，避免机器 ID 漂移。

## 输入

评审合同接收外部引用：T12 结果、Clinical/Target Hypothesis、竞争格局、IP/FTO 初筛、Sponsor Profile、资本边界、能力缺口、买家图谱，以及未来 Phase 4 定义的 Value Inflection Plan。Phase 3 只引用 Value Inflection Plan，不在本阶段定义它。

## 硬控制

1. 没有 `ProgramCommitmentReview`，不得进入 binder 或 de novo route。
2. `MONITOR`、`DATA_PACKAGE_ONLY` 和 `STOP_FOR_SPONSOR` 会保持 `BLOCKED_NO_COMMITMENT`。
3. `SELF_DEVELOP`、`CO_DEVELOP` 和 `PARTNER_NOW` 只产生 `EXTERNAL_HANDOFF_REQUIRED`，不自动执行 Asset Generation。
4. 所有承诺必须有外部 `human_decision_ref`；合同不自动评分、不运行 T12、不改变科学 Gate 事实。
5. 所有实例、证据、策略、理由、资本、能力、买家和来源都位于外部 runtime。

## 不在本阶段

- 不定义 `ValueInflectionPlan` 的字段或执行逻辑。
- 不实现 binder/ADC/de novo route selection。
- 不执行 Gate、EVGAP、provider、模型或数据采集。
- 不修改 45 个 Gate、生命周期、核心对象、ClinicalHypothesis 或 TargetHypothesis。
