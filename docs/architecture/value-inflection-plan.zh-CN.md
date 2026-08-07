# Value Inflection Plan

版本：`ValueInflectionPlan@0.1.0`

这是小微 Biotech 架构调整的第 4 步。它是横跨生命周期的 sponsor-relative 计划对象，回答：

> 当前投入要购买哪一组证据，达到哪个状态后，机会的可转移价值会明显上升？

## 作用边界

- 连接当前项目阶段与目标价值拐点阶段。
- 固定目标交易类型、最小证据包、最低成功标准和停止条件。
- 明确所需能力、能力来源、潜在买家类型、买家要求和回退路线。
- 只保存外部引用，不在仓库保存项目实例、数据、证据或结果。

`estimated_cost_band_ref` 和 `estimated_duration_band_ref` 只是外部估算分档的引用，不是成本模型或数值预算。`target_transaction_type` 是计划目标，不是交易概率，也不自动匹配买家。

## 必须先固定的字段

- `current_stage` / `target_inflection_stage`
- `target_transaction_type`
- `critical_uncertainty_refs`
- `planned_evidence_package_refs`
- `minimum_success_criteria_refs`
- `stop_condition_refs`
- `estimated_cost_band_ref` / `estimated_duration_band_ref`
- `required_capability_refs` / `capability_source_refs`
- `expected_buyer_type_refs` / `buyer_requirement_refs`
- `fallback_route_ref`
- `human_approval_ref`

最小证据包和最低成功标准不能留空；停止条件不能留空。没有 `ValueInflectionPlan` 不得开始 Asset Generation。该规则是架构控制，不代表本合同会触发 Asset Generation。

## 生命周期与交易枚举

生命周期阶段枚举用于统一标签，不会自动推进生命周期：`OPPORTUNITY`、`TARGET_OPPORTUNITY`、`TARGET_ANTIBODY_HYPOTHESIS`、`CONJUGATE_PROTOTYPE`、`TRANSLATIONAL_POC`、`PARTNERABLE_PACKAGE`。

交易目标枚举为：`PARTNERSHIP`、`OPTION_DEAL`、`LICENSE`、`CO_DEVELOPMENT`、`NEWCO`、`DATA_PACKAGE_TRANSFER`。

## 明确不做的事

- 不执行实验、数据采集、模型或 Gate。
- 不改变 ClinicalHypothesis、TargetHypothesis 或科学 Gate 的事实。
- 不计算成本、交易概率或买家匹配分数。
- 不自动推进生命周期、创建 binder/de novo route 或提交交易。

具体计划、证据包和人类批准记录由外部 runtime 管理；本仓库只提供契约、校验代码和说明文档。
