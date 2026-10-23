# TGT-05 / TGT-07 v2 Phase B 实施总纲

状态：**PROPOSED；本 PR 仅冻结 Phase B 范围，未批准任何运行代码或外部数据运行。**

## 1. 来源与目标

- 基线：`main` merge commit `735f8c519a691faf10fb752f2ccf30328b1a5e02`，即人类于 2026-10-23 指示合并的 [PR #143](https://github.com/leezx/StelligenOS/pull/143)。该 PR 的 exact HEAD `705b85ce21735eae24537c8f5d2fa04b953889c8` 已获 ChatGPT Phase A `APPROVE`；批准**仅限契约**。
- 规范来源：`docs/architecture/TGT05_DECISION_MODEL_V1_MIGRATION_RFC.zh-CN.md`、`docs/architecture/TGT07_NEGATIVE_DIRECT_V2_AMENDMENT.zh-CN.md`、`src/contracts/crc_adc_target_gateset_v2.yaml`、`src/contracts/gate_modules/tgt05_normal_tissue_adc_toxicity_v2.yaml` 和四个经 SHA256 锁定的 GateSet v2 policy bodies。
- 用户方向：形成可审计的 ADC 靶点正常组织风险判断，再评估 ADCdb 全靶点；现阶段先使 v2 Gate/Module/Decision 权责链真实可执行，同时保持数据全部在仓库外。

Phase B 的可交付结果是**代码与合成测试能力**：对规范化、可追溯的输入形成 Gate-neutral EvidencePackages、非 canonical 评估建议和人审记录，完成八 Gate 经人工批准后到 Candidate Decision 的受控转换。Phase B 不声称拥有任何真实靶点数据，也不从 Open Targets safety 线索直接判 ADC 正常细胞杀伤。

## 2. 基线缺口

| 项目 | 目前状态 | Phase B 约束 |
|---|---|---|
| `MOD-TGT05@1.0.0` | 冻结的正常组织 liability 模块，原输入/规则不含 v2 E1/E2/E3 和限定阴性 | 保留原模块及测试；新版本单独实现，不原地改 v1 |
| `TGT-05@2.0` | Gate ladder、17 项施工合同和 reviewer record schema 已批准；Module binding 为 `0.0.0` | 实现新 Module，不能把 machine proposal 写成 `HUMAN_APPROVED` 或 Candidate Decision |
| `MOD-TGT07@1.0.0` | 已有复杂的 soluble-antigen/TMDD 完整性、归因、聚合和 fatal review 机制 | 保留旧版本；v2 必须明确绑定 `TGT-07@2.0` 并遵守新 Gate ladder，不静默复用 v1 Module 身份 |
| `TGT-07@2.0` | 新 Gate 科学定义批准，Module binding 为 `0.0.0`；没有独立 v2 模块施工合同 | 先冻结 v2 Module 输入、证据资格、完成度和拒绝边界，再实现代码 |
| GateSet v2 policy / registry | 四个 declarative body 已批准且 registry 标 `APPROVED` | resolver 必须锁定 ref、路径、版本、源 commit、SHA256 和审批状态；失败拒绝、不得回退 v1 |
| 审计关联 | reviewer record 与 Decision 的外部 audit schema 含 `x-resolution-contract` | 实现真实跨文件 resolver；标准 JSON Schema 本身不执行该自定义规则 |
| CRC v2 Instantiation | `HOLD`，TGT-05/07 v2 Module slot 为 `0.0.0` | 只有所有依赖的代码 PR 获批、人工批准路径可用、激活单独获审后才允许解除 HOLD |

## 3. 实施顺序与 PR 单位

后续每一步为**独立 PR 审核单位**；前一步没有明确 `APPROVE` 与人类放行，不进入依赖步骤。每个 PR 均有 `docs/handoff/` 与 `logs/worklog.md`；真实数据运行另需运行 PR 和仓库外 DATA 路径。

1. **B0（本 PR）：范围和接口冻结。** 冻结本实施顺序、TGT-07 v2 施工合同与 resolver 的拒绝条件；不修改 v1、v2 Gate 科学 body、policy body、registry hash 或 Instantiation。B0 通过后才实施 B1。
2. **B1：`MOD-TGT05@2.0.0`。** 以纯 Python、注入式 port 接受外部规范化观察和来源索引，输出 Gate-neutral EP、机器 proposal、覆盖/冲突/失败审计、非 canonical reviewer record 草案。E1 临床归因或正常细胞功能、E2 细胞型表面蛋白、E3 RNA 定位及 Open Targets supporting 必须分域；仅合格的候选抗体阴性结合或覆盖充分的膜蛋白阴性加完整临床 sweep 可以提出限定 `NEGATIVE`。严格测试临床 AE 归因待定、RNA/IHC 仅有、未测关键细胞、same-event conflict、跨事件非 conflict、严重 DIRECT 不因别处缺口降级、身份/来源/EP 复用漂移整轮拒绝。不得输出 canonical Assessment/Decision。
3. **B2：`MOD-TGT07@2.0.0`。** 以新 Module 身份对接 `TGT-07@2.0`。可复用 v1 经验证的算法结构，但须在新版本代码和测试中明确其不变量；只有完成审计且合格的 intended-ADC TMDD 无 material sink 才能提出 `NEGATIVE/DIRECT`。不同暴露场景 material sink 阳性不能被阴性抵消，同场景矛盾须保留双侧 EP；缺 PK、未定量 shedding、低于检测限、未完成搜索均不得阴性。v1 模块保持原行为和可执行性。
4. **B3：policy/audit resolver 与 Decision evaluator。** 从同一版本化 Instantiation 的八 Gate `HUMAN_APPROVED` assessment 和 pinned EP 形成候选 Decision；依照已批准四个 policy body 的行顺序、fatal/required/unknown 规则、`triggered_by` 和 `NOT_EVALUATED` 字面值，不引入新阈值。策略 registry 任一 ref、路径、owner、版本、hash、审批状态或源 commit 错配均拒绝，无 v1 fallback。审计 resolver 实际读取 reviewer record、assessment、Decision，核对 ID、SHA256、target/program/context、candidate/Instantiation、TGT-05 snapshot pin、推荐/最终值，差异原因必填；失败只拒绝 audit acceptance，不改科学政策结果。人类审核者仍独立创建和批准 Assessment/Decision，不能由 Module 或 resolver 冒签。
5. **B4：激活审阅。** 在 B1–B3 均明确批准且集成验证后，以单独 PR 将两个 v2 Module binding 从 `0.0.0` 精确提升为 `2.0.0`，审查 Instantiation 是否可从 `HOLD` 改变。必须由人类负责人与 ChatGPT 对该激活 PR 单独放行；未获批准前保持 HOLD。此步骤不运行真实 ADCdb 数据。

## 4. 跨 PR 验收与停止条件

- **版本/对象：** v1 Gate/GateSet/Module 字节与显式调用回归保持不变；一个 Decision snapshot 精确匹配 v2 八成员，不混用 `TGT-05@1.0` 或 `TGT-07@1.0`。
- **来源：** EP 保持 Gate-neutral 且可追溯；无来源、目标身份冲突、来源完整性错误、重复/漂移 EP 或缺必需完成审计均拒绝整轮，不能写普通 HOLD。
- **安全推断：** Open Targets 四类、RNA 与普通 IHC 只承担 supporting/定位或弱证据；无事件、无表达记录、无报告不等于安全。Module 不能产出 Candidate GO/KILL。
- **人工权责：** 仅人工批准的 Assessment 可以进入 GateSet；`Tgt05DecisionRecord.recommendation` 不参与 policy 输入。Reviewer 建议与 Candidate Decision 差异在外部 audit trace 可见。
- **合成回归：** 必测八 Gate 全合格 GO、任一重大未解风险阻止 GO、缺必要 Gate/MORE_EVIDENCE、TGT-05 临床 sweep 不完整时不得阴性、未归因 AE 不自动 KILL、合格 program/context-specific fatal route、TGT-07 同/异场景冲突、registry 失配拒绝、非法/不存在审计引用拒绝。
- **仓库边界：** 仓库仅存代码、合同、小型合成测试与 manifest；任何 Open Targets/ADCdb/HPA 下载、原始数据、中间表、真实评估或报告必须在仓库外 DATA 工作区，并由独立运行 PR 放行。`webReport_Stelligen` 的 Open Targets 四流提取器已有本地待审代码，但该仓库缺 Git remote；不能借 StelligenOS PR 绕过其 Charter。

## 5. 本 PR 审核问题

请审核 B0 是否足以冻结 Phase B 的顺序与边界，尤其是 TGT-07 v2 施工合同应包含的证据资格与失败条件、B3 是否需要进一步拆分、B4 激活所需的人审证据。若 B1–B4 范围或顺序需改变，先在本 PR 修订并重新审核，不在后续代码 PR 中悄然扩大。
