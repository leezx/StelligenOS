"""Runtime Migration PR E6: MOD-TGT08 deterministic scientific core.

Synthetic, in-memory only -- no network, no real competitor / patent data, no
persistence. The candidate target is ``TARGET_A``; competitor programs are
``PROGRAM_A`` / ``PROGRAM_B``; patent families are ``PATENT_FAMILY_A`` /
``PATENT_FAMILY_B``; the refractory-mCRC context key is ``REFRACTORY_MCRC``.
No HER2 / TROP2 / real target names.

Covers the E6-8 acceptance scenarios: the TGT-08 binding reconciliation
(0.0.0 -> 1.0.0 with MIGRATION_PENDING still in force); the module boundary
(ports only, no network / subprocess / persistence, no generic framework);
input-contract validation (mandatory ``landscape_as_of``); the HARD identity /
provenance integrity gate (candidate<->record target misbinding, unresolved
source, canonical-source drift, incompatible canonical EvidencePackage) which
rejects the WHOLE run and never degrades to an accepted UNKNOWN; exact canonical
EvidencePackage reuse; the frozen E5 competitive / patent classification
mapping; the frozen Direction x Strength truth table (unmet-need-only WEAK
exemption, incomplete-landscape UNKNOWN, weaker-axis overall ceiling, graded
INCONCLUSIVE distinct from UNKNOWN, POSITIVE / NEGATIVE / CONFLICTING); absence
SUPPORT only from an audited completion, never from ``records == []``; the
machine-local ``sponsor_review`` review TRIGGER (never a KILL / STOP_FOR_SPONSOR
/ OUT_OF_MANDATE, never "dominant" / "no differentiation path", never on the
proposal envelope, only actionable on an accepted run); and the accepted-run
output surface (EvidencePackages + two completion states + sponsor_review +
proposal envelope + MachineAcceptanceRecord, never a CandidateGateAssessment).
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import itertools
import unittest
from pathlib import Path

import yaml

from src.objects.crc_adc_target_gateset import BUILT_MODULE_VERSIONS
from src.objects.decision_model import CandidateGateAssessment, EvidencePackage

from gate_modules.tgt08_target_opportunity_competition_ip_whitespace import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    TGT08_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CompetitiveLandscapeCompletion,
    NormalizedOpportunityRecord,
    PatentLandscapeCompletion,
    SponsorReviewRecord,
    Tgt08ModuleInput,
    Tgt08ModuleRunResult,
    run,
)
from gate_modules.tgt08_target_opportunity_competition_ip_whitespace.classify import (
    classify_record,
)
from gate_modules.tgt08_target_opportunity_competition_ip_whitespace.contracts import (
    CANONICAL_ONLY_FIELDS,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt08_target_opportunity_competition_ip_whitespace"
GATESET_YAML = REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"

TARGET_A = "TARGET_A"
CAND = "CAND-L04-000123"
CTX_ID = "CTX-CRC-REFRACTORY"
INST = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CONTEXT_KEY = "REFRACTORY_MCRC"
AS_OF = "2026-08-01"

_SRC_COUNTER = itertools.count(1)


def _next_src() -> str:
    return f"SRC-{next(_SRC_COUNTER):08d}"


# --- deterministic fakes --------------------------------------------------

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
        records: list[NormalizedOpportunityRecord],
        *,
        unresolved: set[str] | None = None,
        mismatch: set[str] | None = None,
    ) -> None:
        from gate_modules.tgt08_target_opportunity_competition_ip_whitespace import (
            CanonicalSourceRecord,
        )

        unresolved = unresolved or set()
        mismatch = mismatch or set()
        self._by_id: dict[str, object] = {}
        for r in records:
            if r.source_id in unresolved:
                continue
            ident = r.source_identifier + ("-DRIFT" if r.source_id in mismatch else "")
            self._by_id.setdefault(
                r.source_id,
                CanonicalSourceRecord(
                    source_id=r.source_id,
                    source_type=r.source_type,
                    source_identifier=ident,
                    locator=r.locator,
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
    def __init__(self, records, competitive, patent) -> None:
        self._records = list(records)
        self._competitive = competitive
        self._patent = patent

    def fetch_records(self, **_):
        return list(self._records)

    def competitive_completion(self, **_):
        return self._competitive

    def patent_completion(self, **_):
        return self._patent


# --- record factories --------------------------------------------------

def _competitor(
    *,
    observation_id: str = "OBS-COMP-1",
    stage: str = "APPROVED",
    status: str = "ACTIVE",
    modality: str = "ADC",
    indication: str = CONTEXT_KEY,
    target: str = TARGET_A,
    authority: str = "TRIAL_REGISTRY",
    source_type: str = "NCT",
    resolved: bool = True,
    program_id: str = "PROGRAM_A",
    source_id: str | None = None,
    as_of: str = AS_OF,
) -> NormalizedOpportunityRecord:
    return NormalizedOpportunityRecord(
        observation_id=observation_id,
        target_identity=target,
        evidence_axis="COMPETITIVE",
        observation_kind="COMPETITOR_PROGRAM",
        claim=f"{program_id} ({modality}) targets {target}; stage {stage}",
        source_id=source_id or _next_src(),
        source_type=source_type,
        source_identifier=f"{program_id}-{observation_id}",
        locator="",
        retrieved_at=as_of,
        source_authority_kind=authority,
        primary_or_official_source_resolved=resolved,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        program_id=program_id,
        modality=modality,
        program_stage=stage,
        program_status=status,
        indication_context_key=indication,
    )


def _patent(
    *,
    observation_id: str = "OBS-PAT-1",
    legal: str = "LIVE",
    category: str = "ADC_COMPOSITION",
    composition: bool = True,
    target: str = TARGET_A,
    authority: str = "PATENT_PUBLICATION",
    family: str = "PATENT_FAMILY_A",
    jurisdiction: str = "US",
    resolved: bool = True,
    source_id: str | None = None,
    as_of: str = AS_OF,
) -> NormalizedOpportunityRecord:
    return NormalizedOpportunityRecord(
        observation_id=observation_id,
        target_identity=target,
        evidence_axis="PATENT",
        observation_kind="PATENT_CLAIM",
        claim=f"{family} contains a {category} claim for {target} ({legal})",
        source_id=source_id or _next_src(),
        source_type="PATENT",
        source_identifier=f"{family}-{observation_id}",
        locator="",
        retrieved_at=as_of,
        source_authority_kind=authority,
        primary_or_official_source_resolved=resolved,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        patent_family_id=family,
        patent_publication_id=f"{family}-A1",
        assignee="ACME_BIO",
        jurisdiction=jurisdiction,
        claim_category=category,
        legal_status=legal,
        composition_level=composition,
    )


def _unmet(
    *, observation_id: str = "OBS-UNMET-1", target: str = TARGET_A, as_of: str = AS_OF
) -> NormalizedOpportunityRecord:
    return NormalizedOpportunityRecord(
        observation_id=observation_id,
        target_identity=target,
        evidence_axis="UNMET_NEED",
        observation_kind="UNMET_NEED_CONTEXT",
        claim="refractory mCRC has poor outcomes after standard-of-care failure",
        source_id=_next_src(),
        source_type="PMID",
        source_identifier=f"unmet-{observation_id}",
        locator="",
        retrieved_at=as_of,
        source_authority_kind="INDICATION_OUTCOME_SOURCE",
        primary_or_official_source_resolved=True,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
    )


_COMP_SCOPE = "primary-source competitive + regulatory sweep"
_COMP_SOURCES = ("TRIAL_REGISTRY", "REGULATORY_SOURCE")
_PAT_SCOPE = "composition-level target-directed ADC claims"
_PAT_SOURCES = ("PATENT_PUBLICATION", "OFFICIAL_PATENT_STATUS")


def _audit(
    axis: str,
    *,
    observation_id: str,
    target: str = TARGET_A,
    as_of: str = AS_OF,
    coverage_complete: bool = True,
    primary: bool = True,
    pipeline: bool = True,
    composition: bool = True,
    target_level: bool = True,
    qualifying: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
    scope: str | None = None,
    sources: tuple[str, ...] | None = None,
    jurisdictions: tuple[str, ...] = ("US", "EP"),
) -> NormalizedOpportunityRecord:
    """A SEARCH_COMPLETION_AUDIT record whose structured snapshot matches a
    default `_comp_completion()` / `_pat_completion()` (E6 round-1 blocker 1).
    Vary the keyword args in lock-step with the paired completion."""
    if axis == "COMPETITIVE":
        extra = dict(
            audit_search_scope=scope or _COMP_SCOPE,
            audit_sources_searched=sources or _COMP_SOURCES,
            audit_coverage_complete=coverage_complete,
            audit_unresolved_items=unresolved,
            audit_primary_source_landscape_complete=primary and coverage_complete,
            audit_pipeline_inventory_complete=pipeline and coverage_complete,
            audit_qualifying_program_ids=qualifying,
        )
    else:
        extra = dict(
            audit_search_scope=scope or _PAT_SCOPE,
            audit_sources_searched=sources or _PAT_SOURCES,
            audit_coverage_complete=coverage_complete,
            audit_unresolved_items=unresolved,
            audit_jurisdictions=jurisdictions,
            audit_composition_level_review_complete=composition and coverage_complete,
            audit_target_level_search_complete=target_level and coverage_complete,
            audit_qualifying_patent_family_ids=qualifying,
        )
    return NormalizedOpportunityRecord(
        observation_id=observation_id,
        target_identity=target,
        evidence_axis=axis,
        observation_kind="SEARCH_COMPLETION_AUDIT",
        claim=f"a {axis.lower()} landscape search for {target} was completed as of {as_of}",
        source_id=_next_src(),
        source_type="OTHER",
        source_identifier=f"audit-{observation_id}",
        locator="",
        retrieved_at=as_of,
        source_authority_kind="SEARCH_AUDIT",
        primary_or_official_source_resolved=True,
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        **extra,
    )


# --- completion factories --------------------------------------------

def _comp_completion(
    *,
    attempted: bool = True,
    coverage_complete: bool = True,
    primary: bool = True,
    pipeline: bool = True,
    audit_obs: str = "OBS-COMP-AUDIT",
    qualifying: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
    as_of: str = AS_OF,
) -> CompetitiveLandscapeCompletion:
    if not attempted:
        return CompetitiveLandscapeCompletion(
            attempted=False,
            coverage_complete=False,
            primary_source_landscape_complete=False,
            pipeline_inventory_complete=False,
            landscape_as_of=as_of,
            search_scope="",
            sources_searched=(),
            unresolved_items=unresolved,
            qualifying_program_ids=(),
            audit_observation_id="",
        )
    return CompetitiveLandscapeCompletion(
        attempted=True,
        coverage_complete=coverage_complete,
        primary_source_landscape_complete=primary and coverage_complete,
        pipeline_inventory_complete=pipeline and coverage_complete,
        landscape_as_of=as_of,
        search_scope=_COMP_SCOPE,
        sources_searched=_COMP_SOURCES,
        unresolved_items=unresolved,
        qualifying_program_ids=qualifying,
        audit_observation_id=audit_obs,
    )


def _pat_completion(
    *,
    attempted: bool = True,
    coverage_complete: bool = True,
    composition: bool = True,
    target_level: bool = True,
    audit_obs: str = "OBS-PAT-AUDIT",
    qualifying: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
    as_of: str = AS_OF,
) -> PatentLandscapeCompletion:
    if not attempted:
        return PatentLandscapeCompletion(
            attempted=False,
            coverage_complete=False,
            composition_level_review_complete=False,
            target_level_search_complete=False,
            landscape_as_of=as_of,
            patent_scope="",
            jurisdictions=(),
            sources_searched=(),
            unresolved_items=unresolved,
            qualifying_patent_family_ids=(),
            audit_observation_id="",
        )
    return PatentLandscapeCompletion(
        attempted=True,
        coverage_complete=coverage_complete,
        composition_level_review_complete=composition and coverage_complete,
        target_level_search_complete=target_level and coverage_complete,
        landscape_as_of=as_of,
        patent_scope=_PAT_SCOPE,
        jurisdictions=("US", "EP"),
        sources_searched=_PAT_SOURCES,
        unresolved_items=unresolved,
        qualifying_patent_family_ids=qualifying,
        audit_observation_id=audit_obs,
    )


def _input(*, existing_evidence_ids: tuple[str, ...] = (), as_of: str = AS_OF) -> Tgt08ModuleInput:
    return Tgt08ModuleInput(
        candidate_id=CAND,
        candidate_name="Candidate A",
        target_identity=TARGET_A,
        instantiation_id=INST,
        context_id=CTX_ID,
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-08",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-TGT08-1",
        code_commit="",
        context_key=CONTEXT_KEY,
        landscape_as_of=as_of,
        retrieval_scope="public primary competitive + regulatory sources",
        patent_scope="composition-level target-directed ADC claims, US/EP",
        jurisdictions=("US", "EP"),
        existing_evidence_ids=tuple(existing_evidence_ids),
    )


def _run(
    records,
    *,
    competitive: CompetitiveLandscapeCompletion | None = None,
    patent: PatentLandscapeCompletion | None = None,
    library: dict[str, EvidencePackage] | None = None,
    unresolved: set[str] | None = None,
    mismatch: set[str] | None = None,
    existing_evidence_ids: tuple[str, ...] = (),
    allocator: FakeAllocator | None = None,
) -> Tgt08ModuleRunResult:
    competitive = competitive or _comp_completion(attempted=False)
    patent = patent or _pat_completion(attempted=False)
    return run(
        _input(existing_evidence_ids=existing_evidence_ids),
        provider=FakeProvider(records, competitive, patent),
        evidence_id_allocator=allocator or FakeAllocator(),
        source_resolver=FakeSourceResolver(records, unresolved=unresolved, mismatch=mismatch),
        evidence_library=FakeEvidenceLibrary(library or {}),
    )


def _classify(rec: NormalizedOpportunityRecord):
    return classify_record(rec, canonical_target_identity=TARGET_A)


def _env(res: Tgt08ModuleRunResult) -> AssessmentProposalEnvelope:
    assert res.proposal_envelope is not None
    return res.proposal_envelope


def _pair(res: Tgt08ModuleRunResult) -> tuple[str, str]:
    env = _env(res)
    return env.proposed_direction, env.proposed_strength


# --- binding reconciliation ------------------------------------------

class BindingReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.gateset = yaml.safe_load(GATESET_YAML.read_text())

    def test_module_yaml_identity(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT08")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e6")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-08")
        self.assertEqual(self.manifest["gate_binding"]["gate_version"], "1.0")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_binding_moved_from_0_0_0_to_1_0_0(self) -> None:
        binding = next(
            b
            for b in self.gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-08"
        )
        self.assertEqual(binding["primary_module_id"], "MOD-TGT08")
        self.assertEqual(binding["primary_module_version"], "1.0.0")
        self.assertEqual(
            self.gateset["primary_module_binding"]["built_module_versions"]["TGT-08"],
            "1.0.0",
        )

    def test_built_module_versions_constant(self) -> None:
        self.assertEqual(
            dict(BUILT_MODULE_VERSIONS),
            {"TGT-01": "1.0.0", "TGT-05": "1.0.0", "TGT-08": "1.0.0"},
        )

    def test_other_tgt_gates_remain_unbuilt(self) -> None:
        for b in self.gateset["context_specific_bindings"]["gate_bindings"]:
            if b["gate_id"] in ("TGT-01", "TGT-05", "TGT-08"):
                continue
            self.assertEqual(b["primary_module_version"], "0.0.0", b["gate_id"])

    def test_migration_pending_remains(self) -> None:
        self.assertIn(
            "per_gate_primary_modules", self.gateset["migration"]["deferred"]
        )
        for flag, value in self.manifest["boundary_flags"].items():
            self.assertFalse(value, flag)


# --- module boundary ------------------------------------------------

class ModuleBoundaryTests(unittest.TestCase):
    FORBIDDEN = {
        "socket", "http", "urllib", "urllib2", "requests", "httpx", "aiohttp",
        "subprocess", "ftplib", "asyncio", "sqlite3", "shelve", "pickle",
        "shutil", "multiprocessing",
    }

    def _sources(self) -> list[Path]:
        return sorted(PKG.rglob("*.py"))

    def _import_roots(self, path: Path) -> set[str]:
        tree = ast.parse(path.read_text(), filename=str(path))
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                roots.add(node.module.split(".")[0])
        return roots

    def test_no_network_subprocess_or_persistence_imports(self) -> None:
        for path in self._sources():
            bad = self._import_roots(path) & self.FORBIDDEN
            self.assertEqual(bad, set(), f"{path.name} imports {bad}")

    def test_module_never_imports_a_sibling_outer_layer(self) -> None:
        for path in self._sources():
            roots = self._import_roots(path)
            self.assertNotIn("extensions", roots)
            self.assertNotIn("genmodules", roots)

    def test_no_filesystem_write_or_eval_in_sources(self) -> None:
        for path in self._sources():
            text = path.read_text()
            for token in ("open(", ".write_text(", ".write_bytes(", "os.system(",
                          "eval(", "exec("):
                self.assertNotIn(token, text, f"{path.name} contains {token!r}")

    def test_run_takes_only_injected_ports(self) -> None:
        params = list(inspect.signature(run).parameters)
        self.assertEqual(
            params,
            ["module_input", "provider", "evidence_id_allocator",
             "source_resolver", "evidence_library"],
        )

    def test_no_generic_gate_module_framework_or_base_class(self) -> None:
        for path in self._sources():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = {getattr(b, "id", getattr(b, "attr", "")) for b in node.bases}
                    self.assertNotIn("ABC", bases, path.name)
                    self.assertFalse(
                        node.name.startswith("GateModule")
                        or node.name.endswith("GateModuleBase"),
                        f"{path.name}:{node.name} looks like a generic framework base",
                    )


# --- input contract ------------------------------------------------

class InputContractTests(unittest.TestCase):
    def test_missing_landscape_as_of_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _input(as_of="")

    def test_non_iso_landscape_as_of_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _input(as_of="August 2026")

    def test_public_only_regime_is_enforced(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(_input(), evidence_regime="PRIVATE_ALLOWED")

    def test_instantiation_binding_is_pinned(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(_input(), instantiation_id="INST-OTHER-CONTEXT-v1")


# --- identity / provenance HARD gate --------------------------------

class IdentityProvenanceGateTests(unittest.TestCase):
    def test_candidate_record_target_misbinding_is_hard(self) -> None:
        res = _run([_competitor(target="SOME_OTHER_TARGET")])
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)

    def test_unresolved_source_is_hard(self) -> None:
        rec = _competitor(source_id="SRC-09990001", stage="EARLY_CLINICAL", status="ACTIVE")
        res = _run([rec], unresolved={"SRC-09990001"})
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)

    def test_canonical_source_metadata_drift_is_hard(self) -> None:
        rec = _competitor(source_id="SRC-09990002", stage="EARLY_CLINICAL")
        res = _run([rec], mismatch={"SRC-09990002"})
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_hard_failure_rejects_whole_run_never_degrades_to_unknown(self) -> None:
        # an otherwise clean audited two-axis landscape, but one misbound record
        ca = _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")
        pa = _audit("PATENT", observation_id="OBS-PAT-AUDIT")
        bad = _competitor(observation_id="OBS-COMP-BAD", target="WRONG_TARGET")
        res = _run(
            [ca, pa, bad],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertFalse(res.sponsor_review.required)

    def test_unresolved_primary_source_flag_is_soft_not_hard(self) -> None:
        rec = _competitor(observation_id="OBS-COMP-LEAD", resolved=False)
        res = _run([rec])
        self.assertFalse(res.hard_integrity_failures)
        self.assertIn(
            "OBS-COMP-LEAD", {oid for oid, _ in res.rejected_records}
        )
        self.assertTrue(res.machine_acceptance.accepted)


# --- exact canonical EvidencePackage reuse --------------------------

class ExactCanonicalReuseTests(unittest.TestCase):
    def _seed_ep(self, rec: NormalizedOpportunityRecord) -> EvidencePackage:
        res = _run([rec])
        self.assertEqual(len(res.evidence_packages), 1)
        return res.evidence_packages[0]

    def test_existing_package_is_reused_verbatim_with_no_allocator_call(self) -> None:
        rec = _competitor(observation_id="OBS-COMP-OI", indication="OTHER_INDICATION")
        ep = self._seed_ep(rec)
        alloc = FakeAllocator(start=500)
        res = _run(
            [rec],
            library={"OBS-COMP-OI": ep},
            existing_evidence_ids=(ep.evidence_id,),
            allocator=alloc,
        )
        self.assertEqual(res.reused_evidence_ids, (ep.evidence_id,))
        self.assertEqual(res.evidence_packages, ())
        self.assertEqual(alloc.calls, 0)

    def test_reused_competitor_package_stage_drift_is_hard(self) -> None:
        rec = _competitor(observation_id="OBS-COMP-OI", indication="OTHER_INDICATION",
                          stage="EARLY_CLINICAL")
        ep = self._seed_ep(rec)
        ctx = dict(ep.study_context)
        ctx["program_stage"] = "APPROVED"
        drifted = dataclasses.replace(ep, study_context=ctx)
        res = _run([rec], library={"OBS-COMP-OI": drifted},
                   existing_evidence_ids=(ep.evidence_id,))
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_reused_patent_package_legal_status_drift_is_hard(self) -> None:
        rec = _patent(observation_id="OBS-PAT-EXP", legal="EXPIRED")
        ep = self._seed_ep(rec)
        ctx = dict(ep.study_context)
        ctx["legal_status"] = "LIVE"
        drifted = dataclasses.replace(ep, study_context=ctx)
        res = _run([rec], library={"OBS-PAT-EXP": drifted},
                   existing_evidence_ids=(ep.evidence_id,))
        self.assertTrue(res.hard_integrity_failures)

    def test_reused_package_missing_classification_field_is_hard(self) -> None:
        rec = _competitor(observation_id="OBS-COMP-OI", indication="OTHER_INDICATION")
        ep = self._seed_ep(rec)
        ctx = dict(ep.study_context)
        del ctx["program_stage"]
        broken = dataclasses.replace(ep, study_context=ctx)
        res = _run([rec], library={"OBS-COMP-OI": broken},
                   existing_evidence_ids=(ep.evidence_id,))
        self.assertTrue(res.hard_integrity_failures)

    def test_reused_package_claim_drift_is_hard(self) -> None:
        rec = _competitor(observation_id="OBS-COMP-OI", indication="OTHER_INDICATION")
        ep = self._seed_ep(rec)
        drifted = dataclasses.replace(ep, claim=ep.claim + " (edited)")
        res = _run([rec], library={"OBS-COMP-OI": drifted},
                   existing_evidence_ids=(ep.evidence_id,))
        self.assertTrue(res.hard_integrity_failures)


# --- frozen competitive / patent classification -------------------

class CompetitiveClassificationTests(unittest.TestCase):
    def test_approved_same_context_opposes(self) -> None:
        c = _classify(_competitor(stage="APPROVED"))
        self.assertTrue(c.admissible)
        self.assertEqual(c.opportunity_implication, "OPPOSES_OPPORTUNITY")
        self.assertTrue(c.qualifying_for_axis)

    def test_registrational_same_context_opposes(self) -> None:
        c = _classify(_competitor(stage="REGISTRATIONAL"))
        self.assertEqual(c.opportunity_implication, "OPPOSES_OPPORTUNITY")

    def test_active_clinical_same_context_opposes(self) -> None:
        c = _classify(_competitor(stage="ACTIVE_CLINICAL"))
        self.assertEqual(c.opportunity_implication, "OPPOSES_OPPORTUNITY")
        self.assertTrue(c.qualifying_for_axis)

    def test_discontinued_competitor_is_contextual_never_supports(self) -> None:
        c = _classify(_competitor(stage="ACTIVE_CLINICAL", status="DISCONTINUED"))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")
        self.assertFalse(c.qualifying_for_axis)

    def test_failed_competitor_is_contextual(self) -> None:
        c = _classify(_competitor(stage="APPROVED", status="FAILED"))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")

    def test_other_indication_competitor_is_contextual(self) -> None:
        c = _classify(_competitor(stage="APPROVED", indication="OTHER_INDICATION"))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")
        self.assertFalse(c.qualifying_for_axis)

    def test_early_preclinical_competitor_is_contextual(self) -> None:
        c = _classify(_competitor(stage="PRECLINICAL", status="ACTIVE"))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")


class PatentClassificationTests(unittest.TestCase):
    def test_live_composition_level_adc_claim_opposes_and_qualifies(self) -> None:
        c = _classify(_patent(legal="LIVE", category="ADC_COMPOSITION", composition=True))
        self.assertEqual(c.opportunity_implication, "OPPOSES_OPPORTUNITY")
        self.assertTrue(c.qualifying_for_axis)
        self.assertTrue(c.record.patent_is_composition_level_adc_claim)

    def test_live_target_level_only_patent_hit_opposes(self) -> None:
        c = _classify(_patent(legal="LIVE", category="METHOD_OF_USE", composition=False))
        self.assertEqual(c.opportunity_implication, "OPPOSES_OPPORTUNITY")
        self.assertTrue(c.qualifying_for_axis)
        self.assertFalse(c.record.patent_is_composition_level_adc_claim)

    def test_expired_patent_is_contextual_never_whitespace(self) -> None:
        c = _classify(_patent(legal="EXPIRED"))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")
        self.assertFalse(c.qualifying_for_axis)

    def test_abandoned_patent_is_contextual(self) -> None:
        c = _classify(_patent(legal="ABANDONED"))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")

    def test_irrelevant_category_patent_is_contextual(self) -> None:
        c = _classify(_patent(legal="LIVE", category="IRRELEVANT", composition=False))
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")

    def test_unmet_need_context_is_contextual(self) -> None:
        c = _classify(_unmet())
        self.assertEqual(c.opportunity_implication, "CONTEXTUAL")
        self.assertFalse(c.qualifying_for_axis)


# --- frozen Direction x Strength truth table ---------------------

class AggregationTruthTableTests(unittest.TestCase):
    def test_unmet_need_only_neither_axis_attempted_is_inconclusive_weak(self) -> None:
        res = _run([_unmet()])
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "WEAK"))
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertTrue(_env(res).evidence_refs)
        self.assertEqual({r for _, r in _env(res).evidence_refs}, {"CONTEXTUAL"})

    def test_no_admissible_landscape_at_all_is_inconclusive_unknown(self) -> None:
        res = _run([])
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(_env(res).evidence_refs, ())

    def test_target_specific_attempted_but_patent_axis_unsearched_is_unknown(self) -> None:
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(attempted=False),
        )
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(_env(res).evidence_refs, ())

    def test_incomplete_competitive_axis_is_unknown(self) -> None:
        res = _run(
            [],
            competitive=_comp_completion(coverage_complete=False),
            patent=_pat_completion(),
        )
        self.assertEqual(_pair(res)[1], "UNKNOWN")

    def test_both_axes_indirect_strong_supporting_only_is_positive_indirect_strong(self) -> None:
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT", primary=False),
             _audit("PATENT", observation_id="OBS-PAT-AUDIT", composition=False)],
            competitive=_comp_completion(primary=False, audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(composition=False, audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertEqual(_pair(res), ("POSITIVE", "INDIRECT_STRONG"))
        self.assertIn("SUPPORTING", {r for _, r in _env(res).evidence_refs})

    def test_competitive_direct_patent_indirect_strong_overall_indirect_strong(self) -> None:
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT"),
             _audit("PATENT", observation_id="OBS-PAT-AUDIT", composition=False)],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(composition=False, audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertEqual(_pair(res), ("POSITIVE", "INDIRECT_STRONG"))

    def test_both_axes_direct_supporting_only_is_positive_direct(self) -> None:
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT"),
             _audit("PATENT", observation_id="OBS-PAT-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertEqual(_pair(res), ("POSITIVE", "DIRECT"))

    def test_opposing_only_is_negative_and_never_a_kill(self) -> None:
        comp = _competitor(stage="ACTIVE_CLINICAL", program_id="PROGRAM_A")
        pat = _patent(legal="LIVE", category="METHOD_OF_USE", composition=False,
                      family="PATENT_FAMILY_A")
        res = _run(
            [comp, pat],
            competitive=_comp_completion(audit_obs="OBS-COMP-CERT",
                                         qualifying=("PROGRAM_A",)),
            patent=_pat_completion(composition=False, audit_obs="OBS-PAT-CERT",
                                   qualifying=("PATENT_FAMILY_A",)),
        )
        self.assertEqual(_env(res).proposed_direction, "NEGATIVE")
        self.assertIn("not a kill", _env(res).aggregation_rationale.lower())
        self.assertFalse(res.sponsor_review.required)
        self.assertTrue(res.machine_acceptance.accepted)

    def test_supporting_and_opposing_is_conflicting(self) -> None:
        comp = _competitor(stage="APPROVED", program_id="PROGRAM_A",
                           authority="PIPELINE_DATABASE", source_type="DATASET")
        res = _run(
            [comp, _audit("PATENT", observation_id="OBS-PAT-AUDIT")],
            competitive=_comp_completion(primary=False, audit_obs="OBS-COMP-CERT",
                                         qualifying=("PROGRAM_A",)),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertEqual(_env(res).proposed_direction, "CONFLICTING")
        roles = {r for _, r in _env(res).evidence_refs}
        self.assertLessEqual({"SUPPORTING", "CONTRADICTING"}, roles)

    def test_completed_direct_landscape_no_directional_signal_is_graded_inconclusive_direct(self) -> None:
        # both axes coverage-complete at DIRECT authority, only CONTEXTUAL
        # observations, and no clean-absence audit EP in the run.
        res = _run(
            [_competitor(observation_id="OBS-COMP-OI", indication="OTHER_INDICATION",
                         program_id="PROGRAM_B"),
             _patent(observation_id="OBS-PAT-EXP", legal="EXPIRED",
                     family="PATENT_FAMILY_B")],
            competitive=_comp_completion(audit_obs="OBS-COMP-CERT"),
            patent=_pat_completion(audit_obs="OBS-PAT-CERT"),
        )
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "DIRECT"))
        self.assertEqual({r for _, r in _env(res).evidence_refs}, {"CONTEXTUAL"})

    def test_completed_indirect_landscape_no_directional_signal_is_graded_inconclusive_indirect(self) -> None:
        res = _run(
            [_competitor(observation_id="OBS-COMP-OI", indication="OTHER_INDICATION",
                         program_id="PROGRAM_B")],
            competitive=_comp_completion(primary=False, audit_obs="OBS-COMP-CERT"),
            patent=_pat_completion(composition=False, audit_obs="OBS-PAT-CERT"),
        )
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "INDIRECT_STRONG"))

    def test_direction_strength_pair_is_always_a_legal_tgt08_pair(self) -> None:
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT"),
             _audit("PATENT", observation_id="OBS-PAT-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertIn(_pair(res), LEGAL_DIRECTION_STRENGTH_PAIRS)

    def test_unmet_need_never_converts_opposing_landscape_into_conflicting(self) -> None:
        comp = _competitor(stage="APPROVED", program_id="PROGRAM_A",
                           authority="PIPELINE_DATABASE", source_type="DATASET")
        res = _run(
            [comp, _unmet()],
            competitive=_comp_completion(primary=False, audit_obs="OBS-COMP-CERT",
                                         qualifying=("PROGRAM_A",)),
            patent=_pat_completion(composition=False, audit_obs="OBS-PAT-CERT"),
        )
        self.assertEqual(_env(res).proposed_direction, "NEGATIVE")


# --- absence inference ------------------------------------------

class AbsenceInferenceTests(unittest.TestCase):
    def test_audited_complete_competitive_zero_qualifying_supports_via_audit_ep(self) -> None:
        ca = _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")
        pa = _audit("PATENT", observation_id="OBS-PAT-AUDIT")
        res = _run(
            [ca, pa],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        env = _env(res)
        self.assertEqual(env.proposed_direction, "POSITIVE")
        support_ids = {eid for eid, role in env.evidence_refs if role == "SUPPORTING"}
        audit_ids = {
            ep.evidence_id
            for ep in res.evidence_packages
            if ep.study_context["observation_kind"] == "SEARCH_COMPLETION_AUDIT"
        }
        self.assertTrue(support_ids)
        self.assertLessEqual(support_ids, audit_ids)

    def test_empty_record_set_without_an_audit_never_supports(self) -> None:
        res = _run([])
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(_env(res).evidence_refs, ())

    def test_no_patent_records_without_a_completion_audit_is_not_whitespace(self) -> None:
        # competitive is audited clean, but the patent axis was never searched:
        # the run must not become POSITIVE / whitespace off the empty patent set.
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(attempted=False),
        )
        self.assertEqual(_pair(res), ("INCONCLUSIVE", "UNKNOWN"))

    def test_completion_claims_zero_competitor_but_a_qualifying_ep_exists_rejects_run(self) -> None:
        comp = _competitor(stage="APPROVED", program_id="PROGRAM_A")
        res = _run(
            [comp, _audit("PATENT", observation_id="OBS-PAT-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-CERT", qualifying=()),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("qualifying_program_ids" in r for r in res.machine_acceptance.reasons)
        )

    def test_completion_claims_zero_patent_family_but_a_qualifying_live_ep_exists_rejects_run(self) -> None:
        pat = _patent(legal="LIVE", category="ADC_COMPOSITION", composition=True,
                      family="PATENT_FAMILY_A")
        res = _run(
            [pat, _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-CERT", qualifying=()),
        )
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(
            any("qualifying_patent_family_ids" in r for r in res.machine_acceptance.reasons)
        )

    def test_completion_audit_evidence_package_carries_canonical_source_provenance(self) -> None:
        ca = _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")
        pa = _audit("PATENT", observation_id="OBS-PAT-AUDIT")
        res = _run(
            [ca, pa],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        audit_eps = [
            ep for ep in res.evidence_packages
            if ep.study_context["observation_kind"] == "SEARCH_COMPLETION_AUDIT"
        ]
        self.assertEqual(len(audit_eps), 2)
        for ep in audit_eps:
            self.assertTrue(ep.provenance["source_id"].startswith("SRC-"))
            self.assertEqual(ep.provenance["source_type"], "OTHER")
            self.assertTrue(ep.provenance["retrieved_at"].startswith("2026-"))


# --- completion audit snapshot parity (E6 round-1 blocker 1) -----

class AuditCompletionSnapshotParityTests(unittest.TestCase):
    """A SEARCH_COMPLETION_AUDIT EvidencePackage that names a completion's
    audit_observation_id must carry a structured snapshot equal to that typed
    completion. Any drift is a HARD run-level integrity failure -- the machine
    never derives an axis ceiling or an absence inference from an audit whose
    own snapshot disagrees with the completion it certifies."""

    def _run_comp_audit(self, audit: NormalizedOpportunityRecord) -> Tgt08ModuleRunResult:
        return _run(
            [audit],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(attempted=False),
        )

    def _assert_hard(self, res: Tgt08ModuleRunResult) -> None:
        self.assertTrue(res.hard_integrity_failures)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)

    def test_audit_snapshot_search_scope_drift_is_hard(self) -> None:
        self._assert_hard(self._run_comp_audit(
            _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT",
                   scope="an entirely different declared scope")))

    def test_audit_snapshot_sources_drift_is_hard(self) -> None:
        self._assert_hard(self._run_comp_audit(
            _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT",
                   sources=("PIPELINE_DATABASE",))))

    def test_audit_snapshot_coverage_flag_drift_is_hard(self) -> None:
        self._assert_hard(self._run_comp_audit(
            _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT",
                   coverage_complete=False)))

    def test_audit_snapshot_direct_authority_flag_drift_is_hard(self) -> None:
        self._assert_hard(self._run_comp_audit(
            _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT", primary=False)))

    def test_audit_snapshot_qualifying_program_set_drift_is_hard(self) -> None:
        self._assert_hard(self._run_comp_audit(
            _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT",
                   qualifying=("PROGRAM_GHOST",))))

    def test_audit_snapshot_patent_jurisdiction_drift_is_hard(self) -> None:
        res = _run(
            [_audit("PATENT", observation_id="OBS-PAT-AUDIT", jurisdictions=("JP",))],
            competitive=_comp_completion(attempted=False),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )
        self._assert_hard(res)

    def test_snapshot_consistent_audit_is_accepted(self) -> None:
        # the control: a faithful snapshot backs the completion and the run
        # reaches an accepted INCONCLUSIVE / UNKNOWN (patent axis unsearched).
        res = self._run_comp_audit(
            _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT"))
        self.assertFalse(res.hard_integrity_failures)
        self.assertTrue(res.machine_acceptance.accepted)

    def test_reused_completion_audit_ep_snapshot_drift_is_hard(self) -> None:
        audit = _audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")
        seed = self._run_comp_audit(audit)
        self.assertEqual(len(seed.evidence_packages), 1)
        ep = seed.evidence_packages[0]
        ctx = dict(ep.study_context)
        ctx["audit_search_scope"] = "a canonical package recorded under a different scope"
        drifted = dataclasses.replace(ep, study_context=ctx)
        res = _run(
            [audit],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(attempted=False),
            library={"OBS-COMP-AUDIT": drifted},
            existing_evidence_ids=(ep.evidence_id,),
        )
        self._assert_hard(res)


# --- machine-local sponsor_review TRIGGER --------------------

class SponsorReviewTests(unittest.TestCase):
    def _trigger_run(self, *, incomplete: str | None = None, **over) -> Tgt08ModuleRunResult:
        comp = _competitor(stage=over.get("stage", "APPROVED"),
                           modality=over.get("modality", "ADC"),
                           authority=over.get("comp_authority", "TRIAL_REGISTRY"),
                           source_type=over.get("source_type", "NCT"),
                           program_id="PROGRAM_A")
        pat = _patent(legal="LIVE",
                      category=over.get("category", "ADC_COMPOSITION"),
                      composition=over.get("composition", True),
                      authority=over.get("pat_authority", "PATENT_PUBLICATION"),
                      family="PATENT_FAMILY_A")
        comp_kw = dict(audit_obs="OBS-COMP-CERT", qualifying=("PROGRAM_A",),
                       coverage_complete=incomplete != "competitive")
        pat_kw = dict(audit_obs="OBS-PAT-CERT", qualifying=("PATENT_FAMILY_A",),
                      coverage_complete=incomplete != "patent")
        return _run(
            [comp, pat],
            competitive=_comp_completion(**comp_kw),
            patent=_pat_completion(**pat_kw),
        )

    def test_approved_adc_plus_live_composition_patent_triggers_potential_pattern(self) -> None:
        res = self._trigger_run()
        sr = res.sponsor_review
        self.assertTrue(sr.required)
        self.assertEqual(sr.status, "POTENTIAL_SPONSOR_FATAL_PATTERN")
        self.assertEqual(sr.competitor_program_ids, ("PROGRAM_A",))
        self.assertEqual(sr.patent_family_ids, ("PATENT_FAMILY_A",))
        self.assertEqual(sr.landscape_as_of, AS_OF)
        self.assertEqual(sr.patent_scope, _input().patent_scope)
        self.assertTrue(sr.evidence_ids)

    def test_active_clinical_non_registrational_adc_alone_does_not_trigger(self) -> None:
        res = self._trigger_run(stage="ACTIVE_CLINICAL")
        self.assertFalse(res.sponsor_review.required)

    def test_non_adc_approved_competitor_may_oppose_but_does_not_trigger(self) -> None:
        res = self._trigger_run(modality="NAKED_ANTIBODY")
        self.assertFalse(res.sponsor_review.required)
        self.assertEqual(res.proposal_envelope.proposed_direction, "NEGATIVE")

    def test_qualifying_adc_competitor_without_composition_patent_does_not_trigger(self) -> None:
        res = self._trigger_run(category="METHOD_OF_USE", composition=False)
        self.assertFalse(res.sponsor_review.required)

    def test_pipeline_database_competitor_is_not_a_primary_source_trigger(self) -> None:
        res = self._trigger_run(comp_authority="PIPELINE_DATABASE", source_type="DATASET")
        self.assertFalse(res.sponsor_review.required)

    def test_sponsor_trigger_is_only_actionable_on_an_accepted_run(self) -> None:
        comp = _competitor(stage="APPROVED", program_id="PROGRAM_A")
        pat = _patent(legal="LIVE", category="ADC_COMPOSITION", composition=True,
                      family="PATENT_FAMILY_A")
        # completion inconsistency -> run rejected -> trigger must not surface
        res = _run(
            [comp, pat],
            competitive=_comp_completion(audit_obs="OBS-COMP-CERT", qualifying=()),
            patent=_pat_completion(audit_obs="OBS-PAT-CERT",
                                   qualifying=("PATENT_FAMILY_A",)),
        )
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertFalse(res.sponsor_review.required)
        self.assertEqual(res.sponsor_review.status, "")

    def test_sponsor_pattern_on_incomplete_competitive_axis_is_not_accepted(self) -> None:
        # E6 round-1 blocker 2: a sponsor_review handoff is a provisional stop
        # (E5 item 16) -- it must not surface as actionable while a core axis is
        # still incomplete (the run would otherwise be an accepted
        # INCONCLUSIVE / UNKNOWN).
        res = self._trigger_run(incomplete="competitive")
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertFalse(res.sponsor_review.required)
        self.assertEqual(res.sponsor_review.status, "")
        self.assertTrue(
            any("both core" in r or "incomplete two-axis" in r
                for r in res.machine_acceptance.reasons)
        )

    def test_sponsor_pattern_on_incomplete_patent_axis_is_not_accepted(self) -> None:
        res = self._trigger_run(incomplete="patent")
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertFalse(res.sponsor_review.required)

    def test_sponsor_pattern_with_both_axes_complete_is_accepted_and_surfaced(self) -> None:
        res = self._trigger_run()
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertTrue(res.sponsor_review.required)
        self.assertEqual(res.sponsor_review.status, "POTENTIAL_SPONSOR_FATAL_PATTERN")

    def test_sponsor_review_is_absent_from_the_proposal_envelope(self) -> None:
        names = AssessmentProposalEnvelope.field_names()
        for token in ("sponsor", "fatal", "kill", "review"):
            self.assertFalse(any(token in n for n in names), token)
        for canonical in CANONICAL_ONLY_FIELDS:
            self.assertNotIn(canonical, names)

    def test_machine_never_asserts_dominant_or_no_differentiation_path(self) -> None:
        res = self._trigger_run()
        self.assertTrue(res.machine_acceptance.accepted)
        # scan the asserted facts (directly_supports + evidence_class) and the
        # rationale -- NOT the neutral does_not_support disclaimer, which names
        # these very phrases precisely to say the package makes no such claim.
        blob = _env(res).aggregation_rationale.lower()
        for ep in res.evidence_packages:
            blob += " " + " ".join(ep.interpretation_boundary["directly_supports"]).lower()
        for banned in ("dominant", "well protected", "well-protected",
                       "no differentiation path", "crowded target", "fto blocked"):
            self.assertNotIn(banned, blob, banned)


# --- accepted-run output surface -------------------------------

class OutputSurfaceTests(unittest.TestCase):
    def _clean_positive(self) -> Tgt08ModuleRunResult:
        return _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT"),
             _audit("PATENT", observation_id="OBS-PAT-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(audit_obs="OBS-PAT-AUDIT"),
        )

    def test_accepted_run_output_shape(self) -> None:
        res = self._clean_positive()
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertTrue(all(isinstance(ep, EvidencePackage) for ep in res.evidence_packages))
        self.assertIsInstance(res.competitive_completion, CompetitiveLandscapeCompletion)
        self.assertIsInstance(res.patent_completion, PatentLandscapeCompletion)
        self.assertIsInstance(res.sponsor_review, SponsorReviewRecord)
        self.assertEqual(res.machine_acceptance.reasons, ())

    def test_module_never_constructs_a_candidate_gate_assessment(self) -> None:
        res = self._clean_positive()
        self.assertNotIsInstance(res.proposal_envelope, CandidateGateAssessment)
        for ep in res.evidence_packages:
            self.assertNotIsInstance(ep, CandidateGateAssessment)

    def test_evidence_ceiling_lives_on_the_envelope_not_the_packages(self) -> None:
        res = self._clean_positive()
        self.assertEqual(res.proposal_envelope.evidence_ceiling, TGT08_EVIDENCE_CEILING)
        for ep in res.evidence_packages:
            self.assertNotEqual(
                ep.interpretation_boundary["evidence_ceiling"], TGT08_EVIDENCE_CEILING
            )

    def test_critical_unknowns_never_use_experiment_required(self) -> None:
        res = _run(
            [_audit("COMPETITIVE", observation_id="OBS-COMP-AUDIT")],
            competitive=_comp_completion(audit_obs="OBS-COMP-AUDIT"),
            patent=_pat_completion(attempted=False, unresolved=("an open FTO question",)),
        )
        resolutions = {r for _, r in _env(res).critical_unknowns}
        self.assertTrue(resolutions)
        self.assertLessEqual(resolutions, {"PUBLIC_RESOLVABLE", "CURRENTLY_UNRESOLVABLE"})

    def test_one_evidence_package_per_observation(self) -> None:
        res = self._clean_positive()
        ids = [ep.evidence_id for ep in res.evidence_packages]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 2)


if __name__ == "__main__":
    unittest.main()
