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


# --------------------------------------------------
# main function for the 'shock-shape' cli command
# --------------------------------------------------
def cmd_shock_shape(
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "--cfg",
            "-c",
            help="Optional config TOML path. Uses [shock_shape] section when provided.",
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
        # read and run from config-file section when a config path is provided
        if config is not None:
            cfg = read_config(config)

            if not hasattr(cfg, "shock_shape"):
                raise ValueError(
                    "Config file does not contain a [shock_shape] section"
                )

            shock_shape_cfg = parse_shock_shape_config(cfg.shock_shape)
            run_shock_shape(shock_shape_cfg)
            return

        # validate required direct inputs when config path is not provided
        if flow_conditions is None:
            raise ValueError("flow_conditions is required unless --config is provided")
        if nose_radius is None:
            raise ValueError("nose_radius is required unless --config is provided")

        # get the typed configuration dataclass
        config = ShockShapeConfig(
            run=True,
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
