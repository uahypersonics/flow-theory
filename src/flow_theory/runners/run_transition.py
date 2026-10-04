"""Runner for [transition] workflow sections."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
import typer

from flow_theory.config import TransitionConfig
from flow_theory.io import write_tecplot
from flow_theory.runners.common import as_float_list, broadcast_sweep
from flow_theory.transition import transition_x


# --------------------------------------------------
# public API
# --------------------------------------------------
def run_transition(config: TransitionConfig) -> None:
    """Execute one or more transition-location calculations."""

    # broadcast scalar and list inputs into aligned cases
    swept = broadcast_sweep(
        mach=as_float_list(config.mach, "transition.mach"),
        re1=as_float_list(config.re1, "transition.re1"),
        tw_te=as_float_list(config.tw_te, "transition.tw_te"),
    )
    n_cases = swept["mach"].size

    # compute the transition location for each case
    transition_values: list[float] = []
    for index in range(n_cases):
        transition_value = transition_x(
            swept["re1"][index],
            swept["mach"][index],
            swept["tw_te"][index],
            method=config.method,
        )
        transition_values.append(transition_value)

    # print a compact result table to stdout
    typer.echo("\n[transition]")
    typer.echo(f"{'Mach':>10} {'Re1':>12} {'Tw_Te':>10} {'x_transition':>14}")
    for index in range(n_cases):
        typer.echo(
            f"{swept['mach'][index]:>10.4g} {swept['re1'][index]:>12.4g} "
            f"{swept['tw_te'][index]:>10.4g} "
            f"{transition_values[index]:>14.6e}"
        )

    # write Tecplot output if requested
    if config.output is not None:
        written = write_tecplot(
            config.output,
            title="flow_theory transition",
            variables=["Mach", "Re1", "Tw_Te", "x_transition"],
            zone_name=f"transition {config.method}",
            values=np.column_stack(
                [
                    swept["mach"],
                    swept["re1"],
                    swept["tw_te"],
                    np.asarray(transition_values),
                ]
            ),
        )
        typer.echo(f"wrote {written}")
