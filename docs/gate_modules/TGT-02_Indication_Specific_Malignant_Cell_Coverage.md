# TGT-02 — Indication-Specific Malignant-Cell Coverage · MOD-TGT02 Construction Drawing

- Runtime Migration **PR E7** (`task_20260829_runtime-migration-pr-e7`)
- Machine contract: `src/contracts/gate_modules/tgt02_indication_specific_malignant_cell_coverage.yaml`
- Status: **construction contract + drawing only.** No implementation ships in
  this PR. `MIGRATION_PENDING` remains.

## What this document is

The frozen 施工图 for **MOD-TGT02**, the single primary Evidence Production
Module of Gate **TGT-02** under `ADC_TARGET_GATESET@1.0` /
`INST-CRC-REFRACTORY-ADC-TARGET-v1`.

CURRENT_SYSTEM v5 §6.4: *逐 Gate 绘制 Evidence Production Module 施工图；审核
通过后 Module 才可开工.* PR E7 delivers the drawing, the machine contract, the
validation / parity tests and the 17-item acceptance checklist. The Module
itself (`gate_modules/tgt02_indication_specific_malignant_cell_coverage/`) is
**PR E8**, and may start only after this contract is APPROVED. PR E8 also bumps
the TGT-02 `gate_binding` `primary_module_version` from `0.0.0` to `1.0.0`;
**PR E7 does not touch it.**

**Kernel invariant.** The kernel defines the contract; the Module implements
it. One-way dependency, exactly like `extensions/` and MOD-TGT01 / MOD-TGT05 /
MOD-TGT08: a future `gate_modules/` package MAY import kernel objects / Gate
identity / contracts; `src/` MUST NEVER import `gate_modules/`. The Module may
not modify the Gate id / name / candidate ownership, the `gate_question`, the
Evidence Ladder, the evidence ceiling, or the fatal / unknown / conflict /
inference semantics; it may not reason across Gates, lower a measurement
requirement, or turn `UNKNOWN` into `PASS` / `HOLD` / `KILL`.

## The three things MOD-TGT02 must never fuse

> **TGT-02 is a bidirectional scientific coverage gate.** High-quality
> protein / malignant-cell-attributed evidence can establish malignant-cell
> target coverage (`POSITIVE`) **or** its absence / rare-and-highly-heterogeneous
> state (`NEGATIVE`). Both are genuine Gate-relative scientific findings.

> **A TGT-02 `NEGATIVE` is not a fatal flag and not a `KILL`.** It means
> *"current admissible evidence shows refractory-mCRC malignant cells lack
> adequate population-level target expression coverage"* — a scientific
> assessment. A cross-cohort protein-level negative-coverage pattern that meets
> the PR D fatal condition is surfaced at most as a **machine-local
> `fatal_review` with `status = POTENTIAL_FATAL_PATTERN`**; the GateSet
> `fatal_gate_policy` (PR B) decides the Candidate-level consequence.

> **One pretty cohort is not a population-level answer.** A single positive or
> negative cohort is a `DIRECT`-class observation, never a completed
> cohort-level judgement. Only a completed, audited CRC coverage landscape
> (a module-local typed `CrcCohortCoverageCompletion`) aggregates single
> observations into a graded Direction.

Three distinct layers must stay separate:

| Layer | Answers |
|---|---|
| **TGT-02** | does the refractory-mCRC **malignant compartment** express the target at the **protein level**, across an **adequately powered cohort**, with **cohort-level consistency**? |
| **TGT-03 / TGT-04** | does expression **persist after treatment / in metastases** (TGT-03); is the target **on the cell surface at adequate density** (TGT-04) |
| **TGT-05** | is there a **normal-tissue liability / unfavorable therapeutic index** |

`NEGATIVE` is **reachable** on TGT-02 — unlike TGT-05 (`NEGATIVE` essentially
unreachable on the public path) and unlike TGT-08 (`NEGATIVE` = a *commercial*
opportunity judgement). A TGT-02 `NEGATIVE` is a *scientific* NEGATIVE about
malignant-cell coverage. It is still never a `KILL`, and it never discharges or
answers TGT-03 / TGT-04 / TGT-05.

## Template provenance

The 17-item checklist is the **approved PR E1 construction template**, already
validated by the merged PR E2 / E4 / E6 implementations. PR E7 reuses it rather
than reinventing it. Blueprint v1.3 §H2.8 is referenced by CURRENT_SYSTEM v5
but is **not in this repository or the File Library**, so the machine contract
marks `template_provenance.claim.not_claimed_verbatim_from_blueprint: true`.
Items **03 / 05 / 07 / 08** are bound to the frozen PR D
`crc_adc_target_gateset.yaml` `TGT-02` contract by a **normalized-equality
parity test**; item **04** additionally does a derived parity against
`evidence_required` + the ladder so no non-admissible evidence class is smuggled
in. The `inference_guard` — *"EVGAP-02 primarily contributes TGT-02; generic
CRC linkage does NOT discharge TGT-03"* — is pinned **verbatim**.

## Gate ordering

Fatal-first + cheap-first: **TGT-01 → TGT-05 → TGT-08 → TGT-02 → TGT-03 →
TGT-04 → TGT-06 → TGT-07**. TGT-01 calibrated the Module mechanics; TGT-05 was
the first fatal-first target-liability pruning Gate; TGT-08 was the external
opportunity gate and the first reachable canonical `NEGATIVE`; **TGT-02 is the
first indication-specific malignant-cell coverage gate** — its semantics are
frozen *before* any code because it slides very easily into "one pretty cohort ⇒
declare population-level coverage" and into confusing a scientific `NEGATIVE`
with a `KILL`.

## Normalized observation & the typed completion (frozen conceptual shape for PR E8)

**Normalized observation** (facts only — the provider never sets a rung, a
direction, or a pass/fail):
`observation_id`, `target_identity`, `context_key`, `landscape_as_of`,
`observation_kind` ∈ {`PROTEIN_COHORT`, `MALIGNANT_SC_SPATIAL`,
`TMA_TRANSCRIPT_PROTEIN_CONCORDANCE`, `BULK_CRC_RNA`, `PAN_CANCER_UNRESOLVED`,
`MATCHED_NORMAL_TUMOR`, `SEARCH_COMPLETION_AUDIT`},
`molecular_layer` ∈ {`PROTEIN`, `TRANSCRIPT`, `BOTH`}, `assay_method`,
`cohort_id` / `cohort_ids`, `cohort_n` *(raw fact, optional)*, `crc_specific`,
`malignant_cell_attribution` ∈ {`MALIGNANT`, `NON_MALIGNANT`, `UNRESOLVED`} +
`malignant_attribution_basis`,
`cohort_adequacy_status` ∈ {`QUALIFIED`, `NOT_ESTABLISHED`} +
`cohort_adequacy_basis`,
`expression_pattern` ∈ {`PRESENT_CONSISTENT`, `ABSENT`,
`RARE_HIGHLY_HETEROGENEOUS`, `MIXED_OR_UNRESOLVED`} + `expression_pattern_basis`
∈ {`SOURCE_REPORTED`, `HUMAN_REVIEWED_NORMALIZATION`},
`source_id` + source metadata + `retrieved_at`.

**`CrcCohortCoverageCompletion`** (PR E8 module-local frozen dataclass — a
run-level machine record, **not a seventh core object**): `attempted`,
`landscape_as_of`, `search_scope`, `sources_searched`,
`public_crc_coverage_search_complete`, `protein_cohort_search_complete`,
`malignant_compartment_sc_spatial_search_complete`,
`tma_concordance_search_complete`, `matched_normal_tumor_search_complete`,
`unresolved_items`, `qualifying_protein_cohort_ids`,
`qualifying_indirect_cohort_ids`, `audit_observation_id`. **No E6-style two
mandatory axes** — TGT-02 needs no artificial two-axis score; the Direct ladder
already states the protein cohort is `DIRECT` and sc / spatial / TMA is a lower
rung, so **overall Strength = the highest qualifying evidence class after the
public CRC coverage search is complete**. The `SEARCH_COMPLETION_AUDIT`
EvidencePackage carries a structured snapshot of this completion and is checked
by the **E6 completion-audit snapshot-parity gene** — a missing / drifted
snapshot is a HARD reject.

## The 17-item acceptance checklist

| # | Item | What MOD-TGT02 must satisfy |
|---|---|---|
| 1 | **Gate identity & version** | `TGT-02@1.0`, `ADC_TARGET_GATESET@1.0`, L04, candidate ownership `ADC_TARGET`, bound to `INST-CRC-REFRACTORY-ADC-TARGET-v1`. Inherited, not owned. |
| 2 | **Primary Module identity & version** | `MOD-TGT02` (deterministic: `MOD-<GATE without hyphen>`). Contract v`0.1.0`; implementation version `0.0.0` = declared, not built. PR E8 builds it and raises the version to ≥ 1.0; **PR E7 does not change the binding version.** |
| 3 | **Gate question** | Quoted **verbatim** from the frozen PR D contract: *"In refractory metastatic colorectal cancer, do malignant cells express the target at the protein level with adequate cohort-level consistency?"*. Not widened, not narrowed. It does **not** answer: post-treatment / metastatic persistence (TGT-03), cell-surface / density (TGT-04), a favorable therapeutic index (TGT-05), or whether the candidate is desirable. |
| 4 | **Admissible evidence classes** | The union of the frozen ladder classes: protein expression (validated IHC / quantitative proteomics / validated multiplex IF) in annotated CRC malignant cells across a powered CRC cohort; single-cell / spatial transcriptomics resolving expression to the CRC malignant compartment; CRC TMA scoring with malignant-cell attribution; matched normal-vs-tumor CRC comparison; CRC TMA transcript-and-protein concordance with malignant-cell attribution; bulk CRC RNA without malignant-cell deconvolution; pan-cancer datasets not resolved to CRC. **Not** admissible here: TGT-01 modality-precedent evidence; TGT-05 normal-tissue liability evidence; TGT-03 persistence evidence; TGT-04 / TGT-06 surface / density / internalization evidence; TGT-07 shedding evidence; TGT-08 competitive / IP evidence. Derived-parity tested against `evidence_required` + the ladder. |
| 5 | **Evidence Ladder & ceiling** | Reproduced verbatim from PR D (parity-tested). `DIRECT` = protein-level target expression in annotated CRC malignant cells across an adequately powered CRC cohort with malignant-cell attribution — *establishes indication-specific malignant-cell coverage at the protein level*. `INDIRECT_STRONG` = sc / spatial transcriptomic expression restricted to the CRC malignant compartment (not stroma or immune), **or** CRC TMA transcript-and-protein concordance with malignant-cell attribution — *strong support; protein-level confirmation is still required for a `DIRECT` call*. `WEAK` = bulk CRC RNA without malignant-cell deconvolution / pan-cancer datasets not resolved to CRC — *expression cannot be attributed to malignant cells; hypothesis only*. Ceiling: *protein-level malignant-cell expression across an adequately powered CRC cohort*. **Transcript never exceeds `INDIRECT_STRONG`**; quantity (many strong transcript datasets) never raises the ceiling to `DIRECT`. No new rungs. |
| 6 | **Direction interpretation** | Strength ⟂ Direction; never a numeric or ranking score. Direction is about the evidence *relative to the Gate question*. `POSITIVE` = evidence supports malignant-cell target coverage; `NEGATIVE` = evidence supports a lack of adequate malignant-cell coverage (absent, or rare and highly heterogeneous); `CONFLICTING` = admissible observations make genuinely incompatible coverage claims and no auditable pattern resolves them; `INCONCLUSIVE` = evidence does not resolve the question. **Frozen truth table (no E8 discretion), on a completed audited CRC coverage landscape:** a qualifying protein cohort supporting broad / consistent presence → `POSITIVE / DIRECT`; supporting absent expression → `NEGATIVE / DIRECT`; supporting rare + highly heterogeneous coverage → `NEGATIVE / DIRECT`; qualifying sc / spatial / TMA concordance supporting malignant-compartment presence → `POSITIVE / INDIRECT_STRONG`; supporting absent / strongly non-covered → `NEGATIVE / INDIRECT_STRONG`; incompatible coverage claims with no resolving pattern → `CONFLICTING /` overall rung; qualifying evidence but no directional resolution → a **graded `INCONCLUSIVE`** (`INCONCLUSIVE / DIRECT` or `INCONCLUSIVE / INDIRECT_STRONG`); **WEAK-only public evidence, or an incomplete CRC coverage search → `INCONCLUSIVE / UNKNOWN`** (never `INCONCLUSIVE / WEAK`). **Overall Strength = the highest qualifying evidence class** after the search is complete — there is **no** E6-style weaker-axis rule. **`"rare / highly heterogeneous"` is upstream-qualified** — MOD-TGT02 never computes it from a %-positive value, an H-score or a cohort n; it consumes an auditable `expression_pattern` + `expression_pattern_basis`. **Never:** a strong CRC RNA signal → `DIRECT`; stroma / immune / mixed-tissue expression → malignant coverage; a WEAK-only landscape → `INCONCLUSIVE / WEAK`; a valid audited multi-cohort finding characterizing coverage as `RARE_HIGHLY_HETEROGENEOUS` → `CONFLICTING` (that is `NEGATIVE`); absence of expression evidence → `POSITIVE`; a favorable therapeutic index read from matched normal-vs-tumor (that is TGT-05). |
| 7 | **Allowed / forbidden inference** | Verbatim from PR D (parity-tested). Allowed: *the target is present on CRC malignant cells at the population level*. Forbidden: *expression persists after treatment or in metastatic sites (TGT-03)*; *the target is on the cell surface or at adequate density (TGT-04)*; *a favorable therapeutic index (TGT-05)*. **`inference_guard` pinned verbatim:** *"The EVGAP-02 CRC linkage lock (v5 §11.2) primarily contributes evidence here. Generic CRC linkage does NOT discharge TGT-03."* — a CRC-linkage observation never stands in for TGT-03's own measurement. |
| 8 | **Fatal conditions** | Verbatim from PR D (parity-tested): *protein-level evidence of absent, or rare and highly heterogeneous, target expression in CRC malignant cells across cohorts* — a potential fatal signal that malignant-cell coverage is inadequate for an ADC. A **single** negative protein cohort is a `DIRECT`-class, `NEGATIVE`-**supporting observation** — **not yet** a `NEGATIVE / DIRECT` proposal and **not** a cross-cohort fatal pattern; a transcript-only negative signal is at most an `INDIRECT_STRONG`-class supporting observation, never fatal; a matched normal-vs-tumor comparison is context only. **Machine detection criteria for a candidate pattern:** protein-level observations, each with CRC malignant-cell attribution, each with a `QUALIFIED` `cohort_adequacy_status` + auditable `cohort_adequacy_basis`, each with a negative coverage class (`ABSENT` / `RARE_HIGHLY_HETEROGENEOUS`) + auditable `expression_pattern_basis`, on a completed audited CRC coverage landscape, with **cross-cohort support** — ***at least two* independent cohort identities** (or one declared multi-cohort analysis with at least two auditable `cohort_ids`). *"Across cohorts"* is **plural-cohorts logic — at least two, not a new `> 2` threshold**. Human-only: whether a cohort's adequacy basis is convincing; whether the cohorts are genuinely independent; whether the `RARE_HIGHLY_HETEROGENEOUS` characterisation is justified; whether assay / platform differences explain the convergence; whether it satisfies the GateSet fatal policy. The machine emits **at most** a module-local `fatal_review` with `status = POTENTIAL_FATAL_PATTERN` — **never** `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / a canonical fatal flag / `KILL` / `HOLD` / `Decision`. No numeric / %-positive / H-score / heterogeneity threshold. |
| 9 | **Evidence-source plan** | Frozen regime `PUBLIC_HYBRID`; `INST-CRC-REFRACTORY-ADC-TARGET-v1` is `PUBLIC_ONLY` → PR E7 designs the current public path only, **connects no provider**. *Direct authority:* validated CRC IHC / quantitative proteomics / validated multiplex IF in annotated malignant cells across an adequately powered CRC cohort, from a primary publication / repository record with malignant-cell attribution. *Indirect-strong:* sc / spatial transcriptomics with the CRC malignant compartment resolved (not stroma or immune); CRC TMA transcript-and-protein concordance with malignant-cell attribution. *Weak-only:* bulk CRC RNA without deconvolution; pan-cancer datasets not resolved to CRC. **Hard locks:** transcript never becomes protein; bulk / pan-cancer never becomes malignant-cell attributed; stromal / immune / mixed-tissue expression is not CRC malignant-cell expression (it may be a contextual observation, it does **not** discharge TGT-02); a matched normal-vs-tumor comparison contextualises CRC malignant-cell expression only (**never** *"normal low + tumor high ⇒ favorable therapeutic index"*); a weak-only class can never lift above `INCONCLUSIVE / UNKNOWN`; the number of qualifying transcript datasets never raises the ceiling above `INDIRECT_STRONG`. A malignant-cell coverage assessment is tracked **separately** from a CRC coverage-landscape-completeness assessment (mandatory components: protein cohort search; malignant-compartment sc / spatial search; CRC TMA transcript-and-protein concordance search; matched normal-vs-tumor comparison search). **No universal threshold** — no cohort-size / %-positive / H-score / heterogeneity cutoff, no ranking. Retrieval / entity-resolution / provenance / serialization are shared infrastructure (§6.5). |
| 10 | **Input contract** | `candidate_id` + the candidate's **canonical target identity** (single authoritative target — the MOD-TGT01 / PR E2 gene; no separate drift-prone target argument); `instantiation_id` + context; the frozen `gate_contract_ref` / `evidence_ladder_ref` and the Gate / GateSet version; run context (`run_id`, `code_commit`, retrieval window / `landscape_as_of`, `evidence_regime = PUBLIC_ONLY`); the **declared CRC coverage search scope** for this run; existing `evidence_refs`. **No implicit default context** — fail rather than assume an indication, modality, cohort or evidence regime not supplied by the Instantiation. |
| 11 | **EvidencePackage output contract** | Atomic and **Gate-neutral** — one neutral empirical observation, no grade / direction / TGT-02 ceiling / pass-fail stamped on it; full `provenance` from the resolved canonical `SourceIndex` record; `candidate_refs`; `measurement` / `claim`; observation-level `interpretation_boundary`; `derivation`. `study_context` carries the classification-driving fields (`observation_kind`, `molecular_layer`, `assay_method`, `cohort_id` / `cohort_ids`, `crc_specific`, `malignant_cell_attribution` + basis, `cohort_adequacy_status` + basis, `expression_pattern` + basis, `context_key`, `landscape_as_of`); a `SEARCH_COMPLETION_AUDIT` observation additionally carries a **structured snapshot** of the `CrcCohortCoverageCompletion` it certifies. An EP may say *"Cohort_A annotated malignant epithelial cells showed TARGET_A protein staining pattern X"*; it may **not** say *"TARGET_A passes TGT-02"*, *"has adequate coverage"*, *"is fatal"*, *"should be killed"*, or any TGT-03 / 04 / 05 conclusion. Reference an existing EP by `evidence_id` and reuse the **exact** canonical package — never copy / re-create (PR C). On reuse, every classification / absence driving field for that observation kind (including the completion snapshot for an audit EP) must be **present AND equal**; a missing or drifted field is a **HARD identity integrity failure** (PR E2 / E6 gene). Forward `status` / `superseded_by` never on `evidence.json`. |
| 12 | **Assessment proposal envelope contract** | The Module emits a **non-canonical, module-local proposal envelope** — *not* a `CandidateGateAssessment`. Carries the **canonical assessment identity pins** (`candidate_id`, `instantiation_id`, `context_id` / `context_version`, `gateset_id` / `gateset_version`, `gate_id` / `gate_version`) plus `proposed_direction` + `proposed_strength` (`POSITIVE` / `NEGATIVE` / `CONFLICTING` / `INCONCLUSIVE` × `DIRECT` / `INDIRECT_STRONG` / `WEAK` / `UNKNOWN`; never a Decision / score), `evidence_refs` `[{evidence_id, role}]` (`SUPPORTING` / `CONTRADICTING` / `CONTEXTUAL`), `aggregation_rationale`, `critical_unknowns`, `evidence_ceiling`, and the machine acceptance record. **Omits** `assessment_id`, `assessment_version`, the `review` block, any TGT-03 / 04 / 05 conclusion, a fatal flag, and a numeric / ranking score. The structured potential-fatal-pattern signal lives in a separate **module-local `fatal_review` record on the run result** (not a proposal field, not a `CandidateGateAssessment` field, not a new core object, not a Decision): `required` / `status` (`POTENTIAL_FATAL_PATTERN`) / `evidence_ids` / `cohort_ids` (the at-least-two independent CRC cohort identities) / `coverage_class` / `cohort_adequacy_basis_refs` / `expression_pattern_basis_refs` / `landscape_as_of` / `crc_coverage_search_scope`. `required = true` iff protein-level CRC malignant-cell-attributed observations across at least two independent cohort identities, each `QUALIFIED` + basis-backed, each with a negative coverage class + basis, on a completed audited landscape. **A `fatal_review` is an actionable handoff only on an accepted run** (PR E6 gene). The review surface constructs the canonical `CandidateGateAssessment` after `HUMAN_APPROVED` (item 14). PR E7 only defines the field lists — no new core object, no runtime code. |
| 13 | **Machine acceptance criteria** | Every EP validates; the candidate's canonical target identity matches every observation's `target_identity` (a mismatch is a HARD misbinding failure); every `source_id` resolves to a canonical `SourceIndex` record whose metadata matches, and every `evidence_id` resolves (PR C / PR E2 genes); **exact canonical EP reuse parity** passes; the **completion ↔ `SEARCH_COMPLETION_AUDIT` snapshot parity** passes (a missing / drifted snapshot is a HARD failure — PR E6 gene); every evidence class is in the item-4 admissible list and none in `not_admissible`; **transcript-level evidence never proposes above `INDIRECT_STRONG`**; bulk / pan-cancer never becomes malignant-cell attributed; protein without malignant-cell attribution never reaches `DIRECT`; every `QUALIFIED` `cohort_adequacy_status` carries an auditable `cohort_adequacy_basis` and every `ABSENT` / `RARE_HIGHLY_HETEROGENEOUS` `expression_pattern` carries an auditable `expression_pattern_basis` (a missing / drifted basis is a HARD failure); the **mandatory CRC coverage landscape is complete** for the path taken (no early grade on a single cohort); `proposed_direction × proposed_strength` is exactly the item-6 truth-table result — **WEAK-only → `INCONCLUSIVE / UNKNOWN` (never `INCONCLUSIVE / WEAK`)**, `INCONCLUSIVE / UNKNOWN` carries zero `evidence_refs`, a graded `INCONCLUSIVE` carries `CONTEXTUAL` refs; if `fatal_review.required = true` its status is `POTENTIAL_FATAL_PATTERN` (never `PUBLIC_FATAL_SIGNAL_ESTABLISHED`), it carries at least two independent `cohort_ids` with the basis refs, and it is surfaced only on an accepted run; `fatal_review` is not a proposal-envelope field; dedup; **no numeric / ranking score anywhere; no cohort-size / %-positive / H-score / heterogeneity threshold**; **no TGT-03 persistence, TGT-04 surface / density, or TGT-05 therapeutic-index conclusion; no `PUBLIC_FATAL_SIGNAL_ESTABLISHED` / `KILL` / `HOLD` / `Decision`** anywhere. On failure → rejected with a machine reason. A **HARD identity / provenance / completion-consistency / classification-qualification integrity failure** rejects the **whole run** — never degraded to an accepted `UNKNOWN` (PR E2 / E6 gene); `UNKNOWN` from a genuinely incomplete public CRC coverage search is *not* an integrity failure. |
| 14 | **Human acceptance / review surface** | The human sees: proposed direction + strength + rationale; each EP's claim / source / `interpretation_boundary` (per-cohort evidence, assay / molecular layer, malignant-cell attribution basis, cohort adequacy basis, expression-pattern basis); the ladder rung per EP; the `CrcCohortCoverageCompletion` snapshot (which mandatory components are complete / incomplete, the qualifying cohort ids); the module-local `fatal_review` record (status `POTENTIAL_FATAL_PATTERN`, the contributing `evidence_ids` / `cohort_ids` / `coverage_class` / basis refs); `critical_unknowns`; the machine acceptance record. Human-only: whether the direction / strength is scientifically correct for TGT-02; whether a cohort is genuinely adequately powered and the malignant-cell attribution convincing; whether a source-level *"rare and highly heterogeneous"* interpretation is justified; whether the cohorts are genuinely independent / non-overlapping; whether a cross-cohort negative pattern satisfies the GateSet fatal policy; final `HUMAN_APPROVED` → the review surface constructs the canonical `CandidateGateAssessment`. |
| 15 | **Failure / UNKNOWN / conflict behaviour** | Retrieval failure → a machine reason, not a partial assessment. Direction / strength follow the item-6 truth table. **WEAK-only bulk / pan-cancer → `INCONCLUSIVE / UNKNOWN`** (never `INCONCLUSIVE / WEAK`; *"Only bulk RNA available → UNKNOWN, not a pass"*; zero `evidence_refs`). **Incomplete CRC coverage search → `INCONCLUSIVE / UNKNOWN`** — do not grade early on a pretty intermediate result (that is what the completion state is for). **High-quality but nondirectional evidence → a graded `INCONCLUSIVE`**. **Positive + negative biological findings with no qualified pattern resolution → `CONFLICTING`**; a **qualified rare-highly-heterogeneous multi-cohort pattern → `NEGATIVE`, not automatically `CONFLICTING`**. **`EXPERIMENT_REQUIRED`** is used **only** when the enumerated public CRC coverage source space is completed / exhausted **and** the unresolved question needs a **new** malignant-cell-resolved protein / adequately-powered-cohort measurement (e.g. public sc / spatial consistently supports malignant-cell expression but no adequate protein cohort exists → `POSITIVE / INDIRECT_STRONG` + `critical_unknown` `"protein-level malignant-cell cohort confirmation"` = `EXPERIMENT_REQUIRED`; only bulk RNA + exhausted source space → `INCONCLUSIVE / UNKNOWN` + `EXPERIMENT_REQUIRED`). A known-but-unfetched public dataset, or an incomplete public cohort search, is `PUBLIC_RESOLVABLE`; an existing source whose access / annotation currently prevents resolution is `CURRENTLY_UNRESOLVABLE`. Once `EXPERIMENT_REQUIRED` is reached the public Module stops chasing weaker proxies. `UNKNOWN` is never silently `PASS` / `HOLD` / `KILL`; `UNKNOWN` from an incomplete search is *not* an integrity failure; a scientific `NEGATIVE` is never a fatal flag and never a `KILL`. |
| 16 | **Stop rule** | The mandatory public CRC coverage landscape is **completed and audited before any graded Direction**; a single positive or negative cohort is never a completed population-level answer. **Normal stop** requires all of: the mandatory CRC cohort coverage landscape complete (item 9 components) and audited; the highest available qualifying evidence class determined; remaining public evidence cannot change Direction / Strength. **Exhaustion stop:** the enumerated public CRC coverage source space is exhausted → the residual `critical_unknown` is classified (`PUBLIC_RESOLVABLE` / `EXPERIMENT_REQUIRED` / `CURRENTLY_UNRESOLVABLE`) → stop. **Potential-fatal trigger:** a machine-detected cross-cohort protein-level negative-coverage pattern (item 8) may stop the chase for weaker bulk / pan-cancer proxy evidence — **but only after** the necessary cohort coverage completeness is satisfied; **the Module never stops on the first negative cohort**. |
| 17 | **Downstream consumer / handoff** | The Module hands off `EvidencePackage`s + one **assessment proposal envelope** to the human review surface (item 14), and separately the module-local `fatal_review` record for human Gate review and the GateSet fatal policy. Only **after** `HUMAN_APPROVED` does the review surface construct the canonical `CandidateGateAssessment`, and *that* record is consumed by: the `MatrixView` cell `(candidate_id, TGT-02)` (PR C); the `ADC_TARGET_GATESET` decision layer that turns the eight TGT assessments into a Candidate-level `Decision` (PR B); the next Gate (`TGT-03`) as **context only** — never as a substitute for its own measurement, and never via generic CRC linkage (item 7 `inference_guard`); experimental validation when a `critical_unknown` is `EXPERIMENT_REQUIRED`. This Module does **not** construct a `CandidateGateAssessment` or emit a `HUMAN_APPROVED` record, produce a Candidate-level `Decision` / `KILL`, emit `PUBLIC_FATAL_SIGNAL_ESTABLISHED` (the machine emits at most a `fatal_review` `POTENTIAL_FATAL_PATTERN`, and only on an accepted run), make a TGT-03 / TGT-04 / TGT-05 conclusion, let generic CRC linkage discharge TGT-03, flip Direction on candidate desirability, grade a Direction before the mandatory CRC coverage landscape is complete, write to another Gate's index or assessment, or modify the Matrix. |

## Deferred to PR E8+

- The new top-level
  `gate_modules/tgt02_indication_specific_malignant_cell_coverage/`
  implementation (providers, adapters, extractor, normalizer, runner,
  EvidencePackage writer, assessment proposer, the `CrcCohortCoverageCompletion`
  typed record, the `fatal_review` detector) and the `primary_module_version`
  bump to `1.0.0`.
- Connecting any retrieval provider or dataset (GEO / HPA / CPTAC / single-cell /
  spatial / TMA repositories).
- The other four TGT primary Modules (`TGT-03 → TGT-04 → TGT-06 → TGT-07`).

PR E7 does **not** create a generic GateModule framework, an abstract base
class, or refactor MOD-TGT01 / MOD-TGT05 / MOD-TGT08. No "平台化" yet.
