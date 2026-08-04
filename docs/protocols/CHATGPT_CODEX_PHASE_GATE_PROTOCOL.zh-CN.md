# ChatGPT-Codex 分阶段 PR 审核协作协议

## 1. 目的

本协议定义一套由人类、ChatGPT、Codex 和 GitHub 共同完成复杂任务的方法。核心目标是让 Codex 始终按照人类与 ChatGPT 共同制定的总纲分阶段执行，避免执行过程脱离原始计划、擅自扩大范围或在未经审核的情况下进入下一阶段。

本协议适用于 StelligenOS 的架构建设、迁移、代码实现和其他需要多轮审核的复杂任务。

## 1.1 全局适用范围与不可绕过门禁

本协议不是只针对代码 Phase 的建议，而是 StelligenOS 的全局执行配置。以下工作全部必须通过 GitHub PR 提交 GPT/ChatGPT 审核：架构和文档变更、代码和脚本、配置、迁移、外部数据处理、试运行、分析运行和由上述变更触发的结果生成。

**唯一例外：** `prompts/GPT-Feedback.md` 的单文件反馈更新，由人类负责人于 2026-08-04 授权，默认通过、无需 ChatGPT 审核。该例外的权威定义与精确文件集合见 `AGENTS.md`「审核豁免」一节，此处不复述以免两处漂移。它**只豁免审核**：PR、`logs/worklog.md` 留痕和 `docs/handoff/` 交接备忘一律照常，本协议下文关于留痕与 handoff 的要求对该例外完全适用。审核豁免以整个 PR 为单位，因此这两个配套审计文件随该 PR 一同出现时，不会使它重新落入审核门禁；但它们只能承载本次反馈更新自身的记录。把该文件中的反馈变成任何架构、代码或 Gate 改动，仍须走完整 Phase gate。

- GPT/ChatGPT 对当前 PR 明确返回 `APPROVE` 前，Codex 不得进入下一 Phase、开始下一项依赖工作、执行依赖该 PR 的外部运行、扩大范围或继续修改。
- `REQUEST_CHANGES` 后只能在同一个 PR 中按反馈做最小修订；修订后必须重新验证并再次提交同一个 PR。
- 每一个动作都必须在 `logs/worklog.md` 留下带时间戳的记录，包括读取、决策、命令、修改、验证、外部运行、失败、修正、审核反馈和结果；每一个 PR 和每一次外部运行都必须更新 `docs/handoff/`，不以任务大小作为豁免条件。
- 外部数据和结果不得进入 StelligenOS。PR 只能提交软件、架构契约、运行 manifest、摘要、校验信息和外部路径引用，以保持仓库 data-free。

## 2. 四个角色

### 人类负责人

- 与 ChatGPT 深度讨论目标、约束、优先级和总体路线。
- 确认总纲和 Phase 划分。
- 决定是否接受外部审核意见。
- 最终决定 merge、打回和是否启动下一 Phase。

### ChatGPT

- 负责理解问题、澄清目标、制定总体计划和阶段验收标准。
- 通过 GitHub 插件读取 PR、diff、commits、handoff、报告、清单和验证结果。
- 对每个 Phase 的完成情况进行独立审核。
- 只有在当前 Phase 达到要求时，才明确允许进入下一 Phase。

### Codex

- 负责按照已批准的总纲和当前 Phase 执行具体修改。
- 不擅自改变总体目标、Phase 顺序或验收标准。
- 通过任务分支、commit、PR 和 handoff 交付执行结果。
- 根据 ChatGPT 的反馈修订当前 PR，直到获得批准。

### GitHub

- 保存代码、文档、commit 历史和 PR 审核上下文。
- 作为 ChatGPT 与 Codex 之间的交付中间层。
- 让审核基于可追溯的远程 diff，而不是依赖人工搬运文件或聊天转述。

## 3. 总体生命周期

复杂任务必须按照以下顺序推进：

```text
人类与 ChatGPT 深度讨论
        |
        v
制定总体计划、Phase 划分和验收标准
        |
        v
Codex 从 main 创建当前 Phase 任务分支
        |
        v
Codex 只执行当前 Phase 范围
        |
        v
提交、推送并创建 PR
        |
        v
ChatGPT 通过 GitHub 插件审核 PR
        |
        +---- REQUEST_CHANGES ----> Codex 按反馈修订当前 PR
        |                              |
        |                              +---- 再次提交 PR 审核
        |
        +---- APPROVE -------------> 人类决定是否 merge
                                       |
                                       v
                              进入下一 Phase
```

任何 Phase 在获得 `APPROVE` 前都不得进入下一 Phase。`REQUEST_CHANGES` 不代表任务失败，而是要求 Codex 留在当前 Phase 内继续修订。

## 4. Phase 开始前：总纲冻结

ChatGPT 在 Phase 开始前应明确以下内容：

- 总体目标和当前 Phase 目标；
- 当前 Phase 的范围和明确不做的事情；
- 依赖的架构契约、旧系统来源和已有决策；
- 需要生成或修改的文件类型；
- 验收标准、验证命令和审核结论格式；
- 数据边界和禁止引入的文件类型；
- 当前 Phase 通过后允许进入的下一阶段。

Codex 开始执行前应读取这些材料，并在 handoff 或 PR 描述中引用它们。若执行中发现总纲存在冲突、缺少关键决策或需要扩大范围，Codex 必须停在当前 Phase，向负责人请求 ChatGPT 重新定义范围，不得自行改写总纲。

## 5. Phase 执行规则

Codex 在当前 Phase 内必须：

1. 从正确的基线分支同步最新代码。
2. 创建 `task_<编号>_<简短名>` 任务分支。
3. 只修改当前 Phase 明确允许的文件。
4. 不把数据、缓存、结果、临时产物或无关文件放入仓库。
5. 提交前运行 `git status --short`。
6. 只使用 `git add -- <相关文件>`，禁止 `git add .`、`git add -A` 和 `git add --all`。
7. 更新 worklog 和当前任务 handoff。
8. 运行 Phase 要求的验证，并保存命令和结果。
9. 创建指向规定基线的 PR。
10. 停下来等待 ChatGPT 审核，不以“代码看起来完成”为理由自行进入下一 Phase。

## 6. PR 审核循环

每一个 Phase 都要经过一个或多个完整的 PR 审核循环：

### 第一步：提交初版 PR

Codex 提交 PR 时必须提供：

- PR 标题和范围；
- base、branch 和 commit 信息；
- 本次改动和明确未改动内容；
- handoff；
- Phase report、review checklist 和 manifest（如当前 Phase 适用）；
- 验证命令和结果；
- 数据边界声明；
- 当前未决问题和风险。

### 第二步：ChatGPT 读取 PR

负责人把 PR 链接交给 ChatGPT，或在约定的“GitHub PR 信息”聊天中提交审核指令。审核时必须通过聊天框的 `+` 菜单确认 GitHub 来源，并要求 ChatGPT 读取 GitHub 上的当前 PR，而不是只看本地工作区或旧聊天内容。

### 第三步：ChatGPT 输出审核结论

审核范围只能限制在当前 PR，包括：

- 当前 PR 的完整 changed files；
- 所有 commits 和 aggregate diff；
- 当前 PR 描述；
- handoff、report、checklist、manifest；
- 验证结果和数据边界；
- 与已批准总纲的冲突。

允许的结论为：

- `APPROVE`
- `APPROVE_WITH_NONBLOCKING_COMMENTS`
- `REQUEST_CHANGES`
- `REJECT_PHASE`

### 第四步：Codex 按反馈修订

- `REQUEST_CHANGES`：Codex 只修当前 PR 指出的阻断和必要问题，不扩展到下一 Phase。
- `APPROVE_WITH_NONBLOCKING_COMMENTS`：只能表示当前 PR 没有新增阻断性意见，不能作为 Phase 放行结论；Codex 仍须等待明确的 `APPROVE` 才能进入下一 Phase。负责人可以在不推进下一 Phase 的前提下决定是否先处理非阻断意见或 merge。
- `REJECT_PHASE`：Codex 停止当前执行，等待人类与 ChatGPT 重新讨论总纲或 Phase 定义。
- `APPROVE`：当前 Phase 达到审核要求，等待负责人决定 merge 和下一 Phase。

每次修订都必须重新运行相关验证、更新 handoff，并把 ChatGPT 的反馈保存到 `logs/`。之后再次提交同一个 PR 供 ChatGPT 审核，直到结论不再是 `REQUEST_CHANGES` 或 `REJECT_PHASE`。

## 7. Phase 放行门

只有同时满足以下条件，Phase 才能放行：

- ChatGPT 对当前 PR 明确给出 `APPROVE`；`APPROVE_WITH_NONBLOCKING_COMMENTS` 不满足 Phase 放行条件，只能作为当前 PR 的非阻断性审查记录；
- 当前 PR 的 aggregate diff 验证通过；
- handoff 与 PR 当前状态、base、code head、metadata commits 和验证结果一致；
- 规定的脚本、测试、报告、清单和 manifest 均已完成；
- 没有引入违反仓库边界的数据或临时产物；
- 没有超出当前 Phase 的业务功能或架构设计；
- 人类负责人决定 merge，或明确批准在当前流程下开始下一 Phase。

如果任一条件不满足，Codex 必须留在当前 Phase。

## 8. 交接与历史记录

每个 Phase PR 都必须在 `docs/handoff/` 留下交接备忘，记录：

- 总体计划和当前 Phase 目标；
- 当前 Phase 实际改动和明确未改动；
- base、code head、PR tip、commit 分类和 PR 状态；
- ChatGPT 每轮审核结论和剩余问题；
- 验证命令和结果；
- 未决风险、下一步和是否允许进入下一 Phase。

ChatGPT 的原始审核反馈保存到 `logs/`，作为审计证据。worklog 记录时间顺序和执行过程；handoff 记录当前收敛状态。历史 worklog 中的旧状态可以保留，但 handoff 必须始终反映当前状态。

## 9. 防止 Codex 胡乱执行

以下行为不允许：

- 未经 ChatGPT 总纲定义就直接开始大范围实现；
- 把未来 Phase 的设计或功能塞入当前 PR；
- 发现范围冲突后自行改变 Phase 目标；
- 未经 PR 审核就从一个 Phase 跳到下一个 Phase；
- 用本地未推送状态替代 GitHub PR 审核材料；
- 使用全量暂存命令把未经检查的文件带入 PR；
- 把聊天中的计划、推测或未来建议当成已批准架构。

本协议的核心不是让 Codex 慢下来，而是让每一次执行都有明确的范围、可验证的产物和独立的放行判断，从而保证最终结果持续符合人类与 ChatGPT 最初制定的路线。

## 10. 推荐审核指令

```text
请使用当前已选中的 GitHub 插件审核这个 Phase PR：
<PR URL>

请读取当前 PR 的完整 changed files、所有 commits、aggregate diff、PR 描述、handoff、report、checklist、manifest 和验证结果。

请只审核当前 Phase 和当前 PR，不扩展到未来 Phase 或无关重构。
请重点检查：
1. 是否严格按照人类与 ChatGPT 已批准的总体计划执行；
2. 是否只完成当前 Phase 范围；
3. 是否存在越界功能、数据、缓存、临时产物或无关文件；
4. handoff 是否与 PR 当前状态一致；
5. aggregate diff 和验证结果是否完整；
6. 是否满足进入下一 Phase 的放行门。

请输出 APPROVE、APPROVE_WITH_NONBLOCKING_COMMENTS、REQUEST_CHANGES 或 REJECT_PHASE。
如果批准，请明确写出是否可以进入下一 Phase；如果不批准，请只列出当前 PR 的具体阻断项和最小修复方式。
```
