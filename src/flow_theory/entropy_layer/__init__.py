"""Entropy-layer estimates and swallowing calculations."""

from .estimate import entropy_layer_thickness
from .swallowing import is_swallowed, swallowing_distance

__all__ = [
    "entropy_layer_thickness",
    "is_swallowed",
    "swallowing_distance",
]
