"""Empirical detached bow-shock shapes for blunt hypersonic bodies."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .standoff import ShockStandoffResult, compute_shock_standoff

# --------------------------------------------------
# module constants
# --------------------------------------------------

# Billig (1967) sphere shock radius-of-curvature correlation constants
_BILLIG_SPHERE_RC_COEFF = 1.143
_BILLIG_SPHERE_RC_EXP = 0.54

SHOCK_SHAPE_GEOMETRIES = ("sphere",)
SHOCK_SHAPE_METHODS = ("billig",)


# --------------------------------------------------
# result type
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class ShockShapeResult:
    """Computed detached bow-shock locus."""

    x: NDArray[np.float64]
    y: NDArray[np.float64]
    standoff: ShockStandoffResult
    geometry: str
    method: str


# --------------------------------------------------
# public API
# --------------------------------------------------
def compute_shock_shape(
    mach: float,
    gamma: float,
    nose_radius: float,
    geometry: str = "sphere",
    method: str = "billig",
    n_points: int = 100,
    lateral_extent: float | None = None,
) -> ShockShapeResult:
    """Compute a detached bow-shock locus.

    The body nose tip is at ``x=0`` and the freestream points in the positive
    x direction. The shock vertex is therefore located at ``x=-delta``.

    Args:
        mach: Freestream Mach number.
        gamma: Specific heat ratio.
        nose_radius: Body nose radius.
        geometry: Body geometry supported by the selected correlation.
        method: Shock-shape correlation name.
        n_points: Number of sampled shock-locus points.
        lateral_extent: Maximum lateral coordinate. Defaults to three nose radii.

    Returns:
        Typed shock coordinates and the standoff result used to construct them.

    Raises:
        ValueError: If an input or selector is invalid.

    References:
        Billig (1967), "Shock-wave shapes around spherical- and cylindrical-nosed
        bodies", J. Spacecraft Rockets, 4(6), 822-823.
    """

    # normalize selectors
    geometry_name = str(geometry).strip().lower()
    method_name = str(method).strip().lower()

    # validate shape-specific inputs
    if geometry_name not in SHOCK_SHAPE_GEOMETRIES:
        raise ValueError(
            f"geometry must be one of {SHOCK_SHAPE_GEOMETRIES}: got {geometry_name!r}"
        )
    if method_name not in SHOCK_SHAPE_METHODS:
        raise ValueError(
            f"method must be one of {SHOCK_SHAPE_METHODS}: got {method_name!r}"
        )
    if isinstance(n_points, bool) or not isinstance(n_points, int) or n_points < 2:
        raise ValueError(f"n_points must be an integer of at least 2: {n_points}")

    # resolve and validate the sampled lateral extent
    if lateral_extent is None:
        lateral_extent_value = 3.0 * nose_radius
    else:
        lateral_extent_value = float(lateral_extent)

    if not math.isfinite(lateral_extent_value) or lateral_extent_value <= 0.0:
        raise ValueError(
            f"lateral_extent must be finite and positive: {lateral_extent_value}"
        )

    # compute the standoff distance used by the shock-shape correlation
    standoff = compute_shock_standoff(
        mach=mach,
        nose_radius=nose_radius,
        geometry=geometry_name,
        method="ambrosio_wortman",
        gamma=gamma,
    )

    # build the lateral coordinate array
    y = np.linspace(0.0, lateral_extent_value, n_points)

    # compute Billig's shock radius of curvature at the nose
    shock_radius = (
        _BILLIG_SPHERE_RC_COEFF
        * math.exp(_BILLIG_SPHERE_RC_EXP / (mach - 1.0) ** 1.2)
        * nose_radius
    )

    # use the Mach angle for the asymptote of the sphere correlation
    shock_angle = math.asin(1.0 / mach)
    cotangent_squared = 1.0 / math.tan(shock_angle) ** 2
    tangent_squared = math.tan(shock_angle) ** 2

    # evaluate Billig's hyperbola fit
    hyperbola_term = (
        shock_radius
        * cotangent_squared
        * (np.sqrt(1.0 + tangent_squared * y**2 / shock_radius**2) - 1.0)
    )
    x = np.asarray(-standoff.delta + hyperbola_term, dtype=float)

    result = ShockShapeResult(
        x=x,
        y=y,
        standoff=standoff,
        geometry=geometry_name,
        method=method_name,
    )

    return result
