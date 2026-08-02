"""CLI handler for ``flow-theory transition``.

Computes the flat-plate transition location for one input case.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.io import write_tecplot
from flow_theory.transition import transition_x


# --------------------------------------------------
# main function for the 'transition' cli command
# --------------------------------------------------
def cmd_transition(
    mach: Annotated[float, typer.Option("--mach", help="Edge Mach number.")],
    re1: Annotated[
        float,
        typer.Option("--re1", help="Unit Reynolds number [1/m]."),
    ],
    tw_te: Annotated[
        float,
        typer.Option("--tw-te", help="Wall-to-edge temperature ratio."),
    ],
    method: Annotated[
        str,
        typer.Option("--method", help="Transition-onset criterion (van_driest_blumer)."),
    ] = "van_driest_blumer",
    output: Annotated[
        Path | None, typer.Option("--output", help="Optional Tecplot .dat output path.")
    ] = None,
) -> None:
    """Compute flat-plate transition location x_transition."""

    try:
        # build input scalars for a single case
        mach_value = float(mach)
        re1_value = float(re1)
        tw_te_value = float(tw_te)

        # compute transition location for the single case
        x_t_value = transition_x(re1_value, mach_value, tw_te_value, method=method)

        # print a compact result table to stdout
        typer.echo(f"{'Mach':>10} {'Re1':>12} {'Tw_Te':>10} {'x_transition':>14}")
        typer.echo(f"{mach_value:>10.4g} {re1_value:>12.4g} {tw_te_value:>10.4g} {x_t_value:>14.6e}")

        # write Tecplot output if requested
        if output is not None:
            written = write_tecplot(
                output,
                title="flow_theory transition",
                variables=["Mach", "Re1", "Tw_Te", "x_transition"],
                zone_name=f"transition {method}",
                values=[[mach_value, re1_value, tw_te_value, x_t_value]],
            )
            typer.echo(f"wrote {written}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
