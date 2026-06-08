from types import SimpleNamespace

from validation.intelligence.engineering.rules.tall_divider_stability_rule import (
    TallDividerStabilityRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_divider_passes():

    panel = SimpleNamespace(
        panel_category="divider",
        height=1800,
        thickness=18,
    )

    result = (
        TallDividerStabilityRule()
        .validate(panel)
    )

    assert result.passed is True


def test_tall_divider_warns():

    panel = SimpleNamespace(
        panel_category="divider",
        height=2400,
        thickness=18,
    )

    result = (
        TallDividerStabilityRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_divider_fails():

    panel = SimpleNamespace(
        panel_category="divider",
        height=2800,
        thickness=18,
    )

    result = (
        TallDividerStabilityRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
