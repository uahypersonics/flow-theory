"""Starter [shock_shape] section template for flow-theory init."""


# --------------------------------------------------
# public API
# --------------------------------------------------
def render_shock_shape_section() -> str:
    """Build a starter [shock_shape] section."""

    lines = [
        "# --------------------------------------------------",
        "# detached bow-shock locus",
        "# --------------------------------------------------",
        "[shock_shape]",
        "run = true",
        'flow_conditions = "flow_conditions.json"',
        '# the current Billig shape correlation supports geometry = "sphere"',
        'geometry = "sphere"',
        "nose_radius = 0.01",
        'method = "billig"',
        "n_points = 201",
        "lateral_extent = 0.05",
        'output = "shock_shape.dat"',
    ]

    return "\n".join(lines)
