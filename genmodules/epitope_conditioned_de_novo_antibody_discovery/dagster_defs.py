"""Optional Dagster wrapper for epitope_conditioned_de_novo_antibody_discovery."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dagster import Definitions, In, Nothing, Out, job, op


MODULE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_ROOT))
from run_pipeline import create_run, execute_stage, finalize_run  # noqa: E402


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set {name} before launching the Dagster job")
    return value


@op(out=Out(dict))
def initialize_epitope_discovery_run() -> dict:
    return create_run(
        _required_env("EPITOPE_GENMODULE_INPUT_CONFIG"),
        _required_env("EPITOPE_GENMODULE_OUTPUT_ROOT"),
        mode="execute",
    )


def _stage_op(name: str, stage_id: str):
    @op(name=name, ins={"state": In(dict)}, out=Out(dict))
    def generated_op(state: dict) -> dict:
        return execute_stage(state, stage_id)

    return generated_op


stage_01 = _stage_op("target_biology", "01_target_biology")
stage_02 = _stage_op("antigen_engineering", "02_antigen_engineering")
stage_03 = _stage_op("epitope_engineering", "03_epitope_engineering")
stage_04 = _stage_op("ip_fto_epitope_selection", "04_ip_fto_epitope_selection")
stage_05 = _stage_op("structural_preparation", "05_structural_preparation")
stage_06 = _stage_op("negative_design", "06_negative_design")
stage_07 = _stage_op("de_novo_antibody_design", "07_de_novo_antibody_design")
stage_08 = _stage_op("computational_ranking", "08_computational_ranking")
stage_09 = _stage_op("asset_diversity_optimization", "09_asset_diversity_optimization")
stage_10 = _stage_op("focused_wet_lab_design", "10_focused_wet_lab_design")
stage_11 = _stage_op("structural_validation", "11_structural_validation")
stage_12 = _stage_op("affinity_maturation", "12_affinity_maturation")
stage_13 = _stage_op("adc_readiness", "13_adc_readiness")
stage_14 = _stage_op("patent_package", "14_patent_package")
stage_15 = _stage_op("asset_report", "15_asset_report")


@op(ins={"state": In(dict)}, out=Out(Nothing))
def finalize_epitope_discovery_run(state: dict) -> None:
    finalize_run(state)


@job
def epitope_conditioned_de_novo_antibody_discovery_job():
    state = initialize_epitope_discovery_run()
    state = stage_01(state)
    state = stage_02(state)
    state = stage_03(state)
    state = stage_04(state)
    state = stage_05(state)
    state = stage_06(state)
    state = stage_07(state)
    state = stage_08(state)
    state = stage_09(state)
    state = stage_10(state)
    state = stage_11(state)
    state = stage_12(state)
    state = stage_13(state)
    state = stage_14(state)
    state = stage_15(state)
    finalize_epitope_discovery_run(state)


defs = Definitions(jobs=[epitope_conditioned_de_novo_antibody_discovery_job])
