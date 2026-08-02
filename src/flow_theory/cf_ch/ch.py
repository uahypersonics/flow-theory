"""Analytical and empirical Stanton number estimates for compressible flat plates.

Provides laminar and turbulent heat transfer coefficient (Ch) correlations via
the Reynolds analogy applied to the skin friction correlations in
flow_theory.cf_ch.

    Ch = cf / (2 * pr^(2/3))

This relation holds for both laminar and turbulent flows over smooth flat
plates in the absence of pressure gradients (Prandtl-Taylor analogy).
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .cf_laminar import cf_laminar
from .cf_turbulent import cf_turbulent

if TYPE_CHECKING:
    from flow_state.transport import TransportModel


# --------------------------------------------------
# public API
# --------------------------------------------------


def ch_laminar(
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
    """Laminar flat-plate Stanton number from the selected skin-friction method.

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
        visc_model: Viscosity model from flow-state. Defaults to Sutherland
            air. See flow_theory.cf_ch.cf_laminar.

    Returns:
        Stanton number Ch as a float for scalar x input, or as an array with
        the same shape as array x input.

    References:
        Eckert (1955), "Engineering relations for heat transfer and friction in
        high-velocity laminar and turbulent boundary-layer flow over surfaces
        with constant pressure and temperature", Trans. ASME, 78, 1273-1283.
    """

    # compute laminar cf, then apply Reynolds analogy: Ch = cf / (2*pr^(2/3))
    cf = cf_laminar(
        x,
        re1,
        mach,
        temp_edge,
        temp_wall,
        wall_type,
        gamma=gamma,
        pr=pr,
        method=method,
        visc_model=visc_model,
    )
    ch = cf / (2.0 * pr ** (2.0 / 3.0))
    return ch


def ch_turbulent(
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
    """Turbulent flat-plate Stanton number (van Driest II or White-Christoph + Reynolds analogy).

    Args:
        x: Streamwise station [m], as a scalar or one-dimensional array.
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        temp_edge: Edge temperature [K].
        temp_wall: Wall temperature [K].
        wall_type: Wall boundary condition, ``"adiabatic"`` or ``"isothermal"``.
        gamma: Specific heat ratio.
        pr: Prandtl number.
        method: "white_christoph" (default) or "van_driest_ii".
        visc_model: Viscosity model from flow-state.  See cf_laminar.

    Returns:
        Stanton number Ch as a float for scalar x input, or as an array with
        the same shape as array x input.

    References:
        Van Driest, E.R. (1951), "Turbulent boundary layer in compressible
        fluids", Journal of the Aeronautical Sciences, 18(3), 145-160.
        White, F.M., Christoph, G.H. (1972), "A simple new analysis of the
        turbulent compressible boundary layer", AIAA Paper 70-164.
    """

    # compute turbulent cf, then apply Reynolds analogy: Ch = cf / (2*pr^(2/3))
    cf = cf_turbulent(
        x,
        re1,
        mach,
        temp_edge,
        temp_wall,
        wall_type,
        gamma=gamma,
        pr=pr,
        method=method,
        visc_model=visc_model,
    )
    ch = cf / (2.0 * pr ** (2.0 / 3.0))
    return ch
