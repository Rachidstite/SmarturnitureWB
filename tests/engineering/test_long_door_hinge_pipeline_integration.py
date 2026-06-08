from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_long_door_hinge_rule_appears_in_report():

    panel = SimpleNamespace(
        panel_category="door",
        height=2400,
        hinge_count=3,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [panel]
        )
    )

    assert len(report.warnings) > 0
