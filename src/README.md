# StelligenOS Implementation

This directory is the implementation boundary for StelligenOS.

The initial skeleton mirrors the architecture contract without introducing
runtime behavior or data storage. External data and processing remain outside
this repository.

## Layers

- `contracts/`: implementation-facing contract adapters and schemas.
- `lifecycle/`: lifecycle state and transition logic.
- `capabilities/`: capability implementations.
- `cross_cutting/`: audit, versioning, Knowledge Ledger, IP/FTO, and stage-aware due diligence.
- `objects/`: core domain object implementations.
- `repository/`: external-workspace integration boundaries.
