"""Laminar flat-plate boundary-layer thickness correlations."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

# --------------------------------------------------
# supported methods
# --------------------------------------------------
BOUNDARY_LAYER_THICKNESS_METHODS = (
    "blasius",
    "eckert_reference",
)


# --------------------------------------------------
# result structure
# --------------------------------------------------
@dataclass(slots=True, frozen=True)
class BoundaryLayerThicknessResult:
    """Boundary-layer thickness estimates at one streamwise station."""

    x: float
    re_x: float
    delta_99: float
    displacement_thickness: float | None
    momentum_thickness: float | None
    method: str


# --------------------------------------------------
# internal helpers
# --------------------------------------------------
def _reference_temperature_ratio(
    mach: float,
    tw_t0: float,
    gamma: float,
) -> float:
    """Return the Eckert reference-temperature ratio T*/Te."""

    # convert stagnation-referenced wall temperature ratio to edge-referenced
    te_t0 = 1.0 / (1.0 + 0.5 * (gamma - 1.0) * mach**2)
    tw_te = tw_t0 / te_t0

    # compute Eckert (1955) reference temperature ratio
    temperature_ratio = 0.5 + 0.039 * mach**2 + 0.5 * tw_te
    return temperature_ratio


# --------------------------------------------------
# public API
# --------------------------------------------------
def compute_boundary_layer_thickness(
    x: float,
    re1: float,
    method: str = "blasius",
    mach: float | None = None,
    tw_t0: float | None = None,
    gamma: float = 1.4,
) -> BoundaryLayerThicknessResult:
    """Compute laminar flat-plate boundary-layer thickness estimates.

    Args:
        x: Streamwise distance from the leading edge [m].
        re1: Unit Reynolds number [1/m].
        method: Thickness correlation name.
        mach: Edge Mach number, required by ``eckert_reference``.
        tw_t0: Wall-to-stagnation temperature ratio, required by
            ``eckert_reference``.
        gamma: Specific heat ratio.

    Returns:
        Boundary-layer thickness estimates [m]. The displacement and momentum
        thicknesses are available only for the incompressible Blasius profile.

    Raises:
        ValueError: If an input or method is invalid.

    References:
        Blasius, H. (1908), "Grenzschichten in Flussigkeiten mit kleiner
        Reibung," Zeitschrift fur Mathematik und Physik, Vol. 56, pp. 1-37.
        Eckert, E.R.G. (1955), "Engineering relations for heat transfer and
        friction in high-velocity laminar and turbulent boundary-layer flow."
    """

    # normalize the method selector
    method_value = str(method).strip().lower()

    # validate common inputs
    if x < 0.0:
        raise ValueError("x must be non-negative")
    if re1 <= 0.0:
        raise ValueError("re1 must be positive")
    if gamma <= 1.0:
        raise ValueError("gamma must be greater than 1")
    if method_value not in BOUNDARY_LAYER_THICKNESS_METHODS:
        raise ValueError(
            f"method must be one of {BOUNDARY_LAYER_THICKNESS_METHODS}: got {method!r}"
        )

    # validate method-specific inputs even when x is zero
    if method_value == "eckert_reference":
        if mach is None:
            raise ValueError("mach is required for method='eckert_reference'")
        if tw_t0 is None:
            raise ValueError("tw_t0 is required for method='eckert_reference'")
        if mach < 0.0:
            raise ValueError("mach must be non-negative")
        if tw_t0 <= 0.0:
            raise ValueError("tw_t0 must be positive")

    # compute the local Reynolds number
    re_x = re1 * x

    # all thicknesses vanish at the leading edge
    if x == 0.0:
        delta_99 = 0.0
        if method_value == "blasius":
            displacement_thickness = 0.0
            momentum_thickness = 0.0
        else:
            displacement_thickness = None
            momentum_thickness = None
    else:
        # start from the incompressible Blasius thickness scale
        thickness_scale = x / sqrt(re_x)

        # apply the established reference-temperature correction when requested
        if method_value == "eckert_reference":
            temperature_ratio = _reference_temperature_ratio(
                mach,
                tw_t0,
                gamma,
            )
            thickness_scale *= temperature_ratio

        # evaluate the 99% velocity thickness on the selected thickness scale
        delta_99 = 5.0 * thickness_scale

        # integral thicknesses require the complete density and velocity profiles
        if method_value == "blasius":
            displacement_thickness = 1.7208 * thickness_scale
            momentum_thickness = 0.664 * thickness_scale
        else:
            displacement_thickness = None
            momentum_thickness = None

    result = BoundaryLayerThicknessResult(
        x=x,
        re_x=re_x,
        delta_99=delta_99,
        displacement_thickness=displacement_thickness,
        momentum_thickness=momentum_thickness,
        method=method_value,
    )
    return result
