# ChatGPT 审核记录：架构说明文档 v5（Blueprint v1.3 对齐）

- 日期：`2026-08-27`
- PR：#94 `task_20260827_architecture-v5-blueprint-alignment`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`
- 被审核 HEAD：`37fa6c2`
- Merge 提交：`ea9dc04`（`Merge pull request #94: architecture v5-draft — Blueprint v1.3 alignment`）
- 结论：**APPROVE**

本记录在**独立 PR**（`task_20260827_v5-approval-record-and-snapshot`）中补登。
按 `docs/architecture/versions/README.md` 与 v4-refresh 先例，审核方的 `APPROVE`
在 PR #94 内容冻结（`37fa6c2`）之后才到，不能在该 branch 上再加文件，否则改掉
被批准的 HEAD。

## 两轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `98fc29f`（v5-draft 首版，含 §16 问题 18–27） | `REQUEST_CHANGES`，6 点 |
| 2 | `37fa6c2`（docs-only 收敛修订） | `APPROVE` |

## 第一轮 REQUEST_CHANGES 的 6 点及关闭方式

1. **治理定位。** `NO_ARCHITECTURE_CHANGE` 不成立（spec 已变、runtime 未变）。
   → 改为 `DOC-LEVEL ARCHITECTURE ALIGNMENT / NO_RUNTIME_CONTRACT_CHANGE`；
   CURRENT_SYSTEM 新增 §0.3 Runtime Conformance block（Target architecture vs
   `core_objects@1.1` / `gate_system@0.1.0` topology `0.2.0` / envelope `2.1.0`；
   `Runtime conformance = MIGRATION_PENDING`；未合并 migration PR 前不得声称
   Blueprint v1.3 conformance）；`contract.zh-CN.md` §3.4.3 同步。审核方明确
   **本 PR 不要求同步修改 `core_objects.yaml` / `gate_system.yaml`**。
2. **§4.5 crosswalk 不能把 legacy composite 说成纯新对象。**
   → 改为 LEGACY → TARGET migration crosswalk：`Opportunity` = orchestration
   wrapper；`ClinicalHypothesis` = legacy composite（→ Context + Candidate +
   biomarker/product hypothesis reference；lock state → Context maturity）；
   `ADCConstruct` = 跨 L9/L10 composite；`LeadSeries` = L11 series/container；
   `Biomarker`/`Endpoint`/`Epitope`/`Linker`/`Payload`/… 移入独立表
   「`core_objects@1.1` 尚缺的 Candidate Types」。
3. **不要重开 45 Gate。**
   → §6.3 改写为 `LEGACY_GATE_SYSTEM ... status = FROZEN_LEGACY`；不重写、
   不原位转换、不重开冻结计数；Candidate-Level canonical GateSets 建立独立
   versioned lineage。§16 B 组问题 19 改为「不修改 frozen topology 前提下的
   migration/compatibility strategy」。
4. **「一 Gate 一主 Module」与现有 broad GenModule 的冲突。**
   → §8 新增边界段 + §8.4：现有 multi-purpose GenModule（`target_safety` 跨
   `TGT-04/05/07`）= shared evidence provider / shared analysis engine /
   legacy composite library，不拥有任何 Gate 的 scientific decision
   ownership；未来每个 Gate 仍有独立 primary Module。
5. **§11.2 CRC lock → Gate 的 evidence ceiling 错误。**
   → 改「贡献证据给」而非「满足」：eligible clinical context lock → upstream
   L1 Context freeze；`EVGAP-01` → contributes evidence to `TGT-04`，不能单独
   discharge antigen density requirement；`EVGAP-02` → primarily contributes
   to `TGT-02`，不自动支持 `TGT-03`；`TGT-03` 需独立的
   treatment/metastasis-context evidence。
6. **§16 把已被 Blueprint 决定的事继续写成开放问题。**
   → 重构为 **A 组 RESOLVED BY BLUEPRINT v1.3**（A1 泛化 Candidate / A2
   canonical GateSets / A3 sponsor 轴非 canonical Gate / A4 Knowledge Ledger ⊋
   EvidencePackage Library / A5 Target 先行 / A6 BVG + human APPROVE 并行）
   与 **B 组 IMPLEMENTATION / MIGRATION BLOCKERS**（18 Instantiation machine
   contract / 19 legacy 45-Gate migration / 20 EvidencePackage no-grade +
   Assessment schema / 21 CRC lock → Gate 映射 / 22 legacy GenModule 重新分类
   / 23 runtime migration PR 顺序，直接给出 PR A–E 推荐序列）。

## 批准范围（审核方原话要点）

- APPROVE PR #94 @ `37fa6c2`；PR 仍 open、mergeable，PR body 已同步为
  `DOC-LEVEL ARCHITECTURE ALIGNMENT / NO_RUNTIME_CONTRACT_CHANGE`。
- 6 个 blocker 均已关闭；architecture-spec 与 runtime implementation 已通过
  `MIGRATION_PENDING` 正确分层。
- 这版足以作为 **Blueprint v1.3 → StelligenOS runtime migration 的正式治理
  基线**。**不建议再修改 `CURRENT_SYSTEM v5-draft`**——继续改的边际收益已明显
  低于开始施工。
- 后续按文档冻结的顺序：
  **PR A Core decision objects → PR B canonical Gate/GateSet contracts →
  PR C Matrix/Provenance → PR D `CRC-ADC-TARGET-GATESET-v1` →
  PR E+ `TGT-01`–`TGT-08` primary Modules**。
- 必须坚持主从关系：**StelligenOS 是产品；Candidate × Gate Matrix +
  Evidence Packages 是核心产品形态**；ADCdb、CRC-Atlas、legacy GenModules
  都是给 Gate Module 使用的材料库 / shared engine / 施工设备，不能再自行产生
  产品 roadmap。

## 操作层说明

审核方尝试通过 GitHub connector 直接给 PR #94 写入 `APPROVE` review，GitHub
返回 `403 Resource not accessible by integration`，未能把 review 状态写回
GitHub。这是 connector 权限问题，不影响审核结论。GitHub 上 PR #94 因此没有
formal review 记录，实际 `APPROVE` 以本文件与对话为准。

## 边界

本次审核仅针对 v5-draft 文档。它是 **architecture-specification** 批准，
**不是** runtime implementation 批准：`core_objects.yaml` / `gate_system.yaml`
/ `src/` 仍为 legacy，`MIGRATION_PENDING` 未解除。任何执行 agent 在 PR A–E
合并前不得声称 repository 已实现 Blueprint v1.3 conformance。
