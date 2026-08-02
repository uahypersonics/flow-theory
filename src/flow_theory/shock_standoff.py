"""Empirical bow-shock standoff distance for blunt hypersonic bodies

Provides the Billig (1967) correlation for the normal-shock standoff distance
ahead of a spherically-blunted nose, and an engineering extension to
sphere-cone noses.  This is an empirical curve fit to shock-shape data -- the
exact inviscid standoff (from Rankine-Hugoniot + Taylor-Maccoll) belongs in
`gasdyn`, not here.

Design
------
Billig's correlation was fit to air (gamma=1.4) data.  To generalize to other
gamma, the leading coefficient is rescaled by the ratio of the mach -> inf
normal-shock density ratio for the given gamma to that of air, so the sphere
formula recovers Billig's published fit exactly at gamma=1.4 and preserves
the correct physical trend (standoff scales with the shock density ratio)
for other gamma.

The cone-angle extension for `standoff_blunt_cone` is an approximation, not a
literal digitized Billig table: the stagnation-region standoff distance is
governed mainly by the local subsonic pocket behind the normal shock near the
stagnation streamline, which is only weakly sensitive to the downstream body
shape.  A sin(half_angle) scaling captures the two known limits: a very
blunt "cone" (half_angle -> 90 deg, i.e. a flat-faced/disk-like body)
recovers the full sphere standoff, while a slender cone (half_angle -> 0)
shrinks the standoff toward zero as the bow shock approaches attachment.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np

# --------------------------------------------------
# module constants
# --------------------------------------------------

# Billig (1967) sphere correlation constants, fit for air (gamma=1.4)
_BILLIG_SPHERE_DELTA_COEFF = 0.143
_BILLIG_SPHERE_DELTA_EXP = 3.24
_GAMMA_AIR = 1.4


# --------------------------------------------------
# public API
# --------------------------------------------------
def standoff_sphere(mach: float, gamma: float = 1.4) -> float:
    """Normal shock standoff distance on a sphere (Billig 1967).

    Returns Delta/r_nose (non-dimensional).

    Args:
        mach: Freestream Mach number.
        gamma: Specific heat ratio.

    Returns:
        Delta/r_nose: Non-dimensional standoff distance.

    References:
        Billig (1967), "Shock-wave shapes around spherical- and cylindrical-nosed
        bodies", J. Spacecraft Rockets, 4(6), 822-823.
    """

    # compute Billig's air-fit standoff correlation
    delta_R_air = _BILLIG_SPHERE_DELTA_COEFF * np.exp(_BILLIG_SPHERE_DELTA_EXP / mach**2)

    # rescale by the ratio of normal-shock density ratios (mach -> inf limit)
    # to generalize the air-only fit to arbitrary gamma
    epsilon = (gamma - 1.0) / (gamma + 1.0)
    epsilon_air = (_GAMMA_AIR - 1.0) / (_GAMMA_AIR + 1.0)
    return delta_R_air * (epsilon / epsilon_air)


def standoff_blunt_cone(
    mach: float, gamma: float, half_angle_deg: float, r_nose: float
) -> float:
    """Standoff distance on a sphere-cone nose.

    Approximates the sphere-cone stagnation-region standoff distance as the
    sphere value scaled by sin(half_angle), reflecting that a very blunt
    (near-flat-faced) cone recovers the full sphere standoff while a slender
    cone shrinks the standoff toward zero.  See module docstring for the
    justification of this extension.

    Args:
        mach: Freestream Mach number.
        gamma: Specific heat ratio.
        half_angle_deg: Cone half-angle [deg].
        r_nose: Nose radius.

    Returns:
        Delta [same units as r_nose].

    References:
        Billig (1967), "Shock-wave shapes around spherical- and cylindrical-nosed
        bodies", J. Spacecraft Rockets, 4(6), 822-823.
    """

    # validate half-angle range
    if not 0.0 < half_angle_deg <= 90.0:
        raise ValueError(f"half_angle_deg must be in (0, 90]: got {half_angle_deg}")

    # compute non-dimensional sphere standoff, then apply cone-angle scaling
    delta_R_sphere = standoff_sphere(mach, gamma=gamma)
    half_angle_rad = np.deg2rad(half_angle_deg)
    delta_R_cone = delta_R_sphere * np.sin(half_angle_rad)

    # return dimensional standoff distance
    return delta_R_cone * r_nose
