"""Runner for [entropy_layer_swallowing] workflow sections."""

from __future__ import annotations

import numpy as np
import typer

from flow_theory.config import EntropyLayerSwallowingConfig
from flow_theory.entropy_layer import swallowing_distance
from flow_theory.io import write_tecplot
from flow_theory.runners.common import as_float_list, broadcast_sweep


def run_entropy_layer_swallowing(
    config: EntropyLayerSwallowingConfig,
) -> None:
    """Execute an entropy-layer swallowing calculation."""

    swept = broadcast_sweep(
        mach=as_float_list(config.mach, "entropy_layer_swallowing.mach"),
        re1=as_float_list(config.re1, "entropy_layer_swallowing.re1"),
        nose_radius=as_float_list(
            config.nose_radius,
            "entropy_layer_swallowing.nose_radius",
        ),
        tw_t0=as_float_list(config.tw_t0, "entropy_layer_swallowing.tw_t0"),
    )
    n_cases = swept["mach"].size

    distance_values: list[float] = []
    for index in range(n_cases):
        distance = swallowing_distance(
            swept["nose_radius"][index],
            swept["re1"][index],
            swept["mach"][index],
            swept["tw_t0"][index],
            gamma=config.gamma,
        )
        distance_values.append(distance)

    typer.echo("\n[entropy_layer_swallowing]")
    typer.echo(f"{'Mach':>10} {'Re1':>12} {'R_nose':>12} {'Tw_T0':>10} {'x_sw':>14}")
    for index in range(n_cases):
        typer.echo(
            f"{swept['mach'][index]:>10.4g} {swept['re1'][index]:>12.4g} "
            f"{swept['nose_radius'][index]:>12.4g} "
            f"{swept['tw_t0'][index]:>10.4g} "
            f"{distance_values[index]:>14.6e}"
        )

    if config.output is not None:
        written = write_tecplot(
            config.output,
            title="flow_theory entropy-layer swallowing",
            variables=["Mach", "Re1", "R_nose", "Tw_T0", "x_sw"],
            zone_name="entropy-layer swallowing distance",
            values=np.column_stack(
                [
                    swept["mach"],
                    swept["re1"],
                    swept["nose_radius"],
                    swept["tw_t0"],
                    np.asarray(distance_values),
                ]
            ),
        )
        typer.echo(f"wrote {written}")
