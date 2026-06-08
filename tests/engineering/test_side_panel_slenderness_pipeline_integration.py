from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_side_panel_rule_appears_in_report():

    panel = SimpleNamespace(
        panel_category="side_panel",
        height=2700,
        thickness=18,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [panel]
        )
    )

    assert len(report.warnings) > 0
