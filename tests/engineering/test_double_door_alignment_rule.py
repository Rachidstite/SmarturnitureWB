from types import SimpleNamespace

from validation.intelligence.engineering.rules.double_door_alignment_rule import (
    DoubleDoorAlignmentRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_double_door_passes():

    panel = SimpleNamespace(
        panel_category="door",
        door_count=2,
        height=1800,
    )

    result = (
        DoubleDoorAlignmentRule()
        .validate(panel)
    )

    assert result.passed is True


def test_tall_double_door_warns():

    panel = SimpleNamespace(
        panel_category="door",
        door_count=2,
        height=2400,
    )

    result = (
        DoubleDoorAlignmentRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_double_door_fails():

    panel = SimpleNamespace(
        panel_category="door",
        door_count=2,
        height=2800,
    )

    result = (
        DoubleDoorAlignmentRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
