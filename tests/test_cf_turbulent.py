"""Regression tests for turbulent skin-friction correlations."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import importlib
import math

import numpy as np
import pytest
from flow_state.transport import get_transport_model
from scipy.optimize import brentq

cf_turbulent_module = importlib.import_module("flow_theory.cf_ch.cf_turbulent")


# --------------------------------------------------
# turbulent correlation tests
# --------------------------------------------------
def test_turbulent_cf_converts_average_schoenherr_value_to_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Turbulent methods should return local rather than average skin friction."""

    # build known transform and average skin-friction values
    average_cf = 4.0e-3
    compressibility_factor = 2.0
    reynolds_factor = 0.5
    factors = cf_turbulent_module.TransformFactors(
        f_c=np.full(2, compressibility_factor),
        f_theta=np.full(2, compressibility_factor * reynolds_factor),
        f_x=np.full(2, reynolds_factor),
    )

    # replace internal calculations so the local conversion is isolated
    monkeypatch.setattr(
        cf_turbulent_module,
        "_compressible_transform_factors",
        lambda *args, **kwargs: factors,
    )
    monkeypatch.setattr(
        cf_turbulent_module,
        "_cf_inc_ave_karman_schoenherr",
        lambda reynolds: np.full_like(reynolds, average_cf),
    )

    # evaluate the public turbulent API
    cf_value = cf_turbulent_module.cf_turbulent(
        x=np.array([1.0, 2.0]),
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=500.0,
        wall_type="isothermal",
        method="van_driest_ii",
    )

    # compute the local Karman-Schoenherr value used by Hopkins and Inouye
    numerator = 0.242 * average_cf
    denominator = 0.242 + 0.8686 * math.sqrt(average_cf)
    local_cf = numerator / denominator
    expected_cf = local_cf / compressibility_factor

    # check
    assert cf_value.shape == (2,)
    assert cf_value == pytest.approx(np.array([expected_cf, expected_cf]))


def test_karman_schoenherr_array_matches_scalar_reference_values() -> None:
    """Array evaluation should retain the previous implicit-law results."""

    # build representative incompressible Reynolds numbers
    reynolds = np.array([1.0e4, 1.0e6, 1.0e8])

    # evaluate the previous scalar implicit solve for reference
    expected_cf = np.array(
        [
            brentq(
                lambda cf: 0.242 / np.sqrt(cf) - np.log10(value * cf),
                1.0e-6,
                0.1,
            )
            for value in reynolds
        ]
    )

    # evaluate the array form of the Karman-Schoenherr relation
    cf_inc_ave = cf_turbulent_module._cf_inc_ave_karman_schoenherr(reynolds)

    # check
    assert cf_inc_ave.shape == reynolds.shape
    assert cf_inc_ave == pytest.approx(expected_cf, rel=1e-8)


def test_spalding_chi_transform_matches_hopkins_inouye_summary() -> None:
    """Spalding-Chi factors should retain the compressibility mapping."""

    # build representative compressible edge and wall conditions
    mach = 4.0
    temp_edge = 300.0
    temp_wall = 500.0
    gamma = 1.4
    pr = 0.72
    # evaluate the implemented transform
    factors = cf_turbulent_module._spalding_chi_transform_factors(
        re_x=np.array([1.0e6, 2.0e6]),
        mach=mach,
        temp_wall=temp_wall,
        temp_edge=temp_edge,
        gamma=gamma,
        pr=pr,
    )

    # independently evaluate the Hopkins-Inouye form of Spalding-Chi
    mach_factor = 0.5 * (gamma - 1.0) * mach**2
    recovery_factor = pr ** (1.0 / 3.0)
    wall_temp_ratio = temp_wall / temp_edge
    adiabatic_temp_ratio = 1.0 + recovery_factor * mach_factor
    wall_adiabatic_ratio = wall_temp_ratio / adiabatic_temp_ratio

    factor_a = math.sqrt(mach_factor * recovery_factor / wall_temp_ratio)
    factor_b = (1.0 + recovery_factor * mach_factor - wall_temp_ratio) / wall_temp_ratio
    denominator = math.sqrt(4.0 * factor_a**2 + factor_b**2)
    alpha = (2.0 * factor_a**2 - factor_b) / denominator
    beta = factor_b / denominator
    angle_sum = math.asin(alpha) + math.asin(beta)

    expected_compressibility_factor = recovery_factor * mach_factor / angle_sum**2
    temperature_factor = 1.0 / (wall_temp_ratio**0.702 * wall_adiabatic_ratio**0.772)
    expected_reynolds_factor = temperature_factor / expected_compressibility_factor

    # check
    assert factors.f_c == pytest.approx(np.full(2, expected_compressibility_factor))
    assert factors.f_theta == pytest.approx(np.full(2, temperature_factor))
    assert factors.f_x == pytest.approx(np.full(2, expected_reynolds_factor))


def test_sommer_short_transform_matches_hopkins_inouye_summary() -> None:
    """Sommer-Short factors should retain the reference-temperature mapping."""

    # build representative compressible edge and wall conditions
    re_x = np.array([1.0e6, 2.0e6])
    mach = 4.0
    temp_edge = 300.0
    temp_wall = 500.0
    visc_model = get_transport_model("sutherland")

    # evaluate the implemented transform
    factors = cf_turbulent_module._sommer_short_transform_factors(
        re_x=re_x,
        mach=mach,
        temp_wall=temp_wall,
        temp_edge=temp_edge,
        gamma=1.4,
        pr=0.72,
        visc_model=visc_model,
    )

    # independently evaluate the Hopkins-Inouye Sommer-Short form
    wall_edge_temp_ratio = temp_wall / temp_edge
    reference_temp_ratio = 1.0 + 0.035 * mach**2 + 0.45 * (wall_edge_temp_ratio - 1.0)
    reference_temp = reference_temp_ratio * temp_edge
    expected_f_c = reference_temp_ratio
    expected_f_theta = visc_model.mu(temp_edge) / visc_model.mu(reference_temp)
    expected_f_x = expected_f_theta / expected_f_c

    # check
    assert factors.f_c == pytest.approx(np.full(2, expected_f_c))
    assert factors.f_theta == pytest.approx(np.full(2, expected_f_theta))
    assert factors.f_x == pytest.approx(np.full(2, expected_f_x))


@pytest.mark.parametrize("method", cf_turbulent_module.TURBULENT_METHODS)
def test_turbulent_transform_returns_station_factors(method: str) -> None:
    """Every transformation should return consistent factors at each station."""

    # build representative station and flow inputs
    re_x = np.array([1.0e6, 2.0e6, 4.0e6])
    visc_model = get_transport_model("sutherland")

    # evaluate the selected transformation
    factors = cf_turbulent_module._compressible_transform_factors(
        re_x=re_x,
        mach=4.0,
        temp_wall=500.0,
        temp_edge=300.0,
        gamma=1.4,
        pr=0.72,
        method=method,
        visc_model=visc_model,
    )

    # check the array contract and defining factor identity
    assert factors.f_c.shape == re_x.shape
    assert factors.f_theta.shape == re_x.shape
    assert factors.f_x.shape == re_x.shape
    assert factors.f_x == pytest.approx(factors.f_theta / factors.f_c)


@pytest.mark.parametrize("method", cf_turbulent_module.TURBULENT_METHODS)
def test_turbulent_transform_has_exact_incompressible_limit(method: str) -> None:
    """Every turbulent transformation should reduce to identity at Mach zero."""

    # build a transport model for the transformation interface
    visc_model = get_transport_model("sutherland")

    # evaluate the incompressible limit
    factors = cf_turbulent_module._compressible_transform_factors(
        re_x=np.array([1.0e6, 2.0e6]),
        mach=0.0,
        temp_wall=300.0,
        temp_edge=300.0,
        gamma=1.4,
        pr=0.72,
        method=method,
        visc_model=visc_model,
    )

    # check
    assert factors.f_c == pytest.approx(np.ones(2))
    assert factors.f_theta == pytest.approx(np.ones(2))
    assert factors.f_x == pytest.approx(np.ones(2))


@pytest.mark.parametrize(
    "method",
    ["spalding_chi_1964", "white_christoph_1972"],
)
def test_turbulent_cf_rejects_method_aliases(method: str) -> None:
    """Turbulent methods should require an exact registered method name."""

    # check
    with pytest.raises(ValueError, match="method must be one of"):
        cf_turbulent_module.cf_turbulent(
            x=0.1,
            re1=1.0e7,
            mach=4.0,
            temp_edge=300.0,
            temp_wall=180.0,
            wall_type="isothermal",
            method=method,
        )
