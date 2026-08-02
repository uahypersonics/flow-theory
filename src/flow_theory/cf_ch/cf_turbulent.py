"""Turbulent skin-friction estimates for compressible flat plates."""

# --------------------------------------------------
# References:
#
# Schoenherr, K. E. (1932), "Resistance of flat surfaces moving through a
# fluid," Transactions of the Society of Naval Architects and Marine
# Engineers, Vol. 40, pp. 279-313. Average incompressible relation.
#
# Van Driest, E. R. (1951), "Turbulent boundary layer in compressible
# fluids," Journal of the Aeronautical Sciences, Vol. 18, No. 3,
# pp. 145-160. Van Driest II compressibility transformation.
#
# Spalding, D. B. and Chi, S. W. (1964), "The drag of a compressible
# turbulent boundary layer on a smooth flat plate with and without heat
# transfer," Journal of Fluid Mechanics. Spalding-Chi transformation.
#
# Sommer, S. C. and Short, B. J. (1955), "Free-flight measurements of
# turbulent boundary-layer skin friction in the presence of severe
# aerodynamic heating at Mach numbers from 2.8 to 7.0," NACA TN 3391.
# Sommer-Short reference-temperature transformation.
#
# Hopkins, E. J. and Inouye, M. (1971), "An evaluation of theories for
# predicting turbulent skin friction and heat transfer on flat plates at
# supersonic and hypersonic Mach numbers," NASA TN D-6353. Transformation
# summaries and average-to-local skin-friction conversion.
#
# White, F. M. and Christoph, G. H. (1972), "A simple new analysis of the
# turbulent compressible boundary layer," AIAA Paper 70-164.
# White-Christoph transformation.
# --------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from flow_state.transport import get_transport_model
from scipy.optimize import brentq

from .validate_cf_ch_inputs import validate_cf_ch_inputs

if TYPE_CHECKING:
    from flow_state.transport import TransportModel

# --------------------------------------------------
# registered turbulent methods
# --------------------------------------------------
TURBULENT_METHODS = (
    "van_driest_ii",
    "spalding_chi",
    "sommer_short",
    "white_christoph",
)


# --------------------------------------------------
# turbulent compressibility transformation factors
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class TransformFactors:
    """Compressibility transformation factors evaluated at each station."""

    f_c: np.ndarray
    f_theta: np.ndarray
    f_x: np.ndarray

# --------------------------------------------------
# turbulent skin-friction estimate: incompressible Karman-Schoenherr
# note: this is an average skin-friction coefficient, not a local coefficient
# --------------------------------------------------
def _cf_inc_ave_karman_schoenherr(rex_inc: np.ndarray) -> np.ndarray:
    """Evaluate the averaged incompressible skin-friction relation for a flat plate according to Karman & Schoenherr."""

    # allocate one average skin-friction coefficient per Reynolds number
    cf_inc_ave = np.empty_like(rex_inc, dtype=float)

    # solve the implicit Karman-Schoenherr relation at each Reynolds number
    for idx, rex in np.ndenumerate(rex_inc):
        # define residual function for the implicit Karman-Schoenherr relation
        def residual(cf_value: float) -> float:

            # compute the left-hand side and right-hand side
            lhs = 0.242 / np.sqrt(cf_value)
            # comptue the right-hand side as log10(re_x * cf_value)
            rhs = np.log10(rex * cf_value)

            # residual is the difference between the left-hand side and right-hand side
            res = lhs - rhs

            # return residual
            return res

        # define search bounds for the root-finding method
        cf_inc_ave_lo = 1.0e-12
        cf_inc_ave_hi = 1.0

        # solve for the average skin-friction coefficient using a root-finding method (here brentq)
        cf_inc_ave[idx] = brentq(residual, cf_inc_ave_lo, cf_inc_ave_hi)

    # return the array of average skin-friction coefficients
    return np.asarray(cf_inc_ave, dtype=float)

# --------------------------------------------------
# turbulent compressibility transform: van Driest II
# --------------------------------------------------
def _van_driest_ii_transform_factors(
    re_x: np.ndarray,
    mach: float,
    temp_wall: float,
    temp_edge: float,
    gamma: float,
    pr: float,
    visc_model: TransportModel,
) -> TransformFactors:
    """Return van Driest II compressibility transformation factors."""

    # return the exact incompressible limit before evaluating the singular transform
    if mach == 0.0:
        ones = np.ones_like(re_x, dtype=float)
        return TransformFactors(f_c=ones, f_theta=ones, f_x=ones)

    # compute the transformation inputs from the physical flow conditions
    m = 0.5 * (gamma - 1.0) * mach**2
    r = pr ** (1.0 / 3.0)
    cap_f = temp_wall / temp_edge

    a = np.sqrt(m * r / cap_f)
    b = (1.0 + r * m - cap_f) / cap_f
    denom = np.sqrt(4.0 * a**2 + b**2)
    alpha = np.clip((2.0 * a**2 - b) / denom, -1.0, 1.0)
    beta = np.clip(b / denom, -1.0, 1.0)

    f_c = r * m / (np.arcsin(alpha) + np.arcsin(beta)) ** 2
    f_theta = visc_model.mu(temp_edge) / visc_model.mu(temp_wall)
    f_x = f_theta / f_c

    factors = TransformFactors(
        f_c=np.full_like(re_x, f_c, dtype=float),
        f_theta=np.full_like(re_x, f_theta, dtype=float),
        f_x=np.full_like(re_x, f_x, dtype=float),
    )

    return factors

# --------------------------------------------------
# turbulent compressibility transform: Spalding-Chi
# --------------------------------------------------
def _spalding_chi_transform_factors(
    re_x: np.ndarray,
    mach: float,
    temp_wall: float,
    temp_edge: float,
    gamma: float,
    pr: float,
) -> TransformFactors:
    """Return Spalding-Chi compressibility transformation factors."""

    # return the exact incompressible limit before evaluating the singular transform
    if mach == 0.0:
        ones = np.ones_like(re_x, dtype=float)
        return TransformFactors(f_c=ones, f_theta=ones, f_x=ones)

    # compute the transformation inputs from the physical flow conditions
    m = 0.5 * (gamma - 1.0) * mach**2
    r = pr ** (1.0 / 3.0)
    cap_f = temp_wall / temp_edge

    taw_te = 1.0 + r * m
    cap_f_aw = cap_f / taw_te

    a = np.sqrt(m * r / cap_f)
    b = (1.0 + r * m - cap_f) / cap_f
    denom = np.sqrt(4.0 * a**2 + b**2)
    alpha = np.clip((2.0 * a**2 - b) / denom, -1.0, 1.0)
    beta = np.clip(b / denom, -1.0, 1.0)

    f_c = r * m / (np.arcsin(alpha) + np.arcsin(beta)) ** 2
    f_theta = 1.0 / (cap_f**0.702 * cap_f_aw**0.772)
    f_x = f_theta / f_c

    factors = TransformFactors(
        f_c=np.full_like(re_x, f_c, dtype=float),
        f_theta=np.full_like(re_x, f_theta, dtype=float),
        f_x=np.full_like(re_x, f_x, dtype=float),
    )

    return factors

# --------------------------------------------------
# turbulent compressibility transform: Sommer-Short
# --------------------------------------------------
def _sommer_short_transform_factors(
    re_x: np.ndarray,
    mach: float,
    temp_wall: float,
    temp_edge: float,
    gamma: float,
    pr: float,
    visc_model: TransportModel,
) -> TransformFactors:
    """Return Sommer-Short compressibility transformation factors."""

    # mark shared interface parameters that are not used by this method
    del gamma, pr

    # return the exact incompressible limit
    if mach == 0.0:
        ones = np.ones_like(re_x, dtype=float)
        return TransformFactors(f_c=ones, f_theta=ones, f_x=ones)

    # compute the empirical Sommer-Short reference temperature
    wall_edge_temp_ratio = temp_wall / temp_edge
    reference_temp_ratio = 1.0 + 0.035 * mach**2 + 0.45 * (wall_edge_temp_ratio - 1.0)
    reference_temp = reference_temp_ratio * temp_edge

    # compute the compressibility transformation factors
    f_c = reference_temp_ratio
    f_theta = visc_model.mu(temp_edge) / visc_model.mu(reference_temp)
    f_x = f_theta / f_c

    factors = TransformFactors(
        f_c=np.full_like(re_x, f_c, dtype=float),
        f_theta=np.full_like(re_x, f_theta, dtype=float),
        f_x=np.full_like(re_x, f_x, dtype=float),
    )

    return factors

# --------------------------------------------------
# turbulent compressibility transform: White-Christoph
# --------------------------------------------------
def _white_christoph_transform_factors(
    re_x: np.ndarray,
    mach: float,
    temp_wall: float,
    temp_edge: float,
    gamma: float,
    pr: float,
    visc_model: TransportModel,
) -> TransformFactors:
    """Return White-Christoph compressibility transformation factors."""

    # return the exact incompressible limit before evaluating the singular transform
    if mach == 0.0:
        ones = np.ones_like(re_x, dtype=float)
        return TransformFactors(f_c=ones, f_theta=ones, f_x=ones)

    # compute the transformation inputs from the physical flow conditions
    m = 0.5 * (gamma - 1.0) * mach**2
    r = pr ** (1.0 / 3.0)
    cap_f = temp_wall / temp_edge

    taw_te = 1.0 + r * m
    cap_f_aw = cap_f / taw_te

    a = np.sqrt(m / cap_f)
    b = (1.0 - cap_f_aw) / cap_f_aw
    denom = np.sqrt(4.0 * a**2 + b**2)
    alpha = np.clip((2.0 * a**2 - b) / denom, -1.0, 1.0)
    beta = np.clip(b / denom, -1.0, 1.0)

    cap_s = np.sqrt(cap_f / cap_f_aw - 1.0) / (np.arcsin(alpha) + np.arcsin(beta))
    f_c = cap_s**2
    viscosity_ratio = visc_model.mu(temp_edge) / visc_model.mu(temp_wall)
    f_x = viscosity_ratio * np.sqrt(1.0 / cap_f) / cap_s
    f_theta = f_x * f_c

    factors = TransformFactors(
        f_c=np.full_like(re_x, f_c, dtype=float),
        f_theta=np.full_like(re_x, f_theta, dtype=float),
        f_x=np.full_like(re_x, f_x, dtype=float),
    )

    return factors

# --------------------------------------------------
# turbulent compressibility transform dispatcher
# --------------------------------------------------
def _compressible_transform_factors(
    re_x: np.ndarray,
    mach: float,
    temp_wall: float,
    temp_edge: float,
    gamma: float,
    pr: float,
    method: str,
    visc_model: TransportModel,
) -> TransformFactors:
    """Return compressible-to-incompressible transform factors."""

    if method == "van_driest_ii":
        factors = _van_driest_ii_transform_factors(
            re_x,
            mach,
            temp_wall,
            temp_edge,
            gamma,
            pr,
            visc_model,
        )
    elif method == "spalding_chi":
        factors = _spalding_chi_transform_factors(
            re_x,
            mach,
            temp_wall,
            temp_edge,
            gamma,
            pr,
        )
    elif method == "sommer_short":
        factors = _sommer_short_transform_factors(
            re_x,
            mach,
            temp_wall,
            temp_edge,
            gamma,
            pr,
            visc_model,
        )
    elif method == "white_christoph":
        factors = _white_christoph_transform_factors(
            re_x,
            mach,
            temp_wall,
            temp_edge,
            gamma,
            pr,
            visc_model,
        )
    else:
        raise ValueError(f"Unknown turbulent method: {method!r}")

    return factors


# --------------------------------------------------
# public API: turbulent skin-friction coefficient estimate computation
# --------------------------------------------------
def cf_turbulent(
    x: float | np.ndarray,
    re1: float,
    mach: float,
    temp_edge: float,
    temp_wall: float,
    wall_type: str,
    gamma: float = 1.4,
    pr: float = 0.72,
    method: str = "white_christoph",
    visc_model: TransportModel | None = None,
) -> float | np.ndarray:
    """Compute turbulent flat-plate skin friction.

    Args:
        x: Streamwise station [m], as a scalar or one-dimensional array.
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        temp_edge: Edge temperature [K].
        temp_wall: Wall temperature [K].
        wall_type: Wall boundary condition, ``"adiabatic"`` or ``"isothermal"``.
        gamma: Specific heat ratio.
        pr: Prandtl number.
        method: Turbulent skin-friction method.
        visc_model: Optional flow-state transport model.

    Returns:
        Local turbulent skin-friction coefficient as a float for scalar x input,
        or as an array with the same shape as array x input.

    Raises:
        ValueError: If x is not a scalar or one-dimensional array, or if an
            option is not supported.
    """

    # --------------------------------------------------
    # validate physical inputs, raise error on common mistakes
    # --------------------------------------------------
    validate_cf_ch_inputs(
        x,
        re1,
        mach,
        temp_edge,
        temp_wall,
        wall_type,
        gamma,
        pr,
    )

    # --------------------------------------------------
    # check if x is a scalar or one-dimensional array
    # --------------------------------------------------
    x_array = np.asarray(x, dtype=float)
    if x_array.ndim == 0:
        scalar_input = True
        x_values = x_array.reshape(1)
    elif x_array.ndim == 1:
        scalar_input = False
        x_values = x_array
    else:
        raise ValueError("x must be a scalar or one-dimensional array")

    # --------------------------------------------------
    # ensure a transport model is available for the viscosity calculation
    # --------------------------------------------------
    if visc_model is None:
        visc_model = get_transport_model("sutherland")

    # --------------------------------------------------
    # compute re_x from x and re1
    # --------------------------------------------------
    re_x = x_values * re1

    # --------------------------------------------------
    # validate the selected turbulent correlation
    # --------------------------------------------------
    if method not in TURBULENT_METHODS:
        raise ValueError(f"method must be one of {TURBULENT_METHODS}: got {method!r}")

    # --------------------------------------------------
    # compute the compressible transformation factors
    # --------------------------------------------------
    factors = _compressible_transform_factors(
        re_x,
        mach,
        temp_wall,
        temp_edge,
        gamma,
        pr,
        method,
        visc_model,
    )

    # --------------------------------------------------
    # convert the reynolds number to the incompressible equivalent using the transformation factor f_x
    # --------------------------------------------------
    re_x_inc = factors.f_x * re_x

    # --------------------------------------------------
    # compute the incompressible average Karman-Schoenherr skin-friction coefficient
    # --------------------------------------------------
    cf_inc_ave = _cf_inc_ave_karman_schoenherr(re_x_inc)

    # --------------------------------------------------
    # convert the average Karman-Schoenherr coefficient to local skin friction according to Hopkins & Inouye 1971
    # --------------------------------------------------
    num = 0.242 * cf_inc_ave
    den = 0.242 + 0.8686 * np.sqrt(cf_inc_ave)
    cf_local_inc = num / den

    # --------------------------------------------------
    # convert the incompressible local skin-friction coefficient to the compressible local skin-friction coefficient using the transformation factor f_c
    # --------------------------------------------------
    cf = np.asarray(cf_local_inc / factors.f_c, dtype=float)

    # --------------------------------------------------
    # preserve scalar or array behavior from the x input
    # --------------------------------------------------
    if scalar_input:
        cf_out = float(cf[0])
    else:
        cf_out = cf

    # return skin-friction coefficient
    return cf_out
