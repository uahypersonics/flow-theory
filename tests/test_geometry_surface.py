"""Tests for geometry surface builders used by shock-shape workflows."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import numpy as np
import pytest

from flow_theory.geometry import build_surface_geometry


# --------------------------------------------------
# surface geometry tests
# --------------------------------------------------
@pytest.mark.parametrize("geometry", ["sphere", "cylinder"])
def test_blunt_caps_terminate_at_2r(geometry: str) -> None:
    """Sphere and cylinder cap surfaces should end at x=2R when x_e is larger."""

    # build a blunt-cap surface with a longer requested streamwise extent
    radius = 0.01
    surface = build_surface_geometry(
        geometry=geometry,
        nose_radius=radius,
        x_e=0.1,
        n_points=101,
        half_angle=None,
    )

    # check physical cap termination and non-negative y values
    assert surface.body_x[0] == pytest.approx(0.0)
    assert surface.body_x[-1] == pytest.approx(2.0 * radius)
    assert np.all(surface.body_y >= 0.0)
    assert surface.requires_blend is False


@pytest.mark.parametrize("geometry", ["cone", "ogive", "wedge"])
def test_blended_geometries_require_half_angle(geometry: str) -> None:
    """Blended geometries should require half_angle."""

    # check required-angle validation
    with pytest.raises(ValueError, match="half_angle is required"):
        build_surface_geometry(
            geometry=geometry,
            nose_radius=0.01,
            x_e=0.1,
            n_points=101,
            half_angle=None,
        )


@pytest.mark.parametrize("geometry", ["cone", "ogive", "wedge"])
def test_blended_geometries_build_virtual_origin(geometry: str) -> None:
    """Blended geometries should provide a virtual cone origin."""

    # build a blended geometry surface
    surface = build_surface_geometry(
        geometry=geometry,
        nose_radius=0.01,
        x_e=0.1,
        n_points=101,
        half_angle=7.0,
    )

    # check shared metadata used by shock-shape blending
    assert surface.requires_blend is True
    assert surface.virtual_cone_origin is not None
    assert surface.standoff_geometry == "sphere"
    assert surface.billig_reference_geometry == "sphere"
