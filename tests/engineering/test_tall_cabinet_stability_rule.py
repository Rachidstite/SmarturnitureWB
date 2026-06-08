from types import SimpleNamespace

from validation.intelligence.engineering.rules.tall_cabinet_stability_rule import (
    TallCabinetStabilityRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)

from shared.roles import NodeRole


def test_normal_cabinet_passes():

    side_a = SimpleNamespace(
        role=NodeRole.SIDE_PANEL,
        height=2000,
    )

    side_b = SimpleNamespace(
        role=NodeRole.SIDE_PANEL,
        height=2000,
    )

    back = SimpleNamespace(
        role=NodeRole.BACK_PANEL,
    )

    scene_graph = SimpleNamespace(
        physical_nodes=[
            side_a,
            side_b,
            back,
        ]
    )

    result = (
        TallCabinetStabilityRule()
        .validate(scene_graph)
    )

    assert result.passed is True


def test_tall_cabinet_without_back_warns():

    side_a = SimpleNamespace(
        role=NodeRole.SIDE_PANEL,
        height=2400,
    )

    side_b = SimpleNamespace(
        role=NodeRole.SIDE_PANEL,
        height=2400,
    )

    scene_graph = SimpleNamespace(
        physical_nodes=[
            side_a,
            side_b,
        ]
    )

    result = (
        TallCabinetStabilityRule()
        .validate(scene_graph)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_cabinet_without_back_fails():

    side_a = SimpleNamespace(
        role=NodeRole.SIDE_PANEL,
        height=2700,
    )

    side_b = SimpleNamespace(
        role=NodeRole.SIDE_PANEL,
        height=2700,
    )

    scene_graph = SimpleNamespace(
        physical_nodes=[
            side_a,
            side_b,
        ]
    )

    result = (
        TallCabinetStabilityRule()
        .validate(scene_graph)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
