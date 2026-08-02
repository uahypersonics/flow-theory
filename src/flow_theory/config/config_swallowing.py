"""Configuration adapter for the [swallowing] workflow section."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .schema import ConfigNode, validate_section_keys

# --------------------------------------------------
# section structure
# --------------------------------------------------
_ALLOWED_KEYS = {
    "gamma",
    "mach",
    "nose_radius",
    "output",
    "re1",
    "run",
    "tw_t0",
}

_REQUIRED_KEYS = {"mach", "nose_radius", "re1", "run", "tw_t0"}


# --------------------------------------------------
# typed configuration
# --------------------------------------------------
@dataclass(slots=True)
class SwallowingConfig:
    """Validated inputs for an entropy swallowing calculation."""

    run: bool
    mach: object
    re1: object
    nose_radius: object
    tw_t0: object
    gamma: float = 1.4
    output: Path | None = None


# --------------------------------------------------
# public API
# --------------------------------------------------
def parse_swallowing_config(section: ConfigNode) -> SwallowingConfig:
    """Validate and convert a [swallowing] section."""

    # validate section keys before accessing required attributes
    validate_section_keys(
        section,
        section_name="swallowing",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    # validate the workflow toggle separately to avoid truthy string values
    run_value = section.run
    if not isinstance(run_value, bool):
        raise ValueError("swallowing.run must be true or false")

    # convert optional values
    gamma = float(getattr(section, "gamma", 1.4))

    output_value = getattr(section, "output", None)
    output = None if output_value is None else Path(str(output_value))

    # build the typed runner input
    config = SwallowingConfig(
        run=run_value,
        mach=section.mach,
        re1=section.re1,
        nose_radius=section.nose_radius,
        tw_t0=section.tw_t0,
        gamma=gamma,
        output=output,
    )
    return config
