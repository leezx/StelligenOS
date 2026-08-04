# ChatGPT Review Record: CI and dependency declaration Final

- Review date: 2026-08-04 EDT
- Pull request: #50
- Approved head: `076c5ffa7615702a419c37992ccae70036a33f0f`
- Base branch: `main`
- Merge commit: `927aebf4f31bcdcfd4a4c4a03089cc41e27a38bd`
- Reviewer: ChatGPT
- Decision: `APPROVE` (Round 2)
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.** The conclusions quoted
  below are reproduced as received, not paraphrased.

## What was reviewed

The two residual risks every handoff from PR #15 to #48 carried: no GitHub
Actions, so test counts were corroborated only by the repository's own audit
records; and no dependency declaration, while several tests import `pyyaml`.

Delivered: `requirements.txt`, `.github/workflows/ci.yml` (Python 3.11/3.12
matrix, five checks), generalisation of the `.claude` exact-path exemption into a
shared restricted-directory mechanism in
`scripts/verify_repository_boundary.sh`, `tests/test_repository_boundary.py`
(15 behavioural tests), and a README section on running the checks locally.

## Review history

### Round 1 — `REQUEST_CHANGES`

> PR #50 — REQUEST_CHANGES
>
> 唯一阻断：requirements.txt 注释仍写“完整测试 192 tests”，而当前 PR、handoff 和 CI 均为 207 tests。
> 请统一为 207。当前 HEAD 的 GitHub Actions 已成功，其余依赖声明、CI 和仓库边界修改未发现阻断。

Verified and real. The comment was written before
`tests/test_repository_boundary.py` existed, when a clean venv genuinely did run
192; the 15 new boundary tests took it to 207 and that one line was not synced.

Corrected by re-measuring rather than editing the number to match: a clean venv
with only `PyYAML==6.0.3` was run again and reported `Ran 207 tests — OK`, after
which 207 was written in. Every other test-count claim in the PR was audited at
the same time; `ci.yml` and `README.md` deliberately carry none, because CI's own
output is authoritative and hardcoding a count in configuration would create
another drift source.

### Round 2 — `APPROVE`

> PR #50 — APPROVE
>
> 上一轮唯一阻断已修复：requirements.txt、PR 描述和 handoff 均统一为 207 tests。当前 HEAD 076c5ff
> 的 GitHub Actions run #3 已通过，Python 3.11/3.12 的全部检查均成功。可以合并 PR #50。

## Dependency scope, and what was deliberately excluded

`PyYAML` is the only declared dependency. `dagster`, `anarci`, `abnumber`, `Bio`
(biopython) and `ImmuneBuilder` appear only in `genmodules` pipeline code that no
test imports. They are excluded not as "not installed yet" but because declaring
them would be a false claim: nothing here executes a pipeline, and
`src/repository/external_runtime.py` was deliberately downgraded to contract-only
with six regression guards. The reasoning is written into `requirements.txt` so it
is not later "fixed" as an omission.

Established empirically, not by reading imports: the full suite passes in a clean
virtual environment with only `PyYAML` installed.

## First independent CI evidence

This is the PR that introduced the workflow, so its first real execution happened
on itself.

```text
run #3 at head 076c5ff    conclusion: success
verify (3.11)  pass    verify (3.12)  pass
Ran 207 tests ... OK
git_sync behavior tests passed (A-D).
Repository boundary check passed.
No bytecode artifacts left behind        success
Working tree unchanged by the test run   success
```

The 3.11 job passing confirms the `enum.StrEnum`-derived version floor rather
than merely asserting it.

**This is the first test evidence in this repository independent of its own audit
records.** Every review round since PR #15 noted that GitHub had no Actions run
associated with the head under review. That condition no longer holds.

## Scope of this approval

Approved:

- `requirements.txt` declaring `PyYAML>=6.0,<7`, and the recorded reasoning for
  excluding the pipeline dependencies.
- `.github/workflows/ci.yml` as written, including the check order and the
  clean-working-tree assertion.
- The restricted-directory mechanism in `scripts/verify_repository_boundary.sh`,
  which allowlists `.github/workflows/ci.yml` by exact path rather than opening
  the directory.
- `tests/test_repository_boundary.py`.
- Merging PR #50 into `main`.

Not authorized by this approval:

- Any change to `src/` Python code, contracts, Gate topology, Model, Profile,
  lifecycle or core objects. None was made.
- Modifying `tests/test_git_sync.sh`. CI installs ripgrep instead.
- Adding further paths to the restricted-directory allowlist.
- Extending CI to macOS, pinning dependencies via a lock file, or introducing
  `pyproject.toml`. All three remain open items for separate tasks.
