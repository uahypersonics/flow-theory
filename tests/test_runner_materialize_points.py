from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest

from flow_theory.config import CfChConfig
from flow_theory.config.point_sweep import point_sweep
from flow_theory.config.schema import ConfigNode
from flow_theory.runners import run_cf_ch


def test_point_sweep_accepts_scalar() -> None:
    values = point_sweep(1.5, key_name="cf_ch.x")

    assert values.shape == (1,)
    assert np.allclose(values, np.array([1.5], dtype=float))


def test_point_sweep_supports_count_based_sweep() -> None:
    values = point_sweep([0.1, 1.0, 5], key_name="cf_ch.x")

    assert np.allclose(values, np.linspace(0.1, 1.0, 5, dtype=float))


def test_point_sweep_supports_step_based_sweep() -> None:
    values = point_sweep([0.1, 1.0, 0.2], key_name="cf_ch.x")

    assert np.allclose(values, np.array([0.1, 0.3, 0.5, 0.7, 0.9, 1.0]))


def test_point_sweep_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        point_sweep(-0.1, key_name="cf_ch.x")

    with pytest.raises(ValueError, match="greater than start"):
        point_sweep([1.0, 1.0, 2], key_name="cf_ch.x")


def test_cf_ch_config_resolves_scalar_x() -> None:
    config = CfChConfig(
        run=True,
        flow_conditions=Path("flow_conditions.json"),
        x=1.5,
    )
    values = config.x

    assert values.shape == (1,)
    assert np.allclose(values, np.array([1.5], dtype=float))


def test_cf_ch_config_resolves_count_based_x() -> None:
    config = CfChConfig(
        run=True,
        flow_conditions=Path("flow_conditions.json"),
        x=[0.1, 1.0, 5],
    )
    values = config.x

    assert np.allclose(values, np.linspace(0.1, 1.0, 5, dtype=float))


def test_cf_ch_config_resolves_step_based_x() -> None:
    config = CfChConfig(
        run=True,
        flow_conditions=Path("flow_conditions.json"),
        x=[0.1, 1.0, 0.2],
    )
    values = config.x

    assert np.allclose(values, np.array([0.1, 0.3, 0.5, 0.7, 0.9, 1.0]))


def test_cf_ch_config_rejects_invalid_x_values() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        CfChConfig(
            run=True,
            flow_conditions=Path("flow_conditions.json"),
            x=-0.1,
        )

    with pytest.raises(ValueError, match="greater than start"):
        CfChConfig(
            run=True,
            flow_conditions=Path("flow_conditions.json"),
            x=[1.0, 1.0, 2],
        )


def test_config_node_repr_is_readable() -> None:
    cfg = ConfigNode({"cf_ch": {"run": True, "x": [0.1, 1.0, 5]}})

    assert "cf_ch" in repr(cfg)
    assert "run" in repr(cfg)


def test_cf_ch_config_is_frozen_after_init() -> None:
    config = CfChConfig(
        run=True,
        flow_conditions=Path("flow_conditions.json"),
        x=1.0,
        wall_type="adiabatic",
    )

    with pytest.raises(FrozenInstanceError):
        config.mode = "laminar"


def test_cf_ch_config_normalizes_values_in_post_init() -> None:
    config = CfChConfig(
        run=True,
        flow_conditions=Path("flow_conditions.json"),
        x=1.0,
        mode=" LAMINAR ",
        method=" Similarity ",
        wall_type=" ISOTHERMAL ",
        temp_wall=300.0,
    )

    assert config.mode == "laminar"
    assert config.method == "similarity"
    assert config.wall_type == "isothermal"


def test_run_cf_ch_requires_cf_ch_config_instance() -> None:
    with pytest.raises(TypeError, match="CfChConfig"):
        run_cf_ch(object())
