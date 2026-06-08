from types import SimpleNamespace

from validation.intelligence.engineering.rules.door_sag_rule import (
    DoorSagRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_door_passes():

    panel = SimpleNamespace(
        panel_category="door",
        height=2200,
        width=500,
        thickness=18,
    )

    result = (
        DoorSagRule()
        .validate(panel)
    )

    assert result.passed is True


def test_tall_door_warns():

    panel = SimpleNamespace(
        panel_category="door",
        height=2500,
        width=600,
        thickness=18,
    )

    result = (
        DoorSagRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_door_fails():

    panel = SimpleNamespace(
        panel_category="door",
        height=2800,
        width=700,
        thickness=18,
    )

    result = (
        DoorSagRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
