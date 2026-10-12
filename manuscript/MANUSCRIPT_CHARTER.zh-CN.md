# StelligenOS 论文总纲与证据契约

## 1. 论文目的

把 StelligenOS 作为一个 biotechnology asset operating system 的设计、实现与验证路线写成可审查的系统论文，使创业项目中的架构决策、软件实现、证据边界和后续实证工作共享同一个学术锚点。

论文不是商业宣传稿，也不以篇幅覆盖整个仓库为目标。它必须提出一个可被同行接受或反驳的核心贡献，并把每一项主张绑定到可定位的证据。

## 2. 暂定研究定位

- 论文类型：design-and-implementation / systems paper；
- 核心对象：面向生物技术资产发现、验证、生成与开发的 operating system；
- 方法主干：Candidate × Gate × Evidence 六对象决策模型、版本化 GateSet、证据生产模块、显式人工决策与审计链；
- 主要研究问题：能否用一个版本化、证据约束且人类可审计的 operating-system abstraction，统一生物技术资产从机会发现到开发承诺之间原本割裂的决策活动？

以上均为 **research 前的 framing hypothesis**，不是已经确认的论文贡献。正式 `confirmed_contribution.md` 必须在本地材料索引、相关工作研究和证据缺口分析完成后，由负责人明确确认。

## 3. 当前允许的主张

在没有新增实证验证前，论文只能主张：

1. 仓库定义并实现了一套明确的架构与软件边界；
2. Candidate × Gate × Evidence 模型、版本化合同、八个 primary Evidence Production Module 和审计门禁在代码与测试层面存在；
3. 系统通过确定性测试、边界检查和历史 PR 审核证明了实现一致性与治理可追溯性；
4. CRC ADC 工作流可作为设计实例或案例说明，但只有已有、可追溯材料能够支持的部分才可写成结果。

## 4. 当前禁止或必须弱化的主张

在获得相应外部证据前，不得声称：

- StelligenOS 提高了真实世界药物研发成功率、临床成功率或投资回报；
- 系统优于现有药物研发平台、AI drug discovery 平台或人工专家流程；
- Gate 结论已获得前瞻性、跨项目或跨机构验证；
- 任何候选靶点、抗体、ADC 或资产具有临床安全性、有效性、可开发性或法律 FTO；
- 软件测试等价于科学有效性或临床有效性；
- 当前 preview、proposal、assessment envelope 或人工审核记录等价于 accepted biological result。

## 5. 证据层级

| 层级 | 可用材料 | 能支持的论文内容 | 不能替代 |
|---|---|---|---|
| E0 架构文本 | canonical contracts、schemas、protocols | 概念模型、设计原则、边界 | 软件实现、科学有效性 |
| E1 软件实现 | `src/`、`gate_modules/`、`genmodules/` | 实现机制、接口、确定性行为 | 真实世界性能 |
| E2 软件验证 | tests、CI、boundary checks | 合同一致性、回归行为、仓库治理 | 生物学与临床验证 |
| E3 审计轨迹 | PR、handoff、worklog、review records | 可追溯治理流程 | 独立外部复现 |
| E4 受控案例 | 小型非敏感示例、外部运行摘要 | 可行性展示、工作流实例 | 普遍有效性 |
| E5 外部实证 | 仓库外数据、实验、独立评估 | 经验性性能和效用主张 | 尚不存在时不得推断 |

## 6. 暂定论文结构

1. Introduction：生物技术资产决策的碎片化、证据异质性和治理缺口；
2. Related Work：drug discovery platforms、scientific workflow systems、decision provenance、human-in-the-loop governance；
3. Design Requirements：可审计性、证据边界、版本化、未知/冲突保真、数据与实现分离；
4. System Architecture：生命周期、六对象模型、Candidate levels、GateSet 和外部 workspace；
5. Implementation：内核、Gate Modules、GenModules、扩展边界与审计基础设施；
6. Evaluation：合同一致性、测试覆盖、可追溯性，以及经批准的案例研究；
7. Discussion：适用范围、尚缺的实证、创业系统与学术系统之间的张力；
8. Limitations and Future Work；
9. Conclusion。

该结构只是 Phase 0 的审查对象。正式 section blueprint 必须等待 motivation 和 contribution 双确认后才能生成。

## 7. 分阶段路线

| Phase | 交付 | 放行条件 |
|---|---|---|
| 0 | intake、论文总纲、证据/仓库边界、阶段计划 | 当前 PR 获得 ChatGPT `APPROVE` 且负责人决定 merge |
| 1 | 本地材料索引、目标场景研究、SOTA gap map、动机选项 | research gate 通过并经 PR 审核 |
| 2 | citation support bank | citation gate 通过并经 PR 审核 |
| 3 | 人类确认 motivation 与 contribution、冻结 claim boundary | 两项确认文件通过检查并经 PR 审核 |
| 4 | source inventory、evidence bank、claim register、section blueprints | planning/build gates 通过并经 PR 审核 |
| 5 | 英文主稿及图表源文件 | drafting gate 通过并经 PR 审核 |
| 6 | 完整性审计、外部 PDF/DOCX 构建记录、中文翻译包 | audit gates 通过并经 PR 审核 |
| 7 | reviewer audit、投稿材料与最终冻结 | final audit 通过并获得最终审核 |

每个 Phase 独立 PR。未获得当前 PR 的明确 `APPROVE`，不得进入下一行。

## 8. 当前未决决策

- 目标期刊与读者群；
- 论文最终贡献属于 new system、design framework 还是 analysis/benchmark；
- 哪些 CRC ADC 材料满足可发表案例研究的证据要求；
- 需要补做哪些外部实证才能支持超出“设计与实现”的效用主张；
- 作者、单位、利益冲突、数据与代码可用性陈述。
