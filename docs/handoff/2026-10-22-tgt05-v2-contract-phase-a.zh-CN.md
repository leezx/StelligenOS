# TGT-05 v2 Phase A 契约 PR 交接

- 时间：2026-10-22 19:32 EDT
- 分支：`task_20261022_tgt05_v2_contract_phase_a`
- Base：`main` @ `004fc44c02fbea9511274427904792b255141521`（RFC PR #142 merge commit）
- 科学来源：`docs/architecture/TGT05_DECISION_MODEL_V1_SOURCE_SNAPSHOT.md`，SHA256 `2e41525f65c6f7e4e9ec909bd8f110623f6ce62f54d5c82448c37aa80224674c`
- PR：[StelligenOS #143](https://github.com/leezx/StelligenOS/pull/143)，当前 `OPEN`；round 1 已收到 `REQUEST_CHANGES`，修订中。
- 稳定 policy body source commit：`5abe4fb38a9f3b5c35654c5f9bad0017f7e7c67c`；registry commit：`e9413c1b714d6468ce1f983a3c7d81d442ff1a0f`。审核结论待补充。

## 本阶段目标与边界

按已获审核并合并的 TGT-05 RFC，新增 `ADC_TARGET_GATESET@2.0`、`TGT-05@2.0` 和 `MOD-TGT05@2.0.0` 的**契约声明**，以及四个版本化 GateSet policy bodies、content-hash registry、非 canonical 人审记录 schema 和契约校验。`INST-CRC-REFRACTORY-ADC-TARGET-v2` 在 Phase A 为 `HOLD`；TGT-05 v2 binding 使用未构建的 `0.0.0` 插槽，计划模块版本是 `2.0.0`。旧 v1 文件保持字节不变且仍可显式执行。Phase A 不构建 Module/人审 UI/决策引擎，不运行真实数据，也不输出 Candidate 结论。

用户于本阶段选择保守全门槛：八 Gate 均有足够的 `HUMAN_APPROVED` assessment、无重大未解风险才允许 Candidate GO。策略明确逐 Gate Direction/Strength，TGT-07 的 GO 阴性需要 qualified intended-ADC TMDD，TGT-05 阴性需要限定范围的经质控膜蛋白/候选抗体证据；这意味着多数 public-only 靶点可能保持 HOLD/MORE_EVIDENCE，不能把缺证据填成 GO。

v2 Instantiation 的 `evidence_regime` 因此为 schema 允许的 `PUBLIC_PLUS_EXPERIMENTAL`；v1 的 `PUBLIC_ONLY` 不变。该配置仅声明未来可接纳合格实验来源，不授权 Phase A 采集或运行实验数据。

## 已起草工件

- `src/contracts/crc_adc_target_gateset_v2.yaml`：v2 身份、八成员、TGT-05 ladder、inactive Instantiation 和 schema-parity bindings。
- `src/contracts/gate_modules/tgt05_normal_tissue_adc_toxicity_v2.yaml`：17 项 Module 施工合同，不含实现。
- `src/contracts/gate_modules/tgt05_decision_record_v2.schema.json`：非 canonical 人审记录的字段与 GO/KILL 边界。
- `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/`：四个声明式政策与 synthetic acceptance cases；registry 已 pin 精确 SHA256 与 source Git commit，审核状态仍为 `PENDING_CHATGPT_REVIEW`。
- `tests/test_tgt05_v2_contract_phase_a.py`：来源、版本、binding、政策和人审边界验证。

## 验证与审核状态

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`：最终 1912 tests，OK。第一次未禁止字节码的运行触发 4 项仓库缓存卫生测试失败；清理 26 个 `__pycache__` 后按无字节码模式重跑通过。
- `git diff --check` 通过；`bash scripts/verify_repository_boundary.sh` 输出 `Repository boundary check passed.`。
- 上述初版检查时尚无 PR 或 ChatGPT `APPROVE`；不得进入 Phase B 或外部运行。后续进度见下节。

## Registry 与 PR 更新（2026-10-22 19:34 EDT）

body commit `d3f3689e47ee087716d46c0489a550259369815a` 已推送，随后创建 Draft PR #143。新 `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/registry.yaml` 对四个 ref pin body 路径、SHA256、Git commit、review PR 与 `PENDING_CHATGPT_REVIEW` 状态。用 `git show <body-commit>:<path>` 独立重算四个 SHA256，均与 registry 一致；resolver 合同要求 `APPROVED`，所以当前 registry 不能被用于 Candidate 决策。registry 测试已加入，定向 11 项通过，禁写字节码的全量 1911 项通过；`git diff --check` 和仓库边界脚本通过。待把 registry/handoff/worklog 提交推送、核对 CI 和 exact HEAD 后，将 PR 标为 ready 并送固定 ChatGPT 会话审核。

送审前追加对象形状复核发现 v2 Gate YAML 缺少 frozen `Gate`/`EvidenceLadder` 的部分规范字段；现已补齐并让测试实际构造这两个对象。其余六个可作科学 fatal 的 Gate 精确继承 v1 `fatal_conditions`，保留 TGT-08 非科学 KILL 边界。此修订使 `fatal_gate_policy.yaml` hash 变化；须在最终 registry commit 更新，不能沿用上一段的初版 manifest 值。

对象字段修正提交为 `a940d9eb7f2cab772556c4d6bbeb25b425e590d8`。后续发现 policy body 的 `status` 若写“待审”会在批准后变为陈旧状态，故 `5abe4fb38a9f3b5c35654c5f9bad0017f7e7c67c` 将 body 状态改成固定的 `DECLARATIVE_POLICY_SOURCE`，Gate/Module 声明改为 `CONTRACT_ONLY_INACTIVE`；审核状态只由 registry 的 `approval_status` 管理。registry 已更新 source Git commit 与四个 body SHA256。此设计无需在批准后为修正文案而改动已审核的政策 body；仍须最终 CI 和 ChatGPT exact-head 核验。

## 送审前最终核对（2026-10-22 19:39 EDT）

registry 和状态修正已在 `e9413c1b714d6468ce1f983a3c7d81d442ff1a0f` 提交并推送。四个 policy body 哈希均从 `5abe4fb38a9f3b5c35654c5f9bad0017f7e7c67c` 的 Git 对象复算并匹配 registry。禁写字节码的全量 1912 项测试通过，`scripts/verify_repository_boundary.sh` 通过。本 PR 仍无 ChatGPT `APPROVE`；Phase B 和外部数据运行禁止启动。

## 新审核会话与 round 1 修订（2026-10-23 01:22 EDT）

用户要求更换已达到长度上限的旧会话；新 [Biotech ideas 审核会话](https://chatgpt.com/g/g-p-68c041b4df6881918a83a55e2dd7ac70-biotech-ideas/c/6adaebc8-4738-83ea-8a87-894771eda8d6) 对 exact HEAD `3103d12e1fa686b83f3c4e3b54944e32c989580d` 给出 L1/L2 `REQUEST_CHANGES`。三项 blocker 详见 `logs/chatgpt-review-2026-10-23-tgt05-phase-a-round1.md`。同一 PR 内修订：显式增加 TGT-07@2.0 阴性 DIRECT 科学授权及对 RFC roster 的后续修正，v2 binding 的 MOD-TGT07 改为未构建的 `0.0.0`；三种 hard failure 不再生成可审议 TGT-05 Decision Record；新增稳定 record ID 和外部推荐差异审计 schema/政策义务，决策输入仍只有人工批准的八 Gate assessments。

修订只限契约、测试及审计。新增 `jsonschema` 作为契约测试依赖，测试对三个失败状态和推荐差异分别做真实 schema 校验。旧 v1 合同与 Module 保持不变。`INST-CRC-REFRACTORY-ADC-TARGET-v2` 仍为 `HOLD`；Phase B 现须另行审核并实现 MOD-TGT05@2.0.0 和 MOD-TGT07@2.0.0，随后方可考虑激活。策略 body 变动需更新 registry 的四项 hash 和源 Git commit。完成提交、CI 和新会话复审前，本修订不获批准，也不产生 Candidate 决策或外部数据运行授权。

修订 policy source commit 为 `4a485eef4594696344c333c7a1dfe6813f473a43`；registry 从该 Git 对象逐个复算四项 SHA256，均与当前工作区 body 字节一致。仓库外 venv 安装 `requirements.txt` 后，全量 `1915` tests 通过；repository boundary、`git diff --check` 和新审计 JSON Schema 语法检查通过。下一步推送同一 PR，等待 CI 并请新会话对新 exact HEAD 复审。
