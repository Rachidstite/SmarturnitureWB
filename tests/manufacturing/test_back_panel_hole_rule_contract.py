from dataclasses import fields, is_dataclass

from manufacturing.back_panel_hole_rule_report import (
    BackPanelHoleRuleReport,
)


def test_back_panel_hole_rule_report_is_dataclass():
    assert is_dataclass(BackPanelHoleRuleReport)


def test_back_panel_hole_rule_report_contract():
    expected = {
        "minimum_panel_width",
        "minimum_panel_height",
        "spacing_rule",
        "edge_rule",
        "corner_rule",
        "maximum_spacing",
        "requires_center_holes",
    }

    actual = {
        field.name
        for field in fields(
            BackPanelHoleRuleReport
        )
    }

    assert actual == expected


def test_back_panel_hole_rule_report_safe_defaults():
    report = BackPanelHoleRuleReport()

    assert report.minimum_panel_width == 0.0
    assert report.minimum_panel_height == 0.0
    assert report.spacing_rule == ""
    assert report.edge_rule == ""
    assert report.corner_rule == ""
    assert report.maximum_spacing == 0.0
    assert report.requires_center_holes is False
