# Contracts

This layer contains implementation-facing contracts and schemas derived from
the canonical architecture documents.

It must not contain datasets, persisted records, or runtime data stores.

Current sponsor-relative strategy contracts:

- `sponsor_strategy.yaml` defines `DevelopmentSponsorProfile@0.1.0` and
  `ProgramThesis@0.1.0`.
- `sponsor_strategy.py` validates these shapes in memory and requires runtime
  references to use the `external:` scheme.

The contracts do not grant program commitment, execute Gates, or persist
instances.
