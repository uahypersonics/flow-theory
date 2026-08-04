"""Runner for [boundary_layer_thickness] workflow sections."""

from __future__ import annotations

import numpy as np
import typer

from flow_theory.boundary_layer import compute_boundary_layer_thickness
from flow_theory.config import BoundaryLayerThicknessConfig
from flow_theory.io import write_tecplot
from flow_theory.runners.common import as_float_list, broadcast_sweep


def run_boundary_layer_thickness(config: BoundaryLayerThicknessConfig) -> None:
    """Execute boundary-layer thickness calculations."""

    # build required sweep inputs
    sweep_inputs = {
        "x": as_float_list(config.x, "boundary_layer_thickness.x"),
        "re1": as_float_list(config.re1, "boundary_layer_thickness.re1"),
    }

    # add thermal inputs only for the reference-temperature method
    if config.method == "eckert_reference":
        sweep_inputs["mach"] = as_float_list(
            config.mach,
            "boundary_layer_thickness.mach",
        )
        sweep_inputs["tw_t0"] = as_float_list(
            config.tw_t0,
            "boundary_layer_thickness.tw_t0",
        )

    # align scalar and list inputs to one common case count
    swept = broadcast_sweep(**sweep_inputs)
    n_cases = swept["x"].size

    # evaluate each aligned case
    re_x_values: list[float] = []
    delta_99_values: list[float] = []
    for index in range(n_cases):
        mach = None
        tw_t0 = None
        if config.method == "eckert_reference":
            mach = swept["mach"][index]
            tw_t0 = swept["tw_t0"][index]

        result = compute_boundary_layer_thickness(
            x=swept["x"][index],
            re1=swept["re1"][index],
            method=config.method,
            mach=mach,
            tw_t0=tw_t0,
            gamma=config.gamma,
        )
        re_x_values.append(result.re_x)
        delta_99_values.append(result.delta_99)

    # print a compact summary table
    typer.echo("\n[boundary_layer_thickness]")
    typer.echo(f"{'x':>12} {'Re_x':>14} {'delta_99':>14} {'method':>20}")
    for index in range(n_cases):
        typer.echo(
            f"{swept['x'][index]:>12.4g} {re_x_values[index]:>14.6e} "
            f"{delta_99_values[index]:>14.6e} {config.method:>20}"
        )

    # optionally write the common thickness outputs
    if config.output is not None:
        written = write_tecplot(
            config.output,
            title="flow_theory boundary-layer thickness",
            variables=["x", "Re_x", "delta_99"],
            zone_name=f"boundary-layer thickness {config.method}",
            values=np.column_stack(
                [
                    swept["x"],
                    np.asarray(re_x_values),
                    np.asarray(delta_99_values),
                ]
            ),
        )
        typer.echo(f"wrote {written}")
