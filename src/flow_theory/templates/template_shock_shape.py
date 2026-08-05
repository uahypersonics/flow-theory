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
        '# supported geometries: sphere, cylinder, cone, ogive, wedge',
        'geometry = "sphere"',
        '# nose_radius is required for all geometries',
        "nose_radius = 0.01",
        'method = "billig"',
        '# half_angle [deg], required only for cone, ogive, and wedge',
        '# sphere and cylinder ignore this value',
        'half_angle = 7.0',
        '# n_points controls sampling resolution for both output zones',
        "n_points = 201",
        '# streamwise endpoint from nose/leading edge for shock sampling',
        '# sphere/cylinder body zone still ends at cap extent (x <= 2*R)',
        'x_e = 0.10',
        'output = "shock_shape.dat"',
    ]

    return "\n".join(lines)
