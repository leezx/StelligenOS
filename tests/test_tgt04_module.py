"""Runtime Migration PR E12: MOD-TGT04 deterministic scientific core.

Synthetic, in-memory only -- no network, no real absolute-quantitation flow /
QIFIKIT / mass-cytometry / surfaceomics / membranous-IHC data, no persistence.
The candidate target is ``TARGET_A``; LOCAL surface contexts are ``SURF_CTX_A`` /
``SURF_CTX_B`` / ``SURF_CTX_C``. No HER2 / TROP2 / real target names.

Covers the E12 acceptance scenarios (ChatGPT AI审核方案 E12-1..E12-8 + 4 required
tightenings):

* the TGT-04 binding reconciliation (0.0.0 -> 1.0.0 with MIGRATION_PENDING still
  in force), the module boundary (ports only, no network / subprocess /
  persistence, no normalizer, no generic framework, no numeric coercion of a raw
  density value);
* the HARD identity / provenance / completion-consistency / qualification
  integrity gate -- rejects the WHOLE run, never degrades to an accepted UNKNOWN;
* exact canonical EvidencePackage reuse (no allocator call, parity drift HARD,
  incl. SYMMETRIC raw-density presence-and-value parity either direction);
* the frozen Evidence-Ladder rung mapping (DIRECT only for a
  QUANTITATIVE_SURFACE_DENSITY observation with measurement_validation_status ==
  QUALIFIED + a non-empty assay_method + a QUALIFIED CRC / well-matched-model
  surface context + MALIGNANT attribution -- assay_method OPEN, no closed
  whitelist; an INDIRECT_STRONG localization rung requires
  surface_context_class == CRC_MALIGNANT_CELLS, a well-matched model localization
  observation is CONTEXTUAL; subcellular / topology / non-CRC / RNA-proxy never
  above WEAK);
* the frozen density_direction_mapping (NEGLIGIBLE_OR_UNDETECTABLE -> OPPOSES;
  else PLAUSIBLY_ADEQUATE -> SUPPORTS; NOT_PLAUSIBLY_ADEQUATE -> OPPOSES; MIXED /
  NOT_ESTABLISHED -> CONTEXTUAL; LOW_BUT_PRESENT alone decides nothing);
* the TWO-TIER / SINGLE-TIER grading authority -- only a qualifying DIRECT
  quantitative antigen-density observation grants a graded Direction; a
  localization-only completed landscape (any number of qualifying
  INDIRECT_STRONG, zero DIRECT) is INCONCLUSIVE / UNKNOWN; the legal pairs are
  exactly POSITIVE/DIRECT, NEGATIVE/DIRECT, CONFLICTING/DIRECT,
  INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN; support + oppose is CONFLICTING /
  DIRECT unless a typed declared multi-context density_plausibility_status
  MIXED_OR_UNRESOLVED characterisation covering all material contexts resolves it
  to a graded INCONCLUSIVE / DIRECT;
* the machine-local ``fatal_review`` review TRIGGER -- Route A (an auditable
  explicit reproducibility qualification, basis text NEVER parsed) OR Route B
  (>= 2 independent qualified CRC MALIGNANT-CELL surface-context identities, NOT
  "> 2"; a well-matched CRC model identity does not count); at most
  POTENTIAL_FATAL_PATTERN; never a canonical fatal flag / KILL / HOLD / Decision;
  only actionable on an accepted run; not a proposal-envelope field;
* the TGT-04 dedup deviation -- distinct surface_context_id observations that
  share a (source_id, claim) both survive;
* the narrow deterministic critical-unknown mapping (unresolved public item ->
  no EXPERIMENT_REQUIRED; public exhausted + localization-only ->
  EXPERIMENT_REQUIRED);
* the accepted-run output surface (EvidencePackages + one
  SurfaceAvailabilityCompletion + fatal_review + proposal envelope +
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

from gate_modules.tgt04_tumor_surface_availability_density_plausibility import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    TGT04_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedSurfaceObservation,
    SurfaceAvailabilityCompletion,
    SurfaceUnresolvedItem,
    Tgt04ModuleInput,
    Tgt04ModuleRunResult,
    run,
)
from gate_modules.tgt04_tumor_surface_availability_density_plausibility.classify import (
    classify_observation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt04_tumor_surface_availability_density_plausibility"
GATESET_YAML = REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"

TARGET_A = "TARGET_A"
CAND = "CAND-L04-000123"
CTX_ID = "CTX-CRC-REFRACTORY-MCRC"
INST = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CONTEXT_KEY = "REFRACTORY_MCRC"
AS_OF = "2026-08-31"
SCOPE = "absolute-quantitation flow + QIFIKIT + mass cytometry + surfaceomics + membranous-IHC repositories"

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
        observations: list[NormalizedSurfaceObservation],
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

    def surface_completion(self, **_):
        return self._completion


# --- observation factories ------------------------------------------------

def _density(
    *,
    observation_id: str | None = None,
    context: str = "SURF_CTX_A",
    context_ids: tuple[str, ...] = (),
    declared_multi_context: bool = False,
    surface_context_class: str = "CRC_MALIGNANT_CELLS",
    antigen_level: str = "QUANTITATIVELY_PRESENT",
    plausibility: str = "PLAUSIBLY_ADEQUATE",
    validation: str = "QUALIFIED",
    adequacy: str = "QUALIFIED",
    attribution: str = "MALIGNANT",
    crc_specific: bool = True,
    reproducibility: str = "NOT_ESTABLISHED",
    assay: str = "QIFIKIT absolute quantitation flow",
    value: str = "",
    unit: str = "",
    summary: str = "",
    source_id: str | None = None,
    as_of: str = AS_OF,
) -> NormalizedSurfaceObservation:
    return NormalizedSurfaceObservation(
        observation_id=observation_id or _next_obs("DENS"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        observation_kind="QUANTITATIVE_SURFACE_DENSITY",
        molecular_layer="PROTEIN",
        assay_method=assay,
        measurement_validation_status=validation,
        measurement_validation_basis=(
            "assay validated on bead-calibrated standards; SOP disclosed"
            if validation == "QUALIFIED"
            else ""
        ),
        crc_specific=crc_specific,
        surface_context_class=surface_context_class,
        surface_context_basis=(
            "annotated CRC malignant epithelium / a validated well-matched CRC model"
            if adequacy == "QUALIFIED"
            else ""
        ),
        context_adequacy_status=adequacy,
        context_adequacy_basis=(
            "malignant compartment and model provenance disclosed in the source"
            if adequacy == "QUALIFIED"
            else ""
        ),
        malignant_cell_attribution=attribution,
        malignant_attribution_basis=(
            "pathologist-annotated malignant epithelium" if attribution == "MALIGNANT" else ""
        ),
        surface_localization_status="",
        surface_localization_basis="",
        density_plausibility_status=plausibility,
        density_plausibility_basis=(
            "SOURCE_REPORTED"
            if plausibility in ("PLAUSIBLY_ADEQUATE", "NOT_PLAUSIBLY_ADEQUATE", "MIXED_OR_UNRESOLVED")
            else ""
        ),
        surface_antigen_level=antigen_level,
        surface_antigen_level_basis=(
            "source reports a quantitative antigen-level class" if antigen_level not in ("", "NOT_ESTABLISHED") else ""
        ),
        reproducibility_status=reproducibility,
        reproducibility_basis=(
            "one study establishing reproducibility across replicates / methods"
            if reproducibility == "QUALIFIED"
            else ""
        ),
        claim=f"QUANTITATIVE_SURFACE_DENSITY {context or ','.join(context_ids)} {antigen_level}",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or context}",
        locator="",
        retrieved_at=as_of,
        primary_or_repository_source_resolved=True,
        surface_context_id=context,
        surface_context_ids=context_ids,
        declared_multi_context_analysis=declared_multi_context,
        reported_density_value=value,
        reported_density_unit=unit,
        reported_density_summary=summary,
    )


def _ihc(
    *,
    observation_id: str | None = None,
    context: str = "SURF_CTX_A",
    kind: str = "MEMBRANOUS_IHC",
    surface_context_class: str = "CRC_MALIGNANT_CELLS",
    localization: str = "SURFACE_LOCALIZED",
    adequacy: str = "QUALIFIED",
    attribution: str = "MALIGNANT",
    crc_specific: bool = True,
    source_id: str | None = None,
) -> NormalizedSurfaceObservation:
    return NormalizedSurfaceObservation(
        observation_id=observation_id or _next_obs("IHC"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind=kind,
        molecular_layer="PROTEIN",
        assay_method="validated membranous IHC panel",
        measurement_validation_status="NOT_ESTABLISHED",
        measurement_validation_basis="",
        crc_specific=crc_specific,
        surface_context_class=surface_context_class,
        surface_context_basis="annotated CRC malignant epithelium" if adequacy == "QUALIFIED" else "",
        context_adequacy_status=adequacy,
        context_adequacy_basis="malignant compartment disclosed" if adequacy == "QUALIFIED" else "",
        malignant_cell_attribution=attribution,
        malignant_attribution_basis=(
            "pathologist-annotated malignant epithelium" if attribution == "MALIGNANT" else ""
        ),
        surface_localization_status=localization,
        surface_localization_basis=(
            "membranous staining pattern / plasma-membrane enrichment reported"
            if localization in ("SURFACE_LOCALIZED", "NOT_SURFACE_LOCALIZED", "MIXED_OR_UNRESOLVED")
            else ""
        ),
        density_plausibility_status="",
        density_plausibility_basis="",
        surface_antigen_level="",
        surface_antigen_level_basis="",
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        claim=f"{kind} {context} membranous localization of the target",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or context}",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        surface_context_id=context,
    )


def _weak(
    *,
    observation_id: str | None = None,
    kind: str = "NON_CRC_SURFACE_EVIDENCE",
    context: str = "SURF_CTX_A",
    source_id: str | None = None,
) -> NormalizedSurfaceObservation:
    layer = "TRANSCRIPT" if kind == "RNA_SURFACE_PROXY" else "PROTEIN"
    return NormalizedSurfaceObservation(
        observation_id=observation_id or _next_obs("WEAK"),
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=AS_OF,
        observation_kind=kind,
        molecular_layer=layer,
        assay_method="validated membranous IHC (non-CRC line)" if kind == "NON_CRC_SURFACE_EVIDENCE" else "bulk RNA-seq",
        measurement_validation_status="NOT_ESTABLISHED",
        measurement_validation_basis="",
        crc_specific=(kind == "RNA_SURFACE_PROXY"),
        surface_context_class="NON_CRC_MODEL" if kind == "NON_CRC_SURFACE_EVIDENCE" else "UNRESOLVED",
        surface_context_basis="",
        context_adequacy_status="NOT_ESTABLISHED",
        context_adequacy_basis="",
        malignant_cell_attribution="UNRESOLVED",
        malignant_attribution_basis="",
        surface_localization_status="",
        surface_localization_basis="",
        density_plausibility_status="",
        density_plausibility_basis="",
        surface_antigen_level="",
        surface_antigen_level_basis="",
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        claim=f"{kind} {context} weak surface hypothesis",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier=f"GSE-{observation_id or context}",
        locator="",
        retrieved_at=AS_OF,
        primary_or_repository_source_resolved=True,
        surface_context_id=context,
    )


def _completion(
    *,
    attempted: bool = True,
    complete: bool = True,
    quant_complete: bool | None = None,
    ihc_complete: bool | None = None,
    proteomics_complete: bool | None = None,
    subcellular_complete: bool | None = None,
    unresolved: tuple[SurfaceUnresolvedItem, ...] = (),
    qualifying_direct: tuple[str, ...] = (),
    qualifying_indirect: tuple[str, ...] = (),
    audit_obs_id: str | None = "OBS-AUDIT-0001",
    as_of: str = AS_OF,
) -> SurfaceAvailabilityCompletion:
    q = complete if quant_complete is None else quant_complete
    i = complete if ihc_complete is None else ihc_complete
    p = complete if proteomics_complete is None else proteomics_complete
    x = complete if subcellular_complete is None else subcellular_complete
    return SurfaceAvailabilityCompletion(
        attempted=attempted,
        landscape_as_of=as_of,
        search_scope=SCOPE if attempted else "",
        sources_searched=("GEO", "HPA", "CPTAC") if attempted else (),
        public_surface_search_complete=complete if attempted else False,
        quantitative_surface_density_search_complete=q if attempted else False,
        membranous_ihc_search_complete=i if attempted else False,
        surface_proteomics_search_complete=p if attempted else False,
        subcellular_localization_search_complete=x if attempted else False,
        unresolved_items=unresolved,
        qualifying_direct_surface_context_ids=qualifying_direct if attempted else (),
        qualifying_indirect_surface_context_ids=qualifying_indirect if attempted else (),
        audit_observation_id=(audit_obs_id or "") if attempted else "",
    )


def _audit(
    completion: SurfaceAvailabilityCompletion,
    *,
    observation_id: str | None = None,
    source_id: str | None = None,
    override: dict | None = None,
) -> NormalizedSurfaceObservation:
    fields = dict(
        observation_id=observation_id or completion.audit_observation_id,
        target_identity=TARGET_A,
        context_key=CONTEXT_KEY,
        landscape_as_of=completion.landscape_as_of,
        observation_kind="SEARCH_COMPLETION_AUDIT",
        molecular_layer="",
        assay_method="SEARCH_AUDIT",
        measurement_validation_status="NOT_ESTABLISHED",
        measurement_validation_basis="",
        crc_specific=True,
        surface_context_class="",
        surface_context_basis="",
        context_adequacy_status="NOT_ESTABLISHED",
        context_adequacy_basis="",
        malignant_cell_attribution="UNRESOLVED",
        malignant_attribution_basis="",
        surface_localization_status="",
        surface_localization_basis="",
        density_plausibility_status="",
        density_plausibility_basis="",
        surface_antigen_level="",
        surface_antigen_level_basis="",
        reproducibility_status="NOT_ESTABLISHED",
        reproducibility_basis="",
        claim="the declared public surface-availability search is complete",
        source_id=source_id or _next_src(),
        source_type="GEO",
        source_identifier="GSE-AUDIT",
        locator="",
        retrieved_at=completion.landscape_as_of,
        primary_or_repository_source_resolved=True,
        audit_search_scope=completion.search_scope,
        audit_sources_searched=completion.sources_searched,
        audit_landscape_as_of=completion.landscape_as_of,
        audit_public_surface_search_complete=completion.public_surface_search_complete,
        audit_quantitative_surface_density_search_complete=completion.quantitative_surface_density_search_complete,
        audit_membranous_ihc_search_complete=completion.membranous_ihc_search_complete,
        audit_surface_proteomics_search_complete=completion.surface_proteomics_search_complete,
        audit_subcellular_localization_search_complete=completion.subcellular_localization_search_complete,
        audit_unresolved_item_keys=tuple(i.snapshot_key for i in completion.unresolved_items),
        audit_qualifying_direct_surface_context_ids=completion.qualifying_direct_surface_context_ids,
        audit_qualifying_indirect_surface_context_ids=completion.qualifying_indirect_surface_context_ids,
    )
    if override:
        fields.update(override)
    return NormalizedSurfaceObservation(**fields)


def _input(*, target: str = TARGET_A, as_of: str = AS_OF, existing: tuple[str, ...] = ()):
    return Tgt04ModuleInput(
        candidate_id=CAND,
        candidate_name="synthetic ADC candidate",
        target_identity=target,
        instantiation_id=INST,
        context_id=CTX_ID,
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-04",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-E12-TEST",
        code_commit="deadbeef",
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        surface_search_scope=SCOPE,
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
    module_input: Tgt04ModuleInput | None = None,
) -> Tgt04ModuleRunResult:
    observations = list(observations)
    return run(
        module_input or _input(),
        provider=FakeProvider(observations, completion),
        evidence_id_allocator=allocator or FakeAllocator(),
        source_resolver=FakeSourceResolver(observations, unresolved=unresolved, mismatch=mismatch),
        evidence_library=FakeEvidenceLibrary(library),
    )


def _pair(res: Tgt04ModuleRunResult):
    pe = res.proposal_envelope
    return None if pe is None else (pe.proposed_direction, pe.proposed_strength)


# =========================================================================


class BindingAndBoundaryTests(unittest.TestCase):
    def test_binding_is_e12_built_module(self):
        self.assertEqual(BUILT_MODULE_VERSIONS["TGT-04"], "1.0.0")
        gs = yaml.safe_load(GATESET_YAML.read_text())
        binding = next(
            b for b in gs["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-04"
        )
        self.assertEqual(binding["primary_module_version"], "1.0.0")
        self.assertEqual(binding["primary_module_id"], "MOD-TGT04")

    def test_other_modules_untouched(self):
        for g in ("TGT-01", "TGT-02", "TGT-03", "TGT-05", "TGT-06", "TGT-08"):
            self.assertEqual(BUILT_MODULE_VERSIONS[g], "1.0.0")
        for g in ("TGT-07",):
            self.assertNotIn(g, BUILT_MODULE_VERSIONS)

    def test_package_has_the_eleven_expected_files(self):
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((PKG / f).is_file(), f)

    def test_migration_pending_remains(self):
        gs = yaml.safe_load(GATESET_YAML.read_text())
        self.assertEqual(gs["repository_policy"]["persistence_in_repository"], "forbidden")
        manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.assertFalse(manifest["boundary_flags"]["lifts_migration_pending"])

    def test_module_source_never_opens_a_network_subprocess_or_file(self):
        forbidden = (
            "import requests", "import httpx", "import urllib", "import socket",
            "import subprocess", "open(", "sqlite3", "boto3",
        )
        for src in PKG.rglob("*.py"):
            text = src.read_text()
            for tok in forbidden:
                self.assertNotIn(tok, text, f"{src.name}: {tok}")

    def test_module_never_coerces_a_raw_density_value_to_a_number(self):
        # E12 tightening 4: no float()/Decimal()/int() over a reported_density_*.
        for src in PKG.rglob("*.py"):
            tree = ast.parse(src.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ("float", "Decimal", "int"):
                        for arg in node.args:
                            dump = ast.dump(arg)
                            self.assertNotIn("reported_density", dump, src.name)

    def test_src_never_imports_gate_modules(self):
        for src in (REPO_ROOT / "src").rglob("*.py"):
            self.assertNotIn(
                "import gate_modules", src.read_text(), src.relative_to(REPO_ROOT)
            )


# =========================================================================


class RungClassificationTests(unittest.TestCase):
    def _classify(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_crc_malignant_cell_quantitative_plus_malignant_is_direct(self):
        c = self._classify(_density(surface_context_class="CRC_MALIGNANT_CELLS", attribution="MALIGNANT"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_for_direct)

    def test_crc_malignant_cell_quantitative_with_unresolved_attribution_is_not_direct(self):
        c = self._classify(_density(surface_context_class="CRC_MALIGNANT_CELLS", attribution="UNRESOLVED"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")
        self.assertFalse(c.qualifying_for_direct)

    def test_well_matched_model_quantitative_plus_malignant_is_direct(self):
        c = self._classify(_density(surface_context_class="WELL_MATCHED_CRC_MODEL", attribution="MALIGNANT"))
        self.assertEqual(c.evidence_rung, "DIRECT")
        self.assertTrue(c.qualifying_for_direct)

    def test_quantitative_without_qualified_measurement_validation_is_not_direct(self):
        c = self._classify(_density(validation="NOT_ESTABLISHED"))
        self.assertNotEqual(c.evidence_rung, "DIRECT")

    def test_quantitative_without_an_assay_method_is_not_direct(self):
        o = _density()
        object.__setattr__(o, "assay_method", "")
        c = self._classify(o)
        self.assertNotEqual(c.evidence_rung, "DIRECT")

    def test_crc_malignant_cell_membranous_ihc_is_indirect_strong(self):
        c = self._classify(_ihc(surface_context_class="CRC_MALIGNANT_CELLS", localization="SURFACE_LOCALIZED"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertTrue(c.qualifying_for_indirect)
        # a qualifying INDIRECT_STRONG localization observation is CONTEXTUAL.
        self.assertEqual(c.density_implication, "CONTEXTUAL")

    def test_well_matched_model_membranous_ihc_is_not_indirect_strong(self):
        c = self._classify(_ihc(surface_context_class="WELL_MATCHED_CRC_MODEL", localization="SURFACE_LOCALIZED"))
        self.assertNotEqual(c.evidence_rung, "INDIRECT_STRONG")
        self.assertEqual(c.density_implication, "CONTEXTUAL")

    def test_surface_proteomics_on_crc_is_indirect_strong(self):
        c = self._classify(_ihc(kind="SURFACE_PROTEOMICS", surface_context_class="CRC_MALIGNANT_CELLS"))
        self.assertEqual(c.evidence_rung, "INDIRECT_STRONG")

    def test_non_crc_surface_evidence_is_weak(self):
        c = self._classify(_weak(kind="NON_CRC_SURFACE_EVIDENCE"))
        self.assertEqual(c.evidence_rung, "WEAK")

    def test_rna_surface_proxy_is_weak(self):
        c = self._classify(_weak(kind="RNA_SURFACE_PROXY"))
        self.assertEqual(c.evidence_rung, "WEAK")

    def test_topology_prediction_is_weak(self):
        o = _weak(kind="TOPOLOGY_OR_GO_PREDICTION")
        object.__setattr__(o, "molecular_layer", "")
        c = self._classify(o)
        self.assertEqual(c.evidence_rung, "WEAK")

    def test_target_misbinding_is_hard(self):
        o = _density()
        object.__setattr__(o, "target_identity", "OTHER_TARGET")
        c = self._classify(o)
        self.assertFalse(c.admissible)
        self.assertEqual(c.rejection_severity, "HARD")


class DensityDirectionMappingTests(unittest.TestCase):
    def _classify(self, o):
        return classify_observation(o, canonical_target_identity=TARGET_A)

    def test_negligible_or_undetectable_opposes(self):
        c = self._classify(_density(antigen_level="NEGLIGIBLE_OR_UNDETECTABLE", plausibility="NOT_ESTABLISHED"))
        self.assertEqual(c.density_implication, "OPPOSES_DENSITY_PLAUSIBILITY")

    def test_plausibly_adequate_supports(self):
        c = self._classify(_density(antigen_level="QUANTITATIVELY_PRESENT", plausibility="PLAUSIBLY_ADEQUATE"))
        self.assertEqual(c.density_implication, "SUPPORTS_DENSITY_PLAUSIBILITY")

    def test_not_plausibly_adequate_opposes(self):
        c = self._classify(_density(antigen_level="LOW_BUT_PRESENT", plausibility="NOT_PLAUSIBLY_ADEQUATE"))
        self.assertEqual(c.density_implication, "OPPOSES_DENSITY_PLAUSIBILITY")

    def test_mixed_or_unresolved_is_contextual(self):
        c = self._classify(_density(antigen_level="MIXED_OR_UNRESOLVED", plausibility="MIXED_OR_UNRESOLVED"))
        self.assertEqual(c.density_implication, "CONTEXTUAL")

    def test_low_but_present_alone_does_not_oppose(self):
        c = self._classify(_density(antigen_level="LOW_BUT_PRESENT", plausibility="NOT_ESTABLISHED"))
        self.assertEqual(c.density_implication, "CONTEXTUAL")


class AggregationTwoTierSingleTierTests(unittest.TestCase):
    def test_many_indirect_strong_zero_direct_is_inconclusive_unknown(self):
        obs = [
            _ihc(observation_id=f"OBS-IHC-{i:04d}", context=f"SURF_CTX_{i}")
            for i in range(1, 6)
        ]
        comp = _completion(qualifying_indirect=tuple(f"SURF_CTX_{i}" for i in range(1, 6)))
        res = _run(obs + [_audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(res.proposal_envelope.evidence_refs, ())

    def test_qualifying_direct_plausibly_adequate_is_positive_direct(self):
        d = _density(context="SURF_CTX_A", plausibility="PLAUSIBLY_ADEQUATE")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))

    def test_qualifying_direct_negligible_is_negative_direct(self):
        d = _density(context="SURF_CTX_A", antigen_level="NEGLIGIBLE_OR_UNDETECTABLE", plausibility="NOT_ESTABLISHED")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("NEGATIVE", "DIRECT"))

    def test_supports_and_opposes_with_no_resolver_is_conflicting_direct(self):
        a = _density(observation_id="OBS-DENS-A1", context="SURF_CTX_A", plausibility="PLAUSIBLY_ADEQUATE")
        b = _density(observation_id="OBS-DENS-B1", context="SURF_CTX_B",
                     antigen_level="NEGLIGIBLE_OR_UNDETECTABLE", plausibility="NOT_ESTABLISHED")
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("CONFLICTING", "DIRECT"))

    def test_supports_and_opposes_with_typed_multi_context_resolver_is_inconclusive_direct(self):
        a = _density(observation_id="OBS-DENS-A2", context="SURF_CTX_A", plausibility="PLAUSIBLY_ADEQUATE")
        b = _density(observation_id="OBS-DENS-B2", context="SURF_CTX_B",
                     antigen_level="NEGLIGIBLE_OR_UNDETECTABLE", plausibility="NOT_ESTABLISHED")
        resolver = _density(
            observation_id="OBS-DENS-R2",
            context="",
            context_ids=("SURF_CTX_A", "SURF_CTX_B"),
            declared_multi_context=True,
            plausibility="MIXED_OR_UNRESOLVED",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, resolver, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))
        roles = {r for _, r in res.proposal_envelope.evidence_refs}
        self.assertIn("CONTEXTUAL", roles)

    def test_not_established_is_not_a_conflict_resolver(self):
        a = _density(observation_id="OBS-DENS-A3", context="SURF_CTX_A", plausibility="PLAUSIBLY_ADEQUATE")
        b = _density(observation_id="OBS-DENS-B3", context="SURF_CTX_B",
                     antigen_level="NEGLIGIBLE_OR_UNDETECTABLE", plausibility="NOT_ESTABLISHED")
        not_resolver = _density(
            observation_id="OBS-DENS-N3",
            context="",
            context_ids=("SURF_CTX_A", "SURF_CTX_B"),
            declared_multi_context=True,
            plausibility="NOT_ESTABLISHED",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, not_resolver, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("CONFLICTING", "DIRECT"))

    def test_qualifying_direct_unresolved_plausibility_is_graded_inconclusive_direct(self):
        d = _density(context="SURF_CTX_A", antigen_level="MIXED_OR_UNRESOLVED", plausibility="MIXED_OR_UNRESOLVED")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))

    def test_incomplete_landscape_is_inconclusive_unknown(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(complete=False, quant_complete=False)
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_all_proposed_pairs_are_in_the_frozen_legal_set(self):
        for d, s in (
            ("POSITIVE", "DIRECT"), ("NEGATIVE", "DIRECT"), ("CONFLICTING", "DIRECT"),
            ("INCONCLUSIVE", "DIRECT"), ("INCONCLUSIVE", "UNKNOWN"),
        ):
            self.assertIn((d, s), LEGAL_DIRECTION_STRENGTH_PAIRS)
        self.assertNotIn(("POSITIVE", "INDIRECT_STRONG"), LEGAL_DIRECTION_STRENGTH_PAIRS)
        self.assertNotIn(("INCONCLUSIVE", "WEAK"), LEGAL_DIRECTION_STRENGTH_PAIRS)


class CompletionInvariantTests(unittest.TestCase):
    def test_unattempted_completion_is_a_strict_empty_state(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(attempted=False, complete=False)
        res = _run([d], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_attempted_incomplete_with_exact_audit_is_accepted_unknown(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(complete=False, ihc_complete=False)
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_attempted_with_zero_audit_is_hard(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)
        self.assertIsNone(res.proposal_envelope)

    def test_attempted_with_two_audits_is_hard(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        a1 = _audit(comp, observation_id="OBS-AUDIT-0001")
        a2 = _audit(comp, observation_id="OBS-AUDIT-0002")
        res = _run([d, a1, a2], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_direct_qualifying_set_drift_is_hard(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(qualifying_direct=("SURF_CTX_WRONG",))
        res = _run([d, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_indirect_qualifying_set_drift_is_hard(self):
        i = _ihc(context="SURF_CTX_A")
        comp = _completion(qualifying_indirect=("SURF_CTX_WRONG",))
        res = _run([i, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_umbrella_flag_contradiction_is_hard(self):
        d = _density(context="SURF_CTX_A")
        comp = SurfaceAvailabilityCompletion(
            attempted=True,
            landscape_as_of=AS_OF,
            search_scope=SCOPE,
            sources_searched=("GEO",),
            public_surface_search_complete=True,
            quantitative_surface_density_search_complete=True,
            membranous_ihc_search_complete=True,
            surface_proteomics_search_complete=True,
            subcellular_localization_search_complete=False,  # umbrella says True, this is False
            unresolved_items=(),
            qualifying_direct_surface_context_ids=("SURF_CTX_A",),
            qualifying_indirect_surface_context_ids=(),
            audit_observation_id="OBS-AUDIT-0001",
        )
        res = _run([d, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)


class FatalReviewTests(unittest.TestCase):
    def _neg(self, *, context, source_id=None, reproducibility="NOT_ESTABLISHED", model=False):
        return _density(
            observation_id=_next_obs("NEG"),
            context=context,
            surface_context_class="WELL_MATCHED_CRC_MODEL" if model else "CRC_MALIGNANT_CELLS",
            antigen_level="NEGLIGIBLE_OR_UNDETECTABLE",
            plausibility="NOT_ESTABLISHED",
            reproducibility=reproducibility,
            source_id=source_id,
        )

    def test_one_crc_negligible_is_not_a_fatal_pattern(self):
        d = self._neg(context="SURF_CTX_A")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)

    def test_one_route_a_qualified_crc_negligible_is_a_potential_fatal_pattern(self):
        d = self._neg(context="SURF_CTX_A", reproducibility="QUALIFIED")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "POTENTIAL_FATAL_PATTERN")
        self.assertTrue(res.fatal_review.reproducibility_basis_refs)

    def test_two_crc_contexts_is_route_b(self):
        a = self._neg(context="SURF_CTX_A")
        b = self._neg(context="SURF_CTX_B")
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertTrue(res.fatal_review.required)
        self.assertEqual(res.fatal_review.reproducibility_basis_refs, ())

    def test_one_crc_plus_one_model_is_not_route_b(self):
        a = self._neg(context="SURF_CTX_A")
        b = self._neg(context="SURF_CTX_B", model=True)
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)

    def test_two_model_contexts_is_not_route_b(self):
        a = self._neg(context="SURF_CTX_A", model=True)
        b = self._neg(context="SURF_CTX_B", model=True)
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)

    def test_low_but_present_never_fatal(self):
        d = _density(
            context="SURF_CTX_A", antigen_level="LOW_BUT_PRESENT",
            plausibility="NOT_PLAUSIBLY_ADEQUATE", reproducibility="QUALIFIED",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertFalse(res.fatal_review.required)

    def test_fatal_review_needs_a_completed_landscape(self):
        d = self._neg(context="SURF_CTX_A", reproducibility="QUALIFIED")
        comp = _completion(complete=False, ihc_complete=False)
        res = _run([d, _audit(comp)], comp)
        self.assertFalse(res.fatal_review.required)

    def test_fatal_review_is_not_a_proposal_envelope_field(self):
        for name in AssessmentProposalEnvelope.field_names():
            self.assertNotIn("fatal", name)
            self.assertNotIn("review", name)


class RawDensityFactTests(unittest.TestCase):
    def _canonical(self, o, evidence_id="EP-00009000", *, value=None, unit=None, summary=None):
        keys = (
            "observation_id", "target_identity", "context_key", "landscape_as_of",
            "observation_kind", "molecular_layer", "assay_method",
            "measurement_validation_status", "measurement_validation_basis", "crc_specific",
            "surface_context_class", "surface_context_basis", "context_adequacy_status",
            "context_adequacy_basis", "malignant_cell_attribution", "malignant_attribution_basis",
            "surface_localization_status", "surface_localization_basis",
            "density_plausibility_status", "density_plausibility_basis",
            "surface_antigen_level", "surface_antigen_level_basis",
            "reproducibility_status", "reproducibility_basis",
            "surface_context_id", "surface_context_ids", "declared_multi_context_analysis",
            "reported_density_value", "reported_density_unit", "reported_density_summary",
        )
        sc = {k: getattr(o, k) for k in keys}
        if value is not None:
            sc["reported_density_value"] = value
        if unit is not None:
            sc["reported_density_unit"] = unit
        if summary is not None:
            sc["reported_density_summary"] = summary
        sc.update(indication="colorectal_cancer", treatment_state="not_applicable",
                  sample_type="crc_malignant_cell_quantitative_surface_density")
        return EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=o.claim,
            measurement={"type": "x", "analyte": o.target_identity, "readout": "r",
                         "result": "res", "unit": sc["reported_density_unit"]},
            candidate_refs=(CAND,),
            study_context=sc,
            provenance={
                "source_id": o.source_id, "source_type": o.source_type,
                "source_identifier": o.source_identifier, "locator": o.locator,
                "retrieved_at": o.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": ("x",), "does_not_support": ("y",),
                "limitations": ("z",), "evidence_ceiling": "c",
            },
            derivation={"module_run_id": "RUN-E12-TEST", "code_commit": "deadbeef"},
        )

    def _run_reuse(self, o, canonical):
        comp = _completion(qualifying_direct=(o.surface_context_id,))
        return _run(
            [o, _audit(comp)], comp,
            library={o.observation_id: canonical},
            allocator=FakeAllocator(50),
        )

    def test_identical_raw_density_is_reused(self):
        o = _density(observation_id="OBS-DENS-RD1", context="SURF_CTX_A",
                     value="12000", unit="molecules/cell", summary="~1.2e4 by QIFIKIT")
        can = self._canonical(o, evidence_id="EP-00009001")
        res = self._run_reuse(o, can)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIn("EP-00009001", res.reused_evidence_ids)

    def test_both_absent_raw_density_is_reused(self):
        o = _density(observation_id="OBS-DENS-RD2", context="SURF_CTX_A")
        can = self._canonical(o, evidence_id="EP-00009002")
        res = self._run_reuse(o, can)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIn("EP-00009002", res.reused_evidence_ids)

    def test_canonical_absent_current_present_is_hard(self):
        o = _density(observation_id="OBS-DENS-RD3", context="SURF_CTX_A", value="12000")
        can = self._canonical(o, evidence_id="EP-00009003", value="")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_canonical_present_current_absent_is_hard(self):
        o = _density(observation_id="OBS-DENS-RD4", context="SURF_CTX_A")
        can = self._canonical(o, evidence_id="EP-00009004", value="12000")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_value_drift_is_hard(self):
        o = _density(observation_id="OBS-DENS-RD5", context="SURF_CTX_A", value="12000")
        can = self._canonical(o, evidence_id="EP-00009005", value="2000")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_unit_drift_is_hard(self):
        o = _density(observation_id="OBS-DENS-RD6", context="SURF_CTX_A", value="12000", unit="molecules/cell")
        can = self._canonical(o, evidence_id="EP-00009006", unit="ABC")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_summary_drift_is_hard(self):
        o = _density(observation_id="OBS-DENS-RD7", context="SURF_CTX_A", summary="~1.2e4 by QIFIKIT")
        can = self._canonical(o, evidence_id="EP-00009007", summary="below assay detection limit")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)


class NamespaceAndDedupTests(unittest.TestCase):
    def test_local_surface_context_id_equal_to_canonical_context_id_is_hard(self):
        o = _density(observation_id="OBS-DENS-NS1", context="SURF_CTX_A")
        object.__setattr__(o, "surface_context_id", CTX_ID)
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([o, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_qualifying_direct_without_a_local_surface_context_is_hard(self):
        o = _density(observation_id="OBS-DENS-NS2", context="")
        comp = _completion(qualifying_direct=())
        res = _run([o, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_same_source_and_claim_different_surface_context_both_survive(self):
        a = _density(observation_id="OBS-DENS-DD1", context="SURF_CTX_A", source_id="SRC-00000777")
        b = _density(observation_id="OBS-DENS-DD2", context="SURF_CTX_B", source_id="SRC-00000777")
        object.__setattr__(b, "claim", a.claim)
        object.__setattr__(b, "source_identifier", a.source_identifier)
        object.__setattr__(b, "locator", a.locator)
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(len(res.evidence_packages), 3)  # a + b + audit

    def test_duplicate_observation_id_is_hard_before_any_allocation(self):
        a = _density(observation_id="OBS-DENS-DUP", context="SURF_CTX_A")
        b = _density(observation_id="OBS-DENS-DUP", context="SURF_CTX_B")
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        alloc = FakeAllocator()
        res = _run([a, b, _audit(comp)], comp, allocator=alloc)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(res.hard_integrity_failures)
        # authoritative-identity precedence: the run short-circuits BEFORE any
        # semantic dedup / source resolution / Evidence ID allocation.
        self.assertEqual(alloc.calls, 0)
        self.assertEqual(res.evidence_packages, ())

    def test_audit_ep_is_never_a_dedup_loser(self):
        d = _density(context="SURF_CTX_A", source_id="SRC-00000888")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        a = _audit(comp, source_id="SRC-00000888")
        object.__setattr__(a, "claim", d.claim)
        object.__setattr__(a, "source_identifier", d.source_identifier)
        res = _run([d, a], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        kinds = {e.study_context["observation_kind"] for e in res.evidence_packages}
        self.assertIn("SEARCH_COMPLETION_AUDIT", kinds)


class IntegrityGateTests(unittest.TestCase):
    def test_target_misbinding_rejects_the_whole_run(self):
        o = _density(context="SURF_CTX_A")
        object.__setattr__(o, "target_identity", "OTHER")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([o, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)

    def test_unresolved_source_is_hard(self):
        o = _density(context="SURF_CTX_A", source_id="SRC-00000123")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([o, _audit(comp)], comp, unresolved={"SRC-00000123"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_canonical_source_metadata_conflict_is_hard(self):
        o = _density(context="SURF_CTX_A", source_id="SRC-00000124")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([o, _audit(comp)], comp, mismatch={"SRC-00000124"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_context_key_drift_is_hard(self):
        o = _density(context="SURF_CTX_A")
        object.__setattr__(o, "context_key", "OTHER_CTX_KEY")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([o, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_search_scope_drift_is_hard(self):
        o = _density(context="SURF_CTX_A")
        comp = SurfaceAvailabilityCompletion(
            attempted=True, landscape_as_of=AS_OF, search_scope="A DIFFERENT SCOPE",
            sources_searched=("GEO",),
            public_surface_search_complete=True,
            quantitative_surface_density_search_complete=True,
            membranous_ihc_search_complete=True,
            surface_proteomics_search_complete=True,
            subcellular_localization_search_complete=True,
            unresolved_items=(),
            qualifying_direct_surface_context_ids=("SURF_CTX_A",),
            qualifying_indirect_surface_context_ids=(),
            audit_observation_id="OBS-AUDIT-0001",
        )
        res = _run([o, _audit(comp)], comp)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_never_degraded_to_an_accepted_unknown(self):
        o = _density(context="SURF_CTX_A", source_id="SRC-00000125")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([o, _audit(comp)], comp, unresolved={"SRC-00000125"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertGreater(len(res.machine_acceptance.reasons), 0)


class UnknownResolutionTests(unittest.TestCase):
    def test_unresolved_public_item_does_not_add_experiment_required(self):
        i = _ihc(context="SURF_CTX_A")
        comp = _completion(
            qualifying_indirect=("SURF_CTX_A",),
            unresolved=(SurfaceUnresolvedItem("a known QIFIKIT dataset not yet fetched", "KNOWN_PUBLIC_NOT_YET_RESOLVED"),),
        )
        res = _run([i, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertNotIn("EXPERIMENT_REQUIRED", resolutions)

    def test_public_exhausted_localization_only_adds_experiment_required(self):
        i = _ihc(context="SURF_CTX_A")
        comp = _completion(qualifying_indirect=("SURF_CTX_A",))
        res = _run([i, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        resolutions = {r for _, r in res.proposal_envelope.critical_unknowns}
        self.assertIn("EXPERIMENT_REQUIRED", resolutions)


class OutputSurfaceTests(unittest.TestCase):
    def test_accepted_run_output_surface(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertIsInstance(res.machine_acceptance, MachineAcceptanceRecord)
        self.assertIsInstance(res.surface_completion, SurfaceAvailabilityCompletion)
        self.assertIsInstance(res.fatal_review, FatalReviewRecord)
        self.assertEqual(res.proposal_envelope.evidence_ceiling, TGT04_EVIDENCE_CEILING)
        self.assertEqual(res.proposal_envelope.context_id, CTX_ID)

    def test_gate_neutral_packages_carry_no_gate_conclusion(self):
        d = _density(context="SURF_CTX_A")
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        for ep in res.evidence_packages:
            ib = " ".join(ep.interpretation_boundary["directly_supports"]).lower()
            self.assertNotIn("passes tgt-04", ib)
            self.assertNotIn("adequate antigen density established", ib)
            self.assertNotIn("kill", ib)

    def test_proposal_omits_canonical_only_fields(self):
        names = AssessmentProposalEnvelope.field_names()
        for f in ("assessment_id", "assessment_version", "review"):
            self.assertNotIn(f, names)


class ReviewRound1RegressionTests(unittest.TestCase):
    """PR E12 ChatGPT AI审核方案 review round 1 -- 3 narrow runtime blockers.

    (1) a raw factual reported_density_* value / unit / summary an EP is
        sanctioned to preserve must NOT be mis-killed by acceptance.py's numeric
        / threshold scan;
    (2) the typed multi-context conflict resolver must ALSO require the
        observation's CLASSIFIED density_implication == CONTEXTUAL -- an actual
        OPPOSES observation (surface_antigen_level == NEGLIGIBLE_OR_UNDETECTABLE)
        may never impersonate the resolver;
    (3) raw-density exact-reuse parity is SYMMETRIC: a canonical package that
        omits the raw density keys is "absent" -- absent on both sides is
        compatible; present on one side only is HARD.
    """

    # ---- blocker 1 ---------------------------------------------------------
    def test_raw_density_summary_with_a_number_is_accepted(self):
        d = _density(
            context="SURF_CTX_A",
            plausibility="PLAUSIBLY_ADEQUATE",
            value="12000",
            unit="molecules/cell",
            summary="12000 molecules per cell by QIFIKIT",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))

    def test_a_real_threshold_conclusion_would_still_be_rejected(self):
        # the guard still fires on decision language, not on a raw factual value.
        from gate_modules.tgt04_tumor_surface_availability_density_plausibility.acceptance import (
            _SCORE_RE,
        )
        self.assertIsNotNone(_SCORE_RE.search("antigen density above the clinically effective range"))
        self.assertIsNotNone(_SCORE_RE.search("apply a density cutoff of 5000 as a decision rule"))
        self.assertIsNotNone(_SCORE_RE.search("h-score threshold"))
        self.assertIsNone(_SCORE_RE.search("source reported ~12000 molecules per cell by QIFIKIT"))

    # ---- blocker 2 ---------------------------------------------------------
    def test_multi_context_mixed_with_quantitatively_present_may_resolve_conflict(self):
        a = _density(observation_id="OBS-DENS-RR1", context="SURF_CTX_A", plausibility="PLAUSIBLY_ADEQUATE")
        b = _density(observation_id="OBS-DENS-RR2", context="SURF_CTX_B",
                     antigen_level="NEGLIGIBLE_OR_UNDETECTABLE", plausibility="NOT_ESTABLISHED")
        resolver = _density(
            observation_id="OBS-DENS-RR3",
            context="",
            context_ids=("SURF_CTX_A", "SURF_CTX_B"),
            declared_multi_context=True,
            antigen_level="QUANTITATIVELY_PRESENT",
            plausibility="MIXED_OR_UNRESOLVED",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, b, resolver, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))

    def test_multi_context_mixed_with_negligible_antigen_is_opposes_not_a_resolver(self):
        a = _density(observation_id="OBS-DENS-RR4", context="SURF_CTX_A", plausibility="PLAUSIBLY_ADEQUATE")
        # this observation is classified OPPOSES (NEGLIGIBLE_OR_UNDETECTABLE wins
        # the density mapping) -- it must NOT be treated as the resolver.
        fake_resolver = _density(
            observation_id="OBS-DENS-RR5",
            context="",
            context_ids=("SURF_CTX_A", "SURF_CTX_B"),
            declared_multi_context=True,
            antigen_level="NEGLIGIBLE_OR_UNDETECTABLE",
            plausibility="MIXED_OR_UNRESOLVED",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        res = _run([a, fake_resolver, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("CONFLICTING", "DIRECT"))

    # ---- blocker 3 ---------------------------------------------------------
    def _canonical_no_density_keys(self, o, evidence_id="EP-00009500"):
        keys = (
            "observation_id", "target_identity", "context_key", "landscape_as_of",
            "observation_kind", "molecular_layer", "assay_method",
            "measurement_validation_status", "measurement_validation_basis", "crc_specific",
            "surface_context_class", "surface_context_basis", "context_adequacy_status",
            "context_adequacy_basis", "malignant_cell_attribution", "malignant_attribution_basis",
            "surface_localization_status", "surface_localization_basis",
            "density_plausibility_status", "density_plausibility_basis",
            "surface_antigen_level", "surface_antigen_level_basis",
            "reproducibility_status", "reproducibility_basis",
            "surface_context_id", "surface_context_ids", "declared_multi_context_analysis",
        )
        sc = {k: getattr(o, k) for k in keys}
        sc.update(indication="colorectal_cancer", treatment_state="not_applicable",
                  sample_type="crc_malignant_cell_quantitative_surface_density")
        return EvidencePackage(
            evidence_id=evidence_id, schema_version=1, claim=o.claim,
            measurement={"type": "x", "analyte": o.target_identity, "readout": "r",
                         "result": "res", "unit": ""},
            candidate_refs=(CAND,), study_context=sc,
            provenance={
                "source_id": o.source_id, "source_type": o.source_type,
                "source_identifier": o.source_identifier, "locator": o.locator,
                "retrieved_at": o.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": ("x",), "does_not_support": ("y",),
                "limitations": ("z",), "evidence_ceiling": "c",
            },
            derivation={"module_run_id": "RUN-E12-TEST", "code_commit": "deadbeef"},
        )

    def _run_reuse(self, o, canonical):
        comp = _completion(qualifying_direct=(o.surface_context_id,))
        return _run([o, _audit(comp)], comp,
                    library={o.observation_id: canonical}, allocator=FakeAllocator(60))

    def test_canonical_missing_raw_keys_current_all_empty_is_reused(self):
        o = _density(observation_id="OBS-DENS-RR6", context="SURF_CTX_A")
        can = self._canonical_no_density_keys(o, evidence_id="EP-00009501")
        res = self._run_reuse(o, can)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIn("EP-00009501", res.reused_evidence_ids)

    def test_canonical_missing_raw_keys_current_value_present_is_hard(self):
        o = _density(observation_id="OBS-DENS-RR7", context="SURF_CTX_A", value="12000")
        can = self._canonical_no_density_keys(o, evidence_id="EP-00009502")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)


class ReviewRound2RegressionTests(unittest.TestCase):
    """PR E12 ChatGPT AI审核方案 review round 2 -- 3 residual integrity blockers
    (round-1's scientific / runtime semantics were basically closed).

    (1) the raw-density redaction in acceptance._scannable_ep_fact_text() was
        order-dependent -- a short value that is a substring of the summary could
        fragment the summary and leave a residual "threshold" to be mis-killed;
    (2) the raw-density reuse parity was not strict EXACT opaque-string parity
        (str()/strip() coercion) -- a canonical int 12000 or "12000 " could match
        a current "12000";
    (3) the duplicate-observation_id HARD reject did not actually precede
        semantic dedup / source resolution / Evidence ID allocation.
    """

    # ---- blocker 1 ---------------------------------------------------------
    def test_raw_density_redaction_is_order_independent(self):
        d = _density(
            context="SURF_CTX_A",
            plausibility="PLAUSIBLY_ADEQUATE",
            value="12000",
            unit="molecules/cell",
            summary="12000 molecules per cell below assay detection threshold",
        )
        comp = _completion(qualifying_direct=("SURF_CTX_A",))
        res = _run([d, _audit(comp)], comp)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))

    def test_score_re_still_fires_on_a_real_threshold_conclusion(self):
        from gate_modules.tgt04_tumor_surface_availability_density_plausibility.acceptance import (
            _SCORE_RE,
        )
        self.assertIsNotNone(_SCORE_RE.search("apply a density threshold of 5000"))
        self.assertIsNotNone(_SCORE_RE.search("above the clinically effective range"))
        self.assertIsNone(_SCORE_RE.search("12000 molecules per cell below assay detection limit"))

    # ---- blocker 2 ---------------------------------------------------------
    def _canonical_with_density(self, o, evidence_id, *, value, unit, summary):
        keys = (
            "observation_id", "target_identity", "context_key", "landscape_as_of",
            "observation_kind", "molecular_layer", "assay_method",
            "measurement_validation_status", "measurement_validation_basis", "crc_specific",
            "surface_context_class", "surface_context_basis", "context_adequacy_status",
            "context_adequacy_basis", "malignant_cell_attribution", "malignant_attribution_basis",
            "surface_localization_status", "surface_localization_basis",
            "density_plausibility_status", "density_plausibility_basis",
            "surface_antigen_level", "surface_antigen_level_basis",
            "reproducibility_status", "reproducibility_basis",
            "surface_context_id", "surface_context_ids", "declared_multi_context_analysis",
        )
        sc = {k: getattr(o, k) for k in keys}
        sc["reported_density_value"] = value
        sc["reported_density_unit"] = unit
        sc["reported_density_summary"] = summary
        sc.update(indication="colorectal_cancer", treatment_state="not_applicable",
                  sample_type="crc_malignant_cell_quantitative_surface_density")
        return EvidencePackage(
            evidence_id=evidence_id, schema_version=1, claim=o.claim,
            measurement={"type": "x", "analyte": o.target_identity, "readout": "r",
                         "result": "res", "unit": str(unit)},
            candidate_refs=(CAND,), study_context=sc,
            provenance={
                "source_id": o.source_id, "source_type": o.source_type,
                "source_identifier": o.source_identifier, "locator": o.locator,
                "retrieved_at": o.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": ("x",), "does_not_support": ("y",),
                "limitations": ("z",), "evidence_ceiling": "c",
            },
            derivation={"module_run_id": "RUN-E12-TEST", "code_commit": "deadbeef"},
        )

    def _run_reuse(self, o, canonical):
        comp = _completion(qualifying_direct=(o.surface_context_id,))
        return _run([o, _audit(comp)], comp,
                    library={o.observation_id: canonical}, allocator=FakeAllocator(70))

    def test_canonical_non_string_raw_value_is_hard(self):
        o = _density(observation_id="OBS-DENS-RR8", context="SURF_CTX_A", value="12000")
        can = self._canonical_with_density(o, "EP-00009601", value=12000, unit="molecules/cell", summary="")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_canonical_raw_value_with_trailing_space_is_hard(self):
        o = _density(observation_id="OBS-DENS-RR9", context="SURF_CTX_A", value="12000")
        can = self._canonical_with_density(o, "EP-00009602", value="12000 ", unit="", summary="")
        res = self._run_reuse(o, can)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(res.hard_integrity_failures)

    def test_canonical_identical_string_raw_facts_are_reused(self):
        o = _density(observation_id="OBS-DENS-RR10", context="SURF_CTX_A",
                     value="12000", unit="molecules/cell", summary="~1.2e4 by QIFIKIT")
        can = self._canonical_with_density(o, "EP-00009603",
                                           value="12000", unit="molecules/cell", summary="~1.2e4 by QIFIKIT")
        res = self._run_reuse(o, can)
        self.assertTrue(res.machine_acceptance.accepted, res.machine_acceptance.reasons)
        self.assertIn("EP-00009603", res.reused_evidence_ids)

    # ---- blocker 3 ---------------------------------------------------------
    def test_duplicate_observation_id_precedes_allocation_and_dedup(self):
        a = _density(observation_id="OBS-DENS-P1", context="SURF_CTX_A")
        b = _density(observation_id="OBS-DENS-P1", context="SURF_CTX_B")
        comp = _completion(qualifying_direct=("SURF_CTX_A", "SURF_CTX_B"))
        alloc = FakeAllocator()
        res = _run([a, b, _audit(comp)], comp, allocator=alloc)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertEqual(alloc.calls, 0)
        self.assertEqual(res.evidence_packages, ())
        self.assertEqual(res.reused_evidence_ids, ())
        why = " ".join(r for _, r in res.hard_integrity_failures)
        self.assertIn("ambiguous observation identity", why)


if __name__ == "__main__":
    unittest.main()
