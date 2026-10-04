"""Shared support for calculator-scoped configuration files."""

from __future__ import annotations

from pathlib import Path

import typer

from flow_theory.templates import render_templates


def write_focused_config(
    preset: str,
    output: Path,
    force: bool,
    run_command: str,
) -> None:
    """Write one calculator's starter configuration."""

    # protect existing user configuration unless overwrite was requested
    if output.exists() and not force:
        raise FileExistsError(f"output exists: {output} (use --force to overwrite)")

    # render and write the calculator-specific TOML
    content = render_templates(preset)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")

    # report the generated path and its matching execution command
    typer.echo(f"wrote {output}")
    typer.echo(f"then run: {run_command} --config {output}")
