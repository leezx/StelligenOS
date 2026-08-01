# Gate Model Rule

This is the software-only contract boundary for AssetGenOS historical
Gate Model Rules. It is not a Gate implementation, model registry, database,
or rule execution runner.

## Scope

- Stable rule-model identity bound to one of StelligenOS's frozen Gate IDs.
- Human-reviewed historical-rule metadata and external applicability references.
- Explicit neutral/unknown semantics until a separately governed executable
  model is promoted.
- Contract YAML for external runtimes and governance services.

## Deliberate exclusions

The repository does not contain historical ADC cases, rule JSON, generated
rule outputs, model artifacts, databases, caches, or execution scripts. Natural
language `if/then` statements are descriptive only and can never change a Gate
score, Gate status, threshold, or Profile binding automatically.

All evidence, review records, candidates, and runtime outputs must live in an
external workspace and be passed as external references.
