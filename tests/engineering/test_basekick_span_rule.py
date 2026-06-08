from types import SimpleNamespace

from validation.intelligence.engineering.rules.basekick_span_rule import (
    BaseKickSpanRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_basekick_passes():

    panel = SimpleNamespace(
        panel_category="basekick",
        span=900,
    )

    result = (
        BaseKickSpanRule()
        .validate(panel)
    )

    assert result.passed is True


def test_long_basekick_warns():

    panel = SimpleNamespace(
        panel_category="basekick",
        span=1400,
    )

    result = (
        BaseKickSpanRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_basekick_fails():

    panel = SimpleNamespace(
        panel_category="basekick",
        span=1800,
    )

    result = (
        BaseKickSpanRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
