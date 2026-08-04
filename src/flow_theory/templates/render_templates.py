"""Reusable TOML templates for flow-theory CLI commands."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from flow_theory.templates.template_boundary_layer_thickness import (
    render_boundary_layer_thickness_section,
)
from flow_theory.templates.template_cf_ch import render_cf_ch_section
from flow_theory.templates.template_entropy_layer_estimate import (
    render_entropy_layer_estimate_section,
)
from flow_theory.templates.template_entropy_layer_swallowing import (
    render_entropy_layer_swallowing_section,
)
from flow_theory.templates.template_shock_shape import render_shock_shape_section
from flow_theory.templates.template_shock_standoff import (
    render_shock_standoff_section,
)

# --------------------------------------------------
# section registry
# --------------------------------------------------
SECTION_RENDERERS = {
    "boundary_layer_thickness": render_boundary_layer_thickness_section,
    "cf_ch": render_cf_ch_section,
    "entropy_layer_estimate": render_entropy_layer_estimate_section,
    "entropy_layer_swallowing": render_entropy_layer_swallowing_section,
    "shock_standoff": render_shock_standoff_section,
    "shock_shape": render_shock_shape_section,
}

SECTION_ORDER = [
    "boundary_layer_thickness",
    "cf_ch",
    "shock_standoff",
    "shock_shape",
    "entropy_layer_estimate",
    "entropy_layer_swallowing",
]

# --------------------------------------------------
# public API
# --------------------------------------------------
def render_templates(preset: str) -> str:
    """Build full config text for a flow-theory init preset.

    Args:
        preset: One registered section name or "all".

    Returns:
        Full TOML template text.
    """

    # build guidance comments
    lines = [
        "# flow-theory starter config",
        "#",
        "# run with:",
        "#   flow-theory run -c flow_theory.toml",
        "#",
        "",
    ]

    # add requested section blocks in deterministic order
    if preset == "all":
        section_names = list(SECTION_ORDER)
    else:
        section_names = [preset]

    # render sections as defined in separate template files
    for section_name in section_names:
        # get section renderer function from registry (defined above)
        render_section = SECTION_RENDERERS[section_name]

        # append rendered section text to lines
        lines.append(render_section())

        # add a blank line after each section for readability
        lines.append("")

    # join lines into a single string and return (rstrip to remove trailing whitespace, then add a final newline)
    return "\n".join(lines).rstrip() + "\n"
