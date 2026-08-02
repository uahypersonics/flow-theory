"""flow-theory command-line interface (typer).

Subcommands are defined in separate ``cmd_*.py`` modules and
registered on the shared ``app`` Typer instance below.
"""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations

from typing import Annotated

import typer

from .callbacks import verbose_callback, version_callback
from .cmd_cf_ch import cmd_cf_ch
from .cmd_init import cmd_init
from .cmd_run import cmd_run
from .cmd_shock_shape import cmd_shock_shape
from .cmd_standoff import cmd_standoff
from .cmd_swallowing import cmd_swallowing
from .cmd_transition import cmd_transition

# --------------------------------------------------
# app
# --------------------------------------------------
app = typer.Typer(
    name="flow-theory",
    help="flow-theory command-line interface",
    no_args_is_help=True,
    add_completion=False,
)

# --------------------------------------------------
# callback for --version and --verbose options
# version_callback and verbose_callback are defined in callbacks.py
# --------------------------------------------------
@app.callback()
def callback(
    # --version -V option
    version: Annotated[
        bool | None,
        typer.Option(
            "--version", "-V",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    # --verbose -v option
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v",
            help="Enable verbose output.",
            callback=verbose_callback
        ),
    ] = False,
) -> None:
    """flow-theory: useful engineering correlations and theoretical estimates."""

# --------------------------------------------------
# register subcommands
# note: subcommands are assigned to a rich help panel for better organization
# --------------------------------------------------

# single calculators (no init file) - rich_help_panel="Calculators"
app.command(name="cf", no_args_is_help=True, rich_help_panel="Calculators")(cmd_cf_ch)
app.command(name="standoff", no_args_is_help=True, rich_help_panel="Calculators")(cmd_standoff)
app.command(name="shock-shape", no_args_is_help=True, rich_help_panel="Calculators")(cmd_shock_shape)
app.command(name="swallowing", no_args_is_help=True, rich_help_panel="Calculators")(cmd_swallowing)
app.command(name="transition", no_args_is_help=True, rich_help_panel="Calculators")(cmd_transition)

# workflow with init and run - rich_help_panel="Workflow"
app.command(name="init", rich_help_panel="Workflow")(cmd_init)
app.command(name="run", rich_help_panel="Workflow")(cmd_run)

# --------------------------------------------------
# main entry point
# --------------------------------------------------
if __name__ == "__main__":
    app()
