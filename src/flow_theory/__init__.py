"""
flow_theory: Theoretical estimates for high-speed aerodynamics.
"""

# --------------------------------------------------
# stdlib imports
# --------------------------------------------------
from importlib.metadata import PackageNotFoundError, version

# --------------------------------------------------
# package imports
# --------------------------------------------------
from flow_theory.boundary_layer import (
    BoundaryLayerThicknessResult,
    compute_boundary_layer_thickness,
)
from flow_theory.cf_ch import (
    cf_laminar,
    cf_turbulent,
    ch_laminar,
    ch_turbulent,
    compute_cf_ch,
)
from flow_theory.entropy_layer import (
    entropy_layer_thickness,
    is_swallowed,
    swallowing_distance,
)
from flow_theory.shock import (
    ShockShapeResult,
    ShockStandoffResult,
    compute_shock_shape,
    compute_shock_standoff,
)
from flow_theory.transition import (
    intermittency,
    n_factor,
    re_theta_onset,
    transition_blunt_delta_wing,
    transition_x,
)

# --------------------------------------------------
# load version
# --------------------------------------------------
try:
    # installed package: importlib.metadata reads from the egg-info/dist-info
    __version__ = version("flow-theory")
except PackageNotFoundError:
    try:
        # fallback: setuptools-scm writes _version.py at build/install time
        from flow_theory._version import version as _scm_version  # type: ignore[import]
        __version__ = _scm_version
    except ImportError:
        __version__ = "unknown"

# --------------------------------------------------
# public api
# --------------------------------------------------

__all__ = [
    "__version__",
    "BoundaryLayerThicknessResult",
    "cf_laminar",
    "cf_turbulent",
    "compute_cf_ch",
    "compute_boundary_layer_thickness",
    "ch_laminar",
    "ch_turbulent",
    "entropy_layer_thickness",
    "intermittency",
    "is_swallowed",
    "n_factor",
    "re_theta_onset",
    "ShockShapeResult",
    "ShockStandoffResult",
    "compute_shock_shape",
    "compute_shock_standoff",
    "swallowing_distance",
    "transition_blunt_delta_wing",
    "transition_x",
]
