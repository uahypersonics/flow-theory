"""flow_theory — theoretical estimates for high-speed aerodynamics."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("flow-theory")
except PackageNotFoundError:
    __version__ = "unknown"
