# `gen_indication_endpoint_target`

Software-only Phase 1 contracts for constrained ADC indication, endpoint, and
target opportunity generation.

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

## Phase 1 contracts

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

