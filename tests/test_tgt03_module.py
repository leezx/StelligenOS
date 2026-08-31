"""Runtime Migration PR E10: MOD-TGT03 deterministic scientific core.

Synthetic, in-memory only -- no network, no real GEO / HPA / CPTAC / single-cell
/ spatial / paired-biopsy / resistance-model data, no persistence. The candidate
target is ``TARGET_A``; LOCAL persistence contexts are ``PERSIST_CTX_A`` /
``PERSIST_CTX_B`` / ``PERSIST_CTX_C``. No HER2 / TROP2 / real target names.

Covers the E10 acceptance scenarios (ChatGPT AI审核方案 E10-1..E10-8):

* the TGT-03 binding reconciliation (0.0.0 -> 1.0.0 with MIGRATION_PENDING still
  in force), the module boundary (ports only, no network / subprocess /
  persistence, no normalizer, no generic framework);
* the HARD identity / provenance / completion-consistency / qualification
  integrity gate -- rejects the WHOLE run, never degrades to an accepted UNKNOWN;
* exact canonical EvidencePackage reuse (no allocator call, parity drift HARD);
* the frozen Evidence-Ladder rung mapping (DIRECT only for a clinical-context
  protein observation with protein_measurement_validation_status == QUALIFIED + a
  QUALIFIED context adequacy + malignant-cell attribution and a matching
  clinical_context -- assay_method is an OPEN factual type, no closed whitelist;
  transcript / a resistance model never DIRECT; treatment-naive primary CRC /
  different tumor never a persistence claim);
* the pattern -> implication mapping incl. the E9 blocker-1 typed
  residual_target_presence_status branch (PRESENT -> SUPPORTING,
  UNRESOLVED -> CONTEXTUAL, no free-text parsing);
* the frozen E9 truth table (overall Strength is the HIGHEST qualifying class, no
  two-axis rule; the four mandatory search components are search-space
  completeness; NEGATIVE is reachable; support + oppose is CONFLICTING unless an
  explicit typed multi-context MIXED characterisation resolves it to a graded
  INCONCLUSIVE; a WEAK-only or incomplete landscape is INCONCLUSIVE / UNKNOWN,
  never INCONCLUSIVE / WEAK);
* the machine-local ``fatal_review`` review TRIGGER -- Route A (an auditable
  explicit reproducibility qualification, basis text NEVER parsed) OR Route B
  (>= 2 independent qualified persistence-context identities, NOT "> 2"); at most
  POTENTIAL_FATAL_PATTERN; never a canonical fatal flag / KILL / HOLD / Decision;
  only actionable on an accepted run; not a proposal-envelope field;
* the TGT-03-specific dedup deviation -- distinct persistence_context_id
  observations that share a (source_id, claim) both survive;
* the narrow deterministic critical-unknown mapping;
* the accepted-run output surface (EvidencePackages + one
  ClinicalPersistenceCompletion + fatal_review + proposal envelope +
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

from gate_modules.tgt03_treatment_metastatic_persistence import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    TGT03_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClinicalPersistenceCompletion,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedPersistenceObservation,
    PersistenceUnresolvedItem,
    Tgt03ModuleInput,
    Tgt03ModuleRunResult,
    run,
)
from gate_modules.tgt03_treatment_metastatic_persistence.classify import classify_observation

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt03_treatment_metastatic_persistence"
GATESET_YAML = REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"

TARGET_A = "TARGET_A"
CAND = "CAND-L04-000123"
CTX_ID = "CTX-CRC-REFRACTORY-MCRC"
INST = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CONTEXT_KEY = "REFRACTORY_MCRC"
AS_OF = "2026-08-30"
SCOPE = "GEO + HPA + CPTAC + paired-biopsy series + CRC resistance-model repositories"

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
        observations: list[NormalizedPersistenceObservation],
        *,
        unresolved: set[str] | None = None,
        mismatch: set[str] | None = None,
    ) -> None:
        unresolved = unresolved or set()
        mismatch = mismatch or set()
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

    def persistence_completion(self, **_):
        return self._completion


# --- observation factories ------------------------------------------------

def _protein(
    *,
    observation_id: str | None = None,
    kind: str = "REFRACTORY_OR_PRIOR_TREATED_PROTEIN",
    context: str = "PERSIST_CTX_A",
    context_ids: tuple[str, ...] = (),
    declared_multi_context: bool = False,
    pattern: str = "RETAINED",
    residual: str = "",
    validation: str = "QUALIFIED",
    adequacy: str = "QUALIFIED",
    attribution: str = "MALIGNANT",
    crc_specific: bool = True,
    reproducibility: str = "NOT_ESTABLISHED",
    assay: str = "validated CRC IHC panel v3",
    source_id: str | None = None,
    as_of: str = AS_OF,
) -> NormalizedPersistenceObservation:
    clinical_context = {
        "REFRACTORY_OR_PRIOR_TREATED_PROTEIN": "REFRACTORY_OR_PRIOR_TREATED",
        "METASTATIC_LESION_PROTEIN": "METASTATIC_CRC",
        "PAIRED_PRE_POST_PROTEIN": "PAIRED_PRE_POST",
    }[kind]
    loss_or_transient = pattern in ("NEAR_LOSS_OR_MARKED_LOSS", "TRANSIENT_OR_MINOR_DOWNREGULATION")
    return NormalizedPersistenceObservation(
        observation_id=observation_id or _next_obs("PROT"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        observation_kind=kind,
        molecular_layer="PROTEIN",
        assay_method=assay,
        protein_measurement_validation_status=validation,
        protein_measurement_validation_basis=(
            "assay validated on matched controls; scoring SOP disclosed"
            if validation == "QUALIFIED"
            else ""
        ),
        crc_specific=crc_specific,
        clinical_context=clinical_context,
        clinical_context_basis=(
            "explicitly a refractory / prior-treated or metastatic CRC series"
            if adequacy == "QUALIFIED"
            else ""
        ),
        context_adequacy_status=adequacy,
        context_adequacy_basis=(
            "treatment history and lesion site disclosed in the source"
            if adequacy == "QUALIFIED"
            else ""
        ),
        malignant_cell_attribution=attribution,
        malignant_attribution_basis=(
            "pathologist-annotated malignant epithelium" if attribution == "MALIGNANT" else ""
        ),
        persistence_pattern=pattern,
        persistence_pattern_basis=("SOURCE_REPORTED" if loss_or_transient else ""),
        residual_target_presence_status=residual,
        residual_target_presence_basis=(
            "source states staining remains present post-treatment" if residual == "PRESENT" else ""
        ),
        reproducibility_status=reproducibility,
        reproducibility_basis=(
            "one study establishing reproducibility across paired patients"
            if reproducibility == "QUALIFIED"
            else ""
        ),
        claim=f"{kind} {context or ','.join(context_ids)} {pattern} target protein",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or context}",
        locator="",
        retrieved_at=as_of,
        primary_or_repository_source_resolved=True,
        persistence_context_id=context,
        persistence_context_ids=context_ids,
        declared_multi_context_analysis=declared_multi_context,
    )


def _transcript(
    *,
    observation_id: str | None = None,
    kind: str = "TREATED_METASTATIC_TRANSCRIPT",
    context: str = "PERSIST_CTX_A",
    pattern: str = "RETAINED",
    residual: str = "",
    attribution: str = "MALIGNANT",
    crc_specific: bool = True,
    source_id: str | None = None,
) -> NormalizedPersistenceObservation:
    layer = "TRANSCRIPT" if kind == "TREATED_METASTATIC_TRANSCRIPT" else "PROTEIN"
    loss_or_transient = pattern in ("NEAR_LOSS_OR_MARKED_LOSS", "TRANSIENT_OR_MINOR_DOWNREGULATION")
    return NormalizedPersistenceObservation(
        observation_id=observation_id or _next_obs("TX"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind=kind,
        molecular_layer=layer,
        assay_method="scRNA-seq" if layer == "TRANSCRIPT" else "model IHC",
        protein_measurement_validation_status="",
        protein_measurement_validation_basis="",
        crc_specific=crc_specific,
        clinical_context="METASTATIC_CRC" if kind == "TREATED_METASTATIC_TRANSCRIPT" else "RESISTANCE_MODEL",
        clinical_context_basis="treated / metastatic CRC malignant compartment resolved",
        context_adequacy_status="QUALIFIED",
        context_adequacy_basis="treated / metastatic context disclosed",
        malignant_cell_attribution=attribution,
        malignant_attribution_basis=(
            "resolved to the malignant epithelial cluster" if attribution == "MALIGNANT" else ""
        ),
        persistence_pattern=pattern,
        persistence_pattern_basis=("SOURCE_REPORTED" if loss_or_transient else ""),
        residual_target_presence_status=residual,
        residual_target_presence_basis=(
            "source states expression remains present" if residual == "PRESENT" else ""
        ),
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        claim=f"{kind} {context} {pattern} in the treated / metastatic CRC compartment",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or context}",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        persistence_context_id=context,
    )


def _weak(
    *,
    observation_id: str | None = None,
    kind: str = "TREATMENT_NAIVE_PRIMARY",
    context: str = "PERSIST_CTX_A",
    source_id: str | None = None,
) -> NormalizedPersistenceObservation:
    return NormalizedPersistenceObservation(
        observation_id=observation_id or _next_obs("WEAK"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind=kind,
        molecular_layer="PROTEIN",
        assay_method="validated IHC (treatment-naive primary series)",
        protein_measurement_validation_status="QUALIFIED",
        protein_measurement_validation_basis="assay validated on controls",
        crc_specific=(kind == "TREATMENT_NAIVE_PRIMARY"),
        clinical_context=kind,
        clinical_context_basis="",
        context_adequacy_status="NOT_ESTABLISHED",
        context_adequacy_basis="",
        malignant_cell_attribution="MALIGNANT",
        malignant_attribution_basis="pathologist-annotated malignant epithelium",
        persistence_pattern="RETAINED",
        persistence_pattern_basis="",
        residual_target_presence_status="",
        residual_target_presence_basis="",
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        claim=f"{kind} {context} target protein present at baseline",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or context}",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        persistence_context_id=context,
    )


def _completion(
    *,
    attempted: bool = True,
    complete: bool = True,
    refractory_complete: bool | None = None,
    metastatic_complete: bool | None = None,
    paired_complete: bool | None = None,
    resistance_complete: bool | None = None,
    unresolved: tuple[PersistenceUnresolvedItem, ...] = (),
    qualifying_direct: tuple[str, ...] = (),
    qualifying_indirect: tuple[str, ...] = (),
    audit_obs_id: str | None = "OBS-AUDIT-0001",
    as_of: str = AS_OF,
) -> ClinicalPersistenceCompletion:
    r = complete if refractory_complete is None else refractory_complete
    m = complete if metastatic_complete is None else metastatic_complete
    p = complete if paired_complete is None else paired_complete
    x = complete if resistance_complete is None else resistance_complete
    return ClinicalPersistenceCompletion(
        attempted=attempted,
        landscape_as_of=as_of,
        search_scope=SCOPE if attempted else "",
        sources_searched=("GEO", "HPA", "CPTAC") if attempted else (),
        public_persistence_search_complete=complete,
        refractory_prior_treated_search_complete=r if attempted else False,
        metastatic_lesion_search_complete=m if attempted else False,
        paired_pre_post_search_complete=p if attempted else False,
        resistance_model_search_complete=x if attempted else False,
        unresolved_items=unresolved,
        qualifying_direct_persistence_context_ids=qualifying_direct,
        qualifying_indirect_persistence_context_ids=qualifying_indirect,
        audit_observation_id=(audit_obs_id or "") if attempted else "",
    )


def _audit(
    completion: ClinicalPersistenceCompletion,
    *,
    observation_id: str | None = None,
    source_id: str | None = None,
    override: dict | None = None,
) -> NormalizedPersistenceObservation:
    fields = dict(
        observation_id=observation_id or completion.audit_observation_id,
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=completion.landscape_as_of,
        observation_kind="SEARCH_COMPLETION_AUDIT",
        molecular_layer="",
        assay_method="SEARCH_AUDIT",
        protein_measurement_validation_status="",
        protein_measurement_validation_basis="",
        crc_specific=True,
        clinical_context="",
        clinical_context_basis="",
        context_adequacy_status="NOT_ESTABLISHED",
        context_adequacy_basis="",
        malignant_cell_attribution="UNRESOLVED",
        malignant_attribution_basis="",
        persistence_pattern="",
        persistence_pattern_basis="",
        residual_target_presence_status="",
        residual_target_presence_basis="",
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        claim="the declared public clinical-persistence search is complete",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier="GSE-AUDIT",
        locator="",
        retrieved_at=completion.landscape_as_of,
        primary_or_repository_source_resolved=True,
        audit_search_scope=completion.search_scope,
        audit_sources_searched=completion.sources_searched,
        audit_landscape_as_of=completion.landscape_as_of,
        audit_public_persistence_search_complete=completion.public_persistence_search_complete,
        audit_refractory_prior_treated_search_complete=completion.refractory_prior_treated_search_complete,
        audit_metastatic_lesion_search_complete=completion.metastatic_lesion_search_complete,
        audit_paired_pre_post_search_complete=completion.paired_pre_post_search_complete,
        audit_resistance_model_search_complete=completion.resistance_model_search_complete,
        audit_unresolved_item_keys=tuple(i.snapshot_key for i in completion.unresolved_items),
        audit_qualifying_direct_persistence_context_ids=completion.qualifying_direct_persistence_context_ids,
        audit_qualifying_indirect_persistence_context_ids=completion.qualifying_indirect_persistence_context_ids,
    )
    if override:
        fields.update(override)
    return NormalizedPersistenceObservation(**fields)


def _input(*, target: str = TARGET_A, as_of: str = AS_OF, existing: tuple[str, ...] = ()):
    return Tgt03ModuleInput(
        candidate_id=CAND,
        candidate_name="synthetic ADC candidate",
        target_identity=target,
        instantiation_id=INST,
        context_id=CTX_ID,
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-03",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-E10-TEST",
        code_commit="deadbeef",
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        persistence_search_scope=SCOPE,
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
    module_input: Tgt03ModuleInput | None = None,
) -> Tgt03ModuleRunResult:
    observations = list(observations)
    return run(
        module_input or _input(),
        provider=FakeProvider(observations, completion),
        evidence_id_allocator=allocator or FakeAllocator(),
        source_resolver=FakeSourceResolver(observations, unresolved=unresolved, mismatch=mismatch),
        evidence_library=FakeEvidenceLibrary(library),
    )


def _pair(res: Tgt03ModuleRunResult):
    pe = res.proposal_envelope
    return None if pe is None else (pe.proposed_direction, pe.proposed_strength)


# =========================================================================


class BindingAndBoundaryTests(unittest.TestCase):
    def test_binding_is_one_zero_zero_with_migration_pending(self):
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-03"], "1.0.0")
        gs = yaml.safe_load(GATESET_YAML.read_text())
        binding = next(
            b for b in gs["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-03"
        )
        self.assertEqual(binding["primary_module_version"], "1.0.0")
        self.assertEqual(binding["primary_module_id"], "MOD-TGT03")
        self.assertIn("per_gate_primary_modules", gs["migration"]["deferred"])

    def test_other_modules_untouched(self):
        for g in ("TGT-01", "TGT-02", "TGT-05", "TGT-08"):
            self.assertEqual(BUILT_MODULE_VERSIONS[g], "1.0.0")
        for g in ("TGT-04", "TGT-06", "TGT-07"):
            self.assertNotIn(g, BUILT_MODULE_VERSIONS)

    def test_package_has_the_eleven_expected_files(self):
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((PKG / f).is_file(), f)
        self.assertFalse((PKG / "normalizer.py").exists(), "E10 has NO normalizer in the package")

    def test_module_yaml_identity_and_conservative_flags(self):
        manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.assertEqual(manifest["module_id"], "MOD-TGT03")
        self.assertEqual(manifest["module_version"], "1.0.0")
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e10")
        for name, value in manifest["boundary_flags"].items():
            self.assertFalse(value, name)

    def test_no_network_subprocess_or_persistence_import_in_the_package(self):
        banned = {"socket", "http", "urllib", "requests", "subprocess", "sqlite3", "pathlib", "os"}
        for py in PKG.glob("*.py"):
            tree = ast.parse(py.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(alias.name.split(".")[0], banned, f"{py.name}: {alias.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], banned, f"{py.name}: {node.module}")

    def test_kernel_never_imports_the_module(self):
        src = REPO_ROOT / "src"
        for py in src.rglob("*.py"):
            text = py.read_text()
            self.assertNotIn("import gate_modules", text, str(py))
            self.assertNotIn("from gate_modules", text, str(py))

    def test_headline_invariants_are_at_the_top_of_contracts_py(self):
        head = (PKG / "contracts.py").read_text()[:2000].lower()
        self.assertIn("baseline expression is not persistence", head)
        self.assertIn("a single observation is evidence, never a direction", head)
        self.assertIn("not fatal and not kill", head)
        self.assertIn("route a", head)
        self.assertIn("route b", head)


class InputContractTests(unittest.TestCase):
    def test_landscape_as_of_must_be_an_iso_date(self):
        with self.assertRaises(ValueError):
            _input(as_of="soon")

    def test_non_canonical_context_id_is_rejected(self):
        with self.assertRaises(ValueError):
            Tgt03ModuleInput(
                candidate_id=CAND, candidate_name="x", target_identity=TARGET_A,
                instantiation_id=INST, context_id="CTX-OTHER", context_version=1,
                gateset_id="ADC_TARGET_GATESET", gateset_version="1.0", gate_id="TGT-03",
                gate_version="1.0", evidence_regime="PUBLIC_ONLY", run_id="R", code_commit="",
                context_key=CONTEXT_KEY, landscape_as_of=AS_OF, persistence_search_scope=SCOPE,
            )

    def test_evidence_regime_must_be_public_only(self):
        with self.assertRaises(ValueError):
            Tgt03ModuleInput(
                candidate_id=CAND, candidate_name="x", target_identity=TARGET_A,
                instantiation_id=INST, context_id=CTX_ID, context_version=1,
                gateset_id="ADC_TARGET_GATESET", gateset_version="1.0", gate_id="TGT-03",
                gate_version="1.0", evidence_regime="PUBLIC_HYBRID", run_id="R", code_commit="",
                context_key=CONTEXT_KEY, landscape_as_of=AS_OF, persistence_search_scope=SCOPE,
            )

    def test_wrong_gate_id_rejected(self):
        with self.assertRaises(ValueError):
            Tgt03ModuleInput(
                candidate_id=CAND, candidate_name="x", target_identity=TARGET_A,
                instantiation_id=INST, context_id=CTX_ID, context_version=1,
                gateset_id="ADC_TARGET_GATESET", gateset_version="1.0", gate_id="TGT-02",
                gate_version="1.0", evidence_regime="PUBLIC_ONLY", run_id="R", code_commit="",
                context_key=CONTEXT_KEY, landscape_as_of=AS_OF, persistence_search_scope=SCOPE,
            )


class IdentityProvenanceIntegrityTests(unittest.TestCase):
    def _completed(self, obs, comp):
        return _run([*obs, _audit(comp)], comp)

    def test_wrong_target_is_a_hard_run_rejection(self):
        o = _protein()
        comp = _completion()
        res = _run([o, _audit(comp)], comp, module_input=_input(target="OTHER_TARGET"))
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)

    def test_unresolved_source_is_a_hard_run_rejection(self):
        o = _protein()
        comp = _completion()
        res = _run([o, _audit(comp)], comp, unresolved={o.source_id})
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_canonical_source_metadata_drift_is_a_hard_run_rejection(self):
        o = _protein()
        comp = _completion()
        res = _run([o, _audit(comp)], comp, mismatch={o.source_id})
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_observation_context_key_drift_is_a_hard_run_rejection(self):
        comp = _completion()
        o = _protein()
        object.__setattr__(o, "context_key", "SOME_OTHER_CONTEXT")
        res = _run([o, _audit(comp)], comp)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_completion_search_scope_drift_is_a_hard_run_rejection(self):
        comp = _completion()
        object.__setattr__(comp, "search_scope", "a different scope")
        res = _run([_protein(), _audit(comp)], comp)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_hard_failure_is_never_degraded_to_accepted_unknown(self):
        o = _protein()
        comp = _completion()
        res = _run([o, _audit(comp)], comp, unresolved={o.source_id})
        self.assertIsNone(res.proposal_envelope)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_duplicate_observation_id_is_a_hard_run_rejection(self):
        comp = _completion()
        a = _protein(observation_id="OBS-DUP-1")
        b = _protein(observation_id="OBS-DUP-1", context="PERSIST_CTX_B")
        res = _run([a, b, _audit(comp)], comp)
        self.assertTrue(any("appears 2 times" in why for _, why in res.hard_integrity_failures))
        self.assertIsNone(res.proposal_envelope)


class ExactReuseTests(unittest.TestCase):
    def _canonical_package(self, o, evidence_id="EP-00009000"):
        res = _run([o, _audit(_completion())], _completion(), allocator=FakeAllocator(9000))
        return next(p for p in res.evidence_packages if p.study_context["observation_id"] == o.observation_id)

    def test_existing_canonical_package_is_reused_without_an_allocator_call(self):
        o = _protein(observation_id="OBS-REUSE-1")
        pkg = self._canonical_package(o)
        alloc = FakeAllocator(5000)
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([o, _audit(comp)], comp, library={o.observation_id: pkg}, allocator=alloc)
        self.assertIn(pkg.evidence_id, res.reused_evidence_ids)
        # the audit EP still needs one allocation; the reused protein EP does not.
        self.assertEqual(alloc.calls, 1)

    def test_classification_driving_drift_on_a_reused_package_is_hard(self):
        o = _protein(observation_id="OBS-REUSE-2")
        pkg = self._canonical_package(o)
        drifted = _protein(observation_id="OBS-REUSE-2", pattern="NEAR_LOSS_OR_MARKED_LOSS")
        comp = _completion()
        res = _run([drifted, _audit(comp)], comp, library={drifted.observation_id: pkg})
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)


class RungClassificationTests(unittest.TestCase):
    def _classify(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_qualified_clinical_context_protein_is_direct(self):
        c = self._classify(_protein())
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_for_direct)

    def test_metastatic_lesion_protein_is_direct(self):
        c = self._classify(_protein(kind="METASTATIC_LESION_PROTEIN", context="PERSIST_CTX_B"))
        self.assertEqual(c.evidence_rung, "DIRECT")

    def test_protein_without_qualified_validation_is_not_direct(self):
        c = self._classify(_protein(validation="NOT_ESTABLISHED"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")
        self.assertEqual(c.persistence_implication, "CONTEXTUAL")

    def test_protein_without_qualified_context_adequacy_is_not_direct(self):
        c = self._classify(_protein(adequacy="NOT_ESTABLISHED"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")

    def test_protein_without_malignant_attribution_is_not_direct(self):
        c = self._classify(_protein(attribution="UNRESOLVED"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")

    def test_assay_method_is_an_open_factual_type_not_a_whitelist(self):
        # any assay_method string qualifies for DIRECT as long as the CLOSED
        # validation predicate is QUALIFIED.
        c = self._classify(_protein(assay="a novel but reliable spatial proteomics method"))
        self.assertEqual(c.evidence_rung, "DIRECT")

    def test_treated_metastatic_transcript_is_indirect_strong_never_direct(self):
        c = self._classify(_transcript())
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_for_indirect)

    def test_resistance_model_is_indirect_strong_even_measuring_protein(self):
        c = self._classify(_transcript(kind="RESISTANCE_MODEL"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")

    def test_treatment_naive_primary_is_weak(self):
        c = self._classify(_weak())
        self.assertEqual(c.evidence_rung, "WEAK")
        self.assertEqual(c.persistence_implication, "CONTEXTUAL")

    def test_different_tumor_type_is_weak(self):
        c = self._classify(_weak(kind="DIFFERENT_TUMOR_TYPE"))
        self.assertEqual(c.evidence_rung, "WEAK")

    def test_search_completion_audit_is_contextual_no_rung(self):
        c = self._classify(_audit(_completion()))
        self.assertEqual(c.evidence_rung, "")
        self.assertEqual(c.persistence_implication, "CONTEXTUAL")


class PatternImplicationTests(unittest.TestCase):
    def _classify(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_retained_supports_persistence(self):
        self.assertEqual(self._classify(_protein(pattern="RETAINED")).persistence_implication,
                         "SUPPORTS_PERSISTENCE")

    def test_near_or_marked_loss_opposes_persistence(self):
        self.assertEqual(
            self._classify(_protein(pattern="NEAR_LOSS_OR_MARKED_LOSS")).persistence_implication,
            "OPPOSES_PERSISTENCE",
        )

    def test_transient_minor_with_residual_present_supports_persistence(self):
        c = self._classify(_protein(pattern="TRANSIENT_OR_MINOR_DOWNREGULATION", residual="PRESENT"))
        self.assertEqual(c.persistence_implication, "SUPPORTS_PERSISTENCE")

    def test_transient_minor_with_residual_unresolved_is_contextual(self):
        c = self._classify(_protein(pattern="TRANSIENT_OR_MINOR_DOWNREGULATION", residual="UNRESOLVED"))
        self.assertEqual(c.persistence_implication, "CONTEXTUAL")

    def test_transient_minor_without_a_typed_residual_status_is_invalid(self):
        with self.assertRaises(ValueError):
            _protein(pattern="TRANSIENT_OR_MINOR_DOWNREGULATION", residual="")

    def test_residual_status_without_transient_pattern_is_drift(self):
        with self.assertRaises(ValueError):
            _protein(pattern="RETAINED", residual="PRESENT")

    def test_mixed_or_unresolved_is_contextual(self):
        c = self._classify(_protein(pattern="MIXED_OR_UNRESOLVED"))
        self.assertEqual(c.persistence_implication, "CONTEXTUAL")


class AggregateTruthTableTests(unittest.TestCase):
    def test_completed_direct_retained_is_positive_direct(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))

    def test_completed_direct_loss_is_negative_direct(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="NEAR_LOSS_OR_MARKED_LOSS"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("NEGATIVE", "DIRECT"))

    def test_completed_transcript_retained_is_positive_indirect_strong(self):
        comp = _completion(qualifying_indirect=("PERSIST_CTX_A",))
        res = _run([_transcript(pattern="RETAINED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_completed_transcript_loss_is_negative_indirect_strong(self):
        comp = _completion(qualifying_indirect=("PERSIST_CTX_A",))
        res = _run([_transcript(pattern="NEAR_LOSS_OR_MARKED_LOSS"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("NEGATIVE", "INDIRECT_STRONG"))

    def test_transcript_alone_never_reaches_direct(self):
        comp = _completion(qualifying_indirect=("PERSIST_CTX_A",))
        res = _run([_transcript(pattern="RETAINED"), _audit(comp)], comp)
        self.assertEqual(res.proposal_envelope.proposed_strength, "INDIRECT_STRONG")

    def test_support_and_oppose_with_no_resolver_is_conflicting(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A", "PERSIST_CTX_B"))
        res = _run(
            [
                _protein(pattern="RETAINED", context="PERSIST_CTX_A"),
                _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_B"),
                _audit(comp),
            ],
            comp,
        )
        self.assertEqual(res.proposal_envelope.proposed_direction, "CONFLICTING")

    def test_explicit_multi_context_mixed_characterisation_is_graded_inconclusive(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A", "PERSIST_CTX_B", "PERSIST_CTX_C"))
        resolver = _protein(
            pattern="MIXED_OR_UNRESOLVED",
            context="",
            context_ids=("PERSIST_CTX_A", "PERSIST_CTX_B", "PERSIST_CTX_C"),
            declared_multi_context=True,
        )
        res = _run(
            [
                _protein(pattern="RETAINED", context="PERSIST_CTX_A"),
                _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_B"),
                resolver,
                _audit(comp),
            ],
            comp,
        )
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))

    def test_weak_only_completed_landscape_is_inconclusive_unknown_not_weak(self):
        comp = _completion()
        res = _run([_weak(), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_no_inconclusive_weak_pair_is_legal(self):
        self.assertNotIn(("INCONCLUSIVE", "WEAK"), LEGAL_DIRECTION_STRENGTH_PAIRS)

    def test_incomplete_four_component_search_is_unknown(self):
        comp = _completion(complete=False, refractory_complete=True, metastatic_complete=False)
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_one_pretty_paired_study_with_other_components_incomplete_is_unknown(self):
        comp = _completion(complete=False, paired_complete=True)
        res = _run([_protein(kind="PAIRED_PRE_POST_PROTEIN", pattern="RETAINED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_overall_strength_is_the_highest_qualifying_class_no_two_axis_rule(self):
        comp = _completion(
            qualifying_direct=("PERSIST_CTX_A",), qualifying_indirect=("PERSIST_CTX_B",)
        )
        res = _run(
            [
                _protein(pattern="RETAINED", context="PERSIST_CTX_A"),
                _transcript(pattern="RETAINED", context="PERSIST_CTX_B"),
                _audit(comp),
            ],
            comp,
        )
        self.assertEqual(res.proposal_envelope.proposed_strength, "DIRECT")


class CompletionInvariantTests(unittest.TestCase):
    def test_umbrella_true_while_a_component_false_is_hard(self):
        comp = ClinicalPersistenceCompletion(
            attempted=True, landscape_as_of=AS_OF, search_scope=SCOPE,
            sources_searched=("GEO",),
            public_persistence_search_complete=True,
            refractory_prior_treated_search_complete=True,
            metastatic_lesion_search_complete=False,
            paired_pre_post_search_complete=True,
            resistance_model_search_complete=True,
            unresolved_items=(), qualifying_direct_persistence_context_ids=(),
            qualifying_indirect_persistence_context_ids=(),
            audit_observation_id="OBS-AUDIT-0001",
        )
        res = _run([_protein(), _audit(comp)], comp)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_complete_landscape_with_no_audit_is_hard(self):
        comp = _completion()
        res = _run([_protein()], comp)  # no audit observation
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_two_audits_is_hard(self):
        comp = _completion()
        res = _run([_protein(), _audit(comp), _audit(comp, source_id=_next_src())], comp)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_audit_snapshot_drift_is_hard(self):
        comp = _completion()
        bad_audit = _audit(comp, override={"audit_refractory_prior_treated_search_complete": False})
        res = _run([_protein(), bad_audit], comp)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_qualifying_direct_context_set_drift_is_hard(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_ZZZ",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_snapshot_consistent_audit_passes(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted)

    def test_single_loss_observation_incomplete_landscape_is_accepted_unknown_not_rejected(self):
        comp = _completion(complete=False, refractory_complete=True)
        res = _run([_protein(pattern="NEAR_LOSS_OR_MARKED_LOSS"), _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertFalse(res.hard_integrity_failures)


class FatalReviewTests(unittest.TestCase):
    def _fatal_run(self, observations, comp):
        return _run([*observations, _audit(comp)], comp)

    def test_single_loss_no_route_a_or_b_raises_no_fatal_review(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = self._fatal_run([_protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A")], comp)
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "")

    def test_route_a_single_qualified_reproducible_direct_loss_is_potential_fatal(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        o = _protein(
            pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A", reproducibility="QUALIFIED"
        )
        res = self._fatal_run([o], comp)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "POTENTIAL_FATAL_PATTERN")
        self.assertTrue(res.fatal_review.reproducibility_basis_refs)

    def test_route_b_two_distinct_persistence_contexts_is_potential_fatal(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A", "PERSIST_CTX_B"))
        res = self._fatal_run(
            [
                _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A"),
                _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_B"),
            ],
            comp,
        )
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.reproducibility_basis_refs, ())
        self.assertEqual(len(set(res.fatal_review.persistence_context_ids)), 2)

    def test_route_b_one_context_two_observations_is_no_trigger(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = self._fatal_run(
            [
                _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A"),
                _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A",
                         source_id=_next_src()),
            ],
            comp,
        )
        self.assertFalse(res.fatal_review.required)

    def test_transcript_loss_across_two_contexts_raises_no_fatal_trigger(self):
        comp = _completion(qualifying_indirect=("PERSIST_CTX_A", "PERSIST_CTX_B"))
        res = self._fatal_run(
            [
                _transcript(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A"),
                _transcript(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_B"),
            ],
            comp,
        )
        self.assertFalse(res.fatal_review.required)

    def test_transient_minor_never_contributes_to_fatal_review(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A", "PERSIST_CTX_B"))
        res = self._fatal_run(
            [
                _protein(pattern="TRANSIENT_OR_MINOR_DOWNREGULATION", residual="UNRESOLVED",
                         context="PERSIST_CTX_A"),
                _protein(pattern="TRANSIENT_OR_MINOR_DOWNREGULATION", residual="UNRESOLVED",
                         context="PERSIST_CTX_B"),
            ],
            comp,
        )
        self.assertFalse(res.fatal_review.required)

    def test_trigger_is_only_surfaced_on_an_accepted_run(self):
        # a HARD failure alongside a would-be fatal pattern -> fatal_review cleared.
        comp = _completion(qualifying_direct=("PERSIST_CTX_A", "PERSIST_CTX_B"))
        o1 = _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A")
        o2 = _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_B")
        res = _run([o1, o2, _audit(comp)], comp, unresolved={o1.source_id})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertFalse(res.fatal_review.required)

    def test_fatal_review_status_is_never_more_than_potential_fatal_pattern(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        o = _protein(pattern="NEAR_LOSS_OR_MARKED_LOSS", context="PERSIST_CTX_A",
                     reproducibility="QUALIFIED")
        res = self._fatal_run([o], comp)
        self.assertIn(res.fatal_review.status, ("", "POTENTIAL_FATAL_PATTERN"))

    def test_fatal_review_is_not_a_proposal_envelope_field(self):
        for name in AssessmentProposalEnvelope.field_names():
            self.assertNotIn("fatal", name)
            self.assertNotIn("review", name)


class CriticalUnknownTests(unittest.TestCase):
    def test_incomplete_public_search_is_public_resolvable(self):
        comp = _completion(
            complete=False,
            refractory_complete=True,
            unresolved=(PersistenceUnresolvedItem("metastatic lesion cohort not yet fetched",
                                                  "KNOWN_PUBLIC_NOT_YET_RESOLVED"),),
        )
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("PUBLIC_RESOLVABLE", resolutions)
        self.assertNotIn("EXPERIMENT_REQUIRED", resolutions)

    def test_access_or_annotation_blocked_is_currently_unresolvable(self):
        comp = _completion(
            complete=False,
            unresolved=(PersistenceUnresolvedItem("resistance-model dataset access-restricted",
                                                  "ACCESS_OR_ANNOTATION_BLOCKED"),),
        )
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("CURRENTLY_UNRESOLVABLE", resolutions)
        self.assertNotIn("EXPERIMENT_REQUIRED", resolutions)

    def test_complete_indirect_only_directional_needs_experiment_required_protein_confirmation(self):
        comp = _completion(qualifying_indirect=("PERSIST_CTX_A",))
        res = _run([_transcript(pattern="RETAINED"), _audit(comp)], comp)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("EXPERIMENT_REQUIRED", resolutions)

    def test_complete_weak_only_is_unknown_plus_experiment_required(self):
        comp = _completion()
        res = _run([_weak(), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("EXPERIMENT_REQUIRED", resolutions)

    def test_graded_direct_does_not_invent_experiment_required(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertNotIn("EXPERIMENT_REQUIRED", resolutions)


class DedupDeviationTests(unittest.TestCase):
    def test_same_source_and_claim_different_persistence_contexts_both_survive(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A", "PERSIST_CTX_B"))
        src = _next_src()
        a = _protein(pattern="RETAINED", context="PERSIST_CTX_A", source_id=src)
        b = _protein(pattern="RETAINED", context="PERSIST_CTX_B", source_id=src)
        # identical source_id + provenance + claim, only the local persistence
        # context differs -> both are distinct scientific observations.
        object.__setattr__(b, "claim", a.claim)
        object.__setattr__(b, "source_identifier", a.source_identifier)
        object.__setattr__(b, "locator", a.locator)
        res = _run([a, b, _audit(comp)], comp)
        emitted_obs = {p.study_context["observation_id"] for p in res.evidence_packages}
        self.assertIn(a.observation_id, emitted_obs)
        self.assertIn(b.observation_id, emitted_obs)
        self.assertTrue(res.machine_acceptance.accepted)

    def test_true_duplicate_same_everything_is_dropped(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        src = _next_src()
        a = _protein(pattern="RETAINED", context="PERSIST_CTX_A", source_id=src)
        b = _protein(pattern="RETAINED", context="PERSIST_CTX_A", source_id=src)
        object.__setattr__(b, "claim", a.claim)
        object.__setattr__(b, "source_identifier", a.source_identifier)
        object.__setattr__(b, "locator", a.locator)
        res = _run([a, b, _audit(comp)], comp)
        dropped = [oid for oid, why in res.rejected_records if "duplicate" in why]
        self.assertEqual(len(dropped), 1)

    def test_audit_ep_is_never_a_dedup_loser(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        audit = _audit(comp)
        # a protein observation sharing the audit's source_id + provenance +
        # claim must not push the audit EP out.
        clash = _protein(pattern="RETAINED", context="PERSIST_CTX_A", source_id=audit.source_id)
        object.__setattr__(clash, "claim", audit.claim)
        object.__setattr__(clash, "source_identifier", audit.source_identifier)
        object.__setattr__(clash, "locator", audit.locator)
        res = _run([clash, audit], comp)
        audit_eps = [p for p in res.evidence_packages
                     if p.study_context["observation_kind"] == "SEARCH_COMPLETION_AUDIT"]
        self.assertEqual(len(audit_eps), 1)
        self.assertTrue(res.machine_acceptance.accepted)


class ForbiddenOutputTests(unittest.TestCase):
    def test_module_never_constructs_a_candidate_gate_assessment(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertNotIn("review", AssessmentProposalEnvelope.field_names())
        self.assertNotIn("assessment_id", AssessmentProposalEnvelope.field_names())

    def test_output_surface_shape(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertIsInstance(res, Tgt03ModuleRunResult)
        self.assertIsInstance(res.persistence_completion, ClinicalPersistenceCompletion)
        self.assertIsInstance(res.fatal_review, FatalReviewRecord)
        self.assertIsInstance(res.machine_acceptance, MachineAcceptanceRecord)

    def test_evidence_package_is_gate_neutral(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        for p in res.evidence_packages:
            blob = " ".join(str(v) for v in p.interpretation_boundary["directly_supports"]).lower()
            self.assertNotIn("passes tgt-03", blob)
            self.assertNotIn("persistence established", blob)
            self.assertNotIn("should be killed", blob)

    def test_proposal_envelope_carries_the_canonical_context_id(self):
        comp = _completion(qualifying_direct=("PERSIST_CTX_A",))
        res = _run([_protein(pattern="RETAINED"), _audit(comp)], comp)
        self.assertEqual(res.proposal_envelope.context_id, CTX_ID)
        self.assertEqual(res.proposal_envelope.evidence_ceiling, TGT03_EVIDENCE_CEILING)


if __name__ == "__main__":
    unittest.main()
