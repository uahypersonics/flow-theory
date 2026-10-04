"""Starter [transition] workflow template."""


# --------------------------------------------------
# public API
# --------------------------------------------------
def render_transition_section() -> str:
    """Build a starter [transition] section."""

    # build the editable transition example
    lines = [
        "[transition]",
        "mach = 5.0",
        "re1 = 3.0e6",
        "tw_te = 0.5",
        'method = "van_driest_blumer"',
        'output = "transition.dat"',
    ]

    # join the section into TOML text
    content = "\n".join(lines)
    return content
