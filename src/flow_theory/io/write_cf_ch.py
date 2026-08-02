"""Terminal and Tecplot output for cf/ch calculations."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from .tecplot_ascii import TecplotFile

logger = logging.getLogger("flow-theory")


# --------------------------------------------------
# write out cf/ch data
# --------------------------------------------------
def write_cf_ch(
    data: dict[str, object],
    fpath: Path | None,
) -> None:
    """Write all cf/ch data sets in the output dictionary to file."""

    # skip output when no file path is configured
    if fpath is None:
        logger.info("cf/ch output file is not configured; skipping file write")
        return

    # get x data (shared for all modes and methods)
    x = data["x"]
    # get re_x data (shared for all modes and methods)
    re_x = data["re_x"]

    # get modes (laminar/turbulent)
    modes = list(data["modes"])
    logger.debug("cf/ch output modes: %s", ", ".join(modes))

    # get method names for each mode
    methods = data["method_names"]
    logger.debug("cf/ch output methods by mode: %s", methods)

    # get skin-friction data (all modes and methods)
    cf_data = data["cf"]
    # get stanton number data (all modes and methods)
    ch_data = data["ch"]
    temp_wall_by_mode = data["temp_wall"]
    wall_type = str(data["wall_type"])

    # loop over modes (laminar/turbulent) and write each to a separate file
    for mode in modes:
        # get wall temperature
        temp_wall = float(temp_wall_by_mode[mode])

        # select the mode-specific output filename
        output_path = fpath
        if len(modes) > 1:
            output_path = output_path.with_name(
                f"{output_path.stem}_{mode}{output_path.suffix}"
            )

        mode_method_names = list(methods[mode])
        logger.debug(
            "preparing %s output with methods: %s",
            mode,
            ", ".join(mode_method_names),
        )
        logger.debug("%s output file: %s", mode, output_path)

        cf_method_values = cf_data[mode]
        ch_method_values = ch_data[mode]

        variables = ["x", "re_x", "temp_wall", "cf", "ch"]
        with TecplotFile(
            output_path,
            title="flow_theory cf sweep",
            variables=variables,
        ) as tecplot_file:
            for method_name in mode_method_names:
                values = np.column_stack(
                    [
                        x,
                        re_x,
                        np.full(x.size, temp_wall, dtype=float),
                        cf_method_values[method_name],
                        ch_method_values[method_name],
                    ]
                )
                zone_name = f"cf_ch {mode} {method_name} {wall_type}"
                tecplot_file.write_zone(zone_name, values)
                logger.debug(
                    "wrote zone %s with %d rows",
                    zone_name,
                    values.shape[0],
                )

        logger.info("wrote %s", output_path)
