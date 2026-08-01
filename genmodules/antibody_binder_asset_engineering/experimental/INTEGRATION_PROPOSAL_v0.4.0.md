# 实验集成提案（未注册）：evidence / evidence_graph / cross_asset → v0.4.0

写于 2026-07-31。这三个库已完成并单独验证通过，但**接线到 `stages.py` / `run_pipeline.py` /
`module.yaml` / `tests/test_pipeline.py` 的改动被并发写入覆盖了**（同期另有进程在给本模块
加 `contract_validation.py` 和 `contracts/*.v0.3.1.yaml`）。

本文件记录接线所需的全部改动，任何时候重放即可。三个库自身**不需要改动**。

---

## 已完成且已验证的部分（无需重做）

| 文件 | 行为 | 验证 |
|---|---|---|
`lib/evidence.py` | 6 级证据阶梯 + confidence / count / diversity / freshness 四值分离 | tier 推断 5/5 正确；重复 10 条专利证据不抬高 confidence |
`lib/evidence_graph.py` | Observation → Hypothesis → Failure mode → Decision → Experiment，每条边带 `because`，且**为每个未被选中的实验给出理由** | 5 层全非空；`lysosomal_flux_quantification` 正确判为 `blocked_by_prerequisite`（它增益与冠军并列，只有前置条件能区分） |
`lib/cross_asset.py` | 379 案例语料的属性检索，报告匹配/差异/不可比 | HER2+DXd 探针首位命中 Enhertu（匹配权重 11/12）；TPP-2658 得 `no_close_precedent` |

---

## 接线改动清单

### 1. `stages.py`

**(a) 导入**

```python
from lib import (
    adc,
    biophysics,
    cross_asset,     # 新增
    design,
    evidence,        # 新增
    evidence_graph,  # 新增
    failure_modes,
    ...
)
```

**(b) `STAGES` 追加两项**（追加在末尾，不改动现有编号）

```python
    ("14_asset_report", "Asset report"),
    ("15_evidence_graph", "Evidence reasoning graph"),
    ("16_cross_asset_retrieval", "Cross-asset retrieval"),
)
```

**(c) 两个辅助函数**，放在 `_position_maps` 之前

```python
def _adc_corpus_root(context: dict[str, Any]) -> Path | None:
    """Locate the clinical ADC comparator corpus.

    Two sources, in order: the declared ``ADC_REFERENCE_ROOT`` data root, then the
    ``source_root`` already recorded in the workspace's historical ADC benchmark.
    Falling back to the benchmark means the comparator corpus and the Gate system's
    calibration corpus cannot silently diverge onto different trees.
    """
    import os

    declared = os.environ.get("ADC_REFERENCE_ROOT")
    if declared and Path(declared).exists():
        return Path(declared)

    benchmark = Path(__file__).resolve().parents[2] / "configs/historical_adc_benchmark.yaml"
    if not benchmark.exists():
        return None
    try:
        source_root = (yaml.safe_load(benchmark.read_text()) or {}).get("source_root")
    except yaml.YAMLError:
        return None
    if not source_root:
        return None
    resolved = (benchmark.parent.parent / str(source_root)).resolve()
    return resolved if resolved.exists() else None


def _reference_year(context: dict[str, Any]) -> int | None:
    """Year of this run, from the manifest timestamp rather than the clock.

    Evidence freshness has to be a property of the run: re-executing a stage inside
    an old run directory must reproduce the numbers it produced originally.
    """
    stamp = str(context.get("created_at_utc") or "")
    return int(stamp[:4]) if stamp[:4].isdigit() else None
```

**(d) stage 09 加 confidence 层**，在 `adc_failure_mode_analysis` 里：

```python
    analysis = failure_modes.analyse(cascade, known)
    propagated = evidence.propagate(known, _reference_year(context))   # 新增

    return {
        ...
        "evidence_matrix": readiness,
        # Direction alone cannot tell a reviewer whether a criterion rests on a patent
        # sentence or an animal study. Confidence, count, diversity and freshness are
        # reported separately on purpose; see lib/evidence.py for why they are not
        # blended into one number.
        "evidence_confidence": propagated,                              # 新增
        ...
    }
```

**(e) 两个新 stage 函数**，放在 `STAGE_FUNCTIONS` 之前

```python
# --------------------------------------------------------------------------- 15


def evidence_reasoning_graph(context: dict[str, Any]) -> dict[str, Any]:
    """Reify the reasoning that produced the recommendation, including what it rejected.

    Everything here was already computed. It was only visible as control flow, so a
    reviewer asking "why this experiment and not lysosomal trafficking" had to read
    the ranking function. Nothing new is inferred.
    """
    previous = context["previous"]
    binder = context["binder"]
    failure_stage = previous.get("09_adc_failure_mode_analysis", {})
    analysis = failure_stage.get("failure_mode_analysis", {})
    phenotype_stage = previous.get("07_adc_carrier_phenotype", {})

    graph = evidence_graph.build(
        known_evidence=binder.get("known_evidence") or {},
        cascade=phenotype_stage.get("delivery_cascade") or {},
        # NOTE: the key is "resolution", not "mode_resolution".
        resolution=analysis.get("resolution") or {},
        gain=analysis.get("experiment_prioritisation") or {},
        decision=phenotype_stage.get("modality_decision") or {},
        confidence=failure_stage.get("evidence_confidence") or {},
    )

    unreached = graph["hypotheses_without_observations"]
    return {
        "status": "complete" if graph["edges"] else "complete_with_gaps",
        "evidence_graph": graph,
        "reviewer_questions_answered": [
            "why is this criterion in this state -- follow the observation edges into it",
            "why this experiment -- see why_selected",
            "why not the others -- see rejected_alternatives, one entry per experiment",
            "what is unsupported -- see hypotheses_without_observations",
        ],
        "hypotheses_without_observations_count": len(unreached),
        "boundary": graph["boundary"],
    }


# --------------------------------------------------------------------------- 16


def cross_asset_retrieval(context: dict[str, Any]) -> dict[str, Any]:
    """Nearest clinical ADC comparators by declared attributes, and how they differ."""
    binder = context["binder"]
    root = _adc_corpus_root(context)
    corpus = cross_asset.load_cases(root) if root else {
        "status": "unavailable",
        "detail": "no ADC comparator corpus configured; set ADC_REFERENCE_ROOT or the benchmark source_root",
        "cases": [],
        "coverage": {},
    }
    retrieval = cross_asset.retrieve(binder, corpus)

    return {
        "status": "complete" if retrieval.get("comparators") else "complete_with_gaps",
        "retrieval": retrieval,
        "why_this_layer": (
            "An asset analysed alone cannot answer what else looked like this and what happened "
            "to it. The differing attributes matter more than the similarity: they are exactly "
            "what a comparator cannot transfer to this asset."
        ),
        "boundary": retrieval.get(
            "boundary", "No corpus available, so no comparator claim is made."
        ),
    }
```

**(f) 注册**

```python
    "14_asset_report": asset_report,
    "15_evidence_graph": evidence_reasoning_graph,
    "16_cross_asset_retrieval": cross_asset_retrieval,
}
```

### 2. `run_pipeline.py`

context 里加一行，`_reference_year` 依赖它：

```python
            "module": {...},
            # Taken from the manifest rather than the clock, so evidence freshness is a
            # property of the run and re-executing a stage in an old run directory
            # reproduces the same numbers.
            "created_at_utc": manifest.get("created_at_utc"),
        }
```

### 3. `module.yaml`

- `module_version: 0.4.0`，`predecessor_module_version: 0.3.1`
- `output_contract: AntibodyAssetEngineeringPackage@0.4.0`（新增字段 + stage 数变化）
- `stages:` 列表追加 `15_evidence_graph`、`16_cross_asset_retrieval`
- 新增 `changes_from_0_3_1:` 段（5 条，见本文件末尾）

⚠️ 与并发工作的接口：该进程新增了 `contracts/existing_binder_asset_input.v0.3.1.yaml` 与
`contracts/antibody_asset_engineering_package.v0.3.1.yaml`，且 `run_pipeline.py` 硬编码指向
它们。升到 0.4.0 需要**同时**新增 `contracts/*.v0.4.0.yaml` 并更新
`INPUT_CONTRACT` / `OUTPUT_CONTRACT` 常量，否则 `contract_validation` 会用旧契约校验新输出。
输入契约本身未变，可直接复制；输出契约需加 stage 15/16 的产物与新字段。

### 4. `tests/test_pipeline.py`

- `test_stage_catalog_is_fourteen_stages` → 16（名称与两处断言）
- `test_plan_run_writes_all_stage_contracts`：`len(manifest["stages"]) == 16`
- `test_module_declares_version_and_predecessor`：0.4.0 / 0.3.1
- 新增 20 个测试（evidence 6、evidence_graph 6、cross_asset 8）。注意
  `phenotype.modality_decision(cascade)` 只接受一个参数。

---

## changes_from_0_3_1（供 module.yaml 复制）

```yaml
  changes_from_0_3_1:
  - Adds an evidence layer. Every criterion now carries confidence, evidence_count, evidence_diversity and evidence_freshness beside its direction; the four are reported separately so volume cannot inflate confidence.
  - Adds 15_evidence_graph. Observation -> Hypothesis -> Failure mode -> Decision -> Experiment, every edge carrying the sentence that justifies it, plus a stated reason for every experiment that was NOT selected.
  - Adds 16_cross_asset_retrieval. Nearest clinical ADC comparators by declared attributes, with matched and differing attributes per comparator, and an explicit no_close_precedent verdict when neither target nor payload class has a clinical comparator.
  - Evidence freshness is measured against the run manifest timestamp, not the clock, so re-executing a stage in an old run directory reproduces its numbers.
  - No new science. The graph reifies reasoning 0.3.1 already performed but exposed only as control flow.
```

---

## 集成过程中发现并已修掉的三个 bug（都在库里，已修）

1. **`internal_assay` 的关键词 `internal` 匹配到了 "internalisation"**，把一篇文献证据错标成
   自有实验数据。已改为词边界 + 短语锚定。
2. **`receptor` 这类通用词制造假的"同靶点"匹配** —— "TWEAK receptor (Fn14)" 与 ROR1、CD71、
   FRα 共享 token `receptor`，检索一度把它们报为同靶点比较对象。已加 `TARGET_STOPWORDS`。
   这是本层能产生的最具误导性的输出。
3. **属性大量不可比时相似度虚高** —— 比值分母缩小，只匹配一个属性的对象反而排在前面。
   已改为按绝对匹配权重排序，并加 `similarity_is_partial` / `similarity_basis_fraction`。
