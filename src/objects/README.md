# Objects

`core.py` is the legacy `core_objects@1.1` registry, retained during the runtime
migration:

- Opportunity
- ClinicalHypothesis
- TargetHypothesis
- BinderCandidate
- ADCConstruct
- LeadSeries
- DevelopmentCandidate
- Asset

`decision_model.py` (Runtime Migration PR A) holds the Blueprint v1.3
decision-layer objects — `Candidate`, `Context`, `EvidencePackage`,
`CandidateGateAssessment` — and the `Instantiation` binding object, which is
**not** a seventh core object. `legacy_adapters.py` maps the eight legacy types
onto the new model.

`gate_model.py` (Runtime Migration PR B) holds the two-rule-layer Gate system
contracts — `Gate` (assessment_rule over an `EvidenceLadder` → Direction +
Strength), `GateSet` (four policy refs → `Decision`), `EvidenceLadder` (rung
shape only; concrete rungs are PR D), and `Decision`, the sixth decision-layer
object, whose persistence shape mirrors `data_layout/decision.schema.json` while
its runtime validation is strictly stricter (runtime-valid ⊂ schema-valid).
`legacy_gate_map.py` is the frozen-45-gate migration reference; it does not
modify `gate_system.yaml` or `src/capabilities/gates.py`.

`evidence_reference_model.py` (Runtime Migration PR C) holds `MatrixView` /
`MatrixRow` — the Candidate × Gate Matrix as a derived, rebuildable projection
with no id (every row Candidate is at the Matrix's Candidate Level) — and the
reusable-evidence reference layer: `EvidenceIndexEntry` / `EvidenceLibraryIndex`
(the global evidence index, the only home of the EvidencePackage lifecycle
`status` and forward `superseded_by`; `ACTIVE` → no pointer, `SUPERSEDED` →
pointer, `RETRACTED` → optional pointer), `SourceIndexEntry` / `SourceIndex`
(one source → many EvidencePackages), and `GateEvidenceIndexEntry` /
`GateEvidenceIndex` (a per-gate reference, never a copy). The `check_*`
functions walk the reference layer for referential integrity in two layers —
across the derived index rows, and *through* the canonical PR A
`CandidateGateAssessment` and `EvidencePackage` (a Matrix cell must equal its
serialized assessment; an EvidencePackage's `provenance.source_id` must be in
the source index). They compute no direction, strength or decision. No JSON
Schema is added under `data_layout/`.

Object implementations must not become implicit data storage.
