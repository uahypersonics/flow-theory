"""Tests for shock-standoff and shock-shape estimates."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math

import numpy as np
import pytest

from flow_theory.shock import compute_shock_shape, compute_shock_standoff


# --------------------------------------------------
# shock-standoff tests
# --------------------------------------------------
def test_sphere_standoff_matches_ambrosio_wortman_air_correlation() -> None:
    """The sphere result should reproduce the published air fit."""

    # evaluate a representative supersonic condition
    result = compute_shock_standoff(
        mach=6.0,
        nose_radius=0.01,
    )

    # independently evaluate the non-dimensional relation
    expected_ratio = 0.143 * math.exp(3.24 / 6.0**2)

    # check dimensional and non-dimensional results
    assert result.delta_over_radius == pytest.approx(expected_ratio)
    assert result.delta == pytest.approx(expected_ratio * 0.01)
    assert result.geometry == "sphere"
    assert result.method == "ambrosio_wortman"


def test_cylinder_standoff_matches_ambrosio_wortman_air_correlation() -> None:
    """The cylinder result should reproduce the published air fit."""

    # evaluate a representative supersonic condition
    result = compute_shock_standoff(
        mach=6.0,
        nose_radius=0.01,
        geometry="cylinder",
    )

    # independently evaluate the non-dimensional relation
    expected_ratio = 0.386 * math.exp(4.67 / 6.0**2)

    # check dimensional and non-dimensional results
    assert result.delta_over_radius == pytest.approx(expected_ratio)
    assert result.delta == pytest.approx(expected_ratio * 0.01)
    assert result.geometry == "cylinder"


@pytest.mark.parametrize(
    ("geometry", "coefficient", "exponent"),
    [
        ("sphere", 0.52, -0.861),
        ("cylinder", 2.52, -1.25),
    ],
)
def test_ambrosio_wortman_density_ratio_correlation(
    geometry: str,
    coefficient: float,
    exponent: float,
) -> None:
    """The density-ratio method should reproduce Eqs. (2) and (3)."""

    # evaluate the correlation through the public API
    result = compute_shock_standoff(
        mach=6.0,
        gamma=1.4,
        nose_radius=0.01,
        geometry=geometry,
        method="ambrosio_wortman_density_ratio",
    )

    # independently compute the perfect-gas normal-shock density ratio
    density_ratio = (2.4 * 6.0**2) / (0.4 * 6.0**2 + 2.0)
    expected_ratio = coefficient * (density_ratio - 1.0) ** exponent

    # check the selected geometry correlation
    assert result.delta_over_radius == pytest.approx(expected_ratio)
    assert result.gamma == 1.4


def test_serbin_sphere_standoff_matches_density_ratio_relation() -> None:
    """The Serbin method should reproduce its published sphere relation."""

    # evaluate the sphere correlation through the public API
    result = compute_shock_standoff(
        mach=6.0,
        gamma=1.4,
        nose_radius=0.01,
        method="serbin",
    )

    # independently evaluate Serbin's density-ratio relation
    density_ratio = (2.4 * 6.0**2) / (0.4 * 6.0**2 + 2.0)
    expected_ratio = (2.0 / 3.0) * (density_ratio - 1.0) ** -1.0

    # check the non-dimensional result
    assert result.delta_over_radius == pytest.approx(expected_ratio)
    assert result.method == "serbin"


def test_serbin_rejects_cylinder_at_public_boundary() -> None:
    """The public API should reject the unsupported Serbin cylinder pairing."""

    # check method-specific geometry validation
    with pytest.raises(ValueError, match="does not support geometry 'cylinder'"):
        compute_shock_standoff(
            mach=6.0,
            gamma=1.4,
            nose_radius=0.01,
            geometry="cylinder",
            method="serbin",
        )


def test_density_ratio_method_requires_gamma() -> None:
    """Density-ratio methods should require a specific heat ratio."""

    # check method-specific input validation
    with pytest.raises(ValueError, match="gamma is required"):
        compute_shock_standoff(
            mach=6.0,
            nose_radius=0.01,
            method="serbin",
        )


def test_standoff_rejects_unsupported_geometry() -> None:
    """The standoff method should reject unsupported nose geometries."""

    # check
    with pytest.raises(ValueError, match="geometry must be one of"):
        compute_shock_standoff(
            mach=6.0,
            nose_radius=0.01,
            geometry="blunt_cone",
        )


# --------------------------------------------------
# shock-shape tests
# --------------------------------------------------
@pytest.mark.parametrize("geometry", ["sphere", "cylinder"])
def test_shock_shape_vertex_matches_composed_standoff(geometry: str) -> None:
    """The first shock point should be the upstream axis standoff location."""

    # compute a sampled Billig shock locus
    result = compute_shock_shape(
        mach=19.25,
        gamma=1.4,
        nose_radius=1.0,
        geometry=geometry,
        n_points=200,
        x_e=1.8,
    )

    # check the coordinate contract and physical sweep direction
    assert result.x.shape == (200,)
    assert result.y.shape == (200,)
    assert result.body_x.shape == (200,)
    assert result.body_y.shape == (200,)
    assert result.x[0] == pytest.approx(-result.standoff.delta)
    assert result.x[-1] == pytest.approx(1.8)
    assert np.all(np.diff(result.x) > 0.0)
    assert np.all(result.y >= 0.0)
    assert result.geometry == geometry


def test_shock_shape_cylinder_differs_from_sphere() -> None:
    """Cylinder and sphere Billig constants should not collapse to one locus."""

    sphere = compute_shock_shape(
        mach=8.0,
        gamma=1.4,
        nose_radius=0.02,
        geometry="sphere",
        n_points=150,
        x_e=0.03,
    )
    cylinder = compute_shock_shape(
        mach=8.0,
        gamma=1.4,
        nose_radius=0.02,
        geometry="cylinder",
        n_points=150,
        x_e=0.03,
    )

    # check both shock loci share x_e but have different vertex locations
    assert sphere.x[-1] == pytest.approx(cylinder.x[-1])
    assert sphere.x[0] != pytest.approx(cylinder.x[0])

    # check geometry-specific Billig constants produce different y-loci
    assert not np.allclose(sphere.y, cylinder.y)


def test_shock_shape_matches_billig_worked_point() -> None:
    """The sampled locus should reproduce Billig's reported sphere point."""

    # compute the worked Mach 19.25 case in the nose-tip coordinate frame
    result = compute_shock_shape(
        mach=19.25,
        gamma=1.4,
        nose_radius=1.0,
        n_points=2000,
        x_e=1.8,
    )

    # Billig's x=0 is the sphere center, which is x=R in this package
    y_at_sphere_center = np.interp(1.0, result.x, result.y)

    # check against the three-significant-figure value reported by Billig
    assert y_at_sphere_center == pytest.approx(1.64, rel=5.0e-3)


def test_shock_shape_rejects_unvalidated_blunt_cone_geometry() -> None:
    """The sphere correlation should not silently represent a cone afterbody."""

    # check
    with pytest.raises(ValueError, match="geometry must be one of"):
        compute_shock_shape(
            mach=6.0,
            gamma=1.4,
            nose_radius=0.01,
            geometry="blunt_cone",
            x_e=0.1,
        )


def test_shock_shape_cone_geometry_uses_requested_x_e() -> None:
    """Cone geometry should sample from the shock vertex to x_e."""

    result = compute_shock_shape(
        mach=6.0,
        gamma=1.4,
        nose_radius=0.01,
        geometry="cone",
        half_angle=15.0,
        x_e=0.10,
        n_points=200,
    )

    # check the streamwise coordinate contract
    assert result.x[0] == pytest.approx(-result.standoff.delta)
    assert result.x[-1] == pytest.approx(0.10)
    assert np.all(np.diff(result.x) > 0.0)

    # check cone metadata is carried on the result
    assert result.half_angle == pytest.approx(15.0)
    assert result.asymptote_shock_angle is not None
    assert result.virtual_cone_origin is not None
    assert result.body_x[0] == pytest.approx(0.0)
    assert result.body_x[-1] == pytest.approx(0.10)


def test_shock_shape_cone_requires_x_e_and_half_angle() -> None:
    """Cone geometry should fail fast when required inputs are missing."""

    with pytest.raises(ValueError, match="half_angle is required"):
        compute_shock_shape(
            mach=6.0,
            gamma=1.4,
            nose_radius=0.01,
            geometry="cone",
            x_e=0.10,
        )

    with pytest.raises(ValueError, match="x_e is required"):
        compute_shock_shape(
            mach=6.0,
            gamma=1.4,
            nose_radius=0.01,
            geometry="cone",
            half_angle=15.0,
        )


@pytest.mark.parametrize("geometry", ["cone", "ogive", "wedge"])
def test_blended_geometries_build_surface_and_shock(geometry: str) -> None:
    """Each blended geometry should build both body and shock zones."""

    result = compute_shock_shape(
        mach=6.0,
        gamma=1.4,
        nose_radius=0.01,
        geometry=geometry,
        half_angle=7.0,
        x_e=0.08,
        n_points=120,
    )

    assert result.x.shape == (120,)
    assert result.body_x.shape == (120,)
    assert result.asymptote_shock_angle is not None
    assert result.virtual_cone_origin is not None


@pytest.mark.parametrize("geometry", ["sphere", "cylinder"])
def test_blunt_surface_zone_terminates_at_cap_end(geometry: str) -> None:
    """Sphere/cylinder body surface should stop at x=2R without a zero tail."""

    radius = 0.01
    result = compute_shock_shape(
        mach=6.0,
        gamma=1.4,
        nose_radius=radius,
        geometry=geometry,
        x_e=0.10,
        n_points=101,
    )

    assert result.body_x[0] == pytest.approx(0.0)
    assert result.body_x[-1] == pytest.approx(2.0 * radius)
    assert np.all(result.body_y >= 0.0)
