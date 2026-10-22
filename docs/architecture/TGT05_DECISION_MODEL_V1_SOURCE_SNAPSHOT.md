# TGT-05 决策模型 v1.0
我建议现在正式收敛 TGT-05。我们已经有足够的信息设计一个可以执行 GO / HOLD / KILL 的 ADC 靶点正常组织毒性决策模型，不需要继续无限增加数据库、证据等级和预测算法。

但首先明确一个边界：

M0 阶段的 GO 不是证明 ADC 安全，而是判断 Target X 是否存在足够低的正常组织靶点相关风险，值得投入下一阶段研发。

同样，KILL 不是宣称 Target X 永远不能开发，而是终止它在当前 ADC 开发场景中的推进。

一、TGT-05 的最终科学问题

If an ADC kills normal human cells expressing Target X, could the resulting cell loss cause unacceptable organ toxicity?

这个问题只需要回答三个子问题：

1. Exposure： 哪些正常人体细胞具有可被 ADC 接触的 Target X 表面抗原？
2. Consequence： 如果这些细胞被杀伤，会造成什么程度的组织功能损伤？
3. Evidence： 我们有多大把握相信上述判断？

不再考虑 Target X 的激活、抑制、敲除所产生的药理学效应。

不再引入传统 target essentiality 评分。

DepMap 和小鼠基因敲除不作为 TGT-05 的核心决策证据。

这是一个重要的范围收敛。

⸻

二、只保留三个证据层级

我建议 TGT-05 采用以下三级证据模型。

Level	Evidence	决策权重
E1：Direct	同靶点 ADC 的临床靶点相关毒性；相关抗体的正常人体组织结合及功能性细胞毒性实验	最高
E2：Protein	正常人体组织经过验证的膜蛋白 IHC、流式、表面蛋白组学	高
E3：RNA	正常组织 scRNA、spatial RNA、bulk RNA	辅助

其他证据全部降级为 supporting information。

注意两个细节。

第一，E1 的临床毒性必须有靶点相关机制证据。

同靶点 ADC 出现肝毒性，并不自动说明 Target X 在正常肝脏表达造成了损伤。

第二，E2 需要尽可能确认细胞膜定位。

普通 total-protein IHC 阳性不能直接等同于循环 ADC 可以结合的细胞表面抗原。

E1 与 E2 的关系

E1 可以直接支持重大风险判断。

E2 可以发现高风险正常细胞群，但单纯发现表达通常不足以证明不可接受的毒性。

E3 不能单独支持 GO，也不能单独支持 KILL。

这三个规则应该固定下来。

⸻

三、只保留四类正常组织风险

不需要为每个器官建立一个独立预测模型。

我们首先把所有正常组织归入四种风险场景。

Risk Class	典型组织 / 细胞	判断依据
Critical functional cells	心肌细胞、神经元、部分肺泡上皮细胞	损伤可能造成严重功能障碍，恢复能力有限
Essential barrier cells	肠道、肺、肾脏等关键上皮细胞	广泛损伤可能破坏器官屏障或运输功能
Regenerative compartments	骨髓造血细胞、组织干/祖细胞	损伤可能造成持续性组织功能缺陷
Other normal cells	其他正常细胞群	需要根据损伤范围、功能和恢复能力判断

这些不是固定的器官毒性等级，而是帮助判断细胞丢失后果的分类。

例如，正常肝脏表达 Target X，不等于自动判定高风险。

必须继续问：

是肝细胞、胆管细胞，还是其他细胞？

表达比例有多大？

是否具有细胞外可接触的抗原？

损伤是否可能导致不可接受的功能后果？

器官名称本身不是 KILL 标准；关键正常细胞群的可接触抗原及其损伤后果才是。

⸻

四、TGT-05 决策模型 v1.0

我建议采用一个极简的决策矩阵，而不是加权综合评分。

1. GO

满足以下条件：

* 没有可靠证据显示 Target X ADC 存在不可接受的靶点介导正常组织毒性。
* 主要高风险正常组织已有足够的蛋白层面证据支持评估。
* 未发现无法合理解释的关键正常细胞高可接触抗原风险。
* 剩余不确定性可以在 M1 通过有限实验验证。

GO 的含义：允许 Target X 进入下一阶段，而不是确认安全。

如果大多数关键组织只有 RNA 数据，没有可靠的蛋白证据，不应轻易 GO。

2. HOLD

出现以下情况：

* 某个关键正常细胞群具有潜在 Target X 表达，但缺少膜蛋白证据。
* RNA 与蛋白证据严重冲突。
* 已有同靶点 ADC 出现严重毒性，但无法判断是否为 on-target。
* 存在高风险正常组织表达，但抗原可及性未知。

HOLD 必须附带一个明确的解决方案。

例如：

HOLD — Confirm Target X membrane accessibility in normal alveolar epithelial cells.

不能只是：

“需要更多数据。”

3. KILL

需要相对严格的证据。

例如：

情形 A：已有可靠的同靶点 ADC 临床证据，支持不可接受的靶点介导正常组织毒性。

或者：

情形 B：相关 ADC 或适当的抗体–payload 实验已经证明，关键正常细胞发生靶点依赖性杀伤，且损伤严重程度与预期开发条件不相容。

仅仅因为正常组织 RNA 高表达，不能 KILL。

仅仅因为某个正常组织 IHC 阳性，也不能 KILL。

即使是关键正常细胞存在膜蛋白，也通常还需要评估实际可及性、结合和潜在损伤。

⸻

五、最高优先级的数据：只保留三种

你要求跳出最高层级的信息，我建议这样排序。

Priority 1：已有同靶点 ADC 临床毒性证据

这是最应该首先检查的。

因为 Target X 来自 ADCdb，意味着至少存在 ADC 研发先例。

但要注意，ADCdb 记录不一定意味着该靶点已有临床 ADC。

如果有临床 ADC，优先调查：

* 是否发生严重器官毒性；
* 是否造成剂量限制或项目终止；
* 是否有正常组织靶点表达与毒性归因证据；
* 不同 ADC 构型是否出现一致信号。

有可信的靶点相关严重毒性，可以直接触发 KILL 审议。

如果只有不良事件、没有机制归因，则进入 HOLD 或继续评估，而不是直接 KILL。

Priority 2：正常人体膜蛋白证据

优先：

HPA validated membranous IHC + cell-surface proteomics。

这比继续增加 bulk RNA 数据更有价值。

目标是得到：

Target X → Organ → Normal Cell Type → Surface Antigen Evidence

不需要一开始计算复杂的风险分数。

只需要找出最值得担心的正常细胞。

Priority 3：正常人体单细胞 RNA

优先用于补充蛋白证据不足的组织。

尤其是：

* 稀有但功能重要的细胞；
* 组织平均表达较低的细胞群；
* IHC 难以明确定位的细胞群。

空间转录组在这里是可选的。

如果已有可靠的细胞类型定位和膜蛋白证据，不必为了完整性强制增加空间转录组。

⸻

六、真正能够决定 GO / KILL 的关键实验

对于 M0 阶段，我建议只定义一个最高优先级的实验方案。

Human Normal-Tissue Binding and Functional Toxicity Assessment

它分成两个连续步骤。

Step 1：正常人体组织结合实验

使用具有充分特异性验证的候选抗体，检查相关正常组织中的结合情况。

重点关注：

* 结合的是哪种细胞；
* 是否位于可接触的细胞膜；
* 是否存在明显的关键组织结合；
* 结合是否具有靶点特异性。

如果发现关键正常细胞明显结合，就进入第二步。

Step 2：正常细胞功能性毒性实验

在适当的正常原代细胞、类器官或其他模型中，使用相关 ADC 检查：

* 是否发生靶点依赖性结合和摄取；
* 是否发生细胞杀伤；
* 是否存在相应的正常组织功能损伤；
* 是否能够通过抗原竞争、靶点缺失对照或其他方式支持靶点依赖性归因。

这里必须强调：

没有具体抗体和 ADC 分子时，不能完成完整的功能性 ADC 毒性实验。

因此，M0 可以通过公共数据做出投资决定，但最终的功能性 GO/KILL 需要在后续分子开发阶段验证。

为什么不选小鼠 knockout？

因为它回答的是：

Target X 缺失后会发生什么？

而我们要回答的是：

表达 Target X 的正常细胞被 ADC 杀死后会发生什么？

这不是同一个实验问题。

⸻

七、最终输出：一页 TGT-05 Decision Record

每个 ADCdb Target X 最终只需要交付以下内容。

Field	Decision content
Target	HGNC symbol / ADCdb ID
Existing ADC clinical liability	Confirmed / Suspected / None documented / Unknown
Highest-risk normal organ	Organ and cell type
Surface antigen evidence	Direct / Indirect / Unknown
Cell-loss consequence	Critical / Potentially serious / Limited / Unknown
Main uncertainty	One decisive unresolved question
TGT-05 recommendation	GO / HOLD / KILL
Next experiment	One experiment capable of changing the decision
Reversal criterion	Explicit result that would reverse the recommendation

这份记录直接进入现有 TGT-05 的 EvidencePackage 和人工审核流程，不建立第九个 Gate。

⸻

八、三个假设性案例

Target	Evidence	Decision
X1	多种关键正常组织缺乏可接触膜抗原的可信证据；已有覆盖充分的蛋白检测；无已知重大靶点相关临床毒性	GO
X2	正常肺泡上皮细胞 scRNA 显示表达，但膜蛋白和抗原可及性未知	HOLD
X3	同靶点 ADC 已出现有充分机制支持的严重正常组织损伤，且与拟开发场景相关	KILL

这里的 X1 不是因为数据库没有查到表达就 GO，而是因为经过适当覆盖和质量控制的检测，提供了有意义的阴性证据。

这是一个重要区别。

⸻

九、正式收敛后的执行方案

我建议现在停止广泛文献探索，将 TGT-05 固定为：

Clinical Precedent → Normal-Cell Surface Expression → Cell-Loss Consequence → GO / HOLD / KILL

具体执行时：

第一步，对 ADCdb 中的 Target X 检查已有临床 ADC 的安全性记录。

第二步，使用正常人体蛋白和单细胞表达数据，确定最值得担心的正常细胞群。

第三步，根据细胞的器官功能重要性、抗原可及性和证据质量作出判断。

第四步，只对可能改变决策的关键不确定性设计下一步实验。

最终原则：不要求证明 Target X 对所有正常组织绝对安全，只要求排除已知不可接受的靶点相关风险，并对剩余关键风险给出可执行的验证方案。

这样 TGT-05 才能真正成为 M0 阶段的投资筛选工具，而不是一个永远无法完成的正常组织图谱项目。
