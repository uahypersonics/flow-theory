"""Runner for [entropy_layer_estimate] workflow sections."""

from __future__ import annotations

import numpy as np
import typer

from flow_theory.config import EntropyLayerEstimateConfig
from flow_theory.entropy_layer import entropy_layer_thickness
from flow_theory.io import write_tecplot
from flow_theory.runners.common import as_float_list, broadcast_sweep


def run_entropy_layer_estimate(config: EntropyLayerEstimateConfig) -> None:
    """Execute an entropy-layer thickness estimate."""

    swept = broadcast_sweep(
        x=as_float_list(config.x, "entropy_layer_estimate.x"),
        mach=as_float_list(config.mach, "entropy_layer_estimate.mach"),
        nose_radius=as_float_list(
            config.nose_radius,
            "entropy_layer_estimate.nose_radius",
        ),
    )
    n_cases = swept["x"].size

    thickness_values: list[float] = []
    for index in range(n_cases):
        thickness = entropy_layer_thickness(
            x=swept["x"][index],
            r_nose=swept["nose_radius"][index],
            mach=swept["mach"][index],
            gamma=config.gamma,
        )
        thickness_values.append(thickness)

    typer.echo("\n[entropy_layer_estimate]")
    typer.echo(f"{'x':>12} {'Mach':>10} {'R_nose':>12} {'delta_EL':>14}")
    for index in range(n_cases):
        typer.echo(
            f"{swept['x'][index]:>12.4g} {swept['mach'][index]:>10.4g} "
            f"{swept['nose_radius'][index]:>12.4g} "
            f"{thickness_values[index]:>14.6e}"
        )

    if config.output is not None:
        written = write_tecplot(
            config.output,
            title="flow_theory entropy-layer estimate",
            variables=["x", "Mach", "R_nose", "delta_EL"],
            zone_name="entropy-layer estimate",
            values=np.column_stack(
                [
                    swept["x"],
                    swept["mach"],
                    swept["nose_radius"],
                    np.asarray(thickness_values),
                ]
            ),
        )
        typer.echo(f"wrote {written}")
