from types import SimpleNamespace

from validation.intelligence.engineering.rules.min_edge_distance_rule import (
    MinEdgeDistanceRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_safe_edge_distance_passes():

    joint = SimpleNamespace(
        edge_distance=50,
    )

    result = (
        MinEdgeDistanceRule()
        .validate(joint)
    )

    assert result.passed is True
    assert result.level == EngineeringLevel.INFO


def test_small_edge_distance_warns():

    joint = SimpleNamespace(
        edge_distance=25,
    )

    result = (
        MinEdgeDistanceRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_critical_edge_distance_fails():

    joint = SimpleNamespace(
        edge_distance=10,
    )

    result = (
        MinEdgeDistanceRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
