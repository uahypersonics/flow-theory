"""Configuration adapter for the [cf_ch] workflow section."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..cf_ch import VALID_MODES
from .point_sweep import point_sweep
from .schema import ConfigNode, validate_section_keys

# --------------------------------------------------
# section structure
# --------------------------------------------------
_ALLOWED_KEYS = {
    "flow_conditions",
    "method",
    "mode",
    "output",
    "run",
    "temp_wall",
    "wall_type",
    "x",
}

_REQUIRED_KEYS = {"flow_conditions", "run", "x"}


# --------------------------------------------------
# typed configuration
# --------------------------------------------------
@dataclass(slots=True, frozen=True)
class CfChConfig:
    """Validated inputs for a cf/ch calculation."""

    run: bool
    flow_conditions: Path
    x: np.ndarray
    mode: str | None = None
    method: str | None = None
    wall_type: str = "adiabatic"
    temp_wall: float | None = None
    output: Path | None = None

    def __post_init__(self) -> None:
        """Normalize and validate cf/ch calculation options."""

        # validate the required flow-state input
        if not isinstance(self.flow_conditions, Path):
            raise TypeError("[cf_ch] flow_conditions must be a Path")

        # --------------------------------------------------
        # normalize and validate selectors
        # --------------------------------------------------

        # mode: first write into local variables to avoid frozen dataclass assignment
        normalized_mode = self.mode

        # normalize (strip whitespace and convert to all lowercase) optional selectors
        if normalized_mode is not None:
            normalized_mode = normalized_mode.strip().lower() or None

        # update the dataclass attributes with normalized values using object.__setattr__ because the dataclass is frozen
        object.__setattr__(self, "mode", normalized_mode)

        # method
        normalized_method = self.method

        if normalized_method is not None:
            normalized_method = normalized_method.strip().lower() or None

        object.__setattr__(self, "method", normalized_method)

        # wall_type
        normalized_wall_type = self.wall_type

        normalized_wall_type = normalized_wall_type.strip().lower()

        object.__setattr__(self, "wall_type", normalized_wall_type)

        # resolve point sweep
        x = point_sweep(self.x, key_name="[cf_ch]")

        object.__setattr__(self, "x", x)

        # validate selector values (after normalization)
        if self.mode is not None and self.mode not in VALID_MODES:
            raise ValueError(f"[cf_ch] mode must be one of {VALID_MODES} when provided")
        if self.wall_type not in ("adiabatic", "isothermal"):
            raise ValueError("[cf_ch] wall_type must be 'adiabatic' or 'isothermal'")

        # ensure temp_wall is set when wall_type is isothermal
        if self.wall_type == "isothermal" and self.temp_wall is None:
            raise ValueError(
                "[cf_ch] temp_wall is required when wall_type='isothermal'"
            )


# --------------------------------------------------
# public API
# --------------------------------------------------
def parse_cf_ch_config(section: ConfigNode) -> CfChConfig:
    """Validate and convert a [cf_ch] section."""

    # validate section keys before accessing required attributes
    validate_section_keys(
        section,
        section_name="cf_ch",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    # validate the workflow toggle separately to avoid truthy string values
    run_value = section.run
    if not isinstance(run_value, bool):
        raise ValueError("cf_ch.run must be true or false")

    # --------------------------------------------------
    # convert required values
    # --------------------------------------------------
    flow_conditions = Path(str(section.flow_conditions))
    x_value = section.x

    # --------------------------------------------------
    # convert optional values
    # --------------------------------------------------

    # mode: can be laminar or turbulent or None (both)
    mode = str(section.mode) if hasattr(section, "mode") else None
    # method: can be any string or None (all)
    method = str(section.method) if hasattr(section, "method") else None
    # wall_type: can be adiabatic or isothermal (default adiabatic)
    wall_type = str(getattr(section, "wall_type", "adiabatic"))
    # temp_wall: can be any float or None (default None)
    temp_wall = float(section.temp_wall) if hasattr(section, "temp_wall") else None

    # output: can be any path or None (default None)
    output = Path(str(section.output)) if hasattr(section, "output") else None

    # --------------------------------------------------
    # build the typed runner input
    # --------------------------------------------------
    config = CfChConfig(
        run=run_value,
        flow_conditions=flow_conditions,
        x=x_value,
        mode=mode,
        method=method,
        wall_type=wall_type,
        temp_wall=temp_wall,
        output=output,
    )

    # return the validated and typed configuration object
    return config
