# ChatGPT 审核记录：TGT-05 决策模型迁移 RFC · PR #142

- 时间：2026-10-22 15:39 EDT
- 审核渠道：固定 `Biotech ideas → AI审核方案` ChatGPT 对话
- PR：[StelligenOS #142](https://github.com/leezx/StelligenOS/pull/142)
- 审核锚点：base `1c8ba2274cbdbdd0c7193e2f5a5b3a440952730c`；head `e712adfa771f359fa85413334d209ec200fdcf8a`
- 审核结论：**REQUEST_CHANGES**。审核方尝试提交 GitHub review，integration 返回 `403 Resource not accessible by integration`；固定 ChatGPT 对话中的结论为本轮有效反馈。

## 原反馈要点（按审核方顺序）

1. v2 lineage 不能仍写成「建议」。固定 `ADC_TARGET_GATESET` ID + 2.0 版本、八个成员的逐项版本、v2 Instantiation/binding 身份、v1/v2 并存及不混用 invariant；明确 v1 模块是历史可读还是仍可执行。
2. E1/E2/E3 是正交证据域，不能代替 canonical ladder。须定义 v2 `DIRECT/INDIRECT_STRONG/WEAK` 与 `POSITIVE/NEGATIVE/CONFLICTING/INCONCLUSIVE` 的证据权威及 ceiling；避免「E1 Direct」混词。
3. `Tgt05DecisionRecord` 是 non-canonical Gate-specific review artifact，不是 core object 或 Decision。`GO/HOLD/KILL` 不得塞进 CandidateGateAssessment 或作为 GateSet shortcut；唯一链路是 EP → reviewer artifact → HUMAN_APPROVED Assessment → GateSet policy → canonical Decision。
4. 单项目 ADC 事件仅可支持当前 program/context-specific KILL 审议，不是 target-intrinsic fatal；临床 route 需 same-target、严重/实质毒性、qualified 归因、正常细胞/器官、暴露/剂量及构型替代解释。功能 route 需人相关表面可及性、靶点依赖性杀伤、临床相关暴露和不可接受细胞丢失后果；不完整时 HOLD。
5. v2 的四个 GateSet policy owner、外部 registry 的 canonical location/ref scheme、不可变版本/content hash、review authority 必须冻结。不能让实施阶段选择单 Gate KILL 建议如何影响 Candidate Decision。
6. webReport 来源设计没有 remote/commit，不能仅用本地路径/标题当 canonical science provenance。RFC 获 APPROVE 前须 pin 来源仓库精确 commit/path，或在 StelligenOS 引入带 immutable provenance/content hash 的精确设计快照。

审核方认可并要求保持：`NONE_DOCUMENTED != safe`；RNA 阴性不能 GO；普通 IHC 不等于表面可及性；Open Targets/人类遗传/小鼠仅 Supporting；E2 阳性不自动 KILL；自动规则只触发审议；canonical Candidate Decision 只由 GateSet 基于完整已批准 assessment snapshot 产生。Handoff/worklog 的旧 head 记录可保留历史，不须改写。

## 修订状态

2026-10-22 18:58 EDT：用户选择把 v2 policy bodies 放在 StelligenOS 的版本化契约目录，并授权将设计章节快照放进公开 PR。已在同一 PR 修订 RFC，对上述 1–5 固定版本/对象/ladder/KILL route/policy registry 与 binding；对第 6 项加入逐字快照，SHA256 `2e41525f65c6f7e4e9ec909bd8f110623f6ce62f54d5c82448c37aa80224674c`。这些是针对 blocker 的作者修订，**尚待同一固定会话复审，不能自行标记 CLOSED/APPROVE**。未进入下一 Phase，也没有真实数据运行。

## Round 2（2026-10-22 19:02 EDT）

- 固定 `Biotech ideas → AI审核方案` 会话审核 [PR #142](https://github.com/leezx/StelligenOS/pull/142) @ exact HEAD `82d95dc982ff8a4fea5fbb1287de7dfe51c8e5df`，明确结论 **APPROVE**，上一轮六项 blocker 逐项 **CLOSED**；未新增 RFC blocker。
- 审核方确认 CI run `39868630714` 的 `verify (3.11)` 与 `verify (3.12)` 均 success；本地 `gh pr view` 同样显示 PR `OPEN`、`MERGEABLE/CLEAN`、同一 head 与两项成功校验。
- 审核范围仅 RFC Phase。审核方说明 Phase A 四个 policy bodies、TGT-05 v2 runtime、真实数据与 250 靶点评估均未获批准，须另行 PR 审核。正式 GitHub APPROVE 仍因 integration 403 未能提交，以固定 ChatGPT 会话的 verdict 为准。
- 人类负责人尚未决定 merge 或下一 Phase；当前停在 RFC Phase。此段是对已审代码 HEAD 的审核结果留痕，不能把本审计文字当作新增科学或契约变更。
