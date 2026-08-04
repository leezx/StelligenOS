# StelligenOS Lifecycle

## Lifecycle Stages

1. Opportunity Generation
2. Opportunity Validation
   - `AssetGenOS` lives here as a subsystem
3. Asset Generation
4. Asset Development

## Lifecycle Rules

- `Asset Development` replaces `Asset Advancement` as the preferred term.
- Due Diligence is stage-aware and uses different question sets at different lifecycle stages.
- A script success signal does not automatically promote lifecycle state.

## Status Fields

Each lifecycle transition should record:

- current state
- proposed next state
- entry criteria
- exit criteria
- required evidence
- unresolved risks
- decision
- decision rationale
- capital level
- timestamp
- reviewer
- relevant versions

## Progressive Clinical Locking

Opportunity Generation does not permanently lock a final indication or
registrational endpoint. The external ClinicalHypothesis contract progresses
through:

`exploratory -> provisional -> anchored -> product-locked -> protocol-locked -> regulatory-locked`

T0 keeps its frozen identity and topology, but its output is a maturity-aware
clinical context and benefit hypothesis. Endpoint class is an early design
input; exact protocol endpoints and observed endpoint performance are later
artifacts. Biomarker biology and assay feasibility are early inputs, while
cutoff and CDx remain deferrable.
