# `gen_indication_endpoint_target` Phase 1 合同报告

- 基线：Phase 0 已获 ChatGPT `APPROVE`
- 分支：`task_20260801_gen-iet-phase1-contracts`
- 状态：`COMPLETED_PENDING_REVIEW`
- Gate 变更：`NO_GATE_CHANGE`

## 本阶段完成

新增软件-only 合同包 `genmodules/gen_indication_endpoint_target/`，包括：

- `OpportunitySearchScope`
- `ClinicalFrame`
- `TargetCandidate`
- `CandidateFilterResult`
- `EvidenceRecord`
- `AdversarialReview`
- `TargetOpportunityHandoff`
- 生命周期、评估状态、证据方向、审核状态和候选筛选 disposition 枚举

## 约束

- `OpportunitySearchScope` 强制 `modality=ADC` 和正整数 candidate budget。
- TargetCandidate identity 固定为 indication、patient population、clinical endpoint、ADC target 四元组，同时保留 disease setting、line、treatment context、comparator 和 endpoint time horizon。
- T0/T1/T12 Gate 结果和所有跨执行边界的 source/run/policy/review/handoff 引用必须是 `external:`。
- `CandidateFilterResult` 明确是非 Gate，且保留 `NOT_EVALUATED` / `UNRESOLVED`。
- EvidenceRecord 包含 source、日期、提取、观察、归一化主张、置信度、局限、独立性和审核状态字段。
- AdversarialReview 只能记录 objections、counter-evidence、alternative explanations、critical unknowns 和 validation tasks，不能产生 Gate 结果。
- TargetOpportunityHandoff 只返回外部 opportunity、hypothesis、Gate、evidence 和 review 引用，不创建本地记录。

## 明确未做

未实现 candidate generator、Evidence Collector、Rule/Model/Gate evaluator、ranking engine、P-chain/C-chain、数据库、数据读取、缓存、结果写入、runner 或新的 Gate。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：53 passed
- `./scripts/verify_repository_boundary.sh`：passed
- `git diff --check`：passed

## 审核停止点

请 ChatGPT 只审核本 Phase 1 PR 的合同、边界和测试；在明确批准前，不进入执行适配或真实资产生成阶段。
