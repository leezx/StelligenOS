# 任务交接备忘：把 GPT-Feedback.md 审核豁免写入 AGENTS.md 并收窄范围

- 任务编号：`task_20260804_gpt-feedback-waiver`
- 分支：`task_20260804_gpt-feedback-waiver`（从 `main` `3708024` 创建）
- 当前状态：`ROUND_1_REQUEST_CHANGES_ADDRESSED_PENDING_REVIEW`
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
| `AGENTS.md` | 新增「审核豁免」一节（含精确文件集合表）；第 23 条全局门禁加一句指向该节的唯一例外。 |
| `ChatGPT-Codex-talk.md` | 第 1.1 节「任何工作都必须进入 PR 审核流程」一条加上该唯一例外的指针。 |
| `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` | 第 1.1 节全局门禁段后加一段说明该唯一例外。 |
| `docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md` | 在「常设授权」一节**开头插入**更正块。 |

## 收窄后的规则

`AGENTS.md`「审核豁免」一节是唯一权威表述。豁免只有一条：

> `prompts/GPT-Feedback.md` 的改动默认通过，无需 ChatGPT 审核。

### 允许的精确文件集合

豁免 PR 的改动必须完全落在三个路径之内，一个都不能多：

| 路径 | 数量 | 是否豁免 |
|---|---|---|
| `prompts/GPT-Feedback.md` | 恰好 1 | 审核豁免 |
| `logs/worklog.md` | 恰好 1，只追加 | **不豁免**，必须写 |
| `docs/handoff/<日期>-<任务名>.zh-CN.md` | 恰好 1，新增 | **不豁免**，必须写 |

**handoff 不豁免。** 收窄的是「谁来审核」，不是「要不要留痕」。

### 其余四条边界

1. **只限这一个反馈文件**，不含 `prompts/` 下任何其他文件。
2. **不豁免留痕**，仍须走 PR、仍须写 worklog 与 handoff。
3. **不豁免实施**。把该文件的反馈变成架构、内核、Gate、扩展或代码改动，一律走完整门禁。记录反馈
   ≠ 获得实施授权，与 `extensions/README.md`「反馈本身不是架构变更授权」一致。
4. **不自我扩展**，不适用于修改 `AGENTS.md` 本身或扩大本豁免。

第 3、4 条与文件集合表中的「不豁免」列各堵一个实际会出现的口子：

- 文件集合表堵「顺手夹带」。若不把允许集合封闭，只要挂上这个文件名就能把任意改动带进去。PR #49
  正是这种形态的实例。
- 第 3 条堵「记录即授权」。这个文件的历史作用恰恰是驱动重大变更：`# v4` 产生了四个扩展包，`# v5` 直接
  改了内核（PR #45）。若不写明，「反馈已默认通过」很容易被读成「反馈里的方案已获批准」。
- 第 4 条堵自我指涉。

## Round 1 `REQUEST_CHANGES` 与修订

ChatGPT 返回 `REQUEST_CHANGES`，两条治理阻断，均经核实成立，无 pushback。

### 阻断 1：豁免规则自相矛盾，无法合规执行

成立，而且是硬矛盾而非表述不清。初版第 2 条写「该 PR 只能改这一个文件」，但：

| 要求来源 | 内容 |
|---|---|
| `AGENTS.md` 第 26 条 | 每一个 PR 都必须更新 `docs/handoff/` |
| `AGENTS.md`「遗留文件」第 38 行 | 每个 PR 都要在 `docs/handoff/` 留下交接备忘 |
| Phase Gate 协议 1.1 | 每一个 PR 都必须更新 `docs/handoff/`，不以任务大小豁免 |
| `ChatGPT-Codex-talk.md` 1.1 | 每一个 PR 都必须写入 `docs/handoff/` |

初版第 3 条自己还要求写 `logs/worklog.md`。因此「只能改一个文件」与「必须写 worklog」「必须写 handoff」
三者不可能同时满足——该豁免按字面无法执行。初版括注「含 `logs/worklog.md` 之外的任何内容」语义混乱，
既没澄清也没解决。

修订：改为**封闭的三路径集合表**（反馈正文 + worklog + handoff），并明确 **handoff 不在豁免之列**。
选择「允许 handoff」而不是「豁免 handoff」，因为后者需要同时修改上表四处留痕要求，属于扩大范围；而前者
不动任何既有留痕规则，只把允许集合定义清楚。

### 阻断 2：与另外两份治理文本冲突

成立。`ChatGPT-Codex-talk.md` 1.1「任何工作都必须进入 PR 审核流程」与 Phase Gate 协议 1.1「以下工作全部
必须通过 GitHub PR 提交 GPT/ChatGPT 审核」都是无例外表述，与 `AGENTS.md` 新增豁免直接冲突。

修订采取「同步指针」而非「三处复述」：两份文本各加一处指向 `AGENTS.md`「审核豁免」的说明，明确该例外
只豁免审核、不豁免 PR/worklog/handoff。**刻意不复制那五条边界。** 复制会产生三份可各自漂移的副本，而
本次工作中已经出现过完全同型的故障——EXT-02 的版本号写在 `extension.yaml` 与 `contracts.py` 两处且无
一致性约束，结果就漂移了，那正是 PR #48 Round 1 的阻断。

审核给的两个选项（同步例外／明确优先级）中取前者：优先级规则会把两句无例外的绝对表述原样留在文中，
未来读者仍会先撞上矛盾，再去别处找优先级。

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
- 未改动 `ChatGPT-Codex-talk.md` 与 Phase Gate 协议中除 1.1 全局门禁一处之外的任何内容；两处均为加入
  指针，未删改任何既有规则。（本条初版写「未改动」这两份文件，Round 1 修订后已不成立，故更正。）

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
