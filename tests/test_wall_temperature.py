"""Tests for compressible flat-plate wall-temperature estimates."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import pytest

from flow_theory.cf_ch import estimate_adiabatic_wall_temperature


# --------------------------------------------------
# adiabatic wall-temperature tests
# --------------------------------------------------
def test_estimate_laminar_adiabatic_wall_temperature() -> None:
    """Laminar estimates should use the square-root recovery factor."""

    # build representative edge conditions
    temp_edge = 300.0
    mach = 4.0
    gamma = 1.4
    pr = 0.72

    # estimate expected adiabatic wall temperature
    recovery_factor = pr**0.5
    temperature_ratio = 1.0 + recovery_factor * 0.5 * (gamma - 1.0) * mach**2
    expected_temp_wall = temp_edge * temperature_ratio

    # evaluate the public wall-temperature API
    temp_wall = estimate_adiabatic_wall_temperature(
        temp_edge=temp_edge,
        mach=mach,
        gamma=gamma,
        pr=pr,
        mode="laminar",
    )

    # check
    assert temp_wall == pytest.approx(expected_temp_wall)


def test_estimate_turbulent_adiabatic_wall_temperature() -> None:
    """Turbulent estimates should use the cube-root recovery factor."""

    # build representative edge conditions
    temp_edge = 300.0
    mach = 4.0
    gamma = 1.4
    pr = 0.72

    # estimate expected adiabatic wall temperature
    recovery_factor = pr ** (1.0 / 3.0)
    temperature_ratio = 1.0 + recovery_factor * 0.5 * (gamma - 1.0) * mach**2
    expected_temp_wall = temp_edge * temperature_ratio

    # evaluate the public wall-temperature API
    temp_wall = estimate_adiabatic_wall_temperature(
        temp_edge=temp_edge,
        mach=mach,
        gamma=gamma,
        pr=pr,
        mode="turbulent",
    )

    # check
    assert temp_wall == pytest.approx(expected_temp_wall)


def test_estimate_adiabatic_wall_temperature_rejects_unknown_mode() -> None:
    """Wall-temperature estimates should reject unknown boundary-layer modes."""

    # check
    with pytest.raises(ValueError, match="mode"):
        estimate_adiabatic_wall_temperature(
            temp_edge=300.0,
            mach=4.0,
            gamma=1.4,
            pr=0.72,
            mode="invalid",
        )
