"""Regression tests for the similarity-based laminar skin-friction formula."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import importlib
import math
from types import SimpleNamespace

import numpy as np
import pytest
from flow_state.transport import get_transport_model

cf_laminar_module = importlib.import_module("flow_theory.cf_ch.cf_laminar")
ch_module = importlib.import_module("flow_theory.cf_ch.ch")


# --------------------------------------------------
# similarity regression tests
# --------------------------------------------------
def test_adiabatic_similarity_cf_uses_solved_wall_temperature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Adiabatic similarity cf should use the wall temperature solved by simbl."""

    # build representative flat-plate state
    re_x = 1.0e6
    mach = 4.0
    temp_edge = 300.0
    temp_wall = 180.0
    gamma = 1.4
    pr = 0.72
    fpp_wall = 0.61
    temp_wall_solved = 720.0
    visc_model = get_transport_model("keyes")

    # force a known similarity solution so the formula can be checked directly
    wall_types: list[str] = []
    viscosity_models = []

    def _known_solve(inputs, options, *, visc_model):
        wall_types.append(inputs.wall_bc)
        viscosity_models.append(visc_model)
        assert options.bvp_fallback is True

        solution = SimpleNamespace(
            fpp=np.array([fpp_wall]),
            tau=np.array([temp_wall_solved / temp_edge]),
        )
        result = SimpleNamespace(converged=True)
        return solution, result

    monkeypatch.setattr(cf_laminar_module, "solve_similarity", _known_solve)

    # compute expected wall-to-edge property ratio from the derivation
    rho_w_rho_e = temp_edge / temp_wall_solved
    mu_w_mu_e = visc_model.mu(temp_wall_solved) / visc_model.mu(temp_edge)
    wall_edge_ratio = rho_w_rho_e * mu_w_mu_e
    expected_cf = math.sqrt(2.0) * wall_edge_ratio * fpp_wall / math.sqrt(re_x)

    # evaluate similarity cf through the public laminar API
    cf_value = cf_laminar_module.cf_laminar(
        x=np.array([0.1]),
        re1=1.0e7,
        mach=mach,
        temp_edge=temp_edge,
        temp_wall=temp_wall,
        wall_type="adiabatic",
        gamma=gamma,
        pr=pr,
        method="similarity",
        visc_model=visc_model,
    )

    # check
    assert wall_types == ["adiabatic"]
    assert viscosity_models == [visc_model]
    assert cf_value == pytest.approx(np.array([expected_cf]))


def test_similarity_ch_uses_similarity_cf(monkeypatch: pytest.MonkeyPatch) -> None:
    """Similarity Ch should apply the Reynolds analogy to similarity cf."""

    # build known skin-friction output
    cf_value = 2.5e-3
    pr = 0.72
    calls: list[str] = []

    def _known_cf(*args, method: str, **kwargs) -> np.ndarray:
        calls.append(method)
        return np.array([cf_value])

    # replace the skin-friction calculation so method forwarding is observable
    monkeypatch.setattr(ch_module, "cf_laminar", _known_cf)

    # evaluate Stanton number through the public laminar API
    ch_value = ch_module.ch_laminar(
        x=np.array([0.1]),
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=180.0,
        wall_type="isothermal",
        pr=pr,
        method="similarity",
    )

    # check
    expected_ch = cf_value / (2.0 * pr ** (2.0 / 3.0))
    assert calls == ["similarity"]
    assert ch_value == pytest.approx(np.array([expected_ch]))


def test_laminar_ch_defaults_to_blasius(monkeypatch: pytest.MonkeyPatch) -> None:
    """Laminar Ch should share the Blasius default used by laminar cf."""

    # track the method forwarded to the skin-friction API
    methods = []

    def _known_cf(*args, method: str, **kwargs) -> float:
        methods.append(method)
        return 2.5e-3

    monkeypatch.setattr(ch_module, "cf_laminar", _known_cf)

    # evaluate Stanton number without selecting a method
    ch_module.ch_laminar(
        x=0.1,
        re1=1.0e7,
        mach=4.0,
        temp_edge=300.0,
        temp_wall=180.0,
        wall_type="isothermal",
    )

    # check
    assert methods == ["blasius"]


def test_laminar_cf_rejects_method_aliases() -> None:
    """Laminar methods should require an exact registered method name."""

    # check
    with pytest.raises(
        ValueError,
        match="method must be one of.*eckert_reference_temperature",
    ):
        cf_laminar_module.cf_laminar(
            x=np.array([0.1]),
            re1=1.0e7,
            mach=4.0,
            temp_edge=300.0,
            temp_wall=180.0,
            wall_type="isothermal",
            method="eckert_reference_temperature",
        )
