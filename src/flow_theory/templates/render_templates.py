"""Reusable TOML templates for flow-theory CLI commands."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from flow_theory.templates.template_cf_ch import render_cf_ch_section
from flow_theory.templates.template_swallowing import render_swallowing_section

# --------------------------------------------------
# section registry
# --------------------------------------------------
SECTION_RENDERERS = {
    "cf_ch": render_cf_ch_section,
    "swallowing": render_swallowing_section,
}

SECTION_ORDER = ["cf_ch", "swallowing"]

# --------------------------------------------------
# public API
# --------------------------------------------------
def render_templates(preset: str) -> str:
    """Build full config text for a flow-theory init preset.

    Args:
        preset: One of "cf_ch", "swallowing", or "all".

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
