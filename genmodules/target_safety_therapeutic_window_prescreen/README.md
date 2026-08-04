# Public-Evidence Target Safety and Therapeutic-Window Pre-screen Engine

This GenModule performs a conservative, target-level ADC safety pre-screen from
already-normalized public evidence. It does **not** predict a product-specific
therapeutic window and does not replace Gate evaluation, toxicology, or human
decision-making.

## Six evidence axes

1. Normal-tissue and cell-type expression.
2. Surface localization and vascular accessibility.
3. Normal-cell antigen density.
4. Soluble antigen, shedding, and target sink.
5. Existing modality exposure and toxicity attribution.
6. Tissue consequence and recoverability.

Evidence levels are `A` (human causal), `B` (human protein/cell-resolved), `C`
(multi-omic concordance), `D` (single or indirect), and `U` (unknown).
Unknown remains unresolved; it is never converted into safety.

## Decision semantics

The evaluator applies fatal flags first:

- `KILL`: a defined target-level fatal condition is supported.
- `HOLD`: critical evidence is unknown, conflicting, or unresolved.
- `CONDITIONAL_GO`: no fatal condition and a plausible exploitable differential
  exists, with explicit mitigation work.
- `GO`: no public target-intrinsic fatal flaw was found; this is not proof of a
  therapeutic window.

## Runtime boundary

The package is pure and in-memory. Evidence claims carry only `external:`
references. A runtime may resolve those references under:

```text
${BIOWORKSPACE_ROOT}/DATA/target_safety_therapeutic_window_prescreen/
├── raw/       immutable source downloads and manifests
├── processed/ normalized evidence tables and provenance
└── result/    run-specific assessment packages and reports
```

The repository contains no source data, database, cache, result, model weight,
or runtime artifact. The external runtime must record source versions,
checksums, policy version, code commit, and unresolved evidence.
