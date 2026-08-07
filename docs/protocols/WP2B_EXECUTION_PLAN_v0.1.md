# WP2B CRC Opportunity Territory Map — Execution Plan v0.1

- 状态：`DRAFT_PENDING_HUMAN_APPROVAL`。**不执行任何 territory 枚举。**
- 类别：execution protocol。**不新增 architecture semantics，不修改 `#77`–`#80`
  已冻结的 contracts/policies。**
- 消费对象：`docs/pools/wp2b_crc_territory_map_run.yaml` 当前
  `authorises_run_count: 1`——**本计划本身不消费它**；消费动作只在人类批准本计划
  之后、真正执行 territory 枚举时发生。
- 依赖且不修改：
  - `src/contracts/opportunity_territory.py`（`OpportunityTerritory@0.1.0`／
    `OpportunityTerritoryMap@0.1.0`，PR #77）
  - `src/contracts/search_space_admission.py`（八项 admission 标准，PR 早期）
  - `docs/pools/search_space_route_policy.yaml`
    （`search_space_admission_route_policy@0.1.0`，PR #79）
  - `docs/pools/wp2b_crc_territory_map_run.yaml`（运行契约，PR #78/#80）
  - `DevelopmentSponsorProfile` 冻结实例 v0.1.2
    （`gen_sponsor_profile_stelligen_v0.1.2_20260807T150000Z_frozen`，实例 SHA-256
    `41f8e02680a976cdf4db34cd18dbf0dfd7a566ed160230934c753d3e7241544a`）

---

## 0. 本计划要回答的问题

上一轮审核指出：#78–#80 花了大量时间把 contract、Sponsor Profile、route policy
冻结下来，真正执行反而最容易返工的不是代码，而是「territory 到底怎么枚举、搜到
什么程度才算 investigate complete」。本计划把这两件事在执行前钉死。

---

## 1. Executor

本次由 Claude 执行，使用可访问的公开检索能力。不为 WP2B v0.1 另建自动化采集
pipeline——首要目标是建立一个高质量、可审计的 CRC territory baseline，把
ontology、territory granularity、evidence depth 和路由逻辑跑通，而不是提前
工程化一个尚未稳定的方法。

### 1.1 授权单位是一个 `run_id`，不是一次会话

`wp2b_crc_territory_map_run.yaml` 授权的是**一次运行**（`authorises_run_count:
1`），单位是 `run_id`，不是「一次 Claude 对话」。给定 15–30 个 territory、每个
还要临床、竞争、trial、biology、buyer/IP/time window 等 field-level
provenance，把整个运行硬绑在一次会话内不稳健——上下文长度或工具中断不应逼着
草率收尾。

因此本次运行可以跨越多个**执行检查点／续接会话**，形态例如：

```
Pass A enumeration → checkpoint
  → Pass B normalization → checkpoint
  → breadth-first evidence（第 7 节） → checkpoint
  → ACTIVE_SEARCH 候选的第二轮 deeper verification → checkpoint
  → 最终打包
```

**跨检查点必须保持不变的四项：** `knowledge_cutoff`（第 4 节）、已批准冻结的
`DevelopmentSponsorProfile` 实例（v0.1.2，SHA-256 见文首）、
`search_space_route_policy.yaml`（PR #79）、第 3 节 source policy，以及一份
连续的 query log（第 14 节 `run_manifest.json`）。四项任一变化都不是同一次
运行的延续，而是新的 `run_id`，需要重新走授权流程——这不在本计划授权范围内。

这不产生第二次运行，也不消费第二次授权：`run_manifest.json` 里的 `run_id` 全程
唯一，检查点只是同一个 `run_id` 下的执行进度记录。

### 1.2 工具清单与决定（如实记录，不夸大）

| 工具 | 状态 | 用途 |
|---|---|---|
| `WebSearch` | 可用，无需授权 | 发现型检索；美国地区限定 |
| `WebFetch` | 可用，无需授权 | 抓取公开 URL 并转 markdown 摘要；对非结构化页面（新闻、公司 IR 页）够用，对结构化字段（trial phase、enrollment、arm 设计）会有损 |
| `PubMed` MCP connector | **已安装但未授权**，需要用户在浏览器完成 OAuth | 结构化文献检索，对应第 3 节 `pubmed`／`pmc` |
| `Clinical Trials` MCP connector | **已安装但未授权**，需要用户在浏览器完成 OAuth | 结构化试验数据（phase、状态、入组、readout），对应第 3 节 `clinicaltrials_gov`——对第 10 节 competition/window-closure 调查价值最高 |

**决定：** 授权 `PubMed` 与 `Clinical Trials`；`bioRxiv` 不用于 WP2B v0.1
——预印本不在第 3 节 `tier_1_sources` 之内，且会增加证据等级管理复杂度，对本次
不是必要输入。两个 connector 均对应第 3 节已冻结的 source class，**不因
connector 可用与否而改变冻结的 source 语义**——若届时 OAuth 未完成，退回
`WebSearch` + `WebFetch` 直接访问 `clinicaltrials.gov`／`pubmed.ncbi.nlm.nih.gov`
公开页面作为 fallback，但正式证据仍必须落在第 3 节允许的来源类别内，不因
fallback 而放宽。

不允许：

- 使用任何 institution/private/unpublished data；
- 把创始人的学术接触当作 Stelligen-controlled evidence；
- 使用 quarantined sources（`EVGAP-01`／`EVGAP-02` 涉及的隔离来源，与旧
  369-pair 池同源的派生数据库）；
- 使用 Tier-2 derived database 代替 primary evidence；
- 从旧的 369 target-pair pool 反向生成 territories；
- 提前生成 target candidates 或 program wedges（WP3 的范围）。

---

## 2. Search objective

WP2B 不做 `CRC unmet needs × targets`。目标是建立 **CRC clinical / biological
opportunity territories**——每个 territory 必须是一个后续可以独立产生 Program
Wedge 的临床搜索水域。

Territory 主要由以下轴定义：

- disease stage
- molecular subtype
- treatment line
- prior treatment
- treatment-resistance state
- metastatic context/site（仅当临床意义明确时）
- clinically meaningful biological state（仅当有证据支持时）
- current SOC failure mode

**不允许仅因为存在一个靶点、基因或 ADC 项目就创建 territory。** 这条对应
`OpportunityTerritory@0.1.0` 里没有任何 `target_ref` 字段的设计——契约本身就
不允许以靶点为主键。

---

## 3. Source hierarchy（不扩大冻结契约，逐字对齐 `wp2b_crc_territory_map_run.yaml` 的 `source_policy`）

上一版在此新增了 NCCN/ESMO/ASCO guideline、WHO ICTRP，并把 TCGA/GEO/cBioPortal/
GTEx/HPA/DepMap 统称「Tier 1E formal evidence」——**这是擅自扩大冻结的 source
admission**，不是执行细节。冻结契约 `source_policy.tier_1_sources` 只列七类：

```yaml
tier_1_sources:
  - pubmed
  - pmc
  - clinicaltrials_gov
  - fda_labels_and_approvals
  - ema_labels_and_approvals
  - company_public_disclosure
  - conference_abstract_public_record
tier_2_derived_databases_permitted: false
```

本计划**不新开 source-admission PR**，因此正式来源严格限定在这七类，逐一对应：

| 冻结 source class | 用途 | 置信度标注 |
|---|---|---|
| `pubmed`／`pmc` | clinical outcome、resistance population、molecular subtype、metastatic-state evidence、human biomarker evidence；treatment-guideline 若以 JCO／Annals of Oncology／JNCCN 等 PubMed 索引期刊发表，落在这一类，不单开 guideline tier | — |
| `clinicaltrials_gov` | trial stage、enrollment/status、竞争者试验进度 | — |
| `fda_labels_and_approvals`／`ema_labels_and_approvals` | current SOC、批准适应症、treatment line、regulatory status | — |
| `company_public_disclosure` | trial initiation、enrollment/status、topline result、licensing/acquisition、disclosed development strategy | **不得仅凭 sponsor claim 判定 clinical superiority** |
| `conference_abstract_public_record`（ASCO、AACR、ESMO、ASCO GI 等原始未发表摘要） | 可能改变 competitive position／window closure 的项目 | **必须标注 `CONFERENCE_ONLY`，不得与完整同行评审证据混为同一 confidence** |

**未解决的张力，如实记录而非自行裁定：** `evidence_standards.clinical_definition`
与 `current_failure` 两个 field group 的 `requires` 字段写的是「公开指南、标签或
同行评议文献」——字面提到「指南」，但 `source_policy.tier_1_sources` 里没有
「guideline」这个独立类别。本计划不通过新增 Tier 解决这处张力：guideline 内容
只有在能落进上表七类之一时才算正式来源（例如已发表为 PubMed 索引论文的共识
指南，或已反映在 FDA／EMA 批准标签里的 SOC）；只能在专属 guideline 网站找到、
无法归入七类任一类的内容，只作 discovery-only，不进入 `source_manifest.json`。

**明确排除出正式 Tier 体系**（按上一轮审核裁定）：

- NCCN/ESMO/ASCO **独立** guideline 页面（不是以上七类的载体时）；
- WHO ICTRP 或其他官方注册库——冻结契约只认 `clinicaltrials_gov`；
- TCGA、GEO、cBioPortal、GTEx、HPA、DepMap——**一律不得出现在
  `source_manifest.json`**（直接触发 `VAL-T16`）。`cBioPortal` 是典型 Tier-2
  派生数据库；TCGA／GEO／GTEx／HPA／DepMap 同样缺少各自的 `SRCADM-02..05`
  admission，`tier_2_derived_databases_permitted: false` 覆盖它们全部，本计划
  不代为裁定谁该单独获得豁免。

**这六个公开资源仍有合法用途，但只在 `availability` field group 内**（`
known_target_biology_refs`／`available_patient_data_refs`／
`available_model_refs`），该组 `requires` 允许「发起方可核验的资源清单」，
用途仅限描述 territory 是否 computationally addressable、是否存在公开人体
证据——**不作为 clinical_definition／current_failure／competition／
sponsor_fit_context／timing 任何字段的证据来源**，且这类 ref 不进入
`source_manifest.json` 的 Tier 分类。与冻结 profile v0.1.2 已有的硬不变量
一致：公共数据库本身不得令 `asymmetric_evidence_advantage = SATISFIED`
（`public_data_plus_generic_bioinformatics_is_insufficient`），此处复用，不
重新定义。

**Discovery-only**：Google Scholar、PubMed related articles、综述，仅用于发现
primary source 的路径，**不得作为关键 route criterion 的唯一证据**；最终
field-level evidence 必须落到上表七类之一。

`field_evidence_map.json` 中每条 `evidence_ref` 必须能对应到七类之一；
`CONFERENCE_ONLY` 与 `company_public_disclosure` 来源的记录必须显式携带对应
标注字段，校验脚本会检查这一点（见第 17 节）。

---

## 4. Temporal cutoff

```
knowledge_cutoff = 2026-08-07
```

以下字段必须主动检查最新状态，不得仅依赖较旧 review 推断：

- current SOC
- leading competitor
- Phase II/III trial status
- recent regulatory approval
- expected near-term readout
- transaction landscape

---

## 5. Two-pass territory generation

### Pass A — high-recall 枚举

目标是尽量覆盖 CRC 中临床上真实存在的治疗空间，**不是**立即路由。系统性枚举
以下方向（人类审核方给定的清单，逐字保留）：

- metastatic MSS/pMMR CRC
- MSI-H/dMMR
- RAS WT / anti-EGFR exposed
- KRAS-mutant subclasses where clinically actionable
- BRAF V600E
- HER2-positive
- rare actionable genotypes only if they constitute meaningful treatment territories
- post-standard-chemotherapy refractory disease
- post-targeted-therapy resistance
- liver-dominant metastatic disease
- peritoneal metastatic disease
- other metastatic-site/state contexts only when evidence shows distinct therapeutic implications
- treatment-induced / drug-tolerant / lineage-state territories only when supported by human evidence

**不预设必须得到 15–30 个。** 合理重叠可以存在，但必须说明两个 territories
为什么不是同一个 territory（写入 `reconciliation_report.md`）。

### Pass B — consolidation / normalization

对 Pass A 结果：

- merge synonyms；
- remove target-defined pseudo-territories；
- remove biologically interesting但临床不可行动的状态；
- 只在 treatment history／SOC／competitive landscape 真正不同时才 split。

输出实际 territory count。**15–30 仅作 `VAL-T01` 的 reconciliation reference**
（报告实际数量，落在区间外不构成失败但须给出 reconciliation note，PR #78 已
冻结的 `territory_count_band` 处理方式——不要与同一契约里 `expected_active_
band`（4–8，指 `ACTIVE_SEARCH` 数量，同样只是 reconciliation reference）混用，
两个区间对应不同的量），**不得为凑数 split/merge**。`VAL-T02`
（`territory_id` 全局唯一）是另一条规则，也不要混用。

---

## 6. 每个 territory 的最小调查深度

上一版声称「18 项调查深度逐一对应 `OpportunityTerritory` 字段」不成立——
`OpportunityTerritory@0.1.0` 实际有 21 个字段（含 `territory_id`／
`search_space_admission_ref`／`source_refs` 三个结构性字段），18 项清单漏了
`disease_ref`、`molecular_subtype_ref`、`treatment_line_ref`、
`prior_therapy_refs`、`metastatic_site_refs`、`known_target_biology_refs`、
`source_refs`。下表覆盖全部 21 个字段，逐一标注所属 `evidence_standards`
field group 与该组的 unknown/empty 处理方式（第 6.1 节展开）：

| # | 契约字段 | field_group | unknown/empty 处理 | 调查内容 |
|---|---|---|---|---|
| 1 | `territory_id` | 结构性（`VAL-T02` 全局唯一） | 不适用 | 唯一标识，不是证据字段 |
| 2 | `disease_ref` | `clinical_definition` | **不允许 UNKNOWN** | Disease 定义 |
| 3 | `clinical_population_ref` | `clinical_definition` | **不允许 UNKNOWN** | Patient definition |
| 4 | `molecular_subtype_ref` | `clinical_definition` | **不允许 UNKNOWN** | Molecular subtype |
| 5 | `treatment_line_ref` | `clinical_definition` | **不允许 UNKNOWN** | Treatment line |
| 6 | `prior_therapy_refs` | `clinical_definition` | **不允许 UNKNOWN** | Prior therapy exposure |
| 7 | `metastatic_site_refs` | `clinical_definition` | **不允许 UNKNOWN** | Metastatic site/context |
| 8 | `current_soc_ref` | `current_failure` | **不允许 UNKNOWN** | Current SOC |
| 9 | `clinical_failure_mode_ref` | `current_failure` | **不允许 UNKNOWN** | Main clinical failure/unmet need |
| 10 | `patient_size_band_ref` | `current_failure` | **不允许 UNKNOWN**（只需分档，不需精确数字） | Approximate population relevance |
| 11 | `current_competitor_refs` | `competition`（list） | empty 允许，须与未调查区分（`VAL-T14`） | Current leading competitors |
| 12 | `leading_asset_refs` | `competition`（list） | empty 允许，须与未调查区分 | Highest development stage |
| 13 | `expected_readout_refs` | `competition`（list） | empty 允许，须与未调查区分 | Important expected readouts |
| 14 | `position_occupancy_ref` | `competition`（single ref，非 list） | **ref 本身不允许为空**——契约里与第 11–13 行同组，但它是 `TERRITORY_SINGLE_REFERENCE_FIELDS` 而非 list 字段，无法为空；结论可以是 `UNRESOLVED` | Evidence that position is locked / not locked / unresolved |
| 15 | `known_target_biology_refs` | `availability` | empty 允许 | 背景生物学情报（仅背景，不是 target candidate，见 PR #77 非阻断意见） |
| 16 | `available_patient_data_refs` | `availability` | empty 允许 | Public patient data availability |
| 17 | `available_model_refs` | `availability` | empty 允许 | Public model availability |
| 18 | `sponsor_evidence_advantage_ref` | `sponsor_fit_context` | **UNKNOWN 允许，且不得省略该字段**（`VAL-T15`） | Territory-specific evidence advantage（profile 本身不足以支撑，见第 9 节） |
| 19 | `window_closure_risk_ref` | `timing` | UNKNOWN 允许 | Window-closure risk（profile 只贡献执行时间跨度那一半） |
| 20 | `search_space_admission_ref` | 结构性（`VAL-T04` 恰好一个） | 八项标准各自 `SATISFIED`／`UNKNOWN`／`UNSATISFIED`，机制见第 6.1 节末段 | 八项 `SearchSpaceAdmission` 标准 + 按 PR #79 解出路由 |
| 21 | `source_refs` | 结构性（`VAL-T13` 每个非空字段至少一条） | 不适用 | 聚合引用列表 |

### 6.1 UNKNOWN 语义——不是「缺资料就写 UNKNOWN」

上一版统一说「任何一项缺资料必须写 UNKNOWN」，这与冻结的
`evidence_standards` 直接冲突。正确语义按 field group 三分：

**(a) 硬性必需，不允许 UNKNOWN**——`clinical_definition`（第 2–7 行）与
`current_failure`（第 8–10 行）。原文：「临床定义不完整的 territory 不成立，
不得录入。」**这些字段任一无法确证，该候选 territory 不进入最终
`territory_map.json`，改记入 `reconciliation_report.md` 的
excluded-enumeration 部分，写明缺哪一项、查过哪些来源仍无法确证。** 不是给
该 territory 填 UNKNOWN 后保留它。

**(b) 允许为空，但空必须与未调查区分**——**仅限 list 字段**：
`current_competitor_refs`／`leading_asset_refs`／`expected_readout_refs`
（第 11–13 行）与 `availability`（第 15–17 行）。原文：「无竞争者或无预期
readout 是真实且有信息量的状态，不等于未调查。」空值必须显式标注
`investigated_and_empty`（对应 `VAL-T14`），不能留白。

**`position_occupancy_ref`（第 14 行）不属于 (b)，尽管它在冻结
`evidence_standards` 里与上面三个 list 字段同属 `competition` field group。**
它是 `TERRITORY_SINGLE_REFERENCE_FIELDS` 之一（同 `OpportunityTerritory` 契约
里的 `sponsor_evidence_advantage_ref`／`window_closure_risk_ref`），
`__post_init__` 用 `_require_external_ref` 校验，**永远不允许为空**——这一点
与 evidence_standards 对整个 `competition` 组「`empty_permitted: true`」的
字面表述有张力，如实记录：`empty_permitted` 对这三个 list 字段成立，对
`position_occupancy_ref` 不成立，因为它根本不是 list。**position_occupancy_ref
必须永远指向一份非空的 territory-specific occupancy assessment；无法确证
competitive position 时，该 assessment 内部记
`state = UNRESOLVED`，而不是把 ref 留空或省略。** 空 list（真实无竞争者）与
空 ref（无法产出任何 assessment）是两件不同的事，不能用同一条规则处理。

**(c) UNKNOWN 允许且必须记录，不得省略字段**——`sponsor_fit_context`（第 18
行）、`timing`（第 19 行），以及刚才归类的 `position_occupancy_ref`（第 14
行）。原文（`sponsor_fit_context`）：「优势未知即记未知，不得因『看起来我们
能做』而记为具有优势。未知不转为不具优势，也不转为具有优势。」`VAL-T15`
明确 `sponsor_evidence_advantage` 未知时记 `UNKNOWN`，**不得省略该字段**——
这与 (a) 恰好相反：(a) 是「不确定就不成立」，(c) 是「不确定也要留下这个
字段，标 UNKNOWN／UNRESOLVED」。`position_occupancy_ref` 与
`sponsor_evidence_advantage_ref`／`window_closure_risk_ref` 在这一点上是
同一种机制：ref 必须存在，ref 指向的内容可以是未知/未解决的结论。

**八项 `SearchSpaceAdmission` 标准（第 20 行）是第四种机制**，不属于以上任何
field group：每项标准的状态本身就是 `SATISFIED`／`UNKNOWN`／`UNSATISFIED`
三值（`CriterionStatus`），`UNKNOWN` 是合法值而非例外，按 `search_space_route_
policy.yaml`（PR #79）的 `first_match_wins` 规则表解出路由——`UNKNOWN` 会阻断
`ACTIVE-01`，但不直接决定最终路由，更早的 `OUT-*`／`PARTNER-*` 规则仍可能先
命中，`WATCHLIST` 只是排到最后的 catch-all。详见第 8 节，不是「缺资料」的
兜底捷径。

---

## 7. Evidence depth：广度优先，仅在决策相关处深入

不做系统综述级穷举。

- 普通 territory：1–3 项权威/当前临床来源 + 1–3 项 primary biological/
  translational 来源（按需） + 对 leading competitor 的当前 trial registry 核查。
- **只有可能进入 `ACTIVE_SEARCH` 的 territory** 才进行第二轮 deeper
  verification。

即 `broad map → route candidate → deeper verification`，不对每个 territory
先读 50 篇论文。

---

## 8. `ACTIVE_SEARCH` 特别规则

按 `search_space_route_policy.yaml`（PR #79）的 `ACTIVE-01` 规则，**八项全部
`SATISFIED` 才能成立**——本计划不改动该规则，只在执行层面重申：

**不得为了产生 ACTIVE territory 乐观解释以下四项：**

- `differentiation_visible_preclinical`
- `defensible_ip_path`
- `plausible_buyer_partner_map`
- `time_window_compatible`

只能提出合理假设而没有足够证据时，正确表述不是「`UNKNOWN → WATCHLIST`」这个
捷径，而是：**`UNKNOWN` 会阻断 `ACTIVE_SEARCH`，但不直接决定最终路由。**
最终路由必须永远交给冻结的 `first_match_wins` 规则表求值：

```
OUT-01 / OUT-02 / OUT-03  （clinical_value_exists、time_window_compatible、
                            competitive_position_not_locked 等 UNSATISFIED）
        ↓ 均不命中
PARTNER-01 / PARTNER-02  （competitive_position_not_locked 或
                            asymmetric_evidence_advantage UNSATISFIED，
                            但 clinical_value_exists 与 plausible_buyer_
                            partner_map 均 SATISFIED）
        ↓ 均不命中
ACTIVE-01  （八项全部 SATISFIED）
        ↓ 不命中
WATCH-01  （catch-all）
```

例如 `clinical_value_exists=SATISFIED`、
`competitive_position_not_locked=UNSATISFIED`、
`plausible_buyer_partner_map=SATISFIED`、
`differentiation_visible_preclinical=UNKNOWN` 这样的组合，会先命中
`PARTNER-01 → PARTNER_ONLY`，**不是** WATCHLIST——`PARTNER-01` 的 `when` 子句
根本不检查 `differentiation_visible_preclinical`，它是不是 UNKNOWN 与这条
规则命中与否无关。**只有当八项标准都走到第 20 行之前的每一条 OUT／PARTNER
规则都不命中时**，`UNKNOWN` 才会以「使 `ACTIVE-01` 无法成立、又没有更早规则
拦截」的方式，落到 `WATCH-01` 这个 catch-all。把「看到 UNKNOWN 就判
WATCHLIST」当捷径，会把本该 `PARTNER_ONLY` 的 territory 错分。这是执行层面的
表述修正，不改 PR #79 冻结的规则表本身。

这是**预期行为**，不是 run failure。**得到 0 个 `ACTIVE_SEARCH` 是合法
结果。**

本计划的成功标准不是找到若干 active territory，而是证据是否真实支持得到的
分布——`20 个 territory → 0 ACTIVE / 8 WATCH / 5 PARTNER_ONLY / 7 OUT` 与
`20 个 territory → 3 ACTIVE / …` 同样合法，只要每一条路由结论都能在
`field_evidence_map.json` 里找到依据。

---

## 9. Sponsor advantage rule

每个 territory 必须生成**独立**的 `sponsor_evidence_advantage_ref`，不能直接
引用 `DevelopmentSponsorProfile` 作为 advantage 本身——这正是冻结 profile
v0.1.2 里 `asymmetric_evidence_advantage_semantics` 已经写死的边界，此处只是
在执行层面复用，不重新定义。

每条必须回答：**Stelligen 相对于一般公开信息使用者，在这个具体 territory 中
究竟能产生什么非平凡、可复现的 derived advantage？**

以下不得判定 `SATISFIED`：

- 会生信；
- 可以查 TCGA；
- 可以做 scRNA analysis。

当前没有公司控制的 patient samples/private models，因此不得隐式调用这些资源
（复用 `NOT_YET_CONTROLLED` 登记表的边界）。

---

## 10. Competition / window closure

对每个 territory 至少调查：approved competitors、Phase III、meaningful Phase
II、ADC programs、adjacent modality programs（能占据同一临床位置的
bispecific、small molecule、cell therapy、新 IO combination 等）。**竞争不是
只看 ADC。**

`window_closure_risk_ref` 必须结合：

- competitor stage；
- expected readout timing；
- possible regulatory timing；
- Stelligen 12–18 个月的证据生成 horizon（`DevelopmentSponsorProfile.time_horizon`）。

---

## 11. Deliverable directory

约定路径：`DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/`。

**已在起草本计划时验证**（不是在执行时才检查）：

```
路径: /Volumes/Stelligen_SSD/Stelligen/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result
存在: 是
可写: 是
```

执行时将新建：

```
wp2b_crc_territory_map_<UTC_TIMESTAMP>/
```

若届时该根路径不存在或不可写，将停止并报告实际 external workspace root，
不模拟一个看起来存在的路径。

---

## 12. Required deliverables

上一版把冻结的 required artifact 名称改写成了别的名字
（`opportunity_territory_map.json`／`territory_table.tsv`），并漏掉了
`run_report.md`／`verify_package.py`。`output.required_artifacts` 是
`wp2b_crc_territory_map_run.yaml` 已冻结的字段，本计划不得替换，只能追加。

**冻结必须（逐字取自契约，不改名）：**

- `territory_map.json`
- `territories.tsv`
- `search_space_admissions.json`
- `sponsor_evidence_advantage.json`
- `source_manifest.json`
- `run_report.md`
- `verify_package.py`

**本计划追加（不替换以上任何一项）：**

- `field_evidence_map.json`（第 13 节，强制——冻结契约没有单独要求它，但
  `VAL-T13`「每个非空字段有至少一条 source_ref」需要一个可审的映射文件才能
  被独立核验，否则审核者只能面对文献列表反推）
- `window_closure_risk.json`
- `run_manifest.json`（第 14 节；与冻结的 `source_manifest.json` 是两个不同
  文件，不要混淆）
- `reconciliation_report.md`（第 5 节 Pass B 的重叠说明与 excluded-enumeration
  记录，第 6.1 节 (a) 类字段无法确证时的候选 territory 也记在这里）

推荐：

- `territory_summary.md`
- `competition_readout_calendar.tsv`
- `unknowns_and_research_gaps.tsv`

---

## 13. Field-level provenance

`source_manifest.json` 只列来源不够。`field_evidence_map.json` 是**强制交付
物**，映射：

```
territory_id + field/criterion + claim + evidence_ref
```

使日后审核可以直接回答「为什么这个 territory 的
`competitive_position_not_locked = SATISFIED`」，而不必面对一堆文献列表反推。

---

## 14. Run manifest / reproducibility

`run_manifest.json` 至少记录：

- `run_id`
- `timestamp`
- `knowledge_cutoff`（`2026-08-07`）
- 契约版本：`OpportunityTerritory@0.1.0`／`OpportunityTerritoryMap@0.1.0`
  （PR #77）、`search_space_admission_route_policy@0.1.0`（PR #79）
- `DevelopmentSponsorProfile` 已批准版本与 content hash：
  `profile_version: "0.1.2"`、
  `approved_content_sha256: f910fc5e2b9c7743c4301ae4ac648ad44e67a22b591e5c266ff8a8995427fd9b`、
  `approved_instance_sha256: 41f8e02680a976cdf4db34cd18dbf0dfd7a566ed160230934c753d3e7241544a`
- source hierarchy（第 3 节表格）
- search queries or query log
- inclusion/exclusion rules
- actual territory count
- route counts（`ACTIVE_SEARCH`／`WATCHLIST`／`PARTNER_ONLY`／`OUT_OF_MANDATE`
  各多少）
- tool/environment identity（第 1.2 节工具清单，含实际使用哪些 connector）

**不要求** bit-for-bit reproducibility of web search。**要求** decision
reproducibility：后来的审核者能理解 territory 为什么存在、为什么被这样路由。

---

## 15. Stop and checkpoint policy

正式 run 一旦开始就是 `wp2b_crc_territory_map_run.yaml` 授权的**那一次**运行
（`authorises_run_count: 1`）。

**本计划本身不消费该授权，也不开始任何 territory 枚举。** 起草本计划期间没有、
也不会同时偷偷开始正式 enumeration。只有在人类负责人明确批准本计划之后，才会
真正执行并消费这一次授权。

---

## 16. Result PR（本计划只描述，不在本 PR 内执行任何一步）

正式 run 完成后，另开 result PR：

- 外部结果 package hash 固定；
- 运行 `VAL-T01`–`VAL-T21`；
- **仓库只记录 result binding／hashes／validation／reconciliation，不把
  territory content 放入 repo**；
- `authorises_run_count → 0`；
- `execution_status` 更新为反映「已执行、结果待审」的状态——当前契约里
  `execution_status` 是自由字符串，`tests/test_wp2b_crc_territory_map_run.py`
  目前只在 blocker 未清/已清两种情形下各断言一个值
  （`not_authorized_not_executed`／`authorised_not_yet_executed`）。执行后的
  第三种状态（例如 `executed_pending_result_review`）与相应测试断言由 result
  PR 自行引入，**本计划不在此提前修改契约或测试**；
- **不自动进入 WP3**——WP3 必须等待 territory result PR 被审核接受。

---

## 17. Validation procedure（本计划起草阶段即定义，执行后原样套用）

结果 PR 必须能重跑并通过以下检查（具体实现随 result PR 一起提交，此处冻结
检查项，不冻结实现）：

1. `territory_map.json` 中每个元素可按 `OpportunityTerritory@0.1.0` 构造成功
   （形状校验，同 profile 校验器模式）。
2. `VAL-T01`–`VAL-T21` 全部通过，逐条按 `wp2b_crc_territory_map_run.yaml`
   已冻结的规则文本核对（本计划不重新定义任何一条，也不改编号）。
3. `field_evidence_map.json` 覆盖 `territory_map.json` 中每个 territory 的
   每个非 `UNKNOWN` 字段/criterion。
4. 每条 `evidence_ref` 能对应到第 3 节冻结的七个 `tier_1_sources` 类别之一；
   `CONFERENCE_ONLY` 与 `company_public_disclosure` 来源显式标注；
   `available_*_refs` 字段引用的六个公开分子/患者资源（第 3 节已排除的
   TCGA/GEO/cBioPortal/GTEx/HPA/DepMap）不出现在这份 Tier 分类里。
5. `ACTIVE_SEARCH` 的每个 territory，八项 admission criteria 全部
   `SATISFIED`，且都有 evidence ref（复核 PR #79 的 `ACTIVE-01`，不重新判定）。
6. `sponsor_evidence_advantage_ref` 不直接等于 `DevelopmentSponsorProfile` 的
   `content_sha256` 或其字段值的字面复制——即不允许把 profile 本身当证据
   （`VAL-T19`）；任意两个 territory 不共用同一个该 ref（`VAL-T20`）。
7. `run_manifest.json` 的 `approved_instance_sha256`／`approved_content_sha256`
   与当前冻结 profile 一致。
8. `source_manifest.json` 中不出现任何 `tier_2_derived_databases_permitted:
   false` 覆盖的派生数据库（`VAL-T16`）——即 cBioPortal 及第 3 节列出的其余
   五个公开资源一律不得作为 Tier 分类下的正式来源出现。**不做机构关键词
   扫描**：`dfci`／`hospital`／`academic`／`institution`／`pdx` 这类字符串
   匹配是 `DevelopmentSponsorProfile` 校验器的规则，防的是「把机构资源写成
   公司资产」；本运行的证据层引用的是**公开发表的论文与试验记录**，一篇由
   DFCI 或某学术医院作者发表的公开论文、一项公开发表的 PDX 研究，都是完全
   合法的 Tier-1 primary evidence，不能因为字符串命中就判 fail。真正要防的是
   把 private／unpublished／institution-controlled 的资源（未发表数据集、
   机构私有队列、未公开的患者样本）当成 Stelligen-controlled evidence 来
   源——即复用第 1 节「不允许」清单里的边界，而不是对 citation 文本做
   关键词扫描。
9. **每个 territory 必须有一个可解析、非空的 `position_occupancy_ref`；
   `current_competitor_refs`／`leading_asset_refs`／`expected_readout_refs`
   为空列表不能免除这条要求。** 三个 list 字段的 `investigated_and_empty`
   标注只满足 `VAL-T14`，不满足 `position_occupancy_ref` 本身的非空约束——
   两者是独立检查，一个 territory 可以同时「无已知竞争者」且「occupancy ref
   存在、内部记 `UNRESOLVED`」。ref 缺失或为空必须在这一步就 FAIL，不能留到
   构造 `OpportunityTerritory@0.1.0` 时才因 `_require_external_ref` 报错。

---

## 18. Expected resource/time range

按第 1.1 节，授权单位是一个 `run_id`，可跨多个执行检查点，不强求单次会话内
完成。预计：

- Pass A 枚举 + Pass B 归并：约 1–2 小时等效工作量，可作第一个检查点。
- 每个 territory 第一轮广度调查（1–3 + 1–3 来源）：数十分钟级；可按若干
  territory 为一批设检查点。
- 进入 `ACTIVE_SEARCH` 候选的第二轮深度核验：视候选数量另计，每个数十分钟级。
- 无法给出 bit-for-bit 时间估计，因为检索路径依赖实际证据分布，且取决于
  `PubMed`／`Clinical Trials` connector 的 OAuth 是否已完成（第 1.2 节）。

---

## 19. 明确不做的事（重申，避免范围蔓延）

- 不修改 `OpportunityTerritory`／`OpportunityTerritoryMap` 契约形状；
- 不修改 `search_space_route_policy.yaml` 的任何规则或标准；
- 不修改 `DevelopmentSponsorProfile` 实例或其冻结状态；
- 不修改 `wp2b_crc_territory_map_run.yaml` 的授权字段（`authorises_run`／
  `authorises_run_count`／`blocked_by`）或 `source_policy`／
  `output.required_artifacts`／`validation_rules`；
- 不新开 source-admission PR 为 TCGA/GEO/cBioPortal/GTEx/HPA/DepMap 或任何
  guideline 网站单独裁定 Tier 归属（第 3 节的排除是复用冻结契约的现状，不是
  本计划的新裁定）；
- 不生成 target candidates 或 program wedges（WP3 范围）；
- 不复活旧的 369 target-pair 池；
- 不裁定 `EVGAP-01`／`EVGAP-02`／`GAP-P07`；
- 不把任何机构资源当作 Stelligen 资产。

---

## 20. 批准后的下一步

人类负责人批准本计划后：

1. 按第 1.1 节的检查点形态执行 territory 枚举（Pass A → Pass B → 分层调查 →
   路由），可跨检查点/续接会话，不强求单次会话内完成；
2. 产出第 12 节列出的全部必需交付物于第 11 节路径；
3. 生成 `run_manifest.json` 并计算整包 SHA-256；
4. 提交 result PR，仅含 hashes／校验结果／reconciliation 摘要，不含
   territory 内容本身；
5. 等待人类负责人与（若适用）ChatGPT 对 result PR 的审核结论。
