# Handoff：PR-A ADCdb → Atlas Target-selection Execution Contract

- 日期：2026-08-21
- 分支：`task_20260821_adcdb-aidd-pr-a-contract`
- 基线：远程 `main`，包含 PR #88 merge commit `a8afcd4`
- 状态：`CONTRACT_REVIEW_REQUIRED_EXECUTION_NOT_AUTHORIZED`
- 合同：`ADCdb_Atlas_ADC_AIDD_PR_A_Contract@0.1.0`
- 审核对话：Chrome ChatGPT `Biotech ideas → ADCdb_Atlas_ADC_AIDD_design`
- PR：[#89](https://github.com/leezx/StelligenOS/pull/89)
- contract commit：`de96148`
- review-handoff HEAD：`89a8c43`

## 本 PR 做什么

把 v0.3 的文字路线变成可执行 contract：source admission、snapshot/checksum、TargetSeed、Atlas G1–G4、developability G5–G7 和 TargetCommit 的输入输出与 operational criteria。

## 本 PR 不做什么

不下载或读取 ADCdb，不生成 TargetSeed，不运行 Atlas，不执行 Gate，不选 primary target，不修改 v0.3 canonical design，不创建 DATA/result/cache/model output。

## 期待结果

PR-A 获批后，PR-B 才能固定 ADCdb snapshot，生成第一批约 20–50 个 TargetSeed，计算 G1–G4 并提交 Atlas survivors 结果。PR-B 不执行 G5–G7，也不生成 TargetCommit。

## 当前阻断与下一步

- 当前阻断：ChatGPT 对 PR #89 返回 `REQUEST_CHANGES`，要求补齐 LOCK schema 和 G1/G2/G4 的统计闭合规则。
- 下一步：只修复上述两个 execution-closure blocker，追加测试并在同一 ChatGPT 对话复审。
- 只有明确 `APPROVE` 后，才允许进入 PR-B。
