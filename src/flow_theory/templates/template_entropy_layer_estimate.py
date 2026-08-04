"""Starter [entropy_layer_estimate] workflow template."""


def render_entropy_layer_estimate_section() -> str:
    """Build a starter [entropy_layer_estimate] section."""

    lines = [
        "[entropy_layer_estimate]",
        "run = true",
        "x = 0.1",
        "mach = 8.0",
        "nose_radius = 0.0254",
        "gamma = 1.4",
        'output = "entropy_layer_estimate.dat"',
    ]
    return "\n".join(lines)
