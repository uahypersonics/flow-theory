"""Entropy-layer swallowing distance for conical hypersonic bodies.

Rotta, N. R. (1966). Effects of nose bluntness on the boundary layer
characteristics of conical bodies at hypersonic speeds
(No. NYU-AA-66-66).
NEW YORK UNIV BRONX DEPT OF AERONAUTICS AND ASTRONAUTICS.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from scipy.optimize import brentq

from flow_theory.boundary_layer import compute_boundary_layer_thickness

from .estimate import entropy_layer_thickness


# --------------------------------------------------
# public API
# --------------------------------------------------
def swallowing_distance(
    r_nose: float,
    re1: float,
    mach: float,
    tw_t0: float,
    gamma: float = 1.4,
) -> float:
    """Compute where the boundary layer swallows the entropy layer.

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

    # define the thickness-balance residual
    def _residual(x: float) -> float:
        boundary_layer = compute_boundary_layer_thickness(
            x=x,
            re1=re1,
            method="eckert_reference",
            mach=mach,
            tw_t0=tw_t0,
            gamma=gamma,
        )
        entropy_layer = entropy_layer_thickness(x, r_nose, mach, gamma)
        residual = boundary_layer.delta_99 - entropy_layer
        return residual

    # bracket the root over the broad range used by the original implementation
    x_lo = 1.0e-6 * r_nose
    x_hi = 1.0e6 * r_nose
    while _residual(x_hi) < 0.0:
        x_hi *= 100.0

    # solve the thickness crossing within the bracket
    distance = brentq(_residual, x_lo, x_hi)
    return distance


def is_swallowed(
    x: float,
    r_nose: float,
    re1: float,
    mach: float,
    tw_t0: float,
    gamma: float = 1.4,
) -> bool:
    """Return whether the boundary layer has swallowed the entropy layer.

    Args:
        x: Streamwise distance from the nose [m].
        r_nose: Nose radius [m].
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        tw_t0: Wall-to-stagnation temperature ratio.
        gamma: Specific heat ratio.

    Returns:
        True if the boundary-layer thickness is at least the entropy-layer
        thickness at x.
    """

    # compare the two thickness estimates at the requested station
    boundary_layer = compute_boundary_layer_thickness(
        x=x,
        re1=re1,
        method="eckert_reference",
        mach=mach,
        tw_t0=tw_t0,
        gamma=gamma,
    )
    entropy_layer = entropy_layer_thickness(x, r_nose, mach, gamma)
    swallowed = boundary_layer.delta_99 >= entropy_layer
    return swallowed
