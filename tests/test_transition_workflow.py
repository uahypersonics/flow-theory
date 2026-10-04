"""Tests for the transition configuration and runner workflow."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

from flow_theory.config import ConfigNode, TransitionConfig, parse_transition_config
from flow_theory.runners import run_transition


# --------------------------------------------------
# tests
# --------------------------------------------------
def test_parse_transition_config_defaults_run_to_true() -> None:
    """Focused transition configs should not require a workflow toggle."""

    config = parse_transition_config(
        ConfigNode({"mach": 5.0, "re1": 3.0e6, "tw_te": 0.5})
    )

    assert isinstance(config, TransitionConfig)
    assert config.run is True
    assert config.method == "van_driest_blumer"


def test_run_transition_writes_swept_output(tmp_path: Path) -> None:
    """The transition runner should broadcast inputs and write every case."""

    output_path = tmp_path / "transition.dat"
    config = TransitionConfig(
        mach=[5.0, 6.0],
        re1=3.0e6,
        tw_te=0.5,
        output=output_path,
    )

    run_transition(config)
    output_text = output_path.read_text(encoding="utf-8")

    assert 'ZONE T="transition van_driest_blumer", I=2' in output_text
