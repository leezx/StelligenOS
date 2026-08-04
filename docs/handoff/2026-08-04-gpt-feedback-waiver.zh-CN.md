# 任务交接备忘：把 GPT-Feedback.md 审核豁免写入 AGENTS.md 并收窄范围

- 任务编号：`task_20260804_gpt-feedback-waiver`
- 分支：`task_20260804_gpt-feedback-waiver`（从 `main` `3708024` 创建）
- 当前状态：`PENDING_CHATGPT_REVIEW`
- 变更性质：治理规则（`AGENTS.md`）+ 一处审计更正
- 代码变更：`NO_CODE_CHANGE`
- Gate 变更：`NO_GATE_CHANGE`

**本 PR 不适用任何豁免，须经 ChatGPT `APPROVE` 后方可合并。** 收窄后的豁免明确排除对 `AGENTS.md` 自身
的修改——用「默认通过」去改「默认通过」的规则属自我指涉。

## 要解决的问题

两件事，一件是补，一件是改错。

**补：** 人类负责人于 2026-08-04 授权 `prompts/GPT-Feedback.md` 的改动无需审核，但该授权此前只写在
`docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md` 与 `logs/worklog.md`，未进入
`AGENTS.md`。`AGENTS.md` 是每个会话实际读取的治理契约，因此该授权对未来会话不可发现——下一个会话仍会
按第 23 条门禁把这类改动送审，授权等于失效。

**改错：** 上述 handoff 中的授权范围表述**过宽，不是人类负责人的原意**。原意只针对
`prompts/GPT-Feedback.md` 一个文件，理由是该文件记录的是其作为审核方与 ChatGPT 对话后确定的反馈需求，
是纯文本反馈记录；而执行者把它推广成了「`logs/chatgpt-review-*.md`、`docs/handoff/*`、`logs/worklog.md`、
`prompts/*` 等全部纯文本」。这是执行者的过度推广，不是授权内容。

## 变更

| 文件 | 变更 |
|---|---|
| `AGENTS.md` | 新增「审核豁免」一节；第 23 条全局门禁加一句指向该节的唯一例外。 |
| `docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md` | 在「常设授权」一节**开头插入**更正块。 |

## 收窄后的规则

`AGENTS.md`「审核豁免」一节是唯一权威表述。豁免只有一条：

> `prompts/GPT-Feedback.md` 的改动默认通过，无需 ChatGPT 审核。

配五条边界，任一条不满足即回落正常门禁：

1. **只限这一个路径**，不含 `prompts/` 下任何其他文件。
2. **该 PR 只能改这一个文件**，出现其他文件改动则整个 PR 回落。
3. **不豁免留痕**，仍须走 PR、仍须写 worklog。豁免的是审核，不是可追溯性。
4. **不豁免实施**。把该文件的反馈变成架构、内核、Gate、扩展或代码改动，一律走完整门禁。记录反馈
   ≠ 获得实施授权，与 `extensions/README.md`「反馈本身不是架构变更授权」一致。
5. **不自我扩展**，不适用于修改 `AGENTS.md` 本身或扩大本豁免。

第 2、4、5 条是刻意加的，各自堵一个实际会出现的口子：

- 第 2 条堵「顺手夹带」。若允许同一 PR 兼含其他文件，只要挂上这个文件名就能把任意改动带进去。PR #49
  正是这种形态的实例。
- 第 4 条堵「记录即授权」。这个文件的历史作用恰恰是驱动重大变更：`# v4` 产生了四个扩展包，`# v5` 直接
  改了内核（PR #45）。若不写明，「反馈已默认通过」很容易被读成「反馈里的方案已获批准」。
- 第 5 条堵自我指涉。

## 关于那处更正的做法

采用**在原文之前插入更正块**，原文一字未删。理由：该 handoff 是已合并的带时间戳审计记录，按追加式审计
不可变原则不得改写；但若只在文末追加，读者读到那张边界表就会停下，并可能据以执行——一条已失效的执行
规则留在原位不加标注是有实际危害的。插入是增量而非隐藏，原始表述与其失效事实同时可见。

更正块中同时如实记录了一件事：**PR #49 本身包含三份审计记录与 handoff，按收窄后的规则不在豁免范围内，
当时应当送审。** 该事实照实写，不作追认。

## 明确未改动

- 未改动任何代码、契约、Gate 拓扑、Model、Profile、生命周期、核心对象或测试。
- 未改动 `prompts/GPT-Feedback.md` 本身。
- 未改动 `AGENTS.md` 的硬性边界、留痕要求、`git add` 禁令或校验一节。
- 未删改 `docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md` 的任何原有文字。
- 未改写 `logs/worklog.md` 中记录旧宽表述的那条历史条目；本次以新条目追加更正。
- 未改动 `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` 与 `ChatGPT-Codex-talk.md`。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 192 tests —— OK
      （不是 207：PR #50 新增的 15 项边界测试尚未合并进 `main`，本分支从 `main` 创建）

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.

命令：git diff --check
结果：通过

git diff -- prompts/GPT-Feedback.md：空（本 PR 未改动该文件）
原 handoff 原有文字：逐字保留，仅在节首插入更正块
```

## 未决问题与风险

- `AGENTS.md` 无测试守卫。仓库内没有任何测试断言其内容，因此「审核豁免」一节将来被改宽或删除不会有
  任何机制报警。这与 45-Gate 拓扑、扩展状态等已被测试锁定的对象形成对比。是否要给治理文档加守卫测试，
  建议由人类负责人决定后另立任务。
- 豁免依赖执行者自觉遵守第 2 条（该 PR 只能改这一个文件）。技术上无强制手段——CI 不区分 PR 是否声明
  豁免。若要强制，需要 CI 侧判断改动文件集，属另一项任务。
- 52 个已合并分支仍未清理；分支删除属破坏性操作，须人类负责人明确授权。
- PR #50（CI 与依赖声明）仍在待审，与本 PR 互相独立，均从 `main` `3708024` 创建；两者都追加
  `logs/worklog.md`，合并时会出现追加式冲突，按时间戳顺序保留两侧即可。

## 下一步

- 提交 ChatGPT 审核本 PR。获 `APPROVE` 后由人类负责人决定合并。
- 合并后，`prompts/GPT-Feedback.md` 的单文件改动即可按 `AGENTS.md`「审核豁免」直接提交，无需送审；
  其余一切照旧。
