# ChatGPT PR #45 Round 2 Review

- Review surface: Chrome ChatGPT conversation `ADC研发靶点选择`
- PR: https://github.com/leezx/StelligenOS/pull/45
- Reviewed head: `2b4ab3e`
- Decision: `REQUEST_CHANGES`

## Blocking Findings

1. `ClinicalHypothesis` is still not the mandatory generation-to-validation-to-T12 identity. `TargetCandidate` still unconditionally requires exact legacy indication, population, endpoint, target, setting, line, comparator and related fields. A candidate cannot use only `clinical_hypothesis_ref`. `TargetOpportunityHandoff` also permits a complete legacy handoff without the new identity. ChatGPT requires an explicit legacy compatibility path, mandatory hypothesis identity for v5 candidate/T12 paths, paired hypothesis and lock-state references, and negative tests.
2. Lock-state minimums are not cumulative. `PROTOCOL_LOCKED` and `REGULATORY_LOCKED` can be constructed without foundational target, anchor, benefit, biomarker or product components. Requirements must accumulate through earlier states, with tests for invalid higher-state construction.
3. Two incompatible `ClinicalLockState` enums exist in the GenModule and Gate capability contracts. A GenModule lock state cannot pass directly into `GateInputEnvelope`. One canonical enum must be shared, with a cross-module integration test.
4. `TARGET_CONTEXT_COSELECTION` permits a completely empty exploratory `ClinicalHypothesis`; it needs a meaningful minimum. The entry-mode test must instantiate and validate all three exploratory modes.

## Correctly Improved

- Typed monotonic single-step lock transition checking.
- Protocol, observed and registrational endpoint references.
- Biomarker cutoff and CDx status/reference types.
- Hypothesis-seed paths in `OpportunitySearchScope` and `ClinicalFrame`.
- T0 input positional ordering and 2.1.0 versions.
- YAML versions 1.1 and 0.2.0.
- Frozen 45-Gate topology and data-free repository boundary.

## Verification Note

ChatGPT noted that GitHub has no Actions run associated with `2b4ab3e`; local handoff reports 179 passing tests.
