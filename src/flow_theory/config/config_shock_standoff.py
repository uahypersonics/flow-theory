"""Configuration adapter for the [shock_standoff] workflow section."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from flow_theory.shock.standoff import (
    SHOCK_STANDOFF_GEOMETRIES,
    SHOCK_STANDOFF_METHODS,
)

from .schema import ConfigNode, validate_section_keys

# --------------------------------------------------
# section structure
# --------------------------------------------------
_ALLOWED_KEYS = {
    "flow_conditions",
    "geometry",
    "method",
    "nose_radius",
    "output",
    "run",
}

_REQUIRED_KEYS = {"flow_conditions", "nose_radius", "run"}


# --------------------------------------------------
# typed configuration
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class ShockStandoffConfig:
    """Validated inputs for a shock-standoff calculation."""

    # runner flag: true/false
    run: bool
    # flow conditions input file path
    flow_conditions: Path
    # nose radius (m)
    nose_radius: float
    # geometry flag
    geometry: str = "sphere"
    # method flag
    method: str = "ambrosio_wortman"
    output: Path | None = None

    def __post_init__(self) -> None:
        """Normalize and validate shock-standoff options."""

        # validate the required flow-state input
        if not isinstance(self.flow_conditions, Path):
            raise TypeError("[shock_standoff] flow_conditions must be a Path")

        # normalize selectors
        geometry_name = self.geometry.strip().lower()
        method_name = self.method.strip().lower()
        object.__setattr__(self, "geometry", geometry_name)
        object.__setattr__(self, "method", method_name)

        # validate physical and selector inputs
        if not math.isfinite(self.nose_radius) or self.nose_radius <= 0.0:
            raise ValueError("[shock_standoff] nose_radius must be positive")
        if geometry_name not in SHOCK_STANDOFF_GEOMETRIES:
            raise ValueError(
                f"[shock_standoff] geometry must be one of {SHOCK_STANDOFF_GEOMETRIES}"
            )
        if method_name not in SHOCK_STANDOFF_METHODS:
            raise ValueError(
                f"[shock_standoff] method must be one of {SHOCK_STANDOFF_METHODS}"
            )


# --------------------------------------------------
# public API
# --------------------------------------------------
def parse_shock_standoff_config(section: ConfigNode) -> ShockStandoffConfig:
    """Validate and convert a [shock_standoff] section."""

    # validate section structure
    validate_section_keys(
        section,
        section_name="shock_standoff",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    # validate the workflow toggle separately
    run_value = section.run
    if not isinstance(run_value, bool):
        raise ValueError("shock_standoff.run must be true or false")

    # convert required values
    flow_conditions = Path(str(section.flow_conditions))
    nose_radius = float(section.nose_radius)

    # convert optional values
    geometry = str(getattr(section, "geometry", "sphere"))
    method = str(getattr(section, "method", "ambrosio_wortman"))
    output = Path(str(section.output)) if hasattr(section, "output") else None

    config = ShockStandoffConfig(
        run=run_value,
        flow_conditions=flow_conditions,
        nose_radius=nose_radius,
        geometry=geometry,
        method=method,
        output=output,
    )

    return config
