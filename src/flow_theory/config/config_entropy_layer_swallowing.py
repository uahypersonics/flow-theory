"""Configuration adapter for the [entropy_layer_swallowing] workflow section."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .schema import ConfigNode, validate_section_keys

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


@dataclass(slots=True, frozen=True)
class EntropyLayerSwallowingConfig:
    """Validated inputs for an entropy-layer swallowing calculation."""

    run: bool
    mach: object
    re1: object
    nose_radius: object
    tw_t0: object
    gamma: float = 1.4
    output: Path | None = None


def parse_entropy_layer_swallowing_config(
    section: ConfigNode,
) -> EntropyLayerSwallowingConfig:
    """Validate and convert an [entropy_layer_swallowing] section."""

    validate_section_keys(
        section,
        section_name="entropy_layer_swallowing",
        allowed_keys=_ALLOWED_KEYS,
        required_keys=_REQUIRED_KEYS,
    )

    run_value = section.run
    if not isinstance(run_value, bool):
        raise ValueError("entropy_layer_swallowing.run must be true or false")

    gamma = float(getattr(section, "gamma", 1.4))
    output_value = getattr(section, "output", None)
    output = None if output_value is None else Path(str(output_value))

    config = EntropyLayerSwallowingConfig(
        run=run_value,
        mach=section.mach,
        re1=section.re1,
        nose_radius=section.nose_radius,
        tw_t0=section.tw_t0,
        gamma=gamma,
        output=output,
    )
    return config
