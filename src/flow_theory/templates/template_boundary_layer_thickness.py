"""Starter [boundary_layer_thickness] workflow template."""


def render_boundary_layer_thickness_section() -> str:
    """Build a starter [boundary_layer_thickness] section."""

    lines = [
        "[boundary_layer_thickness]",
        "x = [0.1, 0.5, 1.0]",
        "re1 = 3.0e6",
        'method = "eckert_reference"',
        "mach = 8.0",
        "tw_t0 = 0.4",
        "gamma = 1.4",
        'output = "boundary_layer_thickness.dat"',
    ]
    return "\n".join(lines)
