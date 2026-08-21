# Handoff：PR-B ADCdb SEED + Atlas MUST-PASS 生产契约

- 日期：2026-08-22
- 分支：`task_20260821_adcdb-aidd-pr-b-production-contract`
- 基线：已获 ChatGPT APPROVE 的 PR-A HEAD `2a2e21b`
- 状态：`PR_B_REVIEW_REQUIRED_EXTERNAL_RUN_NOT_AUTHORIZED`
- 合同：`ADCdb_Atlas_ADC_AIDD_PR_B_Production@0.1.0`
- 审核对话：Chrome ChatGPT `Biotech ideas → ADCdb_Atlas_ADC_AIDD_design`

## 本 PR 做什么

把 PR-B 的第一次生产运行写成可审核契约：source admission/snapshot verification、TargetSeed materialization、G1–G4 顺序、外部 DATA 输出和空 survivor 路由。

## 本 PR 不做什么

不读取或下载 ADCdb，不读取 Atlas 数据，不生成真实 TargetSeed，不运行 G1–G4，不执行 G5–G7，不生成 TargetCommit，不选择 primary/backup，不做 AIDD。

## 期待结果

PR-B 获批后，外部运行应生成有 run lock、快照、provenance 的 seed batch，并输出每个 seed 的 G1–G4 结果、survivor 表和 failure distribution。没有 survivor 也是合法结果。

## 当前阻断与下一步

- 当前阻断：PR-B 尚未获得 ChatGPT `APPROVE`，真实外部运行仍被禁止。
- 下一步：本地验证、显式提交 PR-B 文件、创建 PR、提交同一 ChatGPT 对话审核。
- 只有 PR-B 明确 `APPROVE` 后，才允许在外部 DATA 中执行 ADCdb/Atlas 生产运行。
