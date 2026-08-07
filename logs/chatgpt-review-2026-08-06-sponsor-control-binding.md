# ChatGPT Review Record: Sponsor Control Binding (BinderAdcRouteRequest@0.2.0)

- Review date: 2026-08-06 EDT
- Pull request: #72
- Approved head: `a1b30d6655ded743a68b35786dc4365dc1948939`
- Base branch: `main`
- Merge commit: `4d895d7`
- Reviewer: ChatGPT
- Decision: `APPROVE`
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.** The conclusions quoted
  below are reproduced as received, not paraphrased.
- GitHub review record: **none.** As in the previous rounds, no formal review was
  written back to GitHub. This file is the only durable record of the decision.
- **Why this record is filed in a later PR:** the approval arrived after the PR
  content had been frozen. Adding a record file to `a1b30d6` would have changed
  the very head the reviewer approved, so the record is filed here instead. The
  merge commit `4d895d7` carries the same scope statement.

## Review history

- **Round 1 — `APPROVE` at `4d895e2`.** The reviewer approved the initial
  binding and recorded one non-blocking item: validation strength was asymmetric,
  because only the three sponsor-control fields required a non-empty
  `external:` reference while the five existing fields did not.
- **Round 2 — `APPROVE` at `a1b30d6`.** Recorded below. The revision closed four
  gaps found by checking the delivered PR line by line against the reviewer's
  own guidance, including the non-blocking item from Round 1.

## Reviewer's verification, as relayed

- PR open, non-draft, mergeable; CI run #70 passed on Python 3.11 and 3.12
- unit tests, `git_sync` behaviour tests, repository boundary, no bytecode
  artifacts and working-tree-unchanged all succeeded
- `REQUIRED_REQUEST_REFERENCE_FIELDS` covers all eight request references
- non-strings, empty strings, `external:`, `external:   ` and `local:*` are now
  uniformly rejected
- the three sponsor-control fields sit between other mandatory fields, so giving
  any of them a default violates dataclass argument ordering and fails earlier
  than a runtime check
- the three fields remain mandatory, default-free and opaque external refs
- `field_presence_is_not_a_decision: true`, and `MONITOR`,
  `DATA_PACKAGE_ONLY`, `STOP_FOR_SPONSOR` stay blocked
- `genmodules/README.md` documents the consumer-facing effect of the breaking
  request contract without amounting to a v4 refresh
- added tests cover uniform validation, the `str()`-impostor object, no
  `BinderAdcRouteResult` creation, no lifecycle module change, no repository
  write, YAML/code list equality, and the literal field roster that prevents the
  parameterised tests from self-shrinking

## Accepted conclusion, as stated by the reviewer

> 最新 HEAD 比上一轮更完整，没有引入新的阻断问题。

## Scope of approval, as stated by the reviewer

> 将 Phase 3–4 hard controls 作为 BinderAdcRouteRequest@0.2.0 的强制、非空、
> external-only 前置引用，并统一现有 request reference 校验。

## The boundary the reviewer explicitly accepted

The repository verifies only that an authorization reference exists. It does not
read the Program Commitment outcome. The release judgement stays with the
external human-governance layer that produces
`asset_generation_authorization_ref`. The reviewer stated this rules out the
failure mode:

> 只要提供任意 ProgramCommitmentReview ref，就自动允许 Asset Generation。

## What this approval does not do, as stated by the reviewer

No import of `ProgramCommitmentReview` or `ValueInflectionPlan`; no reading or
deserialising of external instances; no commitment-outcome judgement; no
authorization generation; no automatic binder/de novo route selection; no Asset
Generation; no change to T12, the 45 Gates, lifecycle or core objects; no
architecture document refresh; no data, cache, result, database or model weights.

## Next step, as stated by the reviewer

> 合并后开始架构 v4 refresh
