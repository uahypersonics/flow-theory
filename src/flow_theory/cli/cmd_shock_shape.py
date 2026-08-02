"""CLI handler for ``flow-theory shock-shape``.

Computes the Billig detached bow-shock locus (x, y) for a single
freestream condition and nose radius.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.io import write_tecplot
from flow_theory.shock_shape import shock_shape_points


# --------------------------------------------------
# main function for the 'shock-shape' cli command
# --------------------------------------------------
def cmd_shock_shape(
    mach: Annotated[float, typer.Option("--mach", help="Freestream Mach number.")],
    nose_radius: Annotated[float, typer.Option("--nose-radius", help="Nose radius [m].")],
    gamma: Annotated[float, typer.Option("--gamma", help="Specific heat ratio.")] = 1.4,
    n_pts: Annotated[int, typer.Option("--n-pts", help="Number of shock-locus points.")] = 100,
    output: Annotated[
        Path | None, typer.Option("--output", help="Optional Tecplot .dat output path.")
    ] = None,
) -> None:
    """Compute the detached bow-shock locus (x, y) around a blunted nose."""

    try:
        # compute the shock locus points
        x, y = shock_shape_points(mach, gamma, nose_radius, n_pts=n_pts)

        # print a compact summary to stdout
        typer.echo(f"shock standoff at axis: x = {x[0]:.6e} m")
        typer.echo(f"shock locus: {n_pts} points, y in [0, {y[-1]:.4e}] m")

        # write Tecplot output if requested
        if output is not None:
            written = write_tecplot(
                output,
                title="flow_theory shock shape",
                variables=["x", "y"],
                zone_name=f"shock shape M={mach:g}",
                values=[x, y],
            )
            typer.echo(f"wrote {written}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
