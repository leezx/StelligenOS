# ChatGPT Review Record: EVGAP-01 target surface localization extraction contract

- Review date: 2026-08-05 EDT
- Pull request: #59
- Approved head: `cfc8c594c993d444b93683b37eed1ca71973a3d8`
- Final head: same
- Base branch: `main`
- Merge commit: `e30a430`
- Merged at: 2026-08-05T15:47:51Z
- Reviewer: ChatGPT
- Decision: two rounds of `REQUEST_CHANGES`; final `APPROVE`
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

Contract only. **Extraction is not authorised** — it is blocked pending
`SRCADM-01`.

`EVGAP-01` is one of the two gaps registered by #58. It blocks `LOCK-01`: the
approved evidence layer holds no protein-level plasma-membrane localization or
extracellular-domain evidence, so all 41 targets DEFER, `eligible = 0`, and
Level 01 can admit no pair.

## The finding that made this PR necessary

The needed data was already on local disk — and **that database had never been
approved**. No `logs/chatgpt-review-*.md` mentioned surfaceome at all; the only
worklog mention was a 2026-08-01 mock run. The approved evidence extraction
(PR #31) declared `ADC_internalization_reference` as its source and never
connected this library.

That explains something previously unexplained: **why the approved layer had
only transmembrane-segment annotation.** Not that the data did not exist — it
had never been connected.

## Round 1 — `REQUEST_CHANGES`, four blockers, all accepted

Recorded at `logs/worklog.md` 2026-08-05T00:20:00-04:00. The decisive one:
**a derived database cannot be admitted on self-declaration plus a hash.**
Admission was split out as an independent dependency, `SRCADM-01`; this contract
may only cite it, never grant it. The draft's original request to admit the
database directly was struck, and the pre-ruling text was deliberately kept in
the handoff so the before/after difference stays visible.

The other three: the contract no longer authorises extraction; `RQ-02`'s two
counts separated; reference-absent provenance distinguished from source
provenance; precedence frozen and covering multi-condition overlap.

## Round 2 — `REQUEST_CHANGES`, two contract gaps, both accepted

Recorded at 2026-08-05T01:05:00-04:00. The reviewer confirmed round 1's four
were substantially fixed, then identified two **contract gaps** — described in
the worklog as holes the executor had left. The final head `cfc8c59` is titled
`close the RQ-03 rule gap and the absence-column gap in PR #59`.

## What this contract froze, and what later depended on it

- the `E1-05` → `E1-04` → `E1-04b` → `E1-03` → `E1-02` → `E1-01` precedence,
  later confirmed by the #60 Preview to hit exactly one rule per target with the
  measured distribution 22/6/3/6/**0**/4, **matching this contract's
  `predicted_result_shape` item by item**
- the field whitelist that later became admission condition `COND-02`
- the `AUD-01`..`AUD-09` audit scope that became the authorisation for
  `SRCADM-01`

## Accepted conclusion, as supported by the surviving evidence

Approved and merged as `e30a430`. The reviewer's own approval wording is lost.
