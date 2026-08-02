"""Tests for shared skin-friction and Stanton-number input validation."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
import pytest

from flow_theory.cf_ch import cf_laminar
from flow_theory.cf_ch.validate_cf_ch_inputs import validate_cf_ch_inputs

# --------------------------------------------------
# shared test inputs
# --------------------------------------------------
VALID_INPUTS = {
    "x": np.array([0.1, 0.5, 1.0]),
    "re1": 1.0e7,
    "mach": 4.0,
    "temp_edge": 300.0,
    "temp_wall": 180.0,
    "wall_type": "isothermal",
    "gamma": 1.4,
    "pr": 0.72,
}


# --------------------------------------------------
# shared validator tests
# --------------------------------------------------
def test_validate_cf_ch_inputs_accepts_physical_inputs() -> None:
    """Physical scalar parameters and station arrays should pass validation."""

    # validate
    validate_cf_ch_inputs(**VALID_INPUTS)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("x", np.array([]), "at least one"),
        ("x", np.array([0.1, 0.0]), "positive"),
        ("x", np.array([0.1, np.nan]), "finite"),
        ("re1", 0.0, "re1 must be"),
        ("re1", np.inf, "re1 must be"),
        ("mach", -1.0, "mach must be"),
        ("temp_edge", 0.0, "temp_edge must be"),
        ("temp_wall", np.nan, "temp_wall must be"),
        ("wall_type", "slip", "wall_type must be"),
        ("gamma", 1.0, "gamma must be"),
        ("pr", 0.0, "pr must be"),
    ],
)
def test_validate_cf_ch_inputs_rejects_nonphysical_input(
    name: str,
    value: object,
    message: str,
) -> None:
    """Each common nonphysical input should raise a clear error."""

    # replace one valid input with the invalid test value
    inputs = VALID_INPUTS.copy()
    inputs[name] = value

    # validate
    with pytest.raises(ValueError, match=message):
        validate_cf_ch_inputs(**inputs)


def test_cf_laminar_enforces_shared_input_validation() -> None:
    """Direct laminar API calls should pass through the shared validator."""

    # evaluate with a nonphysical leading-edge station
    with pytest.raises(ValueError, match="x must contain only positive values"):
        cf_laminar(
            x=0.0,
            re1=1.0e7,
            mach=4.0,
            temp_edge=300.0,
            temp_wall=180.0,
            wall_type="isothermal",
        )
