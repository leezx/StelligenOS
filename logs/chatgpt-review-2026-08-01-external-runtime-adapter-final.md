# ChatGPT Review Record: External Runtime Adapter (contract-only) Final

- Review date: 2026-08-03 EDT
- Pull request: #17
- Approved head: `bb65c45`
- Base branch at review time: `task_20260801_os-boot-smoke`
- Reviewer: ChatGPT via GitHub source
- Decision: `APPROVE`
- Approval relayed by: human lead

## Note on when this record was written

This record was written **after** PR #17 was merged, not before. Writing it on
the branch beforehand would have added a commit, changing the approved head and
the aggregate diff, which would have invalidated the reviewer's own merge
instruction to "retarget to main and confirm the aggregate diff has not
changed". The trade-off was raised in PR #17 and resolved by deferring these
three records to this follow-up PR.

## Review history

- Round 1: `REQUEST_CHANGES`. Five blockers, two of them security: the command could write back into the repository via an absolute path while the class docstring claimed "no repository writes"; `os.environ.copy()` leaked credentials; `output_root` was only checked for existence; there was no dedicated handoff; and tests covered none of those cases.
- Round 1 correction kept the executor and added four layers (opt-in execution, an attested sandbox reference, an environment allowlist, and a before/after repository fingerprint), each labelled as prevention or detection.
- Round 2: `REQUEST_CHANGES`. The layered approach did not hold. Two holes were demonstrated empirically: a write into `.git/` went undetected because the fingerprint excluded it, and a written `.git/hooks/` entry is arbitrary code execution on a later checkout or commit; and a command could write, read the repository out, then restore the file before exiting so the after-the-fact comparison compared equal. Neither the environment allowlist nor the path checks provided any filesystem isolation.
- Round 2 correction adopted the recommended option: **downgrade to contract-only**. `SubprocessExternalRuntime`, the fingerprint, `RepositoryMutationError` and the environment construction were removed rather than patched, and the CLI lost all execution capability. Six regression tests now assert the executor cannot be reintroduced.
- Round 3: `REQUEST_CHANGES`. One real contradiction remained: `ExternalRuntimeResult` constrained `status` but never checked it against `exit_code`, so `completed`/3 and `failed`/0 were both constructible. This mattered specifically because the downgrade turned the result from something derived in-repository into untrusted inbound input.
- Round 3 correction added the consistency rule — `completed` requires `exit_code == 0`, `failed` requires non-zero, including the negative values that signal termination produces.
- Round 4: `APPROVE`.

## Final conclusion

The module is contract-only. It defines `ExternalRuntimeRequest`, `ExternalRuntimeResult` and `ExternalRuntimePort` and validates envelopes; it executes nothing. No `subprocess`, fingerprinting or pseudo-sandbox logic remains in the repository.

## Outstanding consequence

StelligenOS now has **no ability to execute an external runtime at all**. This is the intended result, but a real run requires an external controlled environment implementing `ExternalRuntimePort`, and that environment must genuinely make the repository invisible or read-only to the command and host credentials unreachable. The repository cannot verify that; it can only state the requirement in the contract. That environment does not yet exist and needs its own task.
