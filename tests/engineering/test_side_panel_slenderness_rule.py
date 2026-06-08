from types import SimpleNamespace

from validation.intelligence.engineering.rules.side_panel_slenderness_rule import (
    SidePanelSlendernessRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_side_panel_passes():

    panel = SimpleNamespace(
        panel_category="side_panel",
        height=2200,
        thickness=18,
    )

    result = (
        SidePanelSlendernessRule()
        .validate(panel)
    )

    assert result.passed is True


def test_tall_side_panel_warns():

    panel = SimpleNamespace(
        panel_category="side_panel",
        height=2700,
        thickness=18,
    )

    result = (
        SidePanelSlendernessRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_side_panel_fails():

    panel = SimpleNamespace(
        panel_category="side_panel",
        height=3100,
        thickness=18,
    )

    result = (
        SidePanelSlendernessRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
