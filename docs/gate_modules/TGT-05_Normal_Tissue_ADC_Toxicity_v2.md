# MOD-TGT05@2.0.0 — B1 implementation note

Status: **UNBOUND**. The v2 Gate contract still binds
`MOD-TGT05@0.0.0`, and the CRC v2 Instantiation remains `HOLD`.

## Input and authority

`run(request, provider, source_resolver, evidence_library, evidence_id_allocator)`
is pure Python. Ports provide normalized source facts, typed coverage audit,
canonical source metadata and EP identity. This package has no network, file,
database, Open Targets or ADCdb collector. A real provider and data workspace
need separate reviewed work.

The request and every observation/audit must agree on HGNC/ADCdb target,
program and context. The source resolver must agree with each observation's
provenance. Duplicate or drifting EP identity, invalid source, failed sweep or
false completion rejects the entire round. `RunRejection` is an in-memory
rejection value for the external run audit; it never becomes a HOLD review
record or canonical Assessment.

## Evidence and proposal

- E1: serious attributed same-target ADC clinical normal-organ event, or
  human-relevant target-dependent normal-cell ADC killing with serious
  consequence, can reach `POSITIVE/DIRECT`. Attribution-pending serious events
  remain `INCONCLUSIVE/WEAK`. Qualified same-event refutation preserves both
  EP refs as `CONFLICTING/DIRECT`; a different event does not cancel liability.
- E2: validated normal-human surface binding or membrane antigen can reach
  `POSITIVE/INDIRECT_STRONG`. Qualified candidate-antibody non-binding reaches
  only context-bounded `NEGATIVE/DIRECT`; a sensitivity-audited key-cell
  membrane-protein non-detection reaches only
  `NEGATIVE/INDIRECT_STRONG`. Both negative routes require a complete clinical
  sweep and key-cell audit. A positive DIRECT signal survives unrelated gaps.
- E3 RNA and ordinary total-protein IHC remain `INCONCLUSIVE/WEAK`.
  Open Targets safety, human genetics, animal phenotype and non-ADC
  pharmacology are `SUPPORTING` and cannot occupy a liability ladder rung.

Each EP contains one source observation and no Direction, Strength or Candidate
decision. The separate `Proposal` carries the Gate-relative cell, EP roles,
domain refs, coverage gaps, same-event conflict refs and potential fatal-review
routes. `fatal_review_trigger` asks for human review; it never means automatic
KILL. `reviewer_seed` is a **partial, non-canonical draft aid**, not a complete
`Tgt05DecisionRecord` and not schema-valid on its own. A human reviewer must
complete the record, assess alternative explanations, and author any
`HUMAN_APPROVED` canonical Assessment. This module emits no GO/HOLD/KILL value.

## Verification boundary

Synthetic tests cover positive and negative authority, uncertainty, conflict,
integrity rejection, EP reuse, and frozen v2 binding. They do not validate
real source normalization, assay sensitivity or a clinical sweep. No real
ADCdb target or Open Targets safety data has been run through this module.
