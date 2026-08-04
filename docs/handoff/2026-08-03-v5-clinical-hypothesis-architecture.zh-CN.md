# v5 Clinical Hypothesis Architecture Handoff

## Status

- Branch: `task_20260803_v5-clinical-hypothesis-architecture`
- Base: `main` at `b474d13`, synchronized with `origin/main` at start
- Review: Round 1 `REQUEST_CHANGES`; remediation is complete and Round 2 approval is required before merge
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

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`: 179 passed
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
