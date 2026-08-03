# ChatGPT Review Record: Architecture doc versioning and extension shells Final

- Review date: 2026-08-03 EDT
- Pull request: #43
- Approved head: `6f52288`
- Base branch: `task_20260802_current-architecture-expert-review-doc` (PR #42 approved head, not `main`)
- Reviewer: ChatGPT via GitHub source
- Decision: `APPROVE`
- Approval relayed by: human lead

## Review history

- Round 1: `REQUEST_CHANGES` with five blockers.
  1. `PROPOSED_BASELINE` could yield an actionable `SUFFICIENT`, contradicting "not active before expert calibration".
  2. Sufficiency used `independent_supporting_count` only and ignored opposing evidence, producing a supporting-direction bias.
  3. `SufficiencyBaseline` validated only the gate group, allowing illegal baselines.
  4. The whole `.claude` directory was added to the boundary allowlist.
  5. PR description and handoff carried stale aggregate-diff numbers.
- Correction: all five verified against the code and confirmed real, then minimally fixed in the same PR. Direction-neutral sufficiency introduced (`max(supporting, opposing)`, no summing, no direction reported); `actionable` gated on calibration; shared `_validate_thresholds()`; exact-path exemption for `.claude/settings.local.json`; GitHub live HEAD declared the authoritative diff source.
- Round 2: `REQUEST_CHANGES` with two blockers.
  1. `actionable` could still bypass the extension-level governance gate declared in `extensions/README.md`.
  2. Verification metadata had not converged across PR description, handoff and worklog.
- Correction: added `governance_status` and `governance_approval_ref` to the contract plus a module-level `EXTENSION_STATUS` mirroring `extension.yaml`, making `actionable` a four-way conjunction; replaced the one-way invariants with a single biconditional; restructured verification records as "current round authoritative, earlier rounds historical".
- Round 3: `REQUEST_CHANGES` with three metadata conflicts (PR description still described `.claude` as allowlisted; handoff still carried the two-condition `actionable` formula; handoff "next steps" still said "create a PR").
- Correction: text-only synchronisation. Verified with `git diff --stat ed61fc0 HEAD -- extensions/ tests/ scripts/ src/ genmodules/` returning empty, i.e. zero code change.
- Round 4: `APPROVE`.

## Final conclusion

ChatGPT confirmed the three Round 3 metadata conflicts were synchronised without code change, and that the Round 1 and Round 2 code blockers remain correctly fixed at head `6f52288`.

Verification at the approved head: 23 test modules / 128 tests passing (`tests/test_stop_rule_extension.py` 40, `tests/test_extension_boundary.py` 11); `scripts/verify_repository_boundary.sh` passing with negative cases rejected; `tests/test_git_sync.sh` scenarios A-D passing; `git diff --check` clean.

## Scope of this approval

Approved:

- Architecture document versioning rule: stable canonical path, in-document version block, read-only snapshots under `docs/architecture/versions/`.
- The `extensions/` directory, its four kernel invariants, and the extension status semantics.
- `EXT-01` `ground_truth_learning_loop`, `EXT-02` `dynamic_gate_context`, `EXT-03` `asset_search_engine` as `shell_only`.
- `EXT-04` `stop_rule` as `active_design`, with its direction-neutral sufficiency contract and three-gate actionability rule.
- `BL-01` to `BL-07` recorded in `extensions/BACKLOG.zh-CN.md` as registered-not-started.
- `.gitignore` and boundary-script hygiene fixes.

Not authorized by this approval:

- Promoting any extension to `governed`. All four remain `shell_only` or `active_design`.
- Instantiating per-Gate `EvidenceSufficiencyContract` thresholds, which still require domain-expert calibration.
- Any kernel, Gate topology, Model, Profile or lifecycle change.
- CRC Gate scoring, T12 decision, pair ranking/recommendation, or asset generation.
- Merging into `main`. Merge remains a human decision, and the chain-bottom approval question for PR #15/#16/#17 is unresolved.
