"""CLI handler for ``flow-theory run``.

Runs one or more tools from a TOML config where sections are self-discoverable,
for example:

    [boundary_layer_thickness]
    run = true
    ...

    [cf_ch]
    run = true
    ...

    [entropy_layer_estimate]
    run = true
    ...

    [entropy_layer_swallowing]
    run = true
    ...
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer

from flow_theory.config import (
    parse_boundary_layer_thickness_config,
    parse_cf_ch_config,
    parse_entropy_layer_estimate_config,
    parse_entropy_layer_swallowing_config,
    parse_shock_shape_config,
    parse_shock_standoff_config,
    read_config,
)
from flow_theory.runners import (
    run_boundary_layer_thickness,
    run_cf_ch,
    run_entropy_layer_estimate,
    run_entropy_layer_swallowing,
    run_shock_shape,
    run_shock_standoff,
)

logger = logging.getLogger("flow-theory")


# --------------------------------------------------
# main command
# --------------------------------------------------
def cmd_run(
    config_file: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "-c",
            help="Config TOML path. If omitted, auto-discovers flow_theory.toml-like names.",
        ),
    ] = None,
) -> None:
    """Run enabled tool sections from a config file."""

    try:
        # read the config object with attribute access
        cfg = read_config(config_file)

        # output in verbose mode
        logger.debug("loaded config from %s", config_file or ".")

        # --------------------------------------------------
        # run enabled sections (runners are located in ./runners/)
        # --------------------------------------------------
        ran_any = False

        # check if config has a boundary_layer_thickness section
        if hasattr(cfg, "boundary_layer_thickness"):
            cfg_boundary_layer = parse_boundary_layer_thickness_config(
                cfg.boundary_layer_thickness
            )

            if cfg_boundary_layer.run:
                logger.debug("running [boundary_layer_thickness] section")
                run_boundary_layer_thickness(cfg_boundary_layer)
                ran_any = True
            else:
                logger.debug(
                    "skipping [boundary_layer_thickness] section (run=false)"
                )
        else:
            logger.debug("skipping [boundary_layer_thickness] section (not present)")

        # check if config has a cf_ch section
        if hasattr(cfg, "cf_ch"):
            # parse and validate the cf_ch section into a CfChConfig object
            cfg_cf_ch = parse_cf_ch_config(cfg.cf_ch)

            # if the run flag is set, execute the cf_ch runner
            if cfg_cf_ch.run:
                logger.debug("running [cf_ch] section")
                run_cf_ch(cfg_cf_ch)
                ran_any = True
            else:
                logger.debug("skipping [cf_ch] section (run=false)")
        else:
            logger.debug("skipping [cf_ch] section (not present)")

        # check if config has a shock_standoff section
        if hasattr(cfg, "shock_standoff"):
            cfg_shock_standoff = parse_shock_standoff_config(cfg.shock_standoff)

            if cfg_shock_standoff.run:
                logger.debug("running [shock_standoff] section")
                run_shock_standoff(cfg_shock_standoff)
                ran_any = True
            else:
                logger.debug("skipping [shock_standoff] section (run=false)")
        else:
            logger.debug("skipping [shock_standoff] section (not present)")

        # check if config has a shock_shape section
        if hasattr(cfg, "shock_shape"):
            cfg_shock_shape = parse_shock_shape_config(cfg.shock_shape)

            if cfg_shock_shape.run:
                logger.debug("running [shock_shape] section")
                run_shock_shape(cfg_shock_shape)
                ran_any = True
            else:
                logger.debug("skipping [shock_shape] section (run=false)")
        else:
            logger.debug("skipping [shock_shape] section (not present)")

        # check if config has an entropy_layer_estimate section
        if hasattr(cfg, "entropy_layer_estimate"):
            cfg_entropy_estimate = parse_entropy_layer_estimate_config(
                cfg.entropy_layer_estimate
            )

            if cfg_entropy_estimate.run:
                logger.debug("running [entropy_layer_estimate] section")
                run_entropy_layer_estimate(cfg_entropy_estimate)
                ran_any = True
            else:
                logger.debug("skipping [entropy_layer_estimate] section (run=false)")
        else:
            logger.debug("skipping [entropy_layer_estimate] section (not present)")

        # check if config has an entropy_layer_swallowing section
        if hasattr(cfg, "entropy_layer_swallowing"):
            cfg_entropy_swallowing = parse_entropy_layer_swallowing_config(
                cfg.entropy_layer_swallowing
            )

            if cfg_entropy_swallowing.run:
                logger.debug("running [entropy_layer_swallowing] section")
                run_entropy_layer_swallowing(cfg_entropy_swallowing)
                ran_any = True
            else:
                logger.debug(
                    "skipping [entropy_layer_swallowing] section (run=false)"
                )
        else:
            logger.debug("skipping [entropy_layer_swallowing] section (not present)")

        # fail fast when nothing was executed
        if not ran_any:
            raise ValueError(
                "No runnable sections were executed. "
                "Enable at least one supported workflow section."
            )

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
