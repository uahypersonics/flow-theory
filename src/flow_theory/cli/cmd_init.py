"""CLI handler for ``flow-theory init``.

Writes starter TOML configs for ``flow-theory run``.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.templates import render_templates


# --------------------------------------------------
# main command
# --------------------------------------------------
def cmd_init(
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output TOML path.",
        ),
    ] = Path("flow_theory.toml"),
    preset: Annotated[
        str,
        typer.Option(
            "--preset",
            "-p",
            help=(
                "Template preset: boundary_layer_thickness, cf_ch, "
                "shock_standoff, shock_shape, entropy_layer_estimate, "
                "entropy_layer_swallowing, or all."
            ),
        ),
    ] = "all",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing output file.",
        ),
    ] = False,
) -> None:
    """Write starter config TOML for flow-theory run."""

    # define valid presets
    valid_presets = {
        "all",
        "boundary_layer_thickness",
        "cf_ch",
        "entropy_layer_estimate",
        "entropy_layer_swallowing",
        "shock_shape",
        "shock_standoff",
    }

    try:
        # normalize and validate preset input
        preset_value = str(preset).strip().lower()

        # check if normalized preset value is in valid list
        if preset_value not in valid_presets:
            # preset value not valid => report error and exit
            choices = ", ".join(sorted(valid_presets))
            typer.echo(f"error: --preset must be one of: {choices}", err=True)
            raise typer.Exit(1)

        # convert output file name to Path object
        output_path = Path(output)

        # validate overwrite policy
        if output_path.exists() and not force:
            typer.echo(
                f"error: output exists: {output_path} (use --force to overwrite)",
                err=True,
            )
            raise typer.Exit(1)

        # build template content (TOML text) for the requested preset
        # stored in ./templates/
        content = render_templates(preset_value)

        # write template file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        typer.echo(f"wrote {output_path}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
