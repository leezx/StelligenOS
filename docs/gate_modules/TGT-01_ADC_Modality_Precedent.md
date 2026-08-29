# TGT-01 — ADC Modality Precedent · MOD-TGT01 Construction Drawing

- Runtime Migration **PR E1** (`task_20260829_runtime-migration-pr-e1`)
- Machine contract: `src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml`
- Status: **construction contract + drawing only.** No implementation ships in
  this PR. `MIGRATION_PENDING` remains.

## What this document is

The frozen施工图 for **MOD-TGT01**, the single primary Evidence Production
Module of Gate **TGT-01** under `ADC_TARGET_GATESET@1.0` /
`INST-CRC-REFRACTORY-ADC-TARGET-v1`.

CURRENT_SYSTEM v5 §6.4: *逐 Gate 绘制 Evidence Production Module 施工图；审核
通过后 Module 才可开工.* So PR E1 delivers the drawing, the machine contract,
the validation tests and the 17-item acceptance checklist. The Module itself
(`gate_modules/tgt01_adc_modality_precedent/`) is **PR E2**, and may start only
after this contract is APPROVED.

**Kernel invariant.** The kernel defines the contract; the Module implements
it. One-way dependency, exactly like `extensions/`: a future `gate_modules/`
package MAY import kernel objects / Gate identity / contracts; `src/` MUST NEVER
import `gate_modules/`. The Module may not modify the Gate id / name / candidate
ownership, the `gate_question`, the Evidence Ladder, the evidence ceiling, or
the fatal / unknown / conflict / inference semantics; it may not reason across
Gates, lower a measurement requirement, or turn `UNKNOWN` into `PASS` / `HOLD` /
`KILL`.

## The one thing MOD-TGT01 answers

> **Has this target already been reality-tested by the ADC modality?**

It does **not** answer: whether the target is good in CRC (TGT-02), whether our
ADC is effective, whether the therapeutic window is safe (TGT-05), or whether
surface density / internalization is adequate (TGT-04 / TGT-06).

## Template provenance

The Blueprint v1.3 §H2.8 *Gate Module Acceptance Template* is referenced by
CURRENT_SYSTEM v5 but is **not in this repository or the File Library**. The
17-item checklist below is therefore marked
`template_provenance.status: RECONSTRUCTED` in the machine contract —
functionally complete and consistent with the frozen v5 §6.4 Module 权责边界
and the PR A–D contracts, but **not claimed verbatim from the Blueprint**.

## Gate ordering

Fatal-first + cheap-first: **TGT-01 → TGT-05 → TGT-08 → TGT-02 → TGT-03 →
TGT-04 → TGT-06 → TGT-07**. TGT-01 is first as the *Module-architecture
calibration case*: `PUBLIC_PRIMARY`, no CRC multi-omics download, no
experiments, the simplest evidence classes, the fastest way to validate the
full chain (`admissible raw evidence → atomic EvidencePackages → proposed
CandidateGateAssessment → machine acceptance record → human-review surface`).

## The 17-item acceptance checklist

| # | Item | What MOD-TGT01 must satisfy |
|---|---|---|
| 1 | **Gate identity & version** | `TGT-01@1.0`, `ADC_TARGET_GATESET@1.0`, L04, candidate ownership `ADC_TARGET`, bound to `INST-CRC-REFRACTORY-ADC-TARGET-v1`. Inherited, not owned. |
| 2 | **Primary Module identity & version** | `MOD-TGT01` (deterministic: `MOD-<GATE without hyphen>`). Contract v`0.1.0`; implementation version `0.0.0` = declared, not built. Exactly one primary Module per Gate. |
| 3 | **Gate question** | Quoted **verbatim** from the frozen PR D contract: *"Is there prior precedent that this target (or a biologically adjacent target in its lineage) is addressable by the ADC modality?"* Not widened, not narrowed. |
| 4 | **Admissible evidence classes** | Same-target ADC (approved / late-clinical / phase 1), adjacent-target ADC (class-level only), preclinical constructs, patents / disclosures, discontinued-programme reasons. **Not** admissible here: TGT-02…TGT-08 evidence (CRC coverage, persistence, surface density, normal-tissue liability, internalization, shedding, IP landscape). |
| 5 | **Evidence Ladder & ceiling** | Reproduced verbatim from PR D. `DIRECT` = approved / late-clinical same-target ADC with disclosed activity. `INDIRECT_STRONG` = phase-1 same-target ADC. `WEAK` = adjacent-target ADC / preclinical / patents. Ceiling: *clinical-stage ADC precedent against the same target antigen*. No new rungs, no exceeding the ceiling. |
| 6 | **Direction interpretation** | Strength ⟂ Direction. `POSITIVE` = ≥1 admissible precedent class at a graded strength. `NEGATIVE` is reserved for a target-attributable adverse pattern (item 8) — *"no precedent found" is `UNKNOWN`, not `NEGATIVE`*. `CONFLICTING` needs co-present support + adverse pattern with non-empty key evidence. Module proposes both, never a score. |
| 7 | **Allowed / forbidden inference** | Verbatim from PR D. Allowed: *ADC-modality feasibility for this target or its immediate lineage*. Forbidden: efficacy in refractory mCRC; normal-tissue safety / a favorable therapeutic index; adequate surface density or internalization. No cross-Gate conclusion. |
| 8 | **Fatal conditions** | Verbatim from PR D: a *target-attributable* pattern — ≥2 independent same-target ADC programmes discontinued for a consistent on-target toxicity or an intrinsically unachievable window. A single product's failure is admissible evidence, **not** fatal. The Module **recognises and reports** the pattern; it never performs a Candidate-level `KILL` (that is the GateSet `fatal_gate_policy`, PR B). |
| 9 | **Evidence-source plan** | `PUBLIC_PRIMARY`, no experimental sources. *Strong*: regulatory approvals/labels, registrational trial registries. *Supporting*: early-phase registries, peer-reviewed clinical publications, company disclosures with a resolvable primary source. *Weak-only*: patents, preclinical publications, adjacent-target programmes — a weak-only class can never lift the assessment above `WEAK`. An **ADCdb-class database is a discovery / index layer** — it may find, normalize and link a programme but **never establishes a ladder rung on its own**; once resolved, the EvidencePackage's authority is the underlying primary disclosure, and an unresolved database-only row is a retrieval lead. **PR E1 connects no provider.** Retrieval / entity-resolution / provenance / serialization are shared infrastructure (§6.5) — reused, not re-implemented per Gate. |
| 10 | **Input contract** | `candidate_id` + target identity; `instantiation_id` + context; the frozen `gate_contract_ref` / `evidence_ladder_ref`; run context (`run_id`, retrieval window, `evidence_regime = PUBLIC_ONLY`); existing `evidence_refs`. **No implicit default scientific context** — fail rather than assume an indication / modality / regime not given by the Instantiation. |
| 11 | **EvidencePackage output contract** | Atomic, neutral, no grade / direction; full `provenance` (`SRC-` id, source_type, identifier, locator, retrieved_at); `candidate_refs`; `measurement` / `claim`; `interpretation_boundary`; `derivation`. Reference an existing EP by `evidence_id` — never copy or re-create (PR C). Forward `status` / `superseded_by` never on `evidence.json` (PR C: only on `EvidenceIndexEntry`). Shape: `evidence_package.schema.json` / PR A `EvidencePackage`. |
| 12 | **Assessment proposal envelope contract** | The Module emits a **non-canonical, module-local proposal envelope** — *not* a `CandidateGateAssessment`. Per PR A that object is the canonical cell and `CANONICAL_REVIEW_STATUS = HUMAN_APPROVED`; constructing it with any other `review.status` is rejected, so the Module cannot and must not produce one. The envelope carries `proposed_direction` + `proposed_strength` (never a Decision / score), `evidence_refs` `[{evidence_id, role}]`, `aggregation_rationale`, `critical_unknowns`, `evidence_ceiling`, and the machine acceptance record. It **mirrors the field shape of `assessment.schema.json`** (the canonicalisation *target*) so a human review can lift it into a canonical `CandidateGateAssessment`; it carries no `review` block. PR E1 only defines the envelope's field list — no new core object, no runtime code. |
| 13 | **Machine acceptance criteria** | Every EP validates against the schema; every `source_id` / `evidence_id` resolves (PR C `check_*`); every evidence class is in the item-4 admissible list and none in `not_admissible`; strength ≤ the highest rung actually met; dedup (one `SRC` → many `EP`, no duplicated `(source, claim)`); required fields present; **no numeric score**. On failure: rejected with a machine reason, nothing enters the canonical record. |
| 14 | **Human acceptance / review surface** | The human sees: proposed direction + strength + rationale; each EP's claim / source / `interpretation_boundary` (drill-down); the ladder rung per EP; `critical_unknowns`; the machine acceptance record. Human-only: whether the aggregate is scientifically right for TGT-01; whether a "same / adjacent target" call is right; final `HUMAN_APPROVED` → the assessment enters `ASSESSMENTS/<cand>/vNNN.json` and the MatrixView rebuilds (PR C). |
| 15 | **Failure / UNKNOWN / conflict behaviour** | Retrieval failure → a machine reason, not a partial assessment. Insufficient evidence → `INCONCLUSIVE` / `UNKNOWN`, never `PASS`. No admissible evidence at all → `UNKNOWN` (*"...not KILL. A novel target is not disqualified by absence of precedent."*). Conflicting evidence → `CONFLICTING` with non-empty key evidence. Gap closable only by non-public data → `critical_unknown` resolution `EXPERIMENT_REQUIRED`, stop. **`UNKNOWN` is never silently `PASS` / `HOLD` / `KILL`** (§6.4). |
| 16 | **Stop rule** | **Mandatory before any stop:** the same-target ADC programme inventory (active, approved *and* discontinued / failed) and the disclosed failure / discontinuation-reason sweep are complete — a positive ceiling does **not** license stopping, because item 8's target-attributable adverse pattern can only be seen after the failed-programme sweep (fatal-first). **Then** stop when *any* of: the TGT-01 ceiling is reached; marginal search can no longer change direction / strength; the critical unknown is `EXPERIMENT_REQUIRED`; the enumerated source space is exhausted. Bounds the "infinite evidence gathering" failure mode. |
| 17 | **Downstream consumer / handoff** | Consumed by: the `MatrixView` cell `(candidate_id, TGT-01)` (PR C); the `ADC_TARGET_GATESET` decision layer that turns the eight TGT assessments into a Candidate-level `Decision` (PR B); the next Gate (`TGT-05`) as context only; experimental validation when `EXPERIMENT_REQUIRED`. This Module does **not** produce a Decision / `KILL`, write to another Gate's index or assessment, or modify the Matrix. |

## Deferred to PR E2+

- The new top-level `gate_modules/` directory and
  `gate_modules/tgt01_adc_modality_precedent/` implementation (providers,
  adapters, extractor, normalizer, runner, dry-run executor, EvidencePackage
  writer, Assessment proposer).
- Connecting any retrieval provider or dataset.
- The other seven TGT primary Modules (`TGT-05 → TGT-08 → TGT-02 → TGT-03 →
  TGT-04 → TGT-06 → TGT-07`).
