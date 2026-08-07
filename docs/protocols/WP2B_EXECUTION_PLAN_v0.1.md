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

本次由 Claude 在**当前会话**里直接执行，使用当前会话可访问的公开检索能力。不为
WP2B v0.1 另建自动化采集 pipeline——首要目标是建立一个高质量、可审计的 CRC
territory baseline，把 ontology、territory granularity、evidence depth 和路由
逻辑跑通，而不是提前工程化一个尚未稳定的方法。

### 1.1 当前会话的真实工具清单（如实记录，不夸大）

| 工具 | 状态 | 用途 |
|---|---|---|
| `WebSearch` | 可用，无需授权 | 发现型检索；美国地区限定 |
| `WebFetch` | 可用，无需授权 | 抓取公开 URL 并转 markdown 摘要；对非结构化页面（新闻、guideline 页、公司 IR 页）够用，对结构化字段（trial phase、enrollment、arm 设计）会有损 |
| `PubMed` MCP connector | **已安装但未授权**，需要用户在浏览器完成 OAuth | 结构化文献检索，比 `WebFetch` 抓 PubMed 网页更可靠 |
| `Clinical Trials` MCP connector | **已安装但未授权**，需要用户在浏览器完成 OAuth | 结构化试验数据（phase、状态、入组、readout）——对第 10 节的 competition/window-closure 调查价值最高 |
| `bioRxiv` MCP connector | **已安装但未授权**，需要用户在浏览器完成 OAuth | 预印本检索，仅用于 Tier 1C 之外的补充发现，不作为 primary evidence |

**建议**：在正式执行前，请授权 `Clinical Trials` 与 `PubMed` 两个 connector——
两者都用于第 3 节 Tier 1A／1B 的权威信息，结构化字段的可靠度明显高于
`WebFetch` 抓取同一个网页。`bioRxiv` 可选，不授权也不影响 Tier 1A/1B/1D/1E 的
调查完整性。若您不希望授权，我会退回 `WebSearch` + `WebFetch` 直接访问
`clinicaltrials.gov`／`pubmed.ncbi.nlm.nih.gov` 的公开页面，可行但结构化字段的
逐条可追溯性会弱于 connector。

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

## 3. Source hierarchy（本次冻结，供 `source_manifest.json` 与
`field_evidence_map.json` 引用）

| Tier | 来源 | 用途 | 置信度标注 |
|---|---|---|---|
| **1A** 监管／权威临床 | FDA、EMA、NCCN/ESMO/ASCO 公开可及 guideline、ClinicalTrials.gov、WHO ICTRP 或等效官方注册库 | current SOC、批准适应症、treatment line、trial stage、regulatory status | — |
| **1B** 同行评审临床/科学文献 | PubMed 索引原始论文、NEJM、Lancet／Lancet Oncology、JCO、Nature Medicine／Cancer Discovery／Cancer Cell 等 | clinical outcome、resistance population、molecular subtype、metastatic-state evidence、human biomarker evidence | — |
| **1C** 会议摘要（原始，未正式发表） | ASCO、AACR、ESMO、ASCO GI | 尚未发表但可能改变 competitive position／window closure 的项目 | **必须标注 `CONFERENCE_ONLY`，不得与完整同行评审证据混为同一 confidence** |
| **1D** Sponsor 一级披露 | 公司新闻稿、investor presentation、SEC filing | trial initiation、enrollment/status、topline result、licensing/acquisition、disclosed development strategy | **不得仅凭 sponsor claim 判定 clinical superiority** |
| **1E** 公开分子/患者资源 | TCGA、GEO、cBioPortal、GTEx、HPA、DepMap（均已在冻结 `DevelopmentSponsorProfile@0.1.2` 的 `accessible_data` 中列出） | data availability、territory 是否 computationally addressable、是否存在公开人体证据 | **公共数据库本身不得令 `asymmetric_evidence_advantage = SATISFIED`**——已是 profile v0.1.2 的硬不变量（`public_data_plus_generic_bioinformatics_is_insufficient`），此处只是复用，不重新定义 |
| Discovery-only | Google Scholar、PubMed related articles、综述 | 用于发现 primary source 的路径 | **不得作为关键 route criterion 的唯一证据**；最终 field-level evidence 必须尽量回到 primary/authoritative source |

`field_evidence_map.json` 中每条 `evidence_ref` 必须能对应到上表某个 Tier；
`CONFERENCE_ONLY` 与 sponsor-disclosure 来源的记录必须显式携带对应标注字段，
校验脚本会检查这一点（见第 17 节 `validate_field_evidence_map`）。

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

输出实际 territory count。**15–30 仅作 `VAL-T02` 的 reconciliation reference**
（`expected_active_band` 的处理方式，PR #78 已冻结），**不得为凑数 split/merge**。

---

## 6. 每个 territory 的最小调查深度

每个 territory 至少完成以下 18 项才能称为 investigated；任何一项缺资料**必须写
`UNKNOWN`，不能通过推测填满**。此列表与 `OpportunityTerritory@0.1.0` 的字段
逐一对应（右列括注对应的契约字段）：

| # | 调查项 | 对应契约字段 |
|---|---|---|
| 1 | Patient definition | `clinical_population_ref` |
| 2 | Current SOC | `current_soc_ref` |
| 3 | Main clinical failure/unmet need | `clinical_failure_mode_ref` |
| 4 | Approximate population relevance | `patient_size_band_ref` |
| 5 | Current leading competitors | `current_competitor_refs` |
| 6 | Highest development stage | `leading_asset_refs` |
| 7 | Important expected readouts | `expected_readout_refs` |
| 8 | Evidence that position is locked / not locked / unresolved | `position_occupancy_ref` |
| 9 | Public patient data availability | `available_patient_data_refs` |
| 10 | Public model availability | `available_model_refs` |
| 11 | Stelligen territory-specific evidence advantage hypothesis | `sponsor_evidence_advantage_ref` |
| 12 | Key uncertainty addressability | `search_space_admission_ref` → `key_uncertainty_addressable` |
| 13 | Preclinical differentiation visibility | `search_space_admission_ref` → `differentiation_visible_preclinical` |
| 14 | Preliminary defensible IP path | `search_space_admission_ref` → `defensible_ip_path` |
| 15 | Plausible buyer/partner class | `search_space_admission_ref` → `plausible_buyer_partner_map` |
| 16 | Window-closure risk | `window_closure_risk_ref` |
| 17 | 八项 `SearchSpaceAdmission` 标准，均带 evidence ref | `search_space_admission_ref` |
| 18 | 严格按冻结的 `search_space_route_policy.yaml`（PR #79）解出路由 | `search_space_admission_ref` → route |

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

只能提出合理假设而没有足够证据时：`UNKNOWN → WATCHLIST`。这是**预期行为**，
不是 run failure。**得到 0 个 `ACTIVE_SEARCH` 是合法结果。**

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

必须：

- `opportunity_territory_map.json`
- `territory_table.tsv`
- `search_space_admissions.json`
- `source_manifest.json`
- `field_evidence_map.json`
- `sponsor_evidence_advantage.json`
- `window_closure_risk.json`
- `reconciliation_report.md`
- `validation_report.md`
- `run_manifest.json`

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
- tool/environment identity（第 1.1 节工具清单，含实际使用哪些 connector）

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

1. `opportunity_territory_map.json` 中每个元素可按
   `OpportunityTerritory@0.1.0` 构造成功（形状校验，同 profile 校验器模式）。
2. `VAL-T01`–`VAL-T21` 全部通过（`wp2b_crc_territory_map_run.yaml` 已冻结的
   校验规则，本计划不重新定义）。
3. `field_evidence_map.json` 覆盖 `opportunity_territory_map.json` 中每个
   territory 的每个非 `UNKNOWN` 字段/criterion。
4. 每条 `evidence_ref` 能对应到第 3 节 Source hierarchy 的某个 Tier；
   `CONFERENCE_ONLY` 与 sponsor-disclosure 来源显式标注。
5. `ACTIVE_SEARCH` 的每个 territory，八项 admission criteria 全部
   `SATISFIED`，且都有 evidence ref（复核 PR #79 的 `ACTIVE-01`，不重新判定）。
6. `sponsor_evidence_advantage_ref` 不直接等于 `DevelopmentSponsorProfile` 的
   `content_sha256` 或其字段值的字面复制——即不允许把 profile 本身当证据。
7. `run_manifest.json` 的 `approved_instance_sha256`／`approved_content_sha256`
   与当前冻结 profile 一致。
8. `source_manifest.json` 中不出现 `dfci`／`hospital`／`academic`／
   `institution`／`pdx` 关键词（复用 `validate_profile.py` 的机构关键词扫描
   逻辑，应用对象是本次运行产物而非 profile）。

---

## 18. Expected resource/time range

单次会话内完成，预计：

- Pass A 枚举 + Pass B 归并：约 1–2 小时等效工作量。
- 每个 territory 第一轮广度调查（1–3 + 1–3 来源）：数十分钟级。
- 进入 `ACTIVE_SEARCH` 候选的第二轮深度核验：视候选数量另计，每个数十分钟级。
- 无法给出 bit-for-bit 时间估计，因为检索路径依赖实际证据分布，且取决于是否
  授权 `ClinicalTrials`／`PubMed` connector（第 1.1 节）。

---

## 19. 明确不做的事（重申，避免范围蔓延）

- 不修改 `OpportunityTerritory`／`OpportunityTerritoryMap` 契约形状；
- 不修改 `search_space_route_policy.yaml` 的任何规则或标准；
- 不修改 `DevelopmentSponsorProfile` 实例或其冻结状态；
- 不修改 `wp2b_crc_territory_map_run.yaml` 的授权字段（`authorises_run`／
  `authorises_run_count`／`blocked_by`）；
- 不生成 target candidates 或 program wedges（WP3 范围）；
- 不复活旧的 369 target-pair 池；
- 不裁定 `EVGAP-01`／`EVGAP-02`／`GAP-P07`；
- 不把任何机构资源当作 Stelligen 资产。

---

## 20. 批准后的下一步

人类负责人批准本计划后：

1. 直接在当前会话执行 territory 枚举（Pass A → Pass B → 分层调查 → 路由）；
2. 产出第 12 节列出的全部必需交付物于第 11 节路径；
3. 生成 `run_manifest.json` 并计算整包 SHA-256；
4. 提交 result PR，仅含 hashes／校验结果／reconciliation 摘要，不含
   territory 内容本身；
5. 等待人类负责人与（若适用）ChatGPT 对 result PR 的审核结论。
