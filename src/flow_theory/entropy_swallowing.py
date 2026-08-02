"""Entropy layer swallowing distance for conical bodies at hypersonic speeds.

Rotta, N. R. (1966). Effects of nose bluntness on the boundary layer
characteristics of conical bodies at hypersonic speeds
(No. NYU-AA-66-66).
NEW YORK UNIV BRONX DEPT OF AERONAUTICS AND ASTRONAUTICS.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

# --------------------------------------------------
# module constants
# --------------------------------------------------

# Blasius 99% laminar boundary-layer thickness constant: delta_99/x = _BLASIUS_C/sqrt(Re_x)
_BLASIUS_C = 5.0


# --------------------------------------------------
# internal helpers (not part of the public API)
# --------------------------------------------------

def _normal_shock_density_ratio(mach: float, gamma: float) -> float:
    """Return rho1/rho2 across a normal shock at the given Mach number.

    References:
        Anderson, J.D. (2003), "Modern Compressible Flow", 3rd ed., eq. 3.53.
    """
    # compute the normal-shock density ratio (upstream/downstream)
    return ((gamma - 1.0) * mach**2 + 2.0) / ((gamma + 1.0) * mach**2)


def _reference_temperature_ratio(mach: float, tw_t0: float, gamma: float, pr: float = 0.72) -> float:
    """Return T*/Te (Eckert reference temperature ratio) from tw_t0 and mach."""

    # convert stagnation-referenced wall temperature ratio to edge-referenced
    te_t0 = 1.0 / (1.0 + 0.5 * (gamma - 1.0) * mach**2)
    tw_te = tw_t0 / te_t0

    # compute Eckert (1955) reference temperature ratio
    return 0.5 + 0.039 * mach**2 + 0.5 * tw_te


def _boundary_layer_thickness(x: float, re1: float, mach: float, tw_t0: float, gamma: float) -> float:
    """Compressible laminar boundary-layer thickness estimate at station x."""

    # guard against x=0 (thickness is zero there by definition)
    if x <= 0.0:
        return 0.0

    # compute compressibility correction and local Reynolds number
    t_star_te = _reference_temperature_ratio(mach, tw_t0, gamma)
    re_x = re1 * x

    # return Blasius thickness (delta_99/x = C/sqrt(Re_x)) scaled by the
    # compressibility correction
    return _BLASIUS_C * x / np.sqrt(re_x) * t_star_te


# --------------------------------------------------
# public API
# --------------------------------------------------

def entropy_layer_thickness(x: float, r_nose: float, mach: float, gamma: float = 1.4) -> float:
    """Entropy layer thickness estimate at station x.

    Args:
        x: Streamwise distance from the nose [m].
        r_nose: Nose radius [m].
        mach: Edge Mach number.
        gamma: Specific heat ratio.

    Returns:
        Entropy layer thickness estimate [m].

    References:
        Lees, L. (1955), "Hypersonic flow", 5th International Aeronautical
        Conference, Los Angeles, pp. 241-276 (blast-wave analogy growth law).
        Rotta, N.R. (1966), "Effects of nose bluntness on the boundary layer
        characteristics of conical bodies at hypersonic speeds", NYU-AA-66-66.
    """

    # guard against x=0 (thickness is zero at the nose by definition)
    if x <= 0.0:
        return 0.0

    # compute shock-strength proxy from the normal-shock density ratio at mach
    epsilon = _normal_shock_density_ratio(mach, gamma)

    # apply the blast-wave far-field growth law (x/r_nose)^(1/3)
    x_bar = x / r_nose
    return r_nose * x_bar ** (1.0 / 3.0) * epsilon


def swallowing_distance(r_nose: float, re1: float, mach: float, tw_t0: float, gamma: float = 1.4) -> float:
    """Streamwise distance at which boundary layer swallows the entropy layer.

    Solves delta_BL(x_sw) = delta_EL(x_sw) for x_sw by root finding.

    Args:
        r_nose: Nose radius [m].
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        tw_t0: Wall-to-stagnation temperature ratio.
        gamma: Specific heat ratio.

    Returns:
        Swallowing distance x_sw [m].

    References:
        Rotta, N.R. (1966), "Effects of nose bluntness on the boundary layer
        characteristics of conical bodies at hypersonic speeds", NYU-AA-66-66.
        Stetson, K.F. (1983), "Nosetip bluntness effects on cone frustum
        boundary layer transition in hypersonic flow", AIAA 83-1763.
    """

    # define the thickness-balance residual: delta_BL(x) - delta_EL(x)
    def _residual(x: float) -> float:
        return (
            _boundary_layer_thickness(x, re1, mach, tw_t0, gamma)
            - entropy_layer_thickness(x, r_nose, mach, gamma)
        )

    # bracket the root: near the nose the entropy layer dominates (residual < 0),
    # far downstream the boundary layer dominates (residual > 0).  Expand the
    # bracket geometrically since the crossing location can range over many
    # orders of magnitude in r_nose and re1.
    x_lo = 1.0e-6 * r_nose
    x_hi = 1.0e6 * r_nose
    while _residual(x_hi) < 0.0:
        x_hi *= 100.0
    return brentq(_residual, x_lo, x_hi)


def is_swallowed(x: float, r_nose: float, re1: float, mach: float, tw_t0: float, gamma: float = 1.4) -> bool:
    """Return True if the entropy layer has been swallowed at x.

    Args:
        x: Streamwise distance from the nose [m].
        r_nose: Nose radius [m].
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        tw_t0: Wall-to-stagnation temperature ratio.
        gamma: Specific heat ratio.

    Returns:
        True if the boundary layer thickness exceeds the entropy layer
        thickness at x.

    References:
        Rotta, N.R. (1966), "Effects of nose bluntness on the boundary layer
        characteristics of conical bodies at hypersonic speeds", NYU-AA-66-66.
    """

    # compare boundary layer and entropy layer thickness directly at x
    delta_bl = _boundary_layer_thickness(x, re1, mach, tw_t0, gamma)
    delta_el = entropy_layer_thickness(x, r_nose, mach, gamma)
    return delta_bl >= delta_el
