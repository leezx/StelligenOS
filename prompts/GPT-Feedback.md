
# v4
/Volumes/Stelligen_SSD/Stelligen/StelligenOS/docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md
审核这一套，是否有什么重大缺陷

整体评价：没有发现足以推翻整个架构的致命设计错误。这套架构已经从“一个 ADC pipeline”演化成了一个资产操作系统（Asset Operating System），对象、生命周期、Gate、能力模块和治理边界基本已经分离，软件工程上是成立的。 CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md

但是，如果我是一个有 ADC 开发经验的技术负责人或投资人，我会提出 4 个一级风险（Major Design Risks） 和 7 个二级风险（Important Improvements）。

⸻

一级风险一：缺少真正的“Ground Truth Learning Loop”

这是我认为目前最大的缺陷。

你的系统目前是：

Evidence → Gate → Asset Generation → Due Diligence

但是真正优秀的平台应该还有：

Clinical Outcome → 回写 Rule → 回写 Model → 回写 Gate Calibration

否则 Rule 永远停留在”经验总结”。

目前文档提到了：

* calibration
* Knowledge Ledger
* model lifecycle

但是没有定义：

哪一种真实结果可以改变系统。

例如：

一个 ADC III 期失败。

到底应该：

* 修改 Rule？
* 修改 Gate threshold？
* 修改某个 Model？
* 还是只是新增 evidence？

目前没有治理。

建议新增：

Learning Engine（Calibration Engine）

专门负责：

* Clinical outcome ingestion
* Rule calibration
* Model retraining
* Gate threshold validation

否则 Gate 很容易越积越多，却不会越来越准。

⸻

一级风险二：Gate 是静态的，而 Biology 是动态的

你目前：

45 Gate

几乎全部假设：

Target 是固定对象。

但是真实 ADC：

Target 的意义完全依赖：

* indication
* stage
* line of therapy
* biomarker
* combination therapy

例如：

HER2：

乳腺癌：

完全不同。

CRC：

又完全不同。

HER2-low：

又不同。

因此真正评分对象其实不是：

Target

而应该是：

Target × Clinical Context

严格来说应该是：

Clinical Hypothesis

不是 Target。

虽然你前面已经强调：

Clinical first

但是 Gate 输入对象仍然偏向：

TargetHypothesis

建议未来逐步把 Gate 输入改成：

ClinicalOpportunity

而不是：

Target。

这样未来：

ADC

TCE

Radioligand

都会统一。

⸻

一级风险三：Asset Generation 目前仍然是”路线”，不是”搜索”

这一点比较关键。

目前：

Asset Generation

实际上只有两条：

* Existing Binder
* de novo Binder

但是真实 ADC Optimization：

远不止 Binder。

例如：

Payload

Linker

DAR

Site-specific conjugation

Fc engineering

Half-life tuning

Affinity tuning

Epitope shifting

Internalization enhancement

都属于 Asset Search Space。

现在：

Product Gate

负责评价。

但是没有负责：

主动搜索。

换句话说：

目前：

Generation：

几乎只生成 Binder。

未来真正的平台应该是：

Asset Search Engine

里面包括：

多个 Generator：

Binder Generator

Payload Generator

Linker Generator

ADC Architecture Generator

Developability Optimizer

然后统一进入：

Product Gate。

这一块未来扩展空间非常大。

⸻

一级风险四：没有定义 “Stop Rule”

目前：

系统一直在：

Evidence越来越多

Gate越来越多

Review越来越多

但是：

什么时候：

Enough?

没有定义。

例如：

T7：

到底：

多少证据：

可以认为：

Ready?

不知道。

建议：

每个 Gate：

增加：

Evidence Sufficiency Contract

例如：

至少：

Independent evidence >=3

Conflict resolved

Confidence>0.8

Major unknown cleared

否则：

永远可以继续搜索文献。

这是很多 AI Scientist 最后掉进去的大坑。

⸻

七个二级风险

① Evidence Independence 定义仍然不够严格

例如：

Nature Review

引用：

Nature Paper。

PubMed：

又引用：

Nature。

实际上：

还是：

一份证据。

建议未来：

Knowledge Graph

真正追踪：

Primary Source。

⸻

② Opportunity Ranking 太晚

目前：

T12

最后才排序。

实际上：

搜索空间巨大时。

最好：

每完成几个 Hard Gate。

就：

动态排序。

类似：

Beam Search。

否则：

计算浪费。

⸻

③ Due Diligence 可以更早介入

目前：

DD：

最后。

实际上：

FTO

很多时候：

Target 阶段：

就已经决定。

建议：

IP Risk

早点出现。

⸻

④ Commercial Gate 可以动态更新

市场：

不断变化。

例如：

昨天：

HER3

没人。

今天：

十家公司。

Commercial：

应该：

实时刷新。

⸻

⑤ Asset 没有 Probability

目前：

Gate：

更多：

Pass

Hold

Fail

建议：

整个系统：

始终维护：

一个：

Success Probability

方便：

Portfolio。

⸻

⑥ 缺少 Resource-aware Planning

现实研发：

不是：

最佳方案。

而是：

预算内最佳方案。

例如：

实验：

5万美元

还是：

100万美元。

建议：

Experiment Branch：

增加：

Cost

Time

Information Gain

Expected Value。

以后：

AI 自动排实验。

⸻

⑦ 缺少 Portfolio Learning

如果：

100 个项目：

失败：

真正应该学习：

为什么：

整个 Portfolio：

失败。

目前：

Learning：

还是：

单项目。

未来：

Portfolio Analytics：

价值很大。

⸻

我最欣赏的三个设计

第一：Clinical First

这是整个系统最重要的地方。

很多 AI Drug Discovery：

都是：

Target First。

你的：

Clinical unmet need

↓

Endpoint

↓

Target

这个方向更符合临床开发逻辑。 CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md

⸻

第二：Rule 不允许直接控制 Gate

这是非常成熟的软件治理思想。

否则：

Rule

越来越多。

最后：

没人知道：

为什么通过。

这一条建议保留。 CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md

⸻

第三：Binder 双轴 Pareto

这一点我认为比很多论文更合理。

Sequence Quality

和

Carrier Phenotype

不能互相补偿。

现实研发里也确实经常出现：

一个 developability 很好的抗体，

结果：

完全不内吞。

如果加权平均：

反而会被误判。

因此 Pareto 是合理选择。 CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md

⸻

我的结论是：

如果按 10 分制评分：

* 软件架构：9.3/10
* 软件工程规范：9.7/10
* ADC 研发流程抽象：8.8/10
* AI Agent 可执行性：9.0/10
* 生物学真实性：8.3/10
* 长期可扩展性：9.5/10

我认为目前没有必须推倒重来的重大缺陷，可以继续推进下一阶段。

不过，在真正开始大规模生成资产之前，我会优先补齐两件事，而不是增加新的 Gate：

1. 建立 Calibration / Learning Engine，明确真实世界结果如何更新 Rule、Model 和 Gate。
2. 为每个 Gate 制定 Evidence Sufficiency Contract，定义“什么情况下证据已经足够，可以停止继续收集”。

这两项会直接决定系统能否随着项目推进不断提高判断质量，而不是仅仅积累越来越多的信息。

# v3

审批结论

Phase 0 修订：基本通过。
Phase 0.5：未完成。
暂不批准进入 Phase 1。

这版已经修正了上次两个主要问题：

* StelligenOS 已明确为 biotechnology asset operating system，而不是普通软件仓库。
* AssetGenOS 已正确降为 Opportunity Validation 下的子系统。
* Asset Development、Capability层、阶段化Due Diligence、商业意义上的Asset定义都已写入。
* 架构入口与运行Prompt已经分离。
* Repository boundary也比上一版合理。

但还有三个阻断项需要在Phase 0.5一起处理。

⸻

阻断项一：Legacy Inventory仍然只是计划，不是盘点结果

当前的：

docs/architecture/legacy_inventory.zh-CN.md

只有四部分：

* Purpose
* Scope
* Output
* Non-goals

它没有实际列出任何旧组件，也没有形成migration matrix。

Phase 0报告自己也明确承认：

Phase 0.5 is now required as a small legacy inventory pass before Phase 1.

所以不能把当前状态理解为“Phase 0 + Phase 0.5已完成”。README中的：

Current Phase
Phase 0 plus Phase 0.5

容易造成误导。应改为：

Current Phase
Phase 0 completed.
Phase 0.5 pending legacy source inventory.

Phase 0.5至少必须实际盘点：

* 原AssetGenOS；
* 45个Gate及其contracts；
* 已生成的naive rules；
* ADC calibration数据与Prompt；
* antibody_binder_asset_engineering；
* epitope_conditioned_de_novo_antibody_discovery；
* biotech_asset_due_diligence；
* 已有architecture、migration、implementation文档；
* TWEAKR案例资产。

如果这些内容分布在其他仓库或ZIP中，应记录外部来源路径。不能仅仅写“未来要盘点”。

⸻

阻断项二：语言规范尚未落实

用户规定非常明确：

* 操作系统说明、README、Prompt、log、Phase报告：中文；
* 脚本、Schema、字段、核心数据和科学/资产报告：英文。

当前实际情况不符合：

* README.md 基本为英文；
* architecture.md 为英文；
* PHASE_0_REPORT.zh-CN.md 正文几乎全部为英文；
* PHASE_0_REVIEW_CHECKLIST.zh-CN.md 为英文；
* capabilities.zh-CN.md 和 lifecycle.zh-CN.md 基本为英文；
* 文件后缀标注了zh-CN，但内容并不是中文。

这不是表面格式问题。语言分层是StelligenOS降低操作成本的核心规范，必须在架构冻结前真正执行。

建议：

* README.md：中文主体，保留必要英文术语；
* architecture.md：中文导航；
* docs/architecture/*.zh-CN.md：中文说明，类名和ID保持英文；
* Phase报告和审核清单：中文；
* Manifest、Schema、脚本：英文；
* 后续科学报告、asset report、DD report正文：英文。

⸻

阻断项三：Phase报告与Manifest状态不一致

报告写：

Phase 0.5 is now required

Manifest却写：

status: revised_after_feedback
follow_up_phase: "0.5"

README又写：

Phase 0 plus Phase 0.5

三者对当前阶段的表达不一致。

建议统一为：

phase: 0
status: completed
recommendation: PROCEED_TO_PHASE_0_5
follow_up_phase: "0.5"

Phase 0.5需要单独拥有：

docs/phases/PHASE_0_5_REPORT.zh-CN.md
docs/phases/PHASE_0_5_REVIEW_CHECKLIST.zh-CN.md
manifests/phase_0_5_manifest.yaml

不要继续把0.5塞进Phase 0报告里，否则审计边界会越来越模糊。

⸻

两个必须顺手修正的问题

1. 不应把.DS_Store列为允许文件

verify_repository_boundary.sh把.DS_Store放入了允许列表：

".DS_Store"

这等于正式接受无价值的系统元数据污染仓库。应删除该允许项，并确保：

.DS_Store
__MACOSX/

当前ZIP中还包含大量__MACOSX和.DS_Store内容。即使Git未追踪，也不应视为仓库允许内容。

2. Repository boundary的“非数据承载”定义过严且不清楚

文档允许：

demo assets
golden test cases

但同时要求它们：

non-data-bearing

严格来说，golden test case和demo asset必然包含少量数据。真正应该禁止的是：

* 大型原始数据；
* 患者级敏感数据；
* 实验工作区；
* 可再生的中间产物；
* 大型生成输出。

而应允许：

* 小型合成fixtures；
* 脱敏后的最小示例；
* 用于测试Schema的JSON/YAML；
* 一个受控的reference asset package；
* 小型golden outputs。

建议改成：

small, synthetic, de-identified, version-controlled reference data may be stored when necessary for tests, examples or reproducibility.

否则后面Phase 2建立Schema测试时，会被自己的boundary规则卡住。

⸻

关于Capability层的最终边界

Capability层可以保留，但不要把当前九项写成永远不变的封闭清单。

目前：

Opportunity Discovery
Knowledge Mining
Rule Learning
Evidence Extraction
ADC Design
Binder Engineering
Patent Analysis
Due Diligence
Portfolio Management

其中Due Diligence、Patent Analysis和Portfolio Management又与Cross-cutting重复。

这不是立即阻断项，但应在Phase 1冻结前明确：

* Lifecycle：项目经过哪些阶段；
* Core Objects：系统管理什么实体；
* Cross-cutting Services：哪些治理能力贯穿全局；
* Capabilities：系统目前能执行哪些任务，可增加和演化。

也就是说，Capability清单不应成为冻结架构的一部分。冻结的是“存在Capability层”，不是永远冻结这九项能力。

⸻

批准范围

我批准当前版本作为：

StelligenOS Phase 0 revised baseline

我不批准它作为：

Phase 0.5完成版
Frozen Architecture Contract
Phase 1启动基线

下一步只执行Phase 0.5，要求非常克制：

1. 实际读取旧系统来源；
2. 形成真实migration matrix；
3. 修正语言规范；
4. 统一Phase状态；
5. 清理.DS_Store政策；
6. 澄清最小测试数据例外；
7. 不创建Schema、不写业务代码、不迁移模块。

完成后再进行一次审批。通过后才进入Phase 1。

# v2

我认真看了一遍，目前我的结论是：

70/100，可以进入 Phase 1，但我不会批准原样进入。必须先修正几个架构方向，否则以后还是会返工。

这不是代码质量的问题，而是架构哲学的问题。

⸻

一、最大的错误（必须修改）

① 它把 StelligenOS 当成了 Software Repository

这是目前最大的偏差。

README 第一行就是：

StelligenOS is a software repository…

后面的 Phase0 Report 也是：

software-only repository

这其实已经把整个系统定义错了。

你的目标一直不是开发一个软件。

而是：

StelligenOS 是一个 Biotechnology Asset Operating System。

软件仓库只是它的实现形式。

应该改成：

StelligenOS
A biotechnology asset operating system.
This repository contains one implementation
of the operating system.
The repository is NOT the operating system itself.

这是完全不同的定位。

以后投资人看到 README，

第一句话应该知道：

这是Biotech OS，

不是Python项目。

⸻

二、Repository Boundary写得太死

现在它写的是：

禁止

reports
evidence bundles

我不赞成。

为什么？

因为以后一定会有：

examples/
demo/
reference_asset/
tutorial/

例如

examples/
TWEAKR/
README.md
asset_summary.md

这是系统的一部分。

如果一刀切：

report禁止

以后Demo都没地方放。

我建议改成：

⸻

Repository原则应该是

禁止

large datasets
raw sequencing
intermediate files
cache
output
temporary artifacts

允许

reference examples
toy examples
schemas
report templates
demo asset
golden test cases

否则以后会越来越难受。

⸻

三、Phase0没有真正完成Inventory

这是第二大问题。

你最开始的目标其实是：

审核旧系统。

结果现在Phase0几乎没有旧系统。

因为Codex面对的是一个新的repo。

所以它写：

No Gate

No Rule

No Evidence

当然没有。

真正的问题是：

它没有扫描

AssetGenOS

GenModule

DueDiligence

这些历史资产。

所以

这个Inventory

实际上没完成。

严格来说

它完成的是

Repository Audit

没有完成

Migration Inventory

这是两件事情。

⸻

所以我建议

新增

Phase 0.5
Legacy Inventory

非常小。

只做：

旧系统
↓
Mapping
↓
Migration Matrix

不要急着Phase1。

⸻

四、目前架构里少了一样东西

这个我昨天其实没有说。

现在我觉得必须加。

就是：

Capability

目前只有

Lifecycle
↓
Cross-cutting
↓
Objects

还缺

Capabilities

例如：

Opportunity Discovery
Knowledge Mining
Rule Learning
Evidence Extraction
ADC Design
Binder Engineering
Patent Analysis
Due Diligence
Portfolio Management

这些不是生命周期。

不是对象。

不是横向能力。

而是

OS提供的能力。

未来所有Prompt都会属于Capability。

所以我建议：

Operating System
Lifecycle
Objects
Capabilities
Cross-cutting

Capability以后一年都不会变。

Prompt天天变。

⸻

五、Evidence Ledger应该升级

现在写的是

Evidence Ledger

我建议叫

Knowledge Ledger

为什么？

以后不仅有

Evidence

还有

Rules
Hypothesis
Experiments
Failures
Decision
Calibration
Lessons

这些其实都是知识。

Evidence只是其中一类。

Knowledge Ledger

未来更容易扩展。

当然，

如果你觉得Evidence更精准，

也可以保持Evidence Ledger。

这是我唯一没有100%坚持的一点。

⸻

六、Asset定义还差一句

现在：

Asset
=
molecule
+
IP
+
...

我建议加一句：

Asset必须能够独立进入商业讨论。

也就是说

不是任何ADC都是Asset。

只有能够拿出去：

Partner
Investor
BD
Licensing

讨论的，

才叫Asset。

这是商业定义。

不是技术定义。

⸻

七、Lifecycle建议改名字

目前：

Asset Advancement

我建议：

Asset Development

原因：

Advancement

听起来像：

往前推进。

Development

生物医药行业里面：

Lead Development
Drug Development
Clinical Development

这是行业语言。

以后投资人、

药企、

技术合伙人

都会更自然。

⸻

八、Due Diligence的位置

现在还是：

Cross-cutting。

我觉得很好。

但是

建议明确一句：

Due Diligence
is stage-aware.

不同阶段：

Question set

不同。

不要只有一个DD。

⸻

九、Prompt放在Architecture里面太长

这是我很建议改的。

现在：

architecture.md
≈
Prompt

以后会越来越长。

建议：

Architecture

只写

Contract

Prompt

独立。

例如：

architecture/
contract.md
principles.md
objects.md
lifecycle.md

Prompt

放

prompts/

否则

Architecture以后5000行。

没人能维护。

⸻

十、我最满意的一点

就是：

你终于把

AssetGenOS

降级了。

这一步非常重要。

现在真正的关系终于变成：

StelligenOS
↓
Opportunity Validation
↓
AssetGenOS

不是：

AssetGenOS
=
整个系统

这是目前最大的进步。

以后整个系统终于不会围着Gate转了。

⸻

我的最终建议

我会调整为下面这个冻结版。

StelligenOS
Biotechnology Asset Operating System
────────────────────────
Lifecycle
1 Opportunity Generation
2 Opportunity Validation
    └── AssetGenOS
3 Asset Generation
4 Asset Development
────────────────────────
Core Objects
Opportunity
TargetHypothesis
BinderCandidate
ADCConstruct
LeadSeries
DevelopmentCandidate
Asset
────────────────────────
Capabilities
Knowledge Mining
Rule Learning
Opportunity Discovery
Binder Engineering
ADC Engineering
IP/FTO
Due Diligence
Portfolio
────────────────────────
Cross-cutting
Evidence (or Knowledge) Ledger
Audit
Versioning
Portfolio
IP/FTO
Due Diligence
────────────────────────
Architecture Contract
Repository
Implementation

⸻

我的审批意见

可以进入下一步，但建议先完成一次很小的修订，再冻结Phase 0。

必须修改（阻断项）：

1. 把 StelligenOS 定义为 Biotechnology Asset Operating System，而不是 software repository。
2. 完成 Legacy Migration Inventory（至少增加一个 Phase 0.5，或者把它补入 Phase 0）。

建议修改（非阻断）：

* Repository Boundary 放宽，不要禁止所有 report/example。
* 增加 Capability 层。
* Asset 补充商业定义。
* Asset Advancement 改为 Asset Development。
* Architecture Contract 与 Prompt 分离，避免后续文档膨胀。

完成这些调整后，我认为这套架构就可以作为 StelligenOS v1.0 的冻结架构，后续一年内不再改动顶层设计，把精力集中到生成第一个真实ADC资产上。

# v1

下面给出一套可直接交给 Codex 的总控 Prompt。核心原则是：先冻结架构规范，再迁移旧成果；每个 Phase 单独提交、单独审核，未经批准不得进入下一阶段。
我建议总共设置 8 个 Phase。不要再细分成几十个子项目，否则会再次陷入支线扩张。
StelligenOS 冻结后的最小架构
主流程只保留四段：
Opportunity Generation
→ Opportunity Validation
→ Asset Generation
→ Asset Advancement
横向能力只保留五项：
Evidence Ledger
IP/FTO
Due Diligence
Portfolio Decision
Audit and Versioning
核心实体只保留七类：
Opportunity
TargetHypothesis
BinderCandidate
ADCConstruct
LeadSeries
DevelopmentCandidate
Asset
系统内部可以继续增加Gate、Rule、Prompt和Engine，但不得增加新的顶层生命周期层级。
总体Phase划分
Phase	目标	是否迁移旧内容
Phase 0	仓库盘点与只读审计	否
Phase 1	建立冻结架构规范与目录骨架	否
Phase 2	建立核心对象模型、状态机和Evidence Ledger	少量
Phase 3	迁移AssetGenOS Gate体系	是
Phase 4	建立Opportunity Generation模块	是
Phase 5	迁移两条Binder/ADC生成路线	是
Phase 6	迁移IP/FTO、Due Diligence和Portfolio能力	是
Phase 7	端到端最小闭环与TWEAKR示范资产	是
Phase 8	架构冻结、发布与后续开发规范	否
Phase 0只能盘点，不能修改。
Phase 1开始才允许创建新架构。
Phase 8完成后顶层架构冻结。

Phase 0 单独执行Prompt
总控Prompt适合放进仓库，例如：
prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md
实际指挥Codex时，建议再发送下面这个更短、更具体的Phase 0指令。

我们共同审核Phase 0时，只看这七项
Codex完成后，把Phase 0报告和仓库变更发给我。审核只检查：
是否准确理解了现有仓库，而不是套用新架构。
是否偷偷修改了业务文件。
是否识别出真正可迁移的Gate、Rule、Prompt和代码。
是否把文档存在误认为功能已经实现。
是否发现重复、冲突和证据不可追溯问题。
Phase 1建议是否保持最小化。
是否存在遗漏的关键旧资产。
不要现在就让Codex开始重写目录。Phase 0越克制，后面的迁移成本越低。