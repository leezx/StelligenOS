# Migration Log

## 2026-07-31

- Cloned `leezx/StelligenOS` into `/Volumes/Stelligen_SSD/Stelligen/StelligenOS`.
- Reframed the repository as a biotechnology asset operating system implementation repository.
- Split the architecture contract out of the operational prompt and moved the canonical contract under `docs/architecture/`.
- Added `docs/architecture/capabilities.zh-CN.md`, `docs/architecture/lifecycle.zh-CN.md`, and `docs/architecture/legacy_inventory.zh-CN.md`.
- Added `prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md` as the Phase 0 / 0.5 operating prompt.
- Added `scripts/verify_repository_boundary.sh` to prevent top-level data-like drift.
- Added Phase 0 artifacts under `docs/phases/`.
- Marked `prompts/GPT-Feedback.md` as legacy migration input rather than canonical architecture.
- Verified the repo boundary script, Markdown links, YAML parsing, and basic test discovery; no test files were found.
- Updated the manifest to require Phase 0.5 legacy inventory before Phase 1.
- Completed the Phase 0.5 legacy inventory for `AssetGenOS`, `BACKUPS`, and `Zhixins-KB`.
- Added `docs/phases/PHASE_0_5_REPORT.zh-CN.md`, `docs/phases/PHASE_0_5_REVIEW_CHECKLIST.zh-CN.md`, and `manifests/phase_0_5_manifest.yaml`.
- Tightened the repository boundary script by removing `.DS_Store` from the allowlist and deleting stray macOS metadata files from the repo.
- Marked the Phase 0 / 0.5 status as complete and ready for Phase 1.
- Revalidated the repository boundary, Markdown links, and YAML manifests after the Phase 0.5 completion pass.
- Aligned the Phase 0 summary metadata with the 48-file snapshot and kept the Phase 1 recommendation unchanged.
- Added `ChatGPT-Codex-talk.md` as the canonical execution-first interaction protocol and linked it from the repo entry docs.
- Brought the Phase 0 snapshot count up to the live 49-file repo state after adding the interaction protocol file.
- Expanded the repository boundary allowlist to include `ChatGPT-Codex-talk.md` and revalidated the repo.
- Reworked the interaction protocol into a PR-centered review workflow and synced the repo-facing guidance in `AGENTS.md` and `HANDOFF.md`.
- 固化 GitHub 中间层协作方式，新增 `docs/handoff/` 交接模板和本任务 handoff，并将同步脚本改为显式文件清单暂存，禁止全量暂存。
- 按 GPT Feedback v4 修复同步脚本的未跟踪文件和非空暂存区风险，新增 A-D 行为测试，并将 Phase 0.5 审核清单改为中文。

## Next

- Keep Phase 1 architecture-first and minimal.
- Preserve the implementation-focused boundary.
- Avoid adding large datasets or data-bearing artifacts to this repository.
