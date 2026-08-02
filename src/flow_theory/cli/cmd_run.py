"""CLI handler for ``flow-theory run``.

Runs one or more tools from a TOML config where sections are self-discoverable,
for example:

    [cf_ch]
    run = true
    ...

    [swallowing]
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

from flow_theory.config import parse_cf_ch_config, parse_swallowing_config, read_config
from flow_theory.runners import run_cf_ch, run_swallowing

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

        # check if config has a swallowing section
        if hasattr(cfg, "swallowing"):
            # parse and validate the swallowing section into a SwallowingConfig object
            cfg_swallowing = parse_swallowing_config(cfg.swallowing)

            # if the run flag is set, execute the swallowing runner
            if cfg_swallowing.run:
                logger.debug("running [swallowing] section")
                run_swallowing(cfg_swallowing)
                ran_any = True
            else:
                logger.debug("skipping [swallowing] section (run=false)")
        else:
            logger.debug("skipping [swallowing] section (not present)")

        # fail fast when nothing was executed
        if not ran_any:
            raise ValueError(
                "No runnable sections were executed. "
                "Set [cf_ch].run=true and/or [swallowing].run=true."
            )

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(1)
