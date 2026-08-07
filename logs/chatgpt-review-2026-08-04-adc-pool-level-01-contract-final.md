# ChatGPT Review Record: ADC Pool funnel Level 01 definition and execution contract

- Review date: 2026-08-04 EDT
- Pull request: #57
- Approved head: `6036c01` (`address PR #57 review, both blockers accepted`)
- Final head: `3de86a617910878413087cb88f2052741fc48b64`
  (`Merge remote-tracking branch 'origin/main'`; difference from the approved
  head is only `main` being merged in)
- Base branch: `main`
- Merge commit: `5e0458b`
- Merged at: 2026-08-04T23:14:55Z
- Reviewer: ChatGPT
- Decision: Round 1 `REQUEST_CHANGES`; final `APPROVE`
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

## Why this PR exists

It is the direct consequence of the #53/#54 quarantine rulings. Those rulings
required the order: **a contract-only PR freezing scope, semantics, evidence
standards and output validation → `APPROVE` → only then run.** This PR is that
prerequisite contract for Level 01.

It delivers the **definition and execution contract** for Level 01. It does not
execute Level 01. The candidate pool is data and stays in the external
workspace; the repository freezes only the identity, order and semantics of the
criteria.

## Round 1 — `REQUEST_CHANGES`, two blockers, both accepted

Recorded contemporaneously in section 12 of
`docs/handoff/2026-08-04-adc-pool-level-01.zh-CN.md`. Both were noted at the
time as changing real run semantics rather than wording. The handoff also
records that `DEVIATION-01` — splitting the source document's
`weak_or_redundant_context` into `redundant_context` (EXCLUDE) and
`weak_context` (DEFER) — **was accepted in round 1**.

## Mutation testing performed on this PR

Fifteen mutations across two rounds (5 in the first, 10 in the review round),
each confirmed caught, then rolled back precisely, with `diff -q` against the
backup clean and tests back to `OK`. Examples recorded: changing
`borrowed_gate_cost_tier` from `low` to `medium`; allowing RNA to satisfy
`LOCK-01`; deleting `transaction_readiness` from `gates_not_run`; moving a
pair-level lock to first in `run_order`; deleting an EXCLUDE's
`exclusion_basis`.

## Blockers this PR recorded

- `BLOCK-01`: Level 01 must not execute before this contract is approved.
- `BLOCK-02`: `LOCK-02` needs a CRC clinical context list.

## A subsequent correction to this PR's own text, made in #58 and not written back

`BLOCK-02` as merged says the only context enumeration came from the quarantined
2026-08-04 run. **That sentence is inaccurate.** The 2026-08-02 enumeration had
already been approved in **PR #29** — whose record explicitly says "Authorized:
use external enumeration output as input to a new target-level evidence
extraction task" — and target-level evidence extraction was approved in
**PR #31**. A complete, non-quarantined input chain existed.

The correct statement is "the products of that 2026-08-04 run may not be used",
not "no usable context exists". The executor over-generalised "quarantined" into
"no usable input".

**Consequence: no new enumeration run was needed**, reducing the planned "two
contracts plus two runs" to "one contract plus one Level 01 execution".

Per the standing rule, the approved historical text in #57 was **not rewritten**;
the correction lives in #58 and is repeated here.

## Accepted conclusion, as supported by the surviving evidence

The contract was approved and merged as `5e0458b`. Downstream PRs (#58, #59,
#60, #61) each open by citing #57 as an approved and merged prerequisite, which
corroborates the approval. The reviewer's own wording is lost.
