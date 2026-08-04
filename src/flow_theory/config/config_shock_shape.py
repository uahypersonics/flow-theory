"""Configuration adapter for the [shock_shape] workflow section."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from flow_theory.shock.shape import SHOCK_SHAPE_GEOMETRIES, SHOCK_SHAPE_METHODS

from .schema import ConfigNode, validate_section_keys

# --------------------------------------------------
# section structure
# --------------------------------------------------
_ALLOWED_KEYS = {
    "flow_conditions",
    "geometry",
    "lateral_extent",
    "method",
    "n_points",
    "nose_radius",
    "output",
    "run",
}

_REQUIRED_KEYS = {"flow_conditions", "nose_radius", "run"}


# --------------------------------------------------
# typed configuration
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class ShockShapeConfig:
    """Validated inputs for a shock-shape calculation."""

    run: bool
    flow_conditions: Path
    nose_radius: float
    geometry: str = "sphere"
    method: str = "billig"
    n_points: int = 100
    lateral_extent: float | None = None
    output: Path | None = None

    def __post_init__(self) -> None:
        """Normalize and validate shock-shape options."""

        # validate the required flow-state input
        if not isinstance(self.flow_conditions, Path):
            raise TypeError("[shock_shape] flow_conditions must be a Path")

        # normalize selectors
        geometry_name = self.geometry.strip().lower()
        method_name = self.method.strip().lower()
        object.__setattr__(self, "geometry", geometry_name)
        object.__setattr__(self, "method", method_name)

        # validate physical and selector inputs
        if not math.isfinite(self.nose_radius) or self.nose_radius <= 0.0:
            raise ValueError("[shock_shape] nose_radius must be positive")
        if geometry_name not in SHOCK_SHAPE_GEOMETRIES:
            raise ValueError(
                f"[shock_shape] geometry must be one of {SHOCK_SHAPE_GEOMETRIES}"
            )
        if method_name not in SHOCK_SHAPE_METHODS:
            raise ValueError(
                f"[shock_shape] method must be one of {SHOCK_SHAPE_METHODS}"
            )
        if (
            isinstance(self.n_points, bool)
            or not isinstance(self.n_points, int)
            or self.n_points < 2
        ):
            raise ValueError("[shock_shape] n_points must be an integer of at least 2")
        if self.lateral_extent is not None and (
            not math.isfinite(self.lateral_extent) or self.lateral_extent <= 0.0
        ):
            raise ValueError("[shock_shape] lateral_extent must be positive")


# --------------------------------------------------
# public API
# --------------------------------------------------
def parse_shock_shape_config(section: ConfigNode) -> ShockShapeConfig:
    """Validate and convert a [shock_shape] section."""

    # validate section structure
    validate_section_keys(
        section,
        section_name="shock_shape",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    # validate the workflow toggle separately
    run_value = section.run
    if not isinstance(run_value, bool):
        raise ValueError("shock_shape.run must be true or false")

    # convert required values
    flow_conditions = Path(str(section.flow_conditions))
    nose_radius = float(section.nose_radius)

    # convert optional values
    geometry = str(getattr(section, "geometry", "sphere"))
    method = str(getattr(section, "method", "billig"))
    n_points = getattr(section, "n_points", 100)
    lateral_extent = (
        float(section.lateral_extent) if hasattr(section, "lateral_extent") else None
    )
    output = Path(str(section.output)) if hasattr(section, "output") else None

    config = ShockShapeConfig(
        run=run_value,
        flow_conditions=flow_conditions,
        nose_radius=nose_radius,
        geometry=geometry,
        method=method,
        n_points=n_points,
        lateral_extent=lateral_extent,
        output=output,
    )

    return config
