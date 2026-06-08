from types import SimpleNamespace

from validation.intelligence.engineering.rules.long_door_hinge_rule import (
    LongDoorHingeRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_door_passes():

    panel = SimpleNamespace(
        panel_category="door",
        height=1800,
        hinge_count=3,
    )

    result = (
        LongDoorHingeRule()
        .validate(panel)
    )

    assert result.passed is True


def test_tall_door_warns():

    panel = SimpleNamespace(
        panel_category="door",
        height=2400,
        hinge_count=3,
    )

    result = (
        LongDoorHingeRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_very_tall_door_fails():

    panel = SimpleNamespace(
        panel_category="door",
        height=2800,
        hinge_count=3,
    )

    result = (
        LongDoorHingeRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
