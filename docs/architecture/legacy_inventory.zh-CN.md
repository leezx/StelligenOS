# StelligenOS Legacy Inventory

## Purpose

Phase 0.5 的目标是把旧系统做成真正可迁移的映射表。

## Scope

Inventory 只覆盖已经发现的旧系统材料，并把它们映射到 StelligenOS 的目标位置。

### 主要源

#### 1. AssetGenOS 主仓库

- Path: `/Volumes/Stelligen_SSD/Stelligen/AssetGenOS`
- Status: 实际运行中的 ADC Asset Factory v0.2，包含 45 Gates、59 Models、3 个 GenModule、迁移档案、测试和完整治理约定。
- Maturity: 高
- Target position: `Opportunity Validation`, `Asset Generation`, `Asset Development`, `Cross-cutting services`
- Migration value: 很高
- Migration risk: 中到高，因其同时承载系统、实现、运行数据和历史档案
- Recommended status: `MIGRATE_WITH_ADAPTATION`
- Evidence: `README.md`, `AGENTS.md`, `LINKS.md`, `MODEL_PROGRESS_VERSION.md`, `genmodules/README.md`, `configs/v0.2_gate_groups.yaml`, `configs/v0.2_graph.yaml`

#### 2. Gate / Model contract and governance layer

- Path: `AssetGenOS/components/`, `AssetGenOS/components/contracts/`, `AssetGenOS/components/model_governance/`
- Status: 已实现的 Gate、Model、Profile、lifecycle 和 governance contract 层
- Maturity: 高
- Target position: `Opportunity Validation` 下的 Gate / Rule / Evidence / Versioning
- Migration value: 很高
- Migration risk: 中
- Recommended status: `MIGRATE_AS_IS`
- Evidence: `components/contracts/model_lifecycle.v1.0.yaml`, `docs/MODEL_LIFECYCLE_STANDARD_v1.0.md`, `components/model_governance/`

#### 3. Existing-binder GenModule

- Path: `AssetGenOS/genmodules/antibody_binder_asset_engineering/`
- Status: 已实现并可运行的已有 Binder 工程化 GenModule，版本 `0.4.0`
- Maturity: 高
- Target position: `Asset Generation / Route A`
- Migration value: 很高
- Migration risk: 中
- Recommended status: `MIGRATE_AS_IS`
- Evidence: `README.md`, `DESIGN.md`, `SOFTWARE_AND_DATA.md`

#### 4. Epitope-conditioned de novo GenModule

- Path: `AssetGenOS/genmodules/epitope_conditioned_de_novo_antibody_discovery/`
- Status: 已实现并可运行的 de novo 生成 GenModule，版本 `0.1.0`
- Maturity: 中到高
- Target position: `Asset Generation / Route B`
- Migration value: 很高
- Migration risk: 中
- Recommended status: `MIGRATE_AS_IS`
- Evidence: `README.md`

#### 5. Biotech asset due diligence GenModule

- Path: `AssetGenOS/genmodules/biotech_asset_due_diligence/`
- Status: 已实现的垂直切片 due diligence GenModule，Phase 1A 已验证
- Maturity: 中到高
- Target position: `Cross-cutting Due Diligence`
- Migration value: 高
- Migration risk: 中
- Recommended status: `MIGRATE_AS_IS`
- Evidence: `README.md`, `DESIGN.md`

#### 6. Legacy archives and backups

- Paths:
  - `/Volumes/Stelligen_SSD/Stelligen/AssetGenOS/archive/AssetGenOS-v0.1.0.tar.gz`
  - `/Volumes/Stelligen_SSD/Stelligen/BACKUPS/AssetGenOS-pre-packet-refactor-20260729-152514.tar.gz`
  - `/Volumes/Stelligen_SSD/Stelligen/BACKUPS/AssetGenOS-20260731.zip`
  - `/Volumes/Stelligen_SSD/Stelligen/BACKUPS/AssetGenOS-pre-standard-v1.1-20260729-151352.tar.gz`
- Status: 历史版本与恢复包
- Maturity: 已冻结
- Target position: `Archive / reference only`
- Migration value: 中
- Migration risk: 低
- Recommended status: `ARCHIVE`
- Evidence: 文件名与 archive 目录结构

#### 7. Prompt and evidence notes in Zhixins-KB

- Paths:
  - `/Volumes/Stelligen_SSD/Stelligen/Zhixins-KB/2.Biotech/Clinical ADC Gate Evidence Extraction Prompt v1.md`
  - `/Volumes/Stelligen_SSD/Stelligen/Zhixins-KB/2.Biotech/Clinical ADC Gate Evidence Extraction Prompt v1.1.md`
  - `/Volumes/Stelligen_SSD/Stelligen/Zhixins-KB/2.Biotech/Clinical ADC Gate Evidence Extraction Prompt v1.2.md`
  - `/Volumes/Stelligen_SSD/Stelligen/Zhixins-KB/Clippings/WO2016096610 ANTIBODY-DRUG CONJUGATES (ADCS) OF KSP INHIBITORS WITH AGLYCOSYLATED ANTI-TWEAKR ANTIBODIES.md`
  - `/Volumes/Stelligen_SSD/Stelligen/Zhixins-KB/Templates/Partner Gate Template v2.md`
- Status: 外部知识库输入
- Maturity: mixed
- Target position: `Reference only` for prompts, templates, and case notes
- Migration value: medium
- Migration risk: low to medium
- Recommended status: `REFERENCE_ONLY`
- Evidence: external KB file paths

#### 8. Data-like residue inside AssetGenOS

- Path: `AssetGenOS/data/adc_factory.sqlite3`
- Status: local data store / working residue
- Maturity: operational
- Target position: outside the implementation repository or behind a strict external data boundary
- Migration value: low for StelligenOS; high for AssetGenOS cleanup
- Migration risk: high if left in an implementation repo
- Recommended status: `MOVE_OUT_OF_REPO`
- Evidence: file path and file type

## Output

For each important item record:

- current path
- current responsibility
- maturity
- target position in StelligenOS
- migration value
- migration risk
- recommended status
- evidence

## Non-goals

- No code rewrite
- No deletion in this phase
- No data migration
- No lifecycle implementation
