"""Tests for the structured cf/ch computation results."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import importlib

import numpy as np
import pytest

from flow_theory.cf_ch import (
    cf_laminar,
    cf_turbulent,
    ch_laminar,
    ch_turbulent,
    compute_cf_ch,
)


# --------------------------------------------------
# result structure tests
# --------------------------------------------------
def test_compute_cf_ch_returns_arrays_for_scalar_x() -> None:
    """Scalar station inputs should produce one-element result arrays."""

    # compute one method at one streamwise station
    data = compute_cf_ch(
        x=0.1,
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=180.0,
        wall_type="isothermal",
        mode="laminar",
        method="blasius",
    )

    # check the stable array contract
    assert isinstance(data["x"], np.ndarray)
    assert isinstance(data["re_x"], np.ndarray)
    assert isinstance(data["cf"]["laminar"]["blasius"], np.ndarray)
    assert isinstance(data["ch"]["laminar"]["blasius"], np.ndarray)
    assert data["x"].shape == (1,)
    assert data["re_x"].shape == (1,)
    assert data["cf"]["laminar"]["blasius"].shape == (1,)
    assert data["ch"]["laminar"]["blasius"].shape == (1,)


def test_compute_cf_ch_resolves_adiabatic_temperature_by_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One all-mode call should use each mode's adiabatic recovery temperature."""

    # load the module so its method registries and calculations can be isolated
    compute_module = importlib.import_module("flow_theory.cf_ch.compute_cf_ch")
    monkeypatch.setattr(compute_module, "LAMINAR_METHODS", ("laminar_test",))
    monkeypatch.setattr(compute_module, "TURBULENT_METHODS", ("turbulent_test",))

    # capture the wall temperature passed to each mode calculation
    received_temp_wall = {}

    def fake_cf_laminar(
        x,
        re1,
        mach,
        temp_edge,
        temp_wall,
        wall_type,
        **kwargs,
    ):
        received_temp_wall["laminar"] = temp_wall
        return np.ones_like(x, dtype=float)

    def fake_cf_turbulent(
        x,
        re1,
        mach,
        temp_edge,
        temp_wall,
        wall_type,
        **kwargs,
    ):
        received_temp_wall["turbulent"] = temp_wall
        return np.ones_like(x, dtype=float)

    monkeypatch.setattr(compute_module, "cf_laminar", fake_cf_laminar)
    monkeypatch.setattr(compute_module, "cf_turbulent", fake_cf_turbulent)

    # compute both modes through the public all-mode contract
    data = compute_module.compute_cf_ch(
        x=0.1,
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=None,
        wall_type="adiabatic",
    )

    # check each mode receives and reports its own recovery temperature
    assert data["temp_wall"]["laminar"] == pytest.approx(received_temp_wall["laminar"])
    assert data["temp_wall"]["turbulent"] == pytest.approx(
        received_temp_wall["turbulent"]
    )
    assert data["temp_wall"]["laminar"] != pytest.approx(data["temp_wall"]["turbulent"])


@pytest.mark.parametrize("cf_function", [cf_laminar, cf_turbulent])
def test_cf_rejects_unknown_wall_type(cf_function) -> None:
    """Skin-friction APIs should require explicit valid wall metadata."""

    # check
    with pytest.raises(ValueError, match="wall_type"):
        cf_function(
            x=np.array([0.1]),
            re1=1.0e7,
            mach=4.0,
            temp_edge=300.0,
            temp_wall=180.0,
            wall_type="invalid",
        )


@pytest.mark.parametrize("cf_function", [cf_laminar, cf_turbulent])
def test_cf_rejects_multidimensional_x_array(cf_function) -> None:
    """Skin-friction APIs should reject multidimensional station arrays."""

    # check
    with pytest.raises(ValueError, match="scalar or one-dimensional array"):
        cf_function(
            x=np.array([[0.1]]),
            re1=1.0e7,
            mach=4.0,
            temp_edge=300.0,
            temp_wall=180.0,
            wall_type="isothermal",
        )


@pytest.mark.parametrize("cf_function", [cf_laminar, cf_turbulent])
def test_cf_returns_float_for_scalar_x(cf_function) -> None:
    """Direct skin-friction APIs should preserve scalar station inputs."""

    # evaluate one scalar station
    cf_value = cf_function(
        x=0.1,
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=180.0,
        wall_type="isothermal",
    )

    # check
    assert isinstance(cf_value, float)


@pytest.mark.parametrize("ch_function", [ch_laminar, ch_turbulent])
def test_ch_returns_float_for_scalar_x(ch_function) -> None:
    """Direct Stanton APIs should preserve scalar station inputs."""

    # evaluate one scalar station
    ch_value = ch_function(
        x=0.1,
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=180.0,
        wall_type="isothermal",
    )

    # check
    assert isinstance(ch_value, float)


def test_cf_laminar_preserves_x_array_shape() -> None:
    """Laminar skin friction should evaluate a full station array at once."""

    # build multiple streamwise stations
    x_values = np.array([0.1, 0.4, 1.0])
    re1 = 1.0e7

    # evaluate one correlation over the complete station array
    cf_values = cf_laminar(
        x=x_values,
        re1=re1,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=180.0,
        wall_type="isothermal",
        method="blasius",
    )

    # check
    expected_cf = 0.664 / np.sqrt(x_values * re1)
    assert cf_values.shape == x_values.shape
    assert cf_values == pytest.approx(expected_cf)
