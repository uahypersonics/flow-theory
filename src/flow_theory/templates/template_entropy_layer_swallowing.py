"""Starter [entropy_layer_swallowing] workflow template."""


def render_entropy_layer_swallowing_section() -> str:
    """Build a starter [entropy_layer_swallowing] section."""

    lines = [
        "[entropy_layer_swallowing]",
        "mach = 8.0",
        "re1 = 3.0e6",
        "nose_radius = 0.0254",
        "tw_t0 = 0.4",
        "gamma = 1.4",
        'output = "entropy_layer_swallowing.dat"',
    ]
    return "\n".join(lines)
