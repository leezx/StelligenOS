# TGT-05 v2 Phase A 契约 PR 交接

- 时间：2026-10-22 19:32 EDT
- 分支：`task_20261022_tgt05_v2_contract_phase_a`
- Base：`main` @ `004fc44c02fbea9511274427904792b255141521`（RFC PR #142 merge commit）
- 科学来源：`docs/architecture/TGT05_DECISION_MODEL_V1_SOURCE_SNAPSHOT.md`，SHA256 `2e41525f65c6f7e4e9ec909bd8f110623f6ce62f54d5c82448c37aa80224674c`
- 状态：Phase A 实施中；PR URL、body commit、registry commit 和审核结论待补充。

## 本阶段目标与边界

按已获审核并合并的 TGT-05 RFC，新增 `ADC_TARGET_GATESET@2.0`、`TGT-05@2.0` 和 `MOD-TGT05@2.0.0` 的**契约声明**，以及四个版本化 GateSet policy bodies、content-hash registry、非 canonical 人审记录 schema 和契约校验。`INST-CRC-REFRACTORY-ADC-TARGET-v2` 在 Phase A 为 `HOLD`；TGT-05 v2 binding 使用未构建的 `0.0.0` 插槽，计划模块版本是 `2.0.0`。旧 v1 文件保持字节不变且仍可显式执行。Phase A 不构建 Module/人审 UI/决策引擎，不运行真实数据，也不输出 Candidate 结论。

用户于本阶段选择保守全门槛：八 Gate 均有足够的 `HUMAN_APPROVED` assessment、无重大未解风险才允许 Candidate GO。策略明确逐 Gate Direction/Strength，TGT-07 的 GO 阴性需要 qualified intended-ADC TMDD，TGT-05 阴性需要限定范围的经质控膜蛋白/候选抗体证据；这意味着多数 public-only 靶点可能保持 HOLD/MORE_EVIDENCE，不能把缺证据填成 GO。

## 已起草工件

- `src/contracts/crc_adc_target_gateset_v2.yaml`：v2 身份、八成员、TGT-05 ladder、inactive Instantiation 和 schema-parity bindings。
- `src/contracts/gate_modules/tgt05_normal_tissue_adc_toxicity_v2.yaml`：17 项 Module 施工合同，不含实现。
- `src/contracts/gate_modules/tgt05_decision_record_v2.schema.json`：非 canonical 人审记录的字段与 GO/KILL 边界。
- `src/contracts/gateset_policies/ADC_TARGET_GATESET/v2/`：四个声明式政策与 synthetic acceptance cases；registry 将在 body commit 后 pin 精确 SHA256 与 source Git commit。
- `tests/test_tgt05_v2_contract_phase_a.py`：来源、版本、binding、政策和人审边界验证。

## 验证与审核状态

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`：1910 tests，OK。第一次未禁止字节码的运行触发 4 项仓库缓存卫生测试失败；清理 26 个 `__pycache__` 后按无字节码模式重跑通过，当前缓存数为 0。
- `git diff --check` 通过；`bash scripts/verify_repository_boundary.sh` 输出 `Repository boundary check passed.`。
- 本阶段尚无 PR 或 ChatGPT `APPROVE`；不得进入 Phase B 或外部运行。后续需提交 body commit、生成 hash registry、复核测试、创建 PR 并送固定会话审核。
