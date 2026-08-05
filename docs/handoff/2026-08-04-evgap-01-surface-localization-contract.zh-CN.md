# Handoff：EVGAP-01 target surface localization 证据抽取契约

- 日期：`2026-08-04`
- 任务分支：`task_20260804_evgap-01-surface-localization-contract`
- 基线：`main` @ `cd0e041`
- 前置：PR #57、PR #58，均已 `APPROVE` 并合并
- 交付物类型：**contract-only**
- 外部运行：**无。没有执行抽取，没有产生任何证据、判定或候选。**
- 授权范围：**只冻结抽取边界；抽取本身尚未获授权（待 `SRCADM-01`）；不授权执行 Level 01**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（依据是 diff 范围，可由 `git diff --stat` 核验）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次范围

人类负责人指示继续起 `EVGAP-01` 契约。`EVGAP-01` 是 PR #58 登记的两个缺口之一，阻断 `LOCK-01`：已批准证据层没有蛋白层面的质膜定位与细胞外结构域证据，导致 41 个靶点全部 DEFER、`eligible = 0`、Level 01 无法录入任何 pair。

本次交付该缺口的抽取契约。**不执行抽取。**

## 二、关键发现：所需数据已在本地，但那个数据库从未被批准

`DATA/1.Databases/ADC_surfaceome_reference/processed/v0.3.0` 恰好覆盖三项 RQ 要求。但治理状态必须先讲清楚：

> **该数据库从未被审核批准。** 仓库内 `logs/chatgpt-review-*.md` 无任何一条提及 surfaceome；worklog 唯一提及是 2026-08-01 的 mock 运行。已获批的证据抽取（PR #31）在 `source_manifest.json` 中声明的来源是 `ADC_internalization_reference`，**没有接入本库**。

这解释了一件之前没解释的事：**为什么已批准层只有跨膜段注释。** 不是数据不存在，是当时没接。

初稿据此请求把这一个版本纳入已批准来源。

> **本段与下一小节已被第十节阻断 1 推翻。** 派生数据库不能靠自声明 + 哈希纳入；admission 已剥离为独立依赖项 `SRCADM-01`，本契约只引用不批准。原文保留以对照裁决前后差异。

### 主张纳入它的核心理由

该库 `build_manifest.json` 的 `consensus_semantics` 已经写死了本仓库反复要求的守卫，其中两条正是前几轮审核的阻断本身：

- `membrane_topology_is_independent_surface_localization: false` ← **PR #58 第二轮阻断**
- `absence_is_negative_evidence: false` ← 缺失一律 DEFER
- `generic_membrane_is_surface_confirmation: false`、`cci_receptor_role_is_surface_confirmation: false`、`tumor_ihc_is_surface_density: false`
- 排除 `GSE160572_MM_surfaceome.csv.gz`，理由是它是 RNA FPKM 而非蛋白测量 ← RNA 规则

它还自设 `full_t7_gate_confidence_cap: 0.55`，并声明自己不建立 malignant-cell positive fraction、isoform usage、calibrated treatment stability 或 ADC accessibility——即它自己就划开了 Level 02 边界。

守卫是构建时写死的，不是本契约事后附加的。这是主张纳入它、而不是另起一次网络抽取的核心理由。

> **更正（第十节阻断 1）**：以上六条现一律标记 `status: claim_pending_audit`。它们是主张 admission 的**理由**，不是 admission 已完成的**证据**——库自己声明遵守某条规则，不等于已验证它确实遵守。

## 三、仓库内交付了什么

| 文件 | 作用 |
|---|---|
| `docs/tasks/EVGAP_01_SURFACE_LOCALIZATION_EXTRACTION_CONTRACT.zh-CN.md` | 抽取契约（面向操作者，中文） |
| `docs/pools/evgap_01_surface_localization_extraction.yaml` | 机器可读绑定：来源依赖项 `SRCADM-01`＋完整性校验和、字段白名单、禁读清单、RQ 映射、求值优先级、五条判据规则、输出 schema 与 15 条验证 |
| `tests/test_evgap_01_surface_localization.py` | 26 项校验 |

## 四、确定性映射与实测结果

`RQ-01` 用 `independent_evidence_family_count ≥ 2`。该库的三个独立家族是 `curated_knowledge`／`imaging`／`cell_surface_capture_ms`，**拓扑与泛膜已被排除在家族计数之外**，所以家族计数在结构上不可能把跨膜段当定位证据。

`RQ-02` 有两条路径。**`ECD-b` 是必需的，理由是修正数据表示假象。** UniProt 的 extracellular domain 字段由跨膜蛋白的 TOPO_DOM 推导；GPI 锚定蛋白零跨膜段、无 TOPO_DOM，该字段一律 `false`。只用 `ECD-a` 会让 `CEACAM5`、`MSLN`、`FOLR1`、`MELTF` 因假象落 hold——四者在库中都是 `confirmed_surface`、都带信号肽与 GPI 锚。GPI 锚 + 信号肽 + 零跨膜段在结构上即意味着全长成熟蛋白位于胞外。

`LAMP1` 是对照：有跨膜段与信号肽，但结构域朝向溶酶体腔内、无胞外 TOPO_DOM，两条路径都不满足，落 hold。规则自然落在正确一侧，无需特判。

| ID | 条件 | outcome | 数量 |
|---|---|---|---|
| `E1-01` | 三项 RQ 全满足且无冲突 | `eligible_surface_target` RETAIN | **22** |
（按冻结的优先级 `E1-05` → `E1-04` → `E1-03` → `E1-02` → `E1-01` 求值，见第十节阻断 4）
| `E1-02` | 独立家族数 < 2 | `possible_surface_target` DEFER | **6** |
| `E1-03` | 两条 ECD 路径都不满足 | `possible_surface_target` DEFER | **3** |
| `E1-04` | `discordance_flags` 非空 | `possible_surface_target` DEFER | **6** |
| `E1-05` | 不在参考库中 | `possible_surface_target` DEFER | **4** |

22 + 6 + 3 + 6 + 4 = 41，零自由裁量、零排除。`not_surface_target` 与 `identity_unresolved` 仍不可用。

## 五、三条必须写进结果报告的发现

- **`MF-01`：`GUCY2C` 落 hold。** 只有 `curated_knowledge` 一个独立家族，`consensus_class` 是 `supported_surface` 而非 `confirmed_surface`。**这与此前多模型共识把 GUCY2C 列为首选、以及被隔离运行的 Tier A 选择相反。** 必须原样写出，不得因与既有偏好冲突而弱化。测试会检查 `MF-01` 声称 hold 的靶点确实出现在某条 DEFER 规则的 `measured_targets` 里，防止这条发现被改成空话。
- **`MF-02`：`eligible` 只是身份与拓扑层面的结论**，不表示在 CRC 肿瘤细胞表面可得——那是 Level 02 的 T7。
- **`MF-03`：零排除。** hold 不是淘汰，是待证据。

## 六、明确没有做什么

- **没有执行抽取**，没有产生任何证据行、判定或候选。
- 没有执行 Level 01，也不授权执行——`EVGAP-02` 仍未解除。
- 没有读取被禁的四个文件（`tumor_surface_measurement`、`tumor_protein_context`、`treatment_surface_response`、`receptor_evidence`）作为判据；本 handoff 中引用的覆盖率与计数只来自白名单字段。
- 没有解除 `EVGAP-01` 本身——解除要等抽取执行、结果 PR 获批，再另开 PR 更新输入绑定。
- 没有引用被隔离运行（PR #53、#54）的任何产物。
- 没有新增靶点或 clinical context。
- **没有补 #52／#53／#54／#57／#58 的批准记录**（现在是五份）。事实已查全，未写文件。
- 没有修 `requirements.txt` 注释里过期的「207 tests」（实测 309）。属无关改动。

## 七、验证结果

- `Ran 309 tests` 全部通过（`main` 基线 283 + 本次新增 26）。
- `scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- `git diff --check`：通过；零 `__pycache__`。
- 所有计数由脚本读取外部数据库实测，非估计：41 靶点中 37 覆盖 / 4 未覆盖；`consensus_class` 为 29 `confirmed_surface` / 7 `supported_surface` / 1 `no_surface_support`；独立家族数分布 3 家族 10 个、2 家族 19 个、1 家族 7 个、0 家族 1 个；`discordance_flags` 非空 6 个；最终 22 eligible（`ECD-a` 18 + `ECD-b` 4）/ 19 hold / 0 killed。
- 四个数据库文件的 SHA-256 由 `shasum -a 256` 实算。

## 八、后续顺序

1. 本契约 `APPROVE`。
2. **`SRCADM-01` 独立 source admission PR** 审计 `AUD-01`..`AUD-09` → `APPROVE`，在 `logs/` 留记录。
3. 把 `admission_record_ref` 指向该记录，执行抽取 → 结果 PR → `APPROVE`。
4. 另开 PR 更新 `adc_pool_level_01_input_binding.yaml`，绑定抽取产物并解除 `EVGAP-01`。
5. `EVGAP-02` 需其独立契约。**两个缺口都解除后，Level 01 才能执行。**

## 九、当前阻断

- 本契约获 `APPROVE` 前，不得执行抽取。
- **获 `APPROVE` 后仍不得执行抽取**，直到 `SRCADM-01` 取得独立 `APPROVE` 记录（`VAL-E13`）。
- 抽取完成也**不**解除 `EVGAP-02`，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。

## 十、第一轮审核裁决与修订（`REQUEST_CHANGES`，四条阻断全部接受）

ChatGPT 对 PR #59（HEAD `570562c`）返回 `REQUEST_CHANGES`。四条阻断**全部接受**，已在同一 PR 内做最小修订。

### 阻断 1（接受）：未批准数据库不能靠自声明升级为 approved source

`ADC_surfaceome_reference@0.3.0` 是**派生数据库**，不是原始公开数据源。初稿只记录了 snapshot、SHA-256、builder 路径与该库自己的语义守卫，而测试明确不读外部数据库，因此实际上**没有审计** builder 实现、raw manifest、原始来源清单、license、evidence family 是否真正独立、去重与冲突处理、代表性行回溯、snapshot 可重建性。

审核方的判断是对的：**该库自己声明 `membrane_topology_is_independent_surface_localization = false`，不等于它确实遵守这条规则。** 我把「它的语义写得对」当成了「它已被验证」。

修订：把 source admission 从本契约剥离，改为依赖项 `SRCADM-01`——`admission_status: pending_separate_admission_pr`、`admission_record_ref: null`（本契约不得代填）、`authorises_extraction_run: false`、`extraction_blocked_by: [SRCADM-01]`。登记该 admission PR 必须逐项审计的 `AUD-01`..`AUD-09`（builder 与版本、raw manifest 对应、来源清单与 release、license 与再分发、family 独立性、去重逻辑、discordance 生成、代表性靶点回溯、可复现构建）。六条自声明守卫一律标 `status: claim_pending_audit`——它们是主张 admission 的理由，不是 admission 已完成的证据。四个 SHA-256 保留但角色降为 `files_pinned_for_integrity_only`。新增 `VAL-E13`：抽取前 `admission_record_ref` 必须指向实际存在的独立 `APPROVE` 记录，为空即不得执行。

### 阻断 2（接受）：RQ-02 路径计数与 E1-02 自相矛盾

初稿写 `ECD-a measured_count = 18`、`ECD-b = 4`，并让测试强制 18 + 4 = 22 eligible。但 `E1-02` 的 6 个靶点是「`RQ-02` 满足但家族数 < 2」——它们必然也命中某条 ECD 路径。**我把「满足 ECD 路径」错等于「最终 eligible」。**

实测后修订为两个分开的计数：`ECD-a` 路径命中 **30**、其中最终 eligible **18**；`ECD-b` 路径命中 **4**、其中 eligible **4**；两条路径无重叠。并写入分解恒等式：**34 个 RQ-02 阳性 = 22 eligible + 6 `E1-02` + 6 `E1-04` 中 RQ-02 阳性者**。新增 `VAL-E12` 与两条测试：eligible 不得超过路径命中数；`eligible_via_path` 之和必须等于 `E1-01`，而路径命中之和减去重叠必须等于 RQ-02 阳性总数。

### 阻断 3（接受）：VAL-E05 与 reference-absent 靶点冲突

`E1-05` 的 4 个靶点不在参考库中，`source_evidence.tsv` 里本就没有它们的行，而初稿的 `VAL-E05` 要求**每行**都有非空 `source_ids`／`source_releases`／`source_urls`／`licenses`。后果正如审核方所说：合法的 hold 行无法通过验证，或迫使执行者伪造 provenance。

修订：provenance 拆成两类。覆盖行须有完整来源 provenance；未覆盖行的 `source_*` 允许为空，但必须有完整**缺失 provenance**——`reference_dataset_id`、`reference_dataset_version`、`reference_snapshot_id`、`target_axis_ref`、`absence_reason`（只能取 `gene_symbol_not_present_in_reference`）、`lookup_at`。新增 `VAL-E05b`／`VAL-E05c`：**禁止伪造 source evidence，禁止把缺失表述为 source-supported**——`provenance_kind = reference_absent` 的行若出现非空 `source_ids` 即为验证失败。输出列 21 → 26，新增 `provenance_kind`、`absence_reason`、`target_axis_ref`、`lookup_at`。

### 阻断 4（接受）：五条规则没有冻结优先级

条件并非天然互斥，而 `VAL-E01` 要求「命中且仅命中一条」。实测本 snapshot 下有 **2 个**靶点同时满足 `E1-03` 与 `E1-02`：`TM4SF1`、`TDGF1`。初稿只验证了预写计数之和等于 41，**没有证明真实条件下的 one-and-only-one**。

修订：冻结 `derivation_precedence` = `E1-05` → `E1-04` → `E1-03` → `E1-02` → `E1-01`，并写明理由；登记 `measured_multi_condition_targets`，两个靶点解析到 `E1-03`。新增 `VAL-E11`。测试新增三项：优先级覆盖全部规则且首尾正确；用等价 fixture 逐例证明九种条件组合（含 absent+conflict、conflict+low-family、conflict+no-ECD、no-ECD+low-family）各有唯一结果；重叠靶点必须落在优先级更高的规则、且**不得被计入被压制的那条规则的 `measured_targets`**。

**计数未变**：按冻结后的优先级重算仍是 22／6／3／6／4，与初稿一致——因为初稿的计算脚本已隐含同一顺序，只是没把顺序写进契约。

### 本轮变异检验

12 个变异全部被捕获后精确回滚，与备份 `diff -q` 一致、测试恢复 `OK`：自行填入 admission 记录并放行、把自声明守卫标为已验证、删掉 license 审计项、让 eligible 超过路径命中数、用 eligible 冒充路径命中数、破坏分解恒等式、要求未覆盖行也有 source 字段、允许伪造 source evidence、删掉 `absence_reason` 要求、把 `E1-01` 提到优先级最前、把冲突优先级降到最后、让重叠靶点解析到被压制的规则。

### 审核方认可、本轮未改动的部分

`ECD-b` 路径（在 GPI 注释可靠、同时有信号肽、零跨膜段与蛋白级 provenance 的前提下）可作为 extracellular topology 路径；跨膜段不再单独满足 `RQ-01`；GPI 路径没被当成普通跨膜蛋白规则；`LAMP1` 的腔内结构域不被当成胞外；缺失与冲突均 DEFER 不 EXCLUDE；`not_surface_target` 仍不可用；T7 与肿瘤定量文件明确禁止；不执行 Level 01；不新增 target／context；仓库不存 evidence／result；`EVGAP-02` 继续未解除。

### 审核回写状态

审核方尝试通过 GitHub 连接器提交正式 `REQUEST_CHANGES` review，连接器返回 403，未写回 GitHub。裁决以人类负责人转述为准，已记录于本节与 `logs/worklog.md`。

## 十一、第二轮审核裁决与修订（`REQUEST_CHANGES`，两条阻断全部接受）

ChatGPT 对 PR #59（HEAD `f236287`）返回 `REQUEST_CHANGES`。上一轮四条确认已基本修复；本轮两条**契约缺口**全部接受。两条都是我留下的洞。

### 阻断 1（接受）：covered target 的 RQ-03 缺失没有对应 derivation rule

审核方构造的组合是对的：一个在库中的靶点，`RQ-01` 满足、`RQ-02` 满足、无 discordance，但 `source_evidence.tsv` 字段不全导致 `RQ-03` 不满足——它不命中 `E1-01`（RQ-03 未满足）、不命中 `E1-02`（家族数不低）、不命中 `E1-03`（RQ-02 满足）、不命中 `E1-04`（无冲突）、不命中 `E1-05`（在库中）。**`VAL-E01` 的「恰好命中一条」因此无从满足**，而 `VAL-E05` 只写「缺失即该行降为 hold」，没说降到哪条规则，也没有对应 `rule_id`。

修订：新增 `E1-04b`——「在库中但 `RQ-03` provenance 不成立」→ `possible_surface_target` DEFER `hold`。插入优先级第三位：`E1-05` → `E1-04` → **`E1-04b`** → `E1-03` → `E1-02` → `E1-01`。理由写入契约：provenance 不成立时该行证据本身不可引用，再谈拓扑与家族数没有意义，所以排在两个 RQ 判据之前、冲突之后。其 disposition 只能是 DEFER——既不得 RETAIN（无可回溯来源），也不得 EXCLUDE（缺 provenance 不是否定证据）。

**实测 37 个覆盖靶点全部满足 `RQ-03`**，故 `E1-04b` 在本 snapshot 下 `expected_count: 0`、`vacuous_this_run: true`，**计数不变**（22／6／3／6／0／4 = 41）。但它必须存在：provenance 完整性不由本契约保证，抽取时可能失败。

测试新增按验收标准的组合：`RQ-01=true, RQ-02=true, RQ-03=false` → `E1-04b`；`discordance=true 且 RQ-03=false` → `E1-04`（冲突优先）；`RQ-02=false 且 RQ-03=false` → `E1-04b`；共 13 种组合逐例证明恰好命中一条，且 provenance 缺失只能 DEFER。

### 阻断 2（接受）：`VAL-E05b` 要求的字段没有全部进入 output schema

`VAL-E05b` 要求六列，而 `per_target_columns` 初稿只加了 `absence_reason`、`target_axis_ref`、`lookup_at` 三列，缺 `reference_dataset_id`、`reference_dataset_version`、`reference_snapshot_id`。**执行者无法同时遵守 output schema 与 validation rule。** 这是我上一轮补 blocker 3 时漏改的。

修订：三列补入 `per_target_columns`（21 → 26 → **29** 列）。新增 `conditionally_required_columns` 明确条件必填——`provenance_kind = reference_absent` 时六列必填、`source_*` 可空；`provenance_kind = source_supported` 时 `source_*` 必填、这六列可空。并加 `pinned_to_admission_snapshot`：三列必须分别等于 `ADC_surfaceome_reference`／`0.3.0`／`2026-07-29-quant-topology-mm`，不得自由填写；新增 `VAL-E05d` 强制。

测试直接断言 `required_absence_fields ⊆ per_target_columns`，并断言 pinned 值与 `source_admission_dependency` 的 `dataset_id`／`dataset_version`／`snapshot_id` 逐项相等——admission 版本一变，pinned 值不同步就会失败。

### 本轮变异检验

8 个变异全部被捕获后精确回滚，与备份 `diff -q` 一致、测试恢复 `OK`：从优先级里删掉 `E1-04b`、把 `E1-04b` 改判 RETAIN、把 `E1-04b` 排到 `E1-01` 之后、让 RQ-03 不指向失败规则、删掉 `reference_dataset_id` 列、让 pinned 值与 admission 不符、让 `source_supported` 不要求来源字段、谎报 RQ-03 有失败靶点。

### 审核方认可、本轮未改动的部分

`AUD-01`..`AUD-09` 足以覆盖 builder、raw manifest、license、family independence、去重、discordance、行级 provenance 与重建；`admission_record_ref = null` 时不得执行抽取；自声明守卫仅作 pending claim；RQ-02 分解自洽（34 = 22 + 6 + 6）；`ECD-b` 路径合理；reference-absent 靶点不再被迫伪造 source evidence；precedence 已解决 `TM4SF1`／`TDGF1` 的多条件命中；不执行 Level 01；不评估 T7；不新增 target／context；不读取被禁文件；`EVGAP-02` 仍未解除；仓库内无 evidence 或结果数据。

### 审核回写状态

审核方尝试通过 GitHub 连接器提交正式 `REQUEST_CHANGES` review，连接器返回 403，未写回 GitHub。裁决以人类负责人转述为准，已记录于本节与 `logs/worklog.md`。
