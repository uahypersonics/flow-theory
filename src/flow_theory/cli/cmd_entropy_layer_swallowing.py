"""CLI handler for ``flow-theory entropy-layer-swallowing``."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import EntropyLayerSwallowingConfig
from flow_theory.runners import run_entropy_layer_swallowing


def cmd_entropy_layer_swallowing(
    mach: Annotated[float, typer.Option("--mach", help="Edge Mach number.")],
    re1: Annotated[
        float,
        typer.Option("--re1", help="Unit Reynolds number [1/m]."),
    ],
    nose_radius: Annotated[
        float,
        typer.Option("--nose-radius", help="Nose radius [m]."),
    ],
    tw_t0: Annotated[
        float,
        typer.Option("--tw-t0", help="Wall-to-stagnation temperature ratio."),
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
    """Compute the entropy-layer swallowing distance."""

    try:
        config = EntropyLayerSwallowingConfig(
            run=True,
            mach=float(mach),
            re1=float(re1),
            nose_radius=float(nose_radius),
            tw_t0=float(tw_t0),
            gamma=float(gamma),
            output=output,
        )
        run_entropy_layer_swallowing(config)
    except typer.Exit:
        raise
    except Exception as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1)
