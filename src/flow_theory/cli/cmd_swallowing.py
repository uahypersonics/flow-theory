"""CLI handler for ``flow-theory swallowing``.

Computes the entropy-layer swallowing distance for a blunt cone
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import SwallowingConfig
from flow_theory.runners import run_swallowing


# --------------------------------------------------
# main function for the 'swallowing' cli command
# --------------------------------------------------
def cmd_swallowing(
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
    gamma: Annotated[float, typer.Option("--gamma", help="Specific heat ratio.")] = 1.4,
    output: Annotated[
        Path | None, typer.Option("--output", help="Optional Tecplot .dat output path.")
    ] = None,
) -> None:
    """Compute the entropy-layer swallowing distance x_sw."""

    try:
        # build input scalars for a single case
        mach_value = float(mach)
        re1_value = float(re1)
        nose_radius_value = float(nose_radius)
        tw_t0_value = float(tw_t0)

        # build the shared runner configuration
        config = SwallowingConfig(
            run=True,
            mach=mach_value,
            re1=re1_value,
            nose_radius=nose_radius_value,
            tw_t0=tw_t0_value,
            gamma=gamma,
            output=output,
        )

        # run the shared swallowing implementation
        run_swallowing(config)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
