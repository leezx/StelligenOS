# TGT-05 v2 Phase B1 模块交接

状态：**PROPOSED；待 PR、CI 和 ChatGPT L1/L2 审核。**

## 基线与范围

- Phase B0：[PR #144](https://github.com/leezx/StelligenOS/pull/144)，最终 exact HEAD `f28239908e1573247f85a8d27a654acd0c862c4a` 获 ChatGPT `APPROVE`，用户回复“继续”后合并为 `7f032d6cbfd55ea29b1d7acaf7b3af6403406bf9`。
- 本 PR 在 `gate_modules/tgt05_normal_tissue_adc_toxicity_v2/` 单独实现 `MOD-TGT05@2.0.0`。基线为 `src/contracts/gate_modules/tgt05_normal_tissue_adc_toxicity_v2.yaml`、`src/contracts/crc_adc_target_gateset_v2.yaml` 和已批准 B0 计划。
- v1 模块及 GateSet v1 不修改。TGT-05 v2 binding 仍 `0.0.0`，CRC v2 Instantiation 仍 `HOLD`。本 PR 无真实数据、provider/network、Decision evaluator、人工审批 UI 或激活。

## 实现与验证

- typed request/observation/coverage/source；通过四个注入式 port 取得规范化事实和 canonical source/EP。目标、program、context、source、EP reuse 不一致或失败 audit 导致整轮 `RunRejection`，无部分可用 proposal。
- EP 保持 Gate-neutral。独立 proposal 携带 Direction/Strength、四 evidence domain 引用、coverage gaps、冲突 EP 与 fatal-review 路径；无 GO/HOLD/KILL 字段和 canonical Assessment/Decision。`reviewer_seed` 是不完整非 canonical 草案输入，须人工完成 schema 所需审查。
- 定向合成测试覆盖 DIRECT 阳性、限定阴性、RNA/IHC/Open Targets ceiling、同/异事件冲突、来源/身份/EP 复用失败、v2 未绑定状态。旧 v1 测试中的七个 per-Gate package allowlist 各新增 v2 路径，保留禁止 generic framework 的断言。
- 本地首次全量 1936 tests 的七项 allowlist 失败已修正，随后 1936 tests OK；加入临床 validated 限定后全量 1937 tests OK。最终又补了“无报告事件只作 context”的小修订，定向 23 tests OK，待 GitHub CI 全量复核。`bash scripts/verify_repository_boundary.sh` 和 `git diff --check` 已通过。

## 审核重点

1. E1/E2/E3/Supporting 和 DIRECT/INDIRECT_STRONG/WEAK 的证据资格是否与 Gate@2.0 一致，尤其限定阴性、未归因 AE 与 serious DIRECT。
2. 同事件合格反证如何触发 `CONFLICTING`，跨事件和独立严重阳性是否保留。
3. 来源/目标/program/context/EP drift 是否 fail closed，且 reviewer seed、fatal flag 不越权。
4. v1 回归、仓库数据边界与不激活的版本状态。
