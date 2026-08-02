"""Empirical detached bow-shock shape for blunt hypersonic bodies

Provides the Billig (1967) hyperbola fit for the shock locus around a
spherically-blunted nose, as a function of lateral (body-normal) distance
from the axis.

Design
------
Coordinate convention: the body nose tip is at x=0, with the freestream
flowing in the +x direction.  The detached bow shock stands off *upstream*
of the nose (negative x) by the standoff distance from `shock_standoff` at
the axis (s=0), then sweeps back downstream (increasing x) as the lateral
distance s from the axis increases, approaching the freestream Mach cone
asymptote far from the nose, following Billig's hyperbola fit:

    x_shock(s) = -Delta + Rc*cot^2(theta)*(sqrt(1 + tan^2(theta)*s^2/Rc^2) - 1)

where Rc is the shock radius of curvature at the nose and theta is the
asymptotic shock wave angle (the Mach angle, since far from the nose the
shock approaches the freestream Mach cone for a body with no continuing
cone half-angle).  See the Billig (1967) VnV case
(docs/vnv/validation/billig_1967_shock_shape/index.md) for a numeric check
of this formula and its asymptotic behavior against the worked example in
the original paper.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from flow_theory.shock_standoff import standoff_sphere

# --------------------------------------------------
# module constants
# --------------------------------------------------

# Billig (1967) sphere shock radius-of-curvature correlation constants
_BILLIG_SPHERE_RC_COEFF = 1.143
_BILLIG_SPHERE_RC_EXP = 0.54


# --------------------------------------------------
# public API
# --------------------------------------------------
def shock_shape_billig(
    mach: float, gamma: float, r_nose: float, s_array: NDArray
) -> NDArray:
    """Detached shock standoff as function of lateral distance s from axis.

    Args:
        mach: Freestream Mach number.
        gamma: Specific heat ratio.
        r_nose: Nose radius [same units as s_array].
        s_array: Lateral distances from body axis [same units as r_nose].

    Returns:
        x_shock: Axial shock location at each s [same units as r_nose].
        Negative values are upstream of the nose tip (x=0); the shock
        sweeps back downstream (x increasing) as s grows, approaching the
        freestream Mach cone asymptote -- see module docstring for the sign
        convention.

    References:
        Billig (1967), "Shock-wave shapes around spherical- and cylindrical-nosed
        bodies", J. Spacecraft Rockets, 4(6), 822-823.
    """

    # convert input to array for vectorized evaluation
    s_array = np.asarray(s_array, dtype=float)

    # compute standoff distance and shock radius of curvature at the nose
    Delta = standoff_sphere(mach, gamma=gamma) * r_nose
    Rc = _BILLIG_SPHERE_RC_COEFF * np.exp(_BILLIG_SPHERE_RC_EXP / (mach - 1.0) ** 1.2) * r_nose

    # asymptotic shock angle: Mach angle (sphere/cylinder alone, no afterbody cone)
    theta = np.arcsin(1.0 / mach)
    cot2_theta = 1.0 / np.tan(theta) ** 2
    tan2_theta = np.tan(theta) ** 2

    # evaluate Billig's hyperbola fit: standoff upstream at the axis (s=0),
    # sweeping back downstream (increasing x) as s grows toward the
    # freestream Mach cone asymptote
    hyperbola_term = Rc * cot2_theta * (np.sqrt(1.0 + tan2_theta * s_array**2 / Rc**2) - 1.0)
    return -Delta + hyperbola_term


def shock_shape_points(
    mach: float, gamma: float, r_nose: float, n_pts: int = 100
) -> tuple[NDArray, NDArray]:
    """Return (x, y) array of shock locus points for plotting.

    Args:
        mach: Freestream Mach number.
        gamma: Specific heat ratio.
        r_nose: Nose radius.
        n_pts: Number of points along the shock locus.

    Returns:
        (x, y): Axial and lateral shock coordinates [same units as r_nose].

    References:
        Billig (1967), "Shock-wave shapes around spherical- and cylindrical-nosed
        bodies", J. Spacecraft Rockets, 4(6), 822-823.
    """

    # build a lateral distance array spanning several nose radii
    y = np.linspace(0.0, 3.0 * r_nose, n_pts)
    x = shock_shape_billig(mach, gamma, r_nose, y)
    return x, y
