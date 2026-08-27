# Handoff：架构说明文档 v5 — 依据 Blueprint v1.3 深度对齐

## 任务信息

- 任务编号：`task_20260827_architecture-v5-blueprint-alignment`
- 分支：`task_20260827_architecture-v5-blueprint-alignment`
- 基线：`origin/main` @ `a8afcd4`（PR #88 merge）
- PR：待创建
- Commit：待提交
- 时间：`2026-08-27 14:55 EDT`
- 交付物类型：**纯文档深度对齐 + 审核基线升版**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（不改代码、契约、测试、Gate、Model、
  Profile 或科学决策）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、为什么现在做

用户提供两份外部 Blueprint 作为核心输入：

- `StelligenOS-产品形态-Blueprint v1.3`（六对象决策模型 + Instantiation +
  Candidate Level / GateSet 施工骨架冻结）
- `StelligenOS_Candidate_Levels_and_GateSets_Blueprint.v0.1`（L0–L14 Candidate
  Levels 与每级 canonical GateSet、Gate ID 归属）

用户指令：以其为核心对仓库架构做**一轮深度修改**（非重做），提交 PR 审核，
并在网页版 ChatGPT `Biotech ideas` 项目下的 `AI 审核方案` 对话提交审核。
用户明确「忽略轻量级，直接深度修改架构」；范围边界经确认为**文档层深改**。

现有审核基线 `STELLIGENOS-ARCH-2026.08.06-v4-draft` 完全没有 Blueprint v1.3 的
六对象决策模型、Candidate Levels 或 canonical GateSet registry，且基线落后 21
个 commit（测试数 `413` → `555`）。

## 二、改了什么

### 1. `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`

`v4-draft` → `v5-draft`。基线 `main@4d895d7` → `main@a8afcd4`，测试数
`413` → `555`。

顶层章节编号**保持 `v4-draft` 稳定**（§7 sponsor 轴、§16 审核问题等引用位置
不变），深度改写发生在节内：

| 节 | v5-draft 改动 |
|---|---|
| §0 | 新增 0.1 主要变化清单（9 条）、0.2「本版不修改」清单、0.3 章节编号说明 |
| §1 | 一句话定义重写为「版本化、context-aware 的 Candidate × Gate 决策矩阵」 |
| §2 | **重写**：核心命题、六个冻结对象表、Instantiation 配置层（非第七对象）、CRC-Atlas 重定义为 evidence engine |
| §3 | 设计原则 11 条 → 16 条（新增 12–16：Candidate/Context 解耦、Direction⊥Strength 含 CONFLICTING、Gate 专属 Evidence Ladder、ceiling>quantity、两层规则不共用字段） |
| §4 | 新增 4.2 六对象软件层落点表、4.3 Candidate Levels L0–L14 + canonical GateSet registry、4.4 evidence regime 词表、4.5 与 `core_objects@1.1` 8 对象 crosswalk、4.6 ClinicalHypothesis 映射为 Context 成熟度 |
| §5 | Capability 重述为共享 infrastructure 能力 |
| §6 | **重写**：6.1 Gate/GateSet 两层规则分离表、6.2 Direction⊥Strength/ceiling/conflict 铁律、6.3 45-Gate 拓扑 → canonical GateSets 目标映射、6.4 一 Gate 一主 Module 施工责任制 + `TGT-01`–`TGT-08`、6.5 共享 infrastructure 规则、6.6 IO 语义（不变） |
| §7 | sponsor 轴补一句「映射到零个 canonical Gate，是 GateSet Decision 之外的独立治理层」 |
| §8 | 7 个 GenModule 各补「目标映射到哪个 canonical GateSet / Level」 |
| §9 | Knowledge Ledger 补「= 可引用复用的 EvidencePackage 库当前形态」 |
| §11 | **重写**：CRC Level 01 重述为第一次 Instantiation；11.2 三把 eligibility lock → `TGT-02/03/04` + L1 目标映射；11.1/11.3 的 41/369 计数、Preview 数字、`EVGAP-01`/`EVGAP-02`/`GAP-P07` 阻断状态**原样保留** |
| §13 | 运行流程按 Candidate 生命周期 + Instantiation 重写；保留 `Program Commitment Review → ValueInflectionPlan → external human authorization → route selection` 是唯一代码层强制段 |
| §14/§15 | 更新「能/不能运行」与成熟度表；新增 doc-level 行（六对象模型、Candidate Level Registry、canonical GateSet Registry、Instantiation） |
| §16 | 审核问题 17 条 → 27 条。新增 18–27：8 对象是否折叠为泛化 Candidate、45-Gate → canonical GateSet 映射、Instantiation 是否需 machine contract、EvidencePackage 无固有 grade 如何强制、CRC 三锁映射、sponsor 轴位置、Knowledge Ledger 与 EP 库、GenModule 迁移顺序、`core_objects.yaml`/`gate_system.yaml`/`src/` 更新排序、BVG-01/02/03 是否适用本仓库 |
| §17 | 下一版升 `v6-draft`；补 `doc-level` 标记类别 |

**逐项复核的数字（未盲抄）：**

| 项 | `v4-draft` | `v5-draft` | 复核方式 |
|---|---|---|---|
| 仓库基线 | `main@4d895d7` | `main@a8afcd4` | `git log origin/main` |
| 单元测试数 | 413 | 555 | `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'` → `Ran 555 tests OK` |
| Gate 数 / 拓扑 | 45 / `0.2.0` | 45 / `0.2.0`（未改） | `src/contracts/gate_system.yaml` |
| 核心对象 | 8 / `1.1` | 8 / `1.1`（未改） | `src/contracts/core_objects.yaml` |
| Gate envelope 漂移 | `2.0.0` vs `2.1.0` | 同（复核确认仍在） | `gate_system.yaml` vs `src/capabilities/gates.py` |
| CRC 41 targets / 369 pairs | 41 / 369 | 41 / 369（原样保留） | §11 未改事实 |

### 2. `docs/architecture/contract.zh-CN.md`

- §3 层结构后增加一段：分层是软件结构，决策层模型（六对象 + Instantiation）
  见 3.4.1，是所有阶段与所有 Candidate 类型共用骨架。
- §3.4 Objects 重构为四个子节：
  - **3.4.1 决策层模型（Blueprint v1.3，规范）** —— 六个冻结对象 + Instantiation
    非第七对象 + 正交性/ceiling/一等状态铁律。
  - **3.4.2 Candidate Level Registry（L0–L14，规范）** —— 级别清单 + 规范来源
    指向外部 Blueprint 与 `v5-draft` 文档。
  - **3.4.3 当前对象登记（`core_objects@1.1`，待 crosswalk 实现）** —— 8 个
    具名对象到 Candidate Type × Level 的映射；明确「是否折叠为泛化 Candidate」
    是待审核的开放实现问题。
  - **3.4.4 ClinicalHypothesis 递进锁定** —— 原 §3.4 正文，未改内容。
- §6 Source of Truth 增加 `v5-draft` 文档与外部 Blueprint 两条规范来源指针，
  并把 `core_objects.yaml` 标注为「当前实现登记，待 crosswalk」。

### 3. `architecture.md` / `README.md` / `docs/architecture/versions/README.md`

审核基线字符串 `STELLIGENOS-ARCH-2026.08.06-v4-draft` →
`STELLIGENOS-ARCH-2026.08.27-v5-draft`。`versions/README.md` 记录
`v2/v3/v4-draft` 均未获批、无快照，`v5-draft` 未获批前不复制进 `versions/`。

### 4. `logs/worklog.md`

追加一条 `2026-08-27T14:55 EDT` 记录。

## 三、本 PR 不做什么

- 不修改任何 `src/` 代码、`genmodules/`、`extensions/`、测试。
- 不修改 `src/contracts/core_objects.yaml`（仍 8 对象 `1.1`）与
  `src/contracts/gate_system.yaml`（仍 45 Gate 拓扑 `0.2.0`）。
- 不把 8 个具名对象折叠为泛化 `Candidate`；不重排/重编号 45-Gate 拓扑；
  不新增 `Instantiation` machine contract —— 这些是问题 18–27 的实现任务，
  受本 PR 获批与否 gate。
- 不解除 `EVGAP-01`/`EVGAP-02`，不执行任何抽取或外部运行。
- 不修复 §16 登记的任何缺陷（envelope 漂移、YAML 引号、
  `authorises_extraction_run_count` 无消费机制、Phase 1/2 无消费者）。
- 不把 `v5-draft` 复制进 `docs/architecture/versions/`。
- 不触碰仓库中既有的用户自有 untracked 文件（`AI_RESULT_ACCEPTANCE.md`、
  `STELLIGEN_CONSTRAINTS.md`、`docs/worklogs/`、`pipelines/`、
  `CRC Patient Territory Map.png`）。

## 四、验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 555 tests — OK

命令：bash tests/test_git_sync.sh
结果：git_sync behavior tests passed (A-D).

命令：git diff --check
结果：clean（无空白错误）

命令：bash scripts/verify_repository_boundary.sh
结果：仅报告 4 项 pre-existing 用户自有 untracked（`pipelines/`、
      `STELLIGEN_CONSTRAINTS.md`、`CRC Patient Territory Map.png`、
      `AI_RESULT_ACCEPTANCE.md`）；均非本任务产生，未修改、未暂存。
      与 `logs/worklog.md` 中 2026-08-21 PR #88 条目记录的状态一致。

命令：git status --short
结果：本 PR 显式暂存 6 个既有/新增文档文件：README.md、architecture.md、
      docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md、
      docs/architecture/contract.zh-CN.md、docs/architecture/versions/README.md、
      logs/worklog.md，以及新增 docs/handoff/2026-08-27-architecture-v5-blueprint-alignment.zh-CN.md。
      用户自有 untracked 文件未暂存。
```

无数据、cache、result、database、model weights 或实例进入仓库。

## 五、未决问题与风险

- `v5-draft` 把 Blueprint v1.3 六对象模型定为**目标决策层契约**，但
  `core_objects.yaml` / `gate_system.yaml` / `src/` 尚未对齐。文档与实现之间
  存在有意的、已登记的落差（§16 问题 18–27）。审核方需确认：这一「文档先行、
  实现分批」的排序是否可接受，还是要求文档与至少 `core_objects.yaml` 同步。
- 45-Gate 拓扑 → canonical GateSets 的重新归属是一次 GateSet version revision，
  需要独立科学审核（问题 19）。
- CRC Level 01 三把 eligibility lock 到 `TGT-02/03/04` + L1 的映射（§11.2）
  是提案，未经科学确认前不写入 `CRC-ADC-TARGET-GATESET-v1` 的 Evidence Ladder。

## 六、下一步

1. 创建非 draft PR，在网页版 ChatGPT `Biotech ideas` → `AI 审核方案` 对话
   粘贴完整 `v5-draft` 正文提交审核。
2. ChatGPT 明确 `APPROVE` 前不推进：不开始问题 18–27 的任何代码落地，不执行
   依赖本变更的外部运行。
3. 若 `REQUEST_CHANGES`：在同一 PR 按反馈做最小必要修订，重新验证并更新
   worklog / handoff，再次提交同一对话复审。
4. 若 `APPROVE` 且审核方明确「批准 v5 文档版本」：按 `versions/README.md`
   规则 3 把 `v5` 复制进 `docs/architecture/versions/` 形成只读快照。
5. 获批后另立治理任务，逐项处理问题 18–27（建议先 `core_objects.yaml` →
   Candidate Type / Level Registry，再 `gate_system.yaml` GateSet 两层拆分，
   最后 `Instantiation` contract）。

## 七、数据边界声明

本仓库只保存架构系统文档、代码和小型治理文本；本任务没有新增任何数据、缓存
或结果文件。所有数据和处理仍位于外部工作区。本任务只改动 5 个既有文档 +
新增 1 个 handoff，均为治理文本。
