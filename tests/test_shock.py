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
def test_shock_shape_vertex_matches_composed_standoff() -> None:
    """The first shock point should be the upstream axis standoff location."""

    # compute a sampled Billig shock locus
    result = compute_shock_shape(
        mach=19.25,
        gamma=1.4,
        nose_radius=1.0,
        n_points=200,
    )

    # check the coordinate contract and physical sweep direction
    assert result.x.shape == (200,)
    assert result.y.shape == (200,)
    assert result.x[0] == pytest.approx(-result.standoff.delta)
    assert np.all(np.diff(result.x) > 0.0)
    assert result.y[-1] == pytest.approx(3.0)


def test_shock_shape_matches_billig_worked_point() -> None:
    """The sampled locus should reproduce Billig's reported sphere point."""

    # compute the worked Mach 19.25 case in the nose-tip coordinate frame
    result = compute_shock_shape(
        mach=19.25,
        gamma=1.4,
        nose_radius=1.0,
        n_points=2000,
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
        )
