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
**not** a seventh core object. `Decision` lands in PR B. `legacy_adapters.py`
maps the eight legacy types onto the new model.

Object implementations must not become implicit data storage.
