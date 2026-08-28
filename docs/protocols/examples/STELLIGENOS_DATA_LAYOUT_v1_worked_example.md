# StelligenOS Data Layout v1.0 — worked example: `TGT-04 × CEACAM5`

> **REFERENCE EXAMPLE — NOT REAL DATA.** Every path and payload below is a
> placeholder illustrating the physical shape defined by
> `docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md`. Real StelligenOS
> runtime data lives **outside this repository** under `$STELLIGENOS_DATA/`
> (default `/Volumes/Stelligen_SSD/Stelligen/DATA/StelligenOS/`); generate the
> empty external tree with `scripts/scaffold_data_layout.sh`.
>
> This repository stores no `.csv` files (see `scripts/verify_repository_boundary.sh`),
> so this example is a single document rather than a file tree. Only `TGT-04`
> is expanded; `TGT-01..03` and `TGT-05..08` are sibling folders with the
> identical internal structure.

## Tree

```text
$STELLIGENOS_DATA/
├── 00_REGISTRY/
│   ├── candidate_type_registry.csv
│   ├── gateset_registry.csv
│   ├── gate_registry.csv
│   └── instantiation_registry.csv
├── 10_CANDIDATES/
│   └── L04_ADC_TARGET.csv
├── 20_INSTANTIATIONS/
│   └── INST-CRC-REFRACTORY-ADC-TARGET-v1/
│       ├── instantiation.yaml
│       ├── candidates.csv
│       ├── MATRICES/
│       │   ├── L04_ADC_TARGET.matrix.csv
│       │   └── L04_ADC_TARGET.assessments.csv
│       ├── DECISIONS/
│       │   ├── decisions.csv
│       │   └── DEC-0001.json
│       └── GATESETS/
│           └── ADC_TARGET_GATESET-v1/
│               ├── gateset_binding.yaml
│               └── TGT-04/
│                   ├── gate_binding.yaml
│                   ├── CURRENT/
│                   │   ├── assessments.csv
│                   │   ├── evidence_index.csv
│                   │   └── unknowns.csv
│                   ├── ASSESSMENTS/
│                   │   └── CAND-L04-000001/
│                   │       ├── v001.json
│                   │       └── latest.json      (byte-identical copy of v001.json)
│                   └── RUNS/
│                       └── RUN-TGT04-20260827-001/   (IMMUTABLE)
│                           ├── run_manifest.json
│                           ├── candidates_input.csv
│                           ├── evidence_created.csv
│                           ├── assessment_proposals.csv
│                           ├── qc_report.json
│                           └── logs/run.log
└── 30_EVIDENCE_LIBRARY/
    ├── evidence_index.csv
    ├── source_index.csv
    └── PACKAGES/
        └── EP-00000123/
            ├── evidence.json
            ├── summary.md
            └── artifacts/extracted_table.csv
```

---

## `00_REGISTRY/candidate_type_registry.csv`

```csv
candidate_type,level,canonical_gateset,description,status
ADC_TARGET,L04,ADC_TARGET_GATESET,ADC target address candidate,ACTIVE
```

## `00_REGISTRY/gateset_registry.csv`

```csv
gateset_id,gateset_version,candidate_level,member_gate_ids,status
ADC_TARGET_GATESET,1.0,L04,"TGT-01;TGT-02;TGT-03;TGT-04;TGT-05;TGT-06;TGT-07;TGT-08",ACTIVE
```

## `00_REGISTRY/gate_registry.csv`

```csv
gate_id,gateset_id,candidate_level,gate_name,dominant_evidence_regime,gate_version
TGT-04,ADC_TARGET_GATESET,L04,Tumor Surface Availability / Density Plausibility,PUBLIC_HYBRID,1.0
```

## `00_REGISTRY/instantiation_registry.csv`

```csv
instantiation_id,candidate_type,candidate_level,context_id,modality,gateset_id,gateset_version,evidence_regime,status,created_at
INST-CRC-REFRACTORY-ADC-TARGET-v1,ADC_TARGET,L04,CTX-CRC-REFRACTORY-MSSPMMR,ADC,ADC_TARGET_GATESET,1.0,PUBLIC_ONLY,ACTIVE,2026-08-28
```

---

## `10_CANDIDATES/L04_ADC_TARGET.csv`

```csv
candidate_id,candidate_type,level,canonical_name,parent_candidate_id,status,version,created_at,provenance_ref
CAND-L04-000001,ADC_TARGET,L04,CEACAM5,,ACTIVE,1,2026-08-28,external:ADCdb/target/CEACAM5@v3
```

---

## `20_INSTANTIATIONS/INST-CRC-REFRACTORY-ADC-TARGET-v1/instantiation.yaml`

```yaml
instantiation_id: INST-CRC-REFRACTORY-ADC-TARGET-v1
candidate_type: ADC_TARGET
candidate_level: L04
context_id: CTX-CRC-REFRACTORY-MSSPMMR
modality: ADC
gateset_id: ADC_TARGET_GATESET
gateset_version: "1.0"
evidence_regime: PUBLIC_ONLY
status: ACTIVE
version: 1
created_at: 2026-08-28
```

## `.../candidates.csv`

```csv
candidate_id,canonical_name,admitted_at,admission_note
CAND-L04-000001,CEACAM5,2026-08-28,reference example
```

## `.../MATRICES/L04_ADC_TARGET.matrix.csv`

```csv
candidate_id,name,TGT-01,TGT-02,TGT-03,TGT-04,TGT-05,TGT-06,TGT-07,TGT-08,decision
CAND-L04-000001,CEACAM5,—,—,—,POSITIVE/INDIRECT_STRONG,—,—,—,—,MORE_EVIDENCE
```

## `.../MATRICES/L04_ADC_TARGET.assessments.csv`

```csv
candidate_id,gate_id,direction,strength,assessment_id,assessment_version,evidence_count,review_status,last_updated_at
CAND-L04-000001,TGT-04,POSITIVE,INDIRECT_STRONG,ASMT-000001,1,2,HUMAN_APPROVED,2026-08-28
```

## `.../DECISIONS/decisions.csv`

```csv
decision_id,candidate_id,gateset_id,gateset_version,decision,triggered_by_gates,review_status,decided_at
DEC-0001,CAND-L04-000001,ADC_TARGET_GATESET,1.0,MORE_EVIDENCE,TGT-04,HUMAN_APPROVED,2026-08-28
```

## `.../DECISIONS/DEC-0001.json`

```json
{
  "decision_id": "DEC-0001",
  "instantiation_id": "INST-CRC-REFRACTORY-ADC-TARGET-v1",
  "candidate_id": "CAND-L04-000001",
  "gateset_id": "ADC_TARGET_GATESET",
  "gateset_version": "1.0",
  "decision": "MORE_EVIDENCE",
  "triggered_by": [
    {
      "gate_id": "TGT-04",
      "assessment_id": "ASMT-000001",
      "reason": "surface availability supported but quantitative antigen density is EXPERIMENT_REQUIRED"
    }
  ],
  "assessment_snapshot": {
    "TGT-01": "UNKNOWN", "TGT-02": "UNKNOWN", "TGT-03": "UNKNOWN",
    "TGT-04": "POSITIVE/INDIRECT_STRONG", "TGT-05": "UNKNOWN", "TGT-06": "UNKNOWN",
    "TGT-07": "UNKNOWN", "TGT-08": "UNKNOWN"
  },
  "decision_rule_ref": "external:gateset/ADC_TARGET_GATESET/decision_rule@v1",
  "review": { "status": "HUMAN_APPROVED", "reviewer": "human", "reviewed_at": "2026-08-28" }
}
```

---

## `.../GATESETS/ADC_TARGET_GATESET-v1/gateset_binding.yaml`

```yaml
gateset_id: ADC_TARGET_GATESET
gateset_version: "1.0"
instantiation_id: INST-CRC-REFRACTORY-ADC-TARGET-v1
gates:
  - {gate_id: TGT-01, gate_version: "1.0"}
  - {gate_id: TGT-02, gate_version: "1.0"}
  - {gate_id: TGT-03, gate_version: "1.0"}
  - {gate_id: TGT-04, gate_version: "1.0"}
  - {gate_id: TGT-05, gate_version: "1.0"}
  - {gate_id: TGT-06, gate_version: "1.0"}
  - {gate_id: TGT-07, gate_version: "1.0"}
  - {gate_id: TGT-08, gate_version: "1.0"}
decision_rule_ref: external:gateset/ADC_TARGET_GATESET/decision_rule@v1
fatal_gate_policy_ref: external:gateset/ADC_TARGET_GATESET/fatal_gate_policy@v1
required_gate_policy_ref: external:gateset/ADC_TARGET_GATESET/required_gate_policy@v1
```

## `.../TGT-04/gate_binding.yaml`

```yaml
gate_id: TGT-04
gate_version: "1.0"
gateset_id: ADC_TARGET_GATESET
gateset_version: "1.0"
instantiation_id: INST-CRC-REFRACTORY-ADC-TARGET-v1
candidate_level: L04
dominant_evidence_regime: PUBLIC_HYBRID
gate_contract_ref: external:gate/TGT-04/contract@v1
evidence_ladder_ref: external:gate/TGT-04/evidence_ladder@v1
assessment_rule_ref: external:gate/TGT-04/assessment_rule@v1
primary_module_id: MOD-TGT04
primary_module_version: "0.1.0"
```

## `.../TGT-04/CURRENT/assessments.csv`

```csv
candidate_id,gate_id,direction,strength,assessment_id,assessment_version,evidence_count,review_status,last_updated_at
CAND-L04-000001,TGT-04,POSITIVE,INDIRECT_STRONG,ASMT-000001,1,2,HUMAN_APPROVED,2026-08-28
```

## `.../TGT-04/CURRENT/evidence_index.csv`

```csv
evidence_id,candidate_id,role,assessment_id
EP-00000123,CAND-L04-000001,SUPPORTING,ASMT-000001
EP-00000131,CAND-L04-000001,CONTRADICTING,ASMT-000001
```

## `.../TGT-04/CURRENT/unknowns.csv`

```csv
candidate_id,gate_id,assessment_id,unknown,resolution
CAND-L04-000001,TGT-04,ASMT-000001,Quantitative surface antigen density in refractory mCRC,EXPERIMENT_REQUIRED
```

## `.../TGT-04/ASSESSMENTS/CAND-L04-000001/v001.json`  (and `latest.json`, byte-identical)

```json
{
  "assessment_id": "ASMT-000001",
  "assessment_version": 1,
  "instantiation_id": "INST-CRC-REFRACTORY-ADC-TARGET-v1",
  "candidate_id": "CAND-L04-000001",
  "context_id": "CTX-CRC-REFRACTORY-MSSPMMR",
  "gateset_id": "ADC_TARGET_GATESET",
  "gateset_version": "1.0",
  "gate_id": "TGT-04",
  "gate_version": "1.0",
  "direction": "POSITIVE",
  "strength": "INDIRECT_STRONG",
  "evidence_refs": [
    { "evidence_id": "EP-00000123", "role": "SUPPORTING" },
    { "evidence_id": "EP-00000131", "role": "CONTRADICTING" }
  ],
  "aggregation_rationale": "Multiple protein-level datasets support surface availability, but no direct quantitative antigen-density measurement exists in refractory mCRC.",
  "critical_unknowns": [
    { "unknown": "Quantitative surface antigen density in refractory mCRC", "resolution": "EXPERIMENT_REQUIRED" }
  ],
  "evidence_ceiling": "Current evidence supports surface availability but not quantitative antigen density.",
  "review": { "status": "HUMAN_APPROVED", "reviewer": "human", "reviewed_at": "2026-08-28" }
}
```

## `.../TGT-04/RUNS/RUN-TGT04-20260827-001/run_manifest.json`

```json
{
  "run_id": "RUN-TGT04-20260827-001",
  "gate_id": "TGT-04",
  "gate_version": "1.0",
  "instantiation_id": "INST-CRC-REFRACTORY-ADC-TARGET-v1",
  "module_id": "MOD-TGT04",
  "module_version": "0.1.0",
  "code_commit": "0000000000000000000000000000000000000000",
  "started_at": "2026-08-27T14:00:00Z",
  "completed_at": "2026-08-27T15:12:00Z",
  "candidate_count": 1,
  "status": "COMPLETED"
}
```

## `.../RUN-TGT04-20260827-001/candidates_input.csv`

```csv
candidate_id,canonical_name
CAND-L04-000001,CEACAM5
```

## `.../RUN-TGT04-20260827-001/evidence_created.csv`

```csv
evidence_id,candidate_id,source_id,claim_short,created_at
EP-00000123,CAND-L04-000001,SRC-00000881,membranous IHC staining in CRC tumors,2026-08-27
EP-00000131,CAND-L04-000001,SRC-00000902,no quantitative antigen density in refractory mCRC,2026-08-27
```

## `.../RUN-TGT04-20260827-001/assessment_proposals.csv`

```csv
candidate_id,gate_id,proposed_direction,proposed_strength,evidence_count,proposal_rationale,qc_status
CAND-L04-000001,TGT-04,POSITIVE,INDIRECT_STRONG,2,"protein-level surface support; density unknown",QC_PASSED
```

## `.../RUN-TGT04-20260827-001/qc_report.json`

```json
{
  "run_id": "RUN-TGT04-20260827-001",
  "checks": [
    { "check": "evidence_measurement_class_within_boundary", "status": "PASS" },
    { "check": "no_grade_on_evidence_package", "status": "PASS" },
    { "check": "conflict_direction_flagged", "status": "PASS" }
  ],
  "overall": "PASS"
}
```

## `.../RUN-TGT04-20260827-001/logs/run.log`

```text
2026-08-27T14:00:00Z  RUN-TGT04-20260827-001 start (reference example, not a real run)
2026-08-27T15:12:00Z  RUN-TGT04-20260827-001 done  status=COMPLETED candidate_count=1
```

---

## `30_EVIDENCE_LIBRARY/evidence_index.csv`

```csv
evidence_id,version,claim_short,measurement_type,primary_source_id,candidate_refs,created_at,status
EP-00000123,1,"CEACAM5 protein on malignant epithelial membranes",IHC,SRC-00000881,CAND-L04-000001,2026-08-27,ACTIVE
EP-00000131,1,"no quantitative CEACAM5 antigen density in refractory mCRC",review,SRC-00000902,CAND-L04-000001,2026-08-27,ACTIVE
```

## `30_EVIDENCE_LIBRARY/source_index.csv`

```csv
source_id,source_type,external_id,title,year,external_ref
SRC-00000881,PMID,12345678,"Example CEACAM5 IHC cohort study",2025,external:pmid/12345678
SRC-00000902,PMID,23456789,"Example review of ADC target antigen density",2024,external:pmid/23456789
```

## `30_EVIDENCE_LIBRARY/PACKAGES/EP-00000123/evidence.json`

```json
{
  "evidence_id": "EP-00000123",
  "version": 1,
  "claim": "CEACAM5 protein was detected on malignant epithelial cell membranes in a colorectal cancer cohort.",
  "measurement": {
    "type": "IHC",
    "analyte": "CEACAM5 protein",
    "readout": "membranous staining",
    "result": "68% positive tumors"
  },
  "candidate_refs": ["CAND-L04-000001"],
  "study_context": {
    "indication": "colorectal cancer",
    "treatment_state": "mixed",
    "sample_type": "primary tumor",
    "n": 124
  },
  "provenance": {
    "source_id": "SRC-00000881",
    "source_type": "PMID",
    "source_identifier": "12345678",
    "locator": "Figure 2; Supplementary Table S3",
    "retrieved_at": "2026-08-27"
  },
  "interpretation_boundary": {
    "directly_supports": ["membrane-localized protein is detectable in CRC tumor cells"],
    "does_not_support": ["quantitative antigen density", "refractory-state persistence", "ADC therapeutic window"],
    "limitations": ["non-refractory cohort", "semiquantitative IHC"],
    "evidence_ceiling": "protein-level surface plausibility"
  },
  "derivation": {
    "module_run_id": "RUN-TGT04-20260827-001",
    "code_commit": "0000000000000000000000000000000000000000"
  }
}
```

> Note: `evidence.json` carries **no** `direction` / `strength` / `grade`. The
> `POSITIVE / INDIRECT_STRONG` verdict is produced only in the Assessment above,
> where `EP-00000123` has role `SUPPORTING` and `EP-00000131` has role
> `CONTRADICTING`. The same `EP-00000123` could carry a different role in a
> `TGT-01` assessment.

## `30_EVIDENCE_LIBRARY/PACKAGES/EP-00000123/summary.md`

```markdown
# EP-00000123 (reference example — generated from evidence.json)

CEACAM5 protein detected on malignant epithelial cell membranes by IHC in a
colorectal cancer cohort (68% positive, n=124, primary tumor, mixed treatment
state). Directly supports membrane-localized protein detectability in CRC tumor
cells. Does NOT support quantitative antigen density, refractory-state
persistence, or ADC therapeutic window. Ceiling: protein-level surface
plausibility. Source: PMID 12345678 (SRC-00000881).
```

## `30_EVIDENCE_LIBRARY/PACKAGES/EP-00000123/artifacts/extracted_table.csv`

```csv
cohort,n,ihc_positive_pct,scoring
example_CRC_cohort,124,68,semiquantitative_membranous
```
