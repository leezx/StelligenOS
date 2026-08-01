# Cross-Cutting

This layer contains cross-cutting implementation boundaries for Knowledge
Ledger, IP/FTO, stage-aware Due Diligence, audit, and versioning.

IP/FTO, Due Diligence, and Portfolio implementations remain external. This
layer contains ports and contracts only; it must not become a legal analysis,
diligence record, portfolio, or capital data store.
