"""Entropy-layer thickness estimates for blunt hypersonic bodies."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from gasdyn import dens_ratio_normal


# --------------------------------------------------
# internal helpers
# --------------------------------------------------
def _normal_shock_density_ratio(mach: float, gamma: float) -> float:
    """Return rho1/rho2 across a normal shock at the given Mach number.

    References:
        Anderson, J.D. (2003), "Modern Compressible Flow", 3rd ed., eq. 3.53.
    """

    # compute the normal-shock density ratio (upstream/downstream)
    density_ratio = 1.0 / dens_ratio_normal(mach, gamma)
    return density_ratio


# --------------------------------------------------
# public API
# --------------------------------------------------
def entropy_layer_thickness(
    x: float,
    r_nose: float,
    mach: float,
    gamma: float = 1.4,
) -> float:
    """Estimate the entropy-layer thickness at a streamwise station.

    Args:
        x: Streamwise distance from the nose [m].
        r_nose: Nose radius [m].
        mach: Edge Mach number.
        gamma: Specific heat ratio.

    Returns:
        Entropy-layer thickness estimate [m].

    References:
        Lees, L. (1955), "Hypersonic flow", 5th International Aeronautical
        Conference, Los Angeles, pp. 241-276 (blast-wave analogy growth law).
        Rotta, N.R. (1966), "Effects of nose bluntness on the boundary layer
        characteristics of conical bodies at hypersonic speeds", NYU-AA-66-66.
    """

    # guard against x=0 because thickness is zero at the nose by definition
    if x <= 0.0:
        thickness = 0.0
    else:
        # compute a shock-strength proxy from the normal-shock density ratio
        epsilon = _normal_shock_density_ratio(mach, gamma)

        # apply the blast-wave far-field growth law
        x_bar = x / r_nose
        thickness = r_nose * x_bar ** (1.0 / 3.0) * epsilon

    return thickness
