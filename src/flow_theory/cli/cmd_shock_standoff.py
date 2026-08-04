"""CLI handler for ``flow-theory shock-standoff``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import ShockStandoffConfig
from flow_theory.runners import run_shock_standoff


# --------------------------------------------------
# main function for the shock-standoff command
# --------------------------------------------------
def cmd_shock_standoff(
    flow_conditions: Annotated[
        Path,
        typer.Option(
            "--flow-conditions",
            help="Required flow-state JSON file with freestream conditions.",
        ),
    ],
    nose_radius: Annotated[
        float,
        typer.Option("--nose-radius", help="Body nose radius."),
    ],
    geometry: Annotated[
        str,
        typer.Option("--geometry", help="Nose geometry: sphere or cylinder."),
    ] = "sphere",
    method: Annotated[
        str,
        typer.Option(
            "--method",
            help=(
                "Shock-standoff correlation: ambrosio_wortman, "
                "ambrosio_wortman_density_ratio, or serbin."
            ),
        ),
    ] = "ambrosio_wortman",
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Optional Tecplot output path."),
    ] = None,
) -> None:
    """Compute a normal-shock standoff estimate."""

    try:
        # build the shared runner configuration
        config = ShockStandoffConfig(
            run=True,
            flow_conditions=flow_conditions,
            nose_radius=nose_radius,
            geometry=geometry,
            method=method,
            output=output,
        )

        # run the shared shock-standoff implementation
        run_shock_standoff(config)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
