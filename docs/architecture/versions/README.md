# 架构文档版本规则

## 目的

在不破坏既有引用和审计轨迹的前提下，为架构说明文档建立版本概念。

## 规则

1. **规范路径永不改名。** 每份架构说明文档在 `docs/architecture/` 下只有一个规范路径，永远指向最新版本。禁止把版本号写进规范路径的文件名。
2. **版本号写在文档内部。** 每份文档的第 0 节记录 `文档 ID`、`当前版本`、`版本状态` 和历史快照位置。
3. **冻结快照放在本目录。** 当某个版本被 ChatGPT `APPROVE` 且需要长期保留时，把该版本完整复制到本目录，命名为 `<DOC_ID>.v<N>.zh-CN.md`。
4. **文件名禁止空格。** 只允许 `A-Z`、`a-z`、`0-9`、`_`、`.`、`-`。
5. **快照只读。** 本目录下的文件一旦提交就不再修改；修订只发生在规范路径上，然后再产出新的快照。

## 为什么不用「文件名带版本号」

`logs/worklog.md` 和 `logs/chatgpt-review-*.md` 是带时间戳的追加式审计记录，`docs/handoff/` 记录每个 PR 的交接事实。这些文件引用的是文档被审核时的路径。如果把版本号写进规范路径的文件名，每次升版都必须回头改写已经被 ChatGPT 批准过的历史记录，这会破坏审计轨迹的不可变性。

因此版本概念通过「稳定规范路径 + 文档内版本区块 + 只读快照」表达，而不是通过重命名。

## 快照与规范路径的关系

快照保存的是被审核时的正文。规范路径上的同一版本会多出第 0 节版本区块——那是版本元数据，不是架构内容。因此「规范路径当前版本 = vN」与「快照 vN」之间允许存在且仅存在这一处元数据差异；正文一旦出现实质改动，就必须升到 `v(N+1)` 并产出新快照。

## 当前快照

| 文档 ID | 版本 | 快照 | 审核状态 |
|---|---|---|---|
| `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW` | `v1` | `CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.v1.zh-CN.md` | PR #42 `APPROVE` |

`v2-draft` was not approved or snapshotted and has been superseded by the
canonical `v3-draft` review baseline. `v3-draft` must not be copied into this
directory until its dedicated expert/ChatGPT review returns `APPROVE`.
