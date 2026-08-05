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
    "half_angle",
    "flow_conditions",
    "geometry",
    "method",
    "n_points",
    "nose_radius",
    "output",
    "run",
    "x_e",
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
    half_angle: float | None = None
    n_points: int = 100
    x_e: float = 0.1
    output: Path | None = None

    # --------------------------------------------------
    # operations carried out after initialization
    # --------------------------------------------------
    def __post_init__(self) -> None:
        """Normalize and validate shock-shape options."""

        # validate the required flow-state input
        if not isinstance(self.flow_conditions, Path):
            raise TypeError("[shock_shape] flow_conditions must be a Path")

        # normalize (lowercase and stripped) the geometry name
        geometry_name = self.geometry.strip().lower()
        # set the normalized geometry name back to the frozen dataclass
        object.__setattr__(self, "geometry", geometry_name)

        # normalize (lowercase and stripped) the method name
        method_name = self.method.strip().lower()
        # set the normalized method name back to the frozen dataclass
        object.__setattr__(self, "method", method_name)

        # validate nose radius input (cannot be zero or negative)
        if not math.isfinite(self.nose_radius) or self.nose_radius <= 0.0:
            raise ValueError("[shock_shape] nose_radius must be positive")

        # check if geometry name is in supported list
        if geometry_name not in SHOCK_SHAPE_GEOMETRIES:
            raise ValueError(
                f"[shock_shape] geometry must be one of {SHOCK_SHAPE_GEOMETRIES}"
            )

        # check if method name is in supported list
        if method_name not in SHOCK_SHAPE_METHODS:
            raise ValueError(
                f"[shock_shape] method must be one of {SHOCK_SHAPE_METHODS}"
            )

        # check that n_points is a positive integer
        if (
            isinstance(self.n_points, bool)
            or not isinstance(self.n_points, int)
            or self.n_points < 2
        ):
            raise ValueError("[shock_shape] n_points must be an integer of at least 2")

        # check that x_e is a positive number
        if not math.isfinite(self.x_e) or self.x_e <= 0.0:
            raise ValueError("[shock_shape] x_e must be positive")

        # validate geometry-specific input requirements
        if geometry_name in {"cone", "wedge"}:

            # cone and wedge require a half-angle to be specified
            if self.half_angle is None:
                raise ValueError(
                    "[shock_shape] half_angle is required for cone and wedge"
                )

            # make sure the half-angle is a positive number
            if (
                not math.isfinite(self.half_angle)
                or self.half_angle <= 0.0
            ):
                raise ValueError("[shock_shape] half_angle must be positive")

# --------------------------------------------------
# public API
# --------------------------------------------------
def parse_shock_shape_config(section: ConfigNode) -> ShockShapeConfig:
    """Validate and convert a [shock_shape] section."""

    # validate section structure (defined in config/schema.py)
    # _ALLOWED_KEYS are added to the section
    # _REQUIRED_KEYS are checked for presence in the section
    validate_section_keys(
        section,
        section_name="shock_shape",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    # check if run is a boolean variable
    if not isinstance(section.run, bool):
        raise ValueError("shock_shape.run must be true or false")

    # confert flow conditions to a Path
    flow_conditions = Path(str(section.flow_conditions))

    # convert nose radius to a float
    nose_radius = float(section.nose_radius)

    # convert geometry to string
    geometry = str(getattr(section, "geometry", "sphere"))

    # convert method to string
    method = str(getattr(section, "method", "billig"))

    # read optional geometry angle
    if hasattr(section, "half_angle"):
        half_angle = float(section.half_angle)
    else:
        half_angle = None

    # get number of points (default to 100 if not specified)
    n_points = getattr(section, "n_points", 100)

    # read required streamwise endpoint
    if not hasattr(section, "x_e"):
        raise ValueError("[shock_shape] x_e is required")

    # convert x_e to a float
    x_e = float(section.x_e)

    # read optional output path otherwise assign none
    if hasattr(section, "output"):
        output = Path(str(section.output))
    else:
        output = None

    # build the typed configuration dataclass
    config = ShockShapeConfig(
        run=section.run,
        flow_conditions=flow_conditions,
        nose_radius=nose_radius,
        geometry=geometry,
        method=method,
        half_angle=half_angle,
        n_points=n_points,
        x_e=x_e,
        output=output,
    )

    return config
