# ChatGPT Review: PR #45 Round 1

- Conversation: `ADC研发靶点选择`
- PR: https://github.com/leezx/StelligenOS/pull/45
- Result: `REQUEST_CHANGES`
- Review method: Chrome ChatGPT GitHub connector, PR diff and repository files

## Blocking Findings

1. `ClinicalHypothesis` was only parallel to the old chain. `OpportunitySearchScope`,
   `ClinicalFrame`, `TargetCandidate`, and `TargetOpportunityHandoff` still made
   exact indication/endpoint the primary identity. The handoff lacked
   `clinical_hypothesis_ref` and lock state.
2. `ClinicalLockState` was only an enum. There was no transition function,
   monotonicity check, stage minimum, lifecycle mapping, provenance contract,
   or invalid-state rejection.
3. Endpoint and biomarker timing was under-modeled. The contracts lacked
   protocol endpoint, observed performance, cutoff status, final cutoff ref,
   CDx status, and CDx ref semantics.
4. The three entry modes existed only in prose. All five hypothesis refs were
   required from creation, making mature-target-first and clinical-problem-first
   impossible to represent in exploratory state.

## Additional Findings

- `GateInputEnvelope.clinical_lock_state` was an unchecked string with a default
  provisional state and no external-ref checks; its insertion before the old
  `contract_version` created positional compatibility risk.
- Envelope and YAML contract versions were not bumped after structural change.
- Tests did not cover transitions, invalid states, entry modes, endpoint/CDx
  timing, Gate envelope compatibility, or hypothesis-to-handoff propagation.
- The canonical architecture document had duplicate numbering and an unclear
  `ClinicalHypothesis -> TargetHypothesis` relationship.

## Accepted Positive Checks

- 45 Gate identities, order, and groups were unchanged.
- `TargetHypothesis` remained available for downstream compatibility.
- The five new component refs used `external:` boundaries.
- No data, cache, model weights, results, binaries, or local prompt edits were
  included in the PR diff.

## Required Next Action

Address the findings on the same PR, rerun tests and boundary checks, then
request another ChatGPT review. Do not merge or create the v2 snapshot before
`APPROVE`.
