"""Starter [swallowing] section template for flow-theory init."""

# --------------------------------------------------
# public API
# --------------------------------------------------
def render_swallowing_section() -> str:
    """Build a starter [swallowing] section."""

    lines = [
        "[swallowing]",
        "run = true",
        "mach = 5.0",
        "re1 = 3.0e6",
        "nose_radius = 0.0254",
        "tw_t0 = 0.4",
        "gamma = 1.4",
        "output = \"swallowing_from_run.dat\"",
    ]
    return "\n".join(lines)
