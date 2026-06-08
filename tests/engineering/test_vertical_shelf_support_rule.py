from types import SimpleNamespace

from validation.intelligence.engineering.rules.vertical_shelf_support_rule import (
    VerticalShelfSupportRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_supported_shelf_passes():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=800,
    )

    result = (
        VerticalShelfSupportRule()
        .validate(panel)
    )

    assert result.passed is True


def test_long_shelf_warns():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1200,
    )

    result = (
        VerticalShelfSupportRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_shelf_fails():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1600,
    )

    result = (
        VerticalShelfSupportRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
