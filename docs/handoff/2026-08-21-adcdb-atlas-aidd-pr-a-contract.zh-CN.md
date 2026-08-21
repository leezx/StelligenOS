# Handoff：PR-A ADCdb → Atlas Target-selection Execution Contract

- 日期：2026-08-21
- 分支：`task_20260821_adcdb-aidd-pr-a-contract`
- 基线：远程 `main`，包含 PR #88 merge commit `a8afcd4`
- 状态：`CONTRACT_REVIEW_REQUIRED_EXECUTION_NOT_AUTHORIZED`
- 合同：`ADCdb_Atlas_ADC_AIDD_PR_A_Contract@0.1.0`
- 审核对话：Chrome ChatGPT `Biotech ideas → ADCdb_Atlas_ADC_AIDD_design`

## 本 PR 做什么

把 v0.3 的文字路线变成可执行 contract：source admission、snapshot/checksum、TargetSeed、Atlas G1–G4、developability G5–G7 和 TargetCommit 的输入输出与 operational criteria。

## 本 PR 不做什么

不下载或读取 ADCdb，不生成 TargetSeed，不运行 Atlas，不执行 Gate，不选 primary target，不修改 v0.3 canonical design，不创建 DATA/result/cache/model output。

## 期待结果

PR-A 获批后，PR-B 才能固定 ADCdb snapshot，生成第一批约 20–50 个 TargetSeed，计算 G1–G4 并提交 Atlas survivors 结果。PR-B 不执行 G5–G7，也不生成 TargetCommit。

## 当前阻断与下一步

- 当前阻断：PR-A 尚未获得 ChatGPT `APPROVE`。
- 下一步：完成本地测试和边界检查，创建 PR-A，提交同一 ChatGPT 对话审核。
- 只有明确 `APPROVE` 后，才允许进入 PR-B。
