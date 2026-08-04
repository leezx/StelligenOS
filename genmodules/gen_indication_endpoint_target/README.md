# `gen_indication_endpoint_target`

Software-only contracts for constrained ADC opportunity generation. The v5
development unit is `Target x Anchor Clinical Context x Product/Benefit
Hypothesis`; it is not a permanently fixed indication-endpoint-target tuple.

## Boundary

This package defines in-memory contract shapes only. It does not contain:

- clinical, target, or evidence data;
- a database, cache, result tree, model weight, or runner;
- a candidate generator, evidence collector, Rule/Model evaluator, Gate
  evaluator, ranking engine, or persistence layer;
- a new Gate. T0-T12 remain aliases for the existing frozen Target
  Opportunity T-chain.

All source, run, policy, Gate-result, review, opportunity, and hypothesis
references that cross the execution boundary must use `external:` references.
`CandidateFilterResult` and `AdversarialReview` are explicitly non-Gate
contracts. `NOT_EVALUATED` and `UNRESOLVED` preserve insufficient evidence and
must not be converted into PASS or FAIL by this package.

## Progressive hypothesis contracts

- `AnchorClinicalContext`: anchor indication, setting, line, population and
  comparator used for design and validation; expansion indications remain open.
- `IntendedBenefitHypothesis`: clinical value direction and endpoint class;
  observed effect size is never represented as an input.
- `BiomarkerHypothesis`: biology and assay feasibility; final cutoff/CDx may be
  deferred.
- `ProductHypothesis`: ADC design constraints derived from the clinical use.
- `ClinicalHypothesis`: the auditable composition of the external refs and a
  progressive lock state from `exploratory` to `regulatory-locked`.

## Existing contracts

- `OpportunitySearchScope`
- `ClinicalFrame`
- `TargetCandidate`
- `CandidateFilterResult`
- `EvidenceRecord`
- `AdversarialReview`
- `TargetOpportunityHandoff`

External generation and evaluation implementations may consume these shapes
through the Opportunity Generation capability port. They must keep inputs,
observations, evidence, and run outputs outside this repository.
