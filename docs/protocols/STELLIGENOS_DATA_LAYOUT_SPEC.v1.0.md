# StelligenOS Data Layout Spec v1.0

## 0. 版本与来源

- 文档 ID：`STELLIGENOS_DATA_LAYOUT_SPEC`
- 版本：`v1.0-draft`
- 状态：`PENDING_EXPERT_REVIEW`
- 日期：`2026-08-28`
- 规范来源（上游架构，本文件不得与之冲突）：
  - `StelligenOS-产品形态-Blueprint v1.3`（六对象决策模型 + Instantiation +
    Candidate Level / canonical GateSet 骨架）
  - `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`
    （`v5`，`STELLIGENOS-ARCH-2026.08.27-v5`，PR #94 `APPROVE`）
  - `docs/architecture/contract.zh-CN.md` §3.4（决策层模型 + Candidate Level
    Registry）
- 机器可读 schema：`src/contracts/data_layout/`（含 `csv_headers.yaml` 与
  `context.schema.yaml`）
- worked example（单文档，`TGT-04 × CEACAM5`）：`docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md`
- 外部骨架生成脚本：`scripts/scaffold_data_layout.sh`（回归测试
  `tests/test_scaffold_data_layout.sh`，本地 `bash tests/test_scaffold_data_layout.sh`
  运行；接入 `.github/workflows/ci.yml` 需 `workflow` scope，留待负责人加一行）

### 0.1 本文件是什么，不是什么

**是：** StelligenOS **运行数据**（Candidate / Context / Instantiation / Matrix
/ Assessment / EvidencePackage / Decision / Module run）在**仓库外部工作区**的
**固定物理布局与文件规范**。它把 v5 决策层模型落成磁盘上的目录树、文件格式与
命名规则，使 Claude / Codex 后续可以严格按此施工。

**不是：** 架构决策变更。它不新增核心对象、不改 `core_objects.yaml` /
`gate_system.yaml` / 任何现有合同、不启动 runtime migration（PR A–E）。它是那些
migration PR 的**物理层依据**。本仓库**不**保存本布局下的任何真实数据——仓库
只保存本 spec、schema、受控参考样例和生成脚本。

### 0.2 冻结的四条核心原则（来自设计讨论）

1. **CSV 是视图，不是最终事实源。**
2. **Assessment JSON 是 Candidate × Gate 判决的 canonical record。**
3. **Evidence Package 是独立、全局复用的资产，不复制进每个 Gate。**
4. **Gate 文件夹是施工 workspace；一个 Gate 一个包工头，所有 run 都在这里。**

### 0.3 五类 primary product outputs（§19，冻结；以后不得随意新增核心输出格式）

这五类是**每天面向决策的产品输出**。注意：`Context` / `Instantiation` /
`gate_binding` / `gateset_binding` / `run_manifest` 也各有自己的 canonical
record（见对应章节），只是它们是**绑定/配置/施工记录**，不是产品输出层。
因此不再称"只有 5 类 canonical 文件"。

| # | 对象 | 格式 | 示例文件 |
|---|---|---|---|
| 1 | Candidate | CSV | `10_CANDIDATES/L04_ADC_TARGET.csv` |
| 2 | Candidate × Gate Matrix | CSV（derived view） | `MATRICES/L04_ADC_TARGET.matrix.csv` |
| 3 | CandidateGateAssessment | JSON（`vNNN.json` canonical + `latest.json` 副本） | `ASSESSMENTS/CAND-L04-000001/v001.json` |
| 4 | EvidencePackage | folder（`evidence.json` + `summary.md` + `artifacts/`），**immutable-by-ID** | `30_EVIDENCE_LIBRARY/PACKAGES/EP-00000123/` |
| 5 | Decision | JSON（`DEC-*.json` canonical）+ `decisions.csv` view | `DECISIONS/DEC-0001.json` |

其它 canonical records（配置/绑定/施工层）：`15_CONTEXTS/CTX-*/vNNN.yaml`、
`20_INSTANTIATIONS/<inst>/instantiation.yaml`、`GATESETS/<gs>/gateset_binding.yaml`、
`GATESETS/<gs>/TGT-NN/gate_binding.yaml`、`TGT-NN/RUNS/RUN-*/run_manifest.json`。

---

## 1. 顶层目录

所有 StelligenOS 运行数据放在**仓库外部**，默认根：

```text
/Volumes/Stelligen_SSD/Stelligen/DATA/StelligenOS/
```

（下文以 `$STELLIGENOS_DATA` 指代该根；实际路径由操作者选定，不写死进仓库。）

固定结构：

```text
$STELLIGENOS_DATA/
│
├── 00_REGISTRY/                         # 全局受控词表（人工维护，机器只读）
│   ├── candidate_levels.csv             # L00–L14 定义
│   ├── candidate_type_registry.csv      # candidate_type ↔ level ↔ canonical GateSet
│   ├── gateset_registry.csv             # gateset_id ↔ version ↔ 成员 Gate 列表
│   ├── gate_registry.csv                # gate_id ↔ gateset ↔ candidate level ↔ dominant evidence regime
│   └── instantiation_registry.csv       # 所有 Instantiation 的索引
│
├── 10_CANDIDATES/                       # Candidate 身份，按 Level 分 CSV，无 context_id
│   ├── L00_INDICATION.csv
│   ├── L01_PATIENT_TERRITORY.csv
│   ├── L02_ENDPOINT.csv
│   ├── L03_MODALITY.csv
│   ├── L04_ADC_TARGET.csv
│   ├── L05_ADC_EPITOPE.csv
│   ├── L06_ANTIBODY_BINDER.csv
│   ├── L07_LINKER.csv
│   ├── L08_PAYLOAD.csv
│   ├── L09_ADC_DESIGN.csv
│   ├── L10_ADC_HIT.csv
│   ├── L11_ADC_LEAD.csv
│   ├── L12_BIOMARKER.csv
│   ├── L13_DEVELOPMENT_CANDIDATE.csv
│   └── L14_REGIMEN.csv
│
├── 15_CONTEXTS/                         # Context 身份，与 Candidate 一样可复用、可审计、版本化
│   ├── context_index.csv               # 所有 Context 的索引
│   └── CTX-CRC-REFRACTORY-MSSPMMR/
│       ├── v001.yaml                    # canonical，append-only（vNNN）
│       └── latest.yaml                  # derived pointer/copy（byte-identical of 最新 vNNN）
│
├── 20_INSTANTIATIONS/                   # "这一次到底在干什么"
│   └── INST-CRC-REFRACTORY-ADC-TARGET-v1/
│       ├── instantiation.yaml
│       ├── candidates.csv               # 本 Instantiation 纳入评估的 candidate_id 子集
│       │
│       ├── MATRICES/                    # derived view，可由 Assessment JSON 重建
│       │   ├── L04_ADC_TARGET.matrix.csv
│       │   └── L04_ADC_TARGET.assessments.csv
│       │
│       ├── DECISIONS/                   # GateSet-level Decision（不是 Gate-level）
│       │   ├── decisions.csv            # view
│       │   └── DEC-0001.json            # canonical
│       │
│       └── GATESETS/
│           └── ADC_TARGET_GATESET-v1/
│               ├── gateset_binding.yaml
│               │
│               ├── TGT-01/              # 一个 Gate 一个施工 workspace（见 §7）
│               ├── TGT-02/
│               ├── TGT-03/
│               ├── TGT-04/
│               ├── TGT-05/
│               ├── TGT-06/
│               ├── TGT-07/
│               └── TGT-08/
│
├── 30_EVIDENCE_LIBRARY/                 # 全局、跨 Gate / 跨 Instantiation 复用
│   ├── evidence_index.csv
│   ├── source_index.csv
│   └── PACKAGES/
│       ├── EP-00000001/
│       ├── EP-00000002/
│       └── ...
│
└── 90_ARCHIVE/                          # 退役 Instantiation / 已 superseded 的产物
```

这套结构一旦冻结，成为以后所有 StelligenOS 数据产品的固定物理布局。新增
indication / 新 Candidate Level / 新 Instantiation 只是在既有目录下加子目录，
**不改这棵树的形状**。

### 1.1 目录编号约定

`00_` / `10_` / `20_` / `30_` / `90_` 前缀固定，保证 `ls` 排序即为读取顺序：
registry → candidates → instantiations（含 matrix / decisions / gatesets）→
evidence library → archive。中间号段（`40_`–`80_`）预留，新增顶层类别须走
本 spec 的版本修订（`v1.1` / `v2.0`），不得由 Module 私自创建。

---

## 2. Candidate：不同 Level 必须分 CSV

**不要**用 `all_candidates.csv` 作为主要工作文件。不同 Candidate Level 语义
完全不同——ADC Target candidate 与 ADC Hit candidate 不应共享一堆 nullable
列。每个 Level 一个 CSV：`10_CANDIDATES/L04_ADC_TARGET.csv` …

### 2.1 统一 identity 字段（每个 Level CSV 都必须有，且顺序固定）

| 列 | 类型 | 说明 |
|---|---|---|
| `candidate_id` | string | 全局唯一，格式 `CAND-Lnn-nnnnnn`（见 §附录 A） |
| `candidate_type` | enum | 见 `00_REGISTRY/candidate_type_registry.csv`（如 `ADC_TARGET`） |
| `level` | enum | `L00`…`L14` |
| `canonical_name` | string | 人类可读规范名（如 `CEACAM5`） |
| `parent_candidate_id` | string / 空 | lineage 指针（如 Epitope 的 parent = Target），可空 |
| `status` | enum | `ACTIVE` / `HOLD` / `RETIRED` |
| `version` | int | Candidate 身份记录版本，从 `1` 起 |
| `created_at` | date | `YYYY-MM-DD` |
| `provenance_ref` | string | `external:` 前缀的版本化引用（如 `external:ADCdb/...`） |

> **铁律：Candidate CSV 绝对不含 `context_id`。** 同一个 `CEACAM5` 可被多个
> Context 重复评估。Candidate × Context 的关联只发生在 Assessment（§8）与
> Instantiation（§3）层。

### 2.2 Level-specific 列

统一 identity 字段之后，各 Level CSV 可追加该 Level 专属列（如 `L04` 可加
`hgnc_symbol` / `uniprot_id`；`L08` PAYLOAD 可加 `payload_class`）。Level-specific
列不得与 identity 字段重名，不得引入 `context_id` 或任何评估结论字段
（`direction` / `strength` / `decision` 都不允许出现在 Candidate CSV）。

示例（`L04_ADC_TARGET.csv`）：

```csv
candidate_id,candidate_type,level,canonical_name,parent_candidate_id,status,version,created_at,provenance_ref
CAND-L04-000001,ADC_TARGET,L04,CEACAM5,,ACTIVE,1,2026-08-27,external:ADCdb/target/CEACAM5@v3
CAND-L04-000002,ADC_TARGET,L04,TWEAKR,,ACTIVE,1,2026-08-27,external:ADCdb/target/TNFRSF12A@v3
```

---

## 2b. Context：canonical、可复用、版本化（`15_CONTEXTS/`）

Context 与 Candidate 一样是可复用、可审计的资产——同一个 `CTX-*` 可被多个
Instantiation 与多次评估引用——因此它有自己的 canonical 物理落点，**不再是
悬空引用**。

```text
15_CONTEXTS/
├── context_index.csv
└── CTX-CRC-REFRACTORY-MSSPMMR/
    ├── v001.yaml        # canonical，append-only（内容修订 → 新建 vNNN，旧版本不改）
    └── latest.yaml      # derived：最新 vNNN 的 byte-identical 副本（含 context_version 标注哪一版）
```

`CTX-*/vNNN.yaml`：

```yaml
context_id: CTX-CRC-REFRACTORY-MSSPMMR
context_version: 1
canonical_name: "Refractory MSS/pMMR metastatic colorectal cancer, >=3L"
dimensions:
  indication: colorectal cancer
  disease_stage: metastatic
  line_of_therapy: ">=3L"
  molecular_subtype: MSS/pMMR
  patient_territory: refractory
  treatment_history: "prior fluoropyrimidine, oxaliplatin, irinotecan; +/- anti-EGFR, +/- anti-VEGF"
  anatomical_site: null
  model_or_system: human patient tissue
status: ACTIVE          # ACTIVE | HOLD | RETIRED
created_at: 2026-08-28
provenance_ref: external:...
```

`15_CONTEXTS/context_index.csv`：

| context_id | context_version | canonical_name | indication | status | created_at |
|---|---|---|---|---|---|

> Context 本身是范围声明，不是结论——不含 `direction` / `strength` / `decision`
> / `candidate_id`。跨 context 的证据可被引用，但 transfer assumption 记录在
> 引用它的 Assessment，不在 Context。

---

## 3. Instantiation：定义"这一次到底在干什么"

`20_INSTANTIATIONS/<instantiation_id>/instantiation.yaml`：

```yaml
instantiation_id: INST-CRC-REFRACTORY-ADC-TARGET-v1

candidate_type: ADC_TARGET
candidate_level: L04

context_id: CTX-CRC-REFRACTORY-MSSPMMR
context_version: 1            # pin 到 15_CONTEXTS/CTX-.../v001.yaml
modality: ADC

gateset_id: ADC_TARGET_GATESET
gateset_version: "1.0"

evidence_regime: PUBLIC_ONLY   # PUBLIC_ONLY | PUBLIC_PLUS_EXPERIMENTAL | DEVELOPMENT

status: ACTIVE                 # ACTIVE | HOLD | FROZEN | RETIRED
version: 1
created_at: 2026-08-28
```

字段语义对齐 Blueprint v1.3 §M08：Instantiation 只做 configuration/binding，
**不产生科学结论、不持有 Evidence、不产生 Assessment**。`context_id` +
`context_version` pin 到 `15_CONTEXTS/CTX-<id>/v<NNN>.yaml`。

以后 `INST-CRC-EPITOPE-…` / `INST-BREAST-ADC-TARGET-…` / `INST-CRC-ADC-HIT-…`
全部使用**同一目录结构**（`MATRICES/` + `DECISIONS/` + `GATESETS/`），只是绑定
不同 `candidate_type` / `context_id` / `gateset_id`。

`00_REGISTRY/instantiation_registry.csv` 汇总所有 Instantiation：

```csv
instantiation_id,candidate_type,candidate_level,context_id,context_version,modality,gateset_id,gateset_version,evidence_regime,status,created_at
INST-CRC-REFRACTORY-ADC-TARGET-v1,ADC_TARGET,L04,CTX-CRC-REFRACTORY-MSSPMMR,1,ADC,ADC_TARGET_GATESET,1.0,PUBLIC_ONLY,ACTIVE,2026-08-28
```

---

## 4. Candidate × Gate Matrix：宽表（每天真正看的产品界面）

`20_INSTANTIATIONS/<inst>/MATRICES/L04_ADC_TARGET.matrix.csv`：

| candidate_id | name | TGT-01 | TGT-02 | TGT-03 | TGT-04 | TGT-05 | TGT-06 | TGT-07 | TGT-08 | decision |
|---|---|---|---|---|---|---|---|---|---|---|
| CAND-L04-000001 | CEACAM5 | POSITIVE/DIRECT | POSITIVE/DIRECT | POSITIVE/INDIRECT_STRONG | POSITIVE/INDIRECT_STRONG | CONFLICTING/DIRECT | POSITIVE/DIRECT | POSITIVE/WEAK | UNKNOWN | HOLD |
| CAND-L04-000002 | X | POSITIVE/DIRECT | NEGATIVE/DIRECT | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | KILL |

### 4.1 cell 取值（冻结，不得发明数字；全部是显式机器字符串，无 em dash）

`<DIRECTION>/<STRENGTH>` 组合（`Direction ⊥ Strength`，任何 direction 只要有
合格证据就带 strength，避免 CSV view 丢信息）：

```text
POSITIVE/DIRECT           POSITIVE/INDIRECT_STRONG        POSITIVE/WEAK
NEGATIVE/DIRECT           NEGATIVE/INDIRECT_STRONG        NEGATIVE/WEAK
CONFLICTING/DIRECT        CONFLICTING/INDIRECT_STRONG     CONFLICTING/WEAK
INCONCLUSIVE/DIRECT       INCONCLUSIVE/INDIRECT_STRONG    INCONCLUSIVE/WEAK
```

单值状态（无 strength 后缀）：

```text
UNKNOWN         # 已评估，但无合格证据。serialization 固定 direction=INCONCLUSIVE, strength=UNKNOWN, evidence_refs=[]
NOT_APPLICABLE  # 本 Gate 对该 Candidate 结构性不适用（serialization convention: strength=UNKNOWN）
NOT_EVALUATED   # 根本没有 HUMAN_APPROVED Assessment（不是一条 Assessment 状态，而是"该文件不存在"的 CSV 表示）
```

**`NOT_EVALUATED` vs `UNKNOWN` 是两回事**：前者 = 没跑过 / 没批过，后者 = 跑过
批过但没证据。Matrix、`assessments.csv`、Decision 的 `assessment_snapshot`、
worked example 必须一致使用 `NOT_EVALUATED`，**不得用 em dash 或空串作为机器值**。

**禁止** `+3 / +2 / +1 / 0 / -1 / -2 / -3` 或任何单一数值分数。

### 4.2 Matrix 是 derived view

Matrix 由该 Instantiation 下所有 Gate 的 `ASSESSMENTS/<cand>/latest.json`
（§8）自动重建，**不手工编辑**。`decision` 列由 `DECISIONS/DEC-xxxx.json`
（§17）回填。任何时候删掉 matrix.csv 都能从 canonical JSON 无损重建。

---

## 5. long-format `assessments.csv`（机器友好）

宽表适合人看，机器不好处理。同一目录下同时自动生成
`L04_ADC_TARGET.assessments.csv`：

| candidate_id | gate_id | direction | strength | assessment_id | assessment_version | evidence_count | review_status | last_updated_at |
|---|---|---|---|---|---|---:|---|---|
| CAND-L04-000001 | TGT-01 | POSITIVE | DIRECT | ASMT-000001 | 1 | 7 | HUMAN_APPROVED | 2026-08-27 |
| CAND-L04-000001 | TGT-04 | POSITIVE | INDIRECT_STRONG | ASMT-000004 | 1 | 3 | HUMAN_APPROVED | 2026-08-27 |
| CAND-L04-000001 | TGT-08 | INCONCLUSIVE | UNKNOWN | ASMT-000008 | 1 | 0 | HUMAN_APPROVED | 2026-08-27 |

- `direction` ∈ `POSITIVE|NEGATIVE|CONFLICTING|INCONCLUSIVE|NOT_APPLICABLE`；
  `strength` ∈ `DIRECT|INDIRECT_STRONG|WEAK|UNKNOWN`；组合约束见 §8.2。
- `UNKNOWN` 状态：`direction=INCONCLUSIVE, strength=UNKNOWN, evidence_count=0`。
- 只列有 HUMAN_APPROVED Assessment 的 (candidate, gate) 行。没有 Assessment 的
  Gate **不出现在这张表**（Matrix 里对应 `NOT_EVALUATED`），因此 `review_status`
  在本表恒为 `HUMAN_APPROVED`（proposal / machine 状态只在 `RUNS/` 内）。
- 适合 pandas / R / SQL / dashboard / candidate filtering / QC。

`TGT-NN/CURRENT/assessments.csv`（§7）与本表**列完全相同**（同一 `assessments_long`
表头），区别只是作用域：本表跨整个 GateSet，`CURRENT/assessments.csv` 只含
该一个 Gate。

---

## 6. GateSet → Gate folder

```text
GATESETS/
└── ADC_TARGET_GATESET-v1/
    ├── gateset_binding.yaml
    ├── TGT-01/
    ├── TGT-02/
    ├── TGT-03/
    ├── TGT-04/
    ├── TGT-05/
    ├── TGT-06/
    ├── TGT-07/
    └── TGT-08/
```

`gateset_binding.yaml`：

```yaml
gateset_id: ADC_TARGET_GATESET
gateset_version: "1.0"
instantiation_id: INST-CRC-REFRACTORY-ADC-TARGET-v1

# 成员 Gate 及每个 Gate 的绑定版本（来自 00_REGISTRY/gateset_registry.csv）
gates:
  - {gate_id: TGT-01, gate_version: "1.0"}
  - {gate_id: TGT-02, gate_version: "1.0"}
  - {gate_id: TGT-03, gate_version: "1.0"}
  - {gate_id: TGT-04, gate_version: "1.0"}
  - {gate_id: TGT-05, gate_version: "1.0"}
  - {gate_id: TGT-06, gate_version: "1.0"}
  - {gate_id: TGT-07, gate_version: "1.0"}
  - {gate_id: TGT-08, gate_version: "1.0"}

# GateSet 层 Decision policy（Assessments → Decision，见 §17）
decision_rule_ref: external:gateset/ADC_TARGET_GATESET/decision_rule@v1
fatal_gate_policy_ref: external:gateset/ADC_TARGET_GATESET/fatal_gate_policy@v1
required_gate_policy_ref: external:gateset/ADC_TARGET_GATESET/required_gate_policy@v1
```

> `gateset_binding.yaml` 只绑定/引用，**不内联 decision rule 的具体判据内容**——
> 那属于实例化层的科学定义，通过 `external:` 引用挂接。

以后 "把 100 个 target 全部跑 TGT-04" 时，Claude / Codex 的 working directory
直接进入 `.../ADC_TARGET_GATESET-v1/TGT-04/`，完全不需要关心 TGT-01、TGT-05
或整个 CRC-Atlas。

---

## 7. 一个 Gate 文件夹内部（固定三层）

```text
TGT-04/
│
├── gate_binding.yaml
│
├── CURRENT/                             # 快速浏览视图，可由 canonical JSON 重建
│   ├── assessments.csv                  # 本 Gate 全部 candidate 的 latest 判决
│   ├── evidence_index.csv               # 引用（不复制 EP），见 §13
│   └── unknowns.csv                     # critical_unknowns 汇总（分类见 §8）
│
├── ASSESSMENTS/                         # canonical judgment，per candidate 版本化
│   ├── CAND-L04-000001/
│   │   ├── v001.json
│   │   ├── v002.json
│   │   └── latest.json                  # 指向/复制最新 vNNN（symlink 或副本，见 7.2）
│   ├── CAND-L04-000002/
│   │   ├── v001.json
│   │   └── latest.json
│   └── ...
│
└── RUNS/                                # 包工头每次施工的历史，IMMUTABLE
    ├── RUN-TGT04-20260827-001/
    │   ├── run_manifest.json
    │   ├── candidates_input.csv
    │   ├── evidence_created.csv         # 本 run 新建的 EP id（EP 正文写进 30_EVIDENCE_LIBRARY）
    │   ├── assessment_proposals.csv     # 或 proposal JSON；不是 canonical assessment
    │   ├── qc_report.json
    │   └── logs/
    └── RUN-TGT04-20260915-001/
```

### 7.1 三层的职责

| 层 | 可变性 | 职责 |
|---|---|---|
| `RUNS/` | **IMMUTABLE**（run 完成后不再改） | 包工头每次施工的完整可追溯记录；修 bug → 新建 `-002` 重跑，不改旧 run |
| `ASSESSMENTS/` | append-only（新增 `vNNN`，不改旧版本） | Candidate × Gate 的 canonical judgment；evidence 更新 → 新版本（`v001` = 2026 public，`v002` = 2027 IHC，`v003` = proprietary antigen density …），完整历史保留 |
| `CURRENT/` | 可随时重建 | 只是快速浏览视图，无 source-of-truth 地位 |

### 7.2 `latest.json`

每个 `ASSESSMENTS/<candidate_id>/` 下 `latest.json` 是该 candidate 在本 Gate 的
最新 canonical assessment。实现为**副本**（不用 symlink，避免跨平台/打包问题）；
`latest.json` 内容必须与对应 `vNNN.json` 逐字节一致，且 `assessment_version`
字段标明是哪一版。

### 7.3 `gate_binding.yaml`

```yaml
gate_id: TGT-04
gate_version: "1.0"
gateset_id: ADC_TARGET_GATESET
gateset_version: "1.0"
instantiation_id: INST-CRC-REFRACTORY-ADC-TARGET-v1

candidate_level: L04
dominant_evidence_regime: PUBLIC_HYBRID   # 施工优先级元数据，不是 Evidence Strength

# Gate 层规则引用（Evidence → Assessment，只产生本 Gate 的 Direction+Strength）
gate_contract_ref: external:gate/TGT-04/contract@v1
evidence_ladder_ref: external:gate/TGT-04/evidence_ladder@v1
assessment_rule_ref: external:gate/TGT-04/assessment_rule@v1

# 本 Gate 的 primary Evidence Production Module
primary_module_id: MOD-TGT04
primary_module_version: "0.1.0"
```

> Gate 只产生自己的 `Direction + Strength`；`fatal_conditions` 只声明"潜在致命
> 信号"，是否 KILL 由 GateSet 的 `fatal_gate_policy` 决定（§17）。

---

## 8. CandidateGateAssessment：必须是 JSON

不要用 MD 当主文件，也不要只存在 CSV。Canonical：
`TGT-04/ASSESSMENTS/CAND-L04-000001/v001.json`。**canonical Assessment JSON 只
可能是 `review.status = HUMAN_APPROVED`**——proposal 与 machine-QC 结果留在
`RUNS/assessment_proposals.csv`（§16），Human Review 通过后才写成这里的
`vNNN.json`。被打回的提议不进 canonical，只在 RUN 里留痕。

```json
{
  "assessment_id": "ASMT-000001",
  "assessment_version": 1,

  "instantiation_id": "INST-CRC-REFRACTORY-ADC-TARGET-v1",

  "candidate_id": "CAND-L04-000001",
  "context_id": "CTX-CRC-REFRACTORY-MSSPMMR",
  "context_version": 1,

  "gateset_id": "ADC_TARGET_GATESET",
  "gateset_version": "1.0",

  "gate_id": "TGT-04",
  "gate_version": "1.0",

  "direction": "POSITIVE",
  "strength": "INDIRECT_STRONG",

  "evidence_refs": [
    { "evidence_id": "EP-00000123", "role": "SUPPORTING" }
  ],

  "aggregation_rationale": "Concordant tumor IHC and surface-proteomics datasets support membrane-localized target availability; no direct quantitative antigen-density measurement exists in refractory mCRC.",

  "critical_unknowns": [
    { "unknown": "Quantitative surface antigen density in refractory mCRC", "resolution": "EXPERIMENT_REQUIRED" }
  ],

  "evidence_ceiling": "Current evidence supports surface availability but not quantitative antigen density.",

  "review": {
    "status": "HUMAN_APPROVED",
    "reviewer": "human",
    "reviewed_at": "2026-08-27"
  }
}
```

这就是一个 matrix cell 的真正 source of truth。

### 8.1 字段规范

| 字段 | 必填 | 说明 |
|---|---|---|
| `assessment_id` | 是 | `ASMT-nnnnnn`，全 Instantiation 唯一 |
| `assessment_version` | 是 | int，从 `1` 起；evidence state 变化时 +1 并新建 `vNNN.json`（旧版本不改） |
| `instantiation_id` / `candidate_id` / `context_id` / `context_version` / `gateset_id` / `gateset_version` / `gate_id` / `gate_version` | 是 | 定位坐标；`candidate_id` 与 `context_id` 在此**首次关联**；`context_version` pin 到 `15_CONTEXTS/CTX-.../vNNN.yaml` |
| `direction` | 是 | `POSITIVE` / `NEGATIVE` / `CONFLICTING` / `INCONCLUSIVE` / `NOT_APPLICABLE` |
| `strength` | 是 | `DIRECT` / `INDIRECT_STRONG` / `WEAK` / `UNKNOWN`（组合约束见 §8.2） |
| `evidence_refs[]` | 是 | 每项 `{evidence_id, role}`，`role` ∈ `SUPPORTING` / `CONTRADICTING` / `CONTEXTUAL`；引用 `30_EVIDENCE_LIBRARY` 的 **immutable-by-ID** EP，只需 `evidence_id`（无 `evidence_version`，见 §10）。仅当 `strength = UNKNOWN` 时可为空数组 |
| `aggregation_rationale` | 是 | 聚合说明（自由文本） |
| `critical_unknowns[]` | 是（可空数组） | 每项 `{unknown, resolution}`，`resolution` ∈ `PUBLIC_RESOLVABLE` / `EXPERIMENT_REQUIRED` / `CURRENTLY_UNRESOLVABLE`。**absence of evidence（缺某类数据）只能进这里，不能变成 `CONTRADICTING` EP**（§10.2） |
| `evidence_ceiling` | 是 | 本 Assessment 证据能到的天花板（自由文本） |
| `review` | 是 | `{status, reviewer, reviewed_at}`；canonical `vNNN.json` **固定 `status = HUMAN_APPROVED`** |
| `superseded_by` | 否 | 若被更高版本取代，写新版本文件名 |
| `key_supporting_evidence` / `key_contradicting_evidence` | `CONFLICTING` 时必填、非空 | 分别记录冲突双方各自的 evidence 等级与来源（不因冲突自动降级 Strength） |

### 8.2 direction × strength 组合约束（machine-enforced）

| direction | 允许的 strength | evidence_refs | 备注 |
|---|---|---|---|
| `POSITIVE` / `NEGATIVE` | `DIRECT` / `INDIRECT_STRONG` / `WEAK` | ≥1（对应方向的 role） | **不允许 `UNKNOWN`** |
| `CONFLICTING` | `DIRECT` / `INDIRECT_STRONG` / `WEAK` | 至少 1 个 `SUPPORTING` **且** 至少 1 个 `CONTRADICTING`（schema `contains`/`minContains` 强制） | strength = 冲突双方中最强的可信等级；`key_supporting_evidence` / `key_contradicting_evidence` 必填非空 |
| `INCONCLUSIVE` + 有合格证据 | `DIRECT` / `INDIRECT_STRONG` / `WEAK` | ≥1 | Matrix 保留 strength（`INCONCLUSIVE/DIRECT` 等），不丢信息 |
| `INCONCLUSIVE` + 无合格证据（即 `UNKNOWN` 状态） | `UNKNOWN` | `[]` | Matrix 写 `UNKNOWN`；`direction=INCONCLUSIVE, strength=UNKNOWN, evidence_refs=[]` 是固定 serialization |
| `NOT_APPLICABLE` | `UNKNOWN`（serialization convention） | `[]` | Matrix 写 `NOT_APPLICABLE`；结构性不适用，与"没证据"不同 |

### 8.3 聚合铁律（对齐 Blueprint v1.3 §M05）

- `direction` ⊥ `strength`，且在 `CONFLICTING` 下同样成立：`strength` = 冲突
  双方中**最强**的可信证据等级，不自动降级。
- `evidence type ceiling > evidence quantity`：数量不能跨 measurement boundary
  把多个 weak evidence 累积成 `DIRECT`。
- **absence of evidence ≠ negative/contradicting evidence**：缺某类测量只写进
  `critical_unknowns`（通常 `EXPERIMENT_REQUIRED`），绝不构造一条 `CONTRADICTING`
  的 EP（§10.2）。
- Assessment **不产生** Candidate-level Decision（`KILL` / `NOMINATE` /
  `COMMIT`）——那是 GateSet 层（§17）。

---

## 9. Evidence Package：文件夹 + JSON + 可选 artifacts

```text
30_EVIDENCE_LIBRARY/PACKAGES/EP-00000123/
├── evidence.json      # 唯一 canonical machine-readable truth
├── summary.md         # 给人看，可由 JSON 自动生成，不是 source of truth
└── artifacts/         # 只放真正支撑本条 evidence 的东西（可选，不是每个 EP 都有）
    ├── extracted_table.csv
    ├── figure.png
    └── analysis_output.csv
```

`artifacts/` 允许内容：论文 Supplement 提取的表、dataset analysis output、plot、
statistical result、sequence alignment、structure result。

---

## 10. EvidencePackage 本身不带 `POSITIVE/DIRECT`（必须现在钉死）

**错误：**

```json
{ "evidence_id": "...", "direction": "POSITIVE", "strength": "DIRECT" }
```

因为同一条 evidence（"某 ADC 在乳腺癌 Phase I 有 response"）对 `TGT-01 ADC
Modality Precedent` 可能是强证据，对 `TGT-04 quantitative surface density`
却根本不是 direct evidence。

**EvidencePackage 应是一个中性的 empirical observation：**

```json
{
  "evidence_id": "EP-00000123",
  "schema_version": 1,

  "claim": "Target X protein was detected on malignant epithelial cell membranes in cohort Y.",

  "measurement": {
    "type": "IHC",
    "analyte": "Target X protein",
    "readout": "membranous staining",
    "result": "68% positive tumors"
  },

  "candidate_refs": ["CAND-L04-000001"],

  "study_context": {
    "indication": "colorectal cancer",
    "treatment_state": "mixed",
    "sample_type": "primary tumor",
    "n": 124
  },

  "provenance": {
    "source_id": "SRC-00000881",
    "source_type": "PMID",
    "source_identifier": "12345678",
    "locator": "Figure 2; Supplementary Table S3",
    "retrieved_at": "2026-08-27"
  },

  "interpretation_boundary": {
    "directly_supports": ["membrane-localized protein is detectable in CRC tumor cells"],
    "does_not_support": ["quantitative antigen density", "refractory-state persistence", "ADC therapeutic window"],
    "limitations": ["non-refractory cohort", "semiquantitative IHC"],
    "evidence_ceiling": "protein-level surface plausibility"
  },

  "derivation": {
    "module_run_id": "RUN-TGT04-20260827-001",
    "code_commit": "abc123"
  }
}
```

### 10.1 EvidencePackage 是 immutable-by-ID

> **一个 `EP-*` 一旦被任何 Assessment 引用，其 `evidence.json` 内容永不原地
> 修改。** 纠错、新增 interpretation、或换来源 → 建**新的** `EP-*`，旧 EP 写
> `superseded_by: EP-<新id>` 并把 `30_EVIDENCE_LIBRARY/evidence_index.csv` 的
> `status` 改为 `SUPERSEDED`（或 `RETRACTED`）。

这样 Assessment 的 `evidence_refs[]` 只需 `evidence_id`，**不需要
`evidence_version`**，版本引用链自然闭合：历史 Assessment 引用的 `EP-00000123`
永远是当初那份内容。

### 10.2 absence of evidence ≠ contradicting evidence

"没有某类测量数据"（如"refractory mCRC 中没有定量抗原密度数据"）**不是一条
EP**，更不是 `CONTRADICTING` 证据。它只进入引用它的 Assessment 的
`critical_unknowns`，通常 `resolution = EXPERIMENT_REQUIRED`。构造一条
"没有数据" 的 negative EP 是 StelligenOS 明确禁止的推理谬误。

### 10.3 `evidence.json` 字段规范

| 字段 | 必填 | 说明 |
|---|---|---|
| `evidence_id` | 是 | `EP-nnnnnnnn`，全局唯一 |
| `schema_version` | 是 | int，从 `1`；仅当 `evidence.json` 的 **schema 结构**升级时变化，**不是**内容修订版本（内容不可原地修订，见 §10.1） |
| `claim` | 是 | 一句中性 empirical 陈述，**不含** direction/strength 词 |
| `measurement` | 是 | `{type, analyte, readout, result, unit?}`；`type` 声明 measurement class（RNA / protein / surface density / …），**不得跨 class 使用** |
| `candidate_refs[]` | 是 | 相关 candidate_id（仅召回提示，不是定级） |
| `study_context` | 是 | `{indication, treatment_state, sample_type, n, model?, assay?}` |
| `provenance` | 是 | `{source_id, source_type, source_identifier, locator, retrieved_at}`；`source_id` 指向 `30_EVIDENCE_LIBRARY/source_index.csv`（§14） |
| `interpretation_boundary` | 是 | `{directly_supports[], does_not_support[], limitations[], evidence_ceiling}` |
| `derivation` | 是 | `{module_run_id, code_commit}` |
| `superseded_by` | 否 | `EP-nnnnnnnn`；本 EP 被纠错/更新的新 EP 取代时填 |

> **`evidence.json` 里不允许出现 `direction` / `strength` / `grade` / `DIRECT` /
> `POSITIVE` 等定级字段。** 真正的 `POSITIVE / INDIRECT_STRONG` 发生在 Assessment。

---

## 11. Evidence ↔ Assessment 通过引用关联

```text
EP-00000123 ┐
EP-00000124 ├─→ CandidateGateAssessment ─→ POSITIVE / INDIRECT_STRONG
EP-00000125 ┘
```

Assessment 在 `evidence_refs[]` 里给每条 EP 一个 `role`：`SUPPORTING` /
`CONTRADICTING` / `CONTEXTUAL`。**同一个 EP 在另一个 Gate 的 Assessment 里可以
换 role** —— 这才是真正 reusable。

---

## 12. EvidencePackage 全局存储，不在 Gate 内存一份

**禁止：**

```text
TGT-01/evidence/EP-001
TGT-02/evidence/EP-001-copy
TGT-04/evidence/EP-001-copy2
```

**只有一份：**

```text
30_EVIDENCE_LIBRARY/PACKAGES/EP-00000123/
```

然后 `TGT-01 Assessment → EP-00000123`、`TGT-04 Assessment → EP-00000123`。
Evidence Package Library 是 StelligenOS 最有价值的长期资产之一——引用而非复制，
越跑越值钱。

---

## 13. Gate folder 只放 evidence index，不复制 EP

`TGT-04/CURRENT/evidence_index.csv`：

| evidence_id | candidate_id | role | assessment_id |
|---|---|---|---|
| EP-00000123 | CAND-L04-000001 | SUPPORTING | ASMT-000001 |
| EP-00000124 | CAND-L04-000001 | SUPPORTING | ASMT-000001 |
| EP-00000140 | CAND-L04-000001 | CONTRADICTING | ASMT-000001 |

这是引用，不是复制。EP 正文只在 `30_EVIDENCE_LIBRARY/PACKAGES/` 下。

---

## 14. Source 全局 registry

一篇 paper 可产生多个 EP，因此 `30_EVIDENCE_LIBRARY/source_index.csv`：

| source_id | source_type | external_id | title | year | external_ref |
|---|---|---|---|---:|---|
| SRC-00000001 | PMID | 12345678 | ... | 2025 | external:pmid/12345678 |
| SRC-00000002 | GEO | GSE123456 | ... | 2024 | external:geo/GSE123456 |

`source_type` ∈ `PMID` / `PMC` / `DOI` / `NCT` / `GEO` / `PATENT` / `REGULATORY`
/ `COMPANY_DISCLOSURE` / `DATASET` / `OTHER`。EP 只引 `source_id`，不重复整篇
citation metadata。

`30_EVIDENCE_LIBRARY/evidence_index.csv` 汇总所有 EP：

| evidence_id | schema_version | claim_short | measurement_type | primary_source_id | candidate_refs | created_at | status | superseded_by |
|---|---|---|---|---|---|---|---|---|

`status` ∈ `ACTIVE` / `SUPERSEDED` / `RETRACTED`。EP 内容不可原地修订（§10.1）；
纠错走"新 EP + `superseded_by`"。

---

## 15. Module run 必须 immutable

每次 Gate Module run：`TGT-04/RUNS/RUN-TGT04-20260827-001/`，固定含
`run_manifest.json` / `candidates_input.csv` / `evidence_created.csv` /
`assessment_proposals.csv` / `qc_report.json` / `logs/`。

`run_manifest.json`：

```json
{
  "run_id": "RUN-TGT04-20260827-001",
  "gate_id": "TGT-04",
  "gate_version": "1.0",
  "instantiation_id": "INST-CRC-REFRACTORY-ADC-TARGET-v1",
  "module_id": "MOD-TGT04",
  "module_version": "0.1.0",
  "code_commit": "abc123",
  "started_at": "2026-08-27T14:00:00Z",
  "completed_at": "2026-08-27T15:12:00Z",
  "candidate_count": 100,
  "status": "COMPLETED"
}
```

`status` ∈ `RUNNING` / `COMPLETED` / `FAILED` / `ABORTED`。运行完成 → **不再
修改**。修 bug → `RUN-TGT04-20260827-002` 重新跑。

---

## 16. Proposal 与 Human-approved Assessment 必须分开

Module 只能产生 `assessment_proposals.csv`（或 proposal JSON），**不能直接覆盖
canonical assessment**。流程：

```text
Gate Module → Evidence Packages → Assessment Proposal → Machine QC → Human Review
           → Canonical CandidateGateAssessment (ASSESSMENTS/<cand>/vNNN.json) → Matrix refresh
```

`review.status` 从 `MACHINE_PROPOSED` → `MACHINE_QC_PASSED` → `HUMAN_APPROVED`
（或 `HUMAN_REJECTED`）。只有 `HUMAN_APPROVED` 的版本能进 `CURRENT/` 与 Matrix。

---

## 17. Decision 不放在 Gate folder

一个 Gate 只决定自己的 `Direction + Strength`（如 `TGT-05 NEGATIVE/DIRECT`）。
`KILL` / `HOLD` / `MORE_EVIDENCE` / `NOMINATE` / `COMMIT` 属 **GateSet-level
Decision**，放在：

```text
20_INSTANTIATIONS/<inst>/DECISIONS/
├── decisions.csv       # view
└── DEC-0001.json       # canonical
```

**不是** `TGT-05/decision.json`。Gate 不能自己杀 Candidate——它只产生 fatal
signal，GateSet 的 `fatal_gate_policy` 才 `KILL`。

`DEC-0001.json` —— **每个 Gate 的 snapshot 必须 pin `{assessment_id,
assessment_version, cell}`**，这样历史 Decision 永远知道当时用的确切 evidence
state（版本引用链闭合）：

```json
{
  "decision_id": "DEC-0001",
  "instantiation_id": "INST-CRC-REFRACTORY-ADC-TARGET-v1",
  "candidate_id": "CAND-L04-000001",
  "gateset_id": "ADC_TARGET_GATESET",
  "gateset_version": "1.0",
  "decision": "HOLD",
  "triggered_by": [
    { "gate_id": "TGT-07", "assessment_id": "ASMT-000007", "assessment_version": 1, "reason": "shedding/sink liability unresolved" }
  ],
  "assessment_snapshot": {
    "TGT-01": { "assessment_id": "ASMT-000001", "assessment_version": 1, "cell": "POSITIVE/DIRECT" },
    "TGT-02": { "assessment_id": "ASMT-000002", "assessment_version": 1, "cell": "POSITIVE/DIRECT" },
    "TGT-03": { "assessment_id": "ASMT-000003", "assessment_version": 2, "cell": "POSITIVE/INDIRECT_STRONG" },
    "TGT-04": { "assessment_id": "ASMT-000004", "assessment_version": 1, "cell": "POSITIVE/INDIRECT_STRONG" },
    "TGT-05": { "assessment_id": "ASMT-000005", "assessment_version": 1, "cell": "CONFLICTING/DIRECT" },
    "TGT-06": { "assessment_id": "ASMT-000006", "assessment_version": 1, "cell": "POSITIVE/DIRECT" },
    "TGT-07": { "assessment_id": "ASMT-000007", "assessment_version": 1, "cell": "POSITIVE/WEAK" },
    "TGT-08": "NOT_EVALUATED"
  },
  "decision_rule_ref": "external:gateset/ADC_TARGET_GATESET/decision_rule@v1",
  "review": { "status": "HUMAN_APPROVED", "reviewer": "human", "reviewed_at": "2026-08-27" }
}
```

`assessment_snapshot` 的每个 gate_id 值：要么是对象 `{assessment_id,
assessment_version, cell}`，要么是字符串 `"NOT_EVALUATED"`（该 Gate 没有
HUMAN_APPROVED Assessment）。`cell` 取值同 §4.1（含 `UNKNOWN` / `NOT_APPLICABLE`，
**不含 `NOT_EVALUATED` 作为 cell**——那用字符串形式表示）。

`decision` ∈ `GO` / `CONDITIONAL_GO` / `HOLD` / `MORE_EVIDENCE` / `KILL` /
`NOMINATE` / `COMMIT`（对齐 Blueprint v1.3 §M06）。canonical `DEC-*.json`
**固定 `review.status = HUMAN_APPROVED`**（proposal 不进 canonical）。

---

## 18. 最终数据流（物理文件完全对应）

```text
Candidate list + Gate Contract + Context
   → Gate Module (TGT-NN/RUNS/RUN-.../)
   → Sources (30_EVIDENCE_LIBRARY/source_index.csv)
   → Evidence Packages (30_EVIDENCE_LIBRARY/PACKAGES/EP-.../)
   → Assessment Proposal (TGT-NN/RUNS/.../assessment_proposals.csv)
   → Machine QC + Human approval
   → CandidateGateAssessment (TGT-NN/ASSESSMENTS/<cand>/vNNN.json)
   → Matrix (20_INSTANTIATIONS/<inst>/MATRICES/*.matrix.csv + *.assessments.csv)
   → GateSet Decision (20_INSTANTIATIONS/<inst>/DECISIONS/DEC-*.json)
   → NOMINATE / COMMIT → 下一 Candidate Level（新 Instantiation）
```

---

## 19. 五类 primary product outputs（冻结，见 §0.3）

Candidate CSV · Matrix CSV · CandidateGateAssessment JSON · EvidencePackage
folder · Decision JSON。以后不得再随意增加新的 primary output 格式；新增须走
本 spec 版本修订。`Context` / `Instantiation` / `gate_binding` /
`gateset_binding` / `run_manifest` 是配置/绑定/施工层的 canonical record，
不计入这五类，但同样受本 spec 的字段与 schema 约束。

---

## 20. 建筑图

```text
                       STELLIGENOS
                            │
                    Candidate Registry (10_CANDIDATES/Lnn_*.csv)
                            │
                  ┌─────────┴─────────┐
                  │                   │
                L04                 L05 ...
             ADC TARGET            EPITOPE
                  │
                  ▼
              Instantiation (20_INSTANTIATIONS/INST-.../instantiation.yaml)
                  │
                  ▼
               GateSet (GATESETS/ADC_TARGET_GATESET-v1/gateset_binding.yaml)
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
    TGT-01      TGT-02  ...  TGT-08     (一个 Gate 一个 workspace)
      │           │           │
    Module      Module      Module      (TGT-NN/RUNS/, IMMUTABLE)
      │
      ▼
   Sources (source_index.csv)
      │
      ▼
 Evidence Packages (30_EVIDENCE_LIBRARY/PACKAGES/) ──────┐
      │                                                  │ reusable
      ▼                                                  │ (引用而非复制)
 Assessment (TGT-NN/ASSESSMENTS/<cand>/vNNN.json) ◄───────┘
      │
      ▼
Candidate × Gate Matrix (MATRICES/*.matrix.csv + *.assessments.csv)
      │
      ▼
 GateSet Decision (DECISIONS/DEC-*.json)
      │
      ▼
NOMINATE / COMMIT
      │
      ▼
Next Candidate Level
```

---

## 附录 A — ID 命名规范（冻结）

| 对象 | 格式 | 例 |
|---|---|---|
| Candidate | `CAND-Lnn-nnnnnn`（`nn` = level 两位，`nnnnnn` = 6 位零填充序号） | `CAND-L04-000001` |
| Context | `CTX-<UPPER-KEBAB>`；目录内 `vNNN.yaml`（`context_version` int） | `CTX-CRC-REFRACTORY-MSSPMMR` / `v001.yaml` |
| Instantiation | `INST-<UPPER-KEBAB>-v<N>` | `INST-CRC-REFRACTORY-ADC-TARGET-v1` |
| GateSet | `<UPPER_SNAKE>_GATESET`；目录带版本 `<...>-v<N>` | `ADC_TARGET_GATESET` / `ADC_TARGET_GATESET-v1` |
| Gate | 由 canonical GateSet 文档定义（如 `TGT-01`…`TGT-08`） | `TGT-04` |
| EvidencePackage | `EP-nnnnnnnn`（8 位零填充） | `EP-00000123` |
| Source | `SRC-nnnnnnnn`（8 位零填充） | `SRC-00000881` |
| Assessment | `ASMT-nnnnnn`（6 位零填充） | `ASMT-000001` |
| Decision | `DEC-nnnn`（4 位零填充，per Instantiation） | `DEC-0001` |
| Module | `MOD-<GATE 无连字符>` | `MOD-TGT04` |
| Run | `RUN-<GATE 无连字符>-<YYYYMMDD>-nnn` | `RUN-TGT04-20260827-001` |

序号全局单调递增、不复用；跨 Instantiation 的 Candidate / EP / Source 序号
共用同一全局计数器（由 `00_REGISTRY` 维护）。Assessment / Decision 序号
per-Instantiation。

## 附录 B — machine-readable schema 索引

所有 schema 位于 `src/contracts/data_layout/`。

| 对象 | schema |
|---|---|
| Candidate CSV 一行（identity 字段） | `candidate.schema.json` |
| Context `15_CONTEXTS/CTX-*/vNNN.yaml` | `context.schema.yaml` |
| CandidateGateAssessment | `assessment.schema.json` |
| EvidencePackage `evidence.json` | `evidence_package.schema.json` |
| Instantiation `instantiation.yaml` | `instantiation.schema.yaml` |
| `gate_binding.yaml` / `gateset_binding.yaml` | `gate_binding.schema.yaml`（`oneOf` 两分支） |
| `run_manifest.json` | `run_manifest.schema.json` |
| Decision `DEC-*.json` | `decision.schema.json` |
| 所有 CSV 的规范表头（Matrix / assessments-long / context_index / registry / index / run …） | `csv_headers.yaml`（logical name → 有序列名） |

> **本仓库不存放任何 `.csv` 文件**（`scripts/verify_repository_boundary.sh`
> 禁止 data-like 文件）。CSV 的规范定义在 `csv_headers.yaml`；`scaffold_data_layout.sh`
> 在**外部** data root 用它写出真实 `.csv` 表头。逐文件的 worked example 见
> `docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md`。

## 附录 C — 与仓库边界的关系

本仓库（StelligenOS 实现仓库）**不保存**本布局下的任何真实数据、任何 `.csv`
文件、EP 正文或 run 产物。仓库只保存：

- 本 spec（`docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md`）
- `src/contracts/data_layout/` 下的 JSON/YAML schema 与 `csv_headers.yaml`
- `docs/protocols/examples/STELLIGENOS_DATA_LAYOUT_v1_worked_example.md`
  （单文档 worked example，正文顶部标注 `REFERENCE EXAMPLE — NOT REAL DATA`，
  所有 CSV/JSON/YAML 以 fenced code block 呈现，不落地为文件）
- `scripts/scaffold_data_layout.sh`

真实数据全部在 `$STELLIGENOS_DATA`（仓库外部）。

## 附录 D — 版本维护

- 本 spec 走 `docs/protocols/` 的版本后缀约定（`.v1.0.md` / `.v1.1.md` /
  `.v2.0.md`），与 `ADCdb_Atlas_ADC_AIDD_design.v0.2.md` 一致。
- §1 顶层目录形状、§0.2 四原则、§0.3 五类 primary product outputs、附录 A ID
  规范、以及 EvidencePackage immutable-by-ID（§10.1）与版本引用链闭合（Decision
  pin `assessment_version`，§17）为**冻结项**，
  修改须 `v2.0` + 专家审核。
- 字段增删（不破坏既有）可在 `v1.x` 内进行，须同步更新 `src/contracts/
  data_layout/` 与本附录。
- 获 ChatGPT `APPROVE` 后，`v1.0-draft` → `v1.0`；后续 runtime migration
  PR A–E（见 CURRENT_SYSTEM v5 §16 B 组问题 23）须以本 spec 为物理层依据。
