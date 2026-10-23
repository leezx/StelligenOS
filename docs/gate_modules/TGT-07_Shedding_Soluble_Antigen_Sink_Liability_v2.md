# MOD-TGT07@2.0.0 — B2 implementation note

Status: **BUILT_UNBOUND**. The v2 Gate contract still binds `MOD-TGT07@0.0.0`;
the CRC v2 Instantiation remains `HOLD`.

The module is pure Python with injected provider, source resolver, Evidence
Library and ID allocator ports. It neither retrieves data nor authors a
canonical Assessment or Candidate Decision. The v1 package and binding remain
unchanged. This separate v2 package adapts the previously verified v1
classification, completion, provenance, aggregation and fatal-review structure
to the frozen TGT-07@2.0 contract.

## B2 evidence rules

- A same-target, soluble-antigen-attributed clinical PK/PD sink effect or a
  validated TMDD materiality result can support `POSITIVE/DIRECT` in its named
  sink-exposure context. A no-material-sink `NEGATIVE/DIRECT` requires a
  validated intended-ADC TMDD result, the same construct as the run, documented
  concentration, turnover, affinity, dose/exposure and assay-unit bases, and a
  completed audited landscape. There is no module-owned numerical cutoff.
- Quantified CRC-patient soluble antigen reaches `INDIRECT_STRONG` only with a
  source-stated assay unit and detection-limit basis. Below-limit observations
  remain contextual. Sheddase and validated isoform facts remain
  `INDIRECT_STRONG`; predictions and analogies remain weak.
- A truthful incomplete search or unqualified TMDD yields an accepted
  `INCONCLUSIVE/UNKNOWN` with critical unknowns. A missing, contradictory or
  drifted completion audit, target/program/construct/source mismatch, duplicate
  observation ID or incompatible reused EP rejects the whole run. Rejection
  returns no proposal, no partial new EPs and no reused EP IDs.
- The proposal exposes every qualified DIRECT context separately, including
  both EP sides of a same-context conflict and the completion audit EP. An
  independent clean material-sink context remains visible even when another
  context conflicts. Its proposal remains non-canonical. A fatal-review trigger
  asks for human adjudication and cannot issue KILL.

## Evidence and run boundary

Each accepted atomic EP is Gate-neutral and pins program, construct, input
bases, observation identity, source provenance and search context. The provider
is responsible for source-grounded normalization and scientific qualification
of the TMDD inputs; the module checks the required typed bases and identity,
but cannot validate an experimental model from text alone. B2 tests use
synthetic records only. No ADCdb, Open Targets, patient or assay data have run
through this package. B3 resolver, B4 activation and a separately approved
external DATA run are still required before full target evaluation.
