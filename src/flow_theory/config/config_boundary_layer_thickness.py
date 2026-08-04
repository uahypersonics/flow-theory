"""Configuration adapter for [boundary_layer_thickness] workflow sections."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flow_theory.boundary_layer import BOUNDARY_LAYER_THICKNESS_METHODS

from .schema import ConfigNode, validate_section_keys

_ALLOWED_KEYS = {
    "gamma",
    "mach",
    "method",
    "output",
    "re1",
    "run",
    "tw_t0",
    "x",
}
_REQUIRED_KEYS = {"re1", "run", "x"}


@dataclass(slots=True, frozen=True)
class BoundaryLayerThicknessConfig:
    """Validated inputs for a boundary-layer thickness calculation."""

    run: bool
    x: object
    re1: object
    method: str = "blasius"
    mach: object | None = None
    tw_t0: object | None = None
    gamma: float = 1.4
    output: Path | None = None

    def __post_init__(self) -> None:
        """Normalize and validate thickness options."""

        # normalize the method selector
        method_value = self.method.strip().lower()
        object.__setattr__(self, "method", method_value)

        # validate the selected correlation
        if method_value not in BOUNDARY_LAYER_THICKNESS_METHODS:
            raise ValueError(
                "[boundary_layer_thickness] method must be one of "
                f"{BOUNDARY_LAYER_THICKNESS_METHODS}"
            )

        # validate inputs required by the reference-temperature method
        if method_value == "eckert_reference":
            if self.mach is None:
                raise ValueError(
                    "[boundary_layer_thickness] mach is required for "
                    "method='eckert_reference'"
                )
            if self.tw_t0 is None:
                raise ValueError(
                    "[boundary_layer_thickness] tw_t0 is required for "
                    "method='eckert_reference'"
                )


def parse_boundary_layer_thickness_config(
    section: ConfigNode,
) -> BoundaryLayerThicknessConfig:
    """Validate and convert a [boundary_layer_thickness] section."""

    # validate section keys before reading values
    validate_section_keys(
        section,
        section_name="boundary_layer_thickness",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    # validate the workflow toggle separately
    run_value = section.run
    if not isinstance(run_value, bool):
        raise ValueError("boundary_layer_thickness.run must be true or false")

    # convert optional values
    method = str(getattr(section, "method", "blasius"))
    mach = getattr(section, "mach", None)
    tw_t0 = getattr(section, "tw_t0", None)
    gamma = float(getattr(section, "gamma", 1.4))
    output_value = getattr(section, "output", None)
    output = None if output_value is None else Path(str(output_value))

    # build the typed runner input
    config = BoundaryLayerThicknessConfig(
        run=run_value,
        x=section.x,
        re1=section.re1,
        method=method,
        mach=mach,
        tw_t0=tw_t0,
        gamma=gamma,
        output=output,
    )
    return config
