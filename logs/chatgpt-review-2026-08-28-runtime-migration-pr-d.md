# ChatGPT 审核记录：Runtime Migration PR D —— CRC-ADC-TARGET-GATESET-v1

- 日期：`2026-08-28`
- PR：#104 `task_20260828_runtime-migration-pr-d`
- 审核渠道：网页版 ChatGPT，项目 `Biotech ideas` → 对话 `AI审核方案`（Claude 通过
  浏览器自动化把审核请求贴入该对话）
- 被审核 HEAD：`35298de`（科学审核第二轮修订）
- Merge 提交：`16f5f01`（`Merge pull request #104 from leezx/task_20260828_runtime-migration-pr-d`）
- 结论：**APPROVE @ `35298de`**（Structure: PASS / TGT-01…TGT-08 scientific
  Evidence Ladders: PASS / A2′ + B1 implementation: PASS）

本记录在**独立 docs-only PR**（`task_20260828_runtime-migration-pr-d-approval-record`）
中补登，按 PR #95 / #97 / #99 / #101 / #103 先例——审核记录不落在被批准的 PR
branch 上。本 PR 同时把 `manifests/runtime_migration_pr_d_manifest.yaml` 补成
approved。不改 PR D 的 runtime 合同或 ladder 内容。PR body 首版遗留的
`743 OK / 27 tests` 已在 merge 前直接编辑 PR #104 body 为 `751 OK / 35 tests` +
科学审核小结，无新 commit。

## 两个 scoping 决策（建代码前，审核方拍板）

- **Decision A = A2′**：PR D 携带 **8 个 concrete three-rung Evidence Ladders 作为
  proposal**，科学审核在 PR #104 内完成（REQUEST_CHANGES until scientifically
  acceptable → APPROVE → merge = v1.0 frozen ladders）。只冻结 **evidence-class
  semantics / ceilings / inference boundaries**，不发明 numeric biological
  thresholds。A1（只搭 binding 骨架）会让 PR D 变成空壳、把科学合同偷偷 defer
  到 PR E（低于冻结 CURRENT_SYSTEM v5 §16 对 PR D 的定义）；A3（写满 production
  science rules 含 quantitative cutoff）是无来源发明。均否。
- **Decision B = B1**：PR D 建立**第一份 machine-readable TGT-01…TGT-08 roster**。
  CURRENT_SYSTEM v5 §6.4 是 id / name / L04 ownership 的 frozen normative
  basis，但 v5 把完整 Gate 骨架指向外部 `Blueprint v0.1 §H2.4`（不在仓库），且
  无任何冻结仓库文档给出 per-Gate machine `gate_version`。因此 PR D 初始化
  `gate_version = "1.0"`，合同 `gate_version_provenance` 明确 "NOT claimed to be
  copied from a pre-existing per-Gate version in Blueprint prose"。
  - 顺带锁死：`CRC-ADC-TARGET-GATESET-v1` 只是 program label，绝不进
    `gateset_id`；PR D 不建 primary Module —— 只冻结 `MOD-TGT0n` binding slot，
    `primary_module_version = "0.0.0"`（declared, not built）。

## 三轮历史

| 轮 | HEAD | 结果 |
|---|---|---|
| 1 | `29d3def`（PR D 首版：roster + 8 ladders + GateSet + Instantiation + 8 gate_binding + 27 tests） | `REQUEST_CHANGES`。**结构层 PASS**（A2′+B1、label 非 gateset_id、roster 锁死 TGT-01..08 / L04 / `1.0`、`0.0.0` Module slot、只复用 PR A/B/C）；**科学 ladder 层 6 组最小修改**。 |
| 2 | `10aa934`（科学审核第一轮，34 tests） | `REQUEST_CHANGES`。TGT-01 / 03 / 04 / 06 / 07 / 08 六组全部接受；只剩 **TGT-05 `fatal_conditions`** 一个 blocker。 |
| 3 | `35298de`（科学审核第二轮，35 tests / 751 全量） | **`APPROVE`** |

## 第一轮 REQUEST_CHANGES 的 6 组科学修改（`29d3def` → `10aa934`）

不加 numeric cutoff、不改冻结文档、不进 PR E。均在
`src/contracts/crc_adc_target_gateset.yaml` `gate_contracts`：

1. **TGT-01（ADC Modality Precedent）**：INDIRECT_STRONG 移除 "approved / late-clinical
   ADC against a biologically adjacent target in the same lineage"（adjacent-target
   ADC 成功不能强力 de-risk 本 target）→ 降到 WEAK（class-level signal only）；
   `fatal` 从 "单个 same-target ADC 因 target-mediated toxicity 终止" 改为
   "**≥2 个独立 same-target ADC program** 因一致的 on-target / target-mediated
   toxicity 或内在不可达治疗窗终止（单产品失败——可能由 linker / payload /
   format 驱动——不足）"。
2. **TGT-03 / TGT-04 `fatal` 收窄，去掉偷偷的 universal threshold**：TGT-03
   "target down-regulation or loss" → "reproducible protein-level near-loss /
   marked loss 导致 intended refractory / metastatic context 中 meaningful
   target availability 丧失（短暂 / 轻微下调不算）"。TGT-04 删掉 "far below the
   range of clinically validated ADC targets"（ADC field 无可靠统一 antigen-density
   range；adequacy 取决于 payload potency / bystander / internalization /
   epitope / DAR）→ "reproducible 定量证据显示 CRC 恶性细胞表面抗原可忽略 /
   检测不到 —— absence of a targetable surface antigen"。
3. **TGT-05（Normal-Tissue Fatal Liability，最大一组）**：target-level liability
   ≠ product-specific therapeutic window。`gate_question` 去 "unmanageable" 并
   注明 target-level 非 product-window；`DIRECT` 收为 **ADC-specific**
   （same-target ADC 的 on-target / off-tumor 临床毒性）；cross-modality
   （CAR-T / TCE / naked-Ab）毒性下移 INDIRECT_STRONG，ceiling 注明 "机制 /
   暴露 / severity 不 1:1 迁移到 ADC 治疗窗"；`allowed_inference` 去 "or absence"
   （与冻结 "HPA negative ≠ safe" 一致）→ "presence + plausibility / severity
   signals"；`forbidden_inference` 显式加 "negative RNA / IHC / atlas alone ⇏
   absence of liability / safety" + "非 ADC modality severity 不直接迁移" + "不做
   product-specific therapeutic-window 结论"。
4. **TGT-06（Internalization / Trafficking）**：internalization = antibody ×
   epitope × affinity × conjugation × context dependent，非 target-intrinsic
   constant。`DIRECT` → "existence proof that ≥1 tested antibody / epitope
   configuration 实现 antibody-induced internalization + lysosomal delivery in
   disease-relevant context"；`successful same-target ADC` 明确置于
   INDIRECT_STRONG（functional ADC delivery precedent，不证明 trafficking
   mechanism）；`forbidden` 加 "单个 non-internalizing config ⇏ target 非内化"；
   `fatal` 要求 "**多个独立 antibody / epitope configuration** 均 fail
   productive internalization / trafficking（单 config 失败不足）"。
5. **TGT-07（Shedding / Soluble-Antigen / Sink）**：quantified soluble antigen
   ≠ demonstrated sink。"quantified circulating soluble target in CRC patients
   （无 exposure / TMDD 分析）" 从 DIRECT 下移 INDIRECT_STRONG（ceiling：证明
   soluble form 存在于可测水平，是否 material sink 取决于 concentration /
   turnover / dose / affinity / clearance）；`DIRECT` = "documented antigen-sink
   PK / PD effect attributable to soluble antigen" 或 "定量 soluble-target 数据
   + exposure / affinity / turnover（TMDD）分析显示 material sink"；`forbidden`
   加 "a measured concentration by itself establishes a material antigen sink"；
   `fatal` → "circulating soluble antigen demonstrated or quantitatively
   modelled … to materially compromise clinically achievable exposure"。
6. **TGT-08（Target Opportunity / Competition / IP Whitespace）**：删除等价于
   FTO / legal 结论的 `fatal` "blocking composition-of-matter IP … no viable
   design-around"（L04 target stage 尚无 epitope / antibody / linker / payload /
   DAR，不可能做 composition-level FTO 判定）；`forbidden` 加 "no viable
   design-around 结论不可能"；`allowed_inference` 注明 "dense claim coverage /
   apparent congestion 喂 NEGATIVE target-opportunity assessment, not KILL"；
   保留唯一 `fatal` "dominant well-protected competitor ADC approved /
   registrational in same target × mCRC with no differentiation path"（sponsor
   轴 potential fatal，非 canonical 科学 KILL）。

新增 `tests/test_crc_adc_target_gateset.py` `LadderScienceRevisionTests`（+7）：
全 8 gate 正则扫无 numeric cutoff；逐条锁死上述 6 组。

## 第二轮 REQUEST_CHANGES 的 1 处修改（`10aa934` → `35298de`）

**TGT-05 `fatal_conditions`**：单个 ADC construct 的 target-mediated on-target /
off-tumor toxicity 是 **DIRECT evidence of an ADC-relevant liability，但不是
target-wide fatal**（可能 linker / payload / format 驱动）；normal-tissue
expression 与 non-ADC modality toxicity 是 strong liability signal，不单独
fatal。fatal 必须是 "**a convergent target-mediated on-target / off-tumor
toxicity pattern across materially distinct ADC constructs against the same
target**（distinct antibodies / linkers / payloads / formats converging on the
same target-driven normal-tissue toxicity）"，无需机械写 "two or more"。

→ TGT-05 `fatal_conditions` 两条 → 一条 convergent-across-materially-distinct-
constructs pattern，明确 "single ADC construct's toxicity … is NOT target-wide
fatal"，去掉 "preclude an ADC therapeutic window" 这种 product-window 结论。
测试加 `test_tgt05_fatal_requires_convergent_pattern_not_single_construct`。

## 批准范围（审核方原话要点，`35298de`）

> **Structure: PASS**
> **TGT-01…TGT-08 scientific Evidence Ladders: PASS**
> **A2′ + B1 implementation: PASS**
> **APPROVE PR #104 @ `35298de`。可以 merge。**

- 最后一个 TGT-05 scientific blocker 已关闭。当前 `fatal_conditions` 要求
  "across materially distinct same-target ADC constructs 的 convergent、
  target-mediated on-target / off-tumor toxicity pattern"；并明确：单个 ADC
  construct 的 toxicity = DIRECT ADC-relevant liability evidence 但不是
  target-wide fatal；normal-tissue expression = liability signal；
  CAR-T / TCE / naked-Ab toxicity = strong cross-modality liability signal；
  二者都不能单独触发 fatal。regression test 也准确锁住了 `convergent
  target-mediated` / `materially distinct ADC constructs` / `not target-wide
  fatal`，并确认旧的 `preclude an ADC therapeutic window` wording 不再出现。
- 结构层：A2′ + B1 落实正确；`CRC-ADC-TARGET-GATESET-v1` 只是 specialization
  label，canonical id 始终 `ADC_TARGET_GATESET`；roster 严格锁死 TGT-01…08 /
  L04 / `gate_version = 1.0`；`0.0.0` 只是未施工 Module slot；runtime 继续复用
  PR A/B/C contracts，没有另造一套对象体系。
- **Merge 后**：这 8 个 ladder 视为 `ADC_TARGET_GATESET@1.0` 在 refractory mCRC
  specialization 下的 **v1.0 frozen scientific contracts**。后续 PR E+ 只能实现
  各 Gate 的 Evidence Production Module 和定量 calibration，**不能再由 Module
  自行改变 Gate question / evidence class / ceiling / fatal / unknown /
  inference semantics**（v5 §6.4）。
- PR HEAD `35298de51675…`，open、mergeable，pull-request CI success。

## 操作层说明

审核请求由 Claude 通过 Chrome 浏览器自动化贴入网页版 ChatGPT `Biotech ideas`
→ `AI审核方案` 对话（用户 2026-08-28 明确指示"把任何需要审核的全部提交给
ChatGPT 的 Biotech ideas - AI审核方案 对话框审核"）。审核方三轮均尝试通过
GitHub connector 直接给 PR #104 写入 review 状态（`REQUEST_CHANGES` /
`APPROVE` anchor 到对应 HEAD），GitHub 每次返回
`403 Resource not accessible by integration`，未能写回 GitHub。GitHub 上 PR
#104 因此没有 formal review 记录，实际三轮意见与最终 `APPROVE` 以本文件与
`AI审核方案` 对话为准。

## 边界

本次批准的是 **canonical ADC_TARGET_GATESET 的 CRC context-specific 首次施工
实例**（`src/contracts/crc_adc_target_gateset.yaml` +
`src/objects/crc_adc_target_gateset.py` + 35 tests）：TGT-01…TGT-08 roster、
8 个 v1.0 frozen Evidence Ladder（evidence-class semantics / ceilings /
inference boundaries，无 numeric threshold；TGT-02/03/04 带 v5 §11.2 EVGAP
inference guard）、`ADC_TARGET_GATESET@1.0` GateSet、
`INST-CRC-REFRACTORY-ADC-TARGET-v1` Instantiation + 1 gateset_binding + 8
gate_binding（对冻结 `gate_binding.schema.yaml` 做 parity）。它是四个
runtime-migration PR 的最后一个。**没有** evaluator、**没有** Evidence
Production Module（8 个 `MOD-TGT0n` 只是 `0.0.0` declared slot）、**没有**
新增 canonical `gateset_id`、**没有**新增 `data_layout/` schema、**没有**改动
PR A/B/C 或任何冻结文档。CURRENT_SYSTEM v5 的 `MIGRATION_PENDING` 未解除——到
PR E 合并前 repository runtime 不得声称已实现 Blueprint v1.3 conformance。仓库
内不保存运行数据或 `.csv`。

冻结与进度状态：

> Blueprint v1.3：冻结
> CURRENT_SYSTEM v5：冻结
> Data Layout Spec v1.0：冻结
> Runtime Migration PR A（core decision objects）：已合并（PR #98 @ `f225e9f`，`cbab012`）
> Runtime Migration PR B（canonical Gate / GateSet / EvidenceLadder / Decision）：已合并（PR #100 @ `51bfadb`，`d18974b`）
> Runtime Migration PR C（Matrix view / reusable EP references / provenance walk）：已合并（PR #102 @ `d16b634`，`91a8e5b`）
> Runtime Migration PR D（CRC-ADC-TARGET-GATESET-v1）：**已合并**（PR #104 @ `35298de`，`16f5f01`）
> 下一步：Runtime Migration PR E+ —— 逐 Gate primary Evidence Production Module（TGT-01…TGT-08），按 Blueprint v1.3 §H2.8 的 Gate Module Acceptance Template 逐 Gate 绘施工图；PR E 合并后方可解除 `MIGRATION_PENDING`。
