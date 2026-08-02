"""Compute cf/ch skin-friction estimates from x and re1 inputs."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
from flow_state.transport import TransportModel

from .cf_laminar import LAMINAR_METHODS, cf_laminar
from .cf_turbulent import TURBULENT_METHODS, cf_turbulent
from .wall_temperature import estimate_adiabatic_wall_temperature

# --------------------------------------------------
# constants
# --------------------------------------------------
VALID_MODES = ("laminar", "turbulent")


# --------------------------------------------------
# public API
# --------------------------------------------------
def compute_cf_ch(
    x: float | np.ndarray,
    re1: float,
    mach: float,
    temp_edge: float,
    temp_wall: float | None,
    wall_type: str,
    mode: str | None = None,
    method: str | None = None,
    gamma: float = 1.4,
    pr: float = 0.72,
    visc_model: TransportModel | None = None,
) -> dict[str, object]:
    """Compute cf/ch at one x location or a 1D x array.

    - If method is provided with one mode: computes that method only.
    - If method is omitted: computes every method in the selected mode(s).
    - If neither mode nor method is provided: computes all methods in both modes.

    Args:
        x: Streamwise station [m], as a scalar or 1D array.
        re1: Unit Reynolds number [1/m].
        mach: Edge Mach number.
        temp_edge: Edge temperature [K].
        temp_wall: Isothermal wall temperature [K]. Ignored for an adiabatic
            wall.
        wall_type: Wall boundary condition, ``"adiabatic"`` or ``"isothermal"``.
        mode: "laminar", "turbulent", or None.
        method: Skin-friction method when running a single method, as a string.
        gamma: Specific heat ratio.
        pr: Prandtl number.
        visc_model: Optional flow-state transport model.

    Returns:
        ``{"x", "re_x", "modes", "method_names", "cf", "ch", "temp_wall", "wall_type"}``

        ``modes`` is always a list of selected mode names.
        ``method_names`` is always a ``mode -> [method_name, ...]`` map.
        ``cf`` and ``ch`` are always nested ``mode -> method -> values`` maps.
        ``temp_wall`` is always a ``mode -> temperature`` map.

        Result values are always one-dimensional NumPy arrays. Scalar ``x``
        input produces arrays with shape ``(1,)``.
    """

    # --------------------------------------------------
    # validate mode selection
    # --------------------------------------------------
    if mode is None:
        mode_names = list(VALID_MODES)
    else:
        if mode not in VALID_MODES:
            raise ValueError(f"mode must be one of {VALID_MODES}: got {mode!r}")
        mode_names = [mode]

    # --------------------------------------------------
    # reject ambiguous partial selection across both modes
    # --------------------------------------------------
    if len(mode_names) > 1 and method is not None:
        raise ValueError("method cannot be set when mode is None")

    # --------------------------------------------------
    # validate wall inputs needed to resolve the mode-specific temperature
    # --------------------------------------------------
    if wall_type not in ("adiabatic", "isothermal"):
        raise ValueError("wall_type must be 'adiabatic' or 'isothermal'")
    if wall_type == "isothermal" and temp_wall is None:
        raise ValueError("temp_wall is required when wall_type='isothermal'")

    # --------------------------------------------------
    # convert x to array even when a scalar is provided
    # --------------------------------------------------
    x_array = np.asarray(x, dtype=float)

    if x_array.ndim == 0:
        x_values = x_array.reshape(1)
    elif x_array.ndim == 1:
        x_values = x_array
    else:
        raise ValueError("x must be a scalar or a 1D array")

    # --------------------------------------------------
    # compute re_x from x and re1
    # --------------------------------------------------
    re_x_values = x_values * float(re1)

    # --------------------------------------------------
    # choose methods per mode
    # --------------------------------------------------
    method_names_by_mode: dict[str, list[str]] = {}
    for mode_name in mode_names:
        use_all = method is None or len(mode_names) > 1
        if use_all:
            if mode_name == "laminar":
                method_names_by_mode[mode_name] = list(LAMINAR_METHODS)
            else:
                method_names_by_mode[mode_name] = list(TURBULENT_METHODS)
        else:
            assert method is not None
            method_names_by_mode[mode_name] = [method]

    # --------------------------------------------------
    # evaluate each selected mode and method over the full x array
    # --------------------------------------------------
    cf_mode_method_arrays: dict[str, dict[str, np.ndarray]] = {}
    temp_wall_by_mode: dict[str, float] = {}
    for mode_name in mode_names:
        # resolve the wall temperature for this boundary-layer mode
        if wall_type == "isothermal":
            mode_temp_wall = float(temp_wall)
        else:
            mode_temp_wall = estimate_adiabatic_wall_temperature(
                temp_edge=temp_edge,
                mach=mach,
                gamma=gamma,
                pr=pr,
                mode=mode_name,
            )

        temp_wall_by_mode[mode_name] = mode_temp_wall

        method_arrays: dict[str, np.ndarray] = {}
        for method_name in method_names_by_mode[mode_name]:
            if mode_name == "laminar":
                method_arrays[method_name] = cf_laminar(
                    x_values,
                    re1,
                    mach,
                    temp_edge,
                    mode_temp_wall,
                    wall_type,
                    gamma=gamma,
                    pr=pr,
                    method=method_name,
                    visc_model=visc_model,
                )
            else:
                method_arrays[method_name] = cf_turbulent(
                    x_values,
                    re1,
                    mach,
                    temp_edge,
                    mode_temp_wall,
                    wall_type,
                    gamma=gamma,
                    pr=pr,
                    method=method_name,
                    visc_model=visc_model,
                )

        cf_mode_method_arrays[mode_name] = method_arrays

    # derive Ch from cf via Reynolds analogy
    ch_mode_method_arrays = {}
    for mode_name in mode_names:
        ch_mode_method_arrays[mode_name] = {
            method_name: values / (2.0 * pr ** (2.0 / 3.0))
            for method_name, values in cf_mode_method_arrays[mode_name].items()
        }

    # --------------------------------------------------
    # build the result dictionary
    # --------------------------------------------------
    result_dict = {
        "x": x_values,
        "re_x": re_x_values,
        "modes": mode_names,
        "method_names": method_names_by_mode,
        "cf": cf_mode_method_arrays,
        "ch": ch_mode_method_arrays,
        "temp_wall": temp_wall_by_mode,
        "wall_type": wall_type,
    }

    # return the computed skin-friction and heat-transfer results
    return result_dict
