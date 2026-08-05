"""Body-surface construction for shock-shape workflows."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

# --------------------------------------------------
# module constants
# --------------------------------------------------
SURFACE_BLEND_GEOMETRIES = ("cone", "ogive", "wedge")
SURFACE_GEOMETRIES = (
    "sphere",
    "cylinder",
    "cone",
    "ogive",
    "wedge",
)


# --------------------------------------------------
# result type
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class SurfaceGeometryResult:
    """Sampled body surface and geometry metadata."""

    geometry: str
    body_x: NDArray[np.float64]
    body_y: NDArray[np.float64]
    standoff_geometry: str
    billig_reference_geometry: str
    requires_blend: bool
    virtual_cone_origin: float | None = None


# --------------------------------------------------
# helper functions
# --------------------------------------------------
def _build_spherical_cap_surface(
    x: NDArray[np.float64],
    nose_radius: float,
) -> NDArray[np.float64]:
    """Build the upper branch of a spherical-cap surface."""

    # evaluate y from the circle centered at (R, 0): (x-R)^2 + y^2 = R^2
    radicand = np.maximum(2.0 * nose_radius * x - x**2, 0.0)
    y = np.sqrt(radicand)
    y = np.asarray(y, dtype=float)

    return y


def _build_blunt_body_surface(
    x: NDArray[np.float64],
    nose_radius: float,
    half_angle: float,
) -> tuple[NDArray[np.float64], float]:
    """Build a spherical-nose body blended into a straight afterbody line."""

    # convert the body half-angle to radians for geometric relations
    half_angle_rad = math.radians(half_angle)

    # compute spherical-cap tangency point with the straight afterbody line
    x_tangent = nose_radius * (1.0 - math.sin(half_angle_rad))
    y_tangent = nose_radius * math.cos(half_angle_rad)

    # evaluate spherical nose up to the tangency location
    x_nose = np.minimum(x, x_tangent)
    y_nose = _build_spherical_cap_surface(x=x_nose, nose_radius=nose_radius)

    # evaluate straight afterbody beyond tangency
    tan_half_angle = math.tan(half_angle_rad)
    y_line = y_tangent + tan_half_angle * (x - x_tangent)

    # assemble the piecewise body profile
    y = np.where(x <= x_tangent, y_nose, y_line)
    y = np.asarray(y, dtype=float)

    # compute virtual origin used by line-based asymptotes
    virtual_origin = nose_radius * (1.0 / math.sin(half_angle_rad) - 1.0)

    return y, virtual_origin


# --------------------------------------------------
# public API
# --------------------------------------------------
def build_surface_geometry(
    geometry: str,
    nose_radius: float,
    x_e: float,
    n_points: int,
    half_angle: float | None,
) -> SurfaceGeometryResult:
    """Build a sampled body surface for a selected geometry.

    Args:
        geometry: Body geometry selector.
        nose_radius: Nose radius.
        x_e: Streamwise endpoint from the nose/leading edge.
        n_points: Number of sampled points.
        half_angle: Half-angle for blended geometries.

    Returns:
        SurfaceGeometryResult with sampled body coordinates and metadata.
    """

    # normalize geometry selector
    geometry_name = str(geometry).strip().lower()

    # check geometry selector
    if geometry_name not in SURFACE_GEOMETRIES:
        raise ValueError(
            f"geometry must be one of {SURFACE_GEOMETRIES}: got {geometry_name!r}"
        )

    # build the default streamwise sampling array
    body_x = np.linspace(0.0, x_e, n_points)

    # build standalone sphere and cylinder caps (no trailing zero segment)
    if geometry_name == "sphere":
        x_cap_end = min(x_e, 2.0 * nose_radius)
        body_x = np.linspace(0.0, x_cap_end, n_points)
        body_y = _build_spherical_cap_surface(x=body_x, nose_radius=nose_radius)

        result = SurfaceGeometryResult(
            geometry=geometry_name,
            body_x=body_x,
            body_y=body_y,
            standoff_geometry="sphere",
            billig_reference_geometry="sphere",
            requires_blend=False,
            virtual_cone_origin=None,
        )
        return result

    if geometry_name == "cylinder":
        x_cap_end = min(x_e, 2.0 * nose_radius)
        body_x = np.linspace(0.0, x_cap_end, n_points)
        body_y = _build_spherical_cap_surface(x=body_x, nose_radius=nose_radius)

        result = SurfaceGeometryResult(
            geometry=geometry_name,
            body_x=body_x,
            body_y=body_y,
            standoff_geometry="cylinder",
            billig_reference_geometry="cylinder",
            requires_blend=False,
            virtual_cone_origin=None,
        )
        return result

    # check geometry-specific angle for blended geometries
    if half_angle is None:
        raise ValueError(
            "half_angle is required for cone, ogive, and wedge geometries"
        )

    # build the blunt-nose + straight-afterbody profile
    body_y, virtual_cone_origin = _build_blunt_body_surface(
        x=body_x,
        nose_radius=nose_radius,
        half_angle=half_angle,
    )

    result = SurfaceGeometryResult(
        geometry=geometry_name,
        body_x=body_x,
        body_y=body_y,
        standoff_geometry="sphere",
        billig_reference_geometry="sphere",
        requires_blend=True,
        virtual_cone_origin=virtual_cone_origin,
    )

    return result
