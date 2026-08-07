# ChatGPT Review Record: EVGAP-02 CRC-specific linkage evidence extraction contract

- Review date: 2026-08-05 EDT
- Pull request: #61
- Approved head: `57cb10b8043cf140c80c5592f0e9eb10421a8bee`
- Final head: same
- Base branch: `main`
- Merge commit: `6422b5c`
- Merged at: 2026-08-05T17:27:02Z
- Reviewer: ChatGPT
- Decision: `REQUEST_CHANGES` (three blockers, all accepted); final `APPROVE`
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

Contract only, version `0.1.0`. **One extraction may be executed after
approval.** It does not authorise Level 01 execution and does not lift
`EVGAP-01`.

Unlike `EVGAP-01`, this contract needed no admission first. The reason, drawn
from the #59 review's own distinction: **Tier 1 primary public sources are not
derived databases.** PubMed/PMC, ClinicalTrials.gov, TCGA/GEO/HPA plus the
approved enumeration axis (PR #29) can be traced by `source_locator` straight
back to the original record, so the question "does the build logic obey its own
declaration" does not arise.

## Round 1 — `REQUEST_CHANGES`, three blockers, all accepted

Recorded at `logs/worklog.md` 2026-08-05T15:40:00-04:00. CI passed but
`mergeable=false` at the time. The final head `57cb10b` is titled
`close the class-D and evidence-reference gaps in PR #61`.

## What this contract later authorised, and what went wrong with it

The worklog records the human lead's instruction to run `EVGAP-02` first, with
the authority being this merged contract, whose `blocked_by: [contract_approval]`
was now satisfied.

That extraction was performed and submitted as PR #62 — and was blocked. The
reviewer found that the run had registered **search hits as linkage evidence**:
all 7,067 rows carried `evidence_direction=unknown` yet produced 168 RETAIN and
9 EXCLUDE.

The root cause was **in this contract**, not in the run. Version `0.1.0`
required `evidence_direction` as a column but never required it to be
*resolved*, and left `linkage_class` unconstrained, so it came from the query
category. A fully compliant execution therefore produced 168 RETAIN.

The fix was made in the contract, not the run: version `0.2.0` (PR #62) added
the three-layer model, assertion requirements, identity resolution, per-endpoint
admissibility and `VAL-L21`..`VAL-L29`, and the completed run was downgraded to
an `L-RETRIEVAL` product. This record notes the defect against `0.1.0` because
the contract approved here is where it originated.

## Accepted conclusion, as supported by the surviving evidence

Approved and merged as `6422b5c`. The reviewer's own approval wording is lost.
