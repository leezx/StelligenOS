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

## 四之二、第一轮修订（PR #108 @ `57d0c99` REQUEST_CHANGES）

审核方（ChatGPT `AI审核方案`）复审 `57d0c99`：**外层 architecture PASS**（scope /
no-live-provider / no-persistence / `gate_modules/` 单向依赖 / 窄 policy
reconciliation 全部认可）。只剩 **4 个 E2 deterministic-core correctness
blocker**，不需要重新设计架构；E2-1…E2-8、Gate id/question、冻结 ladder、
allowed/forbidden inference、UNKNOWN 语义、repository layout、`MIGRATION_PENDING`、
`1.0.0` 治理方向都不动。

1. **Candidate ↔ target identity 没锁死。** `run()` 收一个独立可漂移的
   `target_identity` 字符串直接交给 provider，未与 candidate 的 canonical target
   校验（HER2 candidate + TROP2 target_identity → 生成 HER2 candidate 的 EP）。
   `NormalizedPrecedentRecord` / EP 只存 `target_relation` 布尔，不存 ADC 项目
   实际 targeting 的抗原，也没有 adjacent 的 basis —— E1 item 14 的 human
   same/adjacent 复核没有事实依据。
   **修**：`target_identity` 移到 `Tgt01ModuleInput`（唯一权威），`run()` 不再
   收该参数；`NormalizedPrecedentRecord` 加 `program_target_identity` +
   （ADJACENT 必填）`adjacency_basis`；`classify_record` 拒绝
   `SAME_TARGET` 但抗原不符（misbinding）与错标的 adjacency；EP `study_context`
   保留 `program_target_identity` / `target_relation` / `adjacency_basis`。
2. **冻结 item-08 fatal 只实现一半。** frozen 是「≥2 independent same-target
   programs discontinued for a consistent on-target/target-mediated toxicity
   **OR an intrinsically unachievable therapeutic window**」，代码只查
   `TARGET_MEDIATED`；且「consistent」被约化成「都是 TARGET_MEDIATED」。
   **修**：`FAILURE_ATTRIBUTION_VALUES` 显式两条 frozen branch
   （`TARGET_MEDIATED_TOXICITY`、`INTRINSIC_THERAPEUTIC_WINDOW`）+
   `CONSTRUCT_SPECIFIC` / `NON_TARGET` / `UNDISCLOSED`，仍要求 primary-source
   attribution；`aggregate()` 只有「同一 frozen class 且 ≥2 个独立同靶点
   program」才成 pattern；不同 class 混合不算 consistent；单个永不 fatal。
3. **PR C reusable EvidencePackage 语义没实现（架构层最重要）。**
   `existing_evidence_ids` 定义了没用，`evidence.py` 每条 observation 都新建
   EP → 破坏 PR C 全局 Evidence Library；EP 被写成 TGT-01-specific
   （`directly_supports = "ADC-modality feasibility..."` / `TGT01_EVIDENCE_CEILING`），
   adverse EP 也说「supports ADC-modality feasibility」却被标 CONTRADICTING，
   自相矛盾；`SourceRegistryPort` 只返回 bool。
   **修**：新增 `ExistingEvidenceLibraryPort`（按 `observation_id` 命中即复用
   `evidence_id`，novel 才 allocate）；`SourceRegistryPort` →
   `SourceResolverPort.resolve(source_id) -> CanonicalSourceRecord | None`，EP
   provenance 用 canonical metadata，provider metadata 不符则 reject；EP 改成
   **Gate-NEUTRAL**（observation-level `directly_supports` / `does_not_support` /
   `limitations` + 中性 observation-level `evidence_ceiling`），TGT-01 ceiling /
   inference / Direction×Strength 只留在 proposal 层。
4. **`program_id → evidence_id` 数据模型错误，会静默串错 EvidenceRef。**
   一个 program 两条 observation → 第二条覆盖 map，两个 ref 都指向第二个 EP，
   第一个 EP 无人引用。
   **修**：`build_evidence_packages` 返回 `list[EmittedEvidence]`（一条
   admissible observation → 一个 EP），不再 program-keyed；`program_id` 只用于
   fatal pattern 的「independent programs」去重；同 program 的重复
   `(source_id, claim)` 干净 drop。

同步：`ports.py`（4 个 port）、`__init__.py`（导出）、`module.yaml`
（ports + owns 改词）、`tests/test_tgt01_module.py`（fakes 重写 + 新增
misbinding / adjacent EP 事实恢复 / 两条 INTRINSIC_THERAPEUTIC_WINDOW → NEGATIVE /
单条 intrinsic 不 fatal / 混合 class 不成 pattern / 同 program 两 observation →
两 EP 两 ref / library 复用 / canonical source 解析 / Gate-neutral EP）。

**仍未改：** E2-1…E2-8 scope、Gate id/question、冻结 DIRECT/INDIRECT_STRONG/WEAK
ladder、allowed/forbidden inference、UNKNOWN 语义、repository layout、
no-live-provider 边界、no persistence、`MIGRATION_PENDING`、TGT-01
`primary_module_version = 1.0.0` 治理方向。

验证：全量 `unittest discover` **818 OK**（774 baseline + 44 E2）/
`git diff --check` clean / 干净 tracked-tree worktree boundary passed /
`module.yaml` 结构合法。

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
