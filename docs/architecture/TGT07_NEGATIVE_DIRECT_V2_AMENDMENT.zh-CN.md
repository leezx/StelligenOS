# TGT-07 阴性 DIRECT 的版本化修正（PR #143）

状态：`PROPOSED / PENDING_CHATGPT_REVIEW`。本文件只修正已合并的 TGT-05 迁移 RFC §2 中 GateSet v2 成员表对 TGT-07 的版本假设，以及依赖该假设的 Phase A 契约。PR #142 的其余科学和权责边界继续适用。

## 缺口与决定

`TGT-07@1.0` 的 Gate EvidenceLadder 将 DIRECT 限于已证实的 material soluble-antigen sink；它没有授权 `NEGATIVE/DIRECT`。已有 `MOD-TGT07@1.0.0` 在完成审计且合格的 intended-ADC TMDD 表明无 material sink 时会提出 `NEGATIVE/DIRECT`，但 Module 行为不能自行扩展冻结的 Gate 科学授权。PR #143 初版 `required_gate_policy@v2` 要求 TGT-07 的 `NEGATIVE/DIRECT` 才准 Candidate GO，构成版本冲突。新 ChatGPT 审核于 2026-10-23 给出 `REQUEST_CHANGES`。

Phase A 仅在新 `TGT-07@2.0` 中显式准入该窄义阴性：已完成并经审计的 soluble-antigen landscape、合格且验证的 intended-ADC TMDD、明确的暴露/亲和力/周转/剂量场景、结论为该场景下**无 material soluble sink**，并无其他暴露场景的未解 material-sink DIRECT 风险。此结论仅限被研究场景；未找到 PK 报告、未定量 shedding、低于检测限或资料未完成均非阴性。阳性 DIRECT 在独立场景仍优先保留，不能被一个阴性场景抵消；同一场景的相反 DIRECT 证据须人审冲突。

`ADC_TARGET_GATESET@2.0` 的第七成员和 CRC v2 binding 因此改为 `TGT-07@2.0`，`MOD-TGT07@2.0.0` 为未来计划版本，Phase A 的 primary module slot 为 `0.0.0`。现有 `MOD-TGT07@1.0.0` 仅服务旧 Gate 版本，禁止重绑。Phase B 必须先另行 PR 审核并实现两个 v2 Module、政策 registry 批准及显式激活；目前 Instantiation 保持 `HOLD`，不产生 Candidate Decision。v1 Gate/GateSet/Module 均不修改。

这是对 PR #142 精确 v2 roster 的**显式后续修正**，只有本 PR 经过 ChatGPT `APPROVE`、人类合并和阶段放行后才可成为实施依据；审核前不得按修正的 roster 运行。若审核不接受此修正，`required_gate_policy@v2` 的 TGT-07 GO 单元继续不可满足，不能以缺证据当阴性或静默回退旧版。
