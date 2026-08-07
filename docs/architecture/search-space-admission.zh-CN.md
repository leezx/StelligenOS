# Early Search-Space Admission

版本：`SearchSpaceAdmission@0.1.0`

这是小微 Biotech 架构调整的第 2 步。它在 CRC Level 01 生成之前或 Preview 之后、正式证据抽取之前提供 sponsor-relative 路由，减少明显不适配机会对 EVGAP 等资源的消耗，同时保留完整审计和未来重评估空间。

## 四种路由

- `ACTIVE_SEARCH`：当前发起方具有非对称证据优势，关键未知可以在当前资源边界内处理。
- `WATCHLIST`：存在尚未解决的窗口、竞争或证据不确定性，暂不主动消耗后续资源。
- `PARTNER_ONLY`：机会本身不被否定，但需要平台、抗体、payload 或其他外部能力后才适合推进。
- `OUT_OF_MANDATE`：在当前 sponsor mandate、资本、时间或组合容量下不推进；这不是全局 KILL，也不是科学失败。

`HER2`、`TROP2` 等成熟靶点不得因为热门而被全局删除；它们只能在当前 sponsor 上下文中被路由为 `PARTNER_ONLY` 或 `OUT_OF_MANDATE`。

## 八个低成本条件

合同要求外部 runtime 为每个候选提供以下八个条件的状态和证据引用：

1. `clinical_value_exists`
2. `competitive_position_not_locked`
3. `asymmetric_evidence_advantage`
4. `key_uncertainty_addressable`
5. `differentiation_visible_preclinical`
6. `defensible_ip_path`
7. `plausible_buyer_partner_map`
8. `time_window_compatible`

每项只能记录 `SATISFIED`、`UNKNOWN` 或 `UNSATISFIED`。`UNKNOWN` 保留为未知，不得自动转为 KILL、FAIL 或任何科学 Gate 结论。路由由外部、可审计的 `route_policy_ref` 提供，仓库内合同只校验形状和边界，不计算总分、不重新评价证据。

## 边界

- 这是 sponsor-relative 路由，不是第 46 个科学 Gate。
- 不删除候选，不改变 `Opportunity`、`ClinicalHypothesis` 或 `TargetHypothesis`。
- 不执行 Gate、EVGAP、模型、数据采集或 Asset Generation。
- 路由结果和所有证据、策略、理由均为外部实例；仓库只保存合同、校验代码和测试。
- 没有 Search-Space Admission 记录，不代表允许进入 T12 后的 Program Commitment Review；后者属于下一阶段。
