# AGENTS.md for StelligenOS

## Mission

本仓库定义 StelligenOS 的实现。它是一个 biotechnology asset operating system implementation repository，
不是数据库，也不是结果仓库。

## 硬性边界

1. 仓库允许放：架构文档、Prompt、Schema、脚本、代码、参考文档，以及少量受控示例。
2. 仓库禁止放：large datasets、raw sequencing、intermediate files、caches、outputs、temporary artifacts、data-bearing working files。
3. 允许的示例材料必须小、可追溯、非敏感，并明确标注为参考或测试用途。
4. 所有数据采集、处理、分析和存储必须发生在仓库外部的工作区。
5. 如果任务需要数据，不要把数据暂存进这个仓库。
6. 任何会让仓库偏离“实现仓库”边界的改动，都要先回到架构契约。

## 工作规则

- 保持 Phase 0 / Phase 0.5 的审计优先心态。
- 现有遗留文本默认只作为参考材料，除非已被正式提升到架构契约。
- Phase 0 = 仓库审计；Phase 0.5 = 旧系统盘点与迁移映射。
- 每次完成较大的任务后，都要追加一条时间戳记录到 `logs/worklog.md`。
- **全局 PR 审核门禁：任何任务类型都必须通过 GitHub PR 交付并提交 GPT/ChatGPT 审核，包括架构、文档、代码、脚本、迁移、外部数据运行、试运行和配置变更；不得以“只是试运行”或“只改文档”为由绕过 PR。唯一例外见「审核豁免」一节，仅限 `prompts/GPT-Feedback.md` 一个文件。**
- **审核前不得继续推进：GPT/ChatGPT 未对当前 PR 明确给出 `APPROVE` 前，不得进入下一阶段、开始下一项工作、执行依赖该变更的外部运行，或自行扩展/修改范围。**
- **审核反馈后的修改必须留在同一个 PR：收到 `REQUEST_CHANGES` 后，只按当前反馈做最小必要修订，重新验证、更新 handoff/worklog 并再次提交同一 PR；不得另起无关变更或跳过复审。**
- **全程留痕：每一步读取、决策、修改、命令、验证、外部运行、失败、修正、审核反馈和结果都必须带时间戳写入 `logs/worklog.md`；每一个 PR 和每一次外部运行都必须更新 `docs/handoff/`，不以“较大任务”作为豁免条件。**
- 外部数据和结果仍不得进入本仓库；PR 中只能提交可审计的代码/架构契约、manifest、摘要、校验信息和外部路径引用。
- 机器可读 ID、路径和 Schema 名保持英文。
- 面向操作者的说明优先使用中文。

## 审核豁免

全局 PR 审核门禁只有一个例外，由人类负责人于 2026-08-04 授权：

- **`prompts/GPT-Feedback.md` 的改动默认通过，无需 ChatGPT 审核。**

理由：该文件记录的是人类负责人作为审核方与 ChatGPT 对话后确定的反馈需求。它是纯文本反馈记录，不是
架构契约、不是代码、不产生任何决策，因此让审核方去审核自己的反馈没有意义。

### 允许的精确文件集合

豁免 PR 的改动**必须完全落在以下三个路径之内**，一个都不能多：

| 路径 | 数量 | 作用 | 是否豁免 |
|---|---|---|---|
| `prompts/GPT-Feedback.md` | 恰好 1 | 反馈正文，本豁免的对象 | 审核豁免 |
| `logs/worklog.md` | 恰好 1，只允许追加 | 时间戳留痕 | **不豁免**，必须写 |
| `docs/handoff/<日期>-<任务名>.zh-CN.md` | 恰好 1，新增 | 交接备忘 | **不豁免**，必须写 |

**handoff 不在豁免之列。** 本节收窄的是「谁来审核」，不是「要不要留痕」。第 26 条留痕要求、
`docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` 与 `ChatGPT-Codex-talk.md` 中「每个 PR
都必须更新 `docs/handoff/`」一律继续适用，本豁免不修改这些要求。

出现上述三者之外的任何改动——包括 `prompts/` 下其他文件、任何 `.py`、任何契约或 manifest——整个 PR
回落到正常门禁，须提交 ChatGPT 审核。

### 其余边界

任一条不满足即回落到正常门禁：

1. **只限这一个反馈文件。** `prompts/GPT-Feedback.md`，不含 `prompts/` 下任何其他文件。
2. **不豁免留痕。** 仍须走 PR、仍须写 worklog 与 handoff，见上表。豁免的是审核，不是可追溯性。
3. **不豁免实施。** 把该文件里的反馈变成架构、内核、Gate、扩展或代码改动，一律走完整门禁。
   记录反馈 ≠ 获得实施授权，这一点与 `extensions/README.md`「反馈本身不是架构变更授权」一致。
4. **不自我扩展。** 本豁免不适用于修改 `AGENTS.md` 本身，也不适用于扩大本豁免的范围。用「默认通过」
   去改「默认通过」的规则属自我指涉，须由人类负责人单独授权。

本节是该豁免的唯一权威表述。`docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md` 曾记录过一个
更宽的表述（覆盖 handoff、worklog、`prompts/*` 等全部纯文本），那是执行者的过度推广，已被本节收窄取代。

## 遗留文件

- `prompts/GPT-Feedback.md` 是用户反馈，不是 canonical architecture。审核豁免见上一节。
- `architecture.md` 是入口页；正式契约在 `docs/architecture/` 下。
- `ChatGPT-Codex-talk.md` 是 ChatGPT/Codex 的固定交互规范；以后需要“只负责执行、由外部模型审核”时，优先遵守这份文件。
- `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` 是分阶段执行、PR 反复审核和 Phase 放行的独立协作协议；任何复杂任务都必须遵守其 Phase gate。
- 默认审核单位是 PR，不是本地未推送工作区；需要复审时，优先提供 PR diff、commits、report、checklist、manifest 和验证结果。
- 默认任务分支格式是 `task_<编号>_<简短名>`；每个 PR 都要在 `docs/handoff/` 留下交接备忘。
- 提交前必须先运行 `git status --short`，只用 `git add -- <相关文件>`，禁止 `git add .`、`git add -A` 和 `git add --all`。

## 校验

- 在增加新的顶层文件或目录之前，先运行 `scripts/verify_repository_boundary.sh`。
- 不要把数据类文件或数据类目录加进这个仓库。
- 例行 GitHub 同步优先使用 `scripts/git_sync.sh <branch> <commit-message> <相关文件...>`，保证 fetch/rebase/显式暂存/commit/push 流程一致。
- 同步脚本在暂存区非空时必须拒绝执行；脚本行为由 `tests/test_git_sync.sh` 的 A-D 场景验证。
