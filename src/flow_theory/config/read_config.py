"""Load and return a flow-theory configuration object."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import tomllib
from pathlib import Path

from .schema import ConfigNode

# --------------------------------------------------
# default config search names
# --------------------------------------------------
_DEFAULT_CONFIG_NAMES = (
    "flow_theory.toml",
    "flow-theory.toml",
    "flow_theory.cfg",
    "flow-theory.cfg",
)

# --------------------------------------------------
# scan for config file in the provided search path or current directory
# --------------------------------------------------
def find_config(search_path: str | Path = ".") -> Path | None:
    """Find the first matching flow-theory config file in *search_path*."""

    # convert search path to Path object
    # note: search path defaults to . if not provided
    fpath = Path(search_path)

    # iterate over default config names and return the first one that exists
    for fname in _DEFAULT_CONFIG_NAMES:

        # assemble candidate path and check if it exists
        candidate = fpath / fname

        if candidate.exists():
            # return the first matching config file path
            return candidate

    # if no config file is found, return None
    return None

# --------------------------------------------------
# public API
# --------------------------------------------------
def read_config(path: str | Path | None = None) -> ConfigNode:
    """Load TOML config and return ConfigNode object.

    Args:
        path: Explicit config path, or None to auto-discover.

    Returns:
        ConfigNode with recursive attribute access.

    Raises:
        FileNotFoundError: If config file cannot be resolved.
    """
    # resolve the config path
    if path is None:
        # no config path provided -> try to find a default config file in the current directory
        cfg_path = find_config(".")

        # no default config file found -> raise FileNotFoundError
        if cfg_path is None:
            tried = ", ".join(_DEFAULT_CONFIG_NAMES)
            raise FileNotFoundError(f"No config file found. Tried: {tried}")
    else:
        # explicit config path provided -> check if it exists
        cfg_path = Path(path)

        # if the explicit config path does not exist, raise FileNotFoundError
        if not cfg_path.exists():
            raise FileNotFoundError(f"Config file not found: {cfg_path}")

    # read and parse config file as TOML
    with cfg_path.open("rb") as stream:
        cfg = tomllib.load(stream)

    # return a ConfigNode object for recursive attribute access
    return ConfigNode(cfg)
