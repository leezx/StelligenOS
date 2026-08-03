# CRC indication/endpoint/target Gate 评分执行契约

- 任务分支：`task_20260802_crc-gate-scoring-contract`
- 前置工作包：PR #35，ChatGPT `APPROVE`
- 当前状态：contract-only，等待 ChatGPT 审核

## 目的

定义对 CRC indication/endpoint/target evidence package 进行系统性 Gate 评分的执行边界。此 PR 只冻结输入、顺序、输出和阻断规则，不执行评分，不生成分数、排序或 pair 推荐。

## 固定输入

- 外部专家复核完成并经独立结果审核 PR 批准的 evidence package。
- 当前准备包基线为 292 条 evidence units、41 targets；supporting/opposing/unknown 为 88/32/172。
- StelligenOS 已冻结的 45-Gate 拓扑、既有 Gate identity、model/profile 和依赖顺序。
- 外部 ADC Index、公共文献和公共数据的可追溯引用；不得将数据复制入本仓库。

## 评分原则

- 只使用已冻结的 Gate、Model、Rule、Profile 和版本化外部输入；不得新增 Gate 或临时改写权重。
- 每个 Gate 输出分数、状态、证据引用、缺失项、反对证据和审计元数据。
- `unknown`、缺失信息和 `null` 不得自动转为 0、negative 或 pass/fail。
- Hard Gate 失败或关键证据未解决时，保留阻断状态，不得用总分覆盖。
- 评分必须按冻结拓扑和依赖顺序执行；不得跳过前置 Gate 或把后置推断倒灌为证据。

## 输出

- 外部 `DATA` 中的 per-Gate trace、summary、unknown/opposing evidence、输入 manifest、版本和 checksum。
- indication/endpoint/target/pair 的评分结果只能作为可审计评估结果，不自动生成资产、不自动晋级、不自动推荐。
- 运行完成后必须创建独立结果审核 PR；在 ChatGPT `APPROVE` 前不得发布排序、推荐或资产决策。

## 当前阻断

- 在真实专家复核完成并通过独立结果审核前，不得执行本契约。
- 在本契约获得 ChatGPT `APPROVE` 前，不得执行 Gate 评分。
- 本仓库不得写入数据库、cache、result、weights 或证据数据。

