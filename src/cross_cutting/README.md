# Cross-Cutting

This layer contains cross-cutting implementation boundaries for Knowledge
Ledger, model lifecycle, IP/FTO, stage-aware Due Diligence, audit, and
versioning.

IP/FTO, Due Diligence, and Portfolio implementations remain external. This
layer contains ports and contracts only; it must not become a legal analysis,
diligence record, portfolio, or capital data store.

`model_contracts.py` validates external `model_id@SemVer` identities and
`ModelLifecycleStandard@1.0.0` metadata. Model registries, model artifacts,
governance records, and promotion decisions remain outside this repository.
