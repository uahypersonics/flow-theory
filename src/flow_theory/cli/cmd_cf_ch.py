"""CLI handler for ``flow-theory cf``.

The commands read edge flow conditions from a flow-state JSON file and sweep
``x`` from ``xs`` to ``xe``.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import CfChConfig
from flow_theory.runners import run_cf_ch


# --------------------------------------------------
# main function for the 'cf' cli command
# --------------------------------------------------
def cmd_cf_ch(
    xs: Annotated[float, typer.Option("--xs", help="Start x location [m].")],
    xe: Annotated[float, typer.Option("--xe", help="End x location [m].")],
    nx: Annotated[int, typer.Option("--nx", help="Number of x stations.")],
    flow_conditions: Annotated[
        Path,
        typer.Option(
            "--flow-conditions",
            help="Required flow-state JSON file with edge conditions.",
        ),
    ],
    temp_wall: Annotated[
        float | None,
        typer.Option(
            "--temp-wall",
            help="Wall temperature [K]. Omit for adiabatic wall temperature.",
        ),
    ] = None,
    mode: Annotated[
        str | None,
        typer.Option("--mode", help="'laminar', 'turbulent', or omit for both."),
    ] = None,
    method: Annotated[
        str | None,
        typer.Option(
            "--method",
            help=(
                "Method name. Omit to evaluate all methods for the selected mode(s). "
                "Laminar: blasius, eckert_reference, similarity. "
                "Turbulent: van_driest_ii, spalding_chi, sommer_short, "
                "white_christoph."
            ),
        ),
    ] = None,
    output: Annotated[
        Path | None, typer.Option("--output", help="Optional Tecplot .dat output path.")
    ] = None,
) -> None:
    """Compute flat-plate cf and Ch along an x sweep."""

    try:
        # sanity checks on x inputs
        if nx < 2:
            raise ValueError("nx must be at least 2")
        if xe <= xs:
            raise ValueError("xe must be greater than xs")
        if xs < 0.0:
            raise ValueError("xs must be non-negative")

        # build the shared runner configuration
        wall_type = "isothermal" if temp_wall is not None else "adiabatic"
        config = CfChConfig(
            run=True,
            flow_conditions=flow_conditions,
            x=[float(xs), float(xe), int(nx)],
            mode=mode,
            method=method,
            wall_type=wall_type,
            temp_wall=temp_wall,
            output=output,
        )

        # run the shared cf/ch implementation
        run_cf_ch(config)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
