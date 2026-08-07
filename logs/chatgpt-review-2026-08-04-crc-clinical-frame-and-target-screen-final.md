# ChatGPT Review Record: CRC clinical frame and membrane target screen run

- Review date: 2026-08-04 EDT
- Pull request: #53
- Approved head: `5318ecad9d1e6f6d048869876c87823570f1a9b8`
- Final head: same
- Base branch: `main`
- Merge commit: `09990c8`
- Merged at: 2026-08-04T22:09:00Z
- Reviewer: ChatGPT
- Decision: Round 1 `REQUEST_CHANGES`; final `APPROVE` of the **quarantine
  revision only**
- Backfilled on: 2026-08-06, in the nine-record backfill PR

- Record type: **`reconstructed_secondary`.** The reviewer's final approval text
  for this PR is **not recoverable**. It was never written to GitHub, never
  relayed into `logs/`, and no verbatim copy survives in the repository. This
  record is reconstructed from `docs/handoff/`, `logs/worklog.md`, the PR
  metadata and the git history, all of which are cited below.
- **Do not read the "Accepted conclusion" section as the reviewer's words.** It
  states what the surviving evidence supports, which is narrower: that an
  approval was given and the PR was merged. Where a round's blocking findings
  were recorded contemporaneously, they are marked as such and are first-hand.
- GitHub review record: **none.** `gh pr view --json reviews` returns empty for
  this PR.

## What was approved, and what was not

This is the record most open to misreading, so it is stated first.

**The external run this PR documents was never accepted.** Its status is
`UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`. What was approved is the *quarantine
revision* — the audit trail that records the run as rejected. Merging #53 did
not license any of its scientific content.

## Round 1 — `REQUEST_CHANGES`, four blockers, all accepted

Recorded contemporaneously in `docs/handoff/2026-08-04-crc-clinical-frame-and-membrane-target-screen.zh-CN.md`,
which quotes them at the top of the file with the original text kept beneath,
unaltered. These four are **first-hand**:

1. The external screen ran with no authorizing PR, and ran while #52 was still
   unapproved. "开始做内容" is not the scoped run authorization the rules
   require; approving it after the fact would open a do-first-review-later hole
   in the gate.
2. The run **widened existing scope** (9 to 20 scenarios, 41 to 45 targets) and
   produced actual RETAIN/DEFER/EXCLUDE results. It was not mere reading or
   tidying.
3. The audit material lacked per-file SHA-256, so no exact result version could
   be pinned to the review.
4. The claim that unverified model domain knowledge suffices to support ranking
   **does not hold**. At most it supports forming hypotheses to be tested.

## Content explicitly not accepted

- every RETAIN/DEFER/EXCLUDE disposition in `membrane_target_screen.tsv`
- every scientific conclusion in `run_report.md`, including payload-class
  conclusions, Tier A selection, and the proposed anchor hypothesis
- the 20 unmet-need scenarios, seven benefit rankings and twelve endpoint
  thresholds

## The correction made under blocker 4

The original text said the model knowledge was "足以支撑排序与定框". That was
wrong and was corrected, not softened, to: it suffices only to form hypotheses
to be tested, and does not support formal screening or ranking. The reasoning
recorded at the time: ranking asserts a relation *between* candidates, and an
unverified input cannot establish such a relation — it can only propose which
relations are worth testing.

## Accepted conclusion, as supported by the surviving evidence

The quarantine revision was approved and merged as `09990c8`. The reviewer's own
approval wording is lost. Downstream contracts (#57, #58) continued to list this
run in `barred_sources`, which is consistent with the run never having been
accepted.

## Branch incident recorded against this PR

A commit by the human lead (`108931b`, the `target_safety_therapeutic_window_prescreen`
GenModule, 684 lines) landed on **#53's branch** rather than a fresh branch off
`origin/main`. PR #55 was then opened on a second branch pointing at the same
commit, making #53 and #55 identical in content and mixing unrelated code into a
PR that was under `REQUEST_CHANGES`. This was resolved by splitting the branches
with the human lead's authorization. See `docs/handoff/2026-08-04-adc-seed-playbook-v0.1.zh-CN.md`
appendix C for the full account. PR #55 was later closed as superseded by #56.
