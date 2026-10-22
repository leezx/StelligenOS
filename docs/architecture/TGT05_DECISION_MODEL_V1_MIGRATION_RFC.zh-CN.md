# TGT-05 决策模型 v1.0：canonical 契约迁移提案

状态：**PROPOSED / PR #142 round 1 `REQUEST_CHANGES` 后修订中**。本文件是契约变更的第一阶段交付，不改变现行 `TGT-05@1.0`、`MOD-TGT05@1.0.0` 或 `ADC_TARGET_GATESET@1.0` 的运行语义。科学来源是 `PR/webReport_Stelligen/gates/M0/TGT-05-Normal-Tissue ADC Toxicity/design-v1.0.md` 中「TGT-05 决策模型 v1.0」；2026-10-22 用户要求同步修改 StelligenOS canonical 契约。跨仓库设计尚无 Git remote，因此将该设计章节**逐字快照**保存为同一 PR 中的 `docs/architecture/TGT05_DECISION_MODEL_V1_SOURCE_SNAPSHOT.md`，SHA256 `2e41525f65c6f7e4e9ec909bd8f110623f6ce62f54d5c82448c37aa80224674c`；原文件完整 SHA256 为 `e4e5198a0021256fdb1cee3f516cd1e941d8c72c3c3fcb90b7c5e3dd9c4a2603`（2026-10-22 15:40 EDT 本地读取）。本 PR 的 Git commit 固定快照内容；后续来源文件变化不自动修改本 RFC。实施 PR 必须 pin 本 PR merge commit、快照路径和 SHA256。

## 1. 目标和不可偷换的问题

新科学问题是：**若 ADC 杀伤表达 Target X 的正常人体细胞，细胞丢失是否会造成不可接受的器官毒性？** 审议顺序为 `Clinical Precedent → Normal-Cell Surface Expression → Cell-Loss Consequence → GO/HOLD/KILL`。M0 的 GO 只表示值得进入下一研发阶段，不是安全性或治疗窗证明。KILL 只适用于当前 ADC 开发场景，须保留证据和适用边界。

现行 canonical TGT-05 是单向 liability detector，按 `DIRECT / INDIRECT_STRONG / WEAK` 对**风险证据**分层；`EvidencePackage` 是 Gate-neutral 原子观察，Module 只给非 canonical assessment proposal 和 potential-fatal 提示。`CandidateGateAssessment` 经人工批准后才进入 GateSet；只有 GateSet 的决策层可以给 Candidate-level `Decision`。外部 `decision_rule` / `fatal_gate_policy` 目前只有引用，没有仓库内可执行策略体。因此新设计的逐靶点 GO/HOLD/KILL 不能直接写入 `EvidencePackage`，不能由现有 Module 冒充 canonical `Decision`，也不能把「未检出风险」升级为阴性安全证据。

## 2. 变更范围和版本冻结

这是**破坏性科学语义变更**，不可原地覆写已冻结的 `TGT-05@1.0`。新 lineage 固定为 `TGT-05@2.0`、`MOD-TGT05@2.0.0`、`ADC_TARGET_GATESET@2.0`；`gateset_id` 仍是 `ADC_TARGET_GATESET`，只递增 `gateset_version`。v2 成员精确为 `TGT-01/02/03/04/06/07/08 @1.0` 加 `TGT-05 @2.0`，不增加第九 Gate。CRC 专用 Instantiation ID 固定为 `INST-CRC-REFRACTORY-ADC-TARGET-v2`，其 `gateset_binding`/`gate_binding` 必须显式 pin v2 GateSet/TGT-05/Module，其余 Gate pin @1.0。v1 与 v2 同时保留**显式调用可执行性**和历史读取/审计能力；不得从 v1 绑定静默升级到 v2。一个 canonical Decision 的 assessment snapshot 必须完全匹配同一 Instantiation 的 v1 或 v2 GateSet 成员版本，不得混用。实施 PR 以新增版本化文件/绑定实现这些不变量，不能覆写 v1。

本阶段只锁定科学语义、对象归属、迁移路径、策略归属和验收标准；不改现行 YAML、运行代码、外部策略引用或数据。后续分为：A. **仅契约**，新增 v2 GateSet/Module construction contract、四个 policy bodies、registry manifest、schema/parity 测试，全部经 PR 审核冻结；B. Module v2 与人审界面实现；C. 仓库外真实数据接入和 250 靶点审议。A 未 `APPROVE` 和 merge 前不得写 B 的实现；B 未 `APPROVE` 和 merge 前不得做 C 的依赖外部运行。C 的原始及派生数据只放 `DATA`。

## 3. 新记录的归属

| 内容 | 应归属对象 | 约束 |
|---|---|---|
| 同靶点 ADC 不良事件、归因材料、抗体正常细胞结合、膜蛋白/RNA 观察 | `EvidencePackage` | 一条观察一包，原始来源与适用边界；不得含 GO/HOLD/KILL。 |
| E1 临床/功能、E2 膜蛋白、E3 RNA | TGT-05 v2 的**正交证据域 taxonomy** | 不是 `DIRECT / INDIRECT_STRONG / WEAK` 的同义词或替代品；避免称「E1 Direct」。同一域内仍按证据强度分层。 |
| 最高风险器官/细胞、可及性、细胞丢失后果、主不确定性、下一实验、翻转条件 | 新的 reviewer-facing `Tgt05DecisionRecord` | 引用 EP ID 和覆盖审计；记录是 Gate-specific 人工审议材料，不能替代 Gate-neutral EP。 |
| `GO/HOLD/KILL` 建议 | `Tgt05DecisionRecord.recommendation` | 非 canonical reviewer-facing 建议；不得作为 Gate assessment 字段或 GateSet policy 的直接输入。 |
| Candidate-level `GO/HOLD/KILL` | canonical `Decision` | 只能由 `ADC_TARGET_GATESET@2.0` 按完整 assessment snapshot 和经批准的策略生成；单一 TGT-05 建议不等于整体 Candidate 决策。 |

`Tgt05DecisionRecord` 是 **non-canonical Gate-specific reviewer artifact / review surface**，不是第七个 core object，也不是 `Decision`。它至少包含：canonical target/HGNC/ADCdb ID、context/版本、clinical liability (`CONFIRMED / SUSPECTED / NONE_DOCUMENTED / UNKNOWN`)、最高风险正常 organ 和 cell type、surface-antigen evidence (`DIRECT / INDIRECT / UNKNOWN`，仅此字段局部用词)、cell-loss consequence (`CRITICAL / POTENTIALLY_SERIOUS / LIMITED / UNKNOWN`)、E1/E2/E3 支撑 EP IDs、覆盖范围及检测能力、主不确定性、推荐、可改变结论的一个下一实验、翻转条件、审议者/时间/状态。`NONE_DOCUMENTED` 必须附已查来源、范围和日期；它不等于不存在或安全。未测量、检索失败及身份冲突须分开编码，后两者不能降格为普通 HOLD。

唯一允许的权责链为 `EvidencePackage → Tgt05DecisionRecord (non-canonical) → human-authored/HUMAN_APPROVED CandidateGateAssessment (Direction + Strength) → ADC_TARGET_GATESET@2.0 policy → canonical Decision`。Module 可提出 assessment proposal，但不能写 HUMAN_APPROVED、GO/HOLD/KILL 或 `Decision`。GateSet policy **只消费经批准且版本匹配的八个 Gate assessments**；不得直接读取 `Tgt05DecisionRecord.recommendation` 作为捷径。Reviewer recommendation 与最终 Candidate-level Decision 不一致时，必须在 policy trace 中可见，而不能静默覆盖。

## 4. 科学决策边界

### 4.1 正交证据域与 canonical v2 ladder

E1/E2/E3 是**证据来源与测量对象的分类**；canonical `Strength` 仍为 `DIRECT / INDIRECT_STRONG / WEAK`，`Direction` 仍为 `POSITIVE / NEGATIVE / CONFLICTING / INCONCLUSIVE`（另有 `UNKNOWN` 状态）。v2 Gate 问的是「正常人可接触抗原与细胞丢失是否构成重大 ADC 正常组织 liability」；Direction 描述相对该问题的证据，不描述靶点商业吸引力。以下规则是 v2 施工合同必须逐字实现的科学底线：

| 证据和前提 | v2 assessment authority | 不能推出 |
|---|---|---|
| E1 同靶点 ADC 临床严重正常组织事件，已审定 target-mediated 且器官/正常细胞归因、构型与暴露背景充分 | `POSITIVE / DIRECT`，记录该产品的严重度和适用场景 | 不自动成为 target-intrinsic fatal、Candidate `KILL`。 |
| E1 人相关正常细胞实验：验证特异性、表面可及性、ADC/适当抗体-payload 靶点依赖性杀伤、临床相关暴露和严重功能后果 | `POSITIVE / DIRECT`，限定模型与构型 | 不自动外推所有 ADC 构型。 |
| E1 只有特异性正常人体组织/细胞表面结合，没有功能杀伤 | `POSITIVE / INDIRECT_STRONG`，提示可接触 liability | 不证明不可接受后果。 |
| E1 同靶点 ADC 严重 AE，但 target attribution 未审定 | `INCONCLUSIVE / WEAK` 的 attribution-pending 风险提示；原始事件保留 EP | 不升为 DIRECT、KILL 或「无风险」。 |
| E2 经验证的正常人关键细胞**膜抗原**定位/表面蛋白组学，细胞归属与方法质控明确 | `POSITIVE / INDIRECT_STRONG` | 不证明 ADC 必定结合/杀伤或可及性绝对充分。 |
| E2 有全面、检测能力足够且可审计的关键正常细胞表面蛋白**未检出**，临床 sweep 亦完整且无已确认 liability | 经人工确认后可为 `NEGATIVE / INDIRECT_STRONG`，含 coverage/sensitivity/批次/阴性边界；仅指被测范围未支持重大 liability | 不证明靶点安全、治疗窗或所有正常细胞阴性；普通 atlas 空白不符合此行。 |
| E1 候选抗体的人正常组织结合实验在足够的器官/细胞、检测灵敏度与生理相关条件下阴性，且归因/临床 sweep 完整 | 经人工确认后可为 `NEGATIVE / DIRECT`，限定该抗体和实验覆盖 | 不外推其他抗体/构型，也不证明安全。 |
| E2 只有普通 total-protein IHC，未证实膜染色；或 E3 任一 RNA-only 来源 | 有表达假设时 `INCONCLUSIVE / WEAK`；无表达/未检出只记 COVERAGE_CONTEXT，不生成 `NEGATIVE` rung | 不产生 GO 或 KILL 的单独依据。 |
| 无合格 liability/阴性检测证据，关键正常细胞覆盖不完整 | `INCONCLUSIVE / UNKNOWN` | 不自动转换成 GO/HOLD/KILL。 |

同一 liability event 的合格正反 target-attribution 材料可为 `CONFLICTING`，须保留两侧 EP 和冲突点；不同组织「一个风险阳性、另一组织未检出」不是同一事件冲突。独立且未被反驳的 DIRECT liability 不因其他组织覆盖缺口降级，缺口进 `critical_unknowns`。E3 不能单独给 `POSITIVE / DIRECT`、`NEGATIVE` 或任何 GO/KILL 建议。Open Targets 等 supporting 只进入背景与待核查风险，不能占上述 ladder rung。每个结论须标示是否是 machine proposal、人工批准的 assessment 或 GateSet Decision。

v2 的 `GO` reviewer recommendation 至少需要本节有质控的 `NEGATIVE / INDIRECT_STRONG` 或更强的局部阴性权威，加上无未解决的重大 E1/E2 liability 和可在下一阶段解决的残余不确定性；不能仅因没有 positive EP 而 GO。`POSITIVE / INDIRECT_STRONG` 可导致 HOLD 审议；`POSITIVE / DIRECT` 也不自动 KILL，因为临床相关性、构型和损伤后果仍需人审。Candidate-level GO/HOLD/KILL 的最终转译只属于版本化 GateSet policy。

- **E1：** 同靶点 ADC 临床毒性只有在正常组织**靶点介导**的归因充分时才支持强 KILL 审议。必须保留项目、靶点身份、抗体/连接子/载荷/格式、剂量与患者背景、器官/细胞、严重度、机制归因、原始来源；不良事件本身不构成 target-level KILL。相关抗体或 ADC 的正常人体组织结合与靶点依赖性功能杀伤可以作 E1 实验支撑，但不得把结合单独等同于严重损伤。
- **E2：** 正常人**细胞类型特异的膜抗原**证据为高权重。普通 total-protein IHC、蛋白阳性或预测的膜定位均不足以确认循环 ADC 的可及性；IHC 可靠性、细胞归属、膜染色模式、抗体特异性与表面蛋白组学方法须分别记录。E2 阳性通常提示优先审议或 HOLD，不自动 KILL。
- **E3：** 正常组织 scRNA / spatial / bulk RNA 只用于定位待核查细胞。E3 单独不能给 GO 或 KILL，也不能在蛋白缺口时作为阴性安全证据。
- **Supporting：** Open Targets safety events、human genetics、小鼠表型、非 ADC 药理学和敲除表型保留来源与机制，不计为 ADC 细胞杀伤的 E1/E2/E3；不作为 GO/KILL 的单独依据。
- **Consequence：** 正常细胞按 critical functional、essential barrier、regenerative compartments、other 场景审议；器官名本身、单次表达阳性或笼统 essentiality 不决定 KILL。
- **GO：** 关键组织的蛋白检测覆盖、质控和限制可核查，无可信不可接受的 target-mediated liability，且剩余关键不确定性可在下一阶段以有限实验解决。GO 不能由数据库无记录或 RNA 阴性自动生成。
- **HOLD：** 关键细胞膜证据缺口、RNA/蛋白冲突、严重同靶点 ADC 事件归因未明或抗原可及性未知；必须给出能够翻转建议的具体实验或来源核查。
- **KILL：** 只允许**当前 program/context-specific** 的人工 KILL recommendation，不能从单一构型直接声明 target-intrinsic fatal。Clinical route 同时要求 same-target identity、严重或临床实质性的正常组织毒性、qualified target-mediated attribution、正常细胞/器官归因、暴露/剂量背景，以及 linker/payload/off-target/product-specific 替代解释的显式审议。Functional route 同时要求 human-relevant 正常细胞表面可及性、靶点依赖性结合/摄取和杀伤、临床相关暴露/开发场景、`CRITICAL` 或明确不可接受的 cell-loss consequence。任一 route 的 consequence、exposure relevance 或归因未解决时为 HOLD 审议，不得 KILL。任何自动规则只可触发 review；只有 GateSet policy 基于人工批准 assessments 才能给 canonical Candidate-level `KILL`。

## 5. 与旧契约的明确差异

| `@1.0` | 新设计需求 | 迁移处置 |
|---|---|---|
| 只检出风险证据，缺证据为 `INCONCLUSIVE/UNKNOWN` | 带检测覆盖依据的 M0 GO 审议 | 新版引入 coverage/negative-evidence 质控；不改写旧版 UNKNOWN。 |
| `DIRECT` 只限同靶点 ADC 临床归因 | E1 还含相关抗体/ADC 功能实验 | 新证据类型单列；不得声称旧 DIRECT 已覆盖。 |
| `INDIRECT_STRONG` 可由正常人组织蛋白支持 | E2 要求细胞类型、膜定位及可及性审议 | 总蛋白/IHC 简单阳性不得自动升格。 |
| 经典 liability fatal pattern 偏重跨构型收敛 | 新模型允许充分机制归因的单项目临床或强功能证据触发 KILL 审议 | 明确产品特异性、场景适用性和人工判断；不能自动宣布 target-wide fatal。 |
| Module 不输出 Candidate 决策 | 每靶点一页 GO/HOLD/KILL | 新 reviewer-facing 建议与 GateSet `Decision` 分离。 |
| 现有外部 `fatal_gate_policy@v1` | 四个 v2 policy bodies | 由 `ADC_TARGET_GATESET@2.0` 拥有并按下节版本化；不得只改引用字符串就宣称可执行。 |

## 6. GateSet v2 策略 registry 与决策权

用户于 2026-10-22 明确选择把 v2 policy bodies 放在 **StelligenOS Git 的版本化契约目录**，由 PR 审核。logical policy owner 是 `ADC_TARGET_GATESET@2.0`，不是 `MOD-TGT05` 或 `Tgt05DecisionRecord`。canonical **source registry** 定在 `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/`；运行时可从 Git release/commit 同步到仓库外工作区，但不得在仓库中创建运行实例、缓存或 decision engine。现行 `external:` ref 语法保持不变：它代表相对于 GateSet 核心对象的**独立策略实体引用**，不是「文件必须在另一个 Git 仓库」；v2 的 resolver 须通过 registry manifest 将 ref 精确映射到文件，不允许动态查找或 fallback 到 v1。

| GateSet v2 字段 | 固定 logical ref | 固定 registry body 路径 |
|---|---|---|
| `decision_rule_ref` | `external:gateset/ADC_TARGET_GATESET/decision_rule@v2` | `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/decision_rule.yaml` |
| `fatal_gate_policy_ref` | `external:gateset/ADC_TARGET_GATESET/fatal_gate_policy@v2` | `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/fatal_gate_policy.yaml` |
| `required_gate_policy_ref` | `external:gateset/ADC_TARGET_GATESET/required_gate_policy@v2` | `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/required_gate_policy.yaml` |
| `unknown_policy_ref` | `external:gateset/ADC_TARGET_GATESET/unknown_policy@v2` | `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/unknown_policy.yaml` |

**四个 policy 均为 v2**，不复用目前只有引用、无已知 body/hash 的 v1 策略。Phase A 须提交上述四个小型 YAML body 与同目录 `registry.yaml`：对每个 logical ref 记录 canonical relative path、policy version `v2`、SHA256、源 Git commit/release、GateSet ID/version、review PR 和 approval status。SHA256 在 body 定稿后写入 manifest；此 RFC 不伪造尚不存在文件的 hash。PR 审核基于 exact HEAD 验证 body、manifest 和引用；`APPROVE` 后修改内容必须升新的 policy version 和 GateSet version，不得重写已批准的 v2 body。策略审批权为 StelligenOS 固定 GPT/ChatGPT PR 审核 + 人类负责人的 merge/阶段放行，运行方无权临时改策略。

现行 `gateset_binding` schema 只有 `decision_rule_ref`、`fatal_gate_policy_ref`、`required_gate_policy_ref` 三个字段；v2 Instantiation 的这三项须**逐字等于**上表同名 GateSet v2 refs，不能创建另一个 instantiation-scoped policy body 或用 v1 的 `external:instantiation/...@v1`。`unknown_policy_ref` 只存在于 GateSet 核心对象并由同一 registry 解析，不擅自扩张 frozen binding schema。若将来需要 CRC 专用政策差异，须另开契约版本和 PR；本 v2 不含隐式 context overlay。

Phase A 的 policy body 至少锁定以下判定，不留给 Module 实现自由选择：

1. 只消费**同一 v2 Instantiation 下、版本匹配且 `HUMAN_APPROVED` 的 Gate assessments**及其 pinned EP refs；不直接消费 `Tgt05DecisionRecord.recommendation`。任何 `GO/HOLD/KILL` reviewer 建议都只是人审材料。
2. `TGT-05 POSITIVE/DIRECT` 只表示强 liability，**不能自动 KILL**。若人审记录支持本 RFC §4 的 clinical 或 functional route 且 `Decision.triggered_by` 指向该 `HUMAN_APPROVED` assessment、写明 program/context/归因与替代解释，GateSet 的 `fatal_gate_policy@v2` 才允许**人工批准** Candidate-level KILL。单项目不能被标为 target-intrinsic fatal；仅有 `POSITIVE/INDIRECT_STRONG`、AE 未归因、可及性/暴露/后果未解决时不得 KILL，按 required/unknown policy 留在 HOLD/MORE_EVIDENCE 审议。
3. `TGT-05 NEGATIVE` 仅代表明确定义检测覆盖内未支持重大 liability；不等于安全。GO 还需其余 Gate 的 required assessments 与政策条件，不能由 TGT-05 单独给出。`INCONCLUSIVE/UNKNOWN`、检索失败、身份或来源完整性错误须区分：前者进入 unknown policy，后两者拒绝产生 canonical Decision，不能默默变成 HOLD 或 GO。
4. `decision_rule@v2`、`fatal_gate_policy@v2`、`required_gate_policy@v2`、`unknown_policy@v2` 必须共同给出八 Gate assessment snapshot 到 Candidate Decision 的完整、可审计转换和 `triggered_by` 规则。Phase A 未完成这四个 body 与验证前，v2 GateSet **不得实例化或用于任何 Candidate 决策**；Phase B 不能自己补写政策。

## 7. 实施前必须通过的验收

1. 建立 v2 与 v1 的身份、binding、schema、旧记录读取/新记录拒混规则；旧回归测试保持通过。
2. 对同一 mock 靶点分别验证：只有 RNA、只有普通 IHC、同靶点 ADC 严重 AE 但归因不明、单个归因充分的 ADC 事件、膜蛋白关键细胞表达但可及性未知、覆盖充分且经质控的阴性检测。逐例检查推荐和不可得结论，不能用合成病例报告真实靶点结果。
3. 验证 EP 保持 Gate-neutral；缺来源/错 target/复用 EP 字段漂移整轮拒绝；记录引用可追溯到原始来源及检测范围。
4. 完成人审保留和四个 GateSet v2 策略实体/manifest/SHA256 的 exact-head 版本锁定；没有人工接受，任何自动建议不得成为 canonical Candidate `Decision`。验证 policy resolver 对 ref、版本、路径、内容 hash、approval 状态严格一致；不存在 body 或 hash 漂移须拒绝，而非退回 v1。
5. Open Targets 四类提取器仍是 supporting 输入；HPA RNA 不得充当膜蛋白；HPA 普通 IHC 不得充当表面可及性；ADCdb 项目表不得充当临床毒性归因表。
6. 从 source snapshot 原始字节重算 SHA256 为 `2e41525f65c6f7e4e9ec909bd8f110623f6ce62f54d5c82448c37aa80224674c`，检查其唯一标题和章节完整性；实施 PR pin 本 PR merge commit。webReport 将来有 remote 时，独立比对该设计章节的新旧差异，不静默改本 RFC。

## 8. 当前阻断与审阅问题

现行 v1 GateSet 只有 `external:` 策略引用，没有可用的 policy body；v2 已在本 RFC 中固定 source registry 的目录、四个 ref 和审阅权。真正的 v2 body、SHA256、resolver 与完整 Candidate 决策真值表属于 Phase A **契约 PR**，须先审定再允许 Module v2 实现。`Tgt05DecisionRecord` 的地位已固定为新增的非 canonical 人审材料，不增加 core object。

`webReport_Stelligen` 目前没有 Git remote；用户于 2026-10-22 授权将本决策模型章节提交到公开的 StelligenOS PR。该章节已作为上述逐字快照和 SHA256 纳入本 PR，PR 审核/merge 后成为本 RFC 可复现的规范来源；webReport 的其余设计与 WorkLog 仍保持本地、未获该仓库 PR 审核。StelligenOS 当前 PR 只供审核科学与迁移边界，**不授权真实数据下载、250 靶点建议生成或依赖的外部运行**。
