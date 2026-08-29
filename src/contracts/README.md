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
`data_layout/` by `tests/test_decision_model.py`. The legacy `core_objects@1.1`
registry is unchanged; `src/objects/legacy_adapters.py` maps its eight types
onto the new model (one-to-one for
`TargetHypothesis`/`BinderCandidate`/`DevelopmentCandidate`,
`NotImplementedError` with a crosswalk pointer for the composites).

Runtime Migration PR B adds `gate_contracts.yaml` (registry) and
`src/objects/gate_model.py` for the two-rule-layer Gate system: `Gate@0.1.0`,
`GateSet@0.1.0`, `EvidenceLadder@0.1.0` and `Decision@0.1.0` (the sixth
decision-layer object; its persistence shape mirrors
`data_layout/decision.schema.json` and its runtime validation is strictly
stricter — runtime-valid ⊂ schema-valid). Policy and ladder bodies are
`external:` refs — there is no decision engine in the repo. The legacy
`gate_system@0.1.0` / 45-gate topology stays `FROZEN_LEGACY`;
`src/objects/legacy_gate_map.py` holds the migration reference and asserts at
import time that it still agrees with the kernel's live topology.

Runtime Migration PR C adds `evidence_reference.yaml` (registry) and
`src/objects/evidence_reference_model.py` for the Matrix view and the
reusable-evidence reference layer: `MatrixView@0.1.0` (a derived, rebuildable
projection with no id — Data Layout Spec Appendix B gives the Matrix no JSON
Schema and PR C adds none), `EvidenceIndexEntry@0.1.0` (the global evidence
index, the only home of the EvidencePackage lifecycle `status` and forward
`superseded_by` — other canonical objects keep their own intrinsic status),
`SourceIndexEntry@0.1.0` and `GateEvidenceIndexEntry@0.1.0`. The view and index
rows serialise to the frozen `data_layout/csv_headers.yaml` headers verbatim.
The `check_*` functions verify referential integrity both across the derived
index rows and *through* the canonical `CandidateGateAssessment` /
`EvidencePackage` — a provenance chain is valid only when it passes through the
canonical records, not merely because the indexes are mutually self-consistent.
PR A's `evidence_refs` mechanism is the reusable-reference primitive and is not
changed. There is no matrix-rebuild engine in the repo.

Runtime Migration PR D adds `crc_adc_target_gateset.yaml` (registry) and
`src/objects/crc_adc_target_gateset.py` for `CRC-ADC-TARGET-GATESET-v1` — the
first machine-readable specialization of the canonical `ADC_TARGET_GATESET`
(L04): the frozen TGT-01…TGT-08 roster (`gate_version` initialized at `"1.0"`,
names from CURRENT_SYSTEM v5 §6.4), eight concrete Evidence Ladders (evidence-class
semantics, ceilings and inference boundaries — no invented numeric thresholds,
with the v5 §11.2 EVGAP→Gate inference guards baked into TGT-02/03/04), the
`ADC_TARGET_GATESET@1.0` GateSet, and the `INST-CRC-REFRACTORY-ADC-TARGET-v1`
Instantiation with its context-specific `gateset_binding` / `gate_binding`
records (parity-checked against the frozen `data_layout/gate_binding.schema.yaml`).
`CRC-ADC-TARGET-GATESET-v1` is a program label, never a `gateset_id`. No Evidence
Production Module is created; each gate carries a `MOD-TGT0n` slot at `"0.0.0"`
(declared, not built). The eight ladders are a proposal frozen by this PR's own
scientific review.
