"""CLI handler for ``flow-theory shock-shape``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import (
    ShockShapeConfig,
    parse_shock_shape_config,
    read_config,
)
from flow_theory.runners import run_shock_shape
from flow_theory.templates import render_templates

# --------------------------------------------------
# shock-shape command group
# --------------------------------------------------
shock_shape_app = typer.Typer(
    name="shock-shape",
    help="Approximate detached bow-shock shape calculations.",
    no_args_is_help=True,
)


@shock_shape_app.command(name="init")
def cmd_init_shock_shape(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output TOML path."),
    ] = Path("shock_shape.toml"),
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing output file."),
    ] = False,
) -> None:
    """Write a focused shock-shape configuration."""
    try:
        if output.exists() and not force:
            raise FileExistsError(f"output exists: {output} (use --force to overwrite)")

        content = render_templates("shock_shape")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        typer.echo(f"wrote {output}")
        typer.echo(f"then run: flow-theory shock-shape run --config {output}")
    except (OSError, ValueError) as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1) from None


# --------------------------------------------------
# main function for the 'shock-shape' cli command
# --------------------------------------------------
@shock_shape_app.command(name="run")
def cmd_shock_shape(
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "--cfg",
            "-c",
            help="Config TOML path. Defaults to shock_shape.toml when no direct inputs are provided.",
        ),
    ] = None,
    flow_conditions: Annotated[
        Path | None,
        typer.Option(
            "--flow-conditions",
            help="Required flow-state JSON file with freestream conditions.",
        ),
    ] = None,
    nose_radius: Annotated[
        float | None,
        typer.Option("--nose-radius", help="Body nose radius."),
    ] = None,
    geometry: Annotated[
        str,
        typer.Option("--geometry", help="Body geometry (sphere, cone, ogive, wedge)."),
    ] = "sphere",
    method: Annotated[
        str,
        typer.Option("--method", help="Shock-shape correlation (default: billig)."),
    ] = "billig",
    half_angle: Annotated[
        float | None,
        typer.Option(
            "--half-angle",
            help="Half-angle [deg], required for cone/ogive/wedge geometries.",
        ),
    ] = None,
    n_points: Annotated[
        int,
        typer.Option(
            "--n-points",
            help="Number of sample points used for both shock and surface zones.",
        ),
    ] = 100,
    x_e: Annotated[
        float,
        typer.Option(
            "--x-e",
            help="Streamwise endpoint for body and shock sampling.",
        ),
    ] = 0.1,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Optional Tecplot output path."),
    ] = None,
) -> None:
    """Compute an approximate shock shape."""

    try:
        # use direct options whenever either required direct input is present
        use_direct_options = flow_conditions is not None or nose_radius is not None

        # read and run from the focused config when direct inputs are absent
        if not use_direct_options:
            config_path = Path("shock_shape.toml") if config is None else config
            cfg = read_config(config_path)

            if not hasattr(cfg, "shock_shape"):
                raise ValueError("Config file does not contain a [shock_shape] section")

            shock_shape_cfg = parse_shock_shape_config(cfg.shock_shape)
            run_shock_shape(shock_shape_cfg)
            return

        if config is not None:
            raise ValueError("--config cannot be combined with direct solver inputs")

        # validate required direct inputs when config path is not provided
        if flow_conditions is None:
            raise ValueError("flow_conditions is required unless --config is provided")
        if nose_radius is None:
            raise ValueError("nose_radius is required unless --config is provided")

        # get the typed configuration dataclass
        config = ShockShapeConfig(
            flow_conditions=flow_conditions,
            nose_radius=nose_radius,
            geometry=geometry,
            method=method,
            half_angle=half_angle,
            n_points=n_points,
            x_e=x_e,
            output=output,
        )

        # run the shared shock-shape implementation
        run_shock_shape(config)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
