# ChatGPT Review Record: ADC Pool Level 01 input binding contract

- Review date: 2026-08-04 EDT (merged 2026-08-05T01:28:11Z, i.e. 21:28 EDT)
- Pull request: #58
- Approved head: `fc87a620d8fabce2a0e4d6a79f1e38034dd2abea`
- Final head: same
- Base branch: `main`
- Merge commit: `cd0e041`
- Reviewer: ChatGPT
- Decision: three rounds of `REQUEST_CHANGES`; final `APPROVE`
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

## Scope as finally approved

**Raw-axis binding only. Level 01 execution is not authorised.** The PR was
downgraded to this scope after round 2; `authorises_level_01_execution` is
`false`.

Bound axes: 9 clinical contexts (36 endpoint rows), 41 targets, 369 raw pairs.

| Approved source | Approval | Contributes |
|---|---|---|
| `gen_iet_crc_target_enumeration_20260802` | #29 `APPROVE` | raw contexts, raw targets |
| `gen_iet_crc_target_evidence_20260801T2235EDT` | #31 `APPROVE` | linkage evidence (292 units, 41 genes) |

## Round 1 — `REQUEST_CHANGES`, two blockers, both accepted

Two engineering defects. Fixed in the same PR with no unrelated changes. The
executor also self-reported a third error found while fixing. Recorded in
`logs/worklog.md` at 2026-08-04T20:05:00-04:00.

## Round 2 — `REQUEST_CHANGES`, two scientific-semantics blockers, both accepted

The reviewer confirmed round 1's engineering fixes were correct — the 36→9
projection made deterministic, `LOCK-01` no longer inheriting the old
disposition and gaining a mapping, input isolation, SHA, DATA boundary and tests
all correct — but exposed two **more fundamental** problems. Recorded at
2026-08-04T20:45:00-04:00. This round is what downgraded the PR to
`raw_axis_binding_only`.

The two gaps registered by this round became `EVGAP-01` and `EVGAP-02`.

## Round 3 — `REQUEST_CHANGES`, one residual contradiction, accepted

The reviewer confirmed round 2's two scientific-semantics problems were
correctly fixed, accepted the downgrade to `raw_axis_binding_only` with
`authorises_level_01_execution: false`, and confirmed `EVGAP-01`/`EVGAP-02` were
adequate as the scope basis for two later controlled extraction contracts. One
residual contradiction remained: stale counts in `VAL-B07`. Recorded at
2026-08-04T21:10:00-04:00. The final head `fc87a62` is titled
`fix VAL-B07 stale counts and lock the three-way agreement`.

## What the projected result shape meant

Raw Enumeration Matrix 369; context eligible 1 / hold 8; target eligible 0 /
hold 41 / killed 0; Eligible Universe Index 0; Pool Level 01 active 0.

The handoff states plainly what this is: **not the expected product of an
authorised run, but the reason not to authorise execution.**

## Accepted conclusion, as supported by the surviving evidence

Approved and merged as `cd0e041`. #59, #60 and #61 each cite #58 as an approved,
merged prerequisite. The reviewer's own approval wording is lost.
