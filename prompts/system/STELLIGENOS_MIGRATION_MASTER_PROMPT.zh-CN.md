# StelligenOS Migration Master Prompt

在开始任何后续 Phase 前，先遵守 `docs/architecture/contract.zh-CN.md`。

## Repository Boundary

StelligenOS 仓库是 biotechnology asset operating system 的实现仓库，不是数据库仓库。

允许：

- architecture docs
- prompts
- schemas
- scripts
- code
- reference examples
- toy examples
- report templates
- demo assets
- golden test cases

禁止：

- large datasets
- raw sequencing
- intermediate files
- caches
- outputs
- temporary artifacts
- data-bearing working files

所有数据和数据处理都必须放在仓库外部的独立工作区。

## 当前工作范围

### Phase 0

- Repository Audit
- inspect the actual repository contents
- identify implementation docs, prompts, scripts, and any legacy text

### Phase 0.5

- Legacy Inventory
- map old components into a migration matrix
- focus on `AssetGenOS`, `GenModule`, `DueDiligence`, gate/rule/evidence text, legacy prompts, backup archives, and KB notes

## 必须产出

Phase 0 / 0.5 work should produce:

- `docs/phases/PHASE_0_REPORT.zh-CN.md`
- `docs/phases/PHASE_0_REVIEW_CHECKLIST.zh-CN.md`
- `docs/phases/PHASE_0_5_REPORT.zh-CN.md`
- `docs/phases/PHASE_0_5_REVIEW_CHECKLIST.zh-CN.md`
- `docs/architecture/legacy_inventory.zh-CN.md`
- `logs/migration_log.zh-CN.md`
- `logs/worklog.md`
- `manifests/phase_0_manifest.yaml`
- `manifests/phase_0_5_manifest.yaml`

## 架构规则

- `StelligenOS` is a biotechnology asset operating system.
- The repository contains one implementation of the operating system.
- The detailed architecture contract is separate from the operational prompt.
- The lifecycle uses `Asset Development`, not `Asset Advancement`.
- `AssetGenOS` is a subsystem of Opportunity Validation, not the whole system.
- `Knowledge Ledger` 是首选 cross-cutting 术语；迁移期间可兼容 `Evidence Ledger`。
- Due Diligence is stage-aware.
- Capability 和 lifecycle 是不同层。

## Phase 0.5 Inventory Checklist

Read and classify the legacy material:

- `AssetGenOS`
- `GenModule`
- `DueDiligence`
- gate / rule / evidence content
- IP/FTO content
- lifecycle or state content
- portfolio content
- prompt material
- backup archives
- KB prompt notes

For each important legacy component, record:

- current path
- current responsibility
- maturity
- target position in StelligenOS
- migration value
- migration risk
- recommended status
- evidence

## 停止条件

Do not start Phase 1 until Phase 0.5 has a completed migration matrix, the updated architecture contract is in place, and the repository docs consistently describe Phase 0 + Phase 0.5 as completed.
