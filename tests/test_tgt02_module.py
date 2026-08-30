"""Runtime Migration PR E8: MOD-TGT02 deterministic scientific core.

Synthetic, in-memory only -- no network, no real GEO / HPA / CPTAC / single-cell
/ spatial / TMA data, no persistence. The candidate target is ``TARGET_A``;
cohorts are ``CRC_COHORT_A`` / ``CRC_COHORT_B`` / ``CRC_COHORT_C``;
non-malignant compartments are ``STROMA`` / ``IMMUNE``. No HER2 / TROP2 / real
target names.

Covers the E8 acceptance scenarios (ChatGPT AI审核方案 E8-1..E8-8):

* the TGT-02 binding reconciliation (0.0.0 -> 1.0.0 with MIGRATION_PENDING still
  in force), the module boundary (ports only, no network / subprocess /
  persistence, no generic framework);
* the HARD identity / provenance / completion-consistency / qualification
  integrity gate (candidate<->target misbinding, unresolved source,
  canonical-source drift, incompatible canonical EvidencePackage, completion
  umbrella-vs-component contradiction, missing / duplicate / drifted
  SEARCH_COMPLETION_AUDIT, qualifying cohort-set drift) -- rejects the WHOLE run
  and never degrades to an accepted UNKNOWN;
* exact canonical EvidencePackage reuse (no allocator call, parity drift HARD);
* the frozen Evidence-Ladder rung mapping (DIRECT only for a validated protein
  assay in a QUALIFIED CRC cohort with malignant-cell attribution;
  INDIRECT_STRONG for qualifying sc / spatial / TMA concordance; WEAK for bulk /
  pan-cancer) and the hard scientific locks (transcript never DIRECT; protein
  without malignant attribution never DIRECT; stroma / immune is CONTEXTUAL not
  a HARD failure; matched normal-tumor is context only; cohort_n never changes a
  rung);
* the frozen E7 truth table (overall Strength is the HIGHEST qualifying class,
  no two-axis rule; NEGATIVE is reachable; a valid audited multi-cohort
  RARE_HIGHLY_HETEROGENEOUS finding is NEGATIVE not CONFLICTING; a graded
  INCONCLUSIVE is distinct from INCONCLUSIVE / UNKNOWN; a WEAK-only or
  incomplete landscape is INCONCLUSIVE / UNKNOWN, never INCONCLUSIVE / WEAK; a
  single positive / negative cohort is never a completed population-level
  answer);
* the machine-local ``fatal_review`` review TRIGGER (required only for
  DIRECT-class protein cohorts across AT LEAST TWO -- not "> 2" -- independent
  cohort identities on a completed audited landscape; at most
  POTENTIAL_FATAL_PATTERN; never a canonical fatal flag / KILL / HOLD /
  Decision; only actionable on an accepted run; not a proposal-envelope field);
* the narrow deterministic critical-unknown mapping (incomplete search ->
  PUBLIC_RESOLVABLE; access / annotation blocked -> CURRENTLY_UNRESOLVABLE;
  complete + IS-only directional -> EXPERIMENT_REQUIRED protein confirmation;
  complete + WEAK-only -> INCONCLUSIVE / UNKNOWN + EXPERIMENT_REQUIRED);
* the accepted-run output surface (EvidencePackages + one CrcCohortCoverageCompletion
  + fatal_review + proposal envelope + MachineAcceptanceRecord, never a
  CandidateGateAssessment / HUMAN_APPROVED / Decision).
"""

from __future__ import annotations

import ast
import dataclasses
import itertools
import unittest
from pathlib import Path

import yaml

from src.objects.crc_adc_target_gateset import BUILT_MODULE_VERSIONS
from src.objects.decision_model import CandidateGateAssessment, EvidencePackage

from gate_modules.tgt02_indication_specific_malignant_cell_coverage import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    TGT02_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    CoverageUnresolvedItem,
    CrcCohortCoverageCompletion,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedCoverageObservation,
    Tgt02ModuleInput,
    Tgt02ModuleRunResult,
    run,
)
from gate_modules.tgt02_indication_specific_malignant_cell_coverage.classify import (
    classify_observation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt02_indication_specific_malignant_cell_coverage"
GATESET_YAML = REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"

TARGET_A = "TARGET_A"
CAND = "CAND-L04-000123"
CTX_ID = "CTX-CRC-REFRACTORY"
INST = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CONTEXT_KEY = "REFRACTORY_MCRC"
AS_OF = "2026-08-30"
SCOPE = "GEO + HPA + CPTAC + single-cell CRC atlases + CRC TMA series"

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
        observations: list[NormalizedCoverageObservation],
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

    def coverage_completion(self, **_):
        return self._completion


# --- observation factories ------------------------------------------------

_NEG_PATTERNS = ("ABSENT", "RARE_HIGHLY_HETEROGENEOUS")


def _protein(
    *,
    observation_id: str | None = None,
    cohort: str = "CRC_COHORT_A",
    cohort_ids: tuple[str, ...] = (),
    pattern: str = "PRESENT_CONSISTENT",
    assay: str = "VALIDATED_IHC",
    attribution: str = "MALIGNANT",
    adequacy: str = "QUALIFIED",
    crc_specific: bool = True,
    cohort_n: int = 0,
    declared_multi_cohort: bool = False,
    source_id: str | None = None,
    as_of: str = AS_OF,
) -> NormalizedCoverageObservation:
    neg = pattern in _NEG_PATTERNS
    return NormalizedCoverageObservation(
        observation_id=observation_id or _next_obs("PROT"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        observation_kind="PROTEIN_COHORT",
        molecular_layer="PROTEIN",
        assay_method=assay,
        crc_specific=crc_specific,
        malignant_cell_attribution=attribution,
        malignant_attribution_basis=(
            "pathologist-annotated malignant epithelium" if attribution == "MALIGNANT" else ""
        ),
        cohort_adequacy_status=adequacy,
        cohort_adequacy_basis=(
            "powered refractory mCRC cohort, sample plan stated" if adequacy == "QUALIFIED" else ""
        ),
        expression_pattern=pattern,
        expression_pattern_basis=("SOURCE_REPORTED" if neg else ""),
        expression_pattern_basis_detail=("reported in the source results table" if neg else ""),
        claim=f"cohort {cohort or ','.join(cohort_ids)} {assay} {pattern} target protein",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or cohort}",
        locator="",
        retrieved_at=as_of,
        primary_or_repository_source_resolved=True,
        cohort_id=cohort,
        cohort_ids=cohort_ids,
        cohort_n=cohort_n,
        declared_multi_cohort_analysis=declared_multi_cohort,
    )


def _sc(
    *,
    observation_id: str | None = None,
    cohort: str = "CRC_COHORT_A",
    pattern: str = "PRESENT_CONSISTENT",
    assay: str = "SINGLE_CELL_RNA",
    attribution: str = "MALIGNANT",
    crc_specific: bool = True,
    kind: str = "MALIGNANT_SC_SPATIAL",
    source_id: str | None = None,
) -> NormalizedCoverageObservation:
    neg = pattern in _NEG_PATTERNS
    layer = "BOTH" if kind == "TMA_TRANSCRIPT_PROTEIN_CONCORDANCE" else "TRANSCRIPT"
    return NormalizedCoverageObservation(
        observation_id=observation_id or _next_obs("SC"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind=kind,
        molecular_layer=layer,
        assay_method=assay,
        crc_specific=crc_specific,
        malignant_cell_attribution=attribution,
        malignant_attribution_basis=(
            "resolved to the malignant epithelial cluster" if attribution == "MALIGNANT" else ""
        ),
        cohort_adequacy_status="NOT_ESTABLISHED",
        cohort_adequacy_basis="",
        expression_pattern=pattern,
        expression_pattern_basis=("SOURCE_REPORTED" if neg else ""),
        expression_pattern_basis_detail=("reported in the source figure" if neg else ""),
        claim=f"{assay} {cohort} {pattern} in the CRC malignant compartment",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or cohort}",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        cohort_id=cohort,
    )


def _bulk(
    *, observation_id: str | None = None, cohort: str = "CRC_COHORT_A",
    kind: str = "BULK_CRC_RNA", source_id: str | None = None,
) -> NormalizedCoverageObservation:
    return NormalizedCoverageObservation(
        observation_id=observation_id or _next_obs("BULK"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind=kind,
        molecular_layer="TRANSCRIPT",
        assay_method="BULK_RNA" if kind == "BULK_CRC_RNA" else "PAN_CANCER_PANEL",
        crc_specific=(kind == "BULK_CRC_RNA"),
        malignant_cell_attribution="UNRESOLVED",
        malignant_attribution_basis="",
        cohort_adequacy_status="NOT_ESTABLISHED",
        cohort_adequacy_basis="",
        expression_pattern="",
        expression_pattern_basis="",
        expression_pattern_basis_detail="",
        claim=f"{kind} {cohort} target expression, no malignant deconvolution",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or cohort}",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        cohort_id=cohort,
    )


def _matched(*, observation_id: str | None = None, source_id: str | None = None):
    return NormalizedCoverageObservation(
        observation_id=observation_id or _next_obs("MNT"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind="MATCHED_NORMAL_TUMOR",
        molecular_layer="PROTEIN",
        assay_method="MATCHED_NORMAL_TUMOR_COMPARISON",
        crc_specific=True,
        malignant_cell_attribution="UNRESOLVED",
        malignant_attribution_basis="",
        cohort_adequacy_status="NOT_ESTABLISHED",
        cohort_adequacy_basis="",
        expression_pattern="",
        expression_pattern_basis="",
        expression_pattern_basis_detail="",
        claim="matched normal colon vs CRC tumor comparison for the target",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier="GSE-MNT",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        cohort_id="CRC_COHORT_A",
    )


def _completion(
    *,
    attempted: bool = True,
    complete: bool = True,
    protein_complete: bool | None = None,
    sc_complete: bool | None = None,
    tma_complete: bool | None = None,
    matched_complete: bool | None = None,
    unresolved: tuple[CoverageUnresolvedItem, ...] = (),
    qualifying_protein: tuple[str, ...] = (),
    qualifying_indirect: tuple[str, ...] = (),
    audit_obs_id: str | None = "OBS-AUDIT-0001",
    as_of: str = AS_OF,
) -> CrcCohortCoverageCompletion:
    p = complete if protein_complete is None else protein_complete
    s = complete if sc_complete is None else sc_complete
    t = complete if tma_complete is None else tma_complete
    m = complete if matched_complete is None else matched_complete
    umbrella = complete
    return CrcCohortCoverageCompletion(
        attempted=attempted,
        landscape_as_of=as_of,
        search_scope=SCOPE if attempted else "",
        sources_searched=("GEO", "HPA", "CPTAC") if attempted else (),
        public_crc_coverage_search_complete=umbrella,
        protein_cohort_search_complete=p if attempted else False,
        malignant_compartment_sc_spatial_search_complete=s if attempted else False,
        tma_concordance_search_complete=t if attempted else False,
        matched_normal_tumor_search_complete=m if attempted else False,
        unresolved_items=unresolved,
        qualifying_protein_cohort_ids=qualifying_protein,
        qualifying_indirect_cohort_ids=qualifying_indirect,
        audit_observation_id=(audit_obs_id or "") if (attempted and umbrella) else "",
    )


def _audit(
    completion: CrcCohortCoverageCompletion,
    *,
    observation_id: str | None = None,
    source_id: str | None = None,
    override: dict | None = None,
) -> NormalizedCoverageObservation:
    fields = dict(
        observation_id=observation_id or completion.audit_observation_id,
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=completion.landscape_as_of,
        observation_kind="SEARCH_COMPLETION_AUDIT",
        molecular_layer="",
        assay_method="SEARCH_AUDIT",
        crc_specific=True,
        malignant_cell_attribution="UNRESOLVED",
        malignant_attribution_basis="",
        cohort_adequacy_status="NOT_ESTABLISHED",
        cohort_adequacy_basis="",
        expression_pattern="",
        expression_pattern_basis="",
        expression_pattern_basis_detail="",
        claim="the declared public CRC malignant-cell coverage search is complete",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier="GSE-AUDIT",
        locator="",
        retrieved_at=completion.landscape_as_of,
        primary_or_repository_source_resolved=True,
        audit_search_scope=completion.search_scope,
        audit_sources_searched=completion.sources_searched,
        audit_landscape_as_of=completion.landscape_as_of,
        audit_public_crc_coverage_search_complete=completion.public_crc_coverage_search_complete,
        audit_protein_cohort_search_complete=completion.protein_cohort_search_complete,
        audit_malignant_compartment_sc_spatial_search_complete=completion.malignant_compartment_sc_spatial_search_complete,
        audit_tma_concordance_search_complete=completion.tma_concordance_search_complete,
        audit_matched_normal_tumor_search_complete=completion.matched_normal_tumor_search_complete,
        audit_unresolved_item_keys=tuple(i.snapshot_key for i in completion.unresolved_items),
        audit_qualifying_protein_cohort_ids=completion.qualifying_protein_cohort_ids,
        audit_qualifying_indirect_cohort_ids=completion.qualifying_indirect_cohort_ids,
    )
    if override:
        fields.update(override)
    return NormalizedCoverageObservation(**fields)


def _input(*, target: str = TARGET_A, as_of: str = AS_OF, existing: tuple[str, ...] = ()):
    return Tgt02ModuleInput(
        candidate_id=CAND,
        candidate_name="synthetic ADC candidate",
        target_identity=target,
        instantiation_id=INST,
        context_id=CTX_ID,
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-02",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-E8-TEST",
        code_commit="deadbeef",
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        crc_coverage_search_scope=SCOPE,
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
    module_input: Tgt02ModuleInput | None = None,
) -> Tgt02ModuleRunResult:
    observations = list(observations)
    return run(
        module_input or _input(),
        provider=FakeProvider(observations, completion),
        evidence_id_allocator=allocator or FakeAllocator(),
        source_resolver=FakeSourceResolver(observations, unresolved=unresolved, mismatch=mismatch),
        evidence_library=FakeEvidenceLibrary(library),
    )


def _pair(res: Tgt02ModuleRunResult):
    pe = res.proposal_envelope
    return None if pe is None else (pe.proposed_direction, pe.proposed_strength)


# =========================================================================


class BindingAndBoundaryTests(unittest.TestCase):
    def test_binding_is_one_zero_zero_with_migration_pending(self):
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-02"], "1.0.0")
        gs = yaml.safe_load(GATESET_YAML.read_text())
        binding = next(
            b for b in gs["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-02"
        )
        self.assertEqual(binding["primary_module_version"], "1.0.0")
        self.assertEqual(binding["primary_module_id"], "MOD-TGT02")
        self.assertIn("per_gate_primary_modules", gs["migration"]["deferred"])

    def test_other_modules_untouched(self):
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-01"], "1.0.0")
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-05"], "1.0.0")
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-08"], "1.0.0")

    def test_package_has_the_eleven_expected_files(self):
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((PKG / f).is_file(), f)

    def test_module_yaml_identity_and_conservative_flags(self):
        manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.assertEqual(manifest["module_id"], "MOD-TGT02")
        self.assertEqual(manifest["module_version"], "1.0.0")
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e8")
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


class InputContractTests(unittest.TestCase):
    def test_landscape_as_of_must_be_an_iso_date(self):
        with self.assertRaises(ValueError):
            _input(as_of="soon")

    def test_instantiation_must_match(self):
        with self.assertRaises(ValueError):
            dataclasses.replace(_input(), instantiation_id="INST-OTHER-v1")

    def test_evidence_regime_must_be_public_only(self):
        with self.assertRaises(ValueError):
            dataclasses.replace(_input(), evidence_regime="PUBLIC_PLUS_EXPERIMENTAL")

    def test_wrong_gate_id_rejected(self):
        with self.assertRaises(ValueError):
            dataclasses.replace(_input(), gate_id="TGT-03")


class IdentityProvenanceIntegrityTests(unittest.TestCase):
    def _complete(self):
        return _completion(qualifying_protein=("CRC_COHORT_A",))

    def test_wrong_target_is_a_hard_run_rejection(self):
        comp = self._complete()
        obs = [_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)]
        res = _run(obs, comp, module_input=dataclasses.replace(_input(), target_identity="TARGET_A"))
        # observation carries TARGET_A already -> accepted; now flip the observation target
        bad = dataclasses.replace(obs[0], target_identity="TARGET_B")
        res = _run([bad, obs[1]], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(res.hard_integrity_failures)

    def test_unresolved_source_is_a_hard_run_rejection(self):
        comp = self._complete()
        p = _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")
        res = _run([p, _audit(comp)], comp, unresolved={p.source_id})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(res.hard_integrity_failures)

    def test_canonical_source_metadata_drift_is_a_hard_run_rejection(self):
        comp = self._complete()
        p = _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")
        res = _run([p, _audit(comp)], comp, mismatch={p.source_id})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_hard_failure_is_never_degraded_to_accepted_unknown(self):
        comp = self._complete()
        p = _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")
        res = _run([p, _audit(comp)], comp, unresolved={p.source_id})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)


class ExactReuseTests(unittest.TestCase):
    def _emit_once(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        p = _protein(observation_id="OBS-REUSE-1", cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")
        res = _run([p, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        ep = next(e for e in res.evidence_packages if e.study_context["observation_id"] == "OBS-REUSE-1")
        return comp, p, ep

    def test_existing_canonical_package_is_reused_without_an_allocator_call(self):
        comp, p, ep = self._emit_once()
        alloc = FakeAllocator(start=900)
        res = _run([p, _audit(comp)], comp, library={"OBS-REUSE-1": ep}, allocator=alloc)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIn(ep.evidence_id, res.reused_evidence_ids)
        # only the audit EP is newly allocated
        self.assertEqual(alloc.calls, 1)

    def test_classification_driving_drift_on_a_reused_package_is_hard(self):
        comp, p, ep = self._emit_once()
        drifted = dataclasses.replace(
            ep, study_context={**ep.study_context, "expression_pattern": "ABSENT"}
        )
        res = _run([p, _audit(comp)], comp, library={"OBS-REUSE-1": drifted})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_missing_classification_field_on_a_reused_package_is_hard(self):
        comp, p, ep = self._emit_once()
        ctx = {k: v for k, v in ep.study_context.items() if k != "assay_method"}
        stripped = dataclasses.replace(ep, study_context=ctx)
        res = _run([p, _audit(comp)], comp, library={"OBS-REUSE-1": stripped})
        self.assertFalse(res.machine_acceptance.accepted)


class RungClassificationTests(unittest.TestCase):
    def _rung(self, obs):
        return classify_observation(obs, canonical_target_identity=TARGET_A)

    def test_validated_ihc_malignant_crc_qualified_is_direct(self):
        c = self._rung(_protein(assay="VALIDATED_IHC"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_for_direct)

    def test_quantitative_proteomics_is_direct(self):
        self.assertEqual(self._rung(_protein(assay="QUANTITATIVE_PROTEOMICS")).evidence_rung, "DIRECT")

    def test_validated_multiplex_if_is_direct(self):
        self.assertEqual(self._rung(_protein(assay="VALIDATED_MULTIPLEX_IF")).evidence_rung, "DIRECT")

    def test_generic_protein_assay_is_not_direct(self):
        c = self._rung(_protein(assay="OTHER"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")
        self.assertFalse(c.qualifying_for_direct)

    def test_protein_without_qualified_cohort_is_not_direct(self):
        c = self._rung(_protein(assay="VALIDATED_IHC", adequacy="NOT_ESTABLISHED"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")

    def test_single_cell_malignant_is_indirect_strong(self):
        c = self._rung(_sc(assay="SINGLE_CELL_RNA"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_for_indirect)

    def test_spatial_malignant_is_indirect_strong(self):
        self.assertEqual(self._rung(_sc(assay="SPATIAL_RNA")).evidence_rung, "INDIRECT_STRONG")

    def test_tma_concordance_is_indirect_strong_never_direct(self):
        c = self._rung(_sc(kind="TMA_TRANSCRIPT_PROTEIN_CONCORDANCE", assay="TMA_TRANSCRIPT_PROTEIN"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertFalse(c.qualifying_for_direct)

    def test_bulk_crc_rna_is_weak(self):
        self.assertEqual(self._rung(_bulk(kind="BULK_CRC_RNA")).evidence_rung, "WEAK")

    def test_pan_cancer_unresolved_is_weak(self):
        self.assertEqual(self._rung(_bulk(kind="PAN_CANCER_UNRESOLVED")).evidence_rung, "WEAK")

    def test_search_completion_audit_is_contextual_no_rung(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        c = self._rung(_audit(comp))
        self.assertEqual(c.evidence_rung, "")
        self.assertEqual(c.coverage_support, "CONTEXTUAL")


class HardScientificBoundaryTests(unittest.TestCase):
    def _rung(self, obs):
        return classify_observation(obs, canonical_target_identity=TARGET_A)

    def test_transcript_never_reaches_direct(self):
        for kind, assay in (("MALIGNANT_SC_SPATIAL", "SINGLE_CELL_RNA"),
                            ("TMA_TRANSCRIPT_PROTEIN_CONCORDANCE", "TMA_TRANSCRIPT_PROTEIN")):
            self.assertNotEqual(self._rung(_sc(kind=kind, assay=assay)).evidence_rung, "DIRECT")

    def test_protein_without_malignant_attribution_never_direct(self):
        c = self._rung(_protein(attribution="NON_MALIGNANT"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")
        self.assertEqual(c.coverage_support, "CONTEXTUAL")

    def test_stroma_immune_is_contextual_not_a_hard_failure(self):
        c = self._rung(_sc(attribution="NON_MALIGNANT"))
        self.assertTrue(c.admissible)
        self.assertEqual(c.rejection_severity, "")
        self.assertEqual(c.coverage_support, "CONTEXTUAL")
        self.assertEqual(c.evidence_rung, "")

    def test_non_crc_protein_is_contextual_only(self):
        c = self._rung(_protein(crc_specific=False))
        self.assertNotEqual(c.evidence_rung, "DIRECT")
        self.assertEqual(c.coverage_support, "CONTEXTUAL")

    def test_matched_normal_tumor_is_context_only_never_a_ti_read(self):
        c = self._rung(_matched())
        self.assertEqual(c.evidence_rung, "")
        self.assertEqual(c.coverage_support, "CONTEXTUAL")

    def test_cohort_n_never_changes_the_rung(self):
        small = self._rung(_protein(cohort_n=3))
        big = self._rung(_protein(cohort_n=5000))
        self.assertEqual(small.evidence_rung, big.evidence_rung)
        self.assertEqual(small.evidence_rung, "DIRECT")

    def test_no_numeric_or_ranking_score_in_the_accepted_output(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"))
        obs = [_protein(cohort="CRC_COHORT_A", pattern="ABSENT"),
               _protein(cohort="CRC_COHORT_B", pattern="ABSENT"), _audit(comp)]
        res = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        pe = res.proposal_envelope
        blob = (pe.aggregation_rationale + " " + " ".join(u for u, _ in pe.critical_unknowns)).lower()
        for token in ("h-score", "score =", "ranking", "cutoff", "% positive", "percent positive"):
            self.assertNotIn(token, blob)


class CompletionInvariantTests(unittest.TestCase):
    def test_umbrella_true_while_a_component_false_is_hard(self):
        comp = _completion(
            qualifying_protein=("CRC_COHORT_A",), sc_complete=False,
        )
        # umbrella=True but sc component=False -> integrity contradiction
        obs = [_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)]
        res = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(any("contradiction" in why for _, why in res.hard_integrity_failures))

    def test_complete_landscape_with_no_audit_is_hard(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_two_audits_is_hard(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        a1 = _audit(comp, observation_id="OBS-AUDIT-0001")
        a2 = _audit(comp, observation_id="OBS-AUDIT-0001", source_id=_next_src())
        # duplicate (source_id, claim) is dropped; use two distinct audit obs ids
        a2 = _audit(comp, observation_id="OBS-AUDIT-0002")
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), a1, a2], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_audit_snapshot_drift_is_hard(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        bad_audit = _audit(comp, override={"audit_qualifying_protein_cohort_ids": ("CRC_COHORT_Z",)})
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="ABSENT"), bad_audit], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(any("snapshot field" in why for _, why in res.hard_integrity_failures))

    def test_qualifying_protein_set_drift_is_hard(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"))
        obs = [_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)]
        res = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(any("qualifying_protein_cohort_ids" in why for _, why in res.hard_integrity_failures))

    def test_qualifying_indirect_set_drift_is_hard(self):
        comp = _completion(qualifying_indirect=("CRC_COHORT_A", "CRC_COHORT_B"))
        obs = [_sc(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)]
        res = _run(obs, comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(any("qualifying_indirect_cohort_ids" in why for _, why in res.hard_integrity_failures))

    def test_snapshot_consistent_audit_passes(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        obs = [_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)]
        res = _run(obs, comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)

    def test_single_positive_cohort_incomplete_landscape_is_unknown(self):
        comp = _completion(attempted=True, complete=False, protein_complete=True)
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_single_negative_cohort_incomplete_landscape_is_unknown(self):
        comp = _completion(attempted=True, complete=False, protein_complete=True)
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="ABSENT")], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertFalse(res.fatal_review.required)


class AggregateTruthTableTests(unittest.TestCase):
    def test_completed_direct_support_is_positive_direct(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))

    def test_completed_direct_oppose_is_negative_direct(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="ABSENT"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("NEGATIVE", "DIRECT"))

    def test_completed_indirect_support_is_positive_indirect_strong(self):
        comp = _completion(qualifying_indirect=("CRC_COHORT_A",))
        res = _run([_sc(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_completed_indirect_oppose_is_negative_indirect_strong(self):
        comp = _completion(qualifying_indirect=("CRC_COHORT_A",))
        res = _run([_sc(cohort="CRC_COHORT_A", pattern="ABSENT"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("NEGATIVE", "INDIRECT_STRONG"))

    def test_support_and_oppose_is_conflicting_at_the_overall_rung(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"))
        res = _run([
            _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"),
            _protein(cohort="CRC_COHORT_B", pattern="ABSENT"),
            _audit(comp),
        ], comp)
        self.assertEqual(_pair(res), ("CONFLICTING", "DIRECT"))

    def test_qualified_nondirectional_direct_is_graded_inconclusive_direct(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="MIXED_OR_UNRESOLVED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertIn("CONTEXTUAL", roles)

    def test_qualified_nondirectional_indirect_is_graded_inconclusive_indirect(self):
        comp = _completion(qualifying_indirect=("CRC_COHORT_A",))
        res = _run([_sc(cohort="CRC_COHORT_A", pattern="MIXED_OR_UNRESOLVED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "INDIRECT_STRONG"))

    def test_weak_only_completed_landscape_is_inconclusive_unknown_not_weak(self):
        comp = _completion()
        res = _run([_bulk(kind="BULK_CRC_RNA"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_no_inconclusive_weak_pair_is_legal(self):
        self.assertNotIn(("INCONCLUSIVE", "WEAK"), LEGAL_DIRECTION_STRENGTH_PAIRS)

    def test_overall_strength_is_the_highest_qualifying_class_no_two_axis_rule(self):
        # a qualifying DIRECT + a qualifying INDIRECT_STRONG -> overall DIRECT
        comp = _completion(
            qualifying_protein=("CRC_COHORT_A",), qualifying_indirect=("CRC_COHORT_B",)
        )
        res = _run([
            _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"),
            _sc(cohort="CRC_COHORT_B", pattern="PRESENT_CONSISTENT"),
            _audit(comp),
        ], comp)
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))


class HeterogeneityTests(unittest.TestCase):
    def test_present_and_absent_with_no_resolver_is_conflicting(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"))
        res = _run([
            _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"),
            _protein(cohort="CRC_COHORT_B", pattern="ABSENT"),
            _audit(comp),
        ], comp)
        self.assertEqual(res.proposal_envelope.proposed_direction, "CONFLICTING")

    def test_audited_multi_cohort_rare_highly_heterogeneous_is_negative_not_conflicting(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"))
        resolver = _protein(
            cohort="", cohort_ids=("CRC_COHORT_A", "CRC_COHORT_B"),
            pattern="RARE_HIGHLY_HETEROGENEOUS", declared_multi_cohort=True,
        )
        res = _run([
            _protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"),
            resolver,
            _audit(comp),
        ], comp)
        self.assertEqual(res.proposal_envelope.proposed_direction, "NEGATIVE")
        self.assertIn(res.proposal_envelope.proposed_strength, ("DIRECT", "INDIRECT_STRONG"))


class FatalReviewTests(unittest.TestCase):
    def _two_neg_cohorts(self, cohort_b="CRC_COHORT_B"):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", cohort_b))
        obs = [
            _protein(cohort="CRC_COHORT_A", pattern="ABSENT"),
            _protein(cohort=cohort_b, pattern="ABSENT"),
            _audit(comp),
        ]
        return _run(obs, comp)

    def test_single_negative_cohort_raises_no_fatal_review(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="ABSENT"), _audit(comp)], comp)
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "")

    def test_two_observations_from_the_same_cohort_are_not_cross_cohort(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([
            _protein(observation_id="OBS-P-1", cohort="CRC_COHORT_A", pattern="ABSENT"),
            _protein(observation_id="OBS-P-2", cohort="CRC_COHORT_A", pattern="RARE_HIGHLY_HETEROGENEOUS"),
            _audit(comp),
        ], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)

    def test_two_distinct_qualifying_protein_cohorts_trigger_potential_fatal_pattern(self):
        res = self._two_neg_cohorts()
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "POTENTIAL_FATAL_PATTERN")
        self.assertEqual(set(res.fatal_review.cohort_ids), {"CRC_COHORT_A", "CRC_COHORT_B"})

    def test_across_cohorts_is_at_least_two_exactly_two_triggers(self):
        # explicitly NOT "> 2" / ">= 3": two independent qualifying cohorts is enough
        res = self._two_neg_cohorts()
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(len(set(res.fatal_review.cohort_ids)), 2)

    def test_declared_multi_cohort_observation_with_two_cohort_ids_triggers(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"))
        multi = _protein(
            cohort="", cohort_ids=("CRC_COHORT_A", "CRC_COHORT_B"),
            pattern="ABSENT", declared_multi_cohort=True,
        )
        res = _run([multi, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)

    def test_transcript_negative_across_two_cohorts_raises_no_fatal_trigger(self):
        comp = _completion(qualifying_indirect=("CRC_COHORT_A", "CRC_COHORT_B"))
        res = _run([
            _sc(cohort="CRC_COHORT_A", pattern="ABSENT"),
            _sc(cohort="CRC_COHORT_B", pattern="ABSENT"),
            _audit(comp),
        ], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)

    def test_protein_plus_transcript_negative_only_counts_the_protein_cohorts(self):
        comp = _completion(
            qualifying_protein=("CRC_COHORT_A",), qualifying_indirect=("CRC_COHORT_B",)
        )
        res = _run([
            _protein(cohort="CRC_COHORT_A", pattern="ABSENT"),
            _sc(cohort="CRC_COHORT_B", pattern="ABSENT"),
            _audit(comp),
        ], comp)
        # only one protein cohort is negative -> no cross-protein fatal pattern
        self.assertFalse(res.fatal_review.required)

    def test_trigger_is_only_surfaced_on_an_accepted_run(self):
        # a cross-cohort negative pattern, but with a completion contradiction ->
        # run rejected, surfaced fatal_review is empty.
        comp = _completion(qualifying_protein=("CRC_COHORT_A", "CRC_COHORT_B"), sc_complete=False)
        res = _run([
            _protein(cohort="CRC_COHORT_A", pattern="ABSENT"),
            _protein(cohort="CRC_COHORT_B", pattern="ABSENT"),
            _audit(comp),
        ], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "")

    def test_fatal_review_status_is_never_more_than_potential_fatal_pattern(self):
        res = self._two_neg_cohorts()
        self.assertIn(res.fatal_review.status, ("", "POTENTIAL_FATAL_PATTERN"))
        for banned in ("PUBLIC_FATAL_SIGNAL_ESTABLISHED", "KILL", "HOLD"):
            self.assertNotEqual(res.fatal_review.status, banned)

    def test_fatal_review_is_not_a_proposal_envelope_field(self):
        for name in AssessmentProposalEnvelope.field_names():
            self.assertNotIn("fatal", name)
            self.assertNotIn("kill", name)


class CriticalUnknownTests(unittest.TestCase):
    def test_incomplete_public_search_is_public_resolvable(self):
        comp = _completion(
            attempted=True, complete=False, protein_complete=True,
            unresolved=(CoverageUnresolvedItem("sc atlas not yet resolved", "KNOWN_PUBLIC_NOT_YET_RESOLVED"),),
        )
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("PUBLIC_RESOLVABLE", resolutions)
        self.assertNotIn("EXPERIMENT_REQUIRED", resolutions)

    def test_access_or_annotation_blocked_item_is_currently_unresolvable(self):
        comp = _completion(
            attempted=True, complete=False, protein_complete=True,
            unresolved=(CoverageUnresolvedItem("CPTAC access pending DUA", "ACCESS_OR_ANNOTATION_BLOCKED"),),
        )
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT")], comp)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("CURRENTLY_UNRESOLVABLE", resolutions)

    def test_complete_indirect_only_directional_needs_experiment_required_protein_confirmation(self):
        comp = _completion(qualifying_indirect=("CRC_COHORT_A",))
        res = _run([_sc(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("POSITIVE", "INDIRECT_STRONG"))
        unknowns = res.proposal_envelope.critical_unknowns
        self.assertTrue(any(r == "EXPERIMENT_REQUIRED" and "protein-level" in u for u, r in unknowns))

    def test_complete_weak_only_is_unknown_plus_experiment_required(self):
        comp = _completion()
        res = _run([_bulk(kind="BULK_CRC_RNA"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertTrue(any(r == "EXPERIMENT_REQUIRED" for _, r in res.proposal_envelope.critical_unknowns))

    def test_graded_inconclusive_does_not_invent_experiment_required(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        res = _run([_protein(cohort="CRC_COHORT_A", pattern="MIXED_OR_UNRESOLVED"), _audit(comp)], comp)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))
        self.assertNotIn("EXPERIMENT_REQUIRED",
                         {r for _, r in res.proposal_envelope.critical_unknowns})


class ForbiddenOutputTests(unittest.TestCase):
    def _accepted(self):
        comp = _completion(qualifying_protein=("CRC_COHORT_A",))
        return _run([_protein(cohort="CRC_COHORT_A", pattern="PRESENT_CONSISTENT"), _audit(comp)], comp)

    def test_no_tgt03_tgt04_or_tgt05_wording_in_evidence_or_rationale(self):
        res = self._accepted()
        blob = res.proposal_envelope.aggregation_rationale.lower()
        for ep in res.evidence_packages:
            blob += " " + " ".join(ep.interpretation_boundary["directly_supports"]).lower()
        for token in ("persistence after treatment", "cell surface", "antigen density",
                      "internalis", "therapeutic index", "therapeutic window"):
            self.assertNotIn(token, blob)

    def test_module_never_constructs_a_candidate_gate_assessment(self):
        res = self._accepted()
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertNotIsInstance(res.proposal_envelope, CandidateGateAssessment)

    def test_output_surface_shape(self):
        res = self._accepted()
        self.assertIsInstance(res, Tgt02ModuleRunResult)
        self.assertIsInstance(res.machine_acceptance, MachineAcceptanceRecord)
        self.assertIsInstance(res.coverage_completion, CrcCohortCoverageCompletion)
        self.assertIsInstance(res.fatal_review, FatalReviewRecord)
        self.assertTrue(all(isinstance(ep, EvidencePackage) for ep in res.evidence_packages))
        self.assertEqual(res.proposal_envelope.evidence_ceiling, TGT02_EVIDENCE_CEILING)

    def test_evidence_package_is_gate_neutral(self):
        res = self._accepted()
        for ep in res.evidence_packages:
            blob = (ep.claim + " " + " ".join(ep.interpretation_boundary["directly_supports"])).lower()
            for token in ("passes tgt-02", "adequate malignant-cell coverage", "should be killed",
                          "coverage is fatal"):
                self.assertNotIn(token, blob)


if __name__ == "__main__":
    unittest.main()
