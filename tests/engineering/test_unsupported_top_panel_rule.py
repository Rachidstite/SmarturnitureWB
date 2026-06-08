from types import SimpleNamespace

from validation.intelligence.engineering.rules.unsupported_top_panel_rule import (
    UnsupportedTopPanelRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_supported_top_panel_passes():

    panel = SimpleNamespace(
        panel_category="top_panel",
        span=900,
    )

    result = (
        UnsupportedTopPanelRule()
        .validate(panel)
    )

    assert result.passed is True


def test_long_top_panel_warns():

    panel = SimpleNamespace(
        panel_category="top_panel",
        span=1400,
    )

    result = (
        UnsupportedTopPanelRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_top_panel_fails():

    panel = SimpleNamespace(
        panel_category="top_panel",
        span=1800,
    )

    result = (
        UnsupportedTopPanelRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
