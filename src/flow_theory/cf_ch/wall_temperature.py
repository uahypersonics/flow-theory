"""Wall-temperature estimates for compressible flat plates."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations


# --------------------------------------------------
# public API
# --------------------------------------------------
def estimate_adiabatic_wall_temperature(
    temp_edge: float,
    mach: float,
    gamma: float,
    pr: float,
    mode: str,
) -> float:
    """Estimate adiabatic wall temperature from the recovery relation.

    Args:
        temp_edge: Edge temperature [K].
        mach: Edge Mach number.
        gamma: Specific heat ratio.
        pr: Prandtl number.
        mode: Boundary-layer mode, either ``"laminar"`` or ``"turbulent"``.

    Returns:
        Estimated adiabatic wall temperature [K].

    Raises:
        ValueError: If mode is not ``"laminar"`` or ``"turbulent"``.
    """

    # estimate the recovery factor for the selected boundary-layer mode
    if mode == "laminar":
        recovery_factor = pr**0.5
    elif mode == "turbulent":
        recovery_factor = pr ** (1.0 / 3.0)
    else:
        raise ValueError("mode must be 'laminar' or 'turbulent'")

    # estimate adiabatic wall temperature from the recovery relation
    temperature_ratio = 1.0 + recovery_factor * 0.5 * (gamma - 1.0) * mach**2
    temp_wall = temp_edge * temperature_ratio

    return temp_wall
