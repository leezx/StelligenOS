# Phase 0.5 Review Checklist

- Confirm `AssetGenOS` was reclassified as a historical source and not the whole StelligenOS system.
- Confirm the legacy inventory covers the main repo, GenModules, backup archives, and KB evidence sources.
- Confirm the migration matrix includes `MIGRATE_AS_IS`, `MIGRATE_WITH_ADAPTATION`, `ARCHIVE`, `REFERENCE_ONLY`, and `MOVE_OUT_OF_REPO` decisions.
- Confirm the repository boundary still forbids large datasets, raw inputs, intermediate files, caches, outputs, and temporary artifacts.
- Confirm `AssetGenOS/data/adc_factory.sqlite3` is treated as data residue and not as repo content.
- Confirm Phase 0 and Phase 0.5 artifacts are both present and consistently say `PROCEED_TO_PHASE_1`.
- Confirm the boundary script passes after removing macOS metadata allowlisting.

