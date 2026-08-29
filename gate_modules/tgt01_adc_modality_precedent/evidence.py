"""Build atomic PR A ``EvidencePackage`` objects from admissible classified
records. One neutral observation per package, no grade, no direction. Ids come
from the injected allocator -- never from the filesystem. ``(source_id, claim)``
duplicates are dropped.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    TGT01_EVIDENCE_CEILING,
    ClassifiedPrecedent,
    Tgt01ModuleInput,
)
from .ports import EvidenceIdAllocatorPort

# Frozen TGT-01 inference boundary (verbatim), attached to every package so the
# neutral observation still carries the gate's ceiling and forbidden inferences.
_DIRECTLY_SUPPORTS: tuple[str, ...] = (
    "ADC-modality feasibility for this target or its immediate lineage",
)
_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "efficacy in refractory mCRC",
    "normal-tissue safety or a favorable therapeutic index",
    "adequate surface density or internalization for this target",
)


def build_evidence_packages(
    classified: list[ClassifiedPrecedent],
    *,
    module_input: Tgt01ModuleInput,
    allocator: EvidenceIdAllocatorPort,
) -> tuple[tuple[EvidencePackage, ...], dict[str, str], list[tuple[str, str]]]:
    """Return (packages, program_id -> evidence_id, dropped duplicates).

    Only admissible records become packages. Order is preserved. A record whose
    ``(source_id, claim)`` was already emitted is dropped as a duplicate.
    """

    packages: list[EvidencePackage] = []
    by_program: dict[str, str] = {}
    dropped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for item in classified:
        if not item.admissible:
            continue
        record = item.record
        key = (record.source_id, record.claim.strip())
        if key in seen:
            dropped.append((record.program_id, "duplicate (source_id, claim)"))
            continue
        seen.add(key)

        evidence_id = allocator.next_evidence_id()
        limitations = (
            f"TGT-01 evidence class: {item.evidence_class}",
            "single-Gate precedent evidence; establishes no cross-Gate conclusion",
        )
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=record.claim,
            measurement={
                "type": "adc_modality_precedent_observation",
                "analyte": record.target_relation,
                "readout": f"{record.program_stage}/{record.program_status}",
                "result": item.evidence_class,
                "unit": "",
            },
            candidate_refs=(module_input.candidate_id,),
            study_context={
                "indication": "not_applicable_adc_modality_precedent",
                "treatment_state": "not_applicable",
                "sample_type": "not_applicable",
                "program_id": record.program_id,
                "program_stage": record.program_stage,
                "program_status": record.program_status,
                "target_relation": record.target_relation,
            },
            provenance={
                "source_id": record.source_id,
                "source_type": record.source_type,
                "source_identifier": record.source_identifier,
                "locator": record.locator,
                "retrieved_at": record.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": _DIRECTLY_SUPPORTS,
                "does_not_support": _DOES_NOT_SUPPORT,
                "limitations": limitations,
                "evidence_ceiling": TGT01_EVIDENCE_CEILING,
            },
            derivation={
                "module_run_id": module_input.run_id,
                "code_commit": module_input.code_commit,
            },
        )
        packages.append(package)
        by_program[record.program_id] = evidence_id

    return tuple(packages), by_program, dropped
