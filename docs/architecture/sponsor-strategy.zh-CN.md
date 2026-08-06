# Sponsor Strategy Contracts

版本：`0.1.0`

本文件记录小微 Biotech 架构调整的第 1 步。它把“资产本身是否科学成立”和“当前发起方是否适合推进”分开，但暂不实现后续的搜索空间准入、项目承诺评审或资源计划。

## 目标

第 1 步只建立两个外部合同：

- `DevelopmentSponsorProfile@0.1.0`：描述发起方的疾病优势、能力、合作能力、不可用能力、资本/时间边界、可访问资源和偏好的风险转移节点。
- `ProgramThesis@0.1.0`：把 `Opportunity`、`ClinicalHypothesis`、预期产品位置、发起方 Profile 和目标转移里程碑绑定为一个可审计的项目主张。

它们是合同形状，不是仓库内的实例记录。实际 Profile、Thesis、预算、患者样本、模型和来源都必须由外部 runtime 提供；所有跨边界对象引用和来源引用必须使用 `external:` 方案。

## 不变量

1. Sponsor-relative 信息不能改变资产内在科学 Gate 的事实或结果。
2. Profile 变化只允许触发未来的 sponsor-fit 重评估，不得回写 `TargetHypothesis`、`ClinicalHypothesis` 或 Gate 结果。
3. `ProgramThesis` 必须包含明确的目标风险转移里程碑。
4. `ProgramThesis` 不授予项目承诺，不执行 Gate，也不启动 Asset Generation。
5. 当前阶段不新增科学 Gate，不改变现有 45-Gate 拓扑，不运行外部数据，不保存实例。

## 后续四步边界

本次只交付第 1 步。后续步骤必须在本 PR 获得 ChatGPT `APPROVE` 并合并后，分别通过新的 PR 执行：

1. 建立 Sponsor Profile 和 Program Thesis 合同（本 PR）。
2. 增加 Early Search-Space Admission，只做 `ACTIVE_SEARCH`、`WATCHLIST`、`PARTNER_ONLY`、`OUT_OF_MANDATE` 路由。
3. 在 T12 后增加 Program Commitment Review；没有承诺结果不得进入 binder 或 de novo route。
4. 实现 `ValueInflectionPlan`，为获批项目定义交易节点、最小证据包、资源需求和停止条件。

任何后续步骤都不是本 PR 的隐含授权。
