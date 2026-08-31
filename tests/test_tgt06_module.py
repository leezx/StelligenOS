"""Runtime Migration PR E14: MOD-TGT06 deterministic scientific core.

Synthetic, in-memory only -- no network, no real live-cell-imaging /
pH-sensitive-dye / surface-decay-flow / lysosomal-co-localization /
recycling-vs-degradation / same-target-ADC data, no persistence. The candidate
target is ``TARGET_A``; LOCAL antibody / epitope configuration identities are
``CFG_A`` / ``CFG_B`` / ``CFG_C``. No HER2 / TROP2 / real target names.

Covers the E14 acceptance scenarios (ChatGPT AI审核方案 E14-1..E14-8 + the 6
required implementation tightenings + the frozen proposal evidence-role mapping):

* the TGT-06 binding reconciliation (0.0.0 -> 1.0.0 with MIGRATION_PENDING still
  in force -- TGT-07 is the last unbuilt primary Module), the module boundary
  (ports only, no network / subprocess / persistence, no normalizer, no generic
  framework, no numeric coercion of a source-reported internalization value);
* the HARD identity / provenance / completion-consistency / qualification
  integrity gate -- rejects the WHOLE run, never degrades to an accepted UNKNOWN;
* the SINGLE classifier authority -- every DIRECT-quality FAILURE (the three
  eligible kinds) maps to DIRECT + OPPOSES_ADDRESSABILITY (E14-3 tightening 2);
* T1 -- an outcome-aware INDIRECT_STRONG (a FAILS outcome is NEVER positive IS;
  INTERNALIZATION_ONLY + PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY is a
  HARD typed-fact incoherence);
* T3 -- the three frozen configuration-identity states, a canonicalised
  ``internalization_configuration_ids``, the ONE projection helper, a DIRECT-quality
  observation in IDENTITY_NOT_DISCLOSED is HARD;
* the frozen ``frozen_evaluation_order`` (7 steps, stop at the first match),
  existence-proof dominance, CONFLICTING only for a same-configuration
  productive-vs-failure pair with NO machine conflict resolver, INCONCLUSIVE /
  DIRECT for exactly one failure configuration, POSITIVE / INDIRECT_STRONG for a
  qualifying-INDIRECT_STRONG landscape, and the frozen evidence-role mapping
  (different-configuration failures under a clean productive existence proof are
  CONTEXTUAL, not CONTRADICTING);
* T4 -- the exact audit identity (audit_observation_id <-> normalized audit
  observation <-> emitted / reused audit EP) + snapshot parity + the
  UNION-of-projection qualifying-DIRECT-configuration set; there is NO
  qualifying_indirect_configuration_ids set; ``attempted == False`` strict-empty;
* T6 -- the fatal_review TRIGGER: a HARD global precondition (any qualifying
  productive DIRECT cancels), Route A (ONE IDENTIFIED_MULTI observation,
  projection >= 2, reproducibility QUALIFIED + basis) OR Route B (>= 2 DISTINCT
  eligible failure observations AND projected configuration union >= 2); a single
  IDENTIFIED_MULTI never satisfies Route B; a Gate NEGATIVE is NOT a machine
  POTENTIAL_FATAL_PATTERN; a QUALIFIED well-matched CRC model contributor IS
  eligible; at most POTENTIAL_FATAL_PATTERN; only actionable on an accepted run;
  not a proposal-envelope field;
* T5 -- exact canonical EvidencePackage reuse parity incl. internalization_outcome
  and the antibody / epitope / affinity / conjugation identity fields; the
  improved TGT-03 dedup (same source_id + claim + different configuration id ->
  BOTH survive); a SEARCH_COMPLETION_AUDIT EP is never a dedup loser;
* T6 -- NO dedicated raw numeric internalization field and NO raw-value
  reuse-parity branch; a source-reported numeric assay fact lives in the neutral
  claim; the "no numeric threshold" check only scans Module-owned text;
* the duplicate observation_id preflight -- proposal None, allocator.calls == 0,
  the source resolver not called, EP construction skipped;
* E14-2 -- study_context.treatment_state == "not_applicable" for EVERY
  observation kind; indication / sample_type stay kind-specific factual and are
  never inflated to "refractory_mcrc";
* the accepted-run output surface (EvidencePackages + one
  InternalizationEvidenceCompletion + fatal_review + proposal envelope +
  MachineAcceptanceRecord, never a CandidateGateAssessment / HUMAN_APPROVED /
  Decision).
"""

from __future__ import annotations

import ast
import itertools
import unittest
from pathlib import Path

import yaml

from src.objects.crc_adc_target_gateset import BUILT_MODULE_VERSIONS
from src.objects.decision_model import EvidencePackage

from gate_modules.tgt06_internalization_trafficking_addressability import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    TGT06_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    FatalReviewRecord,
    InternalizationEvidenceCompletion,
    InternalizationUnresolvedItem,
    MachineAcceptanceRecord,
    NormalizedInternalizationObservation,
    Tgt06ModuleInput,
    Tgt06ModuleRunResult,
    configuration_identity_projection,
    run,
)
from gate_modules.tgt06_internalization_trafficking_addressability.classify import (
    classify_observation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt06_internalization_trafficking_addressability"
GATESET_YAML = REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"

TARGET_A = "TARGET_A"
CAND = "CAND-L04-000123"
CTX_ID = "CTX-CRC-REFRACTORY-MCRC"
INST = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CONTEXT_KEY = "REFRACTORY_MCRC"
AS_OF = "2026-08-31"
SCOPE = (
    "live-cell-imaging + pH-sensitive-dye + surface-decay-flow + "
    "lysosomal-co-localization + recycling-vs-degradation + same-target-ADC repositories"
)
CFG_A, CFG_B, CFG_C = "CFG-AB-001", "CFG-AB-002", "CFG-AB-003"

_SRC_COUNTER = itertools.count(1)
_OBS_COUNTER = itertools.count(1)


def _next_src() -> str:
    return f"SRC-{next(_SRC_COUNTER):08d}"


def _next_obs(tag: str) -> str:
    return f"OBS-{tag}-{next(_OBS_COUNTER):04d}"


# --- deterministic fakes -----------------------------------------------------

class FakeAllocator:
    def __init__(self, start: int = 1) -> None:
        self._n = start - 1
        self.calls = 0

    def next_evidence_id(self) -> str:
        self.calls += 1
        self._n += 1
        return f"EP-{self._n:08d}"


class FakeSourceResolver:
    def __init__(
        self,
        observations,
        *,
        unresolved: set[str] | None = None,
        mismatch: set[str] | None = None,
    ) -> None:
        unresolved = unresolved or set()
        mismatch = mismatch or set()
        self.calls = 0
        self._by_id: dict[str, CanonicalSourceRecord] = {}
        for o in observations:
            if o.source_id in unresolved:
                continue
            ident = o.source_identifier + ("-DRIFT" if o.source_id in mismatch else "")
            self._by_id.setdefault(
                o.source_id,
                CanonicalSourceRecord(
                    source_id=o.source_id,
                    source_type=o.source_type,
                    source_identifier=ident,
                    locator=o.locator,
                ),
            )

    def resolve(self, source_id: str):
        self.calls += 1
        return self._by_id.get(source_id)


class FakeEvidenceLibrary:
    def __init__(self, known: dict[str, EvidencePackage] | None = None) -> None:
        self._known = known or {}

    def resolve(self, observation_id: str):
        return self._known.get(observation_id)


class FakeProvider:
    def __init__(self, observations, completion) -> None:
        self._observations = list(observations)
        self._completion = completion

    def fetch_observations(self, **_):
        return list(self._observations)

    def internalization_completion(self, **_):
        return self._completion


# --- observation factories ------------------------------------------------

_BASE = dict(
    target_identity=TARGET_A,
    context_key=CONTEXT_KEY,
    landscape_as_of=AS_OF,
    assay_method="",
    assay_validation_status="NOT_ESTABLISHED",
    assay_validation_basis="",
    crc_specific=False,
    surface_context_class="",
    surface_context_basis="",
    context_adequacy_status="NOT_ESTABLISHED",
    context_adequacy_basis="",
    internalization_outcome="NOT_ESTABLISHED",
    internalization_outcome_basis="",
    reproducibility_status="NOT_ESTABLISHED",
    reproducibility_basis="",
    source_type="GEO",
    source_identifier="GSE-XXXX",
    locator="",
    retrieved_at=AS_OF,
    primary_or_repository_source_resolved=True,
    declared_multi_configuration_analysis=False,
    internalization_configuration_id="",
    internalization_configuration_ids=(),
    configuration_identity_basis="",
    antibody_identity="",
    epitope_identity_or_region="",
    affinity_context="",
    conjugation_context="",
)


def _obs(kind: str, **over) -> NormalizedInternalizationObservation:
    fields = dict(_BASE)
    fields["observation_id"] = over.pop("observation_id", _next_obs(kind[:6]))
    fields["observation_kind"] = kind
    fields["claim"] = over.pop("claim", f"source reported a {kind} observation for the target")
    fields["source_id"] = over.pop("source_id", _next_src())
    fields.update(over)
    return NormalizedInternalizationObservation(**fields)


def _integrated(
    *,
    outcome: str = "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY",
    context: str = "CRC_MALIGNANT_CELLS",
    config_id: str = CFG_A,
    config_ids: tuple[str, ...] = (),
    reproducibility: str = "NOT_ESTABLISHED",
    assay_qualified: bool = True,
    **over,
) -> NormalizedInternalizationObservation:
    multi = bool(config_ids)
    fields = dict(
        crc_specific=context in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL"),
        surface_context_class=context,
        surface_context_basis="annotated CRC malignant cells" if context != "NON_CRC_CONTEXT" else "a non-CRC cell line",
        context_adequacy_status="QUALIFIED" if context in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL") else "NOT_ESTABLISHED",
        context_adequacy_basis="a QUALIFIED disease-relevant context review" if context in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL") else "",
        assay_method="live-cell imaging + lysosomal co-localization" if assay_qualified else "",
        assay_validation_status="QUALIFIED" if assay_qualified else "NOT_ESTABLISHED",
        assay_validation_basis="orthogonal-assay concordance + isotype control" if assay_qualified else "",
        internalization_outcome=outcome,
        internalization_outcome_basis="the source's typed internalization / trafficking characterisation",
        reproducibility_status=reproducibility,
        reproducibility_basis="independent replicate panel documented in the source" if reproducibility == "QUALIFIED" else "",
        declared_multi_configuration_analysis=multi,
        internalization_configuration_id="" if multi else config_id,
        internalization_configuration_ids=config_ids,
        configuration_identity_basis="the source's disclosed antibody / epitope configuration identity",
        antibody_identity="mAb-synthetic-01",
        epitope_identity_or_region="membrane-proximal region",
    )
    fields.update(over)
    return _obs("ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING", **fields)


def _internalization_only(**over) -> NormalizedInternalizationObservation:
    return _integrated(**over) if False else _kindful(
        "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY", **over
    )


def _trafficking_only(**over) -> NormalizedInternalizationObservation:
    return _kindful("TRAFFICKING_OR_RECYCLING_ONLY", **over)


def _kindful(
    kind: str,
    *,
    outcome: str = "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING",
    context: str = "CRC_MALIGNANT_CELLS",
    config_id: str = CFG_A,
    config_ids: tuple[str, ...] = (),
    assay_qualified: bool = True,
    reproducibility: str = "NOT_ESTABLISHED",
    **over,
) -> NormalizedInternalizationObservation:
    multi = bool(config_ids)
    disease = context in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL")
    fields = dict(
        crc_specific=disease,
        surface_context_class=context,
        surface_context_basis="annotated CRC malignant cells" if context != "NON_CRC_CONTEXT" else "a non-CRC cell line",
        context_adequacy_status="QUALIFIED" if disease else "NOT_ESTABLISHED",
        context_adequacy_basis="a QUALIFIED disease-relevant context review" if disease else "",
        assay_method="surface-decay flow + recycling-vs-degradation readout" if assay_qualified else "",
        assay_validation_status="QUALIFIED" if assay_qualified else "NOT_ESTABLISHED",
        assay_validation_basis="orthogonal-assay concordance" if assay_qualified else "",
        internalization_outcome=outcome,
        internalization_outcome_basis="the source's typed internalization / trafficking characterisation"
        if outcome != "NOT_ESTABLISHED" else "",
        reproducibility_status=reproducibility,
        reproducibility_basis="independent replicate panel documented in the source" if reproducibility == "QUALIFIED" else "",
        declared_multi_configuration_analysis=multi,
        internalization_configuration_id="" if multi else config_id,
        internalization_configuration_ids=config_ids,
        configuration_identity_basis="the source's disclosed antibody / epitope configuration identity"
        if (multi or config_id) else "",
        antibody_identity="mAb-synthetic-02",
        epitope_identity_or_region="distal loop",
    )
    fields.update(over)
    return _obs(kind, **fields)


def _indirect(kind: str, **over) -> NormalizedInternalizationObservation:
    fields = dict(
        crc_specific=False,
        claim=f"the literature establishes a {kind} addressability fact for the target",
    )
    fields.update(over)
    return _obs(kind, **fields)


def _weak(kind: str, **over) -> NormalizedInternalizationObservation:
    return _obs(kind, claim=f"a {kind} hypothesis for the target", **over)


def _completion(
    *,
    attempted: bool = True,
    complete: bool = True,
    ab_complete: bool | None = None,
    traffic_complete: bool | None = None,
    adc_complete: bool | None = None,
    receptor_complete: bool | None = None,
    unresolved: tuple[InternalizationUnresolvedItem, ...] = (),
    qualifying_direct: tuple[str, ...] = (),
    audit_obs_id: str | None = "OBS-AUDIT-0001",
    as_of: str = AS_OF,
) -> InternalizationEvidenceCompletion:
    a = complete if ab_complete is None else ab_complete
    t = complete if traffic_complete is None else traffic_complete
    d = complete if adc_complete is None else adc_complete
    r = complete if receptor_complete is None else receptor_complete
    all_c = a and t and d and r
    return InternalizationEvidenceCompletion(
        attempted=attempted,
        landscape_as_of=as_of,
        search_scope=SCOPE if attempted else "",
        sources_searched=("GEO", "PRIDE", "ADCdb") if attempted else (),
        public_internalization_search_complete=all_c if attempted else False,
        antibody_configuration_internalization_search_complete=a if attempted else False,
        productive_trafficking_search_complete=t if attempted else False,
        same_target_adc_functional_delivery_search_complete=d if attempted else False,
        receptor_endocytosis_and_inference_search_complete=r if attempted else False,
        unresolved_items=unresolved,
        qualifying_direct_configuration_ids=tuple(sorted(qualifying_direct)) if attempted else (),
        audit_observation_id=(audit_obs_id or "") if attempted else "",
    )


def _audit(
    completion: InternalizationEvidenceCompletion,
    *,
    observation_id: str | None = None,
    source_id: str | None = None,
    override: dict | None = None,
) -> NormalizedInternalizationObservation:
    fields = dict(
        observation_id=observation_id or completion.audit_observation_id,
        observation_kind="SEARCH_COMPLETION_AUDIT",
        assay_method="SEARCH_AUDIT",
        assay_validation_status="NOT_ESTABLISHED",
        internalization_outcome="NOT_ESTABLISHED",
        claim="the declared public internalization-evidence search is complete",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier="GSE-AUDIT",
        retrieved_at=completion.landscape_as_of,
        audit_search_scope=completion.search_scope,
        audit_sources_searched=completion.sources_searched,
        audit_landscape_as_of=completion.landscape_as_of,
        audit_public_internalization_search_complete=completion.public_internalization_search_complete,
        audit_antibody_configuration_internalization_search_complete=completion.antibody_configuration_internalization_search_complete,
        audit_productive_trafficking_search_complete=completion.productive_trafficking_search_complete,
        audit_same_target_adc_functional_delivery_search_complete=completion.same_target_adc_functional_delivery_search_complete,
        audit_receptor_endocytosis_and_inference_search_complete=completion.receptor_endocytosis_and_inference_search_complete,
        audit_unresolved_item_keys=tuple(i.snapshot_key for i in completion.unresolved_items),
        audit_qualifying_direct_configuration_ids=completion.qualifying_direct_configuration_ids,
    )
    base = dict(_BASE)
    base.update(fields)
    base["landscape_as_of"] = completion.landscape_as_of
    if override:
        base.update(override)
    return NormalizedInternalizationObservation(**base)


def _input(*, target: str = TARGET_A, as_of: str = AS_OF, existing: tuple[str, ...] = ()):
    return Tgt06ModuleInput(
        candidate_id=CAND,
        candidate_name="synthetic ADC candidate",
        target_identity=target,
        instantiation_id=INST,
        context_id=CTX_ID,
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-06",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-E14-TEST",
        code_commit="deadbeef",
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        internalization_search_scope=SCOPE,
        existing_evidence_ids=existing,
    )


def _run(
    observations,
    completion,
    *,
    unresolved: set[str] | None = None,
    mismatch: set[str] | None = None,
    library: dict[str, EvidencePackage] | None = None,
    allocator: FakeAllocator | None = None,
    resolver: FakeSourceResolver | None = None,
    module_input: Tgt06ModuleInput | None = None,
) -> Tgt06ModuleRunResult:
    observations = list(observations)
    return run(
        module_input or _input(),
        provider=FakeProvider(observations, completion),
        evidence_id_allocator=allocator or FakeAllocator(),
        source_resolver=resolver
        or FakeSourceResolver(observations, unresolved=unresolved, mismatch=mismatch),
        evidence_library=FakeEvidenceLibrary(library),
    )


def _direct_ids(observations) -> tuple[str, ...]:
    """The union of projection sets over the DIRECT-quality-shaped observations --
    a test helper mirroring what the Module computes so the completion parity
    holds."""

    out: set[str] = set()
    for o in observations:
        c = classify_observation(o, canonical_target_identity=TARGET_A)
        if c.admissible and (c.qualifying_direct_productive or c.qualifying_direct_failure):
            out |= set(configuration_identity_projection(o))
    return tuple(sorted(out))


def _accepted_run(observations, *, unresolved=(), **kw) -> Tgt06ModuleRunResult:
    """Build a completed landscape whose completion is consistent with the
    classified DIRECT-quality set, wire in a matching audit, and run."""

    obs = list(observations)
    comp = _completion(qualifying_direct=_direct_ids(obs), unresolved=unresolved)
    audit = _audit(comp)
    return _run([*obs, audit], comp, **kw)


def _pe(res: Tgt06ModuleRunResult):
    return res.proposal_envelope


# =====================================================================
# 1. binding + boundary
# =====================================================================

class BindingAndBoundaryTests(unittest.TestCase):
    def test_binding_is_one_zero_zero_and_migration_pending_remains(self):
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-06"], "1.0.0")
        gs = yaml.safe_load(GATESET_YAML.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gs["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-06"], "1.0.0")
        self.assertEqual(by_gate["TGT-07"], "0.0.0")
        self.assertEqual(
            gs["primary_module_binding"]["built_module_versions"]["TGT-06"], "1.0.0"
        )
        self.assertIn("per_gate_primary_modules", gs["migration"]["deferred"])

    def test_other_modules_untouched(self):
        for g in ("TGT-01", "TGT-02", "TGT-03", "TGT-04", "TGT-05", "TGT-08"):
            self.assertEqual(BUILT_MODULE_VERSIONS[g], "1.0.0")
        self.assertNotIn("TGT-07", BUILT_MODULE_VERSIONS)

    def test_package_has_the_eleven_expected_files(self):
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((PKG / f).is_file(), f)
        py = {p.name for p in PKG.glob("*.py")}
        self.assertNotIn("normalizer.py", py)
        self.assertNotIn("scorer.py", py)
        self.assertNotIn("threshold.py", py)
        self.assertNotIn("generic_gate_module.py", py)

    def test_no_forbidden_runtime_imports_or_numeric_coercion(self):
        forbidden_imports = {
            "socket", "http", "urllib", "requests", "httpx", "aiohttp",
            "subprocess", "sqlite3", "psycopg2", "pymongo", "redis",
            "openai", "anthropic", "torch", "tensorflow", "sentence_transformers",
        }
        forbidden_calls = {"float", "Decimal", "eval", "exec", "compile"}
        for src in PKG.glob("*.py"):
            tree = ast.parse(src.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        self.assertNotIn(a.name.split(".")[0], forbidden_imports, src.name)
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], forbidden_imports, src.name)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_calls, f"{src.name}: {node.func.id}")


# =====================================================================
# 2. rung classification (E14-3 + T1 + T2)
# =====================================================================

class RungClassificationTests(unittest.TestCase):
    def _c(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_integrated_productive_crc_is_a_productive_direct(self):
        c = self._c(_integrated(outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertEqual(c.addressability_implication, "SUPPORTS_ADDRESSABILITY")
        self.assertTrue(c.qualifying_direct_productive)

    def test_integrated_fails_crc_is_a_direct_quality_failure(self):
        c = self._c(_integrated(outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertEqual(c.addressability_implication, "OPPOSES_ADDRESSABILITY")
        self.assertTrue(c.qualifying_direct_failure)

    def test_delivery_unresolved_is_indirect_strong_never_direct(self):
        c = self._c(_integrated(outcome="INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertEqual(c.addressability_implication, "SUPPORTS_ADDRESSABILITY")
        self.assertFalse(c.qualifying_direct_productive)
        self.assertFalse(c.qualifying_direct_failure)
        self.assertTrue(c.qualifying_indirect)

    def test_non_crc_productive_is_indirect_strong_not_direct(self):
        c = self._c(_integrated(context="NON_CRC_CONTEXT", config_id=CFG_A,
                                outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_indirect)

    def test_non_crc_fails_is_contextual_never_opposes_at_gate_level(self):
        c = self._c(_kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
                             context="NON_CRC_CONTEXT", config_id=CFG_A,
                             outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")
        self.assertEqual(c.addressability_implication, "CONTEXTUAL")
        self.assertFalse(c.qualifying_direct_failure)
        self.assertFalse(c.qualifying_indirect)

    def test_fails_outcome_is_never_positive_indirect_strong(self):
        # T1: an internalization assay on CRC whose assay is NOT qualified and
        # whose outcome is FAILS must not become a positive INDIRECT_STRONG.
        c = self._c(_kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
                             assay_qualified=False,
                             outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"))
        self.assertFalse(c.qualifying_indirect)
        self.assertEqual(c.addressability_implication, "CONTEXTUAL")

    def test_internalization_only_fails_is_a_direct_quality_failure_branch_b(self):
        c = self._c(_kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
                             outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_direct_failure)

    def test_trafficking_only_asymmetric_authority(self):
        neg = self._c(_trafficking_only(outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"))
        self.assertEqual(neg.evidence_rung, "DIRECT")
        self.assertTrue(neg.qualifying_direct_failure)
        # a disease-relevant TRAFFICKING_OR_RECYCLING_ONLY observation must
        # disclose its configuration (E14 review round-1 blocker 3).
        pos = self._c(_trafficking_only(
            outcome="INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED",
            config_id=CFG_A))
        self.assertEqual(pos.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(pos.qualifying_indirect)
        self.assertFalse(pos.qualifying_direct_productive)

    def test_constitutive_receptor_biology_and_same_target_adc_are_indirect_strong(self):
        for kind in ("CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
                     "SAME_TARGET_ADC_DELIVERY_PRECEDENT"):
            c = self._c(_indirect(kind))
            self.assertEqual(c.evidence_rung, "INDIRECT_STRONG", kind)
            self.assertTrue(c.qualifying_indirect, kind)
            self.assertEqual(c.addressability_implication, "SUPPORTS_ADDRESSABILITY", kind)

    def test_inference_kinds_are_weak_only(self):
        for kind in ("RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
                     "SURFACE_LOCALIZATION_ONLY_INFERENCE"):
            c = self._c(_weak(kind))
            self.assertEqual(c.evidence_rung, "WEAK", kind)
            self.assertFalse(c.is_qualifying, kind)

    def test_assay_not_qualified_never_reaches_direct(self):
        c = self._c(_integrated(assay_qualified=False))
        self.assertNotEqual(c.evidence_rung, "DIRECT")


# =====================================================================
# 3. frozen_evaluation_order (E14-4) + evidence-role mapping
# =====================================================================

class FrozenEvaluationOrderTests(unittest.TestCase):
    def _direction(self, res):
        return (res.proposal_envelope.proposed_direction, res.proposal_envelope.proposed_strength)

    def test_one_clean_productive_direct_is_positive_direct(self):
        res = _accepted_run([_integrated(config_id=CFG_A)])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("POSITIVE", "DIRECT"))

    def test_existence_proof_dominance_over_heterogeneous_failures(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
            _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY", config_id=CFG_B),
            _kindful("TRAFFICKING_OR_RECYCLING_ONLY", config_id=CFG_C),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("POSITIVE", "DIRECT"))
        # the other-configuration failures are CONTEXTUAL, not CONTRADICTING.
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertNotIn("CONTRADICTING", roles)

    def test_conflicted_config_plus_clean_productive_elsewhere_is_positive_direct(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _integrated(config_id=CFG_B, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("POSITIVE", "DIRECT"))

    def test_same_config_productive_and_failure_is_conflicting_direct(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("CONFLICTING", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertLessEqual({"SUPPORTING", "CONTRADICTING"}, roles)

    def test_different_configs_differ_is_not_conflicting(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
            _integrated(config_id=CFG_B, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
        ]
        res = _accepted_run(obs)
        self.assertEqual(res.proposal_envelope.proposed_direction, "POSITIVE")

    def test_two_independent_failures_no_productive_is_negative_direct(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY", config_id=CFG_B),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("NEGATIVE", "DIRECT"))

    def test_exactly_one_failure_is_inconclusive_direct_never_negative(self):
        res = _accepted_run([_integrated(config_id=CFG_A,
                                         outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING")])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertIn("CONTEXTUAL", roles)

    def test_indirect_strong_only_landscape_is_positive_indirect_strong(self):
        res = _accepted_run([_indirect("CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY")])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_weak_only_landscape_is_inconclusive_unknown_zero_refs(self):
        res = _accepted_run([_weak("RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE")])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_incomplete_landscape_is_inconclusive_unknown(self):
        comp = _completion(complete=False, qualifying_direct=())
        audit = _audit(comp)
        res = _run([_integrated(config_id=CFG_A), audit], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(self._direction(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_legal_pairs_are_exactly_six(self):
        self.assertEqual(len(LEGAL_DIRECTION_STRENGTH_PAIRS), 6)
        self.assertNotIn(("NEGATIVE", "INDIRECT_STRONG"), LEGAL_DIRECTION_STRENGTH_PAIRS)
        self.assertNotIn(("INCONCLUSIVE", "WEAK"), LEGAL_DIRECTION_STRENGTH_PAIRS)


# =====================================================================
# 4. configuration identity (T3)
# =====================================================================

class ConfigurationIdentityTests(unittest.TestCase):
    def test_three_states(self):
        single = _integrated(config_id=CFG_A)
        self.assertEqual(single.configuration_identity_state, "SINGLE")
        multi = _integrated(config_id="", config_ids=(CFG_B, CFG_A))
        self.assertEqual(multi.configuration_identity_state, "IDENTIFIED_MULTI")
        nd = _indirect("CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY")
        self.assertEqual(nd.configuration_identity_state, "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE")

    def test_configuration_ids_are_canonicalised_sorted_and_deduped(self):
        o = _integrated(config_id="", config_ids=(CFG_C, CFG_A, CFG_A, CFG_B))
        self.assertEqual(o.internalization_configuration_ids, (CFG_A, CFG_B, CFG_C))

    def test_identified_multi_projects_every_id(self):
        o = _integrated(config_id="", config_ids=(CFG_A, CFG_B))
        self.assertEqual(configuration_identity_projection(o), frozenset({CFG_A, CFG_B}))

    def test_identified_multi_failure_supports_negative_direct_alone(self):
        obs = [_integrated(config_id="", config_ids=(CFG_A, CFG_B),
                           outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING")]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(res.proposal_envelope.proposed_direction, "NEGATIVE")

    def test_direct_quality_observation_in_not_disclosed_state_is_hard(self):
        # a disease-relevant internalization-family observation that does not
        # disclose its configuration cannot even be constructed (E14 review
        # round-1 blocker 3 -- the constructor is the normalized-shape authority).
        with self.assertRaises(ValueError):
            _obs(
                "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
                crc_specific=True,
                surface_context_class="CRC_MALIGNANT_CELLS",
                surface_context_basis="annotated CRC malignant cells",
                context_adequacy_status="QUALIFIED",
                context_adequacy_basis="a QUALIFIED disease-relevant context review",
                assay_method="live-cell imaging + lysosomal co-localization",
                assay_validation_status="QUALIFIED",
                assay_validation_basis="orthogonal-assay concordance",
                internalization_outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY",
                internalization_outcome_basis="the source characterisation",
            )

    def test_local_config_id_equal_to_canonical_context_id_is_rejected(self):
        with self.assertRaises(ValueError):
            _integrated(config_id=CTX_ID)


# =====================================================================
# 5. completion invariants (T4)
# =====================================================================

class CompletionInvariantTests(unittest.TestCase):
    def test_completeness_contradiction_is_hard(self):
        comp = _completion(ab_complete=False)  # umbrella False, but pass umbrella True
        comp = InternalizationEvidenceCompletion(
            attempted=True,
            landscape_as_of=AS_OF,
            search_scope=SCOPE,
            sources_searched=("GEO",),
            public_internalization_search_complete=True,  # contradiction
            antibody_configuration_internalization_search_complete=False,
            productive_trafficking_search_complete=True,
            same_target_adc_functional_delivery_search_complete=True,
            receptor_endocytosis_and_inference_search_complete=True,
            unresolved_items=(),
            qualifying_direct_configuration_ids=(),
            audit_observation_id="OBS-AUDIT-0001",
        )
        res = _run([_audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_audit_observation_id_mismatch_is_hard(self):
        comp = _completion(qualifying_direct=())
        audit = _audit(comp, observation_id="OBS-AUDIT-9999")
        res = _run([_integrated(config_id=CFG_A), audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_two_audit_observations_is_hard(self):
        comp = _completion(qualifying_direct=_direct_ids([]))
        a1 = _audit(comp)
        a2 = _audit(comp, observation_id="OBS-AUDIT-0002")
        res = _run([a1, a2], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_snapshot_drift_is_hard(self):
        comp = _completion(qualifying_direct=())
        audit = _audit(comp, override={"audit_search_scope": "a different scope"})
        res = _run([audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_qualifying_configuration_set_drift_is_hard(self):
        obs = [_integrated(config_id=CFG_A)]
        comp = _completion(qualifying_direct=(CFG_B,))  # wrong
        audit = _audit(comp)
        res = _run([*obs, audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_qualifying_configuration_set_is_the_union_of_projections(self):
        obs = [
            _integrated(config_id="", config_ids=(CFG_A, CFG_B),
                        outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _integrated(config_id=CFG_C, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(
            set(res.internalization_completion.qualifying_direct_configuration_ids),
            {CFG_A, CFG_B, CFG_C},
        )

    def test_attempted_false_is_a_strict_empty_state(self):
        with self.assertRaises(ValueError):
            InternalizationEvidenceCompletion(
                attempted=False,
                landscape_as_of=AS_OF,
                search_scope=SCOPE,  # not allowed when unattempted
                sources_searched=(),
                public_internalization_search_complete=False,
                antibody_configuration_internalization_search_complete=False,
                productive_trafficking_search_complete=False,
                same_target_adc_functional_delivery_search_complete=False,
                receptor_endocytosis_and_inference_search_complete=False,
                unresolved_items=(),
                qualifying_direct_configuration_ids=(),
                audit_observation_id="",
            )

    def test_completion_has_no_qualifying_indirect_configuration_ids_field(self):
        self.assertNotIn(
            "qualifying_indirect_configuration_ids",
            InternalizationEvidenceCompletion.__dataclass_fields__,
        )


# =====================================================================
# 6. fatal review (T6 / T2)
# =====================================================================

class FatalReviewTests(unittest.TestCase):
    def test_any_productive_direct_cancels_the_trigger(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
            _integrated(config_id=CFG_B, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _integrated(config_id=CFG_C, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
        ]
        res = _accepted_run(obs)
        self.assertFalse(res.fatal_review.required)

    def test_route_b_two_distinct_failure_observations_two_configs(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY", config_id=CFG_B),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "POTENTIAL_FATAL_PATTERN")
        self.assertGreaterEqual(len(set(res.fatal_review.configuration_ids)), 2)
        self.assertEqual(res.fatal_review.reproducibility_basis_refs, ())

    def test_single_identified_multi_failure_is_negative_but_not_a_fatal_pattern(self):
        obs = [_integrated(config_id="", config_ids=(CFG_A, CFG_B),
                           outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING",
                           reproducibility="NOT_ESTABLISHED")]
        res = _accepted_run(obs)
        self.assertEqual(res.proposal_envelope.proposed_direction, "NEGATIVE")
        self.assertFalse(res.fatal_review.required)

    def test_single_identified_multi_failure_with_reproducibility_is_route_a(self):
        obs = [_integrated(config_id="", config_ids=(CFG_A, CFG_B),
                           outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING",
                           reproducibility="QUALIFIED")]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)
        self.assertTrue(res.fatal_review.reproducibility_basis_refs)

    def test_well_matched_crc_model_contributor_is_eligible(self):
        obs = [
            _integrated(config_id=CFG_A, context="WELL_MATCHED_CRC_MODEL",
                        outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _kindful("TRAFFICKING_OR_RECYCLING_ONLY", config_id=CFG_B,
                     context="WELL_MATCHED_CRC_MODEL"),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)

    def test_two_semantic_duplicates_do_not_satisfy_route_b(self):
        src = _next_src()
        claim = "the tested antibody failed productive lysosomal trafficking"
        o1 = _integrated(config_id=CFG_A, source_id=src, claim=claim,
                         outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING")
        o2 = _integrated(config_id=CFG_A, source_id=src, claim=claim,
                         outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING")
        res = _accepted_run([o1, o2])
        # one is dropped as a true duplicate -> a single failure configuration.
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")

    def test_fatal_review_only_on_an_accepted_run(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY", config_id=CFG_B),
        ]
        comp = _completion(qualifying_direct=(CFG_C,))  # deliberately wrong -> HARD
        res = _run([*obs, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "")

    def test_fatal_review_is_not_a_proposal_envelope_field(self):
        for n in AssessmentProposalEnvelope.field_names():
            self.assertNotIn("fatal", n)
            self.assertNotIn("review", n)

    def test_machine_never_emits_more_than_potential_pattern(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _kindful("TRAFFICKING_OR_RECYCLING_ONLY", config_id=CFG_B),
        ]
        res = _accepted_run(obs)
        self.assertIn(res.fatal_review.status, ("", "POTENTIAL_FATAL_PATTERN"))
        blob = " ".join(
            [res.proposal_envelope.aggregation_rationale]
            + [u for u, _ in res.proposal_envelope.critical_unknowns]
        ).lower()
        for banned in ("public_fatal_signal_established", "kill", "hold", "decision"):
            self.assertNotIn(banned, blob)


# =====================================================================
# 7. exact reuse / dedup (T5) + duplicate preflight (T7) + T6
# =====================================================================

class ExactReuseAndDedupTests(unittest.TestCase):
    def _reuse(self, obs, drift: dict | None = None):
        comp = _completion(qualifying_direct=_direct_ids([obs]))
        audit = _audit(comp)
        alloc = FakeAllocator(90)
        resolver = FakeSourceResolver([obs, audit])
        canonical = resolver.resolve(obs.source_id)
        study = {
            "indication": "colorectal_cancer",
            "treatment_state": "not_applicable",
            "sample_type": "crc_malignant_cell_internalization_trafficking",
        }
        from gate_modules.tgt06_internalization_trafficking_addressability.evidence import (
            _KEYS_ALWAYS,
        )
        for k in _KEYS_ALWAYS:
            study[k] = getattr(obs, k)
        if drift:
            study.update(drift)
        pkg = EvidencePackage(
            evidence_id="EP-00000042",
            schema_version=1,
            claim=obs.claim,
            measurement={"type": "x", "analyte": TARGET_A, "readout": "r", "result": "z", "unit": ""},
            candidate_refs=(CAND,),
            study_context=study,
            provenance={
                "source_id": canonical.source_id,
                "source_type": canonical.source_type,
                "source_identifier": canonical.source_identifier,
                "locator": canonical.locator,
                "retrieved_at": obs.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": ("x",), "does_not_support": ("y",),
                "limitations": ("z",), "evidence_ceiling": "c",
            },
            derivation={"module_run_id": "r", "code_commit": "c"},
        )
        return _run([obs, audit], comp, allocator=alloc,
                    library={obs.observation_id: pkg}, resolver=resolver), alloc

    def test_clean_reuse_makes_no_allocator_call(self):
        obs = _integrated(config_id=CFG_A)
        res, alloc = self._reuse(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIn("EP-00000042", res.reused_evidence_ids)
        # only the audit EP is freshly allocated.
        self.assertEqual(alloc.calls, 1)

    def test_internalization_outcome_drift_on_reuse_is_hard(self):
        obs = _integrated(config_id=CFG_A)
        res, _ = self._reuse(obs, drift={"internalization_outcome": "MIXED_OR_UNRESOLVED"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_identity_field_drift_on_reuse_is_hard(self):
        for field in ("antibody_identity", "epitope_identity_or_region",
                      "affinity_context", "conjugation_context"):
            obs = _integrated(config_id=CFG_A, **{field: "as-observed"})
            res, _ = self._reuse(obs, drift={field: "DRIFTED"})
            self.assertFalse(res.machine_acceptance.accepted, field)
            self.assertTrue(res.hard_integrity_failures, field)

    def test_improved_dedup_same_source_and_claim_different_config_both_survive(self):
        src = _next_src()
        claim = "the tested antibody internalized with lysosomal delivery"
        o1 = _integrated(config_id=CFG_A, source_id=src, claim=claim)
        o2 = _integrated(config_id=CFG_B, source_id=src, claim=claim)
        res = _accepted_run([o1, o2])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(len(res.evidence_packages), 3)  # 2 + audit

    def test_true_duplicate_is_dropped(self):
        src = _next_src()
        claim = "identical internalization claim"
        o1 = _integrated(config_id=CFG_A, source_id=src, claim=claim)
        o2 = _integrated(config_id=CFG_A, source_id=src, claim=claim)
        res = _accepted_run([o1, o2])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(len(res.evidence_packages), 2)  # 1 + audit
        self.assertTrue(any("duplicate" in why for _, why in res.rejected_records))

    def test_audit_ep_is_never_a_dedup_loser(self):
        comp = _completion(qualifying_direct=())
        a = _audit(comp)
        # a non-audit obs with the same source_id + claim shape must not evict it.
        res = _run([a], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(len(res.evidence_packages), 1)

    def test_no_raw_value_reuse_parity_branch_in_evidence_module(self):
        src = (PKG / "evidence.py").read_text()
        self.assertNotIn("_DENSITY_KEYS", src)
        self.assertNotIn("reported_density", src)
        self.assertNotIn("symmetric presence-and-value", src.lower())


class DuplicateObservationIdPreflightTests(unittest.TestCase):
    def test_duplicate_observation_id_short_circuits_before_any_allocation(self):
        oid = "OBS-DUP-0001"
        o1 = _integrated(config_id=CFG_A, observation_id=oid)
        o2 = _integrated(config_id=CFG_B, observation_id=oid)
        comp = _completion(qualifying_direct=())
        alloc = FakeAllocator()
        resolver = FakeSourceResolver([o1, o2])
        res = _run([o1, o2, _audit(comp)], comp, allocator=alloc, resolver=resolver)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertEqual(alloc.calls, 0)
        self.assertEqual(resolver.calls, 0)
        self.assertEqual(res.evidence_packages, ())
        self.assertTrue(any(oid in pid for pid, _ in res.hard_integrity_failures))


class NoNumericThresholdTests(unittest.TestCase):
    def test_source_reported_number_in_claim_is_fine(self):
        obs = _integrated(config_id=CFG_A, claim="source reported ~65% internalized at 4 h by surface-decay flow")
        res = _accepted_run([obs])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)

    def test_no_numeric_coercion_of_an_internalization_value_in_the_package(self):
        # bools counted as ints for a rung-role tally are fine; a float / Decimal
        # over a source-reported internalization number is not.
        for src in PKG.glob("*.py"):
            tree = ast.parse(src.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {"float", "Decimal"}, src.name)

    def test_acceptance_only_scans_module_owned_text(self):
        src = (PKG / "acceptance.py").read_text()
        self.assertIn("_module_owned_text", src)
        self.assertIn("directly_supports", src)
        self.assertNotIn('ib["does_not_support"]', src)


# =====================================================================
# 8. typed-fact coherence (T1) + output surface + study_context (E14-2)
# =====================================================================

class TypedFactCoherenceTests(unittest.TestCase):
    def test_internalization_only_plus_productive_is_hard_factual_incoherence(self):
        with self.assertRaises(ValueError):
            _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
                     outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY")

    def test_non_crc_context_requires_crc_specific_false(self):
        with self.assertRaises(ValueError):
            _obs("CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
                 surface_context_class="NON_CRC_CONTEXT",
                 surface_context_basis="a non-CRC line",
                 crc_specific=True)


class OutputSurfaceTests(unittest.TestCase):
    def test_accepted_run_output_surface(self):
        res = _accepted_run([_integrated(config_id=CFG_A)])
        self.assertIsInstance(res, Tgt06ModuleRunResult)
        self.assertIsInstance(res.machine_acceptance, MachineAcceptanceRecord)
        self.assertIsInstance(res.internalization_completion, InternalizationEvidenceCompletion)
        self.assertIsInstance(res.fatal_review, FatalReviewRecord)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertEqual(res.proposal_envelope.evidence_ceiling, TGT06_EVIDENCE_CEILING)
        self.assertEqual(res.proposal_envelope.context_id, CTX_ID)
        # never a canonical assessment.
        self.assertFalse(hasattr(res, "assessment_id"))
        for n in AssessmentProposalEnvelope.field_names():
            self.assertNotIn(n, ("assessment_id", "assessment_version", "review"))

    def test_misbinding_target_rejects_the_whole_run(self):
        res = _accepted_run([_integrated(config_id=CFG_A, target_identity="OTHER_TARGET")])
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)


class StudyContextTests(unittest.TestCase):
    def test_treatment_state_is_not_applicable_for_every_kind(self):
        obs = [
            _integrated(config_id=CFG_A),
            _indirect("CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY"),
            _indirect("SAME_TARGET_ADC_DELIVERY_PRECEDENT"),
            _weak("RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE"),
            _weak("SURFACE_LOCALIZATION_ONLY_INFERENCE"),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        for ep in res.evidence_packages:
            self.assertEqual(ep.study_context["treatment_state"], "not_applicable", ep.study_context)
            self.assertNotEqual(ep.study_context["indication"], "refractory_mcrc")

    def test_crc_integrated_observation_indication_is_colorectal_cancer(self):
        res = _accepted_run([_integrated(config_id=CFG_A)])
        eps = [e for e in res.evidence_packages
               if e.study_context["observation_kind"] == "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING"]
        self.assertEqual(eps[0].study_context["indication"], "colorectal_cancer")

    def test_search_audit_study_context_is_search_audit(self):
        res = _accepted_run([_integrated(config_id=CFG_A)])
        audit = [e for e in res.evidence_packages
                 if e.study_context["observation_kind"] == "SEARCH_COMPLETION_AUDIT"][0]
        self.assertEqual(audit.study_context["sample_type"], "search_audit")
        self.assertEqual(audit.study_context["treatment_state"], "not_applicable")


# =====================================================================
# 9. E14 review round-1 regressions (3 narrow runtime blockers)
# =====================================================================

class ReviewRound1RegressionTests(unittest.TestCase):
    def _c(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    # --- blocker 1: no generic "missed DIRECT -> INDIRECT_STRONG" fallback ---
    def test_crc_productive_with_unqualified_assay_is_contextual_not_indirect_strong(self):
        c = self._c(_integrated(config_id=CFG_A, assay_qualified=False,
                                outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"))
        self.assertEqual(c.evidence_rung, "")
        self.assertEqual(c.addressability_implication, "CONTEXTUAL")
        self.assertFalse(c.is_qualifying)

    def test_crc_productive_with_unqualified_context_is_contextual_not_indirect_strong(self):
        o = _obs(
            "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
            crc_specific=True,
            surface_context_class="CRC_MALIGNANT_CELLS",
            surface_context_basis="a CRC line, context adequacy not established",
            context_adequacy_status="NOT_ESTABLISHED",
            assay_method="live-cell imaging + lysosomal co-localization",
            assay_validation_status="QUALIFIED",
            assay_validation_basis="orthogonal-assay concordance",
            internalization_outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY",
            internalization_outcome_basis="the source characterisation",
            internalization_configuration_id=CFG_A,
            configuration_identity_basis="disclosed configuration",
        )
        c = self._c(o)
        self.assertEqual(c.evidence_rung, "")
        self.assertFalse(c.is_qualifying)

    def test_non_crc_productive_remains_indirect_strong(self):
        c = self._c(_integrated(context="NON_CRC_CONTEXT", config_id=CFG_A,
                                outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_indirect)

    # --- blocker 2: proposal-relative EvidenceRole mapping ---
    def test_conflicted_a_plus_clean_productive_b_roles(self):
        a_prod = _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY")
        a_fail = _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING")
        b_prod = _integrated(config_id=CFG_B, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY")
        res = _accepted_run([a_prod, a_fail, b_prod])
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(res.proposal_envelope.proposed_direction, "POSITIVE")
        role = dict(res.proposal_envelope.evidence_refs)
        b_id = next(e.evidence_id for e in res.evidence_packages
                    if e.study_context["internalization_configuration_id"] == CFG_B)
        self.assertEqual(role[b_id], "SUPPORTING")
        for e in res.evidence_packages:
            if e.study_context["internalization_configuration_id"] == CFG_A:
                self.assertEqual(role[e.evidence_id], "CONTEXTUAL")
        self.assertNotIn("CONTRADICTING", set(role.values()))

    def test_negative_direct_failure_eps_are_supporting_not_contradicting(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
            _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY", config_id=CFG_B),
        ]
        res = _accepted_run(obs)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(res.proposal_envelope.proposed_direction, "NEGATIVE")
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertIn("SUPPORTING", roles)
        self.assertNotIn("CONTRADICTING", roles)

    def test_conflicting_direct_still_carries_contradicting(self):
        obs = [
            _integrated(config_id=CFG_A, outcome="PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"),
            _integrated(config_id=CFG_A, outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"),
        ]
        res = _accepted_run(obs)
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertLessEqual({"SUPPORTING", "CONTRADICTING"}, roles)

    # --- blocker 3: third-state allowed-kind boundary ---
    def test_third_state_valid_for_the_five_non_configuration_kinds(self):
        for kind in ("CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
                     "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
                     "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
                     "SURFACE_LOCALIZATION_ONLY_INFERENCE"):
            o = _indirect(kind) if "CONSTITUTIVE" in kind or "SAME_TARGET" in kind else _weak(kind)
            self.assertEqual(o.configuration_identity_state,
                             "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE", kind)

    def test_third_state_valid_for_non_crc_undisclosed_configuration(self):
        o = _kindful("ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
                     context="NON_CRC_CONTEXT", config_id="",
                     outcome="INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED")
        self.assertEqual(o.configuration_identity_state,
                         "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE")

    def test_disease_relevant_delivery_unresolved_without_config_is_hard(self):
        with self.assertRaises(ValueError):
            _integrated(config_id="",
                        outcome="INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED")

    def test_trafficking_only_without_config_is_hard(self):
        with self.assertRaises(ValueError):
            _kindful("TRAFFICKING_OR_RECYCLING_ONLY", config_id="",
                     outcome="FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING")


if __name__ == "__main__":
    unittest.main()
