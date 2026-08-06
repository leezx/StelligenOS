# Handoff：StelligenOS 当前设计架构与模块逻辑 v3

## 任务

- 分支：`task_20260806_current-architecture-v3`
- 基线：`main@8aa7e87`
- 文档版本：`v3-draft`
- 架构审核基线：`STELLIGENOS-ARCH-2026.08.06-v3-draft`
- 状态：`PENDING_EXPERT_REVIEW`

## 变更范围

本任务只更新当前架构说明、架构入口、版本说明、README 和审计记录；不修改
核心对象、生命周期、Gate、Model、Profile、GenModule 合同或外部数据。

主文档现在区分：

- 已进入 `main` 的内核和模块逻辑；
- 仅合同化、仍依赖外部 runtime 的能力；
- 已登记但未接通的 Biotech/患者数据基础设施；
- CRC Level 01 Preview 与 Accepted pool 的差异；
- 截至 2026-08-06 的开放 PR 和阻断；
- 仅登记、未进入内核的 extensions。

## 事实基线

- 8 个核心对象、4 阶段生命周期、9 类 capability。
- 45 个 Gate：13 Target Opportunity、16 Product Realization、16 Commercial Executability。
- AssetGenOS 软件目录：7 contracts、45 Gates、59 Models、53 Profiles。
- 7 个模块区域，其中 6 个有 `module.yaml`。
- CRC Level 01：9 contexts、41 targets、369 raw pairs、22 provisional pairs、0 active-for-Level-02。
- 当前 `main` 测试基线：338 tests。

## 明确未做

- 未把 PR #62 或 #63 的内容写成 `main` 已完成事实。
- 未执行数据下载、provider、Gate、模型、EVGAP 或资产生成。
- 未创建 `v3` 冻结快照；只有审核批准后才能创建。
- 未修复 Gate envelope `2.0.0`/`2.1.0` 漂移或缺失 module manifest；只登记为审核问题。

## 审核重点

请重点核对主文档第 15 节的 12 个问题，以及“已实现／合同化／外部运行／规划／
待审核”的状态划分是否准确。若返回 `REQUEST_CHANGES`，只在同一任务分支修订
本文档范围；若返回 `APPROVE`，再创建只读 `v3` 快照并更新版本索引。
