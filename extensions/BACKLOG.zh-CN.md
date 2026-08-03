# Extensions Backlog

本文件登记**已知但当前不做**的扩展项。登记的唯一目的是防止遗忘。

登记不等于批准。任何一项要开始做，都必须另立任务分支、独立 PR 和 ChatGPT `APPROVE`。

## 来源

`prompts/GPT-Feedback.md` `# v4` 段落中的七个二级风险（Important Improvements）。对应的四个一级风险已建立扩展包，见 `extensions/README.md` 注册表。

## 七个二级风险

### BL-01 Evidence Independence 定义不够严格

一篇 Nature Review 引用 Nature Paper，PubMed 又引用同一篇 Nature，三条记录实际上只是一份证据。当前 evidence extraction 会把它们计为多个独立来源，从而虚增可信度。

需要的能力是追踪到 primary source 的知识图谱，按 primary source 而不是按检索命中去计数独立性。

与 `EXT-04 stop_rule` 强耦合：Stop Rule 依赖「独立证据数」这个判据，如果独立性定义是错的，Stop Rule 会提前判定证据充分。当前 `EXT-04` 已在契约中把这一点标记为已知限制。

优先级：高（因为它决定 Stop Rule 的正确性），但仍不在本次范围内。

### BL-02 Opportunity Ranking 太晚

目前排序只发生在 T12。当搜索空间很大时，应该每完成若干 Hard Gate 就做一次动态排序并剪枝，类似 beam search，否则算力浪费在明显不会赢的候选上。

需要注意的约束：动态剪枝不得把「暂时排名靠后」变成「淘汰」，也不得让排序覆盖 Hard Gate 或 HOLD 语义。

优先级：中。与 `EXT-04` 有协同（两者都是终止/剪枝语义）。

### BL-03 Due Diligence 可以更早介入

FTO 很多时候在 target 阶段就已经决定成败，但目前 DD 和 IP/FTO 集中在后段（C-chain）。IP risk 信号应该更早出现在 T-chain。

注意 45-Gate 拓扑已冻结，因此这不能通过重排 Gate 顺序实现，只能作为并行的早期风险提示，或者进入独立治理任务讨论拓扑变更。

优先级：中。

### BL-04 Commercial Gate 需要可刷新

竞争格局会变（昨天 HER3 没人做，今天十家公司在做），但 Commercial Gate 的评分是一次性的。需要给 C-chain 的结果加上时效性语义：评分快照时间、失效期限、以及重新评估触发条件。

优先级：中。

### BL-05 Asset 没有 Success Probability

目前 Gate 输出偏向 `PASS`/`HOLD`/`FAIL` 的离散状态。为了做 portfolio 层面的决策，系统应该始终维护一个可累乘、可校准的成功概率。

注意与内核设计原则的张力：`unknown` 不得被当成 0。概率化必须显式区分「低概率」和「证据不足」，否则会退化成把 unknown 当负面证据。

优先级：中。依赖 `EXT-01 ground_truth_learning_loop` 才能校准。

### BL-06 缺少 Resource-aware Planning

现实研发要的不是最佳方案，而是预算内最佳方案。5 万美元的实验和 100 万美元的实验不能同等对待。

`ExperimentBranch` 应该增加 cost、time、information gain 和 expected value 字段，让实验排序可以被自动化。

优先级：中。`genmodules/biotech_asset_due_diligence/contracts/experiment_branch.v1.yaml` 是接触面。

### BL-07 缺少 Portfolio Learning

如果 100 个项目失败，真正该学的是整个 portfolio 为什么失败，而不是单个项目为什么失败。当前 learning 的粒度是单项目。

优先级：低。依赖 `EXT-01` 和足够的历史项目数量。

## 依赖关系速览

- `BL-01` 是 `EXT-04 stop_rule` 正确性的前置条件。
- `BL-05` 和 `BL-07` 都依赖 `EXT-01 ground_truth_learning_loop` 提供真实结局数据。
- `BL-02` 与 `EXT-04` 属于同一类语义（何时停止 / 何时剪枝），将来可能合并考虑。
