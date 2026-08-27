# StelligenOS 当前设计架构与模块逻辑（专家审核版）

## 0. 版本与审核基线

- 文档 ID：`CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW`
- 当前文档版本：`v5-draft`
- 架构审核基线：`STELLIGENOS-ARCH-2026.08.27-v5-draft`
- 仓库基线：`main@a8afcd4`
- 基线日期：`2026-08-27`
- 版本状态：`PENDING_EXPERT_REVIEW`
- 规范路径：本文件固定为最新版本，不在文件名中写版本号。
- 已冻结快照：`docs/architecture/versions/`；当前只有经 PR #42 批准的 `v1`。
  `v2-draft`、`v3-draft`、`v4-draft` 均未获批，因此都没有快照，也不补造快照。

StelligenOS 当前没有一个覆盖全部模块的单一软件 SemVer。核心合同、Gate
拓扑和 GenModule 各自独立版本化。因此，本节的 `v5-draft` 是**架构说明文档
版本**，不是新的运行时发布标签，也不改变任何现有合同版本。

### 0.1 本版相对 `v4-draft` 的主要变化

`v5-draft` 是一次**深度架构对齐**：把外部 Blueprint
`StelligenOS-产品形态-Blueprint v1.3` 与
`StelligenOS_Candidate_Levels_and_GateSets_Blueprint.v0.1`（下称 **Blueprint
v1.3**）确立的决策模型，正式提升为本仓库架构说明的**主干**，并把现有实现
（8 个具名对象、45-Gate 拓扑、sponsor 轴、GenModule 目录、CRC Level 01）改写
为**映射到该主干上的当前实现状态**。

1. **新的架构主干（第 2 节重写）。** 引入 Blueprint v1.3 冻结的六对象决策模型
   `Candidate × Context × Gate/GateSet × EvidencePackage × CandidateGateAssessment
   × Decision`，以及 `Instantiation` 配置/绑定层（**不是第七个对象**）。
   产品形态是 Candidate × Gate 矩阵 + 逐层 drill-down。
2. **Candidate Levels 与 canonical GateSet registry（第 4 节新增 4.2–4.5）。**
   固定 L0–L14 的 Candidate Level 谱系与每级对应的 canonical GateSet；固定
   Gate ID → Candidate Level 的归属骨架；引入 evidence-regime 词表
   `PUBLIC_PRIMARY / PUBLIC_HYBRID / EXPERIMENT_PRIMARY / DEVELOPMENT_PRIMARY`
   作为**施工优先级**元数据，明确它不是 Evidence Strength。
3. **两层规则显式分离（第 6 节重写）。** Gate 层 `assessment_rule`
   （Evidence → Assessment）与 GateSet 层 `decision_rule` / `fatal_gate_policy`
   / `required_gate_policy`（Assessments → Decision）不再共用同一字段。
4. **EvidencePackage 无固有 Strength grade + 引用而非复制。** Strength 是
   Assessment 层属性，随 Gate × Context 变化；同一 EvidencePackage 被多个
   Assessment 通过 `evidence_package_ids` 引用，不产生副本。
5. **一 Gate 一主 Module 施工责任制（第 6.4 节新增）。** 默认每个 Gate 只有
   一个 primary Evidence Production Module；共享 infrastructure 可跨 Gate 复用
   但不拥有 Gate-specific scientific decision authority。
6. **CRC Level 01 改写为第一次 Instantiation（第 11 节重写）。**
   `{candidate_type = ADC Target, context = refractory mCRC, modality = ADC,
   gateset = CRC-ADC-TARGET-GATESET-v1, evidence regime = public evidence only}`。
   41-target / 369-pair 冻结计数、三把 eligibility lock、`EVGAP-01` /
   `EVGAP-02` 阻断状态**全部按事实保留不变**。
7. **crosswalk（第 4.5 节新增）。** `core_objects@1.1` 的 8 个具名对象、
   45-Gate 拓扑、ClinicalHypothesis 递进锁定，逐一映射到 Blueprint v1.3 的
   Candidate Type × Level / canonical GateSet。
8. **仓库基线 `main@4d895d7` → `main@a8afcd4`；测试数 `413` → `555`**
   （逐项复核，见第 15/16 节）。
9. **第 16 节审核问题重构为两组。** 承接 1–17；新增内容分为 **A 组
   RESOLVED BY BLUEPRINT v1.3**（架构方向已定，开放的只是 migration 策略）
   与 **B 组 IMPLEMENTATION / MIGRATION BLOCKERS**（真正待实现设计的问题），
   并在 B 组问题 23 直接给出推荐的 runtime migration PR 顺序（PR A–E）。

### 0.2 本版**不**修改的内容

**本版不修改任何 runtime 工件——`src/` 代码、machine contract、测试或科学 Gate
判据；但本版确实是一次 architecture-specification change**：它把 Blueprint v1.3
六对象模型提升为 `contract.zh-CN.md` 的规范目标架构。因此本 PR 的治理定位是

> **DOC-LEVEL ARCHITECTURE ALIGNMENT / NO_RUNTIME_CONTRACT_CHANGE**

不再使用 `NO_ARCHITECTURE_CHANGE`（该措辞不准确：spec 已变，只是 runtime
implementation 未变）。具体不改动：

- 不修改 `src/contracts/core_objects.yaml`（仍为 8 对象，`version: "1.1"`）。
- 不修改 `src/contracts/gate_system.yaml`（仍为 45 Gate，拓扑 `0.2.0`）。
- 不修改任何 `src/` 代码、`genmodules/` 或 `extensions/`。
- 不解除 `EVGAP-01` / `EVGAP-02`，不执行任何抽取或外部运行。
- 不把 `v5-draft` 复制进 `docs/architecture/versions/`。

Blueprint v1.3 的六对象模型在本版中作为**目标决策层契约**呈现；把它落到
`core_objects.yaml` / `gate_system.yaml` / `src/` 是本 PR 获批之后的独立实现
任务，见第 16 节 B 组 blocker 与推荐 migration 顺序。发现的实现层不一致只
登记为审核问题，另立治理任务修复（第 17 节规则 6）。

### 0.3 Runtime Conformance（运行时符合性）

```text
Target architecture:
  Blueprint v1.3 six-object model
  （Candidate · Context · Gate/GateSet · EvidencePackage ·
   CandidateGateAssessment · Decision + Instantiation binding layer）

Current runtime contracts:
  core_objects@1.1                       （8 legacy object types）
  gate_system@0.1.0 / topology@0.2.0     （45 legacy gates, 3 chains）
  GateInputEnvelope / GateModelOutput@2.1.0  （score/confidence/status，无 Direction×Strength）

Runtime conformance:
  MIGRATION_PENDING

Rule:
  在后续 migration PR（见 §16 推荐顺序 PR A–E）合并之前，
  repository runtime 不得声称已实现 Blueprint v1.3 conformance。
  "architecture target 已冻结" 与 "runtime implementation 仍 legacy"
  是两个不同事实，任何执行 agent 不得混用。
```

### 0.4 章节编号说明

`v5-draft` 保持 `v4-draft` 的顶层章节编号不变（§7 sponsor 轴、§16 审核问题等
引用位置稳定），深度改写发生在 §2 / §4 / §6 / §11 / §13 的**节内**。历史
handoff 与 worklog 对 `v4-draft` 章节的引用属审核时快照，不受影响。

---

## 1. 一句话定义

StelligenOS 是一个面向 biotechnology asset generation 的**软件操作系统实现**：
它把治疗资产的**生成与开发**组织为一个版本化、context-aware 的
**Candidate × Gate 决策矩阵**，矩阵的每个 cell 由可复用、独立可审计的
**Evidence Package** 支撑，能够从公开数据驱动的 candidate selection 持续运作到
专有实验驱动的资产开发，横跨任意 Candidate 类型与开发阶段而**不改变底层数据
模型**。

它不是数据库，也不是一个可以自行宣布资产成功的自治代理。真实数据、证据、
模型权重、运行结果、法律意见、投资结论和生命周期状态全部由外部工作区持有；
仓库只保存对象、合同、端口、规则、代码、测试和文档。

它也不是：通用知识库、文献摘要器、通用数值打分系统、固定的 ADC-target
pipeline、单一的 CRC Atlas，或实验的替代品。

---

## 2. 核心命题与六对象决策模型

### 2.1 核心命题

```text
Candidate × Context × Gate
  → CandidateGateAssessment
  → Evidence Packages
  → Source / Raw Provenance
  → Decision
```

StelligenOS 的主界面是一个矩阵：行是 Candidate，列是 Gate，cell 是该 Candidate
在某个 Context 下、某个 Gate 上的 `Direction + Strength` 评估
（`CandidateGateAssessment`）。点击任意 cell 展开为一组 Evidence Package；
点击任意 Evidence Package 看到原始来源、判据与局限性。任何非 `UNKNOWN` 的 cell
都必须能追溯到独立可审核的 Evidence Package，每个 Package 都必须能追溯到其
原始来源。

Module（证据生产机器）不是产品层的一等对象。持久资产是
Candidate–Context–Gate–Evidence–Decision 系统本身，不是某一套分析或某一个
dataset。

### 2.2 六个冻结的核心对象

| # | 对象 | 关键约束 |
|---|---|---|
| 1 | `Candidate` | 与 Context 解耦（context-independent），**不持有 `context_id`**。同一 `candidate_id`（如 HER2）可在多个 Context 下复用而不产生副本。 |
| 2 | `Context` | 强制对象。承载 indication、stage、line of therapy、molecular subtype、patient territory、modality、treatment history、model、development stage 等维度。 |
| 3 | `Gate`（及其 `GateSet`） | 决策要求，不是分析、不是数据集、不是 Module。Gate 层只产生本 Gate 的 `Direction + Strength`；GateSet 层才产生 Candidate-level `Decision`。 |
| 4 | `EvidencePackage` | 原子、可复用、full provenance。**无固有 Strength grade**——`DIRECT / INDIRECT_STRONG / WEAK` 是 `EvidencePackage × Gate × Context` 之后在 Assessment 层产生的结果，永不回写。 |
| 5 | `CandidateGateAssessment` | 矩阵最小 cell，也是最小决策面对象。**Candidate 与 Context 的关联在此首次发生。** |
| 6 | `Decision` | 把一个 Candidate 名下多个 Assessment 转化为显式状态转移：`GO / CONDITIONAL_GO / HOLD / MORE_EVIDENCE / KILL / NOMINATE / COMMIT`。 |

### 2.3 Instantiation：配置/绑定层（不是第七个对象）

`Instantiation` 是 configuration/binding 对象，只负责把一个 `candidate_type`
+ 一个 `context_id` + 一个 `modality` 绑定到某个版本化的 `gateset_id`，本身
**不产生任何科学结论、不持有 Evidence、不产生 Assessment**。

最小 Contract 字段：`instantiation_id` / `candidate_type` / `context_id` /
`modality` / `gateset_id` / `gateset_version` / `status` / `version`。

同一个通用引擎通过更换 Instantiation 绑定：

- **横向跨项目**：CRC-Atlas（refractory mCRC）vs. 其它 indication；
- **纵向跨生命周期阶段**：Target → Epitope → Binder → ADC Design → ADC Hit →
  ADC Lead → Development Candidate（见第 4 节 Candidate Levels）。

底层六对象模型在所有绑定下不变。`Instantiation` 是**唯一**的跨项目/跨阶段
扩展机制——不允许为新场景绕过它直接扩展六对象模型。

### 2.4 CRC-Atlas 的重新定义

> **CRC-Atlas 不是 datasets 的集合。它是 `refractory mCRC × ADC` context 下，
> 为 Candidate–Gate Matrix 持续生产、标准化和聚合 Evidence Packages 的
> evidence engine。**

它是
`{candidate_type=ADC Target, context=refractory mCRC, modality=ADC, gateset=CRC-ADC-TARGET-GATESET-v1}`
的一次 Instantiation（见第 11 节）。

---

## 3. 不可破坏的设计原则

`v5-draft` 把 `v4-draft` 的 11 条原则与 Blueprint v1.3 的架构不变量合并为
16 条。

1. **临床与产品假设协同。** Candidate 不能脱离人群、治疗场景和 intended
   benefit 被孤立排序。
2. **递进锁定。** 早期 endpoint class、protocol endpoint 和 observed outcome
   是三种不同对象。上一级 Candidate 被选定后，冻结为下一级搜索的 Context /
   Constraint（第 4.1 节）。
3. **证据与判断分离。** Retrieval、assertion、expert review、Gate output 和
   human decision 不得互相冒充。
4. **未知不是失败。** `unknown`、`null`、`NOT_EVALUATED`、`UNRESOLVED`、
   `UNKNOWN` 不得自动转换为 0、FAIL 或安全。
5. **支持与反对证据并存。** Supporting、opposing、conflicting、missing 和
   provenance 都必须保留。
6. **规则和模型不直接改写决策。** Rule/Model 只能产生受限输出，不能自行改
   Gate 分数、状态或 Profile。
7. **状态不自动晋级。** 脚本成功、模型高分、单个 Gate 通过或模块完成都不
   构成生命周期晋级。
8. **Fatal-first 先于加权平均。** 明确致命风险不能被其他高分抵消。
9. **外部引用优先。** 跨边界对象使用版本化 `external:` reference，不把业务
   记录复制进仓库。
10. **全过程可审计。** 输入版本、合同、代码提交、来源、缺失、审核和人类
    决定均须可追溯。
11. **发起方判断与科学事实分离。** Sponsor-relative 的路由、承诺和资源计划
    不得改写、覆盖或反向污染任何科学 Gate 事实。`OUT_OF_MANDATE` 与
    `STOP_FOR_SPONSOR` 表示「当前发起方不推进」，**不是** KILL。
12. **Candidate identity 与 Context 解耦。** Candidate contract 不含
    `context_id`；Candidate × Context 只发生在 Assessment 与 Instantiation 层。
13. **Direction 与 Strength 正交，且在 `CONFLICTING` 状态下同样成立。**
    冲突不自动降级 Strength——`Strength` = 冲突双方中最强的可信证据等级。
14. **每个 Gate 拥有自己的 Evidence Ladder 与 evidence ceiling；不存在全局
    判据。** `EvidencePackage` 本身不持有跨 Gate 的固有 Strength grade。
15. **evidence type ceiling > evidence quantity。** 同一 measurement class 内
    数量可增强 confidence，但不能跨 measurement boundary 把多个 weak evidence
    累积成 `DIRECT`。禁止任何通用数值分数（如 `+3/+2/…/-3`）。
16. **两层规则不共用字段。** Evidence → Assessment（Gate 层 `assessment_rule`）
    与 Assessments → Decision（GateSet 层 `decision_rule` /
    `fatal_gate_policy` / `required_gate_policy`）是两套规则；`UNKNOWN` 与
    `CONFLICTING` 是一等状态，不被消解为假阳性/假阴性。

原则 12–16 是 `v5-draft` 依据 Blueprint v1.3 新增。它们对应的目标软件形态见
第 4–6 节；对应的当前实现差距见第 16 节 A 组 A1/A2 与 B 组问题 18–20。

---

## 4. 总体软件架构

### 4.1 六个软件层（不变）

| 层 | 当前职责 | 当前实现位置 |
|---|---|---|
| Operating System | 统一架构、对象、合同、治理和 boot 边界 | `docs/architecture/`、`src/repository/boot.py` |
| Lifecycle | 约束合法阶段和递进 lock，不持久化状态 | `src/lifecycle/` |
| Capabilities | 定义机会生成、证据、Gate、排序、路线等端口 | `src/capabilities/` |
| Cross-cutting | Knowledge Ledger、Model governance、IP/FTO、DD、Portfolio | `src/cross_cutting/` |
| Objects | 定义核心对象身份，不保存对象记录 | `src/objects/`、`src/contracts/core_objects.yaml` |
| Repository implementation | 连接外部运行时和外部工作区 | `src/repository/` |

依赖方向必须从模块实现指向内核合同，内核 `src/` 不得反向依赖 `genmodules/`
或 `extensions/`。这条边界已有测试保护。

`src/contracts/` 现在同时承载两类工件——YAML 身份/Schema 声明（如
`core_objects.yaml`、`gate_system.yaml`），以及 Phase 1–4 引入的 Python 形状
校验器（`sponsor_strategy.py` 等）。上表把 `src/contracts/` 归入 Objects 层，
已不足以描述这一层的实际内容。是否需要为 sponsor-relative 合同单列一层，见
第 16 节问题 13。

### 4.2 六对象决策模型（Blueprint v1.3，目标决策层契约）

第 2.2 节的六对象是本架构的决策层主干。它在软件层中的目标落点：

| 六对象 | 目标软件层 | 当前实现状态 |
|---|---|---|
| `Candidate`（含 `candidate_type`、`level`、lineage，无 `context_id`） | Objects | **doc-level**；`core_objects.yaml` 仍为 8 个具名对象（第 4.5 节 crosswalk） |
| `Context` | Objects / Cross-cutting | **doc-level**；散见于 ClinicalHypothesis、gate envelope、CRC clinical context |
| `Gate` / `GateSet`（两层规则） | Capabilities（`src/capabilities/gates.py`） | **contract-only**；45-Gate 拓扑冻结，但未按 GateSet 两层规则拆分（第 16 节问题 19） |
| `EvidencePackage`（无固有 grade、引用而非复制） | Cross-cutting（Knowledge Ledger） | **doc-level**；当前 evidence 以外部引用组织，未强制「无固有 grade」属性 |
| `CandidateGateAssessment` | Capabilities | **contract-only**；`GateModelOutput` 输出 score/status/rationale，未拆 `Direction ⊥ Strength` |
| `Decision` | Lifecycle / Capabilities | **contract-only**；T12 decision + lifecycle 状态机存在，未按 GateSet `decision_rule` 组织 |
| `Instantiation`（配置层，非核心对象） | Repository implementation / Operating System | **doc-level**；无独立 machine contract（第 16 节 B 组问题 18） |

「doc-level」= 仅在本架构文档中定义；「contract-only」= 已有 `src/contracts/`
或 `src/capabilities/` 合同形状，但语义与 Blueprint v1.3 不完全一致。

### 4.3 Candidate Level 谱系与 canonical GateSet Registry

> **Normative source：** `StelligenOS_Candidate_Levels_and_GateSets_Blueprint.v0.1`。
> 本节把其 Candidate Level / GateSet / Gate ID 骨架提升为本仓库的顶层架构合同。
> 若本文档 registry 与该 GateSet 文档发生语义冲突，必须提交
> `DESIGN_CHANGE_REQUEST`，不得由 Module 自行选择解释。

一个概念只有在「正在被比较/选择」时才是 Candidate。上一级 Candidate 被选定后，
通常被冻结为下一级搜索的 Context / Constraint。因此 Candidate 生命周期不是一个
所有字段同时被优化的巨型矩阵，而是一系列**逐层收敛的搜索空间**。

| Level | Candidate Type | Canonical GateSet | 角色 |
|---|---|---|---|
| L0 | Indication | `INDICATION_GATESET` | 选择疾病开发空间 |
| L1 | Patient Territory / Clinical Context | `PATIENT_TERRITORY_GATESET` | 选择 indication 内具体患者空间 |
| L2 | Endpoint | `ENDPOINT_GATESET` | 选择希望改变且可开发的临床结果 |
| L3 | Modality | `MODALITY_GATESET` | 仅在 modality 尚未锁定时使用 |
| L4 | ADC Target | `ADC_TARGET_GATESET` | 选择 ADC 的 target address |
| L5 | ADC Epitope | `ADC_EPITOPE_GATESET` | 选择 target 上具体可利用 epitope |
| L6 | Antibody / Binder | `ANTIBODY_BINDER_GATESET` | 选择真实 delivery binder |
| L7 | Linker | `LINKER_GATESET` | 选择连接/释放体系 |
| L8 | Payload | `PAYLOAD_GATESET` | 选择效应载荷 |
| L9 | ADC Design | `ADC_DESIGN_GATESET` | 选择 antibody×linker×payload×DAR 完整设计 |
| L10 | ADC Hit | `ADC_HIT_GATESET` | 选择达到最低功能标准的实体 ADC |
| L11 | ADC Lead | `ADC_LEAD_GATESET` | 选择值得系统开发的 hit |
| L12 | Biomarker | `BIOMARKER_GATESET` | 选择 patient-selection / response biomarker |
| L13 | Development Candidate | `DEVELOPMENT_CANDIDATE_GATESET` | 选择进入正式 IND-enabling 的资产 |
| L14 | Clinical Regimen | `REGIMEN_GATESET` | 选择 dose/schedule/combination 策略 |

`Modality`、`Patient Territory`、`Endpoint` 一旦在某个 program 中已锁定，就从
Candidate 转为该 program 下游 Instantiation 的 Context/Constraint。

**canonical Gate 骨架（Gate ID → Candidate Level 归属）由 Blueprint v1.3 §H2.4
保持完整定义。** Module 不得改名、合并、拆分或重新归属，除非通过 GateSet
version revision。第一施工实例的 8 个 Gate（`ADC_TARGET_GATESET` 的
`TGT-01`–`TGT-08`）见第 6.4 与第 11 节。

### 4.4 Evidence Regime 词表（施工优先级元数据，**不是** Evidence Strength）

每个 Gate 被赋予一个 dominant 当前 evidence regime，用于**施工规划**：

| Code | 含义 | 当前优先级 |
|---|---|---|
| `PUBLIC_PRIMARY` | 当前即可主要依赖公开资料形成有价值 Assessment | 最高 |
| `PUBLIC_HYBRID` | 公开证据可强力 triage，最终 `DIRECT` 往往仍需实验 | 高 |
| `EXPERIMENT_PRIMARY` | Candidate-specific 结论主要依赖专有实验；公开资料多为 precedent/context | 延后施工 |
| `DEVELOPMENT_PRIMARY` | 依赖高级 preclinical / CMC / tox / clinical development 数据 | 更后 |

Evidence regime 只决定 Module 当前应优先施工到什么程度；
`DIRECT / INDIRECT_STRONG / WEAK / UNKNOWN` 仍完全由 Gate-specific Evidence
Ladder 决定（原则 14）。

### 4.5 LEGACY → TARGET ARCHITECTURE migration crosswalk

`v5-draft` 不修改 `core_objects.yaml`。下表是 `core_objects@1.1` 的 8 个 legacy
object type 到 Blueprint v1.3 目标 ontology 的**迁移映射**——**不是一一等价**。
多数 legacy 对象是 composite，迁移时要拆分到多个目标概念；具体 decomposition
在 migration implementation（§16 B 组、PR A）中完成。

| legacy object | 定位 | migration target（拆分） |
|---|---|---|
| `Opportunity` | legacy search/orchestration wrapper | `Instantiation` intent + `Context` seed + Candidate-generation request；**不属于任何 Candidate Level** |
| `ClinicalHypothesis` | legacy composite object（当前组合 target、anchor clinical context、intended benefit、biomarker hypothesis、product hypothesis） | clinical/patient/endpoint 维度 → `Context`；target identity → `Candidate` / candidate reference；biomarker hypothesis → Biomarker candidate/reference；product hypothesis → 下游 candidate/context reference；lock state → `Context` maturity（见 §4.6） |
| `TargetHypothesis` | 接近单一 Candidate | `Candidate`，`candidate_type = ADC Target`，`level = L4`。CRC Level 01 的 41 个 target 即此类 |
| `BinderCandidate` | 接近单一 Candidate | `Candidate`，`candidate_type = Antibody / Binder`，`level = L6` |
| `ADCConstruct` | legacy composite，跨 **L9 ADC Design / L10 ADC Hit** | 未来需 stage/type discriminator 或 distinct Candidate objects 区分「设计」与「已物理构建并达到 hit qualification」；不得让一个对象一半 design 一半 hit |
| `LeadSeries` | legacy series/container | 围绕 **L11 ADC Lead candidates** 的集合/容器；精确 decomposition pending migration，不强行等同单个 L11 Candidate |
| `DevelopmentCandidate` | 接近单一 Candidate | `Candidate`，`candidate_type = Development Candidate`，`level = L13` |
| `Asset` | 非 Candidate Level | L11–L13 经 `NOMINATE` / `COMMIT` `Decision` 后的对外商业/交易表述；不新增 Candidate Level |

**`core_objects@1.1` 尚缺的 Candidate Types（不是上表 8 对象的 crosswalk，而是
migration 时必须新增的类型）：**

| 缺失 Candidate Type | 目标 |
|---|---|
| `Biomarker` | `Candidate`，`candidate_type = Biomarker`，`level = L12`（支持性，不进主链） |
| `Endpoint` | `Candidate`（L2）→ 锁定后成为 `Context` 维度 |
| `Epitope` / `Linker` / `Payload` / `ADC Lead` / `Clinical Regimen` … | 见 §4.3 Candidate Level Registry（L5/L7/L8/L11/L14） |

**架构方向（§16 A 组，已由 Blueprint v1.3 决定）：** 8 个 legacy object type
折叠为泛化 `Candidate` + `candidate_type` + `level`，`core_objects.yaml` 从
「对象枚举」改为「Candidate Type Registry（受控词表）+ Candidate Level
Registry」。开放的只是 **migration 策略**（是否保留 legacy adapter、分几个
PR），不是「要不要做」。本 PR 不做代码改动。

### 4.6 ClinicalHypothesis 递进锁定（映射为 Context 成熟度）

锁定顺序不变：

```text
exploratory → provisional → anchored → product-locked → protocol-locked → regulatory-locked
```

在 Blueprint v1.3 视角下，`ClinicalHypothesis` 是一个**逐步收敛的 `Context`**：
L1 Patient Territory 与 L2 Endpoint 的 Candidate 选择结果被逐级冻结进该
Context。lock state 表示 Context 成熟度，不表示 Gate 已通过。正式路径需要
`clinical_hypothesis_ref`，旧精确 tuple 路径只能显式声明
`legacy_compatibility=True`。

三种入口保持不变：`mature-target-first`、`target-context-co-selection`
（默认）、`clinical-problem-first`。

---

## 5. Capability 与运行边界

内核登记 9 类 OS capability：Opportunity Discovery、Knowledge Mining、Rule
Learning、Evidence Extraction、ADC Design、Binder Engineering、Patent Analysis、
Due Diligence、Portfolio Management。

在 Blueprint v1.3 视角下，这些 capability 是**共享 infrastructure 能力**
（第 6.5 节）：它们提供检索、抽取、entity resolution、provenance ledger、
matrix rendering 等能力，但**不拥有 Gate-specific scientific decision
authority**。

当前代码进一步提供以下数据无关端口：Opportunity generation、Clinical-frame
pipeline、Target-candidate generation、Early T-Gate reduction、Endpoint-biology
completion、Evidence independence / adversarial review / readiness、T12 decision
and opportunity ranking、Binder/ADC route selection、End-to-end pilot and
closure、Architecture freeze/release、External runtime。

这些端口的含义是「外部实现必须遵守什么」，不是「仓库已经内置全部数据和科学
执行器」。`boot()` 只返回静态架构计划和外部引用，状态是
`ready_for_external_runtime`；它不会加载数据、运行模型或写结果。

---

## 6. Gate 系统（科学轴）

### 6.1 两层规则的显式分离（Blueprint v1.3）

| 层 | 字段 | 职责 | 产出 |
|---|---|---|---|
| **Gate** | `assessment_rule` | Evidence → Assessment：把落在本 Gate `evidence_required` 范围内的 Evidence Packages，在本 Gate 的 `evidence_ladder` + 对应 Context 下聚合 | 本 Gate 自己的 `Direction + Strength` |
| **GateSet** | `decision_rule` / `fatal_gate_policy` / `required_gate_policy` / `unknown_policy` | Assessments → Decision：把一个 Candidate 名下**多个** Gate 的 Assessment 组合成 Candidate-level `Decision` | `GO / KILL / NOMINATE / …` |

Gate 的 `fatal_conditions` 只声明「本 Gate 上什么样的结果构成**潜在**致命
信号」；是否据此淘汰 Candidate 由所属 GateSet 的 `fatal_gate_policy` 决定，
**不由 Gate 自己决定**。

**当前实现差距（第 16 节问题 19）：** `gate_system.yaml` 的 45-Gate 拓扑与
`src/capabilities/gates.py` 尚未按 Gate / GateSet 两层拆分；`GateModelOutput`
输出单一 `score` + `status`，未拆分 `Direction ⊥ Strength`。本 PR 不修改合同。

### 6.2 Evidence Ladder / Direction ⊥ Strength / ceiling

- **Direction**（正交于 Strength）：`POSITIVE / NEGATIVE / CONFLICTING /
  INCONCLUSIVE / NOT_APPLICABLE`。`UNKNOWN` 不是 Direction，而是「无合格证据」
  导致的 Assessment 状态。
- **Strength/Grade**（四级）：`DIRECT / INDIRECT_STRONG / WEAK / UNKNOWN`，
  按该 Gate 的 `evidence_ladder` 判定。**不允许任何通用数值分数。**
- **聚合铁律：** `evidence type ceiling > evidence quantity`（原则 15）。
- **Conflict 铁律：** positive 与 negative EP 并存且均达可信 Strength 时，
  `Direction = CONFLICTING`；`Strength = 冲突双方中最强的可信证据等级`，
  **不因冲突自动降级**。`key_supporting_evidence` 与
  `key_contradicting_evidence` 必须分别记录各自等级与来源。

Worked example（`ADC Addressability` Gate 的 `evidence_ladder`）见 Blueprint
v1.3 §I M03。

### 6.3 LEGACY_GATE_SYSTEM（冻结）→ semantic migration/reference → Canonical GateSet Registry

现有 45-Gate 拓扑是**迁移来源，不是未来架构**：

```text
LEGACY_GATE_SYSTEM
  gate_system@0.1.0
  topology@0.2.0
  45 gates（Target Opportunity 13 / Product Realization 16 / Commercial Executability 16）
  status = FROZEN_LEGACY
```

它原样保留用于 provenance / compatibility / migration reference，**不重写、
不原位转换、不重开 45 的冻结计数**。

Blueprint v1.3 的 **Candidate-Level canonical GateSets 是新的 canonical GateSet
lineage**，通过全新的 versioned GateSet contract 实现，拥有自己的 version
history。下表只是 legacy Gate 语义在新 registry 中的**归属参考**，供 migration
mapping 使用：

| legacy Gate chain | 数量 | 语义迁移到（新 canonical GateSet） |
|---|---:|---|
| Target Opportunity（T0–T12） | 13 | 临床上下文/人群 → `INDICATION_GATESET` / `PATIENT_TERRITORY_GATESET`；endpoint benefit → `ENDPOINT_GATESET`；target mapping / persistence / surface / internalization / TI → `ADC_TARGET_GATESET`（`TGT-01`–`TGT-08`）；epitope 可实现性 → `ADC_EPITOPE_GATESET` |
| Product Realization | 16 | `ADC_EPITOPE_GATESET` / `ANTIBODY_BINDER_GATESET` / `LINKER_GATESET` / `PAYLOAD_GATESET` / `ADC_DESIGN_GATESET` / `ADC_HIT_GATESET` |
| Commercial Executability | 16 | 早期 IP whitespace 分散在各层 Gate；formal FTO / 监管 / 交易 → `DEVELOPMENT_CANDIDATE_GATESET` + sponsor 轴（第 7 节） |

开放的实现问题（§16 B 组问题 19）不是「要不要重开 45」，而是「如何在**不修改
frozen legacy topology** 的前提下，建立新的 canonical GateSet contract、migration
mapping 与 compatibility strategy」。

**版本一致性问题仍未解决（`v3-draft` 起已登记，本版复核确认依旧存在）：**
`gate_system.yaml` 把 source envelope 写为 `GateInputEnvelope@2.0.0` /
`GateModelOutput@2.0.0`，而 `src/capabilities/gates.py` 当前默认合同版本是
`2.1.0`。现有测试通过，但两处声明不一致，需在独立治理任务中统一。

### 6.4 一 Gate 一主 Evidence Production Module（施工责任制）

> **一个 Gate 默认只有一个 primary Evidence Production Module 作为「包工头」。**

该 primary Module 对本 Gate 的施工交付负责，内部可自由调用多个数据库 /
provider / 算法 / submodule / 缓存 / QC，并选择实现语言与软件结构。它最终必须
交付：

```text
Gate-specific admissible raw evidence
  → atomic Evidence Packages
  → proposed CandidateGateAssessment
  → machine acceptance record
  → human-review surface
```

**Module 权责边界（严格禁止）：** Module 不得修改 Gate ID / Name / Candidate
ownership；不得扩大或缩小 Gate question；不得修改 Evidence Ladder / evidence
ceiling / fatal / unknown / conflict semantics；不得用另一个 Gate 的 evidence
替代本 Gate 的 measurement requirement；不得跨 Gate 产生新的综合 scientific
conclusion；不得修改 GateSet 的 Candidate-level decision policy；不得因公共数据
方便获取而降低验收标准；不得因当前无法测量而把 `UNKNOWN` 自动改成
PASS/HOLD/KILL。

**当前第一施工实例（固定）：**

```text
candidate_type = ADC Target
context        = refractory mCRC
modality       = ADC
gateset        = CRC-ADC-TARGET-GATESET-v1
evidence regime = public evidence only
```

首批 primary Modules 对应 `TGT-01`–`TGT-08`：ADC Modality Precedent /
Indication-Specific Malignant-Cell Coverage / Treatment / Metastatic
Persistence / Tumor Surface Availability / Normal-Tissue Fatal Liability /
Internalization / Trafficking Addressability / Shedding / Soluble-Antigen /
Sink Liability / Target Opportunity / Competition / IP Whitespace。

这 8 个 Gate 的科学定义属于 canonical GateSet 文档；`v5-draft` 只确认其存在、
边界、归属与施工方式。后续应逐 Gate 绘制 Evidence Production Module 施工图
（Gate Module Acceptance Template 17 项见 Blueprint v1.3 §H2.8），审核通过后
Module 才可开工。

### 6.5 共享 Infrastructure 规则

以下可作为共享基础设施被多个 Gate Module 调用：literature / trial / patent
retrieval provider；public dataset download adapters；entity resolution；
provenance ledger；common QC；ontology / identifier mapping；generic
evidence-package serialization；matrix rendering；audit/versioning utilities。

共享基础设施只提供**能力**，不拥有 Gate-specific scientific decision
authority。

### 6.6 Gate 输入输出语义（不变）

Gate 通过外部 envelope 接收 candidate、Context、证据、上游结果、graph context
和 run context。输出包括 score、confidence、status、rationale、evidence、
missing information 和 validation recommendation。约束：`score=None` 是未知
不是 0；Gate output 不自动写入仓库；Historical Rule 不能自动更改 score /
status / Profile；T12 结果不自动创建 Asset，也不自动切换生命周期；Gate 仍需要
外部运行时和显式审核。

---

## 7. Sponsor-relative 决策轴（Phase 1–4）

第 6 节的 45 个 Gate（科学轴）回答「这个机会科学上成不成立」；本节的四个合同
回答一个**独立且不可互相替代**的问题：「当前这个发起方要不要投、投到哪个风险
转移边界为止」。在 Blueprint v1.3 的 Candidate–Gate 模型中，**sponsor 轴映射到
零个 canonical Gate**——它不是某个 GateSet 的成员 Gate，而是 GateSet `Decision`
之外的独立治理层（第 16 节 A 组 A3）。

对小微 Biotech，这两个问题最容易被混为一谈——把「我们做不了」写成「这个靶点
不行」。因此四个合同的枚举都刻意避免使用 KILL/FAIL 词汇。

### 7.1 四个合同

| 阶段 | 合同 | 位置 | 语义 |
|---|---|---|---|
| 1 | `DevelopmentSponsorProfile@0.1.0`、`ProgramThesis@0.1.0` | `src/contracts/sponsor_strategy.{py,yaml}` | 描述发起方能力/资本/时间边界；把 Opportunity、Context、产品位置和目标转移里程碑绑成可审计主张 |
| 2 | `SearchSpaceAdmission@0.1.0` | `src/contracts/search_space_admission.{py,yaml}` | 正式证据抽取之前的 sponsor-relative 路由 |
| 3 | `ProgramCommitmentReview@0.1.0` | `src/contracts/program_commitment_review.{py,yaml}` | T12 之后、route selection 之前的承诺检查点 |
| 4 | `ValueInflectionPlan@0.1.0` | `src/contracts/value_inflection_plan.{py,yaml}` | 横跨生命周期的价值拐点计划 |

**Phase 2 的四种路由：**`ACTIVE_SEARCH`、`WATCHLIST`、`PARTNER_ONLY`、
`OUT_OF_MANDATE`。八个低成本条件各自只能取 `SATISFIED` / `UNKNOWN` /
`UNSATISFIED`，`UNKNOWN` 保留为未知。`HER2`、`TROP2` 等成熟靶点不得因为热门被
全局删除，只能在当前 sponsor 上下文里被路由为 `PARTNER_ONLY` 或
`OUT_OF_MANDATE`——这与 Blueprint v1.3「同一 Candidate 可在多个 Context 复用」
一致（Candidate 不被删除，只是当前 Instantiation 不推进）。

**Phase 3 的六个结果：**`SELF_DEVELOP`、`CO_DEVELOP`、`DATA_PACKAGE_ONLY`、
`PARTNER_NOW`、`MONITOR`、`STOP_FOR_SPONSOR`。其中 `MONITOR`、
`DATA_PACKAGE_ONLY`、`STOP_FOR_SPONSOR` 保持 `BLOCKED_NO_COMMITMENT`；
`SELF_DEVELOP`、`CO_DEVELOP`、`PARTNER_NOW` 只产生
`EXTERNAL_HANDOFF_REQUIRED`。

**Phase 4** 要求最小证据包、最低成功标准和停止条件三者都不得留空。

### 7.2 与 Binder/ADC route 的绑定（PR #72）

Phase 3–4 的两条硬控制原本只存在于文档。PR #72 把它们接到真正的入口：
`BinderAdcRouteRequest` 升到 `0.2.0`，新增三个无默认值的必填字段
`program_commitment_review_ref` / `value_inflection_plan_ref` /
`asset_generation_authorization_ref`。第三个字段承接 Phase 3 已冻结的
`EXTERNAL_HANDOFF_REQUIRED`，让放行判断留在外部 human-governance layer
（`field_presence_is_not_a_decision: true`）。

八个引用字段共用一套校验：必须是字符串、必须以 `external:` 开头、前缀之后
必须非空。

### 7.3 这条轴当前的实现边界

**仓库不读取、不反序列化、不重新裁定、不生成 authorization。**
`src/capabilities/binder_adc_routes.py` 的 import 集合恰为
`{dataclasses, typing}`，有测试用 AST 解析源文件断言这一点。

**Phase 1 与 Phase 2 目前仍没有消费者**（第 16 节问题 14）。**这条轴不新增
Gate**——45 个 Gate 拓扑未变，没有第 46 个 Gate，也没有 canonical GateSet
成员变化。

---

## 8. GenModule 与目录模块（未来的 Evidence Production Module machinery）

当前有 7 个模块区域，其中 6 个具有 `module.yaml`；`gen_indication_endpoint_target`
是当前被登记为 active 的纯合同包，但尚无模块 manifest。在 Blueprint v1.3 视角
下，这些模块是**降级为后台的证据生产机器**（M09），不是产品层一等对象。

> **重要边界（对应 §6.4「一 Gate 一主 Module」与 §16 B 组问题 22）：**
> 现有 GenModule 大多是 **legacy composite engine**，一个模块同时覆盖多个 Gate
> （最明显是 `target_safety_therapeutic_window_prescreen` 同时覆盖 `TGT-04` /
> `TGT-05` / `TGT-07`）。**这些 legacy composite module 不是未来 canonical Gate
> 的 primary Evidence Production Module。** 迁移后它们的定位是：
> **shared evidence provider / shared analysis engine / legacy composite
> library**，可被多个 Gate Module 调用，但不拥有任何 Gate 的 scientific
> decision ownership。未来每个 Gate 仍必须有自己独立的 primary Module，其
> EvidencePackage 输出、CandidateGateAssessment proposal 与验收严格对应该
> 一个 Gate。下文各模块的「目标映射」按此原则读作「其能力将被哪些 Gate 的
> primary Module 复用」，不是「它将成为这些 Gate 的 primary Module」。

### 8.1 `gen_indication_endpoint_target@0.1.0`

用途：定义受约束的 ADC clinical context、endpoint class 和 target opportunity
生成合同。包含 ClinicalFrame、TargetCandidate、EvidenceRecord、
AdversarialReview、TargetOpportunityHandoff 和 ClinicalHypothesis 相关结构，
但不包含 generator、evidence collector、ranking engine、Gate evaluator、runner
或数据库。目标映射：L0–L2（Indication / Patient Territory / Endpoint）与 L4
（ADC Target）的 Candidate 生成 + Context 冻结。

### 8.2 `assetgenos_catalog@0.1.0`

状态：`migrated_contracts_only`。从 AssetGenOS 迁入 7 个共享合同、45 个 Gate
定义、59 个 Model 定义、53 个 Profile 定义。它是软件目录，不是 Gate runtime。

### 8.3 `gate_model_rule@0.1.0`

用途：保存历史 Rule 的身份、引用和审计合同，不执行自然语言规则。Rule 不能
自动改分、改状态或绑定 Profile。它是迁移可追溯性，不是第二套 Gate 系统。

### 8.4 `target_safety_therapeutic_window_prescreen@0.4.0`

用途：用已标准化的公共证据 claim 做 ADC target-level 安全预筛。六个 evidence
axis：正常组织表达、表面可达性、抗原密度、soluble antigen / shedding / sink、
既有 modality 毒性、组织后果与可恢复性。逻辑 fatal-first：
`KILL` / `HOLD` / `CONDITIONAL_GO` / `GO`。

**legacy composite engine**：当前一个模块同时覆盖 `ADC_TARGET_GATESET` 的
`TGT-04`（Tumor Surface Availability）、`TGT-05`（Normal-Tissue Fatal
Liability）、`TGT-07`（Shedding / Sink）三个 Gate。迁移后它降级为
**shared target-safety analysis engine**；`TGT-04` / `TGT-05` / `TGT-07` 各自
有独立 primary Module，可共同调用本 engine，但**一个包工头不得同时验收三个
不同房间**——每个 Gate 的 EvidencePackage、Assessment proposal 与验收独立。
注意：这里的 `KILL` 是**科学轴**的致命风险判定，与第 7 节
`OUT_OF_MANDATE` / `STOP_FOR_SPONSOR` 完全不同，两者不得互相替代或互相推导。

### 8.5 `antibody_binder_asset_engineering@0.4.0`

用途：把已有 binder 工程化成 ADC carrier/asset package。16 个内部步骤映射到
冻结的 14-stage 外部路线。核心是两条不可互相补偿的轴（Track A 序列/结构/
developability；Track B 结合/内吞/运输/payload delivery 的版本化实验
phenotype），只通过 Pareto dominance 选择。目标映射：`ANTIBODY_BINDER_GATESET`
（L6）+ `ADC_DESIGN_GATESET`（L9）。

### 8.6 `epitope_conditioned_de_novo_antibody_discovery@0.1.0`

用途：从 antigen 和人为定义的 epitope 约束出发，形成 de novo antibody
discovery package。15 步覆盖 target biology 到 asset report。工具不可用时只能
输出约束和实验计划，不能虚构真实抗体序列、结合或 ADC readiness。目标映射：
`ADC_EPITOPE_GATESET`（L5）+ `ANTIBODY_BINDER_GATESET`（L6）。

### 8.7 `biotech_asset_due_diligence@0.1.0`

用途：对外部资产 artifact 建立可审计、modality-neutral 的尽调链。
`SystemRecommendation` 与 `HumanDecision` 严格分离。模块不能声称法律 FTO、
临床安全、临床有效、portfolio 排名或最终资本配置。目标映射：跨 L10–L14 的
stage-aware DD + `DEVELOPMENT_CANDIDATE_GATESET`。

---

## 9. Cross-cutting 逻辑

- **Knowledge Ledger**：以外部引用组织 evidence、rule、hypothesis、experiment、
  failure、decision、calibration 和 lesson。在 Blueprint v1.3 视角下，它是
  **累积的、可引用复用的 EvidencePackage 库**的当前形态——同一 EvidencePackage
  被多个 Assessment 通过 `evidence_package_ids` 引用而不复制（第 16 节 A 组 A4）。
- **Model lifecycle**：使用 `model_id@SemVer`；注册、权重、验证、晋级和退役由
  外部治理系统承担。
- **IP/FTO**：返回外部 decision package，不在仓库保存法律结论。
- **Stage-aware DD**：同一资产在不同生命周期阶段使用不同问题和证据标准。
- **Portfolio**：只定义端口，不保存估值、资本分配或组合决策。
- **Audit/versioning**：每次运行记录 input、contract、model/Gate、evidence、
  review 和时间戳。

---

## 10. Biotech 与患者数据基础设施

仓库已登记可复用的外部 provider 方向，但尚未接通完整 provider runtime：
文献（Europe PMC、PMC OA/BioC）、临床试验（ClinicalTrials.gov API、AACT）、
Target-disease（Open Targets）、单细胞（CELLxGENE Census）、正常组织（GTEx、
Human Protein Atlas）、癌症组学（GDC/TCGA、cBioPortal、DepMap）、蛋白结构
（UniProt、PDB、AlphaFold DB、InterPro）、化学（ChEMBL、PubChem、BindingDB）、
专利（EPO OPS、PATENTSCOPE、Lens）、监管（FDA、EMA 和公司披露）。

Cancer Patient-Anchored Data Infrastructure 采用四层证据空间：

```text
P1 Direct Patient Observation
  → P2 Patient-Derived Living Models
  → P3 Model Perturbation
  → P4 Clinical Intervention and Outcome
```

数据库名不能决定证据强度，患者距离和因果强度必须分开记录——这与 Blueprint
v1.3「EvidencePackage 必须声明 measurement class，不得跨 measurement boundary
使用」一致。当前这部分是基础设施目录和未来 provider 设计，不是已下载数据。

---

## 11. 第一次 Instantiation：refractory mCRC × ADC Target（CRC ADC Pool Level 01）

`v5-draft` 把 CRC ADC Pool Level 01 / CRC-Atlas 重新表述为本仓库的**第一次
Instantiation**：

```text
instantiation  = CRC-ADC-Pool-Level-01
candidate_type = ADC Target        (L4)
context        = refractory mCRC
modality       = ADC
gateset        = CRC-ADC-TARGET-GATESET-v1   (派生自 canonical ADC_TARGET_GATESET，保持 TGT-01–TGT-08 骨架)
evidence regime = public evidence only
```

**下列事实按 `v4-draft` 原样保留，本版不改：**

### 11.1 已进入 `main` 的正式内容

- Level 01 定义与三把 eligibility lock 已冻结。
- 输入绑定固定为 9 个 clinical contexts、41 个 targets、369 个原始 pair。
- `EVGAP-01` surface-localization extraction contract 已合并。
- `EVGAP-02` CRC linkage extraction contract 已修订为 `0.2.0` 并合并（PR #62）。
- `SRCADM-01` surfaceome source admission audit 已合并并获批（PR #63）；
  准入绑定已完成（PR #66）。
- Level 01 Preview revision 2 已合并，状态
  `PROVISIONAL_NOT_AUTHORIZED_FOR_ADVANCEMENT`。

Preview 当前结果：

| 指标 | 当前值 |
|---|---:|
| raw clinical contexts | 9 |
| raw targets | 41 |
| raw matrix | 369 pairs |
| eligible context | 1 |
| provisional surface-eligible targets | 22 |
| provisional eligible universe | 22 pairs |
| active for Level 02 | 0 |
| excluded candidates | 0 |

`active=0` 不表示没有候选，而表示没有 pair 同时通过三把锁。HOLD 是缺证据，
不是负面结论（对应 Blueprint v1.3 `UNKNOWN` 一等状态）。当前不得生成
`ADC_POOL_LEVEL_01_ACCEPTED`。

### 11.2 三把 eligibility lock 到 canonical Gate 的证据贡献映射（第 16 节 B 组问题 21）

映射按 **evidence ceiling** 表述——每把锁**贡献证据给**某个 Gate，**不等于
"满足" 该 Gate**：

| Level 01 lock | 目标 | evidence ceiling 约束 |
|---|---|---|
| eligible clinical context lock | **upstream L1 `Context` freeze**（不是 Target Gate） | — |
| surface-localization lock（`EVGAP-01`） | **contributes evidence to `TGT-04`** Tumor Surface Availability / Density Plausibility | 只提供 surface-localization evidence；**不能单独 discharge `TGT-04` 的 antigen density requirement**（surface localization ≠ 定量抗原密度，典型 evidence ceiling） |
| CRC linkage lock（`EVGAP-02`） | **primarily contributes to `TGT-02`** Indication-Specific Malignant-Cell Coverage | generic CRC linkage **不自动支持 `TGT-03`** Treatment / Metastatic Persistence；`TGT-03` 需要**独立的** treatment/metastasis-context evidence（来自 refractory / treated / paired pre-post / metastatic / CRLM / resistance context），`EVGAP-02` 的 EvidencePackage 只有在其 source/context 明确 qualify 时才可贡献 |

> 这条修正正是 StelligenOS 要制度化阻止的推理谬误：**"有 CRC evidence" ⇏
> "因此 refractory persistence 也有 evidence"**。

此映射为目标状态，需科学审核确认后才写入 `CRC-ADC-TARGET-GATESET-v1` 的
Context-specific Evidence Ladder。`v5-draft` 不改三把锁的当前定义。

### 11.3 已知 CRC 阻断（不变）

1. **`EVGAP-01`：已授权，未执行。** PR #66 已完成绑定：`SRCADM-01` 为
   `approved`，`EVGAP-01` 的 `extraction_blocked_by` 为空，`admission_status`
   为 `admitted_with_conditions`，授权**一次**抽取
   （`authorises_extraction_run_count: 1`）；`execution_status` 为
   `authorised_not_yet_executed`。
2. **`EVGAP-02`：只有 retrieval，没有 assertion。** `execution_status` 为
   `retrieval_layer_executed_assertion_layer_not_executed`，`gap_discharged`
   为 `false`。
3. **`GAP-P07`：41-target 轴含四个待裁定实体。** `Undisclosed`、`EDBN`、`AG7`
   三个无法消歧；`CA19-9` 已解析为 `resolved_as_non_protein_antigen`，但它是否
   属于「膜蛋白 target universe」必须由人裁定。
4. Accepted Level 01 pool 尚未形成，不能进入 Level 02、T-Gate scoring 或资产
   生成。
5. 尚无被批准的 CRC pair 进入 binder/ADC generation。

两个缺口都解除后，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。

---

## 12. Extensions：已登记但未进入内核

扩展只能依赖内核，内核不能依赖扩展；扩展不能改 Gate 或生命周期状态。

| ID | 扩展 | 状态 | 当前含义 |
|---|---|---|---|
| EXT-01 | ground-truth learning loop | `shell_only` | 等真实项目结局后再治理 |
| EXT-02 | dynamic gate context | `partially_absorbed` | v5 已吸收核心概念，剩余范围未治理 |
| EXT-03 | asset search engine | `shell_only` | 仅登记搜索能力方向 |
| EXT-04 | stop rule | `active_design` | 有合同和测试，尚未接真实运行 |

`EXT-04` stop rule 与 Phase 4 `ValueInflectionPlan` 的 `stop_condition_refs`
在概念上相邻，但目前是两套互不相通的工件（第 16 节问题 15）。登记不等于批准。

---

## 13. 系统实际运行逻辑

在 Blueprint v1.3 的 Candidate 生命周期视角下，同一个抽象循环在每个 Candidate
Level 重复，每一级就是一次新的 Instantiation：

```text
Human strategy + external evidence providers
  → BootRequest（只验证外部引用）
  → DevelopmentSponsorProfile / ProgramThesis（sponsor 边界，Phase 1）
  → 锁定 Context（indication / patient territory / endpoint / modality）
  → 定义 Candidate Type + Candidate Set（当前：ADC Target，L4）
  → 加载 / 绑定 Instantiation（gateset_id + gateset_version）
  → Search-Space Admission（sponsor-relative 路由，Phase 2；不删除候选）
  → 采集 / 生成 Evidence Packages（一 Gate 一主 Module；引用而非复制）
  → 构建 Candidate–Gate Assessments（Gate 层 assessment_rule → Direction + Strength）
  → Candidate–Gate Matrix + drill-down
  → Decision（GateSet 层 decision_rule / fatal_gate_policy / required_gate_policy）
       ├─ KILL        → 淘汰 Candidate（保留触发 Gate/Assessment/EP/人工批准链路）
       ├─ HOLD        → 保留待定（UNKNOWN / CONFLICTING 一等状态）
       ├─ MORE_EVIDENCE（公开可解） → 补充公开证据 → 回到 Evidence Packages
       ├─ MORE_EVIDENCE（需实验）   → Public-to-Experimental Handoff（分类：
       │                              PUBLIC_RESOLVABLE / EXPERIMENT_REQUIRED /
       │                              CURRENTLY_UNRESOLVABLE）
       └─ NOMINATE / COMMIT → Program Commitment Review（Phase 3）
                              → ValueInflectionPlan（Phase 4）
                              → external human authorization
                              → explicit human handoff
                              → route selection（BinderAdcRouteRequest@0.2.0：
                                 三个引用缺一不可）
                              → 晋升到下一 Candidate Level（下一次 Instantiation）
```

其中 `Program Commitment Review → ValueInflectionPlan → external human
authorization → route selection` 这一段是目前**唯一在代码层强制**的
sponsor-relative 控制；Phase 1 与 Phase 2 两处仍只是流程约定。

每个箭头传递版本化对象或外部 artifact reference。任何单个模块只能完成自己的
合同职责，不能因为「运行成功」就跳过证据、Gate、审核或人类决定。

CRC-Atlas 目前只对应链条最左侧的 "ADC Target"（L4）一级；后续 Epitope（L5）、
Binder（L6）、ADC Design（L9）、ADC Hit（L10）、ADC Lead（L11）各自绑定独立的
canonical GateSet，复用同一套六对象模型与同一条 EvidencePackage 资产库。

---

## 14. 现在能运行什么，不能运行什么

### 可以运行或验证

- data-free OS boot 和架构 smoke test。
- 8 类对象、4 阶段生命周期、ClinicalHypothesis lock、45 Gate 拓扑和 envelope
  校验。
- 各 capability 的输入输出合同与外部引用边界。
- Phase 1–4 四个 sponsor-relative 合同的形状校验。
- `BinderAdcRouteRequest@0.2.0` 的三项 sponsor 前置引用强制校验。
- Existing-binder pipeline 的大部分软件逻辑和受控外部工具调用。
- De novo route 的流程骨架与外部 package 生成。
- Target-safety `0.4.0` 的纯内存、确定性预筛。
- CRC Level 01 / EVGAP 合同、Preview 和机器可读验证。
- 当前 `main` 的 555 项单元测试和 repository boundary check。

### 不能声称已经完成

- **Blueprint v1.3 六对象模型尚未落到代码。** `core_objects.yaml` 仍是 8 个
  具名对象；Gate/GateSet 两层规则、`Direction ⊥ Strength`、EvidencePackage
  「无固有 grade」、`Instantiation` machine contract 都还只是文档层。
- 没有一个仓库内数据库或统一 data lake。
- 公共 provider 目录不等于 provider 已全部接通。
- `gen_indication_endpoint_target` 不会自行生成 pair。
- AssetGenOS 目录不执行 45 个 Gate。
- Model YAML 不等于模型已经加载、校准或运行。
- Level 01 Preview 不等于 Accepted pool。
- Retrieval hit 不等于 evidence assertion。
- Target safety GO 不等于产品 therapeutic window。
- 三个 sponsor 引用齐全不等于已获批准——仓库只校验引用存在。
- Phase 1 / Phase 2 合同存在不等于已被强制执行。
- Binder/de novo package 不等于实验验证或 development candidate。
- `SystemRecommendation` 不等于 `HumanDecision`。

---

## 15. 当前实现成熟度

| 范围 | 成熟度 | 说明 |
|---|---|---|
| 架构内核（6 软件层） | 已实现并测试 | 对象、生命周期、端口、边界和 boot 可运行 |
| **Blueprint v1.3 六对象决策模型** | **doc-level** | 本 `v5-draft` 定义为目标决策层契约；未落 `core_objects.yaml` / `gate_system.yaml` |
| **Candidate Level Registry（L0–L14）** | **doc-level** | 本版固定；无 machine contract |
| **Canonical GateSet Registry + Gate ownership** | **doc-level** | 骨架由 Blueprint v0.1 保持；45-Gate 拓扑未按 GateSet 拆分 |
| **Instantiation 绑定层** | **doc-level** | CRC Level 01 表述为第一次 Instantiation；无独立 contract |
| Gate/Model/Profile 目录 | 合同已迁移 | 45/59/53；真实运行在外部 |
| ClinicalHypothesis v5（映射为 Context 成熟度） | 已进入内核 | 递进锁定和三入口已实现 |
| Opportunity generation | 合同完整度较高 | 真实 generator/provider 尚在外部 |
| Sponsor 轴 Phase 3–4 | 已接入并强制 | route request 缺任一引用即无法构造 |
| Sponsor 轴 Phase 1–2 | 仅合同形状 | 无消费者，未强制 |
| Existing-binder route | 可运行软件逻辑较多 | 依赖外部输入和科学工具 |
| De novo route | 流程骨架可运行 | 真实序列设计和验证依赖外部工具/实验 |
| Target safety pre-screen | 确定性引擎已实现 | 依赖外部标准化 evidence claims |
| Due diligence | 合同和实体链已实现 | 不产生最终人类决策 |
| Biotech/patient infrastructure | 已登记 | 尚未形成完整 provider adapter 层 |
| CRC Level 01（第一次 Instantiation） | Preview 已形成 | Accepted pool 尚未形成 |
| 端到端真实资产生成 | 未完成 | 尚无批准 pair 贯通全部 Gate 与生成路线 |

---

## 16. 当前需要专家审核的问题

问题 1–17 承接 `v4-draft`（3、4 复核确认仍成立，其余未变）。`v5-draft` 依据
Blueprint v1.3 深度对齐后新增的内容分为 **A 组（架构方向已由 Blueprint v1.3
决定，登记为 Architecture Decision Record，不再作为「专家决定 yes/no」）** 与
**B 组（真正待实现设计的 blocker）**。架构文档的价值在于**不断减少开放问题
数量**，不是把已决定的事重新变成问题。

1. `ClinicalHypothesis` 的三种入口和递进 lock 是否足以覆盖真实 ADC 开发路径。
2. T0-T12 的顺序、Hard Gate、fatal-first、HOLD 和 T12 handoff 是否合理。
3. Gate envelope `2.0.0` / `2.1.0` 版本漂移应如何统一（复核确认仍存在）。
4. `gen_indication_endpoint_target` 是否应补正式 `module.yaml`，还是继续作为
   内核共享合同包。
5. 患者直接观测、患者来源模型、模型扰动和临床干预的 P1-P4 分层是否足够。
6. Evidence independence 应按 primary source、dataset lineage 还是实验批次
   定义。
7. Retrieval → assertion → disposition 三层是否足以阻止检索命中被误当成证据。
8. CRC target 轴中非标准实体应在何处消歧，是否需要重开 41/369 冻结计数。
9. `EVGAP-01` / `EVGAP-02` 解除后，Level 01 Accepted 的最低人工审核门槛是
   什么。
10. Existing-binder 双轴 Pareto 和 de novo 15-stage 路线是否符合实际实验决策。
11. 哪些判断必须专家签字，哪些可由模型辅助，哪些才允许确定性自动化。
12. 何时应把 stop rule、evidence independence 和 resource-aware planning 纳入
    内核。
13. `src/contracts/` 现在同时承载 YAML 身份声明与 Python 形状校验器；
    sponsor-relative 合同是否应在六层模型中单列一层，还是并入 Capabilities。
14. Phase 1 与 Phase 2 仍无消费者。是否应像 Phase 3–4 一样接到某个入口？
15. `EXT-04` stop rule 与 `ValueInflectionPlan.stop_condition_refs` 是否应
    合并。
16. `authorises_extraction_run_count` 没有消费机制（审核方已登记为非阻断项）。
17. 三处 YAML 引号缺陷仍在（`docs/pools/adc_pool_level_01_input_binding.yaml:498`、
    `docs/pools/evgap_01_surface_localization_extraction.yaml:551`、
    `docs/pools/evgap_02_crc_linkage_extraction.yaml:1104`）——` #<数字>` 之后
    内容被 YAML 当注释丢弃。建议另开极小 PR 统一加引号。
### A 组 — RESOLVED BY BLUEPRINT v1.3（Architecture Decision Record）

以下方向已定，**不再作为开放问题**；每条后面括注的才是尚未定的 migration 细节。

- **A1 泛化 `Candidate` 是目标 core model。** 8 个 legacy object type 折叠为
  `Candidate` + `candidate_type` + `level`，`core_objects.yaml` → Candidate Type
  Registry + Candidate Level Registry。（开放：migration 策略、是否保留 legacy
  adapter、分几个 PR —— 见 B 组。）
- **A2 Candidate-Level canonical GateSets 是目标 GateSet 架构。** 旧 45-Gate
  三组拓扑不是未来架构。（开放：legacy → 新 GateSet 的 migration mapping 与
  versioning —— 见 B 组。）
- **A3 sponsor 轴（第 7 节）不属于 canonical scientific GateSet。** 它是 GateSet
  `Decision` 之外的独立 governance layer，映射到零个 canonical Gate。
- **A4 Knowledge Ledger ≠ EvidencePackage Library。** Knowledge Ledger 范围更大，
  包含 rules / hypotheses / experiments / failures / decisions / lessons；
  `EvidencePackage` 是 Ledger 中的一个**强类型子域 / 视图**：
  `Knowledge Ledger ⊃ { EvidencePackage namespace, hypotheses, experiments,
  failures, decisions, lessons }`。
- **A5 施工顺序：先 Target 层（`TGT-01`–`TGT-08`）跑通，再进入 Epitope。**
- **A6 BVG 与 human/ChatGPT `APPROVE` 不是二选一。** `BVG = architecture
  validation criteria`；`ChatGPT / human APPROVE = governance approval
  mechanism`。放行 = **BVG pass + human approval**，两者同时适用。

### B 组 — IMPLEMENTATION / MIGRATION BLOCKERS（真正待设计）

18. **`Instantiation` machine contract。** 最小字段
    `{candidate_type, context_id, modality, gateset_id, gateset_version}`；
    如何在有 machine contract 的同时保证它不被静默升格为第七个核心对象
    （Blueprint v1.3 §N 明确禁止）？
19. **legacy 45-Gate → 新 canonical GateSet 的 migration / compatibility
    strategy。** 前提：**不修改 frozen legacy topology、不重开 45 的冻结计数**。
    如何建立新的 versioned canonical GateSet contract、legacy → 新的语义
    mapping、以及迁移期兼容层？`GateModelOutput` 的单一 `score` 如何演进为
    `Direction ⊥ Strength`（在新 GateSet contract 中，不在 legacy 中）？
20. **`EvidencePackage` 无 universal Strength grade + `CandidateGateAssessment`
    schema。** 如何在当前 Knowledge Ledger / gate evidence 结构中强制
    「Strength 只存在于 Assessment 层」？现有实现是否已在某处给 evidence 赋了
    跨 Gate 通用等级？
21. **CRC legacy lock → canonical Gate 的 evidence 贡献映射（第 11.2 节）。**
    `EVGAP-01 → contributes to TGT-04`（不 discharge density）、
    `EVGAP-02 → primarily TGT-02`（`TGT-03` 需独立 treatment/metastasis-context
    evidence）—— 需科学审核确认后才写入 `CRC-ADC-TARGET-GATESET-v1` 的
    Context-specific Evidence Ladder。
22. **legacy GenModule 的重新分类。** 逐个把现有 7 个 GenModule 判为
    `primary Gate Module` 还是 `shared provider / shared analysis engine /
    legacy composite library`（§8 已给出 `target_safety` 的判定；其余待定）。
23. **runtime migration PR 排序（本条不再完全开放，推荐顺序如下）：**

```text
PR A  — Core decision objects
        Candidate / Context / EvidencePackage / CandidateGateAssessment /
        Instantiation config + legacy core-object adapters
        （不删 legacy 8-object support）

PR B  — Canonical GateSet contracts
        Gate / GateSet / Evidence Ladder / Direction×Strength /
        assessment_rule / decision policy
        （旧 45-Gate 保持 FROZEN_LEGACY）

PR C  — Matrix / provenance / reusable EP references
        （evidence_package_ids 引用机制）

PR D  — CRC-ADC-TARGET-GATESET-v1
        冻结 TGT-01…TGT-08 的 context-specific contract 与 Evidence Ladder

PR E+ — 逐 Gate primary Evidence Production Module
        TGT-01 primary Module / TGT-02 primary Module / … / TGT-08 primary Module
```

    legacy 8 objects 与 legacy 45 Gate 在 migration 完成前保留 compatibility，
    不在任何单个 PR 中一次性删除。

---

## 17. 版本维护规则

1. 规范路径保持不变，下一次实质更新升为 `v6-draft`。
2. 每个版本必须记录 repository baseline、日期和审核状态。
3. 只有获得明确批准的版本才复制到 `docs/architecture/versions/` 形成只读
   快照。批准本 PR 的改动 ≠ 批准把 `v5` 文档版本冻结为快照——后者需要审核方
   明确说「批准 v5 文档版本」。
4. 未批准 draft 被新 draft 取代时不补造「已批准快照」。`v2-draft`、
   `v3-draft`、`v4-draft` 都未获批，因此都没有快照。
5. 架构文档必须分别标记 `implemented`、`contract-only`、`doc-level`、
   `external runtime`、`planned` 和 `pending review`，不得用一个「已完成」
   概括所有层。
6. 架构更新不得顺带改变 Gate、合同或科学决策；发现不一致只登记为审核问题，
   另立治理任务修复。Blueprint v1.3 六对象模型的代码落地属独立实现任务，
   受本 PR 获批与否 gate。
