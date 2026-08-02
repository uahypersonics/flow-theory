"""Laminar skin-friction estimates for compressible flat plates."""

# --------------------------------------------------
# References:
#
# Blasius, H. (1908), "Grenzschichten in Flussigkeiten mit kleiner
# Reibung," Zeitschrift fur Mathematik und Physik, Vol. 56, pp. 1-37.
# Incompressible laminar flat-plate relation.
#
# Eckert, E. R. G. (1955), "Engineering relations for heat transfer and
# friction in high-velocity laminar and turbulent boundary-layer flow over
# surfaces with constant pressure and temperature," Transactions of the
# ASME, Vol. 78, pp. 1273-1283. Reference-temperature method.
#
# Falkner, V. M. and Skan, S. W. (1931), "Solutions of the boundary-layer
# equations," Philosophical Magazine, Vol. 12, No. 80, pp. 865-896.
# Falkner-Skan similarity formulation.
# --------------------------------------------------

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from flow_state.transport import get_transport_model
from simbl import SimilarityInputs, SolverOptions, solve_similarity

from .validate_cf_ch_inputs import validate_cf_ch_inputs

if TYPE_CHECKING:
    from flow_state.transport import TransportModel

# --------------------------------------------------
# registered laminar methods
# --------------------------------------------------
LAMINAR_METHODS = (
    "blasius",
    "eckert_reference",
    "similarity",
)

# --------------------------------------------------
# laminar skin-friction estimate: blasius
# --------------------------------------------------
def _cf_laminar_blasius(re_x: np.ndarray) -> np.ndarray:
    """Incompressible Blasius laminar flat-plate estimate."""

    return 0.664 / re_x**0.5

# --------------------------------------------------
# laminar skin-friction estimate: eckert reference temperature
# --------------------------------------------------
def _cf_laminar_eckert_reference(
    re_x: np.ndarray,
    mach: float,
    temp_edge: float,
    temp_wall: float,
    visc_model: TransportModel,
) -> np.ndarray:
    """Eckert reference-temperature laminar estimate."""

    t_star_te = 0.5 + 0.039 * mach**2 + 0.5 * (temp_wall / temp_edge)
    t_star = t_star_te * temp_edge

    rho_star_rho_e = temp_edge / t_star
    mu_e_mu_star = visc_model.mu(temp_edge) / visc_model.mu(t_star)
    re_star = re_x * rho_star_rho_e * mu_e_mu_star

    return 0.664 / re_star**0.5

# --------------------------------------------------
# laminar skin-friction estimate: similarity solution
# --------------------------------------------------
def _cf_laminar_similarity(
    re_x: np.ndarray,
    mach: float,
    temp_edge: float,
    temp_wall: float,
    wall_type: str,
    gamma: float,
    pr: float,
    visc_model: TransportModel,
) -> np.ndarray:
    """Laminar skin friction from a Falkner-Skan similarity solve."""

    # pass wall temperature only for an isothermal boundary condition
    simbl_temp_wall = temp_wall if wall_type == "isothermal" else None

    # build the flat-plate similarity problem
    inputs = SimilarityInputs(
        mach_edge=mach,
        temp_edge=temp_edge,
        wall_bc=wall_type,
        temp_wall=simbl_temp_wall,
        prandtl=pr,
        gamma=gamma,
        beta=0.0,
        sweep_angle=0.0,
    )
    options = SolverOptions(bvp_fallback=True)

    # solve the similarity profile once for all streamwise stations
    solution, result = solve_similarity(inputs, options, visc_model=visc_model)
    if not result.converged:
        raise RuntimeError("simbl similarity solve did not converge")

    fpp_wall = float(solution.fpp[0])

    # use the wall temperature solved by simbl for an adiabatic wall
    if wall_type == "adiabatic":
        temp_wall_similarity = temp_edge * float(solution.tau[0])
    else:
        temp_wall_similarity = temp_wall

    # build wall-to-edge property ratio from the similarity derivation
    rho_w_rho_e = temp_edge / temp_wall_similarity
    mu_w_mu_e = visc_model.mu(temp_wall_similarity) / visc_model.mu(temp_edge)
    wall_edge_ratio = rho_w_rho_e * mu_w_mu_e

    # simbl returns f''(0) for the normalized velocity f' = u / u_e.
    # Converting back to engineering local skin friction keeps the explicit
    # wall-to-edge property ratio from the Levy-Lees similarity derivation.
    return (2.0**0.5) * wall_edge_ratio * fpp_wall / re_x**0.5

# --------------------------------------------------
# public API: laminar skin-friction coefficient estimate computation
# --------------------------------------------------
def cf_laminar(
    x: float | np.ndarray,
    re1: float,
    mach: float,
    temp_edge: float,
    temp_wall: float,
    wall_type: str,
    gamma: float = 1.4,
    pr: float = 0.72,
    method: str = "blasius",
    visc_model: TransportModel | None = None,
) -> float | np.ndarray:
    """Compute laminar flat-plate skin friction coefficient

    Args:
        x: Streamwise station [m], as a scalar or one-dimensional array.
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        temp_edge: Edge temperature [K].
        temp_wall: Wall temperature [K].
        wall_type: Wall boundary condition, ``"adiabatic"`` or ``"isothermal"``.
        gamma: Specific heat ratio.
        pr: Prandtl number.
        method: Laminar skin-friction method.
        visc_model: Optional flow-state transport model.

    Returns:
        Local laminar skin-friction coefficient as a float for scalar x input,
        or as an array with the same shape as array x input.

    Raises:
        ValueError: If x is not a scalar or one-dimensional array, or if an
            option is not supported.
    """

    # --------------------------------------------------
    # validate inputs, raise error on common mistakes
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
        # x is scalar -> reshape to one-dimensional array
        scalar_input = True
        x_values = x_array.reshape(1)
    elif x_array.ndim == 1:
        # x is already a one-dimensional array
        scalar_input = False
        x_values = x_array
    else:
        # x is not a scalar or one-dimensional array -> raise an error
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
    # validate the selected laminar correlation
    # --------------------------------------------------
    if method not in LAMINAR_METHODS:
        raise ValueError(f"method must be one of {LAMINAR_METHODS}: got {method!r}")

    # --------------------------------------------------
    # dispatch to the selected laminar skin-friction method
    # --------------------------------------------------
    if method == "blasius":
        cf = _cf_laminar_blasius(re_x)
    elif method == "eckert_reference":
        cf = _cf_laminar_eckert_reference(re_x, mach, temp_edge, temp_wall, visc_model)
    elif method == "similarity":
        cf = _cf_laminar_similarity(
            re_x,
            mach,
            temp_edge,
            temp_wall,
            wall_type,
            gamma,
            pr,
            visc_model,
        )

    # --------------------------------------------------
    # preserve scalar or array behavior from the x input
    # --------------------------------------------------
    if scalar_input:
        cf_out = float(cf[0])
    else:
        cf_out = cf

    # return skin-friction coefficient
    return cf_out
