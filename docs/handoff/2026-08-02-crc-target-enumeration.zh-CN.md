# 任务交接备忘：CRC indication/endpoint/target 全靶点枚举

## 任务信息

- 任务编号：`task_20260802_crc-target-enumeration`
- 分支：`task_20260802_crc-target-enumeration`
- 基线：`origin/task_20260801_gen-iet-phase8-external-pilot`
- PR：https://github.com/leezx/StelligenOS/pull/28
- Review tip at PR creation: `f4ecbe5`
- Latest PR tip observed for review: `2f1c17b`
- 说明：PR #27 已合并到该基线分支；`origin/main` 尚未包含 PR #27，因此本任务暂以实际已合并治理基线为 base，不伪装为 main 已同步。
- 当前状态：`APPROVED_EXTERNAL_RUN_AUTHORIZED`
- 时间：`2026-08-01 America/New_York`

## 本次改动

- 新增 CRC indication/endpoint/target 全靶点枚举执行契约。
- 固定 9 个初始 CRC indication 的来源状态，不把 derived strategy 升级为 canonical fact。
- 固定 OS/PFS/ORR+DOR/safety endpoint 层级。
- 定义 ADC target 的公共证据、内吞/递送、正常组织风险、反对证据和 unknown 语义。
- 规划所有外部输出路径和审计文件。

## 明确未执行

- 未抓取公共文献或临床注册库。
- 未下载或分析 TCGA/GEO/单细胞/空间/蛋白组等公共数据。
- 未生成任何 pair、target ranking、Gate 分数或资产。
- 未修改 Gate、Model、Rule、Registry 或架构冻结内容。
- 未向 StelligenOS 写入数据、cache、result、数据库、weights 或临时产物。

## 验证与审核门

- `scripts/verify_repository_boundary.sh`：通过。
- `git diff --check`：通过。
- PR #28 已创建并推送，当前审核 tip 为 `2f1c17b`。
- ChatGPT `APPROVE` 前不得执行外部文献/公共数据枚举。
- 运行结果完成后必须另行提交结果审核 PR。

PR 页面是当前分支 tip 和 aggregate diff 的实时权威；本 handoff 的 PR 创建 tip 是审核快照，不自引用后续更新本 handoff 的提交。

ChatGPT Round 2 已返回 `APPROVE`，明确允许开始外部 CRC 文献/公共数据枚举；运行只能写入指定外部 `DATA` 目录，完成后必须提交独立结果审核 PR。

## 下一步

1. 验证仓库边界和文档 diff。
2. 显式提交、推送并创建 PR。
3. 在 `GitHub PR 信息` 对话中提交审核指令。
4. 只根据 ChatGPT 反馈在同一 PR 修订，直到明确 `APPROVE`。

## 数据边界声明

本仓库只保存架构、执行契约、代码和治理记录；所有数据、文献下载、分析缓存和结果均位于仓库外部。
