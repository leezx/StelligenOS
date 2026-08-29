# TGT-05 — Normal-Tissue Fatal Liability · MOD-TGT05 Construction Drawing

- Runtime Migration **PR E3** (`task_20260829_runtime-migration-pr-e3`)
- Machine contract: `src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml`
- Status: **construction contract + drawing only.** No implementation ships in
  this PR. `MIGRATION_PENDING` remains.

## What this document is

The frozen施工图 for **MOD-TGT05**, the single primary Evidence Production
Module of Gate **TGT-05** under `ADC_TARGET_GATESET@1.0` /
`INST-CRC-REFRACTORY-ADC-TARGET-v1`.

CURRENT_SYSTEM v5 §6.4: *逐 Gate 绘制 Evidence Production Module 施工图；审核
通过后 Module 才可开工.* PR E3 delivers the drawing, the machine contract, the
validation / parity tests and the 17-item acceptance checklist. The Module
itself (`gate_modules/tgt05_normal_tissue_fatal_liability/`) is **PR E4**, and
may start only after this contract is APPROVED. PR E4 also bumps the TGT-05
`gate_binding` `primary_module_version` from `0.0.0` to `1.0.0`; **PR E3 does
not touch it.**

**Kernel invariant.** The kernel defines the contract; the Module implements
it. One-way dependency, exactly like `extensions/` and MOD-TGT01: a future
`gate_modules/` package MAY import kernel objects / Gate identity / contracts;
`src/` MUST NEVER import `gate_modules/`. The Module may not modify the Gate id /
name / candidate ownership, the `gate_question`, the Evidence Ladder, the
evidence ceiling, or the fatal / unknown / conflict / inference semantics; it
may not reason across Gates, lower a measurement requirement, or turn `UNKNOWN`
into `PASS` / `HOLD` / `KILL`.

## The one thing MOD-TGT05 does — and does not — do

> **MOD-TGT05's job is not to prove a target is "safe". It is to find a
> target-level normal-tissue on-target / off-tumor liability as reliably as
> possible.** Public evidence can strongly confirm a liability; it usually
> cannot confirm the absence of one.

This is the biggest scientific-structure difference from TGT-01. TGT-05 is a
**one-way liability detector**, never a safety predictor. It does **not** answer:
a product-specific therapeutic window (this is a target-level gate); whether the
candidate is desirable (Direction is about the evidence, not the candidate);
tumor selectivity or malignant-cell coverage (TGT-02 / TGT-04). A TGT-05
`POSITIVE` / `DIRECT` is a *bad candidate signal* — but the Module does not flip
Direction, and `HOLD` / `KILL` is the GateSet Decision policy's job (PR B).

## Template provenance

The 17-item checklist is the **approved PR E1 construction template**, already
validated by the merged PR E2 implementation. PR E3 reuses it rather than
reinventing it. Blueprint v1.3 §H2.8 is referenced by CURRENT_SYSTEM v5 but is
**not in this repository or the File Library**, so the machine contract marks
`template_provenance.claim.not_claimed_verbatim_from_blueprint: true`. Items
**03 / 05 / 07 / 08** are bound to the frozen PR D `crc_adc_target_gateset.yaml`
`TGT-05` contract by a **normalized-equality parity test** — not a hand
approximation.

## Gate ordering

Fatal-first + cheap-first: **TGT-01 → TGT-05 → TGT-08 → TGT-02 → TGT-03 →
TGT-04 → TGT-06 → TGT-07**. TGT-01 calibrated the Module mechanics; **TGT-05 is
the first true fatal-first target-liability pruning Gate**, which is why its
semantics are frozen *before* any code — it slides very easily into an
incorrect "public-data prediction of the therapeutic window".

## The 17-item acceptance checklist

| # | Item | What MOD-TGT05 must satisfy |
|---|---|---|
| 1 | **Gate identity & version** | `TGT-05@1.0`, `ADC_TARGET_GATESET@1.0`, L04, candidate ownership `ADC_TARGET`, bound to `INST-CRC-REFRACTORY-ADC-TARGET-v1`. Inherited, not owned. |
| 2 | **Primary Module identity & version** | `MOD-TGT05` (deterministic: `MOD-<GATE without hyphen>`). Contract v`0.1.0`; implementation version `0.0.0` = declared, not built. PR E4 builds it and raises the version to ≥ 1.0; **PR E3 does not change the binding version.** |
| 3 | **Gate question** | Quoted **verbatim** from the frozen PR D contract: *"Is there evidence of accessible normal-human-tissue expression, or observed target-mediated toxicity, that creates a potentially material on-target / off-tumor liability for ADC development? (fatal-first gate — a target-level public-evidence gate, not a product-specific therapeutic-window judgement)"*. Not widened, not narrowed. |
| 4 | **Admissible evidence classes** | Same-target ADC clinical on-target/off-tumor toxicity (with target attribution); same-target non-ADC clinical toxicity (CAR-T / TCE / naked Ab); protein-level normal-tissue expression in vital organs from validated human atlases; normal-tissue single-cell expression; translationally relevant same-target NHP toxicity; RNA-only normal-tissue atlases; rodent-only data; vital-organ coverage (CNS, cardiac, hepatic, pulmonary, hematopoietic, GI). **Not** admissible here: TGT-01/02/03/04/06/07/08 evidence. |
| 5 | **Evidence Ladder & ceiling** | Reproduced verbatim from PR D (parity-tested). `DIRECT` = clinical on-target/off-tumor toxicity attributable to this target **from an ADC against the same target**. `INDIRECT_STRONG` = same-target non-ADC clinical toxicity / validated human normal-tissue protein atlas in vital organs / translationally relevant same-target NHP toxicity. `WEAK` = RNA-only normal-tissue atlases / rodent-only data. Ceiling: *clinical (ADC-specific for DIRECT) or protein-level human normal-tissue expression in vital organs; RNA-only atlases do not reach it.* No new rungs, no exceeding the ceiling. |
| 6 | **Direction interpretation** | Strength ⟂ Direction. **Direction describes the evidence relative to the Gate question, not candidate desirability.** One frozen truth table, no E4 discretion: `DIRECT` liability evidence → `POSITIVE / DIRECT`; `INDIRECT_STRONG` liability evidence → `POSITIVE / INDIRECT_STRONG`; **`WEAK`-only liability hypothesis → `INCONCLUSIVE / WEAK`** (PR D: "liability cannot be graded; hypothesis only" — not POSITIVE); no qualifying liability evidence + coverage incomplete/exhausted → `INCONCLUSIVE / UNKNOWN`; **never** absence-of-risk → `NEGATIVE / safe` (`NEGATIVE` is essentially unreachable). **Precedence:** once a `DIRECT`/`INDIRECT_STRONG` liability is established, an uncovered other vital organ does **not** downgrade the direction to `UNKNOWN` — it stays `POSITIVE`, coverage gaps go into `critical_unknowns`. `CONFLICTING` = **only** a target-attribution dispute *on the same liability observation*; a refutation earns **no** `NEGATIVE` rung; "one ADC has toxicity, another has no reported toxicity" is *not* contradictory. Module proposes both, never a score, never flips Direction on desirability. |
| 7 | **Allowed / forbidden inference** | Verbatim from PR D (parity-tested). Allowed: *the presence, and plausibility / severity signals, of a normal-tissue on-target liability class*. Forbidden: negative RNA/IHC/atlas ⇒ absence of liability or safety; tumor selectivity (TGT-02) ⇒ normal-tissue safety; non-ADC modality severity transfers directly to an ADC therapeutic window; a product-specific therapeutic-window conclusion. |
| 8 | **Fatal conditions** | Verbatim from PR D (parity-tested): a *convergent target-mediated on-target/off-tumor toxicity pattern* across **materially distinct** ADC constructs against the same target — a potential target-intrinsic fatal signal. Frozen layers: 1 same-target ADC + explicit target-mediated toxicity → **DIRECT liability, NOT fatal**; human protein expression in a vital organ / same-target non-ADC toxicity / translationally relevant NHP toxicity → **INDIRECT_STRONG, NOT fatal**; ≥2 materially distinct same-target ADC constructs with convergent target-mediated normal-tissue toxicity → **potential fatal signal**. Each clinical ADC toxicity observation must be auditable for: `program_id`, actual target identity, construct fingerprint (antibody/binder, linker, payload, format), affected normal tissue, toxicity phenotype, **observed severity for THIS product** (never elevated to target-wide), target-attribution basis, primary source. "Materially distinct", "truly target-mediated" and "biologically meaningful convergence" stay **human-review** calls. The machine emits **at most** a module-local `fatal_review` record with `status = POTENTIAL_FATAL_PATTERN` — **never** `PUBLIC_FATAL_SIGNAL_ESTABLISHED` (PR D itself only calls it "a potential target-intrinsic fatal signal"). It never performs a Candidate-level `KILL`, never auto-declares target-wide fatal from a grade ≥ X toxicity or a shared AE term, and emits **no numeric severity score**. |
| 9 | **Evidence-source plan** | Frozen contract regime is `PUBLIC_HYBRID`, but `INST-CRC-REFRACTORY-ADC-TARGET-v1` is `PUBLIC_ONLY` → PR E3 designs the **current public path only**, no experiments. *Direct authority*: same-target ADC clinical on-target/off-tumor toxicity **with target attribution** from a resolvable primary regulatory / trial / clinical publication / company primary disclosure. *Indirect-strong*: same-target non-ADC clinical toxicity; validated human normal-tissue protein atlas covering vital organs; translationally relevant same-target NHP toxicity. *Weak-only*: RNA-only normal-tissue atlases; rodent-only data. **Hard locks:** RNA-only ✗→ protein; whole-tissue protein ✗→ cell-surface accessibility; non-ADC severity ✗→ ADC; negative atlas ✗→ safety. A **vital-organ coverage map** (CNS / cardiac / hepatic / pulmonary / hematopoietic / GI) is tracked *separately* from liability evidence. **No universal threshold** — no organ count, TPM/FPKM cutoff, IHC score, or severity grade cutoff. **PR E3 connects no provider.** Retrieval / entity-resolution / provenance / serialization are shared infrastructure (§6.5). |
| 10 | **Input contract** | `candidate_id` + the candidate's **canonical target identity** (single authoritative target — the MOD-TGT01 / PR E2 gene; no separate drift-prone target argument); `instantiation_id` + context; the frozen `gate_contract_ref` / `evidence_ladder_ref`; run context (`run_id`, retrieval window, `evidence_regime = PUBLIC_ONLY`); existing `evidence_refs`. **No implicit default scientific context** — fail rather than assume. |
| 11 | **EvidencePackage output contract** | Atomic and **Gate-neutral** — observation-level meaning only, no grade / direction, **no TGT-05 ceiling stamped on it**; full `provenance` from the resolved canonical `SourceIndex` record; `candidate_refs`; `measurement` / `claim`; observation-level `interpretation_boundary`; `derivation`. A clinical ADC toxicity observation carries the item-8 convergence-audit fields in `study_context`. Reference an existing EP by `evidence_id` and reuse the **exact** canonical package — never copy / re-create (PR C). On reuse, every classification-driving `study_context` field must be **present AND equal**; a missing or drifted field is a **HARD identity integrity failure** (PR E2 gene). Forward `status` / `superseded_by` never on `evidence.json` (PR C). |
| 12 | **Assessment proposal envelope contract** | The Module emits a **non-canonical, module-local proposal envelope** — *not* a `CandidateGateAssessment`. Carries the **canonical assessment identity pins** (`candidate_id`, `instantiation_id`, `context_id` / `context_version`, `gateset_id` / `gateset_version`, `gate_id` / `gate_version`) plus `proposed_direction` + `proposed_strength` (never a Decision / score), `evidence_refs` `[{evidence_id, role}]`, `aggregation_rationale`, `critical_unknowns`, `evidence_ceiling`, and the machine acceptance record. **Omits** `assessment_id`, `assessment_version`, the `review` block, any product-specific therapeutic-window conclusion, **and a fatal flag**. The structured potential-fatal-pattern signal lives in a separate **module-local `fatal_review` record on the run result** (not the proposal envelope, not a `CandidateGateAssessment` field, not a new core object, not a change to `assessment.schema.json`): `required` / `status` (`POTENTIAL_FATAL_PATTERN`) / `evidence_ids` / `program_ids` / `construct_fingerprints` / `affected_tissues` / `target_attribution_basis_refs`. `required = false` for a single `DIRECT` liability; `required = true` for a candidate convergence pattern (≥2 programs, each with an auditable fingerprint + disclosed target-attribution). The review surface constructs the canonical `CandidateGateAssessment` after `HUMAN_APPROVED` (item 14). PR E3 only defines the field lists — no new core object, no runtime code. |
| 13 | **Machine acceptance criteria** | Every EP validates; every `source_id` resolves to a canonical `SourceIndex` record whose metadata matches, and every `evidence_id` resolves (PR C / PR E2 genes); every evidence class is in the item-4 admissible list and none in `not_admissible`; strength ≤ the highest rung actually met; the **item-16 mandatory completion conditions for the path taken** are satisfied; dedup; **no numeric score, no biological threshold**; **no product-specific therapeutic-window conclusion anywhere**. On failure → rejected with a machine reason. A **HARD identity / provenance integrity failure** (target misbinding, missing/mismatched canonical source, incompatible canonical EP) rejects the **whole run** — never degraded to an accepted `UNKNOWN`; `UNKNOWN` from genuinely incomplete coverage is *not* an integrity failure (PR E2 gene). |
| 14 | **Human acceptance / review surface** | The human sees: proposed direction + strength + rationale; each EP's claim / source / `interpretation_boundary` (incl. the item-8 convergence-audit fields); the ladder rung per EP; the **vital-organ coverage map** (covered / uncovered); the **module-local `fatal_review` record** (status `POTENTIAL_FATAL_PATTERN`, the contributing `evidence_ids` / `program_ids` / `construct_fingerprints` / `affected_tissues` / `target_attribution_basis_refs`); `critical_unknowns`; the machine acceptance record. Human-only: whether the aggregate is scientifically right for TGT-05; **whether the constructs are "materially distinct", whether the toxicity is truly target-mediated, and whether the convergence is biologically meaningful** — i.e. whether a `POTENTIAL_FATAL_PATTERN` is a real target-intrinsic fatal signal; whether a "same target" call is right; final `HUMAN_APPROVED` → the review surface constructs the canonical `CandidateGateAssessment`. TGT-05's human-only judgement is materially heavier than TGT-01's. |
| 15 | **Failure / UNKNOWN / conflict behaviour** | Retrieval failure → a machine reason, not a partial assessment. Direction/strength follow the item-6 frozen truth table: `WEAK`-only → `INCONCLUSIVE / WEAK` (never `POSITIVE`); a `DIRECT`/`INDIRECT_STRONG` liability → `POSITIVE`, and it is **not** downgraded to `UNKNOWN` because another organ is uncovered (the gap goes into `critical_unknowns`). No admissible liability evidence + incomplete coverage → `INCONCLUSIVE` / `UNKNOWN`, never `PASS`, never "safe", never `NEGATIVE` (*"Incomplete normal-tissue coverage → UNKNOWN, never auto-PASS"*). Conflicting → `CONFLICTING` **only** with genuinely contradictory admissible target-attribution evidence *on the same observation*; a refutation earns **no** `NEGATIVE` rung. Vital-organ gap closable only by non-public data → `critical_unknown` resolution `EXPERIMENT_REQUIRED`, stop. **`UNKNOWN` is never silently `PASS` / `HOLD` / `KILL`**, `UNKNOWN` from incomplete coverage is **not** an integrity failure, and **absence of public risk evidence is neither a safety-`NEGATIVE` nor a stop condition**. |
| 16 | **Stop rule** | Asymmetric, fatal-sweep-mandatory. **Path A** — the machine detects an *apparent* pattern (≥2 same-target ADC toxicity observations, each from a distinct program, each with an auditable construct fingerprint + a disclosed target-attribution basis, an apparently convergent normal-tissue phenotype) → set `fatal_review.required = true`, `status = POTENTIAL_FATAL_PATTERN`, **provisionally** stop chasing weaker atlas / RNA evidence, hand off to human review. The machine does **not** mark `PUBLIC_FATAL_SIGNAL_ESTABLISHED` — that call requires the item-8 human-review-reserved judgements (materially distinct / truly target-mediated / meaningful convergence) plus the GateSet `fatal_gate_policy`. **Path B** — only one `DIRECT` ADC toxicity → **cannot** stop; must complete the same-target ADC construct inventory (active / approved **and** discontinued / failed) + the toxicity / discontinuation / target-attribution sweep (a 2nd independent construct can lift `DIRECT` liability into a `POTENTIAL_FATAL_PATTERN`). **Path C** — no `DIRECT` clinical liability → must complete the human protein vital-organ coverage sweep + the non-ADC same-target toxicity sweep + the relevant same-target NHP sweep + the RNA-only supporting sweep; if a key coverage gap is unresolvable by public sources → `critical_unknown` = `EXPERIMENT_REQUIRED`, do not keep searching weaker proxies. Core: *absence of public risk evidence is not a completed safety assessment.* |
| 17 | **Downstream consumer / handoff** | The Module hands off `EvidencePackage`s + one **assessment proposal envelope** to the human review surface (item 14). Only **after** `HUMAN_APPROVED` does the review surface construct the canonical `CandidateGateAssessment`, and *that* record is consumed by: the `MatrixView` cell `(candidate_id, TGT-05)` (PR C); the `ADC_TARGET_GATESET` decision layer that turns the eight TGT assessments into a Candidate-level `Decision` (PR B); the next Gate (`TGT-08`) as context only; experimental validation when `EXPERIMENT_REQUIRED`. The Module's own output never enters the `MatrixView` or the decision layer directly. This Module does **not** construct a `CandidateGateAssessment` or emit a `HUMAN_APPROVED` record, produce a Decision / `KILL`, emit `PUBLIC_FATAL_SIGNAL_ESTABLISHED` (it emits at most a `fatal_review` `POTENTIAL_FATAL_PATTERN`), make a product-specific therapeutic-window conclusion, flip Direction on candidate desirability, downgrade an observed `DIRECT`/`INDIRECT_STRONG` liability to `UNKNOWN` for an uncovered organ, write to another Gate's index or assessment, or modify the Matrix. |

## Deferred to PR E4+

- The new top-level `gate_modules/tgt05_normal_tissue_fatal_liability/`
  implementation (providers, adapters, extractor, normalizer, runner, dry-run
  executor, EvidencePackage writer, assessment proposer) and the
  `primary_module_version` bump to `1.0.0`.
- Connecting any retrieval provider or dataset.
- The other six TGT primary Modules (`TGT-08 → TGT-02 → TGT-03 → TGT-04 →
  TGT-06 → TGT-07`).

PR E3 does **not** create a generic GateModule framework, an abstract base
class, or refactor MOD-TGT01. No "平台化" yet.
