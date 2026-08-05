"""Empirical detached bow-shock shapes for blunt hypersonic bodies."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from gasdyn import solve_oblique, solve_taylor_maccoll
from numpy.typing import NDArray

from flow_theory.geometry import (
    SURFACE_BLEND_GEOMETRIES,
    SURFACE_GEOMETRIES,
    build_surface_geometry,
)

from .standoff import ShockStandoffResult, compute_shock_standoff

# --------------------------------------------------
# module constants
# --------------------------------------------------

# Billig (1967) shock radius-of-curvature constants by geometry
_BILLIG_RC_PARAMS = {
    "sphere": {
        "coefficient": 1.143,
        "exponent_coefficient": 0.54,
        "exponent_power": 1.2,
    },
    "cylinder": {
        "coefficient": 1.386,
        "exponent_coefficient": 1.8,
        "exponent_power": 0.75,
    },
}

SHOCK_SHAPE_METHODS = ("billig",)
SHOCK_SHAPE_GEOMETRIES = SURFACE_GEOMETRIES


# --------------------------------------------------
# result type
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class ShockShapeResult:
    """Computed detached bow-shock locus."""

    x: NDArray[np.float64]
    y: NDArray[np.float64]
    body_x: NDArray[np.float64]
    body_y: NDArray[np.float64]
    standoff: ShockStandoffResult
    geometry: str
    method: str
    x_e: float
    half_angle: float | None = None
    asymptote_shock_angle: float | None = None
    virtual_cone_origin: float | None = None


# --------------------------------------------------
# helper functions
# --------------------------------------------------
def _build_billig_x_from_y(
    y: NDArray[np.float64],
    standoff_delta: float,
    shock_radius: float,
    tan_shock_angle: float,
    cotangent_squared: float,
) -> NDArray[np.float64]:
    """Evaluate Billig's hyperbola fit as x(y)."""

    # build repeated factors for readability
    tangent_squared = tan_shock_angle**2

    # evaluate the hyperbola relation in nose-tip coordinates
    hyperbola_term = (
        shock_radius
        * cotangent_squared
        * (np.sqrt(1.0 + tangent_squared * y**2 / shock_radius**2) - 1.0)
    )
    x = np.asarray(-standoff_delta + hyperbola_term, dtype=float)

    return x


def _build_billig_y_from_x(
    x: NDArray[np.float64],
    standoff_delta: float,
    shock_radius: float,
    tan_shock_angle: float,
    cotangent_squared: float,
) -> NDArray[np.float64]:
    """Evaluate Billig's hyperbola fit as y(x)."""

    # build the dimensionless square-root argument
    alpha = 1.0 + (x + standoff_delta) / (shock_radius * cotangent_squared)
    radicand = np.maximum(alpha**2 - 1.0, 0.0)

    # invert the hyperbola relation and keep non-negative y
    y = shock_radius / tan_shock_angle * np.sqrt(radicand)
    y = np.asarray(np.maximum(y, 0.0), dtype=float)

    return y


def _blend_billig_to_asymptote(
    x: NDArray[np.float64],
    y_billig: NDArray[np.float64],
    y_asymptote: NDArray[np.float64],
    x_e: float,
) -> NDArray[np.float64]:
    """Blend near-nose Billig shape into a far-field asymptote."""

    # set blend-window bounds along the streamwise coordinate
    blend_start = max(0.0, 0.15 * x_e)
    blend_end = max(blend_start + 1.0e-12, 0.60 * x_e)

    # convert x to a clamped [0, 1] interpolation coordinate
    xi = (x - blend_start) / (blend_end - blend_start)
    xi = np.clip(xi, 0.0, 1.0)

    # use a smoothstep profile to avoid slope jumps at blend bounds
    weight = xi * xi * (3.0 - 2.0 * xi)

    # build the composite y-locus
    y = (1.0 - weight) * y_billig + weight * y_asymptote
    y = np.asarray(y, dtype=float)

    return y


def _compute_asymptote_shock_angle(
    mach: float,
    gamma: float,
    geometry: str,
    half_angle: float,
) -> float:
    """Compute the far-field shock angle for blending."""

    # compute a conical-shock angle for cone geometry
    if geometry == "cone":
        cone_result = solve_taylor_maccoll(
            mach=mach,
            cone_angle=half_angle,
            gamma=gamma,
        )
        shock_angle = float(cone_result.shock_angle)
        return shock_angle

    # compute a weak oblique-shock angle for line-based deflection bodies
    oblique_result = solve_oblique(
        mach=mach,
        deflection_angle=half_angle,
        gamma=gamma,
        branch="weak",
    )
    shock_angle = float(oblique_result.shock_angle)

    return shock_angle


# --------------------------------------------------
# public API
# --------------------------------------------------
def compute_shock_shape(
    mach: float,
    gamma: float,
    nose_radius: float,
    geometry: str = "sphere",
    method: str = "billig",
    half_angle: float | None = None,
    n_points: int = 100,
    x_e: float | None = None,
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
        half_angle: Half-angle used for cone/wedge/ogive geometries.
        n_points: Number of sampled shock-locus points.
        x_e: Streamwise endpoint for body and shock sampling.

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

    # read direct input values
    x_e_raw = x_e
    half_angle_raw = half_angle

    # validate the streamwise endpoint used for all geometries
    if x_e_raw is None:
        raise ValueError("x_e is required")
    x_e_value = float(x_e_raw)
    if not math.isfinite(x_e_value) or x_e_value <= 0.0:
        raise ValueError(f"x_e must be finite and positive: {x_e_value}")

    # validate geometry-specific angle requirements
    if geometry_name in SURFACE_BLEND_GEOMETRIES:
        if half_angle_raw is None:
            raise ValueError(
                "half_angle is required for cone, ogive, and wedge geometries"
            )
        half_angle_value = float(half_angle_raw)
        if not math.isfinite(half_angle_value) or half_angle_value <= 0.0:
            raise ValueError(
                f"half_angle must be finite and positive: {half_angle_value}"
            )
    else:
        half_angle_value = None

    # build body-surface coordinates and geometry metadata
    surface_geometry = build_surface_geometry(
        geometry=geometry_name,
        nose_radius=nose_radius,
        x_e=x_e_value,
        n_points=n_points,
        half_angle=half_angle_value,
    )

    # compute the standoff distance used by the shock-shape correlation
    standoff_geometry = surface_geometry.standoff_geometry

    standoff = compute_shock_standoff(
        mach=mach,
        nose_radius=nose_radius,
        geometry=standoff_geometry,
        method="ambrosio_wortman",
        gamma=gamma,
    )

    # read Billig geometry constants for the shock radius relation
    billig_geometry = surface_geometry.billig_reference_geometry

    radius_params = _BILLIG_RC_PARAMS[billig_geometry]
    radius_coefficient = radius_params["coefficient"]
    exponent_coefficient = radius_params["exponent_coefficient"]
    exponent_power = radius_params["exponent_power"]

    # compute Billig's shock radius of curvature at the nose
    shock_radius = (
        radius_coefficient
        * math.exp(exponent_coefficient / (mach - 1.0) ** exponent_power)
        * nose_radius
    )

    # use the Mach angle for the asymptote of the sphere correlation
    shock_angle = math.asin(1.0 / mach)
    tan_shock_angle = math.tan(shock_angle)
    cotangent_squared = 1.0 / tan_shock_angle**2

    # build the x-grid used to sample the shock from the vertex to x_e
    x = np.linspace(-standoff.delta, x_e_value, n_points)

    # evaluate Billig's shape on the streamwise sampling grid
    y_billig = _build_billig_y_from_x(
        x=x,
        standoff_delta=standoff.delta,
        shock_radius=shock_radius,
        tan_shock_angle=tan_shock_angle,
        cotangent_squared=cotangent_squared,
    )

    # read shared body-surface coordinates
    body_x = surface_geometry.body_x
    body_y = surface_geometry.body_y

    # compute geometry-specific surface and shock continuation
    if surface_geometry.requires_blend:
        assert half_angle_value is not None
        assert surface_geometry.virtual_cone_origin is not None

        # read the virtual origin from geometry model output
        virtual_cone_origin = surface_geometry.virtual_cone_origin

        # compute the asymptotic shock angle based on selected geometry
        asymptote_shock_angle = _compute_asymptote_shock_angle(
            mach=mach,
            gamma=gamma,
            geometry=geometry_name,
            half_angle=half_angle_value,
        )
        asymptote_angle_rad = math.radians(asymptote_shock_angle)
        asymptote_tangent = math.tan(asymptote_angle_rad)
        y_asymptote = asymptote_tangent * (x + virtual_cone_origin)
        y_asymptote = np.asarray(np.maximum(y_asymptote, 0.0), dtype=float)

        # blend near-nose Billig shock into far-field asymptotic shock line
        y = _blend_billig_to_asymptote(
            x=x,
            y_billig=y_billig,
            y_asymptote=y_asymptote,
            x_e=x_e_value,
        )
    else:
        y = y_billig
        asymptote_shock_angle = None
        virtual_cone_origin = None

    result = ShockShapeResult(
        x=x,
        y=y,
        body_x=body_x,
        body_y=body_y,
        standoff=standoff,
        geometry=geometry_name,
        method=method_name,
        x_e=x_e_value,
        half_angle=half_angle_value,
        asymptote_shock_angle=asymptote_shock_angle,
        virtual_cone_origin=virtual_cone_origin,
    )

    return result
