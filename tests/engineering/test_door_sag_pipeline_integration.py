from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_door_sag_rule_appears_in_report():

    panel = SimpleNamespace(
        panel_category="door",
        height=2500,
        width=600,
        thickness=18,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [panel]
        )
    )

    assert len(report.warnings) > 0
