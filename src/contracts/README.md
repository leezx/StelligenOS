# Contracts

This layer contains implementation-facing contracts and schemas derived from
the canonical architecture documents.

It must not contain datasets, persisted records, or runtime data stores.

Current sponsor-relative strategy contracts:

- `sponsor_strategy.yaml` defines `DevelopmentSponsorProfile@0.1.0` and
  `ProgramThesis@0.1.0`.
- `sponsor_strategy.py` validates these shapes in memory and requires runtime
  references to use the `external:` scheme.

The contracts do not grant program commitment, execute Gates, or persist
instances.

Phase 2 adds `search_space_admission.yaml` and
`search_space_admission.py` for `SearchSpaceAdmission@0.1.0`. It defines four
sponsor-relative routes and eight externally evidenced criteria; it does not
evaluate a scientific Gate or persist a route instance.

Phase 3 adds `program_commitment_review.yaml` and
`program_commitment_review.py` for `ProgramCommitmentReview@0.2.0`. It records
an externally adjudicated sponsor-relative commitment checkpoint after T12;
it does not define ValueInflectionPlan or execute binder/ADC routes.

Phase 4 adds `value_inflection_plan.yaml` and `value_inflection_plan.py` for
`ValueInflectionPlan@0.1.0`. It defines the externally referenced target
value-transfer boundary, minimum evidence package, success criteria, stop
conditions, capability sources, and buyer requirements. It does not execute
Asset Generation, advance lifecycle stages, or store plan instances.

`sponsor_fit_assessment.yaml` and `sponsor_fit_assessment.py` complete Work
Package 1 with `SponsorFitAssessment@0.1.0`, the fourth of that package's four
contracts. It records the seven mandatory sponsor-fit questions, a capability
map and a resource map, and produces a route recommendation. It computes no
aggregate score by design, keeps `UNKNOWN` distinct from `UNSATISFIED`, and
requires an explicit external waiver before `SELF_DEVELOP` without an
asymmetric evidence advantage. It grants no commitment and authorises no
capital; `ProgramCommitmentReview@0.2.0` requires a reference to it, so a
commitment cannot be reached without one.
