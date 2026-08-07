# ChatGPT Review Record: ADC Pool Level 01 Preview result

- Review date: 2026-08-05 EDT
- Pull request: #60
- Approved head: `25d233a795c228ff40d9090dbb9a583413bc3e8c`
  (`Merge remote-tracking branch 'origin/main'`)
- Base branch: `main`
- Merge commit: `8aa7e87`
- Merged at: 2026-08-05T18:52:51Z
- Reviewer: ChatGPT
- Decision: two rounds of `REQUEST_CHANGES`; final `APPROVE` of **revision 2**
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

**Product status: `PROVISIONAL_NOT_AUTHORIZED_FOR_ADVANCEMENT`.**

This is not a formal Level 01 execution result. It may not be used as Gate
input, may not enter Level 02, and may not ground an asset decision.
`ADC_POOL_LEVEL_01_ACCEPTED` requires five further approvals: `SRCADM-01`, the
`EVGAP-01` extraction result and its binding, and the `EVGAP-02` extraction
result and its binding.

Merge commit `8aa7e87` was the repository baseline cited by architecture
document `v3-draft`.

## Why every figure is provisional

The Preview read `ADC_surfaceome_reference@0.3.0`, **which had not passed
review** — `SRCADM-01` was incomplete and #59's `admission_record_ref` was
empty. That is exactly why the 22 targets could only be marked
`provisional_surface_eligible` rather than `eligible_surface_target`. The
manifest records that source as `NOT_ADMITTED_PENDING_SRCADM_01`. The only
approved source was `gen_iet_crc_target_enumeration_20260802` (PR #29). #53 and
#54 were listed as `barred_inputs` with `used: false`.

## Round 1 — `REQUEST_CHANGES`, two blockers, both accepted

Recorded at `logs/worklog.md` 2026-08-05T14:10:00-04:00. The reviewer confirmed
the whole reconciliation section correct — 9/41/369 with no duplicates, 22/19,
22/347, `LOCK-03` 369/369 `unresolved`, `may_advance_to_level_02=false` 369/369,
no active pair, six manifest hashes matching the uploaded package, #53/#54 still
listed as barred inputs, no Gate score, ranking or asset recommendation — and
then raised two blockers. The worklog records that **both were the executor's
own errors**.

The first is recorded in detail: the generation logic was **inverted**. The code
read `"EVGAP-02" if in_index else "EVGAP-01;EVGAP-02"` — but it is precisely
those 22 in-index pairs whose `LOCK-01` status came from the not-yet-admitted
`ADC_surfaceome_reference@0.3.0`, so they are the ones that most needed to carry
`EVGAP-01` as well.

## Round 2 — `REQUEST_CHANGES`: the delivered package was the wrong revision

Recorded at 2026-08-05T15:05:00-04:00. The reviewer stated explicitly that this
was **not a claim the fix was still wrong, but that the actual result package
under review was the wrong version** — the uploaded ZIP was still revision 1:
22 rows still carried only `EVGAP-02`, `raw_clinical_contexts.tsv` still lacked
`may_advance_to_level_02`, `raw_enumeration_matrix.tsv` still lacked two
columns, and `source_manifest.json` had no `revision: 2`. The reviewer confirmed
the PR-level fix itself was correct.

## The rule this round established, and its effect on later work

From this ruling on, **every delivery of an external product must ship a
checksummed package, and every revision gets its own package with its own
SHA-256.** The worklog shows this rule being applied by name in the later
`EVGAP-02` deliveries, and it is the direct ancestor of the in-package
`verify_package.py` used for #62 and the `verify_audit.py` used for #63.

## An executor mistake recorded rather than concealed

While switching branches to handle this PR, `git stash -u` swept the uncommitted
YAML fixes for blockers 1 and 2 into the stash; they were not restored after
switching back, so later edits landed on an unrevised version and tests raised
`KeyError`. Recovered from `stash@{0}` with all 133 lines restored and no
content lost. The lesson recorded at the time: before handling another PR on a
different branch, commit or explicitly note uncommitted work, and restore it
first thing on return.

## Accepted conclusion, as supported by the surviving evidence

Revision 2 was approved and merged as `8aa7e87`. The reviewer's own approval
wording is lost.
