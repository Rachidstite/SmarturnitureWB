from types import SimpleNamespace

from validation.intelligence.engineering.rules.divider_buckling_rule import (
    DividerBucklingRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_short_divider_passes():

    panel = SimpleNamespace(
        panel_category="divider",
        height=2000,
        section_width=500,
        thickness=18,
    )

    result = (
        DividerBucklingRule()
        .validate(panel)
    )

    assert result.passed is True


def test_tall_divider_warns():

    panel = SimpleNamespace(
        panel_category="divider",
        height=2300,
        section_width=650,
        thickness=18,
    )

    result = (
        DividerBucklingRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_divider_fails():

    panel = SimpleNamespace(
        panel_category="divider",
        height=2700,
        section_width=750,
        thickness=18,
    )

    result = (
        DividerBucklingRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
