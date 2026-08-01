"""Optional Dagster wrapper for antibody_binder_asset_engineering@0.3.1.

Configure with:
  ANTIBODY_GENMODULE_BINDER_CONFIG
  ANTIBODY_GENMODULE_OUTPUT_ROOT
  ANTIBODY_GENMODULE_ALLOW_EXTERNAL  (optional; "1"/"true" enables structure prediction)

The op chain is generated from ``EXECUTION_ORDER`` rather than hand-listed, so it
cannot drift from the CLI. The order matters: 07_experimental_design consumes
09_adc_readiness output to lead with the gating experiments, so running the stages
in declared numeric order would silently emit an experimental package with the
decisive experiments missing.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dagster import Definitions, In, Nothing, Out, job, op

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from run_pipeline import create_run, execute_stage, finalize_run  # noqa: E402
from stages import EXECUTION_ORDER  # noqa: E402


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set {name} before launching the Dagster job")
    return value


def _flag(name: str) -> bool:
    return str(os.environ.get(name, "")).strip().casefold() in {"1", "true", "yes", "on"}


@op(out=Out(dict))
def initialize_antibody_asset_run() -> dict:
    return create_run(
        _required_env("ANTIBODY_GENMODULE_BINDER_CONFIG"),
        _required_env("ANTIBODY_GENMODULE_OUTPUT_ROOT"),
        mode="execute",
        allow_external=_flag("ANTIBODY_GENMODULE_ALLOW_EXTERNAL"),
    )


def _stage_op(stage_id: str):
    # Op names must be valid identifiers, so strip the numeric prefix.
    op_name = stage_id.split("_", 1)[1]

    @op(name=op_name, ins={"state": In(dict)}, out=Out(dict))
    def generated_op(state: dict, _stage_id: str = stage_id) -> dict:
        return execute_stage(state, _stage_id)

    return generated_op


STAGE_OPS = tuple(_stage_op(stage_id) for stage_id in EXECUTION_ORDER)


@op(ins={"state": In(dict)}, out=Out(Nothing))
def finalize_antibody_asset_run(state: dict) -> None:
    finalize_run(state)


@job
def antibody_binder_asset_engineering_job():
    state = initialize_antibody_asset_run()
    for stage_op in STAGE_OPS:
        state = stage_op(state)
    finalize_antibody_asset_run(state)


defs = Definitions(jobs=[antibody_binder_asset_engineering_job])
