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
- 将人类与 ChatGPT 制定总纲、Codex 分阶段执行、GitHub PR 审核放行的协作模式固化为 `docs/protocols/CHATGPT_CODEX_PHASE_GATE_PROTOCOL.zh-CN.md`。

## Next

- Keep Phase 1 architecture-first and minimal.
- Preserve the implementation-focused boundary.
- Avoid adding large datasets or data-bearing artifacts to this repository.

## 2026-08-01：`gen_indication_endpoint_target` Phase 0

- 读取并审计主提示词 `prompts/system/STELLIGENOS_GEN_INDICATION_ENDPOINT_TARGET_MASTER_PROMPT_v1.0.zh-CN.md`。
- 核对 AssetGenOS 的 Gate topology freeze、Gate Registry、T/P/C profiles、dependency graph、Model Registry、Rule Registry、evidence contract、clinical unmet need adapter、target generation 入口和测试/日志。
- 确认官方基线为 45 个 Gate（T=13、P=16、C=16），T0-T12 只能映射既有 T-chain，不新增 Gate。
- 确认 AssetGenOS target generation 与 SQLite、数据索引、cache、output 和 runtime 耦合；只保留软件定义、字段语义和外部引用边界，不迁移任何数据实例。
- 生成 `GEN_IET_PHASE_0_REPORT.zh-CN.md`、`GEN_IET_PHASE_0_REVIEW_CHECKLIST.zh-CN.md` 和 `manifests/gen_iet_phase_0_manifest.yaml`。
- 未执行真实候选生成、Gate/Rule/Model 评估、P-chain/C-chain 或数据处理；当前状态为 `COMPLETED_PENDING_REVIEW`，等待批准后才进入 Phase 1。

## 2026-08-01：`gen_indication_endpoint_target` Phase 1

- 基于已批准的 Phase 0，在独立分支实现 data-free 合同包：Scope、ClinicalFrame、TargetCandidate、CandidateFilterResult、EvidenceRecord、AdversarialReview 和 T12 handoff。
- 为合同增加外部引用、四元组 opportunity identity、unknown/not-evaluated 保留、非 Gate filter 和 provenance 字段约束。
- 未实现候选生成、证据采集、Rule/Model/Gate evaluator、ranking、P/C chain、数据库、数据、cache、result 或 runner。
- 55 个 unittest、repository boundary 和 `git diff --check` 均通过；Phase 1 合同已提交并完成审核闭环。
- ChatGPT Round 1/2 提出的外部引用与回归测试问题已修复；Round 3 返回 `APPROVE`，Phase 1 审核通过，可以进入下一阶段。执行适配仍必须另开分支和 PR。

## 2026-08-01：`gen_indication_endpoint_target` Phase 2

- 在 Phase 1 批准分支上新增外部-only T0-T1 Clinical Frame Pipeline port 和 request/result contracts。
- 强制 clinical unmet need、scope、T0/T1 input、policy、run、ClinicalFrame、Evidence 和 missing information 引用使用 `external:`；未读取数据、未运行 T0/T1、未创建本地记录。
- 58 个 unittest、repository boundary 和 `git diff --check` 均通过；等待 ChatGPT 审核后才可进入 Phase 3。

## 2026-08-01：`gen_indication_endpoint_target` Phase 3

- 基于 ChatGPT 已批准的 Phase 2，在独立分支新增 external-only Target Candidate Generation port、bounded generation policy 和 request/result contracts。
- 通过单一 ClinicalFrame 引用、配置化 candidate budget、最少独立正证据组和 external evidence scope 约束候选生成边界；禁止 model-only/rule-only generation。
- 未读取公共证据或临床数据，未生成本地 TargetCandidate/Evidence，未执行 P-chain/T-gate，未写入数据库、cache、result、weights、runner 或新 Gate。
- 61 个 unittest、repository boundary 和 `git diff --check` 均通过；ChatGPT 已返回 `APPROVE`，Phase 3 状态为 `APPROVED_PHASE_3`，可以进入 Phase 4；Phase 4 仍需独立 PR 审核。

## 2026-08-01：`gen_indication_endpoint_target` Phase 4

- 基于 ChatGPT 已批准的 Phase 3，在独立分支新增 external-only Early T-Gate Candidate Reduction port、既有 Gate 调度白名单和候选决策合同。
- 强制 T2/T7 优先，仅允许既有 T2、T7、T8-T11；保留 `PROVISIONAL_ADVANCE`、`HOLD`、`EXCLUDE` 与原因，禁止把无证据视为 FAIL，明确禁止 T12。
- 未读取证据或临床数据，未执行 T2-T11/T12/P-chain，未创建本地候选、Gate 结果或 Evidence，未写入数据库、cache、result、weights、runner 或新 Gate。
- 64 个 unittest、repository boundary 和 `git diff --check` 均通过；ChatGPT 已返回 `APPROVE`，Phase 4 状态为 `APPROVED_PHASE_4`，可以进入 Phase 5；Phase 5 仍需独立 PR 审核。

## 2026-08-01：`gen_indication_endpoint_target` Phase 5

- 基于 ChatGPT 已批准的 Phase 4，在独立分支新增 external-only Endpoint Biology Completion port，定义 T3-T6、历史 ADC Rule、Gate Model 和完整 T0-T11 trace 的引用边界。
- 要求 trace 按既有 Gate 冻结顺序覆盖 T0-T11，明确排除 T12；未修改 Gate 合同。
- 未读取证据或临床数据，未执行 T3-T6/Gate/Rule/Model/T12/P-chain，未创建本地 trace、Gate result 或 Evidence，未写入数据库、cache、result、weights、runner 或新 Gate。
- 67 个 unittest、repository boundary 和 `git diff --check` 均通过；ChatGPT 已返回 `APPROVE`，Phase 5 状态为 `APPROVED_PHASE_5`，可以进入 Phase 6；Phase 6 仍需独立 PR 审核。

## 2026-08-01：`gen_indication_endpoint_target` Phase 6

- 基于 ChatGPT 已批准的 Phase 5，在独立分支新增 external-only Positive Evidence Policy、证据独立性检查、Adversarial Review、ValidationTask 和 readiness ports。
- 保持 Adversarial Review 不是 Gate；只有满足外部 policy、独立性报告和 adversarial review 后才允许 `READY_FOR_T12_DECISION`，不执行 T12。
- 未读取证据或临床数据，未执行 Gate/Rule/Model/T12/P-chain，未创建本地 Evidence、Review、ValidationTask 或 Opportunity，未写入数据库、cache、result、weights、runner 或新 Gate。
- 70 个 unittest、repository boundary 和 `git diff --check` 均通过；当前状态为 `COMPLETED_PENDING_REVIEW`，等待 ChatGPT 审核后才可进入 Phase 7。
