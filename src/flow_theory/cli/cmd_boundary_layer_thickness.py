"""CLI handler for ``flow-theory boundary-layer-thickness``."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import BoundaryLayerThicknessConfig
from flow_theory.runners import run_boundary_layer_thickness


def cmd_boundary_layer_thickness(
    x: Annotated[float, typer.Option("--x", help="Streamwise station [m].")],
    re1: Annotated[
        float,
        typer.Option("--re1", help="Unit Reynolds number [1/m]."),
    ],
    method: Annotated[
        str,
        typer.Option("--method", help="Thickness correlation name."),
    ] = "blasius",
    mach: Annotated[
        float | None,
        typer.Option("--mach", help="Edge Mach number."),
    ] = None,
    tw_t0: Annotated[
        float | None,
        typer.Option("--tw-t0", help="Wall-to-stagnation temperature ratio."),
    ] = None,
    gamma: Annotated[
        float,
        typer.Option("--gamma", help="Specific heat ratio."),
    ] = 1.4,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Optional Tecplot output path."),
    ] = None,
) -> None:
    """Compute laminar flat-plate boundary-layer thickness."""

    try:
        # build the shared runner configuration
        config = BoundaryLayerThicknessConfig(
            run=True,
            x=float(x),
            re1=float(re1),
            method=method,
            mach=mach,
            tw_t0=tw_t0,
            gamma=float(gamma),
            output=output,
        )

        # run the shared thickness implementation
        run_boundary_layer_thickness(config)
    except typer.Exit:
        raise
    except Exception as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1)
