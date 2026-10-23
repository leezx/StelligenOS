"""Synthetic B2 regression for unbound MOD-TGT07@2.0.0.

The v1 scientific core is exercised under v2 identity while frozen v1 tests
remain independent. No external data or canonical assessment is involved.
"""

from __future__ import annotations

import ast
import dataclasses
import itertools
import unittest
from pathlib import Path

import yaml

from src.objects.decision_model import EvidencePackage

from gate_modules.tgt07_shedding_soluble_antigen_sink_liability_v2 import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    TGT07_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    FatalReviewRecord,
    NormalizedSolubleAntigenObservation,
    SolubleAntigenEvidenceCompletion,
    SolubleAntigenUnresolvedItem,
    Tgt07ModuleInput,
    Tgt07ModuleRunResult,
    run,
    sink_materiality_direction,
)
from gate_modules.tgt07_shedding_soluble_antigen_sink_liability_v2.classify import (
    classify_observation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt07_shedding_soluble_antigen_sink_liability_v2"

TARGET_A = "TARGET_A"
CONTEXT_KEY = "ctxkey-crc-refractory"
AS_OF = "2026-09-01"
SCOPE = "public soluble-antigen scope v1"
SINKCTX_A = "adc-format-x / dose-y / affinity-z / crc-refractory"
SINKCTX_B = "same-target-analogue / dose-w"

_OBS = itertools.count(1)


# --- fakes -----------------------------------------------------------------

class Alloc:
    def __init__(self) -> None:
        self.calls = 0

    def next_evidence_id(self) -> str:
        self.calls += 1
        return f"EP-{self.calls:08d}"


class SrcRes:
    def __init__(self, records, *, unresolved=frozenset(), mismatch=frozenset()) -> None:
        self._records = records
        self._unresolved = set(unresolved)
        self._mismatch = set(mismatch)
        self.calls = 0

    def resolve(self, source_id):
        self.calls += 1
        if source_id in self._unresolved:
            return None
        rec = self._records.get(source_id)
        if rec is None:
            return None
        if source_id in self._mismatch:
            return CanonicalSourceRecord(
                source_id=rec.source_id,
                source_type=rec.source_type,
                source_identifier=rec.source_identifier + "-DRIFT",
                locator=rec.locator,
            )
        return rec


class Lib:
    def __init__(self, packages=None) -> None:
        self._packages = packages or {}

    def resolve(self, observation_id):
        return self._packages.get(observation_id)


def _src(source_id="SRC-00000001"):
    return CanonicalSourceRecord(source_id, "PMID", f"PMID:{source_id[-4:]}", "loc")


# --- observation factory --------------------------------------------------

def _obs(**kw) -> NormalizedSolubleAntigenObservation:
    n = next(_OBS)
    base = dict(
        observation_id=f"OBS-{n:04d}",
        target_identity=TARGET_A,
        program_id="PROG-SYNTHETIC",
        construct_id="",
        dose_exposure_basis="",
        soluble_concentration_basis="",
        turnover_basis="",
        affinity_basis="",
        assay_unit="",
        detection_limit_basis="",
        detection_limit_value=None,
        detection_limit_unit="",
        assay_analyte="",
        quantitative_input_source_id="",
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind="SHEDDASE_SUBSTRATE_STATUS",
        analysis_method="",
        circulating_soluble_target_status="",
        circulating_soluble_target_basis="",
        cohort_class="",
        cohort_class_basis="",
        sink_materiality_outcome="NOT_ESTABLISHED",
        sink_materiality_outcome_basis="",
        analysis_validation_status="NOT_ESTABLISHED",
        analysis_validation_basis="",
        tmdd_input_adequacy_status="NOT_ESTABLISHED",
        tmdd_input_adequacy_basis="",
        same_target_therapeutic_match_status="NOT_ESTABLISHED",
        same_target_therapeutic_match_basis="",
        same_target_therapeutic_ref="",
        soluble_antigen_attribution_status="NOT_ESTABLISHED",
        soluble_antigen_attribution_basis="",
        exposure_scenario_class="",
        exposure_scenario_basis="",
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        sink_exposure_context_id="",
        sink_exposure_context_basis="",
        claim=f"claim {n}",
        source_id="SRC-00000001",
        source_type="PMID",
        source_identifier="PMID:0001",
        locator="loc",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
    )
    base.update(kw)
    return NormalizedSolubleAntigenObservation(**base)


def _sheddase(**kw):
    kw.setdefault("observation_kind", "SHEDDASE_SUBSTRATE_STATUS")
    return _obs(**kw)


def _secreted(**kw):
    kw.setdefault("observation_kind", "SECRETED_ISOFORM")
    return _obs(**kw)


def _quant(status="QUANTIFIED_PRESENT", cohort="CRC_PATIENT_SERUM", **kw):
    kw.setdefault("observation_kind", "SOLUBLE_ANTIGEN_QUANTITATION")
    kw.setdefault("circulating_soluble_target_status", status)
    kw.setdefault("circulating_soluble_target_basis", "measured serum level")
    kw.setdefault("cohort_class", cohort)
    kw.setdefault("cohort_class_basis", "cohort described")
    kw.setdefault("assay_unit", "ng/mL")
    kw.setdefault("detection_limit_basis", "source assay LoD and LoQ")
    kw.setdefault("detection_limit_value", 0.1)
    kw.setdefault("detection_limit_unit", "ng/mL")
    kw.setdefault("assay_analyte", TARGET_A)
    kw.setdefault("quantitative_input_source_id", "SRC-00000001")
    return _obs(**kw)


def _weak(kind="PREDICTED_CLEAVAGE_SITE_INFERENCE", **kw):
    kw.setdefault("observation_kind", kind)
    return _obs(**kw)


def _clinical(
    outcome="MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE",
    *,
    match=True,
    attribution=True,
    validation=True,
    ctx=SINKCTX_A,
    **kw,
):
    kw.setdefault("observation_kind", "CLINICAL_ANTIGEN_SINK_PK_EFFECT")
    kw.setdefault("analysis_method", "population PK with antigen-sink term")
    kw.setdefault("sink_materiality_outcome", outcome)
    if outcome != "NOT_ESTABLISHED":
        kw.setdefault("sink_materiality_outcome_basis", "outcome stated by source")
    if match:
        kw.setdefault("same_target_therapeutic_match_status", "QUALIFIED")
        kw.setdefault("same_target_therapeutic_match_basis", "same target, matched")
        kw.setdefault("same_target_therapeutic_ref", "NCT00000001")
    if attribution:
        kw.setdefault("soluble_antigen_attribution_status", "QUALIFIED")
        kw.setdefault("soluble_antigen_attribution_basis", "sink attributed to soluble antigen")
    if validation:
        kw.setdefault("analysis_validation_status", "QUALIFIED")
        kw.setdefault("analysis_validation_basis", "analysis validated")
    if ctx:
        kw.setdefault("sink_exposure_context_id", ctx)
        kw.setdefault("sink_exposure_context_basis", "format x dose x affinity x cohort")
    return _obs(**kw)


def _tmdd(
    outcome="MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE",
    *,
    scenario="INTENDED_ADC_EXPOSURE",
    tmdd_ok=True,
    validation=True,
    ctx=SINKCTX_A,
    **kw,
):
    kw.setdefault("observation_kind", "SOLUBLE_ANTIGEN_TMDD_ANALYSIS")
    kw.setdefault("construct_id", "ADC-SYNTHETIC")
    kw.setdefault("dose_exposure_basis", "dose and exposure curve documented")
    kw.setdefault("soluble_concentration_basis", "measured concentration input")
    kw.setdefault("turnover_basis", "measured turnover input")
    kw.setdefault("affinity_basis", "measured affinity input")
    kw.setdefault("assay_unit", "ng/mL")
    kw.setdefault("detection_limit_basis", "source states validated LoD")
    kw.setdefault("detection_limit_value", 0.1)
    kw.setdefault("detection_limit_unit", "ng/mL")
    kw.setdefault("assay_analyte", TARGET_A)
    kw.setdefault("quantitative_input_source_id", "SRC-00000001")
    kw.setdefault("analysis_method", "TMDD model with soluble-antigen compartment")
    kw.setdefault("sink_materiality_outcome", outcome)
    if outcome != "NOT_ESTABLISHED":
        kw.setdefault("sink_materiality_outcome_basis", "outcome stated by analysis")
    if scenario:
        kw.setdefault("exposure_scenario_class", scenario)
        kw.setdefault("exposure_scenario_basis", "scenario described")
    if tmdd_ok:
        kw.setdefault("tmdd_input_adequacy_status", "QUALIFIED")
        kw.setdefault("tmdd_input_adequacy_basis", "conc / turnover / affinity / dose all handled")
    if validation:
        kw.setdefault("analysis_validation_status", "QUALIFIED")
        kw.setdefault("analysis_validation_basis", "analysis validated")
    if ctx:
        kw.setdefault("sink_exposure_context_id", ctx)
        kw.setdefault("sink_exposure_context_basis", "intended ADC exposure scenario")
    return _obs(**kw)


def _audit_obs(comp, *, observation_id=None, **kw):
    kw.setdefault("observation_kind", "SEARCH_COMPLETION_AUDIT")
    kw.setdefault("analysis_method", "SEARCH_AUDIT")
    kw.setdefault("claim", "search completion audit")
    o = _obs(
        observation_id=observation_id or f"OBS-AUDIT-{next(_OBS):04d}",
        audit_search_scope=comp.search_scope,
        audit_sources_searched=comp.sources_searched,
        audit_landscape_as_of=comp.landscape_as_of,
        audit_public_soluble_antigen_search_complete=comp.public_soluble_antigen_search_complete,
        audit_soluble_antigen_quantitation_search_complete=comp.soluble_antigen_quantitation_search_complete,
        audit_crc_patient_quantitation_subspace_search_complete=comp.crc_patient_quantitation_subspace_search_complete,
        audit_healthy_donor_quantitation_subspace_search_complete=comp.healthy_donor_quantitation_subspace_search_complete,
        audit_sheddase_processing_search_complete=comp.sheddase_processing_search_complete,
        audit_secreted_isoform_search_complete=comp.secreted_isoform_search_complete,
        audit_same_target_pk_pd_or_tmdd_search_complete=comp.same_target_pk_pd_or_tmdd_search_complete,
        audit_unresolved_item_keys=tuple(i.snapshot_key for i in comp.unresolved_items),
        audit_qualifying_direct_evidence_context_ids=comp.qualifying_direct_evidence_context_ids,
        **kw,
    )
    return o


def _completion(
    *,
    attempted=True,
    complete=True,
    unresolved=(),
    qualifying_ctx=(),
    audit_observation_id="OBS-AUDIT-1",
    quant_complete=None,
    crc_sub=None,
    healthy_sub=None,
) -> SolubleAntigenEvidenceCompletion:
    if not attempted:
        return SolubleAntigenEvidenceCompletion(
            attempted=False,
            landscape_as_of=AS_OF,
            search_scope="",
            sources_searched=(),
            public_soluble_antigen_search_complete=False,
            soluble_antigen_quantitation_search_complete=False,
            crc_patient_quantitation_subspace_search_complete=False,
            healthy_donor_quantitation_subspace_search_complete=False,
            sheddase_processing_search_complete=False,
            secreted_isoform_search_complete=False,
            same_target_pk_pd_or_tmdd_search_complete=False,
            unresolved_items=tuple(unresolved),
            qualifying_direct_evidence_context_ids=(),
            audit_observation_id="",
        )
    crc = complete if crc_sub is None else crc_sub
    healthy = complete if healthy_sub is None else healthy_sub
    quant = (crc and healthy) if quant_complete is None else quant_complete
    return SolubleAntigenEvidenceCompletion(
        attempted=True,
        landscape_as_of=AS_OF,
        search_scope=SCOPE,
        sources_searched=("db1", "db2"),
        public_soluble_antigen_search_complete=complete,
        soluble_antigen_quantitation_search_complete=quant,
        crc_patient_quantitation_subspace_search_complete=crc,
        healthy_donor_quantitation_subspace_search_complete=healthy,
        sheddase_processing_search_complete=complete,
        secreted_isoform_search_complete=complete,
        same_target_pk_pd_or_tmdd_search_complete=complete,
        unresolved_items=tuple(unresolved),
        qualifying_direct_evidence_context_ids=tuple(qualifying_ctx),
        audit_observation_id=audit_observation_id,
    )


class Prov:
    def __init__(self, observations, completion):
        self._observations = list(observations)
        self._completion = completion

    def fetch_observations(self, **kw):
        return list(self._observations)

    def soluble_antigen_completion(self, **kw):
        return self._completion


def _input(**kw) -> Tgt07ModuleInput:
    base = dict(
        candidate_id="CAND-L04-000001",
        candidate_name="Candidate A",
        target_identity=TARGET_A,
        program_id="PROG-SYNTHETIC",
        intended_adc_construct_id="ADC-SYNTHETIC",
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v2",
        context_id="CTX-CRC-REFRACTORY-MCRC",
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="2.0",
        gate_id="TGT-07",
        gate_version="2.0",
        evidence_regime="PUBLIC_PLUS_EXPERIMENTAL",
        run_id="run-e16-1",
        code_commit="deadbeef",
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        soluble_antigen_search_scope=SCOPE,
    )
    base.update(kw)
    return Tgt07ModuleInput(**base)


def _run(
    observations,
    completion=None,
    *,
    records=None,
    unresolved=frozenset(),
    mismatch=frozenset(),
    library=None,
    module_input=None,
):
    completion = completion if completion is not None else _completion()
    records = records or {"SRC-00000001": _src()}
    alloc = Alloc()
    srcres = SrcRes(records, unresolved=unresolved, mismatch=mismatch)
    lib = library or Lib()
    res = run(
        module_input or _input(),
        provider=Prov(observations, completion),
        evidence_id_allocator=alloc,
        source_resolver=srcres,
        evidence_library=lib,
    )
    return res, alloc, srcres


def _std_landscape(*observations, qualifying_ctx=(), unresolved=()):
    """A completed audited landscape: the given observations + a matching audit."""

    comp = _completion(
        qualifying_ctx=qualifying_ctx,
        unresolved=unresolved,
        audit_observation_id="OBS-AUDIT-STD",
    )
    audit = _audit_obs(comp, observation_id="OBS-AUDIT-STD")
    return list(observations) + [audit], comp


# =====================================================================
# 1. binding + boundary + migration closeout
# =====================================================================

class BindingAndBoundaryTests(unittest.TestCase):
    def test_evidence_regime_matches_frozen_v2_instantiation(self):
        gs = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset_v2.yaml").read_text()
        )
        self.assertEqual(_input().evidence_regime,
                         gs["instantiation"]["evidence_regime"])
    def test_v2_module_is_unbound(self):
        gs = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset_v2.yaml").read_text()
        )
        by_gate = {b["gate_id"]: b["primary_module_version"]
                   for b in gs["context_specific_bindings"]["gate_bindings"]}
        self.assertEqual(by_gate["TGT-07"], "0.0.0")
        manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.assertEqual(manifest["module_version"], "2.0.0")
        self.assertEqual(manifest["status"], "BUILT_UNBOUND")

    def test_package_has_the_eleven_expected_files(self):
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((PKG / f).is_file(), f)

    def test_no_normalizer_and_no_generic_framework_file(self):
        names = {p.name for p in PKG.iterdir()}
        self.assertNotIn("normalizer.py", names)
        self.assertNotIn("framework.py", names)
        self.assertNotIn("base.py", names)

    def test_run_is_pure_no_forbidden_imports(self):
        forbidden = {"requests", "httpx", "urllib", "socket", "subprocess", "sqlite3"}
        for py in PKG.glob("*.py"):
            tree = ast.parse(py.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        self.assertNotIn(a.name.split(".")[0], forbidden, py.name)
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], forbidden, py.name)

    def test_src_does_not_import_gate_modules(self):
        for py in (REPO_ROOT / "src").rglob("*.py"):
            text = py.read_text()
            self.assertNotIn("import gate_modules", text, str(py))
            self.assertNotIn("from gate_modules", text, str(py))


# =====================================================================
# 2. classify -- T1 kind-specific DIRECT authority
# =====================================================================

class ClassifyClinicalDirectTests(unittest.TestCase):
    def _c(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_clinical_material_sink_with_all_qualifiers_is_direct_supports(self):
        c = self._c(_clinical())
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_material_sink)
        self.assertEqual(c.sink_liability_implication, "SUPPORTS_SINK_LIABILITY")

    def test_clinical_material_sink_without_established_compromise_is_direct_supports(self):
        c = self._c(_clinical(outcome="MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_material_sink)

    def test_clinical_material_sink_with_match_not_established_is_not_direct(self):
        c = self._c(_clinical(match=False))
        self.assertEqual(c.evidence_rung, "")
        self.assertFalse(c.is_qualifying_direct)

    def test_clinical_material_sink_with_attribution_not_established_is_not_direct(self):
        c = self._c(_clinical(attribution=False))
        self.assertFalse(c.is_qualifying_direct)

    def test_clinical_material_sink_with_analysis_validation_not_established_is_not_direct(self):
        c = self._c(_clinical(validation=False))
        self.assertFalse(c.is_qualifying_direct)

    def test_clinical_mixed_with_all_qualifiers_is_direct_contextual(self):
        c = self._c(_clinical(outcome="MIXED_OR_UNRESOLVED"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_mixed)
        self.assertEqual(c.sink_liability_implication, "CONTEXTUAL")

    def test_clinical_no_material_sink_is_never_a_canonical_direct_negative(self):
        c = self._c(_clinical(outcome="NO_MATERIAL_SOLUBLE_SINK"))
        self.assertEqual(c.evidence_rung, "")
        self.assertFalse(c.is_qualifying_direct)

    def test_clinical_not_established_outcome_is_not_direct(self):
        c = self._c(_clinical(outcome="NOT_ESTABLISHED"))
        self.assertFalse(c.is_qualifying_direct)

    def test_clinical_missing_sink_exposure_context_is_not_direct(self):
        c = self._c(_clinical(ctx=None))
        self.assertFalse(c.is_qualifying_direct)


class ClassifyTmddDirectTests(unittest.TestCase):
    def _c(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_material_tmdd_with_input_adequacy_not_established_is_not_direct(self):
        c = self._c(_tmdd(tmdd_ok=False))
        self.assertFalse(c.is_qualifying_direct)

    def test_material_tmdd_qualified_is_direct_supports(self):
        c = self._c(_tmdd())
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_material_sink)

    def test_no_material_intended_exposure_qualified_is_direct_opposes(self):
        c = self._c(_tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_no_material_sink)
        self.assertEqual(c.sink_liability_implication, "OPPOSES_SINK_LIABILITY")

    def test_no_material_analogue_scenario_is_contextual_not_direct_negative(self):
        c = self._c(_tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", scenario="SAME_TARGET_THERAPEUTIC_ANALOGUE"))
        self.assertEqual(c.evidence_rung, "")
        self.assertFalse(c.is_qualifying_direct)

    def test_mixed_tmdd_qualified_is_direct_contextual(self):
        c = self._c(_tmdd(outcome="MIXED_OR_UNRESOLVED"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_mixed)

    def test_not_established_tmdd_outcome_is_not_direct(self):
        c = self._c(_tmdd(outcome="NOT_ESTABLISHED"))
        self.assertFalse(c.is_qualifying_direct)


class ClassifyIndirectAndWeakTests(unittest.TestCase):
    def _c(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_crc_patient_quantified_present_is_indirect_strong(self):
        c = self._c(_quant())
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_indirect)

    def test_crc_patient_below_lod_is_contextual(self):
        c = self._c(_quant(status="BELOW_DETECTION_OR_QUANTITATION_LIMIT"))
        self.assertEqual(c.evidence_rung, "")
        self.assertFalse(c.is_qualifying)

    def test_healthy_donor_quantified_present_is_contextual(self):
        c = self._c(_quant(cohort="HEALTHY_DONOR_SERUM"))
        self.assertEqual(c.evidence_rung, "")
        self.assertFalse(c.is_qualifying)

    def test_sheddase_substrate_status_is_indirect_strong(self):
        c = self._c(_sheddase())
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_indirect)

    def test_secreted_isoform_is_indirect_strong(self):
        c = self._c(_secreted())
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")

    def test_predicted_cleavage_site_is_weak(self):
        c = self._c(_weak("PREDICTED_CLEAVAGE_SITE_INFERENCE"))
        self.assertEqual(c.evidence_rung, "WEAK")
        self.assertFalse(c.is_qualifying)

    def test_family_analogy_is_weak(self):
        c = self._c(_weak("FAMILY_ANALOGY_SHEDDING_INFERENCE"))
        self.assertEqual(c.evidence_rung, "WEAK")

    def test_target_misbinding_is_hard_reject(self):
        c = classify_observation(_sheddase(target_identity="OTHER"), canonical_target_identity=TARGET_A)
        self.assertFalse(c.admissible)
        self.assertEqual(c.rejection_severity, "HARD")

    def test_unresolved_source_is_soft_reject(self):
        c = self._c(_sheddase(primary_or_repository_source_resolved=False))
        self.assertFalse(c.admissible)
        self.assertEqual(c.rejection_severity, "SOFT")


class DirectionMappingTests(unittest.TestCase):
    def test_material_outcomes_support(self):
        for outcome in (
            "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE",
            "MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE",
        ):
            self.assertEqual(sink_materiality_direction(_tmdd(outcome=outcome)), "SUPPORTS_SINK_LIABILITY")

    def test_no_material_intended_adc_tmdd_opposes(self):
        o = _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK")
        self.assertEqual(sink_materiality_direction(o), "OPPOSES_SINK_LIABILITY")

    def test_no_material_analogue_is_contextual(self):
        o = _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", scenario="SAME_TARGET_THERAPEUTIC_ANALOGUE")
        self.assertEqual(sink_materiality_direction(o), "CONTEXTUAL")

    def test_mixed_and_not_established_are_contextual(self):
        self.assertEqual(sink_materiality_direction(_tmdd(outcome="MIXED_OR_UNRESOLVED")), "CONTEXTUAL")


# =====================================================================
# 3. aggregate -- the frozen evaluation order
# =====================================================================

class AggregationTruthTableTests(unittest.TestCase):
    def _direction(self, res):
        env = res.proposal_envelope
        self.assertIsNotNone(env, res.machine_acceptance.reasons)
        return (env.proposed_direction, env.proposed_strength)

    def test_clean_material_sink_direct_context_is_positive_direct(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("POSITIVE", "DIRECT"))

    def test_clean_material_sink_dominates_other_context_no_material(self):
        obs, comp = _std_landscape(
            _clinical(ctx=SINKCTX_A),
            _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", ctx=SINKCTX_B),
            qualifying_ctx=(SINKCTX_A, SINKCTX_B),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("POSITIVE", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertIn("SUPPORTING", roles)
        self.assertIn("CONTEXTUAL", roles)
        self.assertNotIn("CONTRADICTING", roles)

    def test_same_context_material_and_no_material_is_conflicting_direct(self):
        obs, comp = _std_landscape(
            _clinical(ctx=SINKCTX_A),
            _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", ctx=SINKCTX_A),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("CONFLICTING", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertIn("SUPPORTING", roles)
        self.assertIn("CONTRADICTING", roles)

    def test_intended_adc_no_material_tmdd_only_is_negative_direct(self):
        obs, comp = _std_landscape(
            _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", ctx=SINKCTX_A),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("NEGATIVE", "DIRECT"))

    def test_mixed_direct_only_is_inconclusive_direct(self):
        obs, comp = _std_landscape(
            _clinical(outcome="MIXED_OR_UNRESOLVED", ctx=SINKCTX_A),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertEqual(roles, {"CONTEXTUAL"})

    def test_indirect_strong_only_is_positive_indirect_strong(self):
        obs, comp = _std_landscape(_sheddase(), _quant())
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_weak_only_is_inconclusive_unknown(self):
        obs, comp = _std_landscape(_weak("PREDICTED_CLEAVAGE_SITE_INFERENCE"))
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_below_lod_only_is_inconclusive_unknown_not_negative(self):
        obs, comp = _std_landscape(_quant(status="BELOW_DETECTION_OR_QUANTITATION_LIMIT"))
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_no_evidence_completed_landscape_is_inconclusive_unknown(self):
        obs, comp = _std_landscape()
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_different_contexts_differing_is_never_conflicting(self):
        obs, comp = _std_landscape(
            _clinical(ctx=SINKCTX_A),
            _tmdd(outcome="MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE", ctx=SINKCTX_B),
            qualifying_ctx=(SINKCTX_A, SINKCTX_B),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(self._direction(res), ("POSITIVE", "DIRECT"))

    def test_incomplete_landscape_is_inconclusive_unknown_with_zero_refs(self):
        comp = _completion(complete=False, audit_observation_id="OBS-AUDIT-INC")
        audit = _audit_obs(comp, observation_id="OBS-AUDIT-INC")
        res, _, _ = _run([_sheddase(), _quant(), audit], comp)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_legal_pairs_are_exactly_six(self):
        self.assertEqual(len(LEGAL_DIRECTION_STRENGTH_PAIRS), 6)


# =====================================================================
# 4. completion -- T4 dual subspace + audit parity
# =====================================================================

class CompletionInvariantTests(unittest.TestCase):
    def test_claimed_complete_with_known_unfetched_public_item_is_hard(self):
        item = SolubleAntigenUnresolvedItem(
            "known public serum dataset not fetched", "KNOWN_PUBLIC_NOT_YET_RESOLVED"
        )
        obs, comp = _std_landscape(
            _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK"),
            qualifying_ctx=(SINKCTX_A,), unresolved=(item,),
        )
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertEqual(res.evidence_packages, ())

    def test_access_blocked_source_prevents_negative_but_not_positive_direct(self):
        item = SolubleAntigenUnresolvedItem(
            "source annotation inaccessible", "ACCESS_OR_ANNOTATION_BLOCKED"
        )
        negative_obs, comp = _std_landscape(
            _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK"),
            qualifying_ctx=(SINKCTX_A,), unresolved=(item,),
        )
        neg, _, _ = _run(negative_obs, comp)
        self.assertTrue(neg.machine_acceptance.accepted, neg.machine_acceptance.reasons)
        self.assertEqual((neg.proposal_envelope.proposed_direction,
                          neg.proposal_envelope.proposed_strength),
                         ("INCONCLUSIVE", "UNKNOWN"))
        self.assertTrue(neg.proposal_envelope.critical_unknowns)

        positive_obs, comp2 = _std_landscape(
            _clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,),
            unresolved=(item,),
        )
        pos, _, _ = _run(positive_obs, comp2)
        self.assertTrue(pos.machine_acceptance.accepted, pos.machine_acceptance.reasons)
        self.assertEqual((pos.proposal_envelope.proposed_direction,
                          pos.proposal_envelope.proposed_strength),
                         ("POSITIVE", "DIRECT"))
    def test_crc_subspace_true_healthy_false_but_quant_axis_true_is_hard(self):
        comp = SolubleAntigenEvidenceCompletion(
            attempted=True, landscape_as_of=AS_OF, search_scope=SCOPE,
            sources_searched=("db1",),
            public_soluble_antigen_search_complete=True,
            soluble_antigen_quantitation_search_complete=True,
            crc_patient_quantitation_subspace_search_complete=True,
            healthy_donor_quantitation_subspace_search_complete=False,
            sheddase_processing_search_complete=True,
            secreted_isoform_search_complete=True,
            same_target_pk_pd_or_tmdd_search_complete=True,
            unresolved_items=(), qualifying_direct_evidence_context_ids=(),
            audit_observation_id="OBS-AUDIT-X",
        )
        audit = _audit_obs(comp, observation_id="OBS-AUDIT-X")
        res, _, _ = _run([_sheddase(), audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_both_subspaces_true_but_quant_axis_false_is_hard(self):
        comp = SolubleAntigenEvidenceCompletion(
            attempted=True, landscape_as_of=AS_OF, search_scope=SCOPE,
            sources_searched=("db1",),
            public_soluble_antigen_search_complete=False,
            soluble_antigen_quantitation_search_complete=False,
            crc_patient_quantitation_subspace_search_complete=True,
            healthy_donor_quantitation_subspace_search_complete=True,
            sheddase_processing_search_complete=True,
            secreted_isoform_search_complete=True,
            same_target_pk_pd_or_tmdd_search_complete=True,
            unresolved_items=(), qualifying_direct_evidence_context_ids=(),
            audit_observation_id="OBS-AUDIT-Y",
        )
        audit = _audit_obs(comp, observation_id="OBS-AUDIT-Y")
        res, _, _ = _run([_sheddase(), audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_both_subspaces_true_and_axis_true_is_valid(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)

    def test_umbrella_contradicts_components_is_hard(self):
        comp = SolubleAntigenEvidenceCompletion(
            attempted=True, landscape_as_of=AS_OF, search_scope=SCOPE,
            sources_searched=("db1",),
            public_soluble_antigen_search_complete=True,
            soluble_antigen_quantitation_search_complete=True,
            crc_patient_quantitation_subspace_search_complete=True,
            healthy_donor_quantitation_subspace_search_complete=True,
            sheddase_processing_search_complete=False,
            secreted_isoform_search_complete=True,
            same_target_pk_pd_or_tmdd_search_complete=True,
            unresolved_items=(), qualifying_direct_evidence_context_ids=(),
            audit_observation_id="OBS-AUDIT-Z",
        )
        audit = _audit_obs(comp, observation_id="OBS-AUDIT-Z")
        res, _, _ = _run([_sheddase(), audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_missing_audit_observation_is_hard(self):
        comp = _completion(audit_observation_id="OBS-AUDIT-MISSING")
        res, _, _ = _run([_sheddase()], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_two_audit_observations_is_hard(self):
        comp = _completion(audit_observation_id="OBS-AUDIT-DUP")
        a1 = _audit_obs(comp, observation_id="OBS-AUDIT-DUP")
        a2 = _audit_obs(comp, observation_id="OBS-AUDIT-OTHER")
        res, _, _ = _run([_sheddase(), a1, a2], comp)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_audit_snapshot_subspace_drift_is_hard(self):
        comp = _completion(audit_observation_id="OBS-AUDIT-DRIFT")
        audit = _audit_obs(comp, observation_id="OBS-AUDIT-DRIFT")
        audit = _obs(
            observation_id="OBS-AUDIT-DRIFT2",
            observation_kind="SEARCH_COMPLETION_AUDIT",
            analysis_method="SEARCH_AUDIT",
            claim="drifted audit",
            audit_search_scope=comp.search_scope,
            audit_sources_searched=comp.sources_searched,
            audit_landscape_as_of=comp.landscape_as_of,
            audit_public_soluble_antigen_search_complete=True,
            audit_soluble_antigen_quantitation_search_complete=True,
            audit_crc_patient_quantitation_subspace_search_complete=False,  # drift
            audit_healthy_donor_quantitation_subspace_search_complete=True,
            audit_sheddase_processing_search_complete=True,
            audit_secreted_isoform_search_complete=True,
            audit_same_target_pk_pd_or_tmdd_search_complete=True,
        )
        comp2 = _completion(audit_observation_id="OBS-AUDIT-DRIFT2")
        res, _, _ = _run([_sheddase(), audit], comp2)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_qualifying_context_set_drift_is_hard(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_B,))
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_qualifying_context_set_union_of_single_string_ids(self):
        obs, comp = _std_landscape(
            _clinical(ctx=SINKCTX_A),
            _tmdd(outcome="MIXED_OR_UNRESOLVED", ctx=SINKCTX_B),
            qualifying_ctx=(SINKCTX_A, SINKCTX_B),
        )
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)

    def test_no_qualifying_indirect_context_field_exists(self):
        fields = set(SolubleAntigenEvidenceCompletion.__dataclass_fields__)
        self.assertNotIn("qualifying_indirect_evidence_context_ids", fields)
        self.assertIn("qualifying_direct_evidence_context_ids", fields)

    def test_attempted_false_strict_empty(self):
        with self.assertRaises(ValueError):
            SolubleAntigenEvidenceCompletion(
                attempted=False, landscape_as_of=AS_OF, search_scope="scope",
                sources_searched=(),
                public_soluble_antigen_search_complete=False,
                soluble_antigen_quantitation_search_complete=False,
                crc_patient_quantitation_subspace_search_complete=False,
                healthy_donor_quantitation_subspace_search_complete=False,
                sheddase_processing_search_complete=False,
                secreted_isoform_search_complete=False,
                same_target_pk_pd_or_tmdd_search_complete=False,
                unresolved_items=(), qualifying_direct_evidence_context_ids=(),
                audit_observation_id="",
            )

    def test_incomplete_landscape_is_unknown_not_an_integrity_failure(self):
        res, _, _ = _run([_sheddase()], _completion(attempted=False))
        self.assertFalse(res.hard_integrity_failures)
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(
            (res.proposal_envelope.proposed_direction, res.proposal_envelope.proposed_strength),
            ("INCONCLUSIVE", "UNKNOWN"),
        )


# =====================================================================
# 5. fatal_review -- T5
# =====================================================================

class FatalReviewTests(unittest.TestCase):
    def _fatal(self, res):
        return res.fatal_review

    def test_clinical_material_with_compromise_is_fatal_candidate(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "POTENTIAL_FATAL_PATTERN")
        self.assertEqual(res.fatal_review.source_path, ("CLINICAL",))

    def test_clinical_material_with_compromise_and_reproducibility_not_established_still_fatal(self):
        obs, comp = _std_landscape(
            _clinical(ctx=SINKCTX_A, reproducibility_status="NOT_ESTABLISHED"),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.fatal_review.required)

    def test_clinical_attribution_not_qualified_is_not_direct_so_not_fatal(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A, attribution=False))
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.fatal_review.required)

    def test_tmdd_material_with_compromise_intended_is_fatal(self):
        obs, comp = _std_landscape(_tmdd(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.source_path, ("TMDD",))

    def test_validated_material_tmdd_without_numeric_lod_remains_direct_and_fatal(self):
        obs, comp = _std_landscape(
            _tmdd(ctx=SINKCTX_A, detection_limit_basis="",
                  detection_limit_value=None, detection_limit_unit=""),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(
            (res.proposal_envelope.proposed_direction,
             res.proposal_envelope.proposed_strength),
            ("POSITIVE", "DIRECT"),
        )
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.source_path, ("TMDD",))

    def test_tmdd_material_with_compromise_analogue_is_positive_direct_but_not_fatal(self):
        obs, comp = _std_landscape(
            _tmdd(scenario="SAME_TARGET_THERAPEUTIC_ANALOGUE", ctx=SINKCTX_A),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(
            (res.proposal_envelope.proposed_direction, res.proposal_envelope.proposed_strength),
            ("POSITIVE", "DIRECT"),
        )
        self.assertFalse(res.fatal_review.required)

    def test_material_without_established_compromise_is_positive_direct_but_not_fatal(self):
        obs, comp = _std_landscape(
            _clinical(outcome="MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE",
                      ctx=SINKCTX_A),
            qualifying_ctx=(SINKCTX_A,),
        )
        res, _, _ = _run(obs, comp)
        self.assertEqual(
            (res.proposal_envelope.proposed_direction, res.proposal_envelope.proposed_strength),
            ("POSITIVE", "DIRECT"),
        )
        self.assertFalse(res.fatal_review.required)

    def test_no_global_cancellation_precondition_positive_direct_does_not_clear_fatal(self):
        # a clean material-with-compromise DIRECT context -> POSITIVE / DIRECT AND fatal.
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertEqual(
            (res.proposal_envelope.proposed_direction, res.proposal_envelope.proposed_strength),
            ("POSITIVE", "DIRECT"),
        )
        self.assertTrue(res.fatal_review.required)

    def test_fatal_review_not_surfaced_on_a_rejected_run(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        # break provenance -> HARD reject
        res, _, _ = _run(obs, comp, mismatch={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "")

    def test_fatal_review_is_not_a_proposal_envelope_field(self):
        for name in AssessmentProposalEnvelope.field_names():
            self.assertNotIn("fatal", name)
            self.assertNotIn("review", name)

    def test_fatal_review_never_emits_more_than_potential_pattern(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertIn(res.fatal_review.status, ("", "POTENTIAL_FATAL_PATTERN"))

    def test_incomplete_landscape_has_no_fatal_trigger(self):
        res, _, _ = _run([_clinical(ctx=SINKCTX_A)], _completion(complete=False))
        self.assertFalse(res.fatal_review.required)

    def test_the_typed_outcome_alone_is_the_fatal_authority_no_second_boolean(self):
        # E16 review round-1 blocker 1: MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE
        # is itself the sole machine authority -- there is no second
        # documents_clinical_exposure_compromise gate.
        fields = set(NormalizedSolubleAntigenObservation.__dataclass_fields__)
        self.assertNotIn("documents_clinical_exposure_compromise", fields)
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)


class ContextualDirectAuthorityObservationTests(unittest.TestCase):
    """E16 review round-1 blocker 2: a CLINICAL_ANTIGEN_SINK_PK_EFFECT /
    SOLUBLE_ANTIGEN_TMDD_ANALYSIS observation the classifier judged CONTEXTUAL
    (e.g. same-target match / TMDD input adequacy NOT_ESTABLISHED) may keep its
    real factual local sink_exposure_context_id -- it is NOT an illegal input."""

    def _direction(self, res):
        env = res.proposal_envelope
        self.assertIsNotNone(env, res.machine_acceptance.reasons)
        return (env.proposed_direction, env.proposed_strength)

    def test_contextual_clinical_with_factual_sink_context_is_accepted(self):
        obs, comp = _std_landscape(
            _clinical(ctx=SINKCTX_A, match=False), _sheddase(),
        )
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.hard_integrity_failures)
        self.assertFalse(res.fatal_review.required)
        # the sheddase observation still drives the graded answer.
        self.assertEqual(self._direction(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_contextual_tmdd_with_factual_sink_context_is_accepted(self):
        obs, comp = _std_landscape(
            _tmdd(ctx=SINKCTX_A, tmdd_ok=False), _sheddase(),
        )
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(self._direction(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_contextual_clinical_alone_with_factual_sink_context_is_inconclusive_unknown(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A, attribution=False))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_an_indirect_strong_observation_still_may_not_carry_a_sink_context(self):
        # the constructor forbids it; the acceptance kind-check backs it up.
        with self.assertRaises(ValueError):
            _sheddase(sink_exposure_context_id=SINKCTX_A,
                      sink_exposure_context_basis="not allowed here")


# =====================================================================
# 6. evidence -- T6 reuse / dedup / no raw-value branch
# =====================================================================

class EvidenceReuseAndDedupTests(unittest.TestCase):
    def _canonical(self, o, evidence_id="EP-00009000", *, study_context_overrides=None):
        from gate_modules.tgt07_shedding_soluble_antigen_sink_liability_v2.evidence import (
            _KEYS_ALWAYS,
            _AUDIT_KEYS,
            _study_context_facts,
            _measurement,
        )

        ind, treat, samp = _study_context_facts(o)
        sc = {"indication": ind, "treatment_state": treat, "sample_type": samp}
        for k in (*_KEYS_ALWAYS, *_AUDIT_KEYS):
            sc[k] = getattr(o, k)
        if study_context_overrides:
            sc.update(study_context_overrides)
        return EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=o.claim,
            measurement=_measurement(classify_observation(o, canonical_target_identity=TARGET_A)),
            candidate_refs=("CAND-L04-000001",),
            study_context=sc,
            provenance={
                "source_id": "SRC-00000001", "source_type": "PMID",
                "source_identifier": "PMID:0001", "locator": "loc", "retrieved_at": AS_OF,
            },
            interpretation_boundary={
                "directly_supports": ("x",), "does_not_support": ("y",),
                "limitations": ("z",), "evidence_ceiling": "c",
            },
            derivation={"module_run_id": "run-e16-1", "code_commit": "deadbeef"},
        )

    def test_exact_canonical_reuse(self):
        o = _sheddase(observation_id="OBS-REUSE-1")
        obs, comp = _std_landscape(o)
        can = self._canonical(o, evidence_id="EP-00009001")
        res, alloc, _ = _run(obs, comp, library=Lib({"OBS-REUSE-1": can}))
        self.assertIn("EP-00009001", res.reused_evidence_ids)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)

    def test_reuse_retrieved_at_drift_hard_rejects(self):
        o = _sheddase(observation_id="OBS-REUSE-TIME")
        obs, comp = _std_landscape(o)
        can = self._canonical(o)
        bad = dataclasses.replace(can, provenance={**can.provenance,
                                                  "retrieved_at": "2025-01-01"})
        res, _, _ = _run(obs, comp, library=Lib({o.observation_id: bad}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertEqual(res.evidence_packages, ())

    def test_reuse_measurement_drift_hard_rejects(self):
        o = _sheddase(observation_id="OBS-REUSE-MEAS")
        obs, comp = _std_landscape(o)
        can = self._canonical(o)
        bad = dataclasses.replace(can, measurement={**can.measurement,
                                                   "result": "different fact"})
        res, _, _ = _run(obs, comp, library=Lib({o.observation_id: bad}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertEqual(res.evidence_packages, ())

    def test_reuse_with_drifted_sink_materiality_outcome_is_hard(self):
        o = _clinical(observation_id="OBS-REUSE-2", ctx=SINKCTX_A)
        obs, comp = _std_landscape(o, qualifying_ctx=(SINKCTX_A,))
        can = self._canonical(
            o, evidence_id="EP-00009002",
            study_context_overrides={"sink_materiality_outcome": "NO_MATERIAL_SOLUBLE_SINK"},
        )
        res, _, _ = _run(obs, comp, library=Lib({"OBS-REUSE-2": can}))
        self.assertFalse(res.machine_acceptance.accepted)

    def test_same_source_claim_different_sink_context_both_survive(self):
        a = _clinical(observation_id="OBS-DD-A", claim="shared claim", ctx=SINKCTX_A)
        b = _clinical(observation_id="OBS-DD-B", claim="shared claim", ctx=SINKCTX_B)
        obs, comp = _std_landscape(a, b, qualifying_ctx=(SINKCTX_A, SINKCTX_B))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(len(res.evidence_packages), 3)  # a + b + audit

    def test_exact_string_equality_trailing_space_makes_records_distinct(self):
        a = _sheddase(observation_id="OBS-SP-A", claim="claimX")
        b = _sheddase(observation_id="OBS-SP-B", claim="claimX ")
        obs, comp = _std_landscape(a, b)
        res, _, _ = _run(obs, comp)
        self.assertEqual(len(res.evidence_packages), 3)  # both survive + audit

    def test_distinct_event_ids_are_not_collapsed_by_same_source_and_claim(self):
        a = _sheddase(observation_id="OBS-TD-A", claim="dupclaim")
        b = _sheddase(observation_id="OBS-TD-B", claim="dupclaim")
        obs, comp = _std_landscape(a, b)
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(len(res.evidence_packages), 3)  # two events + audit

    def test_search_completion_audit_ep_is_never_a_dedup_loser(self):
        obs, comp = _std_landscape(_sheddase(claim="search completion audit"))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        kinds = [
            ep.study_context["observation_kind"] for ep in res.evidence_packages
        ]
        self.assertIn("SEARCH_COMPLETION_AUDIT", kinds)

    def test_no_dedicated_raw_value_field_on_the_observation(self):
        fields = set(NormalizedSolubleAntigenObservation.__dataclass_fields__)
        for suspicious in ("soluble_antigen_concentration", "sink_ratio", "k_d", "turnover"):
            self.assertNotIn(suspicious, fields)

    def test_source_reported_number_in_claim_is_allowed(self):
        obs, comp = _std_landscape(_quant(claim="serum soluble target 18 ng/mL in CRC patients"))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)


class DuplicateObservationIdPreflightTests(unittest.TestCase):
    def test_duplicate_observation_id_short_circuits_before_any_port_call(self):
        a = _sheddase(observation_id="OBS-SAME")
        b = _secreted(observation_id="OBS-SAME")
        obs, comp = _std_landscape(a, b)
        res, alloc, srcres = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertEqual(alloc.calls, 0)
        self.assertEqual(srcres.calls, 0)
        self.assertTrue(res.hard_integrity_failures)


# =====================================================================
# 7. hard integrity + output surface
# =====================================================================

class HardIntegrityTests(unittest.TestCase):
    def test_unresolved_source_is_hard_reject(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp, unresolved={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_provenance_mismatch_is_hard_reject(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp, mismatch={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)

    def test_context_key_drift_is_hard_reject(self):
        obs, comp = _std_landscape(_sheddase(context_key="other-ctx"))
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_search_scope_drift_is_hard_reject(self):
        obs, comp = _std_landscape(_sheddase())
        mi = _input(soluble_antigen_search_scope="a different declared scope")
        res, _, _ = _run(obs, comp, module_input=mi)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_local_sink_context_equal_to_canonical_context_id_is_rejected_by_constructor(self):
        with self.assertRaises(ValueError):
            _clinical(sink_exposure_context_id="CTX-CRC-REFRACTORY-MCRC",
                      sink_exposure_context_basis="collides")

    def test_hard_failure_is_never_degraded_to_accepted_unknown(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp, unresolved={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)


class OutputSurfaceTests(unittest.TestCase):
    def test_accepted_run_output_surface(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp)
        self.assertIsInstance(res, Tgt07ModuleRunResult)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertIsInstance(res.soluble_antigen_completion, SolubleAntigenEvidenceCompletion)
        self.assertIsInstance(res.fatal_review, FatalReviewRecord)
        self.assertEqual(res.module_id, "MOD-TGT07")
        self.assertEqual(res.module_version, "2.0.0")
        self.assertEqual(res.gate_id, "TGT-07")

    def test_hard_reject_returns_no_partial_ep_or_reuse(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp, unresolved={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertEqual(res.evidence_packages, ())
        self.assertEqual(res.reused_evidence_ids, ())

    def test_source_resolver_must_return_exact_requested_source_id(self):
        obs, comp = _std_landscape(_sheddase())

        class WrongIdSourceResolver:
            def resolve(self, source_id):
                return CanonicalSourceRecord(
                    "SRC-00000002", "PMID", "PMID:0001", "loc"
                )

        res = run(
            _input(), provider=Prov(obs, comp), evidence_id_allocator=Alloc(),
            source_resolver=WrongIdSourceResolver(), evidence_library=Lib(),
        )
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertEqual(res.evidence_packages, ())

    def test_program_misbinding_hard_rejects_entire_round(self):
        obs, comp = _std_landscape(_sheddase(program_id="PROG-OTHER"))
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertEqual(res.evidence_packages, ())

    def test_intended_adc_construct_misbinding_hard_rejects(self):
        o = _tmdd(construct_id="ADC-OTHER")
        obs, comp = _std_landscape(o, qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertEqual(res.evidence_packages, ())

    def test_missing_quantitative_tmdd_inputs_cannot_propose_negative(self):
        o = _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", affinity_basis="")
        obs, comp = _std_landscape(o)
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(
            (res.proposal_envelope.proposed_direction,
             res.proposal_envelope.proposed_strength),
            ("INCONCLUSIVE", "UNKNOWN"),
        )

    def test_missing_tmdd_detection_limit_cannot_propose_negative(self):
        o = _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", detection_limit_basis="")
        obs, comp = _std_landscape(o)
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual((res.proposal_envelope.proposed_direction,
                          res.proposal_envelope.proposed_strength),
                         ("INCONCLUSIVE", "UNKNOWN"))

    def test_invalid_quantitative_unit_is_rejected_at_input_boundary(self):
        with self.assertRaises(ValueError):
            _tmdd(assay_unit="heartbeats/min")

    def test_contradictory_assay_and_detection_limit_units_hard_rejects(self):
        o = _tmdd(detection_limit_unit="pM")
        obs, comp = _std_landscape(o)
        res, _, _ = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertEqual(res.evidence_packages, ())

    def test_unbounded_quantitation_without_assay_limit_is_contextual(self):
        obs, comp = _std_landscape(_quant(detection_limit_basis=""))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")

    def test_review_surface_preserves_each_context_and_both_conflict_sides(self):
        a = _clinical(ctx=SINKCTX_A)
        b = _tmdd(outcome="NO_MATERIAL_SOLUBLE_SINK", ctx=SINKCTX_A)
        c = _clinical(ctx=SINKCTX_B)
        obs, comp = _std_landscape(a, b, c, qualifying_ctx=(SINKCTX_A, SINKCTX_B))
        res, _, _ = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "POSITIVE")
        self.assertEqual([row[1] for row in env.context_outcomes],
                         ["CONFLICTING", "MATERIAL_SINK"])
        self.assertEqual(len(env.conflict_evidence_refs), 2)
        self.assertTrue(env.completion_audit_ref.startswith("EP-"))

    def test_proposal_envelope_carries_frozen_ceiling_and_identity_pins(self):
        obs, comp = _std_landscape(_sheddase())
        res, _, _ = _run(obs, comp)
        env = res.proposal_envelope
        self.assertEqual(env.evidence_ceiling, TGT07_EVIDENCE_CEILING)
        self.assertEqual(env.context_id, "CTX-CRC-REFRACTORY-MCRC")
        self.assertEqual(env.gate_id, "TGT-07")

    def test_proposal_envelope_never_carries_assessment_or_review_fields(self):
        for name in AssessmentProposalEnvelope.field_names():
            self.assertNotIn(name, ("assessment_id", "assessment_version", "review"))

    def test_gate_neutral_packages_carry_treatment_state_not_applicable(self):
        obs, comp = _std_landscape(
            _sheddase(), _quant(), _weak("PREDICTED_CLEAVAGE_SITE_INFERENCE"),
        )
        res, _, _ = _run(obs, comp)
        for ep in res.evidence_packages:
            self.assertEqual(ep.study_context["treatment_state"], "not_applicable")
            self.assertNotEqual(ep.study_context["indication"], "refractory_mcrc")

    def test_gate_neutral_package_does_not_stamp_a_grade(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        for ep in res.evidence_packages:
            self.assertNotIn("proposed_direction", ep.study_context)
            self.assertNotIn("evidence_rung", ep.study_context)
            joined = " ".join(ep.interpretation_boundary["does_not_support"]).lower()
            self.assertIn("kill", joined)  # named as NOT supported

    def test_no_cross_gate_or_decision_language_in_module_owned_text(self):
        obs, comp = _std_landscape(_clinical(ctx=SINKCTX_A), qualifying_ctx=(SINKCTX_A,))
        res, _, _ = _run(obs, comp)
        rationale = res.proposal_envelope.aggregation_rationale.lower()
        for bad in ("kill", "hold", "decision", "public_fatal_signal_established"):
            self.assertNotIn(bad, rationale)


if __name__ == "__main__":
    unittest.main()
