"""Configuration schema helpers for flow-theory.

Provides a recursive config wrapper exposing dict keys
as attributes:

    cfg.cf_ch.run
    cfg.cf_ch.x
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from typing import Any


# --------------------------------------------------
# attribute-access config node
# --------------------------------------------------
class ConfigNode:
    """Recursive config wrapper exposing dict keys as attributes."""

    # build ConfigNode from a dict, recursively converting nested dicts to ConfigNode upon instantiation
    def __init__(self, data: dict[str, Any]) -> None:

        # store the original dict and convert nested dicts to ConfigNode
        self._data: dict[str, Any] = {}

        # loop over key-value pairs in the input dict and convert nested dicts to ConfigNode
        for key, value in data.items():
            converted = self._convert(value)
            self._data[key] = converted
            setattr(self, key, converted)

    @classmethod
    def _convert(cls, value: Any) -> Any:
        """Recursively convert nested dict values to ConfigNode."""
        if isinstance(value, dict):
            return cls(value)
        if isinstance(value, list):
            return [cls._convert(item) for item in value]
        return value

    def __repr__(self) -> str:
        """Return a readable mapping representation for debugging."""
        return repr(self._data)

    def __str__(self) -> str:
        """Return a readable string representation for debugging."""
        return self.__repr__()

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get with default."""
        return self._data.get(key, default)

    def items(self):
        """Dict-like items for top-level section iteration."""
        return self._data.items()


# --------------------------------------------------
# structural validation
# --------------------------------------------------
def validate_section_keys(
    section: ConfigNode,
    section_name: str,
    allowed_keys: set[str],
    required_keys: set[str],
) -> None:
    """Validate the allowed and required keys for one config section."""

    # collect structural errors so the user can fix them together
    section_keys = {key for key, _ in section.items()}
    unknown_keys = sorted(section_keys - allowed_keys)
    missing_keys = sorted(required_keys - section_keys)

    errors: list[str] = []
    if unknown_keys:
        unknown_text = ", ".join(unknown_keys)
        errors.append(f"unknown keys in [{section_name}]: {unknown_text}")
    if missing_keys:
        missing_text = ", ".join(missing_keys)
        errors.append(f"missing required keys in [{section_name}]: {missing_text}")

    # report all structural errors at the config boundary
    if errors:
        raise ValueError("; ".join(errors))
