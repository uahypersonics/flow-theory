"""CLI handler for ``flow-theory entropy-layer-estimate``."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import EntropyLayerEstimateConfig
from flow_theory.runners import run_entropy_layer_estimate


def cmd_entropy_layer_estimate(
    x: Annotated[float, typer.Option("--x", help="Streamwise station [m].")],
    mach: Annotated[float, typer.Option("--mach", help="Edge Mach number.")],
    nose_radius: Annotated[
        float,
        typer.Option("--nose-radius", help="Nose radius [m]."),
    ],
    gamma: Annotated[
        float,
        typer.Option("--gamma", help="Specific heat ratio."),
    ] = 1.4,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Optional Tecplot output path."),
    ] = None,
) -> None:
    """Estimate entropy-layer thickness at one station."""

    try:
        config = EntropyLayerEstimateConfig(
            run=True,
            x=float(x),
            mach=float(mach),
            nose_radius=float(nose_radius),
            gamma=float(gamma),
            output=output,
        )
        run_entropy_layer_estimate(config)
    except typer.Exit:
        raise
    except Exception as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1)
