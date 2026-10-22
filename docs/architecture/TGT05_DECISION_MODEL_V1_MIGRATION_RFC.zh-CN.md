# TGT-05 决策模型 v1.0：canonical 契约迁移提案

状态：**PROPOSED / 未获 PR 审核**。本文件是契约变更的第一阶段交付，不改变现行 `TGT-05@1.0`、`MOD-TGT05@1.0.0` 或 `ADC_TARGET_GATESET@1.0` 的运行语义。科学来源是 `PR/webReport_Stelligen/gates/M0/TGT-05-Normal-Tissue ADC Toxicity/design-v1.0.md` 中「TGT-05 决策模型 v1.0」；2026-10-22 用户要求同步修改 StelligenOS canonical 契约。跨仓库设计尚未进入 GitHub PR，故本文件以来源路径和标题锁定版本，后续实施 PR 必须锁定其 Git commit。

## 1. 目标和不可偷换的问题

新科学问题是：**若 ADC 杀伤表达 Target X 的正常人体细胞，细胞丢失是否会造成不可接受的器官毒性？** 审议顺序为 `Clinical Precedent → Normal-Cell Surface Expression → Cell-Loss Consequence → GO/HOLD/KILL`。M0 的 GO 只表示值得进入下一研发阶段，不是安全性或治疗窗证明。KILL 只适用于当前 ADC 开发场景，须保留证据和适用边界。

现行 canonical TGT-05 是单向 liability detector，按 `DIRECT / INDIRECT_STRONG / WEAK` 对**风险证据**分层；`EvidencePackage` 是 Gate-neutral 原子观察，Module 只给非 canonical assessment proposal 和 potential-fatal 提示。`CandidateGateAssessment` 经人工批准后才进入 GateSet；只有 GateSet 的决策层可以给 Candidate-level `Decision`。外部 `decision_rule` / `fatal_gate_policy` 目前只有引用，没有仓库内可执行策略体。因此新设计的逐靶点 GO/HOLD/KILL 不能直接写入 `EvidencePackage`，不能由现有 Module 冒充 canonical `Decision`，也不能把「未检出风险」升级为阴性安全证据。

## 2. 变更范围和版本提案

这是**破坏性科学语义变更**，不可原地覆写已冻结的 `TGT-05@1.0`。建议经本 RFC 审核后，独立实施 PR 创建 `TGT-05@2.0`、`MOD-TGT05@2.0.0`、`ADC_TARGET_GATESET@2.0` 的新 lineage；其他七个 Gate 的证据契约保持各自 `1.0`。新 Instantiation 和 bindings 显式选择新版本。旧 `@1.0` 仍可审计和读取，但新旧 assessment 不得混入同一个 GateSet 决策快照。版本名只是本 RFC 的审阅提案；正式身份、兼容性迁移和引用解析须由实施 PR 的验证锁定。

本阶段只锁定科学语义、对象归属、迁移路径和验收标准；不改现行 YAML、运行代码、外部策略引用或数据。后续实施分为：A. canonical 契约和 schema / parity 测试；B. Module v2 与人审界面；C. 仓库外真实数据接入和 250 靶点审议。每阶段独立 PR 获得 `APPROVE` 后，才启动依赖阶段；C 的原始及派生数据只放 `DATA`。

## 3. 新记录的归属

| 内容 | 应归属对象 | 约束 |
|---|---|---|
| 同靶点 ADC 不良事件、归因材料、抗体正常细胞结合、膜蛋白/RNA 观察 | `EvidencePackage` | 一条观察一包，原始来源与适用边界；不得含 GO/HOLD/KILL。 |
| E1 Direct / E2 Protein / E3 RNA | TGT-05 v2 的**审议证据类别** | 不是现行 GateSet `DIRECT / INDIRECT_STRONG / WEAK` 的同义词；同一 E1 内临床与实验来源也需细分。 |
| 最高风险器官/细胞、可及性、细胞丢失后果、主不确定性、下一实验、翻转条件 | 新的 reviewer-facing `Tgt05DecisionRecord` | 引用 EP ID 和覆盖审计；记录是 Gate-specific 人工审议材料，不能替代 Gate-neutral EP。 |
| `GO/HOLD/KILL` 建议 | `Tgt05DecisionRecord.recommendation` | 明确标为非 canonical 建议；只能经人工审核进入 v2 Gate assessment / GateSet 决策策略。 |
| Candidate-level `GO/HOLD/KILL` | canonical `Decision` | 只能由 `ADC_TARGET_GATESET@2.0` 按完整 assessment snapshot 和经批准的策略生成；单一 TGT-05 建议不等于整体 Candidate 决策。 |

`Tgt05DecisionRecord` 至少应包含：canonical target/HGNC/ADCdb ID、context/版本、clinical liability (`CONFIRMED / SUSPECTED / NONE_DOCUMENTED / UNKNOWN`)、最高风险正常 organ 和 cell type、surface-antigen evidence (`DIRECT / INDIRECT / UNKNOWN`)、cell-loss consequence (`CRITICAL / POTENTIALLY_SERIOUS / LIMITED / UNKNOWN`)、E1/E2/E3 支撑 EP IDs、覆盖范围及检测能力、主不确定性、推荐、可改变结论的一个下一实验、翻转条件、审议者/时间/状态。`NONE_DOCUMENTED` 必须附已查来源、范围和日期；它不等于不存在或安全。未测量、检索失败及身份冲突须分开编码，后两者不能降格为普通 HOLD。

## 4. 科学决策边界

- **E1：** 同靶点 ADC 临床毒性只有在正常组织**靶点介导**的归因充分时才支持强 KILL 审议。必须保留项目、靶点身份、抗体/连接子/载荷/格式、剂量与患者背景、器官/细胞、严重度、机制归因、原始来源；不良事件本身不构成 target-level KILL。相关抗体或 ADC 的正常人体组织结合与靶点依赖性功能杀伤可以作 E1 实验支撑，但不得把结合单独等同于严重损伤。
- **E2：** 正常人**细胞类型特异的膜抗原**证据为高权重。普通 total-protein IHC、蛋白阳性或预测的膜定位均不足以确认循环 ADC 的可及性；IHC 可靠性、细胞归属、膜染色模式、抗体特异性与表面蛋白组学方法须分别记录。E2 阳性通常提示优先审议或 HOLD，不自动 KILL。
- **E3：** 正常组织 scRNA / spatial / bulk RNA 只用于定位待核查细胞。E3 单独不能给 GO 或 KILL，也不能在蛋白缺口时作为阴性安全证据。
- **Supporting：** Open Targets safety events、human genetics、小鼠表型、非 ADC 药理学和敲除表型保留来源与机制，不计为 ADC 细胞杀伤的 E1/E2/E3；不作为 GO/KILL 的单独依据。
- **Consequence：** 正常细胞按 critical functional、essential barrier、regenerative compartments、other 场景审议；器官名本身、单次表达阳性或笼统 essentiality 不决定 KILL。
- **GO：** 关键组织的蛋白检测覆盖、质控和限制可核查，无可信不可接受的 target-mediated liability，且剩余关键不确定性可在下一阶段以有限实验解决。GO 不能由数据库无记录或 RNA 阴性自动生成。
- **HOLD：** 关键细胞膜证据缺口、RNA/蛋白冲突、严重同靶点 ADC 事件归因未明或抗原可及性未知；必须给出能够翻转建议的具体实验或来源核查。
- **KILL：** 经人工确认的强同靶点 ADC 临床靶点介导严重正常组织毒性，或与当前开发场景相关的靶点依赖性正常细胞杀伤及不可接受后果。任何自动规则只可触发审议，不可独自 KILL。

## 5. 与旧契约的明确差异

| `@1.0` | 新设计需求 | 迁移处置 |
|---|---|---|
| 只检出风险证据，缺证据为 `INCONCLUSIVE/UNKNOWN` | 带检测覆盖依据的 M0 GO 审议 | 新版引入 coverage/negative-evidence 质控；不改写旧版 UNKNOWN。 |
| `DIRECT` 只限同靶点 ADC 临床归因 | E1 还含相关抗体/ADC 功能实验 | 新证据类型单列；不得声称旧 DIRECT 已覆盖。 |
| `INDIRECT_STRONG` 可由正常人组织蛋白支持 | E2 要求细胞类型、膜定位及可及性审议 | 总蛋白/IHC 简单阳性不得自动升格。 |
| 经典 liability fatal pattern 偏重跨构型收敛 | 新模型允许充分机制归因的单项目临床或强功能证据触发 KILL 审议 | 明确产品特异性、场景适用性和人工判断；不能自动宣布 target-wide fatal。 |
| Module 不输出 Candidate 决策 | 每靶点一页 GO/HOLD/KILL | 新 reviewer-facing 建议与 GateSet `Decision` 分离。 |
| 现有外部 `fatal_gate_policy@v1` | 需要新政策 | 不能只改本仓库引用字符串就宣称可执行；策略所有者和版本化实体必须在实施前确定。 |

## 6. 实施前必须通过的验收

1. 建立 v2 与 v1 的身份、binding、schema、旧记录读取/新记录拒混规则；旧回归测试保持通过。
2. 对同一 mock 靶点分别验证：只有 RNA、只有普通 IHC、同靶点 ADC 严重 AE 但归因不明、单个归因充分的 ADC 事件、膜蛋白关键细胞表达但可及性未知、覆盖充分且经质控的阴性检测。逐例检查推荐和不可得结论，不能用合成病例报告真实靶点结果。
3. 验证 EP 保持 Gate-neutral；缺来源/错 target/复用 EP 字段漂移整轮拒绝；记录引用可追溯到原始来源及检测范围。
4. 完成人审保留和 GateSet 策略版本锁定；没有人工接受，任何自动建议不得成为 canonical Candidate `Decision`。
5. Open Targets 四类提取器仍是 supporting 输入；HPA RNA 不得充当膜蛋白；HPA 普通 IHC 不得充当表面可及性；ADCdb 项目表不得充当临床毒性归因表。

## 7. 当前阻断与审阅问题

本仓库当前没有 `ADC_TARGET_GATESET` 外部决策策略体，只有 `external:` 引用。实施 PR 需确定策略的 canonical 存放位置、版本解析与审阅责任，否则无法验证 GO/HOLD/KILL 如何从八个 Gate 的 assessment 汇总。还需确认 v2 版本路线和 `Tgt05DecisionRecord` 是新增审议对象还是复用现有 review surface 的版本化扩展。此 RFC 建议前者，避免污染 EP 或让 Module 冒充 GateSet。

`webReport_Stelligen` 目前没有 Git remote，且 TGT-05 设计尚未通过该仓库的 PR 审核；所以不能把它当作已批准运行规范。StelligenOS 当前 PR 只供审核科学与迁移边界，**不授权真实数据下载、250 靶点建议生成或依赖的外部运行**。
