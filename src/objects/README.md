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
object, kept in exact parity with `data_layout/decision.schema.json`.
`legacy_gate_map.py` is the frozen-45-gate migration reference; it does not
modify `gate_system.yaml` or `src/capabilities/gates.py`.

Object implementations must not become implicit data storage.
