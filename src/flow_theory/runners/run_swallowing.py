"""Runner for the [swallowing] section in flow-theory run configs."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
import typer

from flow_theory.config import SwallowingConfig
from flow_theory.entropy_swallowing import swallowing_distance
from flow_theory.io import write_tecplot
from flow_theory.runners.common import as_float_list, broadcast_sweep


# --------------------------------------------------
# public API
# --------------------------------------------------
def run_swallowing(config: SwallowingConfig) -> None:
    """Execute an entropy swallowing calculation."""

    # read section options with defaults
    gamma = config.gamma
    output = config.output

    # build sweep arrays from scalar/list config values
    swept = broadcast_sweep(
        mach=as_float_list(config.mach, "swallowing.mach"),
        re1=as_float_list(config.re1, "swallowing.re1"),
        nose_radius=as_float_list(
            config.nose_radius,
            "swallowing.nose_radius",
        ),
        tw_t0=as_float_list(config.tw_t0, "swallowing.tw_t0"),
    )
    n_cases = swept["mach"].size

    # compute swallowing distance for each sweep case
    x_sw_values: list[float] = []
    for i in range(n_cases):
        x_sw_values.append(
            swallowing_distance(
                swept["nose_radius"][i],
                swept["re1"][i],
                swept["mach"][i],
                swept["tw_t0"][i],
                gamma=gamma,
            )
        )

    # print compact summary table
    typer.echo("\n[swallowing]")
    typer.echo(f"{'Mach':>10} {'Re1':>12} {'R_nose':>12} {'Tw_T0':>10} {'x_sw':>14}")
    for i in range(n_cases):
        typer.echo(
            f"{swept['mach'][i]:>10.4g} {swept['re1'][i]:>12.4g} "
            f"{swept['nose_radius'][i]:>12.4g} {swept['tw_t0'][i]:>10.4g} "
            f"{x_sw_values[i]:>14.6e}"
        )

    # optionally write Tecplot output
    if output is not None:
        written = write_tecplot(
            output,
            title="flow_theory swallowing",
            variables=["Mach", "Re1", "R_nose", "Tw_T0", "x_sw"],
            zone_name="swallowing distance",
            values=np.column_stack(
                [
                    swept["mach"],
                    swept["re1"],
                    swept["nose_radius"],
                    swept["tw_t0"],
                    np.asarray(x_sw_values),
                ]
            ),
        )
        typer.echo(f"wrote {written}")
