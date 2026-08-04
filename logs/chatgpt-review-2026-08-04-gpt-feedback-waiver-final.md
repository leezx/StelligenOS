# ChatGPT Review Record: GPT-Feedback.md review waiver into AGENTS.md Final

- Review date: 2026-08-04 EDT
- Pull request: #51
- Approved head: `e9eced830cfc8f093b501edef96f166ceaca0286`
- Base branch: `main`
- Merge commit: `dcc94a7bb8b38650df98c9e8a787d59b8eba9d1b`
- Reviewer: ChatGPT
- Decision: `APPROVE` (Round 3)
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.** The conclusions quoted
  below are reproduced as received, not paraphrased.

## What was reviewed

Two things: writing the human lead's 2026-08-04 review waiver for
`prompts/GPT-Feedback.md` into `AGENTS.md`, and narrowing the over-broad version
of it that the executor had recorded in
`docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md`.

The grant covers one file. The executor had generalised it to
`logs/chatgpt-review-*.md`, `docs/handoff/*`, `logs/worklog.md` and all of
`prompts/*`. That was over-extension, not the grant.

This PR was itself covered by no waiver: the narrowed rule explicitly excludes
amending `AGENTS.md`.

## Review history

### Round 1 — `REQUEST_CHANGES`, two governance blockers

1. **The waiver was literally unsatisfiable.** It said "the PR may touch only
   that file", while four separate rules require every PR to update
   `docs/handoff/` (`AGENTS.md` rule 26 and line 38, Phase Gate protocol 1.1,
   `ChatGPT-Codex-talk.md` 1.1), and its own clause required a worklog entry.
2. **Conflict with the other two governance texts,** both of which state the PR
   review gate without exception.

Corrections: a closed three-path set (feedback body + worklog + handoff), and a
pointer synced into each of the two texts. The boundaries were deliberately not
restated in three places, because three copies are three things free to drift —
the identical failure had already occurred in this same work, with EXT-02's
version living in `extension.yaml` and `contracts.py` untied and drifting, which
was PR #48's Round 1 blocker. Of the review's two options, "sync the exception"
was chosen over "state precedence", since a precedence rule leaves both absolute
sentences standing for a future reader to hit first.

### Round 2 — `REQUEST_CHANGES`, one semantic conflict

Marking exemption per file made the waiver negate itself. The table had an
"是否豁免" column marking `logs/worklog.md` and the handoff as **not exempt**.
Review is per-PR, so if the companion files are not exempt then a PR containing
them needs review — and the same table makes them mandatory. Every compliant
waiver PR would therefore require review.

Root cause: two different axes forced into one column. Review exemption is a
property of the whole PR; the traceability requirement is a property of each file.
"The handoff is required" is true on the traceability axis; writing it as "the
handoff is not exempt" put it on the review axis, where it means something else.

Corrections: the column became **角色**, valued 反馈正文 or 必需的配套审计文件;
an explicit statement that the presence of worklog and handoff does not trigger
the review gate, bounded by what they may contain; and every remaining `不豁免`
phrasing rewritten so "exempt" applies only at PR level, including the two
pointers, which carried the same mixed axes.

### Round 3 — `APPROVE`

> APPROVE
>
> 上一轮语义冲突已消除：
>
> * 审核豁免明确以整个 PR 为单位。
> * worklog 和 handoff 被定义为必需配套审计文件，不会重新触发审核门。
> * 三文件集合及内容范围封闭，无夹带漏洞。
> * AGENTS.md、ChatGPT-Codex-talk.md 和 Phase Gate 协议表述一致。
> * 当前 HEAD e9eced8 mergeable；CI run #5 的 Python 3.11/3.12 全部检查通过，共 207 tests。
>
> 可以合并 PR #51。

## The rule as approved

`AGENTS.md` `## 审核豁免` is the single authoritative statement. Review exemption
applies to the **whole PR**, and a waiver PR's changes must fall entirely within
three paths:

| Path | Count and form | Role |
|---|---|---|
| `prompts/GPT-Feedback.md` | exactly 1 | the feedback body |
| `logs/worklog.md` | exactly 1, one timestamped entry appended | required companion audit file |
| `docs/handoff/<date>-<task>.zh-CN.md` | exactly 1, new file | required companion audit file |

The companion files' presence does not trigger the review gate, but they may carry
only the prescribed content. Four further boundaries: that feedback path only;
traceability unchanged; implementing the feedback is not covered; and the waiver
cannot amend itself.

## How the stale record was handled

A correction block was **inserted before** the original text in the merged
handoff, with nothing deleted. Appending only at the end would leave a reader
stopping at a boundary table no longer in force — a superseded *operational rule*
left unmarked is actively harmful, unlike a superseded fact.

That block also records, without ratifying it, that PR #49 contained three audit
records and a handoff, which under the narrowed rule fall outside the waiver and
should have been submitted for review.

## Scope of this approval

Approved:

- The `## 审核豁免` section of `AGENTS.md` as written, including the closed
  three-path set and the four boundaries.
- The exception pointers in `ChatGPT-Codex-talk.md` 1.1 and
  `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md` 1.1.
- The inserted correction block in
  `docs/handoff/2026-08-04-audit-records-and-v5-source.zh-CN.md`.
- Merging PR #51 into `main`.

Not authorized by this approval:

- Widening the waiver, adding paths to the three-path set, or applying it to any
  file other than `prompts/GPT-Feedback.md`.
- Treating a recorded feedback update as authorisation to implement it. Turning
  that file's contents into architecture, kernel, Gate, extension or code changes
  goes through the full gate.
- Retroactive ratification of PR #49, which was merged under the over-broad
  wording.
- Any code, contract, Gate topology, Model, Profile, lifecycle or test change.
  None was made.

## Known structural weaknesses, recorded not fixed

- **No test guards `AGENTS.md`.** Nothing in the repository asserts its content,
  so this section being widened or deleted later would raise no alarm — unlike the
  45-Gate topology or extension statuses, which are test-locked.
- **The three-path limit relies on executor discipline.** CI cannot tell whether a
  PR claims the waiver, so nothing mechanically enforces the closed file set.
  Enforcing it would require CI-side inspection of the changed file set.

Both are open items for separate tasks and were stated in the PR rather than left
implicit.
