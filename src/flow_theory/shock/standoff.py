"""Empirical bow-shock standoff estimates for blunt hypersonic bodies."""

# --------------------------------------------------
# References:
#
# Ambrosio, A., and Wortman, A. (1962), "Stagnation-point shock-detachment distance for flow around spheres and cylinders in air," ARS Journal, Vol. 32, No. 2, p. 281.
# Billig, F. S. (1967), "Shock-wave shapes around spherical- and cylindrical-nosed bodies," J. Spacecraft Rockets, Vol. 4, No. 6, pp. 822-823.
# Serbin, H. (1958), "Supersonic flow around blunt bodies," Journal of the Aeronautical Sciences, Vol. 25, No. 1.
# --------------------------------------------------

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass

from gasdyn import dens_ratio_normal

# --------------------------------------------------
# module constants
# --------------------------------------------------
SHOCK_STANDOFF_GEOMETRIES = ("cylinder", "sphere")
SHOCK_STANDOFF_METHODS = (
    "ambrosio_wortman",
    "ambrosio_wortman_density_ratio",
    "serbin",
)

# --------------------------------------------------
# result type
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class ShockStandoffResult:
    """Computed normal-shock standoff distance."""

    mach: float
    gamma: float | None
    nose_radius: float
    delta: float
    delta_over_radius: float
    geometry: str
    method: str


# --------------------------------------------------
# ambrosio & wortman (1962) correlation
# --------------------------------------------------
def _compute_standoff_ambrosio_wortman(mach: float, geometry: str) -> float:
    """Compute the non-dimensional standoff distance for a cylinder or sphere according to Ambrosio & Wortman (1962)."""

    if(geometry == "cylinder"):
        delta_over_radius = 0.386 * math.exp(4.67 / mach**2)
    elif(geometry == "sphere"):
        delta_over_radius = 0.143 * math.exp(3.24 / mach**2)

    return delta_over_radius

# --------------------------------------------------
# ambrosio & wortman density based correlation
# --------------------------------------------------
def _compute_standoff_ambrosio_wortman_density_ratio(
    density_ratio: float,
    geometry: str,
) -> float:
    """Compute the non-dimensional Ambrosio-Wortman density-ratio fit."""

    if geometry == "cylinder":
        delta_over_radius = 2.52 * (density_ratio - 1.0) ** -1.25
    elif geometry == "sphere":
        delta_over_radius = 0.52 * (density_ratio - 1.0) ** -0.861

    return delta_over_radius

# --------------------------------------------------
# serbin (1958) correlation (note: only valid for a sphere)
# --------------------------------------------------
def _compute_standoff_serbin(density_ratio: float) -> float:
    """Compute the non-dimensional Serbin sphere standoff distance."""

    delta_over_radius = (2.0 / 3.0) * (density_ratio - 1.0) ** -1.0

    return delta_over_radius

# --------------------------------------------------
# public API
# --------------------------------------------------
def compute_shock_standoff(
    mach: float,
    nose_radius: float,
    geometry: str = "sphere",
    method: str = "ambrosio_wortman",
    gamma: float | None = None,
) -> ShockStandoffResult:
    """Compute the normal-shock standoff distance.

    Args:
        mach: Freestream Mach number.
        nose_radius: Body nose radius.
        geometry: ``"sphere"`` or ``"cylinder"``.
        method: Standoff correlation name.
        gamma: Specific heat ratio, required by density-ratio methods.

    Returns:
        Typed dimensional and non-dimensional standoff result.

    Raises:
        ValueError: If an input or selector is invalid.

    References:
        Ambrosio and Wortman (1962), "Stagnation-point shock-detachment distance
        for flow around spheres and cylinders in air", ARS Journal, 32(2), 281.
        Serbin (1958), "Supersonic flow around blunt bodies", Journal of the
        Aeronautical Sciences, 25(1).
    """

    # --------------------------------------------------
    # normalize selectors: remove all white space and convert to lowercase strings
    # --------------------------------------------------
    geometry_name = str(geometry).strip().lower()
    method_name = str(method).strip().lower()

    # --------------------------------------------------
    # inpute validation: catch inputs that would lead to invalid calculations
    # --------------------------------------------------

    # mach number must be finite and larger than 1
    if not math.isfinite(mach) or mach <= 1.0:
        raise ValueError(f"mach must be finite and greater than 1: {mach}")

    # nose radius must be finite and positive
    if not math.isfinite(nose_radius) or nose_radius <= 0.0:
        raise ValueError(f"nose_radius must be finite and positive: {nose_radius}")

    # geometry must be in the list of supported geometries (devined above)
    if geometry_name not in SHOCK_STANDOFF_GEOMETRIES:
        raise ValueError(
            f"geometry must be one of {SHOCK_STANDOFF_GEOMETRIES}: "
            f"got {geometry_name!r}"
        )

    # method must be in the list of supported methods (defiend above)
    if method_name not in SHOCK_STANDOFF_METHODS:
        raise ValueError(
            f"method must be one of {SHOCK_STANDOFF_METHODS}: got {method_name!r}"
        )

    # Serbin's relation applies to a sphere, not a cylinder
    if method_name == "serbin" and geometry_name == "cylinder":
        raise ValueError(
            "method 'serbin' does not support geometry 'cylinder'"
        )

    # gamma is required only when the method uses the normal-shock density ratio
    density_ratio_methods = ("ambrosio_wortman_density_ratio", "serbin")
    if method_name in density_ratio_methods:
        if gamma is None:
            raise ValueError(f"gamma is required when method={method_name!r}")
        if not math.isfinite(gamma) or gamma <= 1.0:
            raise ValueError(f"gamma must be finite and greater than 1: {gamma}")

    # --------------------------------------------------
    # compute the standoff distance
    # --------------------------------------------------
    if method_name == "ambrosio_wortman":
        # abrosio & wortman (1962) correlation
        delta_over_radius = _compute_standoff_ambrosio_wortman(mach, geometry_name)
    elif method_name == "ambrosio_wortman_density_ratio":
        # ambrosio & wortman density-ratio correlation
        density_ratio = dens_ratio_normal(mach, gamma)
        delta_over_radius = _compute_standoff_ambrosio_wortman_density_ratio(
            density_ratio,
            geometry_name,
        )
    elif method_name == "serbin":
        # serbin (1958) correlation
        density_ratio = dens_ratio_normal(mach, gamma)
        delta_over_radius = _compute_standoff_serbin(density_ratio)

    # dimensionalize the result with the nose radius
    delta = delta_over_radius * nose_radius

    # build the result dataclass
    result = ShockStandoffResult(
        mach=mach,
        gamma=gamma,
        nose_radius=nose_radius,
        delta=delta,
        delta_over_radius=delta_over_radius,
        geometry=geometry_name,
        method=method_name,
    )

    return result
