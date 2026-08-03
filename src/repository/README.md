# Repository Boundary

This layer defines adapters to external workspaces and services. It must not
copy external datasets, caches, outputs, or working files into StelligenOS.

`boot.py` and `scripts/boot_os.py` provide the data-free OS boot boundary.
Boot validates that workspace, run, and policy references are external, then
returns a static architecture plan. It does not load data, execute models,
write results, or promote lifecycle state.
