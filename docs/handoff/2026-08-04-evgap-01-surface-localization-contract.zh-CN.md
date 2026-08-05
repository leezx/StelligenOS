# Handoff：EVGAP-01 target surface localization 证据抽取契约

- 日期：`2026-08-04`
- 任务分支：`task_20260804_evgap-01-surface-localization-contract`
- 基线：`main` @ `cd0e041`
- 前置：PR #57、PR #58，均已 `APPROVE` 并合并
- 交付物类型：**contract-only**
- 外部运行：**无。没有执行抽取，没有产生任何证据、判定或候选。**
- 授权范围：**一次抽取运行；不授权执行 Level 01**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（依据是 diff 范围，可由 `git diff --stat` 核验）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、本次范围

人类负责人指示继续起 `EVGAP-01` 契约。`EVGAP-01` 是 PR #58 登记的两个缺口之一，阻断 `LOCK-01`：已批准证据层没有蛋白层面的质膜定位与细胞外结构域证据，导致 41 个靶点全部 DEFER、`eligible = 0`、Level 01 无法录入任何 pair。

本次交付该缺口的抽取契约。**不执行抽取。**

## 二、关键发现：所需数据已在本地，但那个数据库从未被批准

`DATA/1.Databases/ADC_surfaceome_reference/processed/v0.3.0` 恰好覆盖三项 RQ 要求。但治理状态必须先讲清楚：

> **该数据库从未被审核批准。** 仓库内 `logs/chatgpt-review-*.md` 无任何一条提及 surfaceome；worklog 唯一提及是 2026-08-01 的 mock 运行。已获批的证据抽取（PR #31）在 `source_manifest.json` 中声明的来源是 `ADC_internalization_reference`，**没有接入本库**。

这解释了一件之前没解释的事：**为什么已批准层只有跨膜段注释。** 不是数据不存在，是当时没接。

因此本 PR 请求把这一个版本纳入已批准来源：`0.3.0` / snapshot `2026-07-29-quant-topology-mm` / `raw_manifest_sha256 884f4191…`，四个文件逐一记录 SHA-256。

### 主张纳入它的核心理由

该库 `build_manifest.json` 的 `consensus_semantics` 已经写死了本仓库反复要求的守卫，其中两条正是前几轮审核的阻断本身：

- `membrane_topology_is_independent_surface_localization: false` ← **PR #58 第二轮阻断**
- `absence_is_negative_evidence: false` ← 缺失一律 DEFER
- `generic_membrane_is_surface_confirmation: false`、`cci_receptor_role_is_surface_confirmation: false`、`tumor_ihc_is_surface_density: false`
- 排除 `GSE160572_MM_surfaceome.csv.gz`，理由是它是 RNA FPKM 而非蛋白测量 ← RNA 规则

它还自设 `full_t7_gate_confidence_cap: 0.55`，并声明自己不建立 malignant-cell positive fraction、isoform usage、calibrated treatment stability 或 ADC accessibility——即它自己就划开了 Level 02 边界。

守卫是构建时写死的，不是本契约事后附加的。这是主张纳入它、而不是另起一次网络抽取的核心理由。

## 三、仓库内交付了什么

| 文件 | 作用 |
|---|---|
| `docs/tasks/EVGAP_01_SURFACE_LOCALIZATION_EXTRACTION_CONTRACT.zh-CN.md` | 抽取契约（面向操作者，中文） |
| `docs/pools/evgap_01_surface_localization_extraction.yaml` | 机器可读绑定：来源纳入请求＋SHA-256、字段白名单、禁读清单、RQ 映射、五条判据规则、输出 schema 与十条验证 |
| `tests/test_evgap_01_surface_localization.py` | 15 项校验 |

## 四、确定性映射与实测结果

`RQ-01` 用 `independent_evidence_family_count ≥ 2`。该库的三个独立家族是 `curated_knowledge`／`imaging`／`cell_surface_capture_ms`，**拓扑与泛膜已被排除在家族计数之外**，所以家族计数在结构上不可能把跨膜段当定位证据。

`RQ-02` 有两条路径。**`ECD-b` 是必需的，理由是修正数据表示假象。** UniProt 的 extracellular domain 字段由跨膜蛋白的 TOPO_DOM 推导；GPI 锚定蛋白零跨膜段、无 TOPO_DOM，该字段一律 `false`。只用 `ECD-a` 会让 `CEACAM5`、`MSLN`、`FOLR1`、`MELTF` 因假象落 hold——四者在库中都是 `confirmed_surface`、都带信号肽与 GPI 锚。GPI 锚 + 信号肽 + 零跨膜段在结构上即意味着全长成熟蛋白位于胞外。

`LAMP1` 是对照：有跨膜段与信号肽，但结构域朝向溶酶体腔内、无胞外 TOPO_DOM，两条路径都不满足，落 hold。规则自然落在正确一侧，无需特判。

| ID | 条件 | outcome | 数量 |
|---|---|---|---|
| `E1-01` | 三项 RQ 全满足且无冲突 | `eligible_surface_target` RETAIN | **22** |
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
- 没有修 `requirements.txt` 注释里过期的「207 tests」（实测 298）。属无关改动。

## 七、验证结果

- `Ran 298 tests` 全部通过（`main` 基线 283 + 本次新增 15）。
- `scripts/verify_repository_boundary.sh`：`Repository boundary check passed.`
- `git diff --check`：通过；零 `__pycache__`。
- 所有计数由脚本读取外部数据库实测，非估计：41 靶点中 37 覆盖 / 4 未覆盖；`consensus_class` 为 29 `confirmed_surface` / 7 `supported_surface` / 1 `no_surface_support`；独立家族数分布 3 家族 10 个、2 家族 19 个、1 家族 7 个、0 家族 1 个；`discordance_flags` 非空 6 个；最终 22 eligible（`ECD-a` 18 + `ECD-b` 4）/ 19 hold / 0 killed。
- 四个数据库文件的 SHA-256 由 `shasum -a 256` 实算。

## 八、后续顺序

1. 本契约 `APPROVE`。
2. 执行抽取 → 结果 PR → `APPROVE`。
3. 另开 PR 更新 `adc_pool_level_01_input_binding.yaml`，绑定抽取产物并解除 `EVGAP-01`。
4. `EVGAP-02` 需其独立契约。**两个缺口都解除后，Level 01 才能执行。**

## 九、当前阻断

- 本契约获 `APPROVE` 前，不得执行抽取。
- 抽取完成也**不**解除 `EVGAP-02`，Level 01 仍不可执行。
- 本仓库不得写入证据、候选、快照、cache、result 或 weights。
