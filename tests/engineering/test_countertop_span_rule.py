from types import SimpleNamespace

from validation.intelligence.engineering.rules.countertop_span_rule import (
    CountertopSpanRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_supported_countertop_passes():

    panel = SimpleNamespace(
        panel_category="countertop",
        span=900,
        thickness=36,
    )

    result = (
        CountertopSpanRule()
        .validate(panel)
    )

    assert result.passed is True


def test_long_countertop_warns():

    panel = SimpleNamespace(
        panel_category="countertop",
        span=1400,
        thickness=36,
    )

    result = (
        CountertopSpanRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_countertop_fails():

    panel = SimpleNamespace(
        panel_category="countertop",
        span=1800,
        thickness=36,
    )

    result = (
        CountertopSpanRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
