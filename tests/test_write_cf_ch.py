"""Tests for cf/ch terminal and Tecplot output."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pytest

from flow_theory.io import write_cf_ch


# --------------------------------------------------
# cf/ch writer tests
# --------------------------------------------------
def test_write_cf_ch_skips_when_output_is_not_configured(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Missing output paths should stop before result data is parsed."""

    # capture the normal output notice
    caplog.set_level(logging.INFO, logger="flow-theory")

    # call with no data to prove the output-path guard runs first
    write_cf_ch({}, None)

    # check
    assert "cf/ch output file is not configured; skipping file write" in caplog.messages


def test_write_cf_ch_discovers_modes_and_writes_method_zones(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each mode should produce one file containing one zone per method."""

    # build representative multi-mode result data
    estimate_data = {
        "x": np.array([0.1, 0.2]),
        "re_x": np.array([1.0e6, 2.0e6]),
        "modes": ["laminar", "turbulent"],
        "method_names": {
            "laminar": ["blasius", "similarity"],
            "turbulent": ["van_driest_ii"],
        },
        "cf": {
            "laminar": {
                "blasius": np.array([6.64e-4, 4.69e-4]),
                "similarity": np.array([6.50e-4, 4.60e-4]),
            },
            "turbulent": {
                "van_driest_ii": np.array([3.00e-3, 2.80e-3]),
            },
        },
        "ch": {
            "laminar": {
                "blasius": np.array([4.13e-4, 2.92e-4]),
                "similarity": np.array([4.04e-4, 2.86e-4]),
            },
            "turbulent": {
                "van_driest_ii": np.array([1.87e-3, 1.74e-3]),
            },
        },
        "temp_wall": {"laminar": 180.0, "turbulent": 500.0},
        "wall_type": "isothermal",
    }
    output = tmp_path / "cf_vs_x.dat"

    # capture the records enabled by the CLI's verbose callback
    caplog.set_level(logging.DEBUG, logger="flow-theory")

    # write all modes and methods from the result dictionary
    write_cf_ch(estimate_data, output)

    # read the mode-specific Tecplot files
    laminar_text = (tmp_path / "cf_vs_x_laminar.dat").read_text(encoding="utf-8")
    turbulent_text = (tmp_path / "cf_vs_x_turbulent.dat").read_text(encoding="utf-8")

    # check one zone per discovered method
    assert laminar_text.count("ZONE") == 2
    assert 'ZONE T="cf_ch laminar blasius isothermal"' in laminar_text
    assert 'ZONE T="cf_ch laminar similarity isothermal"' in laminar_text
    assert turbulent_text.count("ZONE") == 1
    assert 'ZONE T="cf_ch turbulent van_driest_ii isothermal"' in turbulent_text

    # check verbose output details
    assert "cf/ch output modes: laminar, turbulent" in caplog.messages
    assert (
        "cf/ch output methods by mode: "
        "{'laminar': ['blasius', 'similarity'], 'turbulent': ['van_driest_ii']}"
        in caplog.messages
    )
    assert (
        "preparing laminar output with methods: blasius, similarity" in caplog.messages
    )
    assert f"laminar output file: {tmp_path / 'cf_vs_x_laminar.dat'}" in caplog.messages
    assert "wrote zone cf_ch laminar blasius isothermal with 2 rows" in caplog.messages
    assert (
        "wrote zone cf_ch turbulent van_driest_ii isothermal with 2 rows"
        in caplog.messages
    )

    # check direct terminal output is owned by the logger
    terminal_output = capsys.readouterr().out
    assert terminal_output == ""
