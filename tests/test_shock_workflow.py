"""Tests for config-driven shock workflows."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import importlib
from pathlib import Path

import pytest
import typer
from flow_state.gas import PerfectGas
from flow_state.io import write_json
from flow_state.solvers import solve

from flow_theory.cli.cmd_run import cmd_run
from flow_theory.config import (
    ConfigNode,
    ShockShapeConfig,
    ShockStandoffConfig,
    parse_shock_shape_config,
    parse_shock_standoff_config,
)
from flow_theory.runners import run_shock_shape, run_shock_standoff

run_shock_shape_module = importlib.import_module("flow_theory.runners.run_shock_shape")
run_shock_standoff_module = importlib.import_module(
    "flow_theory.runners.run_shock_standoff"
)


# --------------------------------------------------
# configuration tests
# --------------------------------------------------
def test_parse_shock_workflow_configs() -> None:
    """Each workflow section should produce its own typed configuration."""

    # parse representative sections
    standoff = parse_shock_standoff_config(
        ConfigNode(
            {
                "run": True,
                "flow_conditions": "flow.json",
                "geometry": "cylinder",
                "nose_radius": 0.01,
            }
        )
    )
    shape = parse_shock_shape_config(
        ConfigNode(
            {
                "run": True,
                "flow_conditions": "flow.json",
                "nose_radius": 0.01,
                "n_points": 51,
                "lateral_extent": 0.05,
            }
        )
    )

    # check independent workflow contracts
    assert isinstance(standoff, ShockStandoffConfig)
    assert standoff.geometry == "cylinder"
    assert isinstance(shape, ShockShapeConfig)
    assert shape.n_points == 51
    assert shape.lateral_extent == 0.05


# --------------------------------------------------
# FlowState handoff tests
# --------------------------------------------------
@pytest.mark.parametrize(
    ("config_class", "runner", "runner_module", "compute_name", "writer_name"),
    [
        (
            ShockStandoffConfig,
            run_shock_standoff,
            run_shock_standoff_module,
            "compute_shock_standoff",
            "write_shock_standoff",
        ),
        (
            ShockShapeConfig,
            run_shock_shape,
            run_shock_shape_module,
            "compute_shock_shape",
            "write_shock_shape",
        ),
    ],
)
def test_shock_runners_use_reconstructed_flow_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    config_class,
    runner,
    runner_module,
    compute_name: str,
    writer_name: str,
) -> None:
    """Both runners should get Mach and gamma from canonical FlowState JSON."""

    # build and write a complete freestream state
    state = solve(
        mach=6.0,
        pres=101325.0,
        temp=300.0,
        gas=PerfectGas.air(),
    )
    flow_state_path = tmp_path / "flow_state.json"
    write_json(state, flow_state_path)

    config = config_class(
        run=True,
        flow_conditions=flow_state_path,
        nose_radius=0.01,
    )
    captured: dict[str, object] = {}

    def capture_compute(**kwargs):
        captured.update(kwargs)
        return object()

    # isolate the runner's data handoff
    monkeypatch.setattr(runner_module, compute_name, capture_compute)
    monkeypatch.setattr(runner_module, writer_name, lambda result, output: None)

    # run through the public workflow boundary
    runner(config)

    # check canonical state values reach the physics API
    assert captured["mach"] == state.mach
    assert captured["gamma"] == state.gamma
    assert captured["nose_radius"] == 0.01


def test_run_command_executes_both_shock_sections(tmp_path: Path) -> None:
    """One run config should independently execute standoff and shape sections."""

    # build and write the shared canonical freestream state
    state = solve(
        mach=6.0,
        pres=101325.0,
        temp=300.0,
        gas=PerfectGas.air(),
    )
    flow_state_path = tmp_path / "flow_state.json"
    write_json(state, flow_state_path)

    # build a config that enables both independent shock workflows
    standoff_path = tmp_path / "standoff.dat"
    shape_path = tmp_path / "shape.dat"
    config_path = tmp_path / "flow_theory.toml"
    config_text = f"""
[shock_standoff]
run = true
flow_conditions = "{flow_state_path}"
nose_radius = 0.01
method = "serbin"
output = "{standoff_path}"

[shock_shape]
run = true
flow_conditions = "{flow_state_path}"
nose_radius = 0.01
n_points = 11
output = "{shape_path}"
"""
    config_path.write_text(config_text, encoding="utf-8")

    # execute the same dispatcher used by the CLI
    try:
        cmd_run(config_path)
    except typer.Exit as error:
        pytest.fail(f"flow-theory run exited unexpectedly: {error}")

    # check both workflows produced their own output
    assert standoff_path.exists()
    assert shape_path.exists()
    assert (
        'ZONE T="shock standoff sphere serbin", I=1'
        in standoff_path.read_text(encoding="utf-8")
    )
    assert 'ZONE T="shock shape sphere billig", I=11' in shape_path.read_text(
        encoding="utf-8"
    )
