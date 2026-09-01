# WorkLog —— Runtime Migration PR A–E16（Blueprint-v1.3 Candidate × Gate × Evidence runtime-conformance migration）

- 汇编日期：`2026-09-01`
- 状态：**COMPLETE**。PR A/B/C/D + PR E1…E16 全部 merge 入 `main`；八个 primary
  Evidence Production Module（MOD-TGT01…MOD-TGT08）全部建成 @ `1.0.0`；
  `src/contracts/crc_adc_target_gateset.yaml` 的每个
  `primary_module_binding.<gate> == "1.0.0"`；`MIGRATION_PENDING` 已解除。
- 收官测试：`main` 上全量 `unittest` **1900 OK**（迁移开始前约 555；PR A 首次
  APPROVE 时 609）。
- 本文件是整个迁移的**合并式 WorkLog**（做了什么 + 怎么做的）。逐 PR 的
  完整逐轮审核往返见 `logs/chatgpt-review-2026-08-2[89]/-30/-31/-2026-09-01-runtime-migration-pr-*.md`；
  逐 PR 的 scoping / IS-NOT 边界见 `manifests/runtime_migration_pr_*_manifest.yaml`；
  逐 PR 的中文 handoff 见 `docs/handoff/2026-08-*/2026-09-01-runtime-migration-pr-*.zh-CN.md`。
  `logs/worklog.md` 里也有逐条 append 记录，本文件是其归纳。

---

## 1. 背景与目标

### 1.1 起点（迁移开始前，已冻结并 merge）

- **Blueprint v1.3** —— 冻结。
- **`CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md` v5**
  （`STELLIGENOS-ARCH-2026.08.27-v5` / APPROVED，PR #94 / #95）。
- **`docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md`**（`v1.0` / APPROVED，
  PR #96；approval record PR #97）。

这三层是 **doc / spec 层**。它们刻意把 `core_objects.yaml` / `gate_system.yaml`
/ `src/` 留在 legacy 状态，`runtime conformance: MIGRATION_PENDING` 未解除 ——
runtime 落地就是本次 PR A–E16 迁移。

### 1.2 目标

把 Blueprint v1.3 / CURRENT_SYSTEM v5 §16 B 组的决策层模型（Candidate × Gate ×
Evidence，"one Gate → one primary Evidence Production Module"）真正落到可运行、
可测试、边界受控的 runtime 代码，并在**八个 primary Module 全部建成**后解除
`MIGRATION_PENDING`。

### 1.3 治理流程（每个 PR 一致）

```
task 分支
  → 需要审核的内容先提交给 ChatGPT 项目 Biotech ideas → 对话 AI审核方案
    （Claude 通过浏览器自动化把审核请求 / 逐轮回复贴入该对话）
  → 开 GitHub PR
  → CI 绿（python 3.11 + 3.12 矩阵，jobs verify (3.11) / verify (3.12)）
  → 提交 implementation / design-level review 给 AI审核方案
  → 每一轮 REQUEST_CHANGES 在同一 PR 分支上修复、commit、push、poll CI、回贴
  → APPROVE 后 gh pr merge <N> --merge --delete-branch=false
  → 另开一个独立 docs-only approval-record PR
    （审核记录 logs/chatgpt-review-<date>-runtime-migration-pr-*.md
     + manifest status: approved）
  → merge approval-record PR
  → 删除两个分支（本地 + 远端）
  → 追加 logs/worklog.md
```

- **实现类 PR（E 系列偶数 E2/E4/…/E16）** 还多一步：写代码前先把 pre-code
  scoping 提交给 `AI审核方案`（APPROVE-to-proceed + required tightenings），
  然后才建 11 文件 `gate_modules/<name>/` 确定性核心。
- **GitHub connector 每一轮都返回 `403 Resource not accessible by integration`**，
  formal GitHub review state 从未写回 —— **`AI审核方案` 对话结论为
  authoritative**，逐轮记录落在 `logs/chatgpt-review-*.md` + manifest。

---

## 2. 三段结构

| 段 | PR | 交付物 |
|---|---|---|
| **核心 runtime 契约 / 对象** | A、B、C、D | core decision objects + legacy adapters；canonical Gate / GateSet / EvidenceLadder / Decision；Matrix view + reusable EvidencePackage reference + provenance walk；`CRC-ADC-TARGET-GATESET-v1`（roster + 8 条 evidence ladder + GateSet + Instantiation + 8 个 gate_binding，`primary_module_version` 全部 `0.0.0` 槽位） |
| **八个 primary Module（施工合同 → 实现，交错）** | E1…E16 | 奇数 E = 某个 TGT 的 **construction contract**（design-only：17 项施工合同 + human-readable drawing + parity / validation 测试 + 17 项验收清单）；偶数 E = 对应的 **deterministic implementation**（11 文件 `gate_modules/tgt0n_*/` + 测试 + 窄 binding 对账） |
| **收口** | E16（同一个 PR 内） | MOD-TGT07 实现 + binding 对账 + **runtime-conformance 收口**：live docs 的 `MIGRATION_PENDING` → runtime conformance COMPLETE；`migration.deferred` 保留 |

### 2.1 Module ↔ Gate ↔ PR 对照

| Gate | Gate question（节选） | 施工合同 PR | 实现 PR |
|---|---|---|---|
| **TGT-01** | prior precedent that this target … is addressable by the ADC modality | E1 | E2 |
| **TGT-02** | in refractory mCRC, do malignant cells express the target at protein level with adequate cohort-level consistency | E7 | E8 |
| **TGT-03** | does target expression persist in the actual clinical setting (refractory / prior-treated and/or metastatic CRC) | E9 | E10 |
| **TGT-04** | is the target present on the cell surface at a density plausibly adequate for ADC payload delivery | E11 | E12 |
| **TGT-05** | accessible normal-tissue expression / target-mediated toxicity → on-target/off-tumor liability（fatal-first gate） | E3 | E4 |
| **TGT-06** | upon antibody binding, is the complex internalized and trafficked to a compartment compatible with payload release | E13 | E14 |
| **TGT-07** | circulating soluble form (shed ectodomain / secreted isoform) acting as antigen sink or altering PK / biodistribution | E15 | E16 |
| **TGT-08** | differentiated opportunity in refractory mCRC: unmet need, competitive landscape, IP whitespace | E5 | E6 |

建成顺序（按实现 PR）：TGT-01 → TGT-05 → TGT-08 → TGT-02 → TGT-03 → TGT-04 →
TGT-06 → **TGT-07（第八个也是最后一个，E16 解除 MIGRATION_PENDING）**。

---

## 3. 逐 PR 记录

> 每行：PR 号 / 分支 / 被审 HEAD / 审核轮数 / merge 提交 / approval-record merge /
> 全量测试数 / 一句话内容 + 关键 blocker。

### 段一：核心契约 / 对象

#### PR A —— core decision objects + legacy core-object adapters
- PR #98 `task_20260828_runtime-migration-pr-a`；被审 HEAD `f225e9f`；**2 轮**；
  merge `cbab012`；approval-record PR #99 merge `7555f8e`；全量 **609**。
- 内容：`decision_objects.yaml` + `decision_model.py` + `legacy_adapters.py`。
- Round 1 REQUEST_CHANGES 的 3 点（全部关闭）：deep immutability；nested schema
  parity（`review` 精确 3 key、`status == HUMAN_APPROVED`、`reviewer` 非空）；
  `missing_candidate_types` 清单不完整。方向 / scope 从一开始就 PASS、无架构越界。

#### PR B —— canonical Gate / GateSet / EvidenceLadder / Decision
- PR #100 `task_20260828_runtime-migration-pr-b`；被审 HEAD `51bfadb`；**2 轮**；
  merge `d18974b`；approval-record PR #101 merge `9aafc57`；全量 **658**。
- 内容：`gate_contracts.yaml` + `gate_model.py` + `legacy_gate_map.py`。
- Round 1 的 3 个 blocker（全部关闭）：canonical GateSet identity 不是
  invariant；`Decision.triggered_by` ↔ `assessment_snapshot` 无 cross-field
  一致性；"exact parity" 措辞不真实。2 个非 blocker（PR body 过期）merge 前直接
  编辑。

#### PR C —— Matrix view / reusable EvidencePackage references / provenance walk
- PR #102 `task_20260828_runtime-migration-pr-c`；被审 HEAD `d16b634`；**4 轮**；
  merge `91a8e5b`；approval-record PR #103 merge `5e7d2a6`；全量 **716**。
- 内容：`evidence_reference.yaml` + `evidence_reference_model.py`。
- Round 1 的 3 个 PR-C-local blocker：canonical provenance chain 声明 ≠ 实际
  checker（主 blocker）；MatrixView 未保证 row Candidate 属于 Matrix 的
  candidate_level；EvidenceIndex lifecycle 比冻结 spec 更窄 / boundary wording
  对 status 过宽。Round 2–3 收尾：新增
  `check_evidence_index_against_packages`，补上最后两处 layer-2 checker 自身的
  false-pass / identity gap。Round 4 APPROVE。

#### PR D —— `CRC-ADC-TARGET-GATESET-v1`
- PR #104 `task_20260828_runtime-migration-pr-d`；被审 HEAD `35298de`；**3 轮**
  （结构层 1 轮 + 科学 ladder 层 2 轮）；merge `16f5f01`；approval-record PR #105
  merge `9794c54`；全量 **751**。
- 内容：roster + 8 条 evidence ladder + GateSet + Instantiation + 8 个
  gate_binding（每个声明 `primary_module_id = MOD-TGT0n`、`primary_module_version
  = "0.0.0"` 槽位）。只复用 PR A/B/C。
- scoping：这是 **evidence-class proposal**，科学审核在 PR #104 内完成
  （REQUEST_CHANGES until scientifically acceptable → APPROVE = v1.0 frozen
  ladders）。
- Round 1：结构层 PASS（A2′+B1、label 非 gateset_id、roster 锁死
  TGT-01..08 / L04 / `1.0`、`0.0.0` Module slot）；科学 ladder 6 组最小修改。
  Round 2：TGT-01/03/04/06/07/08 六组接受，只剩 TGT-05 `fatal_conditions` 一个
  blocker（去掉 "preclude an ADC therapeutic window" 这类 product-window 结论，
  改成 target-level public-evidence 判断）。Round 3 APPROVE
  （Structure PASS / 8 条 ladder PASS / A2′+B1 PASS）。

### 段二：八个 primary Module（施工合同 → 实现）

> 奇数 E = design-only construction contract；偶数 E = deterministic
> implementation。实现类 PR 都遵循同一 11-file 包骨架：
> `__init__ / module.yaml / contracts / ports / classify / evidence / aggregate /
> completion / fatal_review / acceptance / module`；`run()` 是纯 injected-port
> Python，无 normalizer / scorer / threshold / 网络 / 子进程 / 持久化 /
> 数值强制转换 / generic base class。

#### PR E1 —— TGT-01 construction contract（design-only）
- PR #106；被审 HEAD `2596c96`；**4 轮**；merge `b20c021`；approval-record #107
  merge `c03fa88`；全量 **774**。
- Round 1 的 3 个 blocker：proposal / canonical boundary（Module 永不构造
  `CandidateGateAssessment`、永不发 `HUMAN_APPROVED` / `Decision`，只产出
  proposal envelope 给 human-review surface）。Round 2：item 12 proposal-envelope
  identity completeness。Round 3：同一 boundary blocker 在 human drawing 的两处
  旧措辞（docs-only）。Round 4 APPROVE。

#### PR E2 —— MOD-TGT01@1.0.0 实现
- PR #108；被审 HEAD `72546a3`；**5 轮**；merge `5b92dee`；approval-record #109
  merge `cb98460`；全量 **821**。
- 外层 architecture 从一开始 PASS。Round 1 的 4 个 deterministic-core
  correctness blocker（hard integrity → machine reject、exact canonical EP
  reuse、classification parity 等）。Round 2–4 逐步收口 canonical-reuse semantic
  identity + 三条 drift regression + 缺字段边界条件。Round 5 APPROVE ——
  `MOD-TGT01@1.0.0` 是 E1 frozen contract 的合格 deterministic implementation。
  `MIGRATION_PENDING` 继续保持。

#### PR E3 —— TGT-05 construction contract（design-only）
- PR #110；被审 HEAD `359744c`；**2 轮**；merge `b0e452a`；approval-record #111
  merge `14ac39f`；全量 **862**。
- 大框架 1 轮就 PASS（design-only、17 项完整、03/05/07/08 PR D parity、MOD-TGT05
  仍 `0.0.0`、无 provider/persistence/scoring/threshold/therapeutic-window）。
  Round 1 的 2 个 E3 自身确定性 blocker → Round 2 APPROVE。非阻断 note：E4 把
  `fatal_review.status` 固定成 `POTENTIAL_FATAL_PATTERN`。

#### PR E4 —— MOD-TGT05@1.0.0 实现
- PR #112；被审 HEAD `bbc630f`；**2 轮**；merge `b8518d8`；approval-record #113
  merge `bdae380`；全量 **918**。
- architecture 1 轮 PASS（standalone core / injected ports only / one-way
  liability detector / frozen truth table / negative atlas = coverage context /
  `fatal_review` 仅 `POTENTIAL_FATAL_PATTERN` trigger / exact
  tissue+phenotype key convergence / Path A·B·C）。Round 1 的 4 个 evidence-
  integrity / scientific-equivalence blocker → Round 2 逐 blocker 复核 CLOSED、
  APPROVE。

#### PR E5 —— TGT-08 construction contract（design-only）
- PR #114；被审 HEAD `3e5a551`；**4 轮**；merge `f9b4ddd`；approval-record #115
  merge `14b7ac5`；全量 **967**。
- Round 1 的 2 个 narrow Direction × Strength / two-axis blocker → Round 2
  residual（WEAK unmet-need exception 与 two-axis completion rule 冲突）→
  Round 3 residual（item 13 machine acceptance 还保留旧的广义 UNKNOWN 规则）→
  Round 4 APPROVE。`NEGATIVE` 可达但 ≠ KILL / sponsor stop；FTO 边界；
  `sponsor_review` 独立 module-local trigger。

#### PR E6 —— MOD-TGT08@1.0.0 实现
- PR #116；被审 HEAD `9a033e8`；**2 轮**；merge `c03fa34`；approval-record #117
  merge `97ad48d`；全量 **1053**。
- 主链 1 轮 PASS。Round 1 的 2 个 blocker（同一原则：机器不能因为 provider 给
  了一个布尔声明就获得本不该有的权威）：`SEARCH_COMPLETION_AUDIT` 没真正证明
  completion、headline invariant 1 可被绕过；`sponsor_review` 可在 incomplete
  landscape 上成为 accepted actionable trigger。Round 2 均 CLOSED、APPROVE。

#### PR E7 —— TGT-02 construction contract（design-only）
- PR #118；被审 HEAD `a1d00b1`；**4 轮**（Round 3–4 只是治理记录 / PR body 同步、
  无新 commit）；merge `9ec30e6`；approval-record #119 merge `76814c1`；全量
  **1104**。
- Round 1 的 4 个 narrow blocker："qualifying" 不是 rung-specific；"across
  cohorts" 被写成 `> 2` / MORE THAN TWO（隐式 ≥ 3 阈值，应为 "at least two
  independent cohorts"）；observation-level evidence class 与 final Gate
  Direction 混写；item 04 derived parity 只是 superset 检查。Round 2–4 关闭
  governance-record + PR body 里的旧 `> 2` / 旧测试数字残留。

#### PR E8 —— MOD-TGT02@1.0.0 实现
- PR #120；被审 HEAD `3e48626`；**3 轮**；merge `ca0b4ad`；approval-record #121
  merge `94039e5`；全量 **1208**。
- 主体架构 1 轮接受（11-file standalone、typed assay、highest-qualifying-class
  aggregation、`>= 2` cross-cohort、NEGATIVE ≠ fatal ≠ KILL、TMA never DIRECT）。
  Round 1 的 7 个 runtime correctness / integrity blocker → Round 2 的 4 个
  narrow integrity / factual-output blocker → Round 3 APPROVE。

#### PR E9 —— TGT-03 construction contract（design-only）
- PR #122；被审 HEAD `8ba624c`；**3 轮**；merge `a2d585d`；approval-record #123
  merge `80790c8`；全量 **1283**。
- Round 1 的 3 个窄 contract-shape blocker → Round 2 的 1 个 audit-snapshot
  rename residue → Round 3 无新 blocker、APPROVE。persistence / loss 事实只有
  Gate-relative 结论被禁。

#### PR E10 —— MOD-TGT03@1.0.0 实现
- PR #124；被审 HEAD `6445ae5`；**2 轮**；merge `551a938`；approval-record #125
  merge `c9748b1`；全量 **1379**。
- Round 1 的 5 个 factual-integrity blocker（不重开 frozen E9 contract body /
  Direction truth table）→ Round 2 全部实质关闭、regression 覆盖对应错误路径、
  APPROVE。`tests/test_tgt03_module.py` 78 → 91。

#### PR E11 —— TGT-04 construction contract（design-only）
- PR #126；被审 HEAD `1ad620d`；**3 轮**；merge `499cf3a`；approval-record #127
  merge `be72c15`；全量 **1450**。
- Round 1 的 4 个 construction-contract blocker → Round 2 的 2 个窄 residual
  consistency blocker → Round 3 无新 blocker、APPROVE。5 个 legal
  Direction × Strength pair。

#### PR E12 —— MOD-TGT04@1.0.0 实现
- PR #128；被审 HEAD `14fba32`；**3 轮**；merge `f09ab3d`；approval-record #129
  merge `6ef1892`；全量 **1538**。
- `MIGRATION_PENDING` / package boundary 无 blocker、无 E11 science 重开、无
  11-file 重构。Round 1 的 3 个窄 runtime blocker → Round 2 的 3 个窄 residual
  integrity blocker → Round 3 APPROVE。引入 "duplicate `observation_id`
  preflight-before-side-effects" 基因（后被 E16 复用）。

#### PR E13 —— TGT-06 construction contract（design-only）
- PR #130；被审 HEAD `0ab57b9`；**4 轮**；merge `aa57640`；approval-record #131
  merge `aa80865`；全量 **1629**。
- Round 1 的 4 个 construction-contract blocker → Round 2 的 3 个窄 consistency
  blocker → Round 3 的 1 个 Route A/B consistency blocker（Route B 现在同时要求
  `>= 2` distinct …）→ Round 4 无新 blocker、APPROVE。7/7 original freeze point
  intact。

#### PR E14 —— MOD-TGT06@1.0.0 实现
- PR #132；被审 HEAD `7b87a58`；**3 轮**；merge `d65a5a7`；approval-record #133
  merge `bbfb1f1`；全量 **1713**。
- pre-code scoping：APPROVE-to-proceed + **6 个 required implementation
  tightenings**。Round 1 的 3 个窄 runtime blocker（含 classifier authority、
  EvidenceRole mapping）→ Round 2 的 1 个 residual → Round 3 APPROVE。合并后
  7 / 8 primary Modules implemented，`MIGRATION_PENDING` 继续保留。

#### PR E15 —— TGT-07 construction contract（design-only）
- PR #134；被审 HEAD `3747f8e`；**2 轮**；merge `7684d27`；approval-record #135
  merge `a706a47`；全量 **1796**。
- scoping：CONSTRUCTION_CONTRACT_ADD，与 E1/E3/E5/E7/E9/E11/E13 同型；canonical
  Gate 名 "Shedding / Soluble-Antigen / Sink Liability"；MOD-TGT07
  `primary_module_version` 保持 `0.0.0`（E16 才 bump）。**7 个 required
  tightening**（逐字冻结在合同）：Option A（`INDIRECT_STRONG` →
  `POSITIVE / INDIRECT_STRONG`，恰好 6 个 legal Direction × Strength pair）；
  below-detection/LOQ 定量为 CONTEXTUAL（新 CLOSED
  `circulating_soluble_target_status` enum）；canonical `NEGATIVE / DIRECT`
  只能由 qualified intended-ADC `SOLUBLE_ANTIGEN_TMDD_ANALYSIS` 产生；fatal =
  one predicate + two alternative source paths（clinical / TMDD），**无强制
  `reproducibility_status` predicate**、无 global cancellation precondition；
  单字符串 `sink_exposure_context_id`（无 declared_multi / 第三态 /
  set-projection）；DIRECT / fatal authority 由 typed status 承载、永不
  semantic-parse prose；`SolubleAntigenEvidenceCompletion` 恰好 4 条
  search-completion 轴、无 `qualifying_indirect_evidence_context_ids`。
- Round 1 的 1 个窄 blocker：clinical fatal source path 误加了强制
  `reproducibility_status == QUALIFIED` predicate（会对强的单次 clinical PK
  observation 造成 false negative）→ 删除、降为 optional factual metadata。
  Round 2 APPROVE。

#### PR E16 —— MOD-TGT07@1.0.0 实现 + runtime-conformance 收口
- PR #136 `task_20260901_runtime-migration-pr-e16`；被审 HEAD `798c734`；
  **2 轮**；merge `004dbed`；approval-record PR #137
  `task_20260901_runtime-migration-pr-e16-approval-record` merge `de936cf`；
  全量 **1900**。
- pre-code scoping：APPROVE-to-proceed + **7 个 required implementation
  tightenings**（T1 kind-specific DIRECT 判定只在 `classify.py`；T2
  `MIXED_OR_UNRESOLVED` = DIRECT-quality CONTEXTUAL、`NOT_ESTABLISHED` 永不
  qualifying DIRECT；T3 `aggregate` / `fatal_review` 只消费 classified 结果、
  直接写冻结的 `frozen_evaluation_order`；T4 completion 加
  `crc_patient_` + `healthy_donor_quantitation_subspace_search_complete` 两个
  typed fact + 严格 AND + 审计 parity；T5 `fatal_review` 只做 fatal-specific
  narrowing、`module.py` 顺序 raw-candidate → acceptance → surface；T6 精确
  字符串等值、duplicate-`observation_id` preflight HARD 短路；T7 收官 machine
  invariant regression：八个 binding 全 `"1.0.0"` + 八个 package manifest 齐备
  才允许 live docs 停止写 `MIGRATION_PENDING`）。
- **11 文件 MOD-TGT07 包** + `tests/test_tgt07_module.py`（91 → 96）+ binding
  对账（`src/contracts/crc_adc_target_gateset.yaml` TGT-07 `0.0.0` → `1.0.0`、
  `built_module_versions` 加 TGT-07、`primary_module_binding.rule` 改写为
  8/8 built；`src/objects/crc_adc_target_gateset.py` `BUILT_MODULE_VERSIONS`
  加 TGT-07）。
- **runtime-conformance 收口**：`gate_modules/README.md` / `README.md` /
  `architecture.md` / `docs/architecture/contract.zh-CN.md` 的 live
  `MIGRATION_PENDING` → runtime conformance COMPLETE；**冻结的 v5 expert-review
  文档与 historical version snapshots / archived approval records 不动**。
  `migration.deferred` **不删除**，`per_gate_primary_modules` key 标记
  completed / 8-of-8。新增 `tests/test_gate_modules_boundary.py` 的
  `Tgt07ModuleManifestTests` + `MigrationCloseoutInvariantTests`。
- Round 1 REQUEST_CHANGES 的 3 个窄 blocker（全部 CLOSED，一个 commit `798c734`）：
  1. `documents_clinical_exposure_compromise` 成了第二套 fatal authority
     （与 CLOSED typed `sink_materiality_outcome ==
     MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE` 冲突，后者按 T5
     本身即唯一 machine authority）→ 从 `contracts.py` / `evidence.py` parity /
     `fatal_review.py` / `acceptance.py` / `module.yaml` / tests 全部移除；
     fatal narrowing 只 keys off typed outcome + `observation_kind`（+ TMDD
     path 的 `exposure_scenario_class == INTENDED_ADC_EXPOSURE`）。
  2. `acceptance.py` 错误地整轮 reject 携带真实 `sink_exposure_context_id` 的
     CONTEXTUAL CLINICAL / TMDD observation（把「没到 DIRECT」升级成「输入非法」）
     → check 改成 keys off `observation_kind`（只有 non-DIRECT-authority kind
     不得携带 context）；新增 `ContextualDirectAuthorityObservationTests`。
  3. `docs/architecture/contract.zh-CN.md` §3.4.3 同时写「runtime
     implementation 未变 / migration pending」和「Runtime conformance:
     COMPLETE」→ 只改 live doc（不动 frozen v5 / historical snapshots）：legacy
     contracts 降格为 retained compatibility snapshots、「尚缺、migration 时须
     新增」Candidate Types →「仍属 deferred downstream work」、B 组 blockers
     标为已关闭、Source-of-Truth 行 → legacy-compatibility / crosswalk
     reference；`MigrationCloseoutInvariantTests` 扩展到 README + architecture
     + contract 并禁止 stale phrase。
- Round 2 APPROVE @ `798c734`：三个 blocker 全部 CLOSED，无新 blocker；
  round-1 → round-2 只有一个 commit、约 10 文件，`classify.py` / `aggregate.py`
  / `completion.py` / binding science 及其它已 CLOSED 逻辑未重新触碰。非阻断
  housekeeping：PR body 的旧测试计数 `91 OK` / `1895 OK` merge 前更新为
  `96` / `1900`。
- **收口效果**：八个 primary Module 施工合同全部 APPROVE **且** 八个全部实现
  @ `1.0.0`（TGT-01/02/03/04/05/06/07/08）；每个
  `primary_module_binding.<gate> == "1.0.0"`；**`MIGRATION_PENDING` 已解除**
  —— PR A–E16 Blueprint-v1.3 Candidate × Gate × Evidence runtime-conformance
  migration 与八个 primary Module 的 migration 均 COMPLETE。

---

## 4. 贯穿全程的方法 / 约束（"怎么做的"）

### 4.1 审核

- 所有需要审核的内容（pre-code scoping、design contract、implementation、
  逐轮 REQUEST_CHANGES 回复）**只**提交给 ChatGPT 项目 `Biotech ideas` → 对话
  `AI审核方案`，由 Claude 通过浏览器自动化（Chrome tab）把请求 / 回复贴入。
- GitHub connector 每一轮都 `403 Resource not accessible by integration` ——
  formal review state 无法写回，**`AI审核方案` 对话结论为 authoritative**，
  逐轮落在 `logs/chatgpt-review-*.md` + manifest 的 `review_round_N` block。
- REQUEST_CHANGES 在**同一个 PR 分支**上修复；APPROVE 之后审核记录 + manifest
  翻 approved 落在**独立的 docs-only approval-record PR**（不落在被批准的 PR
  branch 上，PR #95 / #97 起的先例）。

### 4.2 边界（每个实现 PR 的 IS-NOT，见各 manifest）

- `run()` 纯 injected-port Python：**无** normalizer / live provider / retrieval
  / 网络 / 子进程 / 数据库 / cache / 仓库内持久化 / 从文件系统分配 id。
- **无** numeric / ranking scoring，**无**发明的浓度 / turnover / affinity /
  dose-exposure / threshold，**无**对 source-reported 数值做 `float()` /
  `Decimal()` 强制转换。
- **无** generic GateModule framework / base class；八个 Module 各自 standalone，
  互不 refactor。
- Module **永不**构造 canonical `CandidateGateAssessment` / 发
  `HUMAN_APPROVED` / `Decision`；至多产出 proposal envelope 给 human-review
  surface；`fatal_review` 至多 `POTENTIAL_FATAL_PATTERN`，且只在 accepted run
  上 surface。机器**永不**裁决 fatality / KILL / HOLD / 疗效 / Candidate-level
  后果。
- **无**跨 Gate 结论；**不**触碰 PR A/B/C 契约、PR D 的科学 ladder、以及已冻结的
  奇数 E construction contract body。
- 唯一被允许的既有文件改动：偶数 E 的窄 binding / registry 对账 + `worklog.md`
  append；E16 额外允许 live runtime-conformance docs 收口。
- 迁移只用一个依赖：PyYAML。

### 4.3 CI / 提交纪律

- `.github/workflows/ci.yml` 矩阵 python 3.11 + 3.12（jobs `verify (3.11)` /
  `verify (3.12)`），步骤含 Unit tests + Repository boundary
  (`bash scripts/verify_repository_boundary.sh`) + working-tree cleanliness。
- 每次 commit 前：`find . -name __pycache__ -not -path './.git/*' -exec rm -rf
  {} +` + `rm -rf .pytest_cache .benchmarks`；全量
  `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p
  'test_*.py'`。
- commit trailer：`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` +
  `Claude-Session: …`；PR body trailer：`🤖 Generated with [Claude Code]…`。
- 不提交仓库里既有的 untracked 杂项（`AI_RESULT_ACCEPTANCE.md`、
  `CRC Patient Territory Map.png`、`STELLIGEN_CONSTRAINTS.md`、`docs/worklogs/`、
  `pipelines/` 等）—— 只 stage 明确的 E-series artifact。

### 4.4 测试增长

| 里程碑 | 全量 unittest |
|---|---|
| 迁移开始前（约） | ~555 |
| PR A APPROVE | 609 |
| PR B APPROVE | 658 |
| PR C APPROVE | 716 |
| PR D APPROVE | 751 |
| PR E2（MOD-TGT01） | 821 |
| PR E4（MOD-TGT05） | 918 |
| PR E6（MOD-TGT08） | 1053 |
| PR E8（MOD-TGT02） | 1208 |
| PR E10（MOD-TGT03） | 1379 |
| PR E12（MOD-TGT04） | 1538 |
| PR E14（MOD-TGT06） | 1713 |
| PR E15（TGT-07 contract） | 1796 |
| **PR E16（MOD-TGT07 + 收口）** | **1900** |

---

## 5. 收官状态

- **八个 primary Evidence Production Module 全部建成 @ `1.0.0`**：
  MOD-TGT01…MOD-TGT08，各自一个 11-file `gate_modules/tgt0n_*/` 包 +
  `tests/test_tgt0n_module.py` + `manifests/gate_modules/*` package manifest。
- `src/contracts/crc_adc_target_gateset.yaml`：每个
  `primary_module_binding.<gate> == "1.0.0"`；`built_module_versions` 八个键
  齐备；`primary_module_binding.rule` = 8/8 built。
- **`MIGRATION_PENDING` 已解除**。`README.md` / `architecture.md` /
  `gate_modules/README.md` / `docs/architecture/contract.zh-CN.md` 的 live 文案
  = runtime conformance COMPLETE for the Blueprint-v1.3 Candidate × Gate ×
  Evidence migration。冻结的 `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW`
  v5 与 historical snapshots / archived approval records **未改动**。
- `main` 全量 `unittest` **1900 OK**。
- **没有 PR E17。** `migration.deferred` 未删除，剩余 StelligenOS deferred work
  各自需要单独的 explicit go-ahead：
  - `per_gate_primary_modules`：completed / 8-of-8。
  - `assessment_and_decision_evaluators`：not in this repo。
  - `epitope_layer_and_beyond`：PR E+（quantitative ladder calibration、
    epitope-layer 及更下游分析）。
  - external evaluators、下游 Candidate levels、FTO 任务。

---

## 6. 索引

- 逐 PR 审核记录：`logs/chatgpt-review-2026-08-28-runtime-migration-pr-a.md` …
  `logs/chatgpt-review-2026-09-01-runtime-migration-pr-e16.md`（共 20 个）。
- 逐 PR manifest：`manifests/runtime_migration_pr_{a,b,c,d}_manifest.yaml` +
  `manifests/runtime_migration_pr_e{1..16}_manifest.yaml`。
- 逐 PR 中文 handoff：`docs/handoff/2026-08-*-runtime-migration-pr-*.zh-CN.md` +
  `docs/handoff/2026-09-01-runtime-migration-pr-e16.zh-CN.md`。
- 逐条 append 记录：`logs/worklog.md`。
- Module 包：`gate_modules/tgt0{1..8}_*/`；binding：
  `src/contracts/crc_adc_target_gateset.yaml`。
