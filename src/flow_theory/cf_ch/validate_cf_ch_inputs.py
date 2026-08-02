"""Shared physical-input validation for skin-friction and Stanton estimates."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math

import numpy as np


# --------------------------------------------------
# public API: shared cf/ch input validation
# --------------------------------------------------
def validate_cf_ch_inputs(
    x: float | np.ndarray,
    re1: float,
    mach: float,
    temp_edge: float,
    temp_wall: float,
    wall_type: str,
    gamma: float,
    pr: float,
) -> None:
    """Validate physical inputs shared by the cf/ch correlations.

    Args:
        x: Streamwise station [m], as a scalar or one-dimensional array.
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        temp_edge: Edge temperature [K].
        temp_wall: Wall temperature [K].
        wall_type: Wall boundary condition, ``"adiabatic"`` or ``"isothermal"``.
        gamma: Specific heat ratio.
        pr: Prandtl number.

    Raises:
        ValueError: If an input is nonphysical, nonfinite, or has an unsupported
            shape or value.
    """

    # validate the streamwise station shape and values
    x_array = np.asarray(x, dtype=float)
    if x_array.ndim > 1:
        raise ValueError("x must be a scalar or one-dimensional array")
    if x_array.size == 0:
        raise ValueError("x must contain at least one streamwise station")
    if not np.all(np.isfinite(x_array)):
        raise ValueError("x must contain only finite values")
    if np.any(x_array <= 0.0):
        raise ValueError("x must contain only positive values")

    # validate the unit Reynolds number
    if not math.isfinite(re1) or re1 <= 0.0:
        raise ValueError(f"re1 must be finite and positive: {re1}")

    # validate the edge Mach number
    if not math.isfinite(mach) or mach < 0.0:
        raise ValueError(f"mach must be finite and nonnegative: {mach}")

    # validate the edge and wall temperatures
    if not math.isfinite(temp_edge) or temp_edge <= 0.0:
        raise ValueError(f"temp_edge must be finite and positive: {temp_edge}")
    if not math.isfinite(temp_wall) or temp_wall <= 0.0:
        raise ValueError(f"temp_wall must be finite and positive: {temp_wall}")

    # validate the wall boundary condition
    if wall_type not in ("adiabatic", "isothermal"):
        raise ValueError("wall_type must be 'adiabatic' or 'isothermal'")

    # validate the gas-property parameters
    if not math.isfinite(gamma) or gamma <= 1.0:
        raise ValueError(f"gamma must be finite and greater than 1: {gamma}")
    if not math.isfinite(pr) or pr <= 0.0:
        raise ValueError(f"pr must be finite and positive: {pr}")
