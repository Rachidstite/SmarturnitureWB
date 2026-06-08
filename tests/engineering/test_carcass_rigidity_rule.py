from types import SimpleNamespace

from validation.intelligence.engineering.rules.carcass_rigidity_rule import (
    CarcassRigidityRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)

from shared.roles import NodeRole


def test_rigid_cabinet_passes():

    scene_graph = SimpleNamespace(
        physical_nodes=[
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2200,
            ),
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2200,
            ),
            SimpleNamespace(
                role=NodeRole.BACK_PANEL,
            ),
        ]
    )

    result = (
        CarcassRigidityRule()
        .validate(scene_graph)
    )

    assert result.passed is True


def test_tall_cabinet_without_back_warns():

    scene_graph = SimpleNamespace(
        physical_nodes=[
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2200,
            ),
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2200,
            ),
        ]
    )

    result = (
        CarcassRigidityRule()
        .validate(scene_graph)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_very_tall_cabinet_without_back_fails():

    scene_graph = SimpleNamespace(
        physical_nodes=[
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2600,
            ),
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2600,
            ),
        ]
    )

    result = (
        CarcassRigidityRule()
        .validate(scene_graph)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
