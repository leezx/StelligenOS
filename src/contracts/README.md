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

`opportunity_territory.yaml` and `opportunity_territory.py` open Work Package 2
with `OpportunityTerritory@0.1.0` and `OpportunityTerritoryMap@0.1.0`. A
territory is a clinical water, not a candidate: it names no target and generates
none. It carries a `search_space_admission_ref` recording which admission routed
it, and deliberately stores no route state of its own - the route lives in
`SearchSpaceAdmission@0.1.0` and nowhere else, so nothing here can drift from
it. The schema holds no disease-specific content; territory instances live in an
external workspace.

Runtime Migration PR A adds `decision_objects.yaml` (registry) and
`src/objects/decision_model.py` (frozen dataclasses) for the Blueprint v1.3
decision-layer objects `Candidate@0.1.0`, `Context@0.1.0`,
`EvidencePackage@0.1.0`, `CandidateGateAssessment@0.1.0` and the
`Instantiation@0.1.0` binding object. Field sets, enums and the
direction x strength matrix are kept in step with the frozen disk schemas under
`data_layout/` by `tests/test_decision_model.py`. The sixth object, `Decision`,
lands in PR B. The legacy `core_objects@1.1` registry is unchanged;
`src/objects/legacy_adapters.py` maps its eight types onto the new model
(one-to-one for `TargetHypothesis`/`BinderCandidate`/`DevelopmentCandidate`,
`NotImplementedError` with a crosswalk pointer for the composites).
