"""CLI handler for ``flow-theory standoff``.

Computes the detached bow-shock standoff distance on a sphere
for one input case.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.io import write_tecplot
from flow_theory.shock_standoff import standoff_sphere


# --------------------------------------------------
# main function for the 'standoff' cli command
# --------------------------------------------------
def cmd_standoff(
    mach: Annotated[float, typer.Option("--mach", help="Freestream Mach number.")],
    nose_radius: Annotated[
        float,
        typer.Option("--nose-radius", help="Nose radius [m]."),
    ],
    gamma: Annotated[float, typer.Option("--gamma", help="Specific heat ratio.")] = 1.4,
    output: Annotated[
        Path | None, typer.Option("--output", help="Optional Tecplot .dat output path.")
    ] = None,
) -> None:
    """Compute the bow-shock standoff distance on a sphere."""

    try:
        # build input scalars for a single case
        mach_value = float(mach)
        nose_radius_value = float(nose_radius)

        # compute dimensional standoff distance for the single case
        delta_over_r = standoff_sphere(mach_value, gamma=gamma)
        delta_value = delta_over_r * nose_radius_value

        # print a compact result table to stdout
        typer.echo(f"{'Mach':>10} {'R_nose':>12} {'Delta':>14}")
        typer.echo(f"{mach_value:>10.4g} {nose_radius_value:>12.4g} {delta_value:>14.6e}")

        # write Tecplot output if requested
        if output is not None:
            written = write_tecplot(
                output,
                title="flow_theory standoff",
                variables=["Mach", "R_nose", "Delta"],
                zone_name="standoff sphere",
                values=[[mach_value, nose_radius_value, delta_value]],
            )
            typer.echo(f"wrote {written}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
