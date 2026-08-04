# v5 Clinical Hypothesis Architecture Handoff

## Status

- Branch: `task_20260803_v5-clinical-hypothesis-architecture`
- Base: `main` at `b474d13`, synchronized with `origin/main` at start
- Review: Round 1/2 `REQUEST_CHANGES`; Round 3 `APPROVE` for head `20a2328`; merge authorization remains with the human owner
- Data boundary: no data, cache, result, model weight, or runtime output added

## What Changed

The v5 revision changes the early development unit from a permanently fixed
`indication-endpoint-target` tuple to:

`Target x Anchor Clinical Context x Intended Benefit/Product Hypothesis`

The repository now exposes data-free contracts for:

- `ClinicalHypothesis`
- `AnchorClinicalContext`
- `IntendedBenefitHypothesis`
- `BiomarkerHypothesis`
- `ProductHypothesis`
- `ClinicalLockState`

`TargetHypothesis` remains in the registry for downstream compatibility.
T0 keeps its frozen Gate identity and topology, but its envelope can carry the
clinical hypothesis references and progressive lock state. Exact protocol
endpoints, final biomarker cutoff, and CDx remain stage-dependent.

## Round 1 Remediation

- `ClinicalHypothesis` now carries the generation-to-validation-to-T12 identity;
  legacy exact indication/endpoint fields remain optional compatibility snapshots.
- Exploratory seeds support `mature-target-first`, `target-context-co-selection`,
  and `clinical-problem-first` without falsely requiring final labels.
- Lock transitions are typed, monotonic, single-step, and state-specific minimum
  fields reject invalid protocol/regulatory states.
- Endpoint semantics now distinguish protocol endpoint, observed performance,
  registrational endpoint, biomarker cutoff status/reference, and CDx status/reference.
- T0 input and output envelopes carry validated hypothesis and lock-state references;
  contract versions were bumped and old positional input ordering was retained.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`: 183 passed
- `bash scripts/verify_repository_boundary.sh`: passed
- `git diff --check`: passed

## Important Working-Tree Note

`prompts/GPT-Feedback.md` contains a user-provided v5 edit and remains
uncommitted intentionally. It must not be reverted or staged as part of the
architecture PR unless explicitly requested.

## Next Steps

1. Stage only the architecture, contract, test, handoff, review record, and worklog files.
2. Commit and push the remediation to the existing PR #45.
3. Submit the PR review instruction in the existing Chrome ChatGPT conversation
   `ADC研发靶点选择`.
4. Apply any further `REQUEST_CHANGES` feedback on the same PR and repeat until
   ChatGPT returns `APPROVE`.
5. Only after approval may the v2 architecture snapshot be created and the
   PR be merged.

## Round 2 Remediation

- `TargetCandidate` now has an explicit `legacy_compatibility` path; the v5
  path can omit exact legacy snapshots but requires `clinical_hypothesis_ref`.
- `TargetOpportunityHandoff` requires hypothesis and lock state as a pair for
  v5; legacy T12 requires an explicit compatibility flag.
- All higher lock-state requirements are cumulative, and the Gate capability
  imports the canonical GenModule `ClinicalLockState`.
- Co-selection exploratory hypotheses require at least one target, anchor, or
  intended-benefit seed; tests instantiate all three entry modes and negative
  higher-state and identity cases.

## Round 3 Approval

- ChatGPT returned `APPROVE` with no blocking findings for head `20a2328`.
- The approval covers the v5 clinical-hypothesis architecture remediation,
  associated tests, contracts, docs, handoff, and audit logs in PR #45.
- No v2 snapshot was created and the PR was not merged by Codex.

## Post-Merge Audit

- Human-authorized PR #45 merge completed through GitHub with approved head `20a2328421c5c5ae25c62569672500f7b112a575`.
- Remote `main` now points to merge commit `a5bf77f0189906e8442902b9953f3080b0afaca3`; its second parent is the approved PR head.
- Local `main` was advanced to `origin/main` without checking it out, preserving intentional audit records and the user's unstaged prompt edit.
- No code, contract, Gate topology, data, cache, result, model weight, or runtime artifact was added after approval.

## Audit Closure (PR C, `task_20260804_pr45-audit-closure`)

The records above were written but never committed. They are committed by PR C,
branched from `main` at `a5bf77f`.

- Gap confirmed: `logs/chatgpt-review-2026-08-03-pr45-round3.md` was an untracked
  file present on no branch. The in-repository review trail for PR #45 therefore
  ended at Round 2 `REQUEST_CHANGES` while head `20a2328` was already the second
  parent of `main`. Any later reviewer would read "REQUEST_CHANGES, then merged".
- GitHub state was inconsistent with the repository: PR #45 showed `open` /
  `merged: false` / `mergeable_state: dirty` because the merge was performed as a
  manual merge commit, which GitHub did not detect. PR #45 is closed with a
  comment naming `a5bf77f` as the merge commit and `20a2328` as the approved head.
- Round 1 and Round 2 records are not rewritten. No existing worklog entry or
  handoff section is rewritten. Append-only audit history is preserved.
- Follow-up work is deliberately **not** in this PR: the `src/` → `genmodules/`
  dependency inversion introduced by v5 is PR A, and the EXT-02 / seven-object
  documentation drift is PR B.
