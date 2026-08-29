# Handoff：Runtime Migration PR E2 —— MOD-TGT01 Implementation

## 任务信息

- 任务编号：`task_20260829_runtime-migration-pr-e2`
- 分支：`task_20260829_runtime-migration-pr-e2`
- 基线：`origin/main`（PR #106 merge + PR #107 approval record 之后，E1 收口）
- PR：待创建
- 时间：`2026-08-29`
- 授权：用户 PR E1 APPROVE 后追加 "go ahead"；开工前审核方（ChatGPT
  `AI审核方案`）拍了 8 个 scoping 决策（E2-1…E2-8）。
- 变更定位：`RUNTIME_IMPL_ADD`（第五层：TGT-01 primary Evidence Production
  Module 的**确定性科学核心实现** + 一次极窄的 repository-policy reconciliation。
  不接真实 provider、不上网、不落盘、不产 canonical 记录、不解除
  `MIGRATION_PENDING`）。

## 一、8 个 scoping 决策（审核方在 `AI审核方案` 拍板，写代码前）

| # | 决策 |
|---|---|
| E2-1 | E2 是**真正的确定性实现**，不再拆 skeleton PR。`module_version = 1.0.0`。不做 CLI / crawler / DB / 后台任务 / human-review UI。 |
| E2-2 | Module 内**不实现任何 source-specific live provider**，只定义一个 normalized `Tgt01PrecedentProviderPort`。`failure_attribution = TARGET_MEDIATED` 只能来自明确 primary-source disclosure，Module 不做自由文本 NLP 推断。 |
| E2-3 | ADCdb 仍只是 discovery / entity-resolution / index 层，在 port 之后。未解析的 database-only 行是 retrieval lead，永不确立 ladder rung。 |
| E2-4 | 输出全部是 in-memory `Tgt01ModuleRunResult`，仓库零 persistence。`evidence_id` 由 injected allocator 给，Module 不扫文件系统自增。 |
| E2-5 | Direction × Strength 确定性、严格 E1 语义、无 score、无第四套 ladder。adverse pattern 只有满足冻结 item 08（≥2 个独立同靶点项目、一致 target-mediated failure）才成立；单个 failed ADC 永不 NEGATIVE / fatal。 |
| E2-6 | stop rule 是 **machine-enforced prerequisite**：`same_target_program_inventory_complete` 与 `failure_reason_sweep_complete` 都为真，才可能产出可接受 proposal —— 即使已经找到 DIRECT positive precedent。 |
| E2-7 | 一次极窄的 repository-policy reconciliation：允许顶层 `gate_modules/` 源码；live retrieval / execution / persistence 仍 forbidden；TGT-01 `primary_module_version` `0.0.0 → 1.0.0`。E1 施工合同正文与 TGT-01…08 全部 Gate science 一字不动。 |
| E2-8 | CI 只跑 synthetic / in-memory 验收用例，不联网、不用真实 ADC 数据，用 synthetic `TARGET_A` / `PROGRAM_A`。 |

边界一句话：

- **PR E2 owns**：normalized evidence → Gate-specific scientific interpretation
  → EvidencePackages → assessment proposal envelope
- **PR E2 does NOT own**：web retrieval → database / cache → source registry
  persistence → human approval → canonical persistence

## 二、交付物

### 2.1 `gate_modules/`（新顶层目录）

`gate_modules/README.md` —— 目录说明 + 五条 kernel invariant（镜像
`extensions/README.md`）：单向依赖（`src/` 永不 `import gate_modules`）；内核定义
合同、Module 实现合同（不改 Gate id / question / ladder / ceiling / fatal /
unknown / conflict / inference）；Module 不产 canonical 记录、不产 Decision /
KILL；仓库 data-free、零 persistence、不上网、不开 subprocess、不自增 ID；Module
只做 Gate-specific 科学判读，共享 infra（v5 §6.5）不按 Gate 重写。

`gate_modules/tgt01_adc_modality_precedent/`：

| 文件 | 内容 |
|---|---|
| `module.yaml` | 身份（`MOD-TGT01` / `1.0.0` / `built_in: runtime_migration_pr_e2`）、gate binding、the-one-question、owns / does_not_own、ports、`boundary_flags`（全部保守 `false`）。 |
| `contracts.py` | frozen dataclass：`NormalizedPrecedentRecord`（provider 输出，含 `failure_attribution` + `failure_attribution_from_primary_source` 锁）、`Tgt01ModuleInput`（8 个 identity pin + run context，`evidence_regime` 必须 `PUBLIC_ONLY`，无隐式默认）、`ClassifiedPrecedent`、`AssessmentProposalEnvelope`（E1 item 12：identity pins + proposed_direction/strength + evidence_refs + aggregation_rationale + critical_unknowns + evidence_ceiling；**不带** `assessment_id` / `assessment_version` / `review` —— `CANONICAL_ONLY_FIELDS` 常量供测试断言）、`SweepCompletionRecord`、`MachineAcceptanceRecord`、`Tgt01ModuleRunResult`。 |
| `ports.py` | Protocol：`Tgt01PrecedentProviderPort`（`fetch_precedents` + `sweep_completion`）、`EvidenceIdAllocatorPort`、`SourceRegistryPort`。 |
| `classify.py` | 逐条把 `NormalizedPrecedentRecord` 放到**冻结的 TGT-01 Evidence Ladder**：DIRECT = 同靶点 approved / late-clinical + disclosed activity；INDIRECT_STRONG = 同靶点 phase-1；WEAK = adjacent-target clinical / 同靶点 preclinical / patent。未解析 primary source → reject（retrieval lead）；source_id 未在 registry → reject。discontinued 同靶点 + target-mediated（primary-source）→ `ADVERSE_CANDIDATE`；其它 discontinued → `CONTEXTUAL`。 |
| `evidence.py` | 从 admissible record 构造 PR A `EvidencePackage`（`measurement` / `provenance` / `interpretation_boundary`（含冻结 allowed / forbidden inference + `evidence_ceiling`）/ `derivation`）。`evidence_id` 来自 allocator。`(source_id, claim)` 去重。 |
| `aggregate.py` | 确定性 Direction × Strength（E2-5 规则表）；`adverse_pattern = ≥2 个独立 `ADVERSE_CANDIDATE` program`；strength = 实际命中最强 rung（`DIRECT>INDIRECT_STRONG>WEAK`）；UNKNOWN state（无 admissible）→ `INCONCLUSIVE` + `UNKNOWN` + 无 refs。 |
| `acceptance.py` | machine acceptance（E1 item 13）+ item 16 stop-rule 前置：每个 EP 合法、每个 emitted record 有 resolved primary source、只用冻结 admissible class、strength 不超过命中 rung、无重复 `(source_id, claim)`、每个 evidence_ref 指向 emitted EP、**两个 sweep completion flag 都为真**。任一硬失败 → `accepted = False`、无 proposal envelope。 |
| `module.py` | 纯 Python `run(module_input, *, provider, evidence_id_allocator, source_registry, target_identity)`：fetch → classify → build EP → aggregate → evaluate → （accepted 才）build envelope → `Tgt01ModuleRunResult`。只调 injected port。 |

### 2.2 repository-policy reconciliation（E2-7）

- `scripts/verify_repository_boundary.sh`：`allowed_top_level` 增 `"gate_modules"`。
- `src/contracts/crc_adc_target_gateset.yaml`：
  - TGT-01 gate_binding `primary_module_version: "0.0.0" → "1.0.0"`；
  - `primary_module_binding.built_module_versions: {TGT-01: "1.0.0"}` + rule 改词；
  - `repository_policy`：`evidence_production_module_in_repository: forbidden` 换成
    `gate_module_source_code_in_repository: allowed` +
    `gate_module_live_retrieval_execution_or_persistence_in_repository: forbidden`。
- `src/objects/crc_adc_target_gateset.py`：`BUILT_MODULE_VERSIONS`（`{"TGT-01": "1.0.0"}`）
  + `expected_primary_module_version(gate_id)`；`TgtGateContract.__post_init__`
  的「必须 == 0.0.0」改成「== 该 gate 的 expected version」。**Gate science
  一字未改。**

### 2.3 测试

- `tests/test_tgt01_module.py`（synthetic）：DIRECT / INDIRECT_STRONG / WEAK
  positive；无证据 → UNKNOWN state；单个 failed ADC 不 NEGATIVE；两个独立一致
  target-mediated failure → NEGATIVE（adverse pattern）；construct-specific 两个
  不成 pattern；positive + adverse pattern → CONFLICTING；未解析 ADCdb-only lead
  不建 rung；未解析 source_id → reject；sweep 不完整（三种）→ run rejected 且
  positive ceiling 不能绕过；重复 `(source, claim)` → 丢一条；输入契约无隐式默认
  （错 gate_id / gateset_id / regime / instantiation / candidate level → `ValueError`）；
  strength 不超过命中 rung；envelope 带全 8 个 identity pin 且**不带**
  `assessment_id` / `assessment_version` / `review`；Module 不构造
  `CandidateGateAssessment` / `Decision`；run result 纯 in-memory。
- `tests/test_gate_modules_boundary.py`：`src/` 永不 `import gate_modules`；Module
  不 import `extensions` / `genmodules`；Module 不 import
  socket / http / urllib / requests / subprocess / sqlite3 等；`gate_modules` 在
  boundary 脚本 `allowed_top_level`；无 data-like 文件；文件名无空格；无
  `__pycache__`；`module.yaml` ↔ 包常量 ↔ CRC gateset binding 三方 parity；
  `boundary_flags` 全保守。
- `tests/test_crc_adc_target_gateset.py`：`NoModuleInPrDTests` → `ModuleBindingSlotTests`
  （per-gate expected version：TGT-01 = `1.0.0`，其余 `0.0.0`；`built_module_versions`
  parity；新增 `test_tgt01_module_is_built_in_gate_modules`）。
- `tests/test_tgt01_module_construction_contract.py`：E1 的
  `test_no_gate_modules_top_level_directory_yet` →
  `test_e1_shipped_no_implementation_under_gate_modules`（若 `gate_modules/` 存在，
  必须是 `built_in: runtime_migration_pr_e2`，指向 E1 施工合同）。

## 三、明确未改 / 未做

- **未接**任何真实 provider / adapter；**未上网**、未开 subprocess、未建
  database / cache；**未落盘**（输出全 in-memory）；**未自增 ID**（injected
  allocator）。
- **未加** numeric score；**未加**新 scientific ladder semantics —— 冻结 TGT-01
  ladder / `evidence_ceiling` / allowed·forbidden inference / `fatal_conditions`
  / `unknown_behavior` 全部逐字复现。
- **未改** PR A / B / C 合同或对象；**未改** PR D 的 Gate science（只动
  `primary_module_version` slot + `repository_policy` 措辞）；**未改** E1 施工
  合同正文（`src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml` 未动）。
- **未构造** canonical `CandidateGateAssessment`（PR A：`HUMAN_APPROVED` only，由
  review surface 在批准后构造）；**未产** `Decision` / `KILL`；**未写**
  `MatrixView`。
- **未解除** `MIGRATION_PENDING` —— 8 个 primary Module 只做完 1 个。无新依赖。

## 四、验证命令与结果

```
find . -name __pycache__ -not -path './.git/*' -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
# -> Ran 807 tests ... OK   (774 baseline + 33 new: test_tgt01_module + test_gate_modules_boundary)
git diff --check                       # clean
bash scripts/verify_repository_boundary.sh   # 干净 tracked-tree worktree 上 pass
python3 -c "import yaml; yaml.safe_load(open('gate_modules/tgt01_adc_modality_precedent/module.yaml'))"  # 结构合法
```

## 五、审核

- 提交至 ChatGPT 网页版 `Biotech ideas` → `AI审核方案` 对话（Claude 通过浏览器
  自动化贴入；GitHub connector 写 review 仍 `403`）。审核重点：8 个 scoping 决策
  是否落实、冻结 TGT-01 ladder / fatal / inference / unknown 是否逐字复现、是否
  确实无 provider / 网络 / 落盘 / numeric score / canonical 记录、
  repository-policy reconciliation 是否只动措辞与 module_version slot。
- REQUEST_CHANGES → 同一 PR 最小修订、复跑、更新本 handoff 与 worklog、回同一对话
  复审。APPROVE → merge + 独立 docs-only approval-record PR（按 PR
  #95/#97/#99/#101/#103/#105/#107 先例）。

## 六、后续（PR E3+，未启动）

- **PR E3** —— 在 port 之后接真实只读 provider（ClinicalTrials.gov / PubMed /
  FDA / patent / ADCdb primary-source resolution），external workspace 跑真实
  calibration run。
- **PR E4+** —— 逐 Gate 施工图 + 实现，按 `TGT-05 → 08 → 02 → 03 → 04 → 06 →
  07` 顺序。
- 全部 8 个 primary Module 完成后方可解除 `MIGRATION_PENDING`。
